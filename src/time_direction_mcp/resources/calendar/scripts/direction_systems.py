"""Direction evidence from separate systems; not a direction chooser."""
from qimen import BRANCH_PALACE
from rules import ZHI

DOU_NOTES=dict(zip(ZHI,[
 '原文兵行途次迷惑，非通用行动推荐','原文小通、途宿待明','原文临寅有喜；另核罡塞鬼户',
 '原文闭塞宜藏匿','原文关梁闭塞、宜安营','原文天地初开、原论行师',
 '原文天地纵横、宜坐帐','原文天地小通','原文天地迫争','原文天地闭塞、人马惊骇',
 '原文乖隔','原文天阱、惊怕']))

def ritual_facts(f):
    noble=f['noble']['ground'];dou=next(b for b,s in f['sky'].items() if s=='辰')
    return {'liuren_noble':{'branch':noble,'azimuth_deg':ZHI.index(noble)*30,
              'noble_star':f['noble']['branch'],'phase':f['noble']['phase'],'source':'https://zh.wikisource.org/wiki/六壬大全/12',
              'star_in_day_void':f['noble']['branch'] in f['void'],'ground_in_day_void':noble in f['void'],
              'scope':'贵人所临地盘方，不是时支见贵，也不自动定为最佳用方。'},
            'symbolic_dou_handle':{'branch':dou,'azimuth_deg':ZHI.index(dou)*30,'sky_branch':'辰',
              'basis':'月将加时，寻天盘辰天罡所临地盘。','source':'https://zh.wikisource.org/wiki/六壬大全/4',
              'traditional_note':DOU_NOTES[dou],'scope':'式盘斗柄符号方；原论兵机行师，不能直接当成真实七星方位。'}}

def enrich_candidate(candidate,f):
    b=candidate['branch'];systems=f['direction_systems'];q=f['qimen_chart']
    p=next(p for p in q['palaces'] if p['number']==BRANCH_PALACE[b])
    result={**candidate,'qimen':p,'ritual_markers':[],'astronomical_stars':[]}
    for key,label in [('liuren_noble','六壬贵人方'),('symbolic_dou_handle','式盘斗柄方')]:
        if systems[key]['branch']==b:result['ritual_markers'].append({'name':label,**systems[key]})
    for star in systems['real_beidou'].get('stars',[]):
        distance=abs((star['azimuth_deg']-candidate['azimuth_deg']+180)%360-180)
        if distance<=15:result['astronomical_stars'].append({**star,'bearing_difference_deg':round(distance,2)})
    return result
