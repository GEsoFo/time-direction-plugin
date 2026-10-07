"""Location-neutral geometric Big Dipper positions, with no runtime downloads.

SIMBAD ICRS J2000 coordinates and proper motions; Skyfield's public ICRF
direction/AltAz transformations provide precession, nutation and Earth rotation.
No annual aberration/parallax or atmospheric refraction is claimed.  Display
precision is 0.1 degree; above-horizon is not a naked-eye visibility guarantee.
"""
import math
from datetime import timezone,timedelta
from functools import lru_cache

def hms(h,m,s):return h+m/60+s/3600
def dms(d,m,s):return d+m/60+s/3600

# name, id, J2000 RA h, Dec deg, mu-alpha*cos(delta), mu-delta (mas/year).
STARS=[
 ('天枢','Dubhe',hms(11,3,43.67152),dms(61,45,3.7249),-134.11,-34.70),
 ('天璇','Merak',hms(11,1,50.4797515135),dms(56,22,56.761138187),79.959,32.365),
 ('天玑','Phecda',hms(11,53,49.8473166),dms(53,41,41.135025),107.68,11.01),
 ('天权','Megrez',hms(12,15,25.5598467041),dms(57,1,57.421119850),103.947,8.141),
 ('玉衡','Alioth',hms(12,54,1.7495922),dms(55,57,35.362645),111.91,-8.24),
 ('开阳','Mizar',hms(13,23,55.54048),dms(54,55,31.2671),119.01,-25.97),
 ('摇光','Alkaid',hms(13,47,32.43776),dms(49,18,47.7602),-121.17,-14.91),
]
SCOPE='几何地平坐标，约0.1°巡天级；含自行、岁差章动，不含周年光行差、视差、折射、地形或天气。'

def validate_observer(observer):
    if observer is None:return None
    if not isinstance(observer,dict):raise ValueError('Observer must be latitude/longitude object')
    if any(isinstance(observer.get(k),bool) or not isinstance(observer.get(k),(int,float)) for k in ['latitude','longitude']):
        raise ValueError('Latitude and longitude must be numeric, not guessed from a city label')
    lat=float(observer['latitude']);lon=float(observer['longitude']);height=float(observer.get('elevation_m',0))
    if not all(math.isfinite(x) for x in [lat,lon,height]) or not -90<=lat<=90 or not -180<=lon<=180 or not -500<=height<=10000:
        raise ValueError('Observer coordinates/elevation are outside supported ranges')
    return {'latitude':lat,'longitude':lon,'elevation_m':height,'label':str(observer.get('label','自定义观测点'))}

@lru_cache(maxsize=1)
def _timescale():
    from skyfield.api import load
    return load.timescale(builtin=True)

def positions_many(datetimes,observer):
    observer=validate_observer(observer)
    if observer is None:return [{'status':'needs_observer','observer':None,'stars':[],
       'reason':'真实七星方位需要每次调用提供经纬度；没有默认城市。','scope':SCOPE} for _ in datetimes]
    import numpy as np
    from skyfield.api import position_of_radec,wgs84
    dates=[(d.replace(tzinfo=timezone(timedelta(hours=8))) if d.tzinfo is None else d).astimezone(timezone.utc) for d in datetimes]
    if not dates:return []
    ts=_timescale();t=ts.from_datetimes(dates)
    site=wgs84.latlon(observer['latitude'],observer['longitude'],elevation_m=observer['elevation_m'])
    years=(t.tt-2451545.0)/365.25;points=[]
    for name,ident,ra,dec,pra,pdec in STARS:
        ra_now=ra+years*pra/(3600000*15*math.cos(math.radians(dec)))
        dec_now=dec+years*pdec/3600000
        position=position_of_radec(ra_now,dec_now,t=t,center=site)
        alt,az,_=position.altaz()
        points.append((name,ident,alt.degrees,az.degrees))
    # Approximate equatorial-of-date solar direction solely for daylight warning.
    n=t.tt-2451545.0;L=np.radians((280.459+.98564736*n)%360);g=np.radians((357.529+.98560028*n)%360)
    lam=L+np.radians(1.915)*np.sin(g)+np.radians(.020)*np.sin(2*g);eps=np.radians(23.439-.00000036*n)
    sun_ra=np.degrees(np.arctan2(np.cos(eps)*np.sin(lam),np.cos(lam)))%360/15
    sun_dec=np.degrees(np.arcsin(np.sin(eps)*np.sin(lam)))
    solar=position_of_radec(sun_ra,sun_dec,epoch=t,t=t,center=site).altaz()[0].degrees
    results=[]
    for i,d in enumerate(dates):
        stars=[{'name':name,'catalog_id':ident,'azimuth_deg':round(float(az[i]),2)%360,'altitude_deg':round(float(alt[i]),2),
                'above_horizon':bool(alt[i]>0),'azimuth_defined':bool(alt[i]<89.99),
                'source':'https://simbad.u-strasbg.fr/simbad/sim-id?Ident='+ident} for name,ident,alt,az in points]
        results.append({'status':'computed','observer':observer,'utc':d.isoformat(),'stars':stars,
          'sun_altitude_deg_approx':round(float(solar[i]),1),'daylight':bool(solar[i]>-6),
          'handle_tip':stars[-1],'scope':SCOPE,'visibility_note':'地平线上并不保证肉眼可见；还须核对昼光、天气、遮挡及光污染。'})
    return results
