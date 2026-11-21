import json, os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
DATA = os.path.join(ROOT, 'data')
SCRAPE = os.path.join(DATA, 'scrape')
STATE = os.path.join(DATA, 'cars.json')      # current processed listing (one car per line)
INDEX = os.path.join(ROOT, 'index.html')
CN_IMG = "https://static-cornes.s3.amazonaws.com/tzy0td2h07pi/public/web/master/"

def load(path, default=None):
    if not os.path.exists(path): return default
    with open(path, encoding='utf-8') as f: return json.load(f)

def save_state(cars):
    os.makedirs(DATA, exist_ok=True)
    with open(STATE, 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(c, ensure_ascii=False, separators=(',', ':')) for c in cars) + '\n]\n')

def save(path, obj):
    with open(path, 'w', encoding='utf-8') as f: json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
