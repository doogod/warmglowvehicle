import json,math,os,datetime,numpy as np
from common import DATA, NEW_DAYS, BOOST_DAYS, days_since
from collections import defaultdict,Counter
d=json.load(open(os.path.join(DATA,'data.json')))
_t=datetime.date.today(); NOWM=_t.year*12+_t.month
def age(r):
    p=r['reg'].split('/'); y=int(p[0]); m=int(p[1]) if len(p)>1 else 12
    return NOWM-(y*12+m)
fams=defaultdict(list)
for r in d: fams[(r['brand'],r['family'])].append(r)
picks={}
for (b,f),arr in fams.items():
    P=[r for r in arr if r['incl'] and not r['flag']]
    variants=sorted({r['model'] for r in P})
    pred=None
    if len(P)>=4:
        vi={v:i for i,v in enumerate(variants)}
        def X(r):
            x=[1,r['year']-2024,math.log(r['km']+300)]+[0]*len(variants); x[3+vi[r['model']]]=1; return x
        A=np.array([X(r) for r in P],float); y=np.log([r['incl']/1.1 for r in P])
        lam=np.eye(A.shape[1])*0.3; lam[0,0]=0
        w=np.linalg.solve(A.T@A+lam,A.T@y)
        pred=lambda r:math.exp(np.dot(X(r),w)) if r['model'] in vi else None
    elif P:
        med=sorted(r['incl']/1.1 for r in P)[len(P)//2]; pred=lambda r:med
    for r in arr:
        e=pred(r) if (pred and r['incl'] and not r['flag']) else None
        r['_res']=(r['incl']/1.1/e-1) if e else None
        r['_np']=len(P)
    cand=[r for r in arr if not r['flag'] and age(r)>=6 and (r['_res'] is not None or len(arr)==1)]
    if not cand: continue
    q=max(1,min(3,round(math.sqrt(len(arr))*0.32)))
    sc=lambda r:(-50 if r['_res'] is None else -r['_res']*100)+(2 if r['km']<=1000 else 0)+(1.5 if r['src']=='cornes' else 0)+(1 if age(r)>=12 else 0)-(4 if r['km']>40000 else 2 if r['km']>25000 else 0)
    for i,r in enumerate(sorted(cand,key=sc,reverse=True)[:q]):
        t=[]
        if i==0: t.append('top')
        if r['_res'] is not None and r['_np']>=3:
            if r['_res']<=-0.05: t.append('value')
            elif r['_res']<=0.02: t.append('fair')
        if r['km']<=1000: t.append('lowkm')
        if r['km']<=300: t.append('new')
        if r['src']=='cornes': t.append('cornes')
        if len(arr)<=2: t.append('rare')
        picks[r['id']]={'r':None if (r['_res'] is None or r['_np']<3) else round(r['_res'],3),'n':r['_np'],'t':t}
json.dump(picks,open(os.path.join(DATA,'picks.json'),'w'))

# ---- Recommended order (default sort on the site). Rough, relative only:
#  brand weight (Ferrari/Lamborghini first) + price level (dearer first) + value vs. market (cheaper than expected first)
#  + freshness: cars first seen today/yesterday (NEW) come first, then a boost fading over 7 days
BRAND_W={'FERRARI':3.0,'LAMBO':3.0,'ROLLSROYCE':1.6,'MCLAREN':1.2,'BENTLEY':1.0,'PORSCHE':0.6,'MASERATI':0.0}
fam_med={}
for (b,f),arr in fams.items():
    ps=sorted(r['incl'] for r in arr if r['incl']); fam_med[(b,f)]=ps[len(ps)//2] if ps else 0
rec={}
for r in d:
    price=r['incl'] or fam_med.get((r['brand'],r['family'])) or 2e7          # price on request -> model median
    res=r.get('_res'); val=0 if res is None else max(-0.25,min(0.25,-res))  # +0.25 = 25 % under market
    sc=BRAND_W.get(r['brand'],0)+1.5*math.log10(price/1e7)+6*val
    if r['id'] in picks: sc+=0.4
    if r['flag']: sc-=1
    if age(r)<12: sc-=0.2                                                     # still has to wait in Japan
    ds=days_since(r.get('first'))                                            # freshness:
    if ds<=NEW_DAYS: sc+=10                                                   #  new today/yesterday -> top block
    elif ds<BOOST_DAYS: sc+=1.5*(BOOST_DAYS-ds)/(BOOST_DAYS-NEW_DAYS)         #  then fades out over a week
    rec[r['id']]=round(sc,2)
json.dump(rec,open(os.path.join(DATA,'rec.json'),'w'))
print(len(picks)); print(Counter(t for p in picks.values() for t in p['t']))
print(Counter((r['brand']) for r in d if r['id'] in picks))
for r in d:
    if r['id'] in picks: print(r['brand'][:4],r['model'][:28].ljust(28),r['year'],str(r['km']).rjust(6),str(round(r['incl']/1.1e4)).rjust(5),picks[r['id']])
