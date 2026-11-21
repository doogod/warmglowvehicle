/* WARMGLOW — Cornes Motors scraper. Paste into the console on
   https://www.cornesmotors.com/usedcar  and again on  https://www.cornesmotors.com/usedcar/ferrari
   It only uses the site's own UI: clicks 「さらに読み込む」 until the full list is shown, reads the
   list from the page's React state, then opens each car's detail view (clicks the card)
   to collect every photo. Random 3–5 s pauses between clicks.
   Tip: if the browser tab is in the background, Chrome slows timers to once a minute; keep the tab
   visible, or run WG.fastTimers() first.

     await WG.cornesLoadAll()            // load every car on this page
     WG.cornesDump()                     // JSON → data/scrape/cornes_page_main.json / cornes_page_ferrari.json
     await WG.cornesGallery(['a0J…'])    // sfids printed by `python3 build.py todo` (new cars)
                                         //   or WG.cornesGallery() for every RHD car on the page
     WG.dumpGalLines()                   // text → data/scrape/gal_<page>.txt (build.py reads every gal_*.txt)
*/
window.WG = window.WG || {};
(function (WG) {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const jitter = (a, b) => a + Math.random() * (b - a);

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
  WG.cornesItems = () => {
    let best = [];
    for (const el of document.querySelectorAll('a[href*="sfid="], li[class*="search-result-list-item"]')) {
      const fk = Object.keys(el).find(k => k.startsWith('__reactFiber')); let f = el[fk], d = 0;
      while (f && d < 60) {
        let h = f.memoizedState, i = 0;
        while (h && i < 40) { const v = h.memoizedState; if (Array.isArray(v) && v.length > best.length && v[0] && v[0].sfid) best = v; h = h.next; i++; }
        const p = f.memoizedProps; if (p) for (const k in p) { const v = p[k]; if (Array.isArray(v) && v.length > best.length && v[0] && v[0].sfid) best = v; }
        f = f.return; d++;
      }
      break;
    }
    return best;
  };

  WG.cornesLoadAll = async () => {
    for (let i = 0; i < 30; i++) {
      const b = [...document.querySelectorAll('button')].find(b => b.innerText.includes('さらに読み込む'));
      if (!b) break;
      b.click(); await sleep(jitter(3000, 5000));
    }
    return WG.cornesItems().length;
  };

  const KEEP = ['sfid', 'brand', 'vinSuffix', 'modelName', 'currentPrice', 'totalPrice', 'thumbnailPictureUrl', 'store', 'exteriorColor',
    'interiorColor', 'mileageKm', 'totalEmissionVolumeCcm', 'firstRegistrationDate', 'vehicleInspection', 'transmission', 'handlePosition'];
  WG.cornesDump = () => {
    const it = WG.cornesItems();
    return JSON.stringify({
      page: location.pathname,
      sel: it.filter(c => c.handlePosition === '右' && +(c.firstRegistrationDate || '0').slice(0, 4) >= 2022)
             .map(c => Object.fromEntries(KEEP.map(k => [k, c[k]]))),
      allh: it.map(c => [c.brand, c.vinSuffix, c.handlePosition, (c.firstRegistrationDate || '').slice(0, 7)])
    });
  };

  // opens each car's detail view by clicking its card (works on /usedcar and /usedcar/ferrari), then closes it
  WG.cornesGallery = async (sfids) => {
    const it = WG.cornesItems(); const byId = Object.fromEntries(it.map(c => [c.sfid, c]));
    if (!sfids) sfids = it.filter(c => c.handlePosition === '右' && +(c.firstRegistrationDate || '0').slice(0, 4) >= 2022).map(c => c.sfid);
    WG.gal = WG.gal || {}; WG.status = { phase: 'gallery', done: 0, total: sfids.length, err: [] };
    for (const id of sfids) {
      const c = byId[id]; if (!c) { WG.status.err.push([id, 'not on this page']); WG.status.done++; continue; }
      const folder = (c.thumbnailPictureUrl || '').split('/').slice(-2, -1)[0];
      const card = document.querySelector('a[href*="sfid=' + id + '"]') ||
        [...document.querySelectorAll('li[class*="search-result-list-item"]')].find(l => l.querySelector('img[src*="/' + folder + '/"]'));
      if (!card) { WG.status.err.push([id, 'card not found']); WG.status.done++; continue; }
      (card.querySelector('img') || card).click();
      let files = [];
      for (let k = 0; k < 12; k++) {
        await sleep(800);
        files = [...new Set([...document.querySelectorAll('img')].map(i => i.currentSrc || i.src)
          .filter(u => u.includes('/' + folder + '/')).map(u => u.split('/').pop().split('?')[0]))];
        if (files.length > 3) break;
      }
      WG.gal[id] = [folder, files];
      const x = document.querySelector('[class*="detailModal__closeBtn"]'); if (x) x.click();
      WG.status.done++;
      await sleep(jitter(2500, 4500));
    }
    WG.status.finished = true;
    return WG.status;
  };
  // one line per car (→ data/scrape/gal_*.txt):  sfid folder file1,file2,…
  WG.dumpGalLines = () => Object.entries(WG.gal || {}).map(([k, [f, fs]]) => k + ' ' + f + ' ' + fs.join(',')).join('\n');
  WG.dumpGal = () => JSON.stringify(WG.gal || {});
})(window.WG);
