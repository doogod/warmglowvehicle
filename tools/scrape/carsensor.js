/* WARMGLOW — Carsensor scraper. Paste into the browser console (or javascript_tool) on any
   https://www.carsensor.net page. Everything runs slowly (random 3–7 s between requests) and stops
   by itself on HTTP 403/429 or a captcha page. Results stay in window.WG and localStorage.

   Daily (incremental):
     await WG.csListAll()            // ~25–30 list pages → WG.list  [{id,b,body,total}]
     WG.dumpList()                   // JSON for data/scrape/cs_list.json
     WG.csDetails(['AU…', …])        // only the NEW ids printed by `python3 build.py todo`
     WG.dumpFull()                   // JSON for data/scrape/cs_detail.json
   Full photo/price refresh of existing cars (weekly/monthly, ~1 h for ~650 cars):
     WG.csDetails(WG.list.map(x => x.id)); later WG.dumpCompact(ids) in chunks → data/scrape/cs_detail.json
   Progress: WG.status.  Tab in the background? run WG.fastTimers() first (Chrome slows hidden-tab timers).
*/
window.WG = window.WG || {};
(function (WG) {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const jitter = (a, b) => a + Math.random() * (b - a);
  const man = s => { s = (s || '').replace(/\s/g, ''); const m = s.match(/([\d.]+)万円/); return m ? Math.round(parseFloat(m[1]) * 10000) : 0; };
  // Background tabs only wake timers once a minute; this routes our pauses through a Web Worker
  // (pauses of 0.7–8 s only) so a hidden tab keeps the normal 3–7 s rhythm.
  WG.fastTimers = () => {
    if (window.__wgT) return 'already on';
    const w = new Worker(URL.createObjectURL(new Blob(['onmessage=e=>setTimeout(()=>postMessage(e.data.id),e.data.ms)'])));
    const cb = {}; let n = 0; w.onmessage = e => { const f = cb[e.data]; delete cb[e.data]; f && f(); };
    const orig = window.setTimeout; window.__wgT = { w, orig };
    window.setTimeout = function (f, ms, ...a) {
      if (typeof f !== 'function' || !(ms >= 700 && ms <= 8000)) return orig.apply(window, arguments);
      const id = ++n; cb[id] = () => f(...a); w.postMessage({ id, ms }); return 1e9 + id;
    };
    return 'on';
  };
  WG.DELAY = [3000, 7000];
  // brand code → list paths (Porsche: 911 series only)
  WG.CS_PATHS = { FE: ['bFE'], LG: ['bLG'], RR: ['bRR'], BE: ['bBE'], MS: ['bMS'], ML: ['bML'], PO: ['bPO/s001', 'bPO/s002', 'bPO/s027'] };
  const Q = '?YMIN=2022&ST=R';

  WG.parseList = (doc, b) => [...doc.querySelectorAll('.cassette.js_listTableCassette')].map(c => {
    const a = c.querySelector('a[href*="/usedcar/detail/AU"]'); if (!a) return null;
    const t = c.textContent.replace(/\s+/g, ' ');
    const bm = t.match(/車両本体価格\s*([\d.]+)\s*万円/), tm = t.match(/支払総額\s*([\d.]+)\s*万円/);
    return { id: a.getAttribute('href').match(/AU\d+/)[0], b, body: bm ? Math.round(+bm[1] * 10000) : 0, total: tm ? Math.round(+tm[1] * 10000) : 0 };
  }).filter(Boolean);

  async function getHTML(url) {
    const r = await fetch(url, { credentials: 'include' });
    if (r.status === 403 || r.status === 429) throw new Error('STOP HTTP ' + r.status);
    if (r.status === 404) return null;
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const t = await r.text();
    if (/captcha|recaptcha|ロボットではありません/i.test(t) && !/cassette|車台末尾番号/.test(t)) throw new Error('STOP captcha');
    return t;
  }

  WG.csListAll = async (brands = Object.keys(WG.CS_PATHS)) => {
    WG.list = []; WG.status = { phase: 'list', pages: 0, err: [] };
    const seen = new Set();
    try {
      for (const b of brands) for (const p of WG.CS_PATHS[b]) {
        for (let n = 1; n <= 40; n++) {
          const html = await getHTML(`/usedcar/${p}/index${n === 1 ? '' : n}.html${Q}`);
          WG.status.pages++;
          if (!html) break;
          const rows = WG.parseList(new DOMParser().parseFromString(html, 'text/html'), b);
          const fresh = rows.filter(r => !seen.has(r.id)); fresh.forEach(r => { seen.add(r.id); WG.list.push(r); });
          await sleep(jitter(...WG.DELAY));
          if (rows.length < 30 || !fresh.length) break;
        }
      }
    } catch (e) { WG.status.err.push(String(e)); if (String(e).includes('STOP')) WG.status.stopped = String(e); }
    WG.status.finished = true;
    try { localStorage.setItem('WG_list', JSON.stringify(WG.list)); } catch (e) {}
    return { cars: WG.list.length, pages: WG.status.pages, stopped: WG.status.stopped || null };
  };

  WG.parseDetail = (html, id) => {
    const d = new DOMParser().parseFromString(html, 'text/html');
    const th = {};
    d.querySelectorAll('th').forEach(t => { const n = t.nextElementSibling; const k = t.textContent.replace(/\s+/g, ''); if (n && !(k in th)) th[k] = n.textContent.replace(/\s+/g, ' ').trim(); });
    const bc = [...d.querySelectorAll('a[href^="/usedcar/"]')].map(a => [a.getAttribute('href'), a.textContent.trim()]);
    const bb = bc.find(([h]) => /^\/usedcar\/shashu\/b[A-Z]{2}\//.test(h));
    const b = bb ? bb[0].match(/\/b([A-Z]{2})\//)[1] : null;
    const ser = b && bc.find(([h]) => new RegExp('^/usedcar/b' + b + '/s\\d+/index\\.html$').test(h));
    const h1 = d.querySelector('h1'); const h1t = h1 ? [...h1.childNodes].map(n => n.textContent).join(' ').replace(/\s+/g, ' ').trim() : '';
    const im = th['車検'] && th['車検'].match(/(\d{4})年?\s*[（(](R\d+)[）)]\s*年?\s*(\d{1,2})月/);
    const shopA = d.querySelector('a[href*="/shop/"][href*="BKKN"]') || d.querySelector('a[href*="/shop/"]');
    // photos
    const mls = [...html.matchAll(/ccsrpcml\.carsensor\.net\/CSphoto\/ml\/(\d+\/\d+\/(U\w+?))\/\2_(\d+_\d{3})\.jpg/g)];
    let folder = mls.length ? mls[0][1] : '';
    if (!folder) { const og = (d.querySelector('meta[property="og:image"]') || {}).content || ''; const m = og.match(/bkkn\/(\d+\/\d+\/(U\w+?))\//); if (m) folder = m[1]; }
    const U = folder.split('/').pop();
    const ml = [...new Set(mls.filter(m => m[1] === folder).map(m => m[3]))];
    const mm = U && html.match(new RegExp('bkkn/' + folder + '/(' + U + '_\\d{3}L\\.JPG)'));
    return {
      id, b, model: ser ? ser[1].replace(/の中古車$/, '') : '', h1: h1t,
      year: th['年式'] || th['年式(初度登録年)'] || '', insp: im ? `${im[1]}(${im[2]})年${im[3]}月` : '',
      km: th['走行距離'] || '', color: th['色'] || '', handle: th['ハンドル'] || '', vin: th['車台末尾番号'] || '',
      tm: th['ミッション'] || '', cc: th['排気量'] || '', body: man(th['車両本体価格']), total: man(th['支払総額（税込）'] || th['支払総額']),
      shop: shopA ? shopA.textContent.replace(/\s+/g, ' ').trim() : '', pref: th['地域'] || '',
      folder, main: mm ? mm[1] : '', ml
    };
  };

  WG.csDetails = async (ids) => {
    WG.det = WG.det || JSON.parse(localStorage.getItem('WG_det') || '{}');
    WG.status = { phase: 'detail', done: 0, total: ids.length, err: [] };
    for (const id of ids) {
      if (WG.det[id]) { WG.status.done++; continue; }
      try {
        const html = await getHTML(`/usedcar/detail/${id}/index.html`);
        WG.det[id] = html ? WG.parseDetail(html, id) : { id, gone: true };
      } catch (e) {
        WG.status.err.push([id, String(e)]);
        if (String(e).includes('STOP')) { WG.status.stopped = String(e); break; }
      }
      WG.status.done++;
      try { localStorage.setItem('WG_det', JSON.stringify(WG.det)); } catch (e) {}
      await sleep(jitter(...WG.DELAY));
    }
    WG.status.finished = true;
    return WG.status;
  };

  // run-length encode photo tokens: 1_002…6_002,7_003 → "1-6.2,7.3"
  const runs = ml => { const out = []; let s = null;
    for (const t of ml) { const [a, v] = t.split('_').map(Number);
      if (s && a === s.e + 1 && v === s.v) s.e = a; else { if (s) out.push(s); s = { a, e: a, v }; } }
    if (s) out.push(s); return out.map(s => (s.a === s.e ? s.a : s.a + '-' + s.e) + '.' + s.v).join(','); };

  WG.dumpList = () => JSON.stringify(WG.list);
  // full records (new cars). h1 is cut to 70 chars – the model parser only reads the start.
  WG.dumpFull = (ids = Object.keys(WG.det || {})) => JSON.stringify(Object.fromEntries(ids.filter(i => WG.det[i])
    .map(i => [i, Object.assign({}, WG.det[i], { h1: (WG.det[i].h1 || '').slice(0, 70) })])));
  // one line per car, smallest form (→ data/scrape/cs_detail.txt):  id U main runs vin handle body万 total万
  WG.dumpLines = (ids) => ids.filter(i => WG.det[i]).map(i => WG.det[i]).map(x => x.gone ? x.id.slice(2) + ' gone' :
    [x.id.slice(2), x.folder.split('/').pop() || '-', (x.main.match(/_(\d{3})L/) || [, '-'])[1], runs(x.ml) || '-', x.vin || '-',
     x.handle === '右' ? 'R' : x.handle === '左' ? 'L' : '-', x.body / 1e4, x.total / 1e4].join(' ')).join('\n');
  // compact form for cars already in data/cars.json (photos, VIN, handle, price only)
  WG.dumpCompact = (ids) => JSON.stringify(Object.fromEntries(ids.filter(i => WG.det[i]).map(i => WG.det[i]).map(x =>
    [x.id, x.gone ? { gone: 1 } : { v: x.vin, h: x.handle, f: x.folder, m: x.main, r: runs(x.ml), p: x.body, t: x.total }])));
})(window.WG);
