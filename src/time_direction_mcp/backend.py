import calendar as _stdlib_calendar  # Do not shadow stdlib calendar with resources.
import importlib.util,json,os,re,sys,tempfile,uuid
from datetime import datetime as DateTime,timezone,timedelta
from pathlib import Path
from functools import lru_cache

RESOURCE_ROOT=Path(__file__).resolve().parent/'resources/calendar'

@lru_cache(maxsize=1)
def engine():
    scripts=RESOURCE_ROOT/'scripts'
    sys.path.insert(0,str(scripts))
    spec=importlib.util.spec_from_file_location('_time_direction_calendar_engine',scripts/'calendar.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module

def parse_time(value,input_timezone='Asia/Shanghai'):
    dt=DateTime.fromisoformat(value.replace('Z','+00:00'))
    if not 1900<=dt.year<=2099:raise ValueError('Supported chart years are 1900..2099')
    if dt.tzinfo is None:
        if input_timezone=='Asia/Shanghai':zone=timezone(timedelta(hours=8))
        elif input_timezone=='UTC':zone=timezone.utc
        else:
            from zoneinfo import ZoneInfo
            zone=ZoneInfo(input_timezone)
        dt=dt.replace(tzinfo=zone)
    local=dt.astimezone(timezone(timedelta(hours=8))).replace(tzinfo=None)
    if not 1900<=local.year<=2099:raise ValueError('Supported Beijing chart years are 1900..2099')
    return dt,local

def get_direction_facts(datetime,purpose='',participants=None,observer=None,noble_profile='liuren-common',rollover='zi',input_timezone='Asia/Shanghai',qimen_method='chaibu',mountain=''):
    e=engine();absolute,chart_time=parse_time(datetime,input_timezone)
    if mountain not in ['',*e.ZHI]:raise ValueError('Only twelve-branch directions are supported')
    if noble_profile not in e.NOBLE or rollover not in ['zi','midnight']:raise ValueError('Unknown named chart profile')
    f=e.calc(chart_time,noble_profile=noble_profile,rollover=rollover,qimen_method=qimen_method)
    wrapper={'meta':{},'days':[{'windows':[{'profiles':{noble_profile:f}}]}]};e.attach_liuren(wrapper)
    f['liuren_chart']=wrapper['liuren_charts'][f['liuren_key']]
    from astronomy import positions_many
    from participants import normalize_lives,direction_candidates
    lives=normalize_lives(lives=participants)
    f['direction_systems']['real_beidou']=positions_many([absolute],observer)[0]
    return {'schema':'time-direction-facts/v1','requested_time':absolute.isoformat(),'chart_time_beijing':chart_time.isoformat(),
      'context':{'purpose':purpose,'participants':lives,'noble_profile':noble_profile,'rollover':rollover,'qimen_method':qimen_method,'mountain':mountain},
      'facts':f,'direction_candidates':direction_candidates(f,lives),'judgment_criteria':e.JUDGMENT_CRITERIA,
      'instructions':'逐方结合事类、全部本命、奇门主式/另说与冲突、六壬贵人及斗柄、真实星空条件；不得评分自动选方。没有观测点不推真实七星方位。'}

def get_qimen_chart(datetime,input_timezone='Asia/Shanghai',rollover='zi',qimen_method='chaibu'):
    e=engine();_,local=parse_time(datetime,input_timezone)
    if rollover not in ['zi','midnight']:raise ValueError('Unknown rollover')
    return e.calc(local,rollover=rollover,qimen_method=qimen_method)['qimen_chart']

def get_beidou_sky(datetime,observer,input_timezone='Asia/Shanghai'):
    engine();absolute,_=parse_time(datetime,input_timezone)
    from astronomy import positions_many
    if observer is None:raise ValueError('Observer latitude and longitude are required')
    return positions_many([absolute],observer)[0]

def output_root():
    configured=os.environ.get('TIME_DIRECTION_OUTPUT_ROOT')
    return Path(configured).resolve() if configured else (Path(tempfile.gettempdir())/'time-direction-mcp').resolve()

def artifact_dir(artifact_id):
    if not re.fullmatch(r'[0-9a-f]{12}',artifact_id):raise ValueError('Invalid artifact id')
    root=output_root();p=(root/artifact_id).resolve()
    if p.parent!=root or not p.is_dir():raise ValueError('Artifact not found under configured output root')
    return p

def build_election_request(start,days=7,purpose='',participants=None,observer=None,noble_profile='liuren-common',rollover='zi',qimen_method='chaibu',mountain=''):
    if not isinstance(days,int) or isinstance(days,bool) or not 1<=days<=7:raise ValueError('Request batches must be 1..7 days')
    e=engine();_,local=parse_time(start)
    if noble_profile not in e.NOBLE or rollover not in ['zi','midnight'] or qimen_method not in e.QIMEN_METHODS:raise ValueError('Unknown named chart profile')
    if mountain not in ['',*e.ZHI]:raise ValueError('Only twelve-branch directions are supported')
    if (local+timedelta(days=days-1)).year>2099:raise ValueError('Request range exceeds supported chart years')
    if local.time()!=DateTime.min.time():raise ValueError('start must be a date or midnight in Beijing time')
    from review_request import make_request
    from participants import normalize_lives
    lives=normalize_lives(lives=participants)
    data=e.build(local,days,rollover=rollover,observer=observer)
    if qimen_method not in e.QIMEN_METHODS:raise ValueError('Unknown Qimen method')
    data['meta']['initial_qimen_method']=qimen_method
    data['facts_digest']=e.digest({k:v for k,v in data.items() if k!='facts_digest'})
    requests=[make_request(data,m,purpose=purpose,profile='zhongqi/'+noble_profile,lives=lives,qimen_method=qimen_method,mountain=mountain) for m in sorted({d['date'][:7] for d in data['days']})]
    request=requests[0];request['windows']=[w for req in requests for w in req['windows']]
    request['range']={'start':start,'days':days};request['month']=None
    ident=uuid.uuid4().hex[:12];root=output_root();root.mkdir(parents=True,exist_ok=True);out=root/ident;out.mkdir()
    e.write_json(out/'facts.json',data);e.write_json(out/'request.json',request);e.render(data,out/'择时日历.html',initial_context=request['context'])
    return {'artifact_id':ident,'request_path':str(out/'request.json'),'html_path':str(out/'择时日历.html'),
      'facts_digest':data['facts_digest'],'window_count':len(request['windows']),'context':request['context'],
      **_preview_fields(out),
      'next_step':'Use read_election_windows in small batches; model writes verdicts and directions; then render_election_calendar.'}

def build_year_election(year,purpose='',participants=None,observer=None,noble_profile='liuren-common',rollover='zi',qimen_method='chaibu',mountain=''):
    if not isinstance(year,int) or isinstance(year,bool) or not 1900<=year<=2099:raise ValueError('year must be integer in 1900..2099')
    e=engine()
    if noble_profile not in e.NOBLE or rollover not in ['zi','midnight'] or qimen_method not in e.QIMEN_METHODS:raise ValueError('Unknown named chart profile')
    from review_request import make_request
    from participants import normalize_lives
    lives=normalize_lives(lives=participants)
    start=DateTime(year,1,1);days=(DateTime(year+1,1,1)-start).days
    data=e.build(start,days,rollover=rollover,observer=observer)
    data['meta']['initial_qimen_method']=qimen_method
    data['facts_digest']=e.digest({k:v for k,v in data.items() if k!='facts_digest'})
    first=data['days'][0]['windows'][0]['id']
    request=make_request(data,f'{year}-01',purpose=purpose,profile='zhongqi/'+noble_profile,lives=lives,qimen_method=qimen_method,mountain=mountain,window_ids={first})
    request['windows']=[{k:w[k] for k in ['id','start','end']} for d in data['days'] for w in d['windows']]
    request['window_index_only']=True;request['range']={'year':year,'start':start.date().isoformat(),'days':days};request['month']=None
    ident=uuid.uuid4().hex[:12];root=output_root();root.mkdir(parents=True,exist_ok=True);out=root/ident;out.mkdir()
    e.write_json(out/'facts.json',data);e.write_json(out/'request.json',request);e.render(data,out/'择时日历.html',initial_context=request['context'])
    return {'artifact_id':ident,'year':year,'days':days,'months':12,'window_count':len(request['windows']),
            'facts_digest':data['facts_digest'],'context':request['context'],'html_path':str(out/'择时日历.html'),
            'request_path':str(out/'request.json'),**_preview_fields(out),'next_step':'Read windows in batches with read_election_windows. Submit each reviewed batch via render_election_calendar; judgments accumulate until coverage is complete.'}

@lru_cache(maxsize=1)
def _stored_facts(path,mtime):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def read_election_windows(artifact_id,offset=0,limit=7):
    if not isinstance(offset,int) or isinstance(offset,bool) or offset<0 or not isinstance(limit,int) or isinstance(limit,bool) or not 1<=limit<=14:raise ValueError('offset >=0, limit 1..14')
    p=artifact_dir(artifact_id);r=json.loads((p/'request.json').read_text(encoding='utf-8'))
    windows=r['windows'][offset:offset+limit]
    if r.get('window_index_only') and windows:
        engine()  # A fresh server has not yet made the bundled modules importable.
        from review_request import make_request
        fpath=p/'facts.json';data=_stored_facts(str(fpath),fpath.stat().st_mtime_ns);context=r['context'];ids={w['id'] for w in windows}
        expanded=[]
        for month in sorted({w['id'][:7] for w in windows}):
            batch=make_request(data,month,purpose=context['purpose'],mountain=context['mountain'],profile=context['profile'],lives=context['lives'],qimen_method=context['qimen_method'],window_ids=ids)
            expanded.extend(batch['windows'])
        windows=expanded
    return {'artifact_id':artifact_id,'facts_digest':r['facts_digest'],'context':r['context'],'total_windows':len(r['windows']),
            'offset':offset,'next_offset':offset+len(windows),'has_more':offset+len(windows)<len(r['windows']),
            'windows':windows,'judgment_criteria':r['judgment_criteria'],'instructions':r['instructions']}

def render_election_calendar(artifact_id,review):
    e=engine();p=artifact_dir(artifact_id)
    fpath=p/'facts.json';data=_stored_facts(str(fpath),fpath.stat().st_mtime_ns);request=json.loads((p/'request.json').read_text(encoding='utf-8'))
    if review.get('context')!=request['context']:raise ValueError('Review context must match this artifact request exactly')
    e.validate_review(review,data)
    valid={w['id'] for w in request['windows']}
    if any(x['id'] not in valid for x in review['decisions']):raise ValueError('Review windows must belong to this request batch')
    review_path=p/'review.json';prior={}
    if review_path.exists():
        previous=json.loads(review_path.read_text(encoding='utf-8'))
        if previous.get('facts_digest')!=review['facts_digest'] or previous.get('context')!=review['context']:raise ValueError('Stored review context differs; regenerate the artifact')
        e.validate_review(previous,data);prior={x['id']:x for x in previous['decisions']}
    added=sum(x['id'] not in prior for x in review['decisions'])
    prior.update({x['id']:x for x in review['decisions']})
    merged={**review,'decisions':sorted(prior.values(),key=lambda x:x['id'])}
    merged['coverage']={**merged.get('coverage',{}),'year':request.get('range',{}).get('year'),
                        'reviewed_windows':len(prior),'total_windows':len(valid),'complete':len(prior)==len(valid)}
    e.validate_review(merged,data)
    e.write_json(review_path,merged);e.render(data,p/'择时日历.html',merged)
    return {'artifact_id':artifact_id,'html_path':str(p/'择时日历.html'),'review_path':str(review_path),
      **_preview_fields(p),'newly_reviewed_windows':added,'reviewed_windows':len(prior),'requested_windows':len(valid),'complete':len(prior)==len(valid)}


def _preview_fields(folder):
    from .preview import calendar_url
    try:return {'preview_url':calendar_url(folder),'preview_lifetime':'MCP server process; reopen with preview_election_calendar after a restart'}
    except (OSError,ValueError) as error:return {'preview_error':str(error),'preview_fallback':'Use html_path and keep all .data.js files beside it'}

def preview_election_calendar(artifact_id):
    folder=artifact_dir(artifact_id)
    result={'artifact_id':artifact_id,'html_path':str(folder/'择时日历.html'),**_preview_fields(folder)}
    if (folder/'review.json').is_file():
        review=json.loads((folder/'review.json').read_text(encoding='utf-8'))
        result['coverage']=review.get('coverage',{})
    return result


def restore_previews():
    from .preview import restore_registered
    try:return restore_registered(output_root())
    except (OSError,ValueError):return 0
