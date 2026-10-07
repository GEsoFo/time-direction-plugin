"""Canonical participant identities: separate named natal branches, no merging."""
from rules import ZHI,pair
from direction_systems import enrich_candidate

def normalize_lives(life='',lives=None):
    if lives is None: lives=[{'name':'本人','branch':life}] if life else []
    if not isinstance(lives,list) or len(lives)>6: raise ValueError('Provide at most six participants')
    result=[];names=set()
    for i,item in enumerate(lives):
        if not isinstance(item,dict): raise ValueError('Participant must be an object')
        if not isinstance(item.get('name',''),str):raise ValueError('Participant name must be text')
        name=item.get('name','').strip() or ('本人' if i==0 else f'参与者{i+1}')
        branch=item.get('branch','')
        if branch not in ['',*ZHI]:raise ValueError('Invalid natal branch')
        if name in names: raise ValueError('Participant names must be distinct')
        names.add(name);result.append({'name':name,'branch':branch})
    return result

def context_lives(context):
    return normalize_lives(context.get('life',''),context.get('lives'))

COMPASS=['正北','东北偏北','东北偏东','正东','东南偏东','东南偏南','正南','西南偏南','西南偏西','正西','西北偏西','西北偏北']

def direction_candidates(f,lives):
    result=[{'branch':b,'name':COMPASS[i], 'azimuth_deg':i*30,
             'sky':f['sky'][b],'general':f['liuren_chart']['wei'][i]['shen']['tianJiang'],
             'void':f['liuren_chart']['wei'][i]['shen']['kongWang'],
             'participants':[{'name':p['name'],'branch':p['branch'],'relations':pair(b,p['branch']) if p['branch'] else ['本命未填写']} for p in lives],
             'year_month_positions':[k for k,v in f['directions'].items() if b in v]}
            for i,b in enumerate(ZHI)]
    return [enrich_candidate(c,f) for c in result] if 'qimen_chart' in f else result
