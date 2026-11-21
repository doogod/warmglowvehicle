"""Write data/data.json + data/picks.json into index.html (PICKS / DATA lines) and set the
"last updated" date in the footer and README. Usage: python3 emit.py [YYYY-MM-DD]"""
import json, re, os, sys, datetime
from common import *

d = load(os.path.join(DATA, 'data.json')); picks = load(os.path.join(DATA, 'picks.json')); rec = load(os.path.join(DATA, 'rec.json'), {})
day = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()

def enc(imgs):
    if not imgs: return ''
    if imgs[0].startswith(CN_IMG):
        folder = imgs[0][len(CN_IMG):].split('/')[0]
        return 'c|' + folder + '|' + ','.join(u.split('/')[-1] for u in imgs if u.startswith(CN_IMG + folder + '/'))
    main = ''; ml = []; folder = ''
    for u in imgs:
        m = re.match(r'https://ccsrpcma\.carsensor\.net/CSphoto/bkkn/(.+)/([^/]+)$', u)
        if m: folder = m.group(1); main = m.group(2); continue
        m = re.match(r'https://ccsrpcml\.carsensor\.net/CSphoto/ml/(.+)/U\w+?_(\d+_\d{3})\.jpg$', u)
        if m: folder = m.group(1); ml.append(m.group(2))
    return 's|' + folder + '|' + main + '|' + ','.join(ml)

rows = [[r['id'], 'k' if r['src'] == 'cornes' else 's', r['brand'], r['model'], r['family'], r['reg'], 1 if r['regFromInsp'] else 0, r['insp'], r['km'], r['ext'], r['int'],
         r['cc'], r['tm'], r['incl'], r['total'], r['store']['en'], r['store']['zh'], enc(r['imgs']), 1 if r['flag'] else 0, 1 if r['isNew'] else 0, 1 if r['curated'] else 0, rec.get(r['id'], 0)] for r in d]

html = open(INDEX, encoding='utf-8').read()
html = re.sub(r'^const PICKS = .*;$', lambda m: 'const PICKS = ' + json.dumps(picks, separators=(',', ':')) + ';', html, count=1, flags=re.M)
html = re.sub(r'^const DATA = .*;$', lambda m: 'const DATA = ' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';', html, count=1, flags=re.M)
html = re.sub(r'last updated \d{1,2} [A-Z][a-z]{2} \d{4}', f"last updated {day.day} {day.strftime('%b')} {day.year}", html)
html = re.sub(r'最近更新于 \d{4}年\d{1,2}月\d{1,2}日', f"最近更新于 {day.year}年{day.month}月{day.day}日", html)
open(INDEX, 'w', encoding='utf-8').write(html)

readme = os.path.join(ROOT, 'README.md')
t = open(readme, encoding='utf-8').read()
open(readme, 'w', encoding='utf-8').write(re.sub(r'最近一次数据更新：\d{4}-\d{2}-\d{2}', f'最近一次数据更新：{day.isoformat()}', t))
print('index.html updated:', len(rows), 'cars,', len(picks), 'picks,', round(len(html) / 1024), 'KB, date', day)
