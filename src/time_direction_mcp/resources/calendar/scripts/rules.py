"""Fixed rule facts. No suitability scores and no automatic auspiciousness verdict."""
from itertools import combinations

VERSION = '2026-10-07.1'
GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
ELEMENT = dict(zip(GAN + ZHI, '木木火火土土金金水水' + '水土木木土火火土金金土水'))
HIDDEN = dict(zip(ZHI, ['癸','己癸辛','甲丙戊','乙','戊乙癸','丙戊庚','丁己','己丁乙','庚壬戊','辛','戊辛丁','壬甲']))
LU = dict(zip(GAN, '寅卯巳午巳午申酉亥子'))
DAY_DE = dict(zip(GAN, '寅申巳亥巳寅申巳亥巳'))
GAN_HE = [('甲','己','土'),('乙','庚','金'),('丙','辛','水'),('丁','壬','木'),('戊','癸','火')]
LIU_HE = [('子','丑','土'),('寅','亥','木'),('卯','戌','火'),('辰','酉','金'),('巳','申','水'),('午','未','土')]
SAN_HE = [('申子辰','水'),('亥卯未','木'),('寅午戌','火'),('巳酉丑','金')]
SAN_HUI = [('亥子丑','水'),('寅卯辰','木'),('巳午未','火'),('申酉戌','金')]
HAI = ['子未','丑午','寅巳','卯辰','申亥','酉戌']
PO = ['子酉','丑辰','寅亥','卯午','巳申','未戌']
XING = [('寅','巳'),('巳','申'),('申','寅'),('丑','戌'),('戌','未'),('未','丑'),('子','卯'),('卯','子')]
SELF_XING = '辰午酉亥'
JIAN = ['建','除','满','平','定','执','破','危','成','收','开','闭']
GODS = ['青龙','明堂','天刑','朱雀','金匮','宝光','白虎','玉堂','天牢','玄武','司命','勾陈']
YELLOW = {0,1,4,5,7,10}
# 寅申起子、卯酉起寅、辰戌起辰、巳亥起午、子午起申、丑未起戌。
QING_START = dict(zip(ZHI, [8,10,0,2,4,6,8,10,0,2,4,6]))
TIAN_DE = dict(zip('寅卯辰巳午未申酉戌亥子丑', '丁申壬辛亥甲癸寅丙乙巳庚'))
TIAN_DE_HE = dict(zip('寅卯辰巳午未申酉戌亥子丑', ['壬',None,'丁','丙',None,'己','戊',None,'辛','庚',None,'乙']))
YUE_DE = {b:g for group,g in [('寅午戌','丙'),('申子辰','壬'),('亥卯未','甲'),('巳酉丑','庚')] for b in group}
GAN_PARTNER = {a:b for a,b,_ in GAN_HE} | {b:a for a,b,_ in GAN_HE}
WU_BU_YU = dict(zip(GAN, [('庚午',),('辛巳',),('壬辰',),('癸卯',),('甲寅',),('乙丑','乙亥'),('丙子','丙戌'),('丁酉',),('戊申',),('己未',)]))
# Deliberate named alternatives: never silently interchange these tables.
NOBLE = {
 'liuren-common': {'name':'六壬常用昼丑夜未口径', 'day':dict(zip(GAN,'丑子亥亥丑子丑午巳巳')), 'night':dict(zip(GAN,'未申酉酉未申未寅卯卯'))},
 'xieji': {'name':'协纪阳贵未、阴贵丑口径', 'day':dict(zip(GAN,'未申酉亥丑子丑寅卯巳')), 'night':dict(zip(GAN,'丑子亥酉未申未午巳卯'))},
}
ZHONG_QI = dict(zip(['雨水','春分','谷雨','小满','夏至','大暑','处暑','秋分','霜降','小雪','冬至','大寒'], '亥戌酉申未午巳辰卯寅丑子'))
ALIASES = {'DONG_ZHI':'冬至','DA_HAN':'大寒','YU_SHUI':'雨水'}

JUDGMENT_CRITERIA = {
 'joint_direction':{
   'name':'六壬、奇门与北斗方位综合',
   'basis':'逐方核对奇门星门神、天地盘干与具名格局条件，再核六壬天将、贵人所临及式盘斗柄、全部本命关系。',
   'judgment':'主式与另说不混用；龙遁虎遁等原有事类用途，不能命中格名便定一切有利。门迫、击刑、旬空和他法冲突须解释，不按分数累加。贵人方不自动优于其他方。',
   'astronomy':'没有经纬度不计算真实星空；七星地平坐标是物理定位，不直接推出吉方。星空为具体时刻快照，引用真实七星择方须注明观测时刻与视界、昼光条件。',
   'scope':'盘法和真实天文分别提供证据，实际适用性由模型按事项裁决。',
   'source':'https://zh.wikisource.org/wiki/遁甲演義_(四庫全書本)/卷2'
 },
 'rilu_ride': {
  'name':'日禄与日德', 'source':'https://zh.wikisource.org/wiki/六壬大全/1',
  'basis':'日德按甲乙丙丁戊己庚辛壬癸取寅申巳亥巳寅申巳亥巳；阳干取本干禄，阴干取所合阳干之禄。日禄另按十干临官表。',
  'evidence_fields':['lu','lu_ground','day_de','sky','pillars.日','pillars.时','tags'],
  'judgment':'区分时支见日禄/日德与天盘禄德所临地盘。日德的生旺、旬空、受制仍须结合事实讨论，不因出现德字自动判适合。',
  'limits':'时支见德不是德临日、入传或发用；需核对现已提供的四课三传事实，不得仅凭时支相见断德入传或鬼德格。'
 },
 'gangsai_guihu': {
  'name':'罡塞鬼户',
  'source':'https://zh.wikisource.org/wiki/六壬大全/12',
  'basis':'辰为天罡，寅为鬼户；天盘辰加地盘寅即成立，不论在传不在传。',
  'evidence_fields':['gangsai','patterns.gangsai_guihu','sky.寅','jiang','noble','guideng'],
  'application':'原文列闪灾避难、阴谋私祷、吊丧问病、合药书符；转为择时参考时须说明与所办事项的关联。',
  'enhancement':'原文说甲戊庚日尤的、辰月将尤妙；昼贵登天门是否同时成立，必须依选定贵人表与实际昼夜核验，不凭日干自动推出。',
  'judgment':'逐时段核对成立与否；成立时按事类作为护场避凶依据，同时讨论五不遇时、冲山冲命及其他冲突，不自动给通用大吉或加减分。',
  'limits':'格局成立不要求入传；现已提供四课三传，需实际核对后才能进一步论三传皆鬼或完整斩关课。'
 }
}

def opposite(b):
    return ZHI[(ZHI.index(b)+6)%12]

def god(base, target):
    i = (ZHI.index(target)-QING_START[base])%12
    return {'name':GODS[i], 'path':'黄道' if i in YELLOW else '黑道', 'basis':f'{base}起青龙于{ZHI[QING_START[base]]}'}

def hour_pillar(day_gan, hour_zhi):
    return GAN[(GAN.index(day_gan)%5*2+ZHI.index(hour_zhi))%10]+hour_zhi

def voids(pillar):
    i = next(i for i in range(60) if GAN[i%10]+ZHI[i%12] == pillar)
    first = i//10*10
    return ''.join(ZHI[(first+10+k)%12] for k in range(2))

def pair(a,b):
    """Names are facts; 合化 is a possibility, never a proven transformation."""
    out=[]
    if a in GAN and b in GAN:
        for x,y,e in GAN_HE:
            if {a,b}=={x,y}: out.append(f'五合（{e}，未判合化）')
    if a in ZHI and b in ZHI:
        if opposite(a)==b: out.append('六冲')
        for x,y,e in LIU_HE:
            if {a,b}=={x,y}: out.append(f'六合（{e}，未判合化）')
        if a!=b:
            for g,e in SAN_HE:
                if set(a+b)<=set(g): out.append(f'三合两支（{g}{e}，缺支未成全局）')
            for g,e in SAN_HUI:
                if set(a+b)<=set(g): out.append(f'三会两支（{g}{e}，缺支未成全局）')
        if any(set(a+b)==set(p) for p in HAI): out.append('六害')
        if any(set(a+b)==set(p) for p in PO): out.append('六破')
        if (a,b) in XING: out.append(f'{a}刑{b}')
        if a==b and a in SELF_XING: out.append('自刑（复见条件，强弱待判）')
    if a==b: out.append('同气')
    ea,eb=ELEMENT[a],ELEMENT[b]
    cycle='木火土金水'
    delta=(cycle.index(eb)-cycle.index(ea))%5
    out.append(['五行比和',f'{a}生{b}',f'{a}克{b}',f'{b}克{a}',f'{b}生{a}'][delta])
    return out

def groups(branches):
    s=set(branches)
    return [f'{g}{typ}（{e}，未判合化）' for table,typ in [(SAN_HE,'三合齐备'),(SAN_HUI,'三会齐备')] for g,e in table if set(g)<=s]

def sansha(b):
    return next(v for group,v in [('申子辰','巳午未'),('寅午戌','亥子丑'),('亥卯未','申酉戌'),('巳酉丑','寅卯辰')] if b in group)

def horse(b):
    return next(v for g,v in [('申子辰','寅'),('寅午戌','申'),('亥卯未','巳'),('巳酉丑','亥')] if b in g)

def fixed_facts(year,month,day,hour,jiang,daytime,noble_profile):
    yg,mg,dg,hg = [x[0] for x in [year,month,day,hour]]
    yb,mb,db,hb = [x[1] for x in [year,month,day,hour]]
    noble=NOBLE[noble_profile]['day' if daytime else 'night'][dg]
    sky={b:ZHI[(ZHI.index(b)+ZHI.index(jiang)-ZHI.index(hb))%12] for b in ZHI}
    noble_ground=ZHI[(ZHI.index(noble)-ZHI.index(jiang)+ZHI.index(hb))%12]
    td,md=TIAN_DE[mb],YUE_DE[mb]
    tags=[]
    if dg==td or db==td: tags.append('天德日')
    if dg==TIAN_DE_HE[mb]: tags.append('天德合日')
    if dg==md: tags.append('月德日')
    if dg==GAN_PARTNER[md]: tags.append('月德合日')
    if hg==td or hb==td: tags.append('天德到时')
    if hg==TIAN_DE_HE[mb]: tags.append('天德合到时')
    if hg==md: tags.append('月德到时')
    if hg==GAN_PARTNER[md]: tags.append('月德合到时')
    if hb==LU[dg]: tags.append('日禄到时')
    if hb==DAY_DE[dg]: tags.append('时支见日德')
    if hb==horse(db): tags.append('日马到时')
    if hb in {NOBLE[noble_profile]['day'][dg],NOBLE[noble_profile]['night'][dg]}: tags.append('时支见天乙（另核昼夜）')
    if noble_ground=='亥': tags.append('贵登天门')
    gangsai=sky['寅']=='辰'
    if gangsai: tags.append('罡塞鬼户')
    if hour in WU_BU_YU[dg]: tags.append('五不遇时')
    if hb in voids(day): tags.append('时支落日旬空')
    if hb==opposite(db): tags.append('日破时')
    if db==opposite(mb): tags.append('月破日（与建除破同源）')
    pillars={'年':year,'月':month,'日':day,'时':hour}
    relations=[]
    for (ka,pa),(kb,pb) in combinations(pillars.items(),2):
        relations += [{'between':ka+kb,'stems':pair(pa[0],pb[0]),'branches':pair(pa[1],pb[1])}]
    return {'pillars':pillars,'elements':{k:[ELEMENT[p[0]],ELEMENT[p[1]]] for k,p in pillars.items()},
        'hidden_stems':{k:HIDDEN[p[1]] for k,p in pillars.items()},
        'jianchu':JIAN[(ZHI.index(db)-ZHI.index(mb))%12], 'day_god':god(mb,db),'hour_god':god(db,hb),
        'directions':{'太岁':yb,'岁破':opposite(yb),'年三煞':sansha(yb),'月建':mb,'月破':opposite(mb),'月三煞':sansha(mb)},
        'de':{'天德':td,'天德合':TIAN_DE_HE[mb],'月德':md,'月德合':GAN_PARTNER[md]},
        'lu':LU[dg],'lu_ground':next(b for b,v in sky.items() if v==LU[dg]),
        'day_de':{'branch':DAY_DE[dg],'ground':next(b for b,v in sky.items() if v==DAY_DE[dg]),
                  'at_hour_branch':hb==DAY_DE[dg],'in_day_void':DAY_DE[dg] in voids(day)},
        'horse':horse(db),'void':voids(day), 'wubuyu':hour in WU_BU_YU[dg],
        'noble':{'branch':noble,'phase':'昼贵' if daytime else '夜贵','profile':noble_profile,'ground':noble_ground},
        'jiang':jiang,'sky':sky,'guideng':noble_ground=='亥','gangsai':gangsai,
        'patterns':{'gangsai_guihu':{'matched':gangsai,'actual_sky_at_yin':sky['寅'],
            'ground_branch':'寅','required_sky_branch':'辰','requires_transmission':False,
            'jia_wu_geng_day':dg in '甲戊庚','chen_general':jiang=='辰',
            'with_day_guideng':gangsai and daytime and noble_ground=='亥'}},
        'tags':tags,'relations':relations,'groups':groups([yb,mb,db,hb])}
