"""Source-bound election facts. Names and matches never imply suitability.

Month tables use the project's explicitly chosen solar-term month, not lunar
month numbers. Direction rules never become day/hour bans merely by sharing a
branch. Corrected Xieji tables take precedence over the old tables it quotes.
"""
from datetime import timedelta
from rules import GAN, ZHI, ELEMENT, LU, GAN_PARTNER, XING, SELF_XING, HAI, horse, voids

MONTHS = '寅卯辰巳午未申酉戌亥子丑'
SEASONS = ['春', '夏', '秋', '冬']
LIS = {'立春', '立夏', '立秋', '立冬'}
FENZHI = {'春分', '夏至', '秋分', '冬至'}
JIES = ['立春','惊蛰','清明','立夏','芒种','小暑','立秋','白露','寒露','立冬','大雪','小寒']
CYCLE = [GAN[i % 10] + ZHI[i % 12] for i in range(60)]
SOURCE = 'https://zh.wikisource.org/wiki/欽定協紀辨方書_(四庫全書本)/卷'
CATALOG = {}
RULES = []


def add(name, scope, field, fn, volume, basis, note='', alias=''):
    key = scope + '.' + name
    if key in CATALOG: raise ValueError('Duplicate rule: ' + key)
    CATALOG[key] = {'name':name, 'scope':scope, 'field':field,
                    'source':SOURCE + f'{volume:02}', 'basis':basis,
                    'note':note, 'alias':alias}
    RULES.append((key, field, fn))


def values(v):
    if isinstance(v, list): return v
    return [] if v is None or v == '' else [v]


def month(name, table, field='branch', volume=6, note='', alias=''):
    entries = list(table) if isinstance(table, str) else table
    if len(entries) != 12: raise ValueError(name + ': expected 12 months')
    add(name, '月神', field, lambda e,t=entries:values(t[e['mi']]), volume,
        '按节月寅至丑依次取：' + '；'.join('/'.join(values(v)) or '无' for v in entries), note, alias)


def seasonal(name, table, field='branch', note='', alias=''):
    add(name, '四时', field, lambda e,t=table:values(t[e['si']]), 5,
        '春夏秋冬依次取：' + '；'.join('/'.join(values(v)) for v in table), note, alias)


def step(b,n): return ZHI[(ZHI.index(b)+n)%12]
def trine(b,targets):
    return next(v for g,v in targets if b in g)
def penalty(b):
    return [y for x,y in XING if x == b] + ([b] if b in SELF_XING else [])


# Year directions (not day prohibitions).
for name,n,alias in [('太岁',0,''),('岁破',6,'大耗'),('岁支德',5,''),
                     ('丧门',2,''),('太阴',-2,'吊客'),('官符',4,'畜官'),
                     ('岁白虎',-4,''),('病符',-1,''),('死符',5,'小耗')]:
    add(name,'年方','direction',lambda e,n=n:[step(e['yb'],n)],3,
        f'年支顺移 {n % 12} 辰',alias=alias)
add('岁德','年方','direction',lambda e:[dict(zip(GAN,'甲庚丙壬戊甲庚丙壬戊'))[e['yg']]],3,
    '甲乙丙丁戊己庚辛壬癸年依次甲庚丙壬戊甲庚丙壬戊')
add('岁德合','年方','direction',lambda e:[GAN_PARTNER[dict(zip(GAN,'甲庚丙壬戊甲庚丙壬戊'))[e['yg']]]],3,'岁德所合之干')
add('岁干合','年方','direction',lambda e:[GAN_PARTNER[e['yg']]],3,'年干五合之干','与岁德或岁德合同位，不重复计权')
add('大将军','年方','direction',lambda e:[trine(e['yb'],[('寅卯辰','子'),('巳午未','卯'),('申酉戌','午'),('亥子丑','酉')])],3,'寅卯辰子、巳午未卯、申酉戌午、亥子丑酉')
for name,tab in [('奏书','艮巽坤乾'),('博士','坤乾艮巽'),('力士','巽坤乾艮'),('蚕室','乾艮巽坤'),('蚕官','戌丑辰未'),('蚕命','亥寅巳申')]:
    add(name,'年方','direction',lambda e,t=tab:[t[((ZHI.index(e['yb'])-2)%12)//3]],3,
        '年支寅卯辰、巳午未、申酉戌、亥子丑依次：'+'/'.join(tab),
        '干维方保留原名，不强行折算为十二支坐方')
for name,t in [('劫煞',[('申子辰','巳'),('寅午戌','亥'),('亥卯未','申'),('巳酉丑','寅')]),
               ('灾煞',[('申子辰','午'),('寅午戌','子'),('亥卯未','酉'),('巳酉丑','卯')]),
               ('岁煞',[('申子辰','未'),('寅午戌','丑'),('亥卯未','戌'),('巳酉丑','辰')]),
               ('黄幡',[('申子辰','辰'),('寅午戌','戌'),('亥卯未','未'),('巳酉丑','丑')]),
               ('伏兵',[('申子辰','丙'),('寅午戌','壬'),('亥卯未','庚'),('巳酉丑','甲')]),
               ('大祸',[('申子辰','丁'),('寅午戌','癸'),('亥卯未','辛'),('巳酉丑','乙')])]:
    add(name,'年方','direction',lambda e,t=t:[trine(e['yb'],t)],3,'按年支三合局取：'+'；'.join(g+'→'+v for g,v in t))
add('豹尾','年方','direction',lambda e:[step(trine(e['yb'],[('申子辰','辰'),('寅午戌','戌'),('亥卯未','未'),('巳酉丑','丑')]),6)],3,'黄幡对冲')
add('岁刑','年方','direction',lambda e:penalty(e['yb']),3,'年支相刑之支；辰午酉亥取本支')
add('岁大煞','年方','direction',lambda e:[ZHI[(-3*ZHI.index(e['yb']))%12]],3,'子年起子，逆行四仲','即岁三合旺支，与月大煞分开')
add('飞廉','年方','direction',lambda e:[dict(zip(ZHI,'申酉戌巳午未寅卯辰亥子丑'))[e['yb']]],3,'子至亥年：申酉戌巳午未寅卯辰亥子丑')
add('金神','年方','direction',lambda e:[list('午未申酉'),list('辰巳'),list('子丑寅卯午未'),list('寅卯戌亥'),list('申酉子丑')][GAN.index(e['yg'])%5],3,'甲己午未申酉、乙庚辰巳、丙辛子丑寅卯午未、丁壬寅卯戌亥、戊癸申酉子丑')
add('破败五鬼','年方','direction',lambda e:[step('辰',-ZHI.index(e['yb']))],3,'子年起辰，逆行十二辰')
add('五鬼','年方','direction',lambda e:[dict(zip(GAN,'巽艮坤震离坎兑乾巽艮'))[e['yg']]],3,'甲壬巽、乙癸艮、丙坤、丁震、戊离、己坎、庚兑、辛乾')
add('岁禄','年方','direction',lambda e:[LU[e['yg']]],8,'年干临官之支')
add('群丑','年方','direction',lambda e:[step(e['yb'],-2)] if e['yb'] in '寅申巳亥' else [],3,
    '四孟年太阴与大将军同居四仲之方','同位的组合条件，不再重复算两项凶')

# Month/day rules. Aliases remain one rule so the same origin cannot be counted twice.
for name,n,alias in [('月建',0,'小时、土府、兵福'),('吉期',1,'兵宝'),('福德',2,'天巫'),
                     ('死神',3,''),('时阴',4,'月官符、死气'),('支德',5,'月小耗'),
                     ('月破',6,'月大耗、建除破'),('天医',8,'天喜、建除成'),
                     ('时阳',-2,'生气'),('血支',-1,'建除闭')]:
    month(name,[step(b,n) for b in MONTHS],volume=4,alias=alias,
          note='同位异名保留事类差异，由模型取舍，不能重复加减分')
month('天罡',[step(b,3 if i%2==0 else -3) for i,b in enumerate(MONTHS)],volume=4)
month('河魁',[step(b,-3 if i%2==0 else 3) for i,b in enumerate(MONTHS)],volume=4)
month('月厌',[step('戌',-i) for i in range(12)],volume=4,alias='地火')
month('厌对',[step('辰',-i) for i in range(12)],volume=4,alias='六仪、招摇',note='原书定厌对忌嫁娶、六仪宜视事临官；不是统一宜忌')
month('月空','壬庚丙甲壬庚丙甲壬庚丙甲','stem',5)
month('月恩','丙丁庚己戊辛壬癸庚乙甲辛','stem',5)
month('天愿','乙亥 甲戌 乙酉 丙申 丁未 戊午 己巳 庚辰 辛卯 壬寅 癸丑 甲子'.split(),'pillar',5,
      '采用原书按语校订表，不用其前引的旧表')
month('九空','辰丑戌未辰丑戌未辰丑戌未',volume=5)
month('五墓','乙未 乙未 戊辰 丙戌 丙戌 戊辰 辛丑 辛丑 戊辰 壬辰 壬辰 戊辰'.split(),'pillar',5)
month('九坎','辰丑戌未卯子酉午寅亥申巳',volume=5,alias='九焦')
month('解神','申申戌戌子子寅寅辰辰午午',volume=5)
month('复日',[list(x) for x in ['甲庚','乙辛','戊己','丙壬','丁癸','戊己','甲庚','乙辛','戊己','丙壬','丁癸','戊己']],'stem',5,
      '按历例两干表标注；原书同时保留地理新书单干说。原书不支持概断重丧')
month('临日','午亥申丑戌卯子巳寅未辰酉',note='原书按语纠正临民受讼之忌，不直接判宜忌')
month('月驿马','申巳寅亥申巳寅亥申巳寅亥',alias='天后',note='这里的天后是月神，区别于六壬十二天将')
month('月劫煞','亥申巳寅亥申巳寅亥申巳寅')
month('月灾煞','子酉午卯子酉午卯子酉午卯',alias='天火、天狱',note='按原书校订为逆行四仲；天狱同源不另计')
month('月煞','丑戌未辰丑戌未辰丑戌未辰',alias='月虚')
month('月刑',[penalty(b) for b in MONTHS])
month('月害','巳辰卯寅丑子亥戌酉申未午')
month('大时','卯子酉午卯子酉午卯子酉午',alias='大败、咸池')
month('游祸','巳寅亥申巳寅亥申巳寅亥申')
month('天吏','酉午卯子酉午卯子酉午卯子',alias='致死')
month('月六合','亥戌酉申未午巳辰卯寅丑子',alias='无翘',note='按月建六合起，不用所选月将替代此表')
month('兵吉',[[step('子',-i+j) for j in range(4)] for i in range(12)])
month('五富','亥寅巳申亥寅巳申亥寅巳申')
month('天仓',[step('寅',-i) for i in range(12)])
month('天贼',[step('丑',-i) for i in range(12)])
for name,table in [('要安','寅申卯酉辰戌巳亥午子未丑'),('玉宇','卯酉辰戌巳亥午子未丑申寅'),
                   ('金堂','辰戌巳亥午子未丑申寅酉卯'),('敬安','未丑申寅酉卯戌辰亥巳子午'),
                   ('普护','申寅酉卯戌辰亥巳子午丑未'),('福生','酉卯戌辰亥巳子午丑未寅申'),
                   ('圣心','亥巳子午丑未寅申卯酉辰戌'),('益后','子午丑未寅申卯酉辰戌巳亥'),
                   ('续世','丑未寅申卯酉辰戌巳亥午子')]:
    month(name,table,note='九神总论限为祭祀祈禳之占，不沿用前引笼统修造上表宜忌')
month('阳德','戌子寅辰午申戌子寅辰午申')
month('阴德','酉未巳卯丑亥酉未巳卯丑亥')
month('天马','午申戌子寅辰午申戌子寅辰')
month('兵禁','寅子戌申午辰寅子戌申午辰')
month('地囊',[x.split('/') for x in ['庚子/庚午','乙未/癸丑','甲子/壬午','己卯/己酉','壬戌/甲辰','丙辰/丙戌',
                                  '丁巳/丁亥','丙寅/丙申','辛丑/辛未','戊寅/戊申','辛卯/辛酉','癸酉/乙卯']],
      'pillar',6,'采用原书按语校订表，不用其前引的旧表')
month('土符','丑巳酉寅午戌卯未亥辰申子')
month('月大煞','戌巳午未寅卯辰亥子丑申酉')
month('归忌','丑寅子丑寅子丑寅子丑寅子',note='原书定止忌般移远回，不因“归”字扩为忌嫁娶')
month('往亡','寅巳申亥卯午酉子辰未戌丑')

# 不将 and the common 厌建 pillar patterns, using actual listed days.
BUJIANG = [
 '辛亥 辛丑 辛卯 庚子 庚寅 己亥 己丑 己卯 丁亥 丁丑 丁卯 丙子 丙寅',
 '庚戌 庚子 庚寅 己亥 己丑 丁亥 丁丑 丙戌 丙子 丙寅 乙亥 乙丑',
 '己酉 己亥 己丑 丁酉 丁亥 丁丑 丙戌 丙子 乙酉 乙亥 乙丑 甲戌 甲子',
 '丁酉 丁亥 丙申 丙戌 丙子 乙酉 乙亥 甲申 甲戌 甲子 戊申 戊戌 戊子',
 '丙申 丙戌 乙未 乙酉 乙亥 甲申 甲戌 戊申 戊戌 癸未 癸酉 癸亥',
 '乙未 乙酉 甲午 甲申 甲戌 戊申 戊戌 癸未 癸酉 壬午 壬申 壬戌',
 '乙巳 乙未 乙酉 甲午 甲申 戊午 戊申 癸巳 癸未 癸酉 壬午 壬申',
 '甲辰 甲午 甲申 戊辰 戊午 戊申 癸巳 癸未 壬辰 壬午 壬申 辛巳 辛未',
 '戊辰 戊午 癸卯 癸巳 癸未 壬辰 壬午 辛卯 辛巳 辛未 庚辰 庚午',
 '癸卯 癸巳 壬寅 壬辰 壬午 辛卯 辛巳 庚寅 庚辰 庚午 己卯 己巳',
 '壬寅 壬辰 辛丑 辛卯 辛巳 庚寅 庚辰 己丑 己卯 己巳 丁丑 丁卯 丁巳',
 '辛丑 辛卯 庚子 庚寅 庚辰 己丑 己卯 丁丑 丁卯 丙子 丙寅 丙辰']
month('阴阳不将',[x.split() for x in BUJIANG],'pillar',4,'依原书按语，六月戊午逐阵已从不将表剔除')
for name,table in [
 ('阴阳大会',{0:'甲戌',1:'乙酉',4:'丙午',5:'丁巳',6:'庚辰',7:'辛卯',10:'壬子',11:'癸亥'}),
 ('阴阳小会',{1:'己卯',2:'戊辰',3:'己巳',4:'戊午',7:'己酉',8:'戊戌',9:'己亥',10:'戊子'}),
 ('行狠',{2:'甲申',3:'乙未',8:'庚寅',9:'辛丑'}),('了戾',{2:'丙申',3:'丁未',8:'壬寅',9:'癸丑'}),
 ('孤辰',{2:['戊申','庚申','壬申'],3:['己未','辛未','癸未'],8:['甲寅','丙寅','戊寅'],9:['乙丑','己丑','丁丑']}),
 ('单阴',{2:'戊辰'}),('纯阴',{9:'己亥'}),('孤阳',{8:'戊戌'}),('纯阳',{3:'己巳'}),
 ('岁薄',{3:['丙午','戊午'],9:['壬子','戊子']}),('逐阵',{5:['戊午','丙午'],11:['壬子','戊子']}),
 ('阴阳交破',{3:'癸亥',9:'丁巳'}),('阴阳击冲',{4:'壬子',10:'丙午'}),
 ('阳破阴冲',{5:'癸丑',11:'丁未'}),('阴道冲阳',{1:'己酉',7:'己卯'}),
 ('阴位',{2:'庚辰',8:'甲戌'}),('三阴',{0:'辛酉',6:'乙卯'})]:
    month(name,[table.get(i) for i in range(12)],'pillar',4,
          '采用原书校订：小会二月己卯、八月己酉；阴道冲阳取相反两日。不加入被删所领日；月宿附加条件不代算')

# Season rules, without propagating a day rule to hours.
seasonal('四相',[list('丙丁'),list('戊己'),list('壬癸'),list('甲乙')],'stem')
seasonal('时德',list('午辰子寅'))
seasonal('王日',list('寅巳申亥'),note='按原书校订，王取四孟，官取四仲')
seasonal('官日',list('卯午酉子'),note='按原书校订，王取四孟，官取四仲')
seasonal('相日',list('巳申亥寅'))
seasonal('民日',list('午酉子卯'))
seasonal('守日',list('辰未戌丑'),note='从原书按语，守/牢旧名互讹已校订')
seasonal('牢日',list('酉子卯午'),note='从原书按语，守/牢旧名互讹已校订')
seasonal('四击',list('戌丑辰未'))
seasonal('天赦',['戊寅','甲午','戊申','甲子'],'pillar')
seasonal('四耗',['壬子','乙卯','戊午','辛酉'],'pillar')
seasonal('四废',[['庚申','辛酉'],['壬子','癸亥'],['甲寅','乙卯'],['丙午','丁巳']],'pillar')
seasonal('四忌',['甲子','丙子','庚子','壬子'],'pillar',alias='与四穷并称八龙、七鸟、九虎、六蛇')
seasonal('四穷',['乙亥','丁亥','辛亥','癸亥'],'pillar')
seasonal('五虚',[list('巳酉丑'),list('申子辰'),list('亥卯未'),list('寅午戌')])
seasonal('八风',[['丁丑','己酉'],['甲申','甲辰'],['辛未','丁未'],['甲戌','甲寅']],'pillar')
add('母仓','四时','branch',lambda e:list('巳午') if e['earth'] else [list('亥子'),list('寅卯'),list('辰戌丑未'),list('申酉')][e['si']],5,
    '春亥子、夏寅卯、秋辰戌丑未、冬申酉；土王期间改巳午','土王取四立前18个公历日；该日段规则不随23:00换日切换')

# Fixed day and hour facts.
add('天恩','日神','pillar',lambda e:[CYCLE[i] for i in list(range(5))+list(range(15,20))+list(range(45,50))],5,'甲子至戊辰、己卯至癸未、己酉至癸丑共15日')
add('八专','日神','pillar',lambda e:['丁未','己未','庚申','甲寅','癸丑'],5,'采用卷五列举的五日，不混用后世八日表')
add('禄落旬空候选','日神','pillar',lambda e:[e['day']] if LU[e['dg']] in voids(e['day']) else [],5,
    '日禄在该日旬空中','又称无禄、十恶大败；原书要求核年月太阳填实，不因候选直接判凶',alias='无禄、十恶大败候选')
add('重日','日神','branch',lambda e:list('巳亥'),5,'巳亥二支；依据原书随后解释区别“己”与“巳”')
add('五合日','日神','branch',lambda e:list('寅卯'),5,'寅卯日；区别于天干五合')
add('五离','日神','branch',lambda e:list('申酉'),5,'申酉日',alias='除神')
add('触水龙','日神','pillar',lambda e:['丙子','癸丑','癸未'],5,'丙子、癸丑、癸未')
add('鸣吠','日神','pillar',lambda e:[p for p in CYCLE if p[1] in '午申酉' and p[0]!='戊'],5,
    '按神煞起例校订：午申酉，除戊干，共13日','原书前引一行表14日与后引校订13日不同，采用后者')
add('鸣吠对','日神','pillar',lambda e:[p for p in CYCLE if (p[1]=='卯' and p[0]!='己') or (p[1]=='寅' and p[0]!='戊') or (p[1]=='子' and p[0] not in '甲戊')],5,
    '按神煞起例校订：四卯、四寅、三子，共11日','不是前引十日表，不冒称统一无争议')
add('九丑候选','日神','pillar',lambda e:['戊子','戊午','壬子','壬午','乙卯','己卯','辛卯','乙酉','己酉','辛酉'],7,
    '乙戊己辛壬临四仲所得合法干支','真九丑还要大吉丑临四仲；候选不等于真格')
add('真九丑','时神','condition',lambda e:['丑临'+e['chou_ground']] if e['day'] in ['戊子','戊午','壬子','壬午','乙卯','己卯','辛卯','乙酉','己酉','辛酉'] and e['chou_ground'] in '子午卯酉' else [],7,
    '九丑候选日，所选月将加时后天盘丑临地盘四仲')
add('截路空亡','时神','hour_stem',lambda e:list('壬癸'),7,'五鼠遁所得时干为壬癸','区别日旬空；戊癸日在子丑及戌亥复现')
add('喜神方','日方','direction',lambda e:[['艮','乾','坤','离','巽'][GAN.index(e['dg'])%5]],7,'甲己艮、乙庚乾、丙辛坤、丁壬离、戊癸巽')
add('喜神时','时神','hour_branch',lambda e:[['寅','戌','申','午','辰'][GAN.index(e['dg'])%5]],7,'甲己寅、乙庚戌、丙辛申、丁壬午、戊癸辰')
for name,delta in [('宝日',1),('义日',4),('制日',2),('伐日',3),('专日',0)]:
    add(name,'日神','pillar',lambda e,n=delta:[e['day']] if ('木火土金水'.index(ELEMENT[e['db']])-'木火土金水'.index(ELEMENT[e['dg']]))%5==n else [],5,
        ['干支同五行','干生日支','干克日支','支克日干','支生日干'][delta],
        '五种干支分类之一；原书论事类用途，不能分类即定通用吉凶')
add('上朔','年日','pillar',lambda e:[GAN[(GAN.index(e['yg'])+(9 if GAN.index(e['yg'])%2==0 else 4))%10]+('亥' if GAN.index(e['yg'])%2==0 else '巳')],6,
    '阳年年干加寅顺至亥、阴年年干加丑顺至巳')


def calendar_rule(name,basis,note='',source=6):
    add(name,'历日','calendar',lambda e,n=name:e['calendar'].get(n,[]),source,basis,note)


calendar_rule('四离','二分二至前一个公历日','按公历00:00–24:00整日；不提前到前夜23:00')
calendar_rule('四绝','四立前一个公历日','按公历00:00–24:00整日；不提前到前夜23:00')
calendar_rule('气往亡','从交节所在公历日含当日数，春7/14/21，夏8/16/24，秋9/18/27，冬10/20/30日')
calendar_rule('月忌日','农历初五、十四、二十三','按所选日柱换日对齐农历日数；民俗标记，不作为通用禁令')
calendar_rule('反支','农历月朔支戌亥初一、申酉初二、午未初三、辰巳初四、寅卯初五、子丑初六','本月朔支决定，不用当天支代替')
calendar_rule('土王用事','四立之前各18个公历日','按公历日界；不扩成整个季月')
CATALOG['历日.土王用事']['source']='https://zh.wikisource.org/wiki/田家占候集覽/卷十#○土王用事'


def evaluate(year,month_pillar,day,hour,sky,calendar_info,earth=False):
    yg,yb=year;dg,db=day;hg,hb=hour
    mi=MONTHS.index(month_pillar[1]);si=mi//3
    env={'yg':yg,'yb':yb,'dg':dg,'db':db,'hg':hg,'hb':hb,'mi':mi,'si':si,'day':day,
         'earth':earth,'calendar':calendar_info,'chou_ground':next(b for b,v in sky.items() if v=='丑')}
    targets={};days=[];hours=[]
    for key,field,fn in RULES:
        vals=fn(env);targets[key]=vals
        if field in {'branch','stem','pillar'} and {'branch':db,'stem':dg,'pillar':day}[field] in vals:days.append(key)
        if field=='calendar' and vals:days.append(key)
        if (field=='hour_stem' and hg in vals) or (field=='hour_branch' and hb in vals) or (field=='condition' and vals):hours.append(key)
    return {'day':days,'hour':hours,'targets':targets,'season':SEASONS[si],
            'lunar_day':calendar_info.get('_lunar_day'),'month_first_branch':calendar_info.get('_first_branch')}
