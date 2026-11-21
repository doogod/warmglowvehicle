import json,re
d=json.load(open('data.json')); picks=json.load(open('picks2.json'))
CN="https://static-cornes.s3.amazonaws.com/tzy0td2h07pi/public/web/master/"
def enc(imgs):
    if not imgs: return ''
    if imgs[0].startswith(CN):
        folder=imgs[0][len(CN):].split('/')[0]
        return 'c|'+folder+'|'+','.join(u.split('/')[-1] for u in imgs if u.startswith(CN+folder+'/'))
    main=''; ml=[]; folder=''
    for u in imgs:
        m=re.match(r'https://ccsrpcma\.carsensor\.net/CSphoto/bkkn/(.+)/([^/]+)$',u)
        if m: folder=m.group(1); main=m.group(2); continue
        m=re.match(r'https://ccsrpcml\.carsensor\.net/CSphoto/ml/(.+)/U\w+?_(\d+_\d{3})\.jpg$',u)
        if m: folder=m.group(1); ml.append(m.group(2))
    return 's|'+folder+'|'+main+'|'+','.join(ml)
rows=[]
for r in d:
    rows.append([r['id'],'k' if r['src']=='cornes' else 's',r['brand'],r['model'],r['family'],r['reg'],1 if r['regFromInsp'] else 0,r['insp'],r['km'],r['ext'],r['int'],r['cc'],r['tm'],r['incl'],r['total'],r['store']['en'],r['store']['zh'],enc(r['imgs']),1 if r['flag'] else 0,1 if r['isNew'] else 0,1 if r['curated'] else 0])
js='const PICKS = '+json.dumps(picks,separators=(',',':'))+';\nconst DATA = '+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n'
open('data_block.js','w').write(js); print(len(js))
