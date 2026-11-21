"""One-off: rebuild data/cars.json from the DATA block already in index.html
(used once, because the raw scrape files of the first versions were never committed)."""
import json, re
from common import *

html = open(INDEX, encoding='utf-8').read()
rows = json.loads(re.search(r'^const DATA = (.*);$', html, re.M).group(1))

def dec(e):
    if not e: return []
    p = e.split('|')
    if p[0] == 'c': return [CN_IMG + p[1] + '/' + f for f in p[2].split(',')]
    folder = p[1]; U = folder.split('/')[-1]; out = []
    if p[2]: out.append(f"https://ccsrpcma.carsensor.net/CSphoto/bkkn/{folder}/{p[2]}")
    if p[3]: out += [f"https://ccsrpcml.carsensor.net/CSphoto/ml/{folder}/{U}_{s}.jpg" for s in p[3].split(',')]
    return out

cars = []
for (id_, src, brand, model, family, reg, rfi, insp, km, ext, int_, cc, tm, incl, total, sen, szh, im, flag, isNew, cur) in rows:
    imgs = dec(im); cornes = src == 'k'
    vin = imgs[0][len(CN_IMG):].split('/')[0][-3:] if cornes and imgs else None
    url = ("https://www.cornesmotors.com/usedcar" + ("/ferrari" if brand == 'FERRARI' else "") + "?sfid=" + id_) if cornes \
        else f"https://www.carsensor.net/usedcar/detail/{id_}/index.html"
    cars.append(dict(id=id_, src='cornes' if cornes else 'carsensor', brand=brand, model=model, family=family, curated=bool(cur),
                     year=int(reg[:4]), reg=reg, regFromInsp=bool(rfi), insp=insp, km=km, ext=ext, int=int_, cc=cc, tm=tm, incl=incl, total=total,
                     store={'en': sen, 'zh': szh}, imgs=imgs, url=url, flag=bool(flag), vin=vin, isNew=bool(isNew)))
save_state(cars)
print('wrote', len(cars), 'cars to', STATE)
