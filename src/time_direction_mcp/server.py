"""MCP standard UTF-8 JSON-RPC stdio transport, with optional loopback calendar preview and no credentials.

Implements initialize/initialized, ping, tools/list and tools/call.  This is a
small dedicated stdio server, not an HTTP or general-purpose MCP framework.
Protocol reference: modelcontextprotocol.io/specification/2025-11-25
"""
import json,sys,inspect
from . import backend,__version__

OBSERVER={'type':'object','properties':{'latitude':{'type':'number','minimum':-90,'maximum':90},
 'longitude':{'type':'number','minimum':-180,'maximum':180},'elevation_m':{'type':'number','default':0},'label':{'type':'string'}},
 'required':['latitude','longitude'],'additionalProperties':False}
PEOPLE={'type':'array','maxItems':6,'items':{'type':'object','properties':{'name':{'type':'string'},'branch':{'type':'string','enum':['','子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']}},'required':['name','branch'],'additionalProperties':False}}
TIME={'datetime':{'type':'string','description':'ISO 8601; naive times use input_timezone; chart clock explicitly converts to Beijing civil time.'},'input_timezone':{'type':'string','default':'Asia/Shanghai'}}
QIMEN={'type':'string','enum':['chaibu','zhirun'],'default':'chaibu','description':'拆补法 / 置闰法（九日含符首、接气借下元）'}
DIRECTION={'type':'string','enum':['','子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'],'default':''}
TOOLS=[];FUNCTIONS={}
def register(name,description,props,required,readonly=True):
    FUNCTIONS[name]=getattr(backend,name)
    TOOLS.append({'name':name,'description':description,'inputSchema':{'type':'object','properties':props,'required':required,'additionalProperties':False},
      'annotations':{'readOnlyHint':readonly,'destructiveHint':False,'openWorldHint':False}})

register('get_qimen_chart','奇门时家转盘拆补/置闰局：星门神、天地干、主式和另说格局与警示；不自动判吉。',
         {**TIME,'qimen_method':QIMEN,'rollover':{'type':'string','enum':['zi','midnight'],'default':'zi'}},['datetime'])
register('get_beidou_sky','按每次请求的经纬度计算真实北斗七星几何方位/高度与地平线状态；没有默认城市。',
         {**TIME,'observer':OBSERVER},['datetime','observer'])
register('get_direction_facts','联合六壬完整式盘、奇门、贵人方、式盘斗柄、可选真实七星及每个本命；只给证据和候选，不给分数。',
         {**TIME,'purpose':{'type':'string'},'mountain':DIRECTION,'participants':PEOPLE,'observer':OBSERVER,
          'noble_profile':{'type':'string','enum':['liuren-common','xieji']},'qimen_method':QIMEN,'rollover':{'type':'string','enum':['zi','midnight']}},['datetime'])
register('build_election_request','生成1至7日的联合择时判断材料及离线HTML；逐批读材料后由模型裁决。跨月不会漏掉窗口。',
         {'start':{'type':'string'},'days':{'type':'integer','minimum':1,'maximum':7},'purpose':{'type':'string'},'mountain':DIRECTION,'participants':PEOPLE,
          'observer':OBSERVER,'noble_profile':{'type':'string','enum':['liuren-common','xieji']},'qimen_method':QIMEN,'rollover':{'type':'string','enum':['zi','midnight']}},['start'],False)
register('build_year_election','生成完整公历年度365/366日择时事实及按月加载的HTML；模型逐批判断，回填累积全年覆盖。没有默认观测城市。',
         {'year':{'type':'integer','minimum':1900,'maximum':2099},'purpose':{'type':'string'},'mountain':DIRECTION,'participants':PEOPLE,
          'observer':OBSERVER,'noble_profile':{'type':'string','enum':['liuren-common','xieji']},'qimen_method':QIMEN,'rollover':{'type':'string','enum':['zi','midnight']}},['year'],False)
register('read_election_windows','读取已生成材料中的小批次窗口；每窗包含完整式盘、方位候选和判断规则。',
         {'artifact_id':{'type':'string'},'offset':{'type':'integer','minimum':0},'limit':{'type':'integer','minimum':1,'maximum':14}},['artifact_id'])
register('render_election_calendar','合并本批与已保存判断，逐批累积；校验模型判断与全部参与者、观测点和事实版本一致后回填HTML；未指定用方的可用段必须附建议方位。',
         {'artifact_id':{'type':'string'},'review':{'type':'object'}},['artifact_id','review'],False)

register('preview_election_calendar','恢复已生成日历的本机HTTP预览；只开放该日历及配套数据脚本。MCP重启后可再次取地址，文件仍可离线打开。',{'artifact_id':{'type':'string'}},['artifact_id'],False)

def main():
    sys.stdin.reconfigure(encoding='utf-8');sys.stdout.reconfigure(encoding='utf-8')
    backend.restore_previews()
    initialized=False;ready=False;protocol='2025-11-25'
    for line in sys.stdin:
        if len(line)>16*1024*1024:continue
        ident=None
        try:req=json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Parse error'}}),flush=True);continue
        if not isinstance(req,dict) or req.get('jsonrpc')!='2.0':
            print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Invalid request'}}),flush=True);continue
        try:
            ident=req.get('id')
            method=req.get('method');params=req.get('params',{})
            if not isinstance(params,dict):raise ValueError('Params must be object')
            if not isinstance(method,str):raise ValueError('Method must be string')
            if method=='notifications/initialized':ready=initialized;continue
            if ident is None:continue
            if method=='initialize':
                offered=params.get('protocolVersion');protocol=offered if offered in ['2024-11-05','2025-03-26','2025-11-25'] else '2025-11-25'
                initialized=True
                result={'protocolVersion':protocol,'capabilities':{'tools':{'listChanged':False}},
                        'serverInfo':{'name':'time-direction-mcp','version':__version__},
                        'instructions':'Use the bundled time-direction-election skill for election workflows: build a request or year, read small batches, judge each window, then render; reviews accumulate. Copy facts_digest and context unchanged. Keep fixed chart facts, physical astronomy, and model judgment separate. No scores or automatic auspicious verdicts. Observer coordinates are required for real sky.'}
            elif method=='ping':result={}
            elif not ready:
                raise ValueError('Initialize and send notifications/initialized first')
            elif method=='tools/list':result={'tools':TOOLS}
            elif method=='tools/call':
                name=params.get('name');args=params.get('arguments',{})
                if name not in FUNCTIONS:raise ValueError('Unknown tool')
                try:
                    if not isinstance(args,dict):raise ValueError('Tool arguments must be object')
                    inspect.signature(FUNCTIONS[name]).bind(**args)
                    data=FUNCTIONS[name](**args)
                    result={'content':[{'type':'text','text':json.dumps(data,ensure_ascii=False,allow_nan=False)}],'isError':False}
                    if protocol!='2024-11-05':result['structuredContent']=data
                except Exception as e:result={'content':[{'type':'text','text':str(e)}],'isError':True}
            else:
                response={'jsonrpc':'2.0','id':ident,'error':{'code':-32601,'message':'Method not supported'}}
                print(json.dumps(response,ensure_ascii=False),flush=True);continue
            response={'jsonrpc':'2.0','id':ident,'result':result}
        except (ValueError,TypeError,AttributeError) as e:
            response={'jsonrpc':'2.0','id':ident,'error':{'code':-32602,'message':str(e)}}
        print(json.dumps(response,ensure_ascii=False,allow_nan=False,separators=(',',':')),flush=True)

if __name__=='__main__':main()
