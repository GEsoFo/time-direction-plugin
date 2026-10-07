"""Build an election request; does not choose or score windows."""
import argparse
import json
from pathlib import Path
from rules import pair,ZHI,groups
from participants import normalize_lives,direction_candidates

def make_request(data,month,purpose='',mountain='',life='',profile='zhongqi/liuren-common',lives=None,qimen_method='chaibu',window_ids=None):
    if mountain not in ['',*ZHI] or life not in ['',*ZHI]: raise ValueError('Only twelve-branch directions are supported')
    if qimen_method not in ['chaibu','zhirun']:raise ValueError('Unknown Qimen method')
    lives=normalize_lives(life,lives)
    life=lives[0]['branch'] if lives else ''
    windows=[]
    for d in data['days']:
        if not d['date'].startswith(month): continue
        for w in d['windows']:
            if window_ids is not None and w['id'] not in window_ids:continue
            f=w['profiles'][profile]
            if 'shensha_key' in f:
                f={**f,'shensha':data['shensha_sets'][f['shensha_key']]}
            if 'liuren_key' in f:
                f={**f,'liuren_chart':data['liuren_charts'][f['liuren_key']]}
            if 'qimen_key' in f:
                f={**f,'qimen_chart':data['qimen_charts'][f.get('qimen_keys',{}).get(qimen_method,f['qimen_key'])],
                   'direction_systems':{**f['direction_systems'],'real_beidou':data['sky_samples'][f['sky_sample_key']]}}
            target=[]
            for label,b in [('坐方',mountain)]+[(('本命' if len(lives)==1 else p['name']+'本命'),p['branch']) for p in lives]:
                if not b: continue
                for k,p in f['pillars'].items():
                    target.append({'between':k+'支与'+label,'value':pair(p[1],b)})
                if label=='坐方':
                    for k,v in f['directions'].items():
                        if b in v: target.append({'between':'坐方与'+k,'value':['同位']})
                target.append({'between':'四柱与'+label+'成组','value':groups([p[1] for p in f['pillars'].values()]+[b]) or ['未见完整三合/三会']})
            if mountain:
                for key,vals in f.get('shensha',{}).get('targets',{}).items():
                    rule=data['shensha_catalog'][key]
                    if rule['field']=='direction' and mountain in vals and rule['name'] not in f['directions']:
                        target.append({'between':'坐方与'+rule['scope']+rule['name'],'value':['同位'],'rule_id':key})
            if mountain:
                for p in lives:
                    if p['branch']:target.append({'between':'坐方与'+('本命' if len(lives)==1 else p['name']+'本命'),'value':pair(mountain,p['branch'])})
            for i,a in enumerate(lives):
                for b in lives[i+1:]:
                    if a['branch'] and b['branch']:target.append({'between':a['name']+'与'+b['name']+'本命','value':pair(a['branch'],b['branch'])})
            windows.append({'id':w['id'],'start':w['start'],'end':w['end'],'facts':f,'target_relations':target,
                            'direction_candidates':direction_candidates(f,lives) if not mountain and 'liuren_chart' in f else []})
    if not windows: raise ValueError('No facts for selected month')
    return {'schema':'liuren-election-request/v3','facts_digest':data['facts_digest'],'meta':{**data['meta'],'qimen_method':data['meta'].get('qimen_methods',{}).get(qimen_method,data['meta'].get('qimen_method'))},
            'shensha_catalog':data.get('shensha_catalog',{}),
            'judgment_criteria':data.get('judgment_criteria',{}),
            'context':{'purpose':purpose,'mountain':mountain,'life':life,'lives':lives,'profile':profile,'direction_policy':'ai-required','observer':data['meta'].get('observer'),'qimen_method':qimen_method},
            'instructions':'多个本命逐人核对，再看参与者关系；遗漏本命须待定。未指定用方时，模型为优先/可选时段输出 suggested_direction（branch、reason、evidence），不按吉凶分数或规则程序自动选方；避用/待定说明为何不推荐方位。',
            'month':month,'windows':windows}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--facts',required=True);p.add_argument('--month',required=True)
    for name in ['purpose','mountain','life']: p.add_argument('--'+name,default='')
    p.add_argument('--qimen-method',choices=['chaibu','zhirun'],default='chaibu')
    p.add_argument('--lives',help='JSON file of named participant natal branches')
    p.add_argument('--profile',default='zhongqi/liuren-common');p.add_argument('--output',required=True)
    a=p.parse_args();d=json.loads(Path(a.facts).read_text(encoding='utf-8-sig'))
    lives=json.loads(Path(a.lives).read_text(encoding='utf-8-sig')) if a.lives else None
    req=make_request(d,a.month,a.purpose,a.mountain,a.life,a.profile,lives,a.qimen_method)
    Path(a.output).write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Prepared {len(req["windows"])} factual windows; model judgment pending.')
