"""Generate immutable factual windows and an offline HTML election calendar."""
import argparse
import hashlib
import json
import subprocess
import shutil
from datetime import datetime, timedelta
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path
from lunar_python import Solar
from rules import *
from shensha import CATALOG, LIS, FENZHI, JIES, evaluate as shensha_facts
from participants import context_lives,normalize_lives
from qimen import chart as qimen_chart,TERM_JU,METHOD as QIMEN_METHOD,for_time as qimen_for_time,METHODS as QIMEN_METHODS
from astronomy import positions_many,validate_observer
from direction_systems import ritual_facts

ROOT=Path(__file__).resolve().parents[1]

def attach_liuren(data):
    inputs={}
    for d in data['days']:
        for w in d['windows']:
            for f in w['profiles'].values():
                item={'day':f['pillars']['日'],'hour':f['pillars']['时'],'jiang':f['jiang'],'sky':f['sky'],'noble':f['noble']}
                key=digest(item)[:24];inputs[key]=item;f['liuren_key']=key
    node=shutil.which('node')
    if not node: raise RuntimeError('Node.js is required for the existing Liuren plugin engine')
    result=subprocess.run([node,str(ROOT/'scripts/build_liuren.mjs')],input=json.dumps(inputs,ensure_ascii=False),
                          text=True,encoding='utf-8',capture_output=True)
    if result.returncode:raise RuntimeError('Liuren plugin failed: '+result.stderr[-2500:])
    data['liuren_charts']=json.loads(result.stdout)
    data['meta']['liuren_engine']={'name':'dsh-liuren-paipan','source':'plugins/dsh-liuren-paipan/src/core/liuren.ts',
        'digest':digest((ROOT/'assets/liuren-core.mjs').read_text(encoding='utf-8')),
        'bridge_digest':digest((ROOT/'scripts/build_liuren.mjs').read_text(encoding='utf-8')),
        'daylight_and_noble':'Use calendar facts; preserve selected daylight and noble profile',
        'changsheng':'五行统一顺行，水土长生申'}

def digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def write_json(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

@lru_cache(maxsize=16)
def terms(year):
    table=Solar.fromYmd(year,6,1).getLunar().getJieQiTable()
    return sorted({(datetime.fromisoformat(s.toYmdHms()),ALIASES.get(n,n)) for n,s in table.items()})

def lunar(dt):
    return Solar.fromYmdHms(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second).getLunar()


@lru_cache(maxsize=1100)
def calendar_shensha(civil_date, pillar_date):
    """Civil-day solar markers and rollover-aligned lunar markers stay separate."""
    term_list=sorted(set(item for y in range(civil_date.year-1,civil_date.year+2) for item in terms(y)))
    marks={}
    for t,name in term_list:
        if name in LIS and t.date()-timedelta(days=1)==civil_date:
            marks['四绝']=[name+'前一日']
        if name in FENZHI and t.date()-timedelta(days=1)==civil_date:
            marks['四离']=[name+'前一日']
        if name in JIES:
            i=JIES.index(name);count=(7+i//3)*(i%3+1)
            if t.date()+timedelta(days=count-1)==civil_date:
                marks['气往亡']=[f'{name}日起含当日第{count}日']
    earth=any(t.date()-timedelta(days=18)<=civil_date<t.date() for t,n in term_list if n in LIS)
    if earth: marks['土王用事']=['四立前18日内']
    l=Solar.fromYmd(pillar_date.year,pillar_date.month,pillar_date.day).getLunar()
    ld=l.getDay()
    first=pillar_date-timedelta(days=ld-1)
    fb=Solar.fromYmd(first.year,first.month,first.day).getLunar().getDayInGanZhi()[1]
    reverse_day=6-ZHI.index(fb)//2
    if ld in [5,14,23]: marks['月忌日']=[f'农历第{ld}日']
    if ld==reverse_day: marks['反支']=[f'月朔{fb}，本月第{reverse_day}日']
    marks['_lunar_day']=ld;marks['_first_branch']=fb
    return marks,earth

def calc(dt,jiang_mode='zhongqi',noble_profile='liuren-common',rollover='zi',daytime=None,qimen_method='chaibu'):
    l=lunar(dt)
    year,month=l.getYearInGanZhiExact(),l.getMonthInGanZhiExact()
    ddt=dt+timedelta(days=1) if rollover=='zi' and dt.hour>=23 else dt
    # civil-date day pillar bypasses the library's independent late-Zi switch.
    day=Solar.fromYmd(ddt.year,ddt.month,ddt.day).getLunar().getDayInGanZhi()
    hb=ZHI[((dt.hour+1)//2)%12]
    hour=hour_pillar(day[0],hb)
    if jiang_mode!='zhongqi': raise ValueError('Only zhongqi month general is supported')
    general_terms=sorted(set(item for y in [dt.year-1,dt.year] for item in terms(y)))
    jiang=next(ZHONG_QI[n] for t,n in reversed(general_terms) if t<=dt and n in ZHONG_QI)
    daytime=(5<=dt.hour<19) if daytime is None else daytime
    facts=fixed_facts(year,month,day,hour,jiang,daytime,noble_profile)
    calendar_info,earth=calendar_shensha(dt.date(),ddt.date())
    facts['shensha']=shensha_facts(year,month,day,hour,facts['sky'],calendar_info,earth)
    qterms=sorted(set(item for y in [dt.year-1,dt.year,dt.year+1] for item in terms(y)))
    current_term=next(n for t,n in reversed(qterms) if t<=dt and n in TERM_JU)
    facts['qimen_chart']=qimen_for_time(day,hour,current_term,dt,ddt.date(),qimen_method)
    facts['qimen_variants']={m:qimen_for_time(day,hour,current_term,dt,ddt.date(),m) for m in QIMEN_METHODS}
    facts['direction_systems']=ritual_facts(facts)
    return facts

def build(start,days,rollover='zi',sun_times=None,observer=None):
    observer=validate_observer(observer)
    end=start+timedelta(days=days)
    calendar=[]
    shensha_sets={};shensha_keys={}
    qimen_charts={};sample_times=[];sample_ids=[]
    all_terms=sorted(set(t for y in range(start.year,end.year+1) for t,n in terms(y) if start<t<end))
    for offset in range(days):
        base=start+timedelta(days=offset)
        if sun_times is not None:
            sun=sun_times[base.date().isoformat()]
            rise=datetime.fromisoformat(base.date().isoformat()+'T'+sun['sunrise'])
            setting=datetime.fromisoformat(base.date().isoformat()+'T'+sun['sunset'])
            if not base<rise<setting<base+timedelta(days=1): raise ValueError('Bad sunrise/sunset order')
        else:
            rise=base+timedelta(hours=5);setting=base+timedelta(hours=19)
        bounds={base,base+timedelta(days=1),rise,setting}
        bounds.update(base+timedelta(hours=h) for h in range(1,24,2))
        bounds.update(t for t in all_terms if base<t<base+timedelta(days=1))
        bounds=sorted(bounds)
        windows=[]
        for a,b in zip(bounds,bounds[1:]):
            mid=a+(b-a)/2
            profiles={f'zhongqi/{n}':calc(mid,'zhongqi',n,rollover,rise<=mid<setting) for n in NOBLE}
            # Intern repeated evidence across the two named noble profiles.
            for f in profiles.values():
                sha=f.pop('shensha');sha_digest=digest(sha)
                if sha_digest not in shensha_keys:
                    key=f'sha-{len(shensha_sets)}';shensha_keys[sha_digest]=key;shensha_sets[key]=sha
                f['shensha_key']=shensha_keys[sha_digest]
                q=f.pop('qimen_chart');qkey=digest(q)[:24];qimen_charts[qkey]=q;f['qimen_key']=qkey
                f['qimen_keys']={}
                for method,chart in f.pop('qimen_variants').items():
                    key=digest(chart)[:24];qimen_charts[key]=chart;f['qimen_keys'][method]=key
                f['sky_sample_key']=a.isoformat(timespec='seconds') if observer is not None else 'needs-observer'
            sample_times.append(mid);sample_ids.append(a.isoformat(timespec='seconds'))
            windows.append({'id':a.isoformat(timespec='seconds'),'start':a.isoformat(timespec='seconds'),
                            'end':b.isoformat(timespec='seconds'),'profiles':profiles})
        noon=lunar(base+timedelta(hours=12))
        calendar.append({'date':base.date().isoformat(),'weekday':base.weekday(),'lunar':f'{noon.getMonthInChinese()}月{noon.getDayInChinese()}',
                         'sunrise':rise.strftime('%H:%M:%S'),'sunset':setting.strftime('%H:%M:%S'),'windows':windows})
    meta={'schema':'liuren-time-calendar/v2','rule_version':VERSION,'calendar_library':'lunar-python '+version('lunar_python'),
          'start':start.date().isoformat(),'days':days,'timezone':'Asia/Shanghai','clock':'北京时间，无真太阳时校正',
          'rollover':rollover,'jiang_mode':'zhongqi','daylight':'provided-sunrise-sunset' if sun_times else 'mao-you-05-19',
          'sun_source':sun_times.get('_source') if sun_times else None,
          'rules_digest':digest({name:Path(__file__).with_name(name).read_text(encoding='utf-8') for name in ['rules.py','shensha.py','calendar.py']}),
          'shensha_rule_count':len(CATALOG),'month_rule_basis':'节月；历日月忌和反支使用农历',
          'solar_day_markers':'四离、四绝、气往亡、土王按公历00:00换日',
          'observer':observer,'qimen_method':QIMEN_METHOD,'qimen_methods':QIMEN_METHODS,
          'sky_sample_policy':'星空在每个窗口中点采样；不是整个时段恒定，具体分钟请调用真实星空工具。',
          'shensha_sources_digest':digest({p.name:p.read_text(encoding='utf-8') for p in sorted((ROOT/'references/sources').glob('*.txt'))})}
    data={'meta':meta,'days':calendar,'pair_relations':{a+b:pair(a,b) for a in GAN+ZHI for b in GAN+ZHI},
          'group_rules':[{'branches':g,'name':typ,'element':e} for table,typ in [(SAN_HE,'三合齐备'),(SAN_HUI,'三会齐备')] for g,e in table],
          'shensha_catalog':CATALOG,'shensha_sets':shensha_sets,'judgment_criteria':JUDGMENT_CRITERIA,
          'qimen_charts':qimen_charts,'sky_samples':{}}
    samples=positions_many(sample_times,observer)
    data['sky_samples']=dict(zip(sample_ids,samples)) if observer is not None else {'needs-observer':samples[0]}
    attach_liuren(data)
    data['facts_digest']=digest(data)
    return data

def validate_review(review,data):
    if review.get('facts_digest')!=data['facts_digest']: raise ValueError('Review facts digest does not match')
    context=review['context']
    if context.get('qimen_method','chaibu') not in QIMEN_METHODS:raise ValueError('Bad Qimen method')
    for k in ['purpose','mountain','life','profile']:
        if k not in context: raise ValueError('Missing review context '+k)
    if context['profile'] not in [f'zhongqi/{n}' for n in NOBLE]: raise ValueError('Bad review profile')
    if context['mountain'] not in ['',*ZHI] or context['life'] not in ['',*ZHI]: raise ValueError('Bad mountain or life')
    lives=context_lives(context)
    joint_marriage=any(word in context['purpose'] for word in ['婚姻','结婚','嫁娶'])
    ids={w['id'] for d in data['days'] for w in d['windows']}
    seen=set()
    for item in review['decisions']:
        if item['id'] not in ids or item['id'] in seen: raise ValueError('Unknown or duplicate reviewed window')
        seen.add(item['id'])
        if item['verdict'] not in ['优先','可选','避用','待定']: raise ValueError('Unknown verdict')
        if not context['purpose'].strip() and item['verdict']!='待定': raise ValueError('An election verdict requires a purpose')
        if not isinstance(item.get('reason'),str) or not item['reason'].strip(): raise ValueError('Decision must explain reason')
        if not isinstance(item.get('evidence'),list) or not item['evidence']: raise ValueError('Decision must cite factual fields')
        if any(not p['branch'] for p in lives) and item['verdict'] in ['优先','可选']:
            raise ValueError('Incomplete participant natal branches require pending judgment')
        if joint_marriage and len(lives)<2 and item['verdict'] in ['优先','可选']:
            raise ValueError('Marriage timing requires both participants before usable judgments')
        direction=item.get('suggested_direction')
        if not context['mountain'] and item['verdict'] in ['优先','可选']:
            if not isinstance(direction,dict) or direction.get('branch') not in list(ZHI) or not direction.get('reason'):
                raise ValueError('A usable window requires an explained AI direction when unspecified')
        if direction is not None and (not isinstance(direction,dict) or direction.get('branch') not in list(ZHI)):
            raise ValueError('Invalid suggested direction')
    return review

def render(data,target,review=None,initial_context=None):
    if review: validate_review(review,data)
    target=Path(target)
    # Keep the restored HTML editor small. A multi-megabyte JSON literal on one
    # line can stall syntax highlighting when the desktop restores this tab.
    payload=target.with_suffix('.data.js')
    def script(path,variables,marker=None):
        encoder=json.JSONEncoder(ensure_ascii=False,separators=(',',':'))
        temporary=path.with_name(path.name+'.tmp')
        with temporary.open('w',encoding='utf-8') as stream:
            if marker:stream.write(marker+'\n')
            for variable,value in variables:
                stream.write('globalThis.LIUREN_CALENDAR_'+variable+'=')
                column=0
                for token in encoder.iterencode(value):
                    token=token.replace('<','\\u003c')
                    stream.write(token);column+=len(token)
                    if token==',' and column>=1000:stream.write('\n');column=0
                stream.write(';\n')
        temporary.replace(path)
    manifest=data
    if len(data['days'])>=180:
        # Only one month of heavy charts is kept by the browser at a time.
        heavy={'days','shensha_sets','liuren_charts','qimen_charts','sky_samples'}
        manifest={k:v for k,v in data.items() if k not in heavy}
        manifest['days']=[];manifest['month_payloads']={}
        manifest['window_ids']=[w['id'] for d in data['days'] for w in d['windows']]
        manifest['month_counts']={}
        for month in sorted({d['date'][:7] for d in data['days']}):
            days=[d for d in data['days'] if d['date'].startswith(month)]
            facts=[f for d in days for w in d['windows'] for f in w['profiles'].values()]
            keys={'shensha_sets':{f['shensha_key'] for f in facts},
                  'liuren_charts':{f['liuren_key'] for f in facts},
                  'qimen_charts':{key for f in facts for key in f.get('qimen_keys',{'chaibu':f['qimen_key']}).values()},
                  'sky_samples':{f['sky_sample_key'] for f in facts}}
            part={'days':days,**{field:{key:data[field][key] for key in ids} for field,ids in keys.items()}}
            month_path=target.with_name(target.stem+'.'+month+'.data.js')
            marker='// facts_digest: '+data['facts_digest']
            existing_marker=None
            if month_path.exists():
                with month_path.open(encoding='utf-8') as stream:existing_marker=stream.readline().strip()
            if existing_marker!=marker:script(month_path,[('MONTH',part)],marker)
            manifest['month_payloads'][month]=month_path.name
            manifest['month_counts'][month]={'days':len(days),'windows':sum(len(d['windows']) for d in days)}
    if initial_context is not None:manifest={**manifest,'initial_context':initial_context}
    script(payload,[('DATA',manifest),('REVIEW',review)])
    content=(ROOT/'assets/calendar.html').read_text(encoding='utf-8')
    from html import escape
    content=content.replace('__FACTS_SCRIPT__',escape(payload.name,quote=True))
    content=content.replace('__FACTS__','globalThis.LIUREN_CALENDAR_DATA')
    content=content.replace('__REVIEW__','globalThis.LIUREN_CALENDAR_REVIEW')
    target.write_text(content,encoding='utf-8')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--year',type=int,help='Full civil year, January 1 through December 31')
    p.add_argument('--start',default='2026-10-01');p.add_argument('--days',type=int,default=92)
    p.add_argument('--output',required=True);p.add_argument('--review');p.add_argument('--facts')
    p.add_argument('--rollover',choices=['zi','midnight'],default='zi');p.add_argument('--sun-times')
    p.add_argument('--observer',help='JSON observer with latitude, longitude, optional elevation_m and label')
    args=p.parse_args()
    if args.year is not None:
        if args.facts or not 1900<=args.year<=2099:p.error('--year requires regenerated facts and a year in 1900..2099')
        args.start=f'{args.year}-01-01';args.days=(datetime(args.year+1,1,1)-datetime(args.year,1,1)).days
    if not 1<=args.days<=366: p.error('--days must be 1..366')
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    if args.facts:
        if args.observer:p.error('Change observer by regenerating facts, not while rendering immutable facts')
        data=json.loads(Path(args.facts).read_text(encoding='utf-8-sig'))
        if data['meta'].get('jiang_mode')!='zhongqi':
            raise ValueError('Old month-general facts must be regenerated; only zhongqi is supported')
        if 'liuren_charts' not in data or 'qimen_charts' not in data or 'qimen_methods' not in data['meta']:
            raise ValueError('Old facts without complete joint direction charts must be regenerated')
        if digest({k:v for k,v in data.items() if k!='facts_digest'})!=data['facts_digest']:
            raise ValueError('Facts changed after generation; regenerate before rendering')
    else:
        sun=json.loads(Path(args.sun_times).read_text(encoding='utf-8-sig')) if args.sun_times else None
        observer=json.loads(Path(args.observer).read_text(encoding='utf-8-sig')) if args.observer else None
        data=build(datetime.fromisoformat(args.start),args.days,args.rollover,sun,observer)
    write_json(output/'facts.json',data)
    review=json.loads(Path(args.review).read_text(encoding='utf-8-sig')) if args.review else None
    render(data,output/'择时日历.html',review)
    print(json.dumps({'html':str(output/'择时日历.html'),'days':len(data['days']),
        'windows':sum(len(d['windows']) for d in data['days']),'facts_digest':data['facts_digest']},ensure_ascii=False))

if __name__=='__main__': main()
