"""Named rotating-board Chaibu / Zhirun profiles; factual patterns, never scores.

Zhirun: inclusive nine-day gate threshold, repeat three yuan at Mangzhong / Daxue,
and borrow the incoming lower yuan during Jieqi. Calendar rollover is explicit.
"""
from rules import GAN,ZHI,ALIASES
from datetime import datetime,timedelta
from functools import lru_cache

METHOD='时家转盘·拆补法·天禽寄芮·中五寄坤二'
VERSION='2026-10-07.1'
METHODS={'chaibu':METHOD,'zhirun':'时家转盘·置闰法·九日阈值（含符首日）·接气借下元·天禽寄芮·中五寄坤二'}
ZHIRUN_SOURCE='https://zh.wikisource.org/zh-hant/遁甲演義#超神接氣置閏訣'
SOURCE='https://zh.wikisource.org/wiki/遁甲演義_(四庫全書本)/卷2'
JU_SOURCE='https://zh.wikisource.org/wiki/欽定協紀辨方書_(四庫全書本)/卷35'
RING=[1,8,3,4,9,2,7,6]
PALACE={1:('坎','正北',0,'水','子'),8:('艮','东北',45,'土','丑寅'),3:('震','正东',90,'木','卯'),
        4:('巽','东南',135,'木','辰巳'),9:('离','正南',180,'火','午'),2:('坤','西南',225,'土','未申'),
        7:('兑','正西',270,'金','酉'),6:('乾','西北',315,'金','戌亥'),5:('中','中宫',None,'土','')}
BRANCH_PALACE={b:n for n,v in PALACE.items() for b in v[4]}
STARS={1:'天蓬',2:'天芮',3:'天冲',4:'天辅',5:'天禽',6:'天心',7:'天柱',8:'天任',9:'天英'}
DOORS={1:'休门',8:'生门',3:'伤门',4:'杜门',9:'景门',2:'死门',7:'惊门',6:'开门'}
DOOR_ELEMENT={'休门':'水','生门':'土','伤门':'木','杜门':'木','景门':'火','死门':'土','惊门':'金','开门':'金'}
GODS=['值符','螣蛇','太阴','六合','白虎','玄武','九地','九天']
INSTRUMENTS='戊己庚辛壬癸丁丙乙'
TERM_JU={
 '冬至':(1,[1,7,4]),'小寒':(1,[2,8,5]),'大寒':(1,[3,9,6]),'立春':(1,[8,5,2]),
 '雨水':(1,[9,6,3]),'惊蛰':(1,[1,7,4]),'春分':(1,[3,9,6]),'清明':(1,[4,1,7]),
 '谷雨':(1,[5,2,8]),'立夏':(1,[4,1,7]),'小满':(1,[5,2,8]),'芒种':(1,[6,3,9]),
 '夏至':(-1,[9,3,6]),'小暑':(-1,[8,2,5]),'大暑':(-1,[7,1,4]),'立秋':(-1,[2,5,8]),
 '处暑':(-1,[1,4,7]),'白露':(-1,[9,3,6]),'秋分':(-1,[7,1,4]),'寒露':(-1,[6,9,3]),
 '霜降':(-1,[5,8,2]),'立冬':(-1,[6,9,3]),'小雪':(-1,[5,8,2]),'大雪':(-1,[4,7,1])}
HIDDEN=dict(zip(['甲子','甲戌','甲申','甲午','甲辰','甲寅'],'戊己庚辛壬癸'))
CYCLE=[GAN[i%10]+ZHI[i%12] for i in range(60)]

PATTERN_DEFS={
 '天遁':('天盘丙、生门、地盘丁','朝谒、上书、出行、市贾等原文事类，仍核墓迫'),
 '地遁':('天盘乙、开门、地盘己','营造、安营、守护等原文事类'),
 '人遁':('天盘丁、休门、太阴','隐匿、密谋、和合等原文事类'),
 '神遁':('天盘丙、生门、九天','祭神、建坛、庙宇等原文事类'),
 '鬼遁·歌诀式':('天盘乙、杜门、九地','隐伏、探机、祭祷等原文事类'),
 '风遁·歌诀式':('天盘乙、开休生之一、巽四','顺风行舟等原文事类'),
 '云遁·歌诀式':('天盘乙、开休生之一、地盘辛','祈雨、农稼等原文事类；同时核乙加辛格'),
 '龙遁·坎休乙式':('天盘乙、休门、坎一','祈雨、涉水、河渡等原文事类'),
 '龙遁·休乙加癸条件候选':('天盘乙、休门、地盘癸','原文另说含伏吟文字，含义待辨；只标这三个条件的候选，不宣称完整另说已成立'),
 '虎遁·艮休乙辛式':('天盘乙、地盘辛、休门、艮八','原文歌诀式；招安、设伏、守险等事类'),
 '虎遁·生乙辛另说':('天盘乙、地盘辛、生门','原文又说不强加艮宫条件；不混作休门主式'),
 '虎遁·艮生辛另说':('地盘辛、生门、艮八','原文一云；不臆增天盘乙条件'),
 '三奇吉门会合':('乙丙丁之一与开休生之一同宫','只列会合事实，事项适用性由模型核对'),
}

def pattern_matches(p):
    t=p.get('heaven_stems',[]);e=p['earth_stems'];g=p.get('door');god=p.get('god');n=p['number']
    good=g in ['开门','休门','生门'];out=[]
    checks={
      '天遁':'丙' in t and g=='生门' and '丁' in e,
      '地遁':'乙' in t and g=='开门' and '己' in e,
      '人遁':'丁' in t and g=='休门' and god=='太阴',
      '神遁':'丙' in t and g=='生门' and god=='九天',
      '鬼遁·歌诀式':'乙' in t and g=='杜门' and god=='九地',
      '风遁·歌诀式':'乙' in t and good and n==4,
      '云遁·歌诀式':'乙' in t and good and '辛' in e,
      '龙遁·坎休乙式':'乙' in t and g=='休门' and n==1,
      '龙遁·休乙加癸条件候选':'乙' in t and g=='休门' and '癸' in e,
      '虎遁·艮休乙辛式':'乙' in t and '辛' in e and g=='休门' and n==8,
      '虎遁·生乙辛另说':'乙' in t and '辛' in e and g=='生门',
      '虎遁·艮生辛另说':'辛' in e and g=='生门' and n==8,
      '三奇吉门会合':bool(set(t)&set('乙丙丁')) and good}
    for name,hit in checks.items():
        if hit:
            basis,application=PATTERN_DEFS[name]
            out.append({'name':name,'basis':basis,'application':application,'source':SOURCE,
                        'condition_scope':'条件候选，须辨伏吟文字' if '条件候选' in name else '具名组合条件命中，须继续核墓迫与事类',
                        'evidence':{'palace':n,'heaven_stems':t,'earth_stems':e,'door':g,'god':god}})
    return out

def _overcomes(a,b):return ('木火土金水'.index(b)-'木火土金水'.index(a))%5==2

@lru_cache(maxsize=8)
def zhirun_schedule(year):
    from lunar_python import Solar
    # A disclosed 正授 anchor: 1899-12-07 is 甲午 and 大雪 day.
    # Both 23:00 / 00:00 rollover use the same pillar-date sequence.
    anchor=datetime(1899,12,7)
    events={}
    aliases=ALIASES
    for y in range(1899,year+2):
        for n,t in Solar.fromYmd(y,6,1).getLunar().getJieQiTable().items():
            n=aliases.get(n,n)
            if n in TERM_JU and t.getYear()<=year+1:
                events[(datetime.fromisoformat(t.toYmdHms()),n)]=None
    events=sorted((t,n) for t,n in events if t.date()>=anchor.date())
    start=anchor;out=[]
    for event,term in events:
        lead=(event.date()-start.date()).days
        repeat=term in ('芒种','大雪') and lead>=8
        out.append({'start':start,'end':start+timedelta(days=15),'term':term,'leap':False,'lead_days':lead,'term_time':event})
        start+=timedelta(days=15)
        if repeat:
            out.append({'start':start,'end':start+timedelta(days=15),'term':term,'leap':True,'lead_days':lead,'term_time':event})
            start+=timedelta(days=15)
    return out

def for_time(day,hour,current_term,dt,pillar_date,method='chaibu'):
    if method not in METHODS:raise ValueError('Unknown Qimen method')
    term=current_term;timing=None
    if method=='zhirun':
        if not 1900<=dt.year<=2099:raise ValueError('Zhirun supported years are 1900..2099')
        point=datetime.combine(pillar_date,datetime.min.time())
        slot=next(x for x in reversed(zhirun_schedule(dt.year)) if x['start']<=point<x['end'])
        term=slot['term']
        # In 接气, the term has arrived before its upper head: borrow its lower yuan.
        if not slot['leap'] and term!=current_term and dt>=slot['term_time']:
            term=current_term
        timing={'is_leap':slot['leap'],'cycle_start':slot['start'].date().isoformat(),
                'cycle_end_exclusive':slot['end'].date().isoformat(),'scheduled_term':slot['term'],
                'actual_term':current_term,'lead_days':slot['lead_days'],
                'relation':'闰奇' if slot['leap'] else '超神' if dt<slot['term_time'] else '正授' if slot['lead_days']==0 else '接气' if slot['lead_days']<0 else '符节已交',
                'anchor':'1899-12-07 甲午大雪正授','threshold':'芒种/大雪符首至节日含首尾达到9日及以上，三元完后再重复15日；接气节已到而上元未到，借该节下元。',
                'source':ZHIRUN_SOURCE}
    result=chart(day,hour,term)
    result.update(method=METHODS[method],method_key=method,actual_solar_term=current_term,timing=timing)
    result['scope']='时家转盘；'+('拆补随精确节气换局' if method=='chaibu' else '置闰采用九日阈值（含符首日）和接气借下元口径；不混称其他阈值派法')+'；不等同九星飞宫。格局命中不是通用吉方。'
    return result

def chart(day,hour,term,ju_override=None):
    di=CYCLE.index(day);hi=CYCLE.index(hour)
    fu=CYCLE[di-di%5];fb=fu[1]
    yuan=0 if fb in '子午卯酉' else 1 if fb in '寅申巳亥' else 2
    direction,jus=TERM_JU[term];ju=jus[yuan] if ju_override is None else ju_override
    if not isinstance(ju,int) or not 1<=ju<=9:raise ValueError('Ju must be 1..9')
    earth={(ju-1+i*direction)%9+1:stem for i,stem in enumerate(INSTRUMENTS)}
    xun=CYCLE[hi-hi%10];hidden=HIDDEN[xun]
    xun_palace=next(n for n,s in earth.items() if s==hidden)
    origin=2 if xun_palace==5 else xun_palace
    used=hidden if hour[0]=='甲' else hour[0]
    hour_palace=next(n for n,s in earth.items() if s==used)
    star_target=2 if hour_palace==5 else hour_palace
    star_shift=(RING.index(star_target)-RING.index(origin))%8
    door_raw=(xun_palace-1+direction*(hi%10))%9+1
    door_target=2 if door_raw==5 else door_raw
    door_shift=(RING.index(door_target)-RING.index(origin))%8
    voids=[ZHI[(ZHI.index(xun[1])+10)%12],ZHI[(ZHI.index(xun[1])+11)%12]]
    palaces={n:{'number':n,'trigram':v[0],'name':v[1],'azimuth_deg':v[2],'branches':list(v[4]),
                 'earth_stems':[earth[n]],'heaven_stems':[],'stars':[],'door':None,'god':None,
                 'void_branches':[b for b in v[4] if b in voids]} for n,v in PALACE.items()}
    for i,n in enumerate(RING):
        dest=RING[(i+star_shift)%8];palaces[dest]['stars']=[STARS[n]]+(['天禽'] if n==2 else [])
        palaces[dest]['heaven_stems']=[earth[n]]+([earth[5]] if n==2 else [])
        palaces[RING[(i+door_shift)%8]]['door']=DOORS[n]
    start=RING.index(star_target)
    for i,g in enumerate(GODS):palaces[RING[(start+direction*i)%8]]['god']=g
    palaces[2]['earth_stems'].append(earth[5])
    for n,p in palaces.items():
        p['patterns']=pattern_matches(p);warnings=[]
        if p['door'] and _overcomes(DOOR_ELEMENT[p['door']],PALACE[n][3]):warnings.append('门迫（门克宫）')
        for stem in p['heaven_stems']:
            if {'戊':3,'己':2,'庚':8,'辛':9,'壬':4,'癸':4}.get(stem)==n:warnings.append(stem+'仪击刑')
            if {'乙':2,'丙':6,'丁':6}.get(stem)==n:warnings.append(stem+'奇入墓（武经说）')
        if '乙' in p['heaven_stems'] and '辛' in p['earth_stems']:warnings.append('乙加辛（青龙逃走）')
        if '辛' in p['heaven_stems'] and '乙' in p['earth_stems']:warnings.append('辛加乙（白虎猖狂）')
        p['warnings']=warnings
        for match in p['patterns']:match['palace_warnings']=warnings[:]
    return {'method':METHOD,'version':VERSION,'solar_term':term,'dun':'阳遁' if direction==1 else '阴遁',
            'ju':ju,'yuan':['上元','中元','下元'][yuan],'fu_head':fu,'hour_xun':xun,'hidden_jia':hidden,
            'zhi_fu':STARS[xun_palace],'zhi_fu_palace':star_target,'zhi_shi':DOORS[origin],
            'zhi_shi_palace':door_target,'hour_void':voids,'palaces':[palaces[n] for n in range(1,10)],
            'source':JU_SOURCE,'scope':'该拆补转盘口径；不等同置闰法或九星飞宫法。格局命中不是通用吉方。'}
