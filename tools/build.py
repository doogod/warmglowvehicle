"""Merge today's scrape into data/cars.json (incremental).

Inputs (all optional, in data/scrape/):
  cs_list.json     [{id,b,body,total}]  – every Carsensor list page (daily, cheap)
  cs_detail.json   {id: full record | compact {v,h,f,m,r,p,t} | {gone:1}}  – detail pages
  cornes_page_*.json  {page, sel:[…], allh:[…]}  – one file per Cornes page (/usedcar, /usedcar/ferrari)
  cornes_gal.json / gal_*.txt   {sfid: [folder, [file, …]]} / 'sfid folder f1,f2,…' lines
  cs_detail*.txt   WG.dumpLines() – compact lines for cars already in the state
Rules:
  • Carsensor car in today's list but not in state → needs a detail page (see `python3 build.py todo`)
  • car in state but not in today's list → sold, removed
  • car in state and in list → kept, price updated from the list; photos/price replaced if a detail record exists
  • Cornes cars are rebuilt from the list every time (the list carries every field); photos kept unless a new gallery exists
  • no photo limit: every photo on the source page is kept

  python3 build.py todo   → prints what the browser still has to fetch
  python3 build.py        → writes data/cars.json and data/data.json
"""
import json, re, sys, os, glob
from collections import Counter
from common import *
from maps import *
from shops import SHOP_EN

BASELINE_FIRST = '2026-11-21'               # cars already listed when tracking started
state = load(STATE, [])
prev = {c['id']: c for c in state}
cs_list = load(os.path.join(SCRAPE, 'cs_list.json'))
cs_det = load(os.path.join(SCRAPE, 'cs_detail.json'), {})
for _txt in sorted(glob.glob(os.path.join(SCRAPE, 'cs_detail*.txt'))):   # WG.dumpLines() output (compact)
    for line in open(_txt, encoding='utf-8'):
        p = line.split()
        if not p: continue
        id_ = 'AU' + p[0]
        if id_ in cs_det and cs_det[id_].get('b'): continue
        if p[1] == 'gone': cs_det[id_] = {'gone': 1}; continue
        U, m, r, v, h, body, total = p[1:8]
        dg = re.sub(r'\D', '', U)
        cs_det[id_] = {'f': f"{dg[-6:-3]}/{dg[-3:]}/{U}" if U != '-' else '', 'm': f"{U}_{m}L.JPG" if m != '-' else '',
                       'r': '' if r == '-' else r, 'v': None if v == '-' else v, 'h': {'R': '右', 'L': '左'}.get(h),
                       'p': round(float(body) * 10000), 't': round(float(total) * 10000)}
cornes_in = [load(p) for p in sorted(glob.glob(os.path.join(SCRAPE, 'cornes_page_*.json')))] or None
cornes_gal = load(os.path.join(SCRAPE, 'cornes_gal.json'), {})
for _g in glob.glob(os.path.join(SCRAPE, 'gal_*.txt')):                 # WG.dumpGalLines() output
    for line in open(_g, encoding='utf-8'):
        p = line.split()
        if len(p) == 3: cornes_gal[p[0]] = [p[1], p[2].split(',')]

CB = {'FERRARI': 'FERRARI', 'LAMBO': 'LAMBO', 'ROLLSROYCE': 'ROLLSROYCE', 'BENTLEY': 'BENTLEY'}
BMAP = {'FE': 'FERRARI', 'LG': 'LAMBO', 'RR': 'ROLLSROYCE', 'PO': 'PORSCHE', 'BE': 'BENTLEY', 'MS': 'MASERATI', 'ML': 'MCLAREN'}
LET = {'FERRARI': 'F', 'LAMBO': 'L', 'ROLLSROYCE': 'R', 'BENTLEY': 'B'}
STORE = {"ランボルギーニ芝 ショールーム": ("Lamborghini Shiba, Tokyo", "兰博基尼 东京芝展厅"), "ロールス・ロイス・モーター・カーズ東京": ("Rolls-Royce Motor Cars Tokyo", "劳斯莱斯 东京"),
         "ロールス・ロイス・モーター・カーズ大阪": ("Rolls-Royce Motor Cars Osaka", "劳斯莱斯 大阪"), "ベントレー東京 ショールーム": ("Bentley Tokyo", "宾利 东京展厅"), "ベントレー大阪 ショールーム": ("Bentley Osaka", "宾利 大阪展厅"),
         "ベントレー大阪 神戸ショールーム": ("Bentley Osaka – Kobe", "宾利 神户展厅"), "コーンズ 大阪中古車ショールーム": ("Cornes Ferrari Osaka (Pre-owned)", "Cornes 法拉利 大阪二手车展厅"),
         "コーンズ 芝ショールーム": ("Cornes Ferrari Shiba, Tokyo", "Cornes 法拉利 东京芝展厅"), "コーンズ 名古屋ショールーム": ("Cornes Ferrari Nagoya", "Cornes 法拉利 名古屋展厅")}

def cmodel(c):
    m = c['modelName']; cur = '【Curated' in m
    m = re.sub(r'\s*【.*?】', '', m).strip(); m = re.sub(r'^Ferrari ', '', m); m = m.replace('（V8）', ' V8').replace('New ', '')
    m = re.sub(r'\bSeries2\b', 'Series II', m, flags=re.I); m = re.sub(r' 2025$', '', m)
    if (m.isupper() and not re.search(r'\d', m)) or m in ('PUROSANGUE',): m = m.title().replace('Ii', 'II').replace('Gtc', 'GTC').replace('Gt ', 'GT ')
    m = m.replace('Huracan', 'Huracán').replace(' A V8', ' Azure V8').replace('GTC SPEED', 'GTC Speed').replace('GT SPEED', 'GT Speed')
    return m, cur

def fam(brand, m):
    s = m.lower()
    rules = [('296 gtb', '296 GTB'), ('296', '296 GTS'), ('cilindri', '12Cilindri'), ('roma spider', 'Roma Spider'), ('roma', 'Roma'), ('portofino', 'Portofino M'), ('f8', 'F8 Tributo'), ('purosangue', 'Purosangue'),
             ('urus', 'Urus'), ('hurac', 'Huracán'), ('cullinan', 'Cullinan'), ('spectre', 'Spectre'), ('ghost', 'Ghost'), ('bentayga', 'Bentayga'), ('flying spur', 'Flying Spur'), ('continental gtc', 'Continental GTC'), ('continental gt', 'Continental GT')]
    for k, v in rules:
        if k in s: return v
    return m

def cornes_rec(c, imgs):
    b = CB[c['brand']]; m, cur = cmodel(c); reg = c['firstRegistrationDate'][:7].replace('-', '/')
    insp = c.get('vehicleInspection') or ''
    st = STORE.get(c['store'], (z(c['store']), z(c['store'])))
    tm = c.get('transmission') or ''; tmc = (re.search(r'(\d)AT', tm).group(1) + 'AT') if re.search(r'(\d)AT', tm) else ('EV' if 'SPECTRE' in c['modelName'].upper() else 'AT')
    return dict(id=c['sfid'], src='cornes', brand=b, model=m, family=fam(b, m), curated=cur, year=int(reg[:4]), reg=reg, regFromInsp=False, insp=insp if re.match(r'\d{4}/\d{2}', insp) else '',
                km=c['mileageKm'], ext=c.get('exteriorColor') or '', int=c.get('interiorColor') or '', cc=c.get('totalEmissionVolumeCcm') or 0, tm=tmc,
                incl=int(c['currentPrice']) if str(c['currentPrice']).isdigit() else 0, total=c.get('totalPrice') or 0, store={'en': st[0], 'zh': st[1]},
                imgs=imgs, url="https://www.cornesmotors.com/usedcar" + ("/ferrari" if b == 'FERRARI' else "") + "?sfid=" + c['sfid'], flag=False, vin=c['vinSuffix'])

def cs_imgs(folder, main, ml):
    # Carsensor slots 20–29 hold the dealer's service/promo pictures (coating, warranty…), not the car
    ml = [s for s in ml if not 20 <= int(s.split('_')[0]) <= 29]
    U = folder.split('/')[-1]
    imgs = ([f"https://ccsrpcma.carsensor.net/CSphoto/bkkn/{folder}/{main}"] if main else []) + [f"https://ccsrpcml.carsensor.net/CSphoto/ml/{folder}/{U}_{s}.jpg" for s in ml]
    return [u for u in imgs if 'UZ0027698225' not in u]

def unruns(r):
    out = []
    for part in filter(None, (r or '').split(',')):
        rng, v = part.split('.'); a, _, e = rng.partition('-'); e = e or a
        out += [f"{n}_{int(v):03d}" for n in range(int(a), int(e) + 1)]
    return out

def cs_rec(x):
    b = BMAP[x['b']]; y = int((x.get('year') or '0').strip()[:4] or 0)
    m, f = model_cs(x)
    mi = re.search(r'(\d{4})\(R\d+\)年(\d{1,2})月', x.get('insp') or ''); insp = f"{mi.group(1)}/{int(mi.group(2)):02d}" if mi else ''
    if not y and insp: y = int(insp[:4]) - 3
    if x.get('regm'): reg = x['regm'].replace('-', '/'); rfi = False
    elif insp and int(insp[:4]) - y in (2, 3): reg = f"{y}/{insp[5:]}"; rfi = True
    else: reg = str(y); rfi = False
    kms = x.get('km') or ''; km = int(round(float(re.search(r'([\d.]+)', kms).group(1)) * 10000)) if '万' in kms else int(re.sub(r'\D', '', kms) or 0)
    p = pref(x.get('pref')); sh = SHOP_EN.get(z(x.get('shop')), shop(x.get('shop')))
    return dict(id=x['id'], src='carsensor', brand=b, model=m, family=f, curated=False, year=y, reg=reg, regFromInsp=rfi, insp=insp, km=km, ext=col(x.get('color')), int='',
                cc=int(re.sub(r'\D', '', x.get('cc') or '') or 0), tm=tm_cs(x.get('tm')), incl=x.get('body') or 0, total=x.get('total') or 0,
                store={'en': f"{sh} · {p}", 'zh': f"{sh} · {p}"}, imgs=cs_imgs(x.get('folder') or '', x.get('main'), x.get('ml') or []),
                url=f"https://www.carsensor.net/usedcar/detail/{x['id']}/index.html", flag=False, vin=x.get('vin'), shopjp=x.get('shop'), handle=x.get('handle'))

CORNES_SHOP_JP = re.compile(r'コーンズ|ランボルギーニ芝|ロールス・ロイス・モーター・カーズ(東京|大阪)|ベントレー(東京|大阪)')
CORNES_SHOP_EN = re.compile(r'Cornes|Lamborghini Shiba|Rolls-Royce Motor Cars (Tokyo|Osaka)|Bentley (Tokyo|Osaka)')
def is_cornes_shop(r):
    return bool(CORNES_SHOP_JP.search(r['shopjp'])) if r.get('shopjp') else bool(CORNES_SHOP_EN.search(r['store']['en']))

# ---------------------------------------------------------------- todo
if len(sys.argv) > 1 and sys.argv[1] == 'todo':
    need_cs = [r['id'] for r in (cs_list or []) if r['id'] not in prev and not (cs_det.get(r['id']) or {}).get('b')]
    need_gal = {}
    for page in cornes_in or []:
        for c in page['sel']:
            if c['sfid'] not in prev and c['sfid'] not in cornes_gal: need_gal.setdefault(page.get('page', '?'), []).append(c['sfid'])
    print(json.dumps({'carsensor_detail': need_cs, 'cornes_gallery': need_gal}, ensure_ascii=False))
    sys.exit()

# ---------------------------------------------------------------- build
out = []
# Cornes
if cornes_in:
    allh = []; sel = []
    for page in cornes_in: sel += page['sel']; allh += page['allh']
    for c in sel:
        if c['brand'] not in CB: continue
        g = cornes_gal.get(c['sfid'])
        if g and g[1]:
            files = g[1]; thumb = c['thumbnailPictureUrl'].split('/')[-1]
            imgs = [CN_IMG + g[0] + '/' + f for f in ([thumb] + [f for f in files if f != thumb])]
        elif c['sfid'] in prev: imgs = prev[c['sfid']]['imgs']
        else: imgs = [c['thumbnailPictureUrl']]
        out.append(cornes_rec(c, imgs))
    cornes_lhd = {(LET.get(br, '?'), v, int(r[:4]) if r else 0) for br, v, h, r in allh if h == '左'}
else:
    out += [c for c in state if c['src'] == 'cornes']
    cornes_lhd = None
cornes_keys = {(LET[r['brand']], r['vin'], r['year']): r for r in out if r['src'] == 'cornes'}

# Carsensor
listed = {r['id']: r for r in cs_list} if cs_list is not None else None
ids = list(listed) if listed is not None else [c['id'] for c in state if c['src'] == 'carsensor']
missing = []; dropped = 0; gone = 0
for id_ in ids:
    d = cs_det.get(id_) or {}
    if d.get('gone'): gone += 1; continue
    if d.get('b'): rec = cs_rec(d)
    elif id_ in prev:
        rec = dict(prev[id_])
        if d.get('f'):
            rec['imgs'] = cs_imgs(d['f'], d.get('m'), unruns(d.get('r')))
            if d.get('v'): rec['vin'] = d['v']
            if d.get('h'): rec['handle'] = d['h']
            if d.get('p') is not None: rec['incl'] = d['p']; rec['total'] = d.get('t') or rec['total']
    else: missing.append(id_); continue
    if listed is not None and id_ in listed:
        l = listed[id_]
        if l.get('body') or l.get('total'): rec['incl'] = l['body']; rec['total'] = l['total']
    if rec.get('handle') and rec['handle'] != '右': continue
    key = (LET.get(rec['brand'], '?'), rec.get('vin'), rec['year'])
    if rec.get('vin') and is_cornes_shop(rec) and key in cornes_keys: dropped += 1; continue
    if cornes_lhd is not None and rec.get('vin'): rec['flag'] = is_cornes_shop(rec) and key in cornes_lhd
    out.append(rec)

for r in out:                                 # 911 groups may change over time – recompute for every car
    if r['brand'] == 'PORSCHE': r['family'] = po_family(r['model'])
# first = date the car was first seen (Malaysia date of the update). NEW = first seen today or yesterday.
TODAY = today().isoformat()
for r in out:
    r['first'] = prev.get(r['id'], {}).get('first') or (TODAY if r['id'] not in prev else BASELINE_FIRST)
    r['isNew'] = days_since(r['first']) <= NEW_DAYS

save_state(out)
save(os.path.join(DATA, 'data.json'), out)
now = {r['id'] for r in out}
print('total', len(out), '| new', sum(r['id'] not in prev for r in out), '| NEW badge', sum(r['isNew'] for r in out), '| removed (sold)', len(set(prev) - now),
      '| dup dropped', dropped, '| 404', gone, '| flagged', sum(r['flag'] for r in out))
if missing: print('WARNING', len(missing), 'Carsensor cars have no detail yet – run `python3 build.py todo`:', missing[:10])
print(Counter(r['brand'] for r in out))
n = [len(r['imgs']) for r in out]; print('photos per car: min', min(n), 'median', sorted(n)[len(n) // 2], 'max', max(n))
print('no family', [r['model'] for r in out if not r['family']][:20])
