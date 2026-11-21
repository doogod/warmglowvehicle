import json,re
from maps import *
from shops import SHOP_EN
cs=json.load(open('cs_new.json')); c1=json.load(open('cornes1.json')); fer=json.load(open('cornes_fer.json'))
prev=set(json.load(open('prev_ids.json')))
allh=json.load(open('cornes_main_allh.json'))+[['F',v,h,r] for v,h,_,r in fer['allh']]
CB={'FERRARI':'FERRARI','LAMBO':'LAMBO','ROLLSROYCE':'ROLLSROYCE','BENTLEY':'BENTLEY'}
BMAP={'FE':'FERRARI','LG':'LAMBO','RR':'ROLLSROYCE','PO':'PORSCHE','BE':'BENTLEY','MS':'MASERATI','ML':'MCLAREN'}
LET={'FERRARI':'F','LAMBO':'L','ROLLSROYCE':'R','BENTLEY':'B'}
IMG="https://static-cornes.s3.amazonaws.com/tzy0td2h07pi/public/web/master/"
STORE={"ランボルギーニ芝 ショールーム":("Lamborghini Shiba, Tokyo","兰博基尼 东京芝展厅"),"ロールス・ロイス・モーター・カーズ東京":("Rolls-Royce Motor Cars Tokyo","劳斯莱斯 东京"),
"ロールス・ロイス・モーター・カーズ大阪":("Rolls-Royce Motor Cars Osaka","劳斯莱斯 大阪"),"ベントレー東京 ショールーム":("Bentley Tokyo","宾利 东京展厅"),"ベントレー大阪 ショールーム":("Bentley Osaka","宾利 大阪展厅"),
"ベントレー大阪 神戸ショールーム":("Bentley Osaka – Kobe","宾利 神户展厅"),"コーンズ 大阪中古車ショールーム":("Cornes Ferrari Osaka (Pre-owned)","Cornes 法拉利 大阪二手车展厅"),
"コーンズ 芝ショールーム":("Cornes Ferrari Shiba, Tokyo","Cornes 法拉利 东京芝展厅"),"コーンズ 名古屋ショールーム":("Cornes Ferrari Nagoya","Cornes 法拉利 名古屋展厅")}
def cmodel(c):
    m=c['modelName']; cur='【Curated' in m
    m=re.sub(r'\s*【.*?】','',m).strip(); m=re.sub(r'^Ferrari ','',m); m=m.replace('（V8）',' V8').replace('New ','')
    m=re.sub(r'\bSeries2\b','Series II',m,flags=re.I); m=re.sub(r' 2025$','',m)
    if (m.isupper() and not re.search(r'\d',m)) or m in('PUROSANGUE',): m=m.title().replace('Ii','II').replace('Gtc','GTC').replace('Gt ','GT ')
    m=m.replace('Huracan','Huracán').replace(' A V8',' Azure V8').replace('GTC SPEED','GTC Speed').replace('GT SPEED','GT Speed')
    if c['brand']=='BENTLEY' and m.startswith('Bentayga EWB'): pass
    return m,cur
def fam(brand,m):
    s=m.lower()
    rules=[('296 gtb','296 GTB'),('296','296 GTS'),('cilindri','12Cilindri'),('roma spider','Roma Spider'),('roma','Roma'),('portofino','Portofino M'),('f8','F8 Tributo'),('purosangue','Purosangue'),
      ('urus','Urus'),('hurac','Huracán'),('cullinan','Cullinan'),('spectre','Spectre'),('ghost','Ghost'),('bentayga','Bentayga'),('flying spur','Flying Spur'),('continental gtc','Continental GTC'),('continental gt','Continental GT')]
    for k,v in rules:
        if k in s: return v
    return None
out=[]; cornes_vins={}
for c in c1+fer['sel']:
    b=CB[c['brand']]; m,cur=cmodel(c); reg=c['firstRegistrationDate'][:7].replace('-','/')
    insp=c.get('vehicleInspection') or ''
    imgs=[c['thumbnailPictureUrl']]+[u for u in c['gal'] if u!=c['thumbnailPictureUrl']]
    st=STORE.get(c['store'],(z(c['store']),z(c['store'])))
    tm=c.get('transmission') or ''; tmc=(re.search(r'(\d)AT',tm).group(1)+'AT') if re.search(r'(\d)AT',tm) else ('EV' if 'SPECTRE' in c['modelName'].upper() else 'AT')
    rec=dict(id=c['sfid'],src='cornes',brand=b,model=m,family=fam(b,m),curated=cur,year=int(reg[:4]),reg=reg,regFromInsp=False,insp=insp if re.match(r'\d{4}/\d{2}',insp) else '',
      km=c['mileageKm'],ext=c.get('exteriorColor') or '',int=c.get('interiorColor') or '',cc=c.get('totalEmissionVolumeCcm') or 0,tm=tmc,
      incl=int(c['currentPrice']) if str(c['currentPrice']).isdigit() else 0,total=c.get('totalPrice') or 0,store={'en':st[0],'zh':st[1]},
      imgs=imgs[:14],url="https://www.cornesmotors.com/usedcar"+("/ferrari" if b=='FERRARI' else "")+"?sfid="+c['sfid'],flag=False,vin=c['vinSuffix'])
    out.append(rec); cornes_vins[(LET[b],c['vinSuffix'],rec['year'])]=rec
cornes_lhd={(x[0],x[1],int(x[3][:4]) if x[3] else 0) for x in allh if x[2]=='左'}
isCornesShop=lambda s: bool(re.search(r'コーンズ|ランボルギーニ芝|ロールス・ロイス・モーター・カーズ(東京|大阪)|ベントレー(東京|大阪)',s or ''))
dropped=0; flagged=[]
for x in cs:
    b=BMAP[x['b']]; y=int((x.get('year') or '0')[:4] or 0)
    key=(LET.get(b,'?'),x.get('vin'),y)
    if isCornesShop(x.get('shop')) and key in cornes_vins: dropped+=1; continue
    flag=isCornesShop(x.get('shop')) and key in cornes_lhd
    if flag: flagged.append(x['id'])
    m,f=model_cs(x)
    mi=re.search(r'(\d{4})\(R\d+\)年(\d{1,2})月',x.get('insp') or ''); insp=f"{mi.group(1)}/{int(mi.group(2)):02d}" if mi else ''
    if not y and insp: y=int(insp[:4])-3
    if x.get('regm'): reg=x['regm'].replace('-','/'); rfi=False
    elif insp and int(insp[:4])-y in (2,3): reg=f"{y}/{insp[5:]}"; rfi=True
    else: reg=str(y); rfi=False
    kms=x.get('km') or ''; km=int(round(float(re.search(r'([\d.]+)',kms).group(1))*10000)) if '万' in kms else int(re.sub(r'\D','',kms) or 0)
    folder=x.get('folder') or ''; U=folder.split('/')[-1]
    imgs=([f"https://ccsrpcma.carsensor.net/CSphoto/bkkn/{folder}/{x['main']}"] if x.get('main') else [])+[f"https://ccsrpcml.carsensor.net/CSphoto/ml/{folder}/{U}_{s}.jpg" for s in x.get('ml',[])[:12]]
    imgs=[u for u in imgs if 'UZ0027698225' not in u]
    p=pref(x.get('pref')); sh=SHOP_EN.get(z(x.get('shop')), z(x.get('shop')))
    out.append(dict(id=x['id'],src='carsensor',brand=b,model=m,family=f,curated=False,year=y,reg=reg,regFromInsp=rfi,insp=insp,km=km,ext=col(x.get('color')),int='',
      cc=int(re.sub(r'\D','',x.get('cc') or '') or 0),tm=tm_cs(x.get('tm')),incl=x.get('body') or 0,total=x.get('total') or 0,
      store={'en':f"{sh} · {p}",'zh':f"{sh} · {p}"},imgs=imgs,url=f"https://www.carsensor.net/usedcar/detail/{x['id']}/index.html",flag=flag,vin=x.get('vin')))
for r in out: r['isNew']= r['id'] not in prev
json.dump(out,open('data.json','w'),ensure_ascii=False)
from collections import Counter
print('total',len(out),'dropped dup',dropped,'flagged',len(flagged))
print(Counter(r['brand'] for r in out)); print('new',sum(r['isNew'] for r in out),'removed',len(prev-{r['id'] for r in out}))
print('no family',[r['model'] for r in out if not r['family']][:20])
print(Counter(r['model'] for r in out if r['brand'] in('PORSCHE','MASERATI','BENTLEY','MCLAREN')).most_common(60))
print('noext',sum(1 for r in out if not r['ext']), 'noimg',sum(1 for r in out if len(r['imgs'])<2))
