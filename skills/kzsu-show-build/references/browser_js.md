# Browser JavaScript snippets

Run these with the Chrome `javascript_tool` (javascript_exec). Top-level `await` works. Each call must finish in under about 35 seconds, so split long loops across calls and keep state on `window`.

## Sleep that works in background tabs

Background tabs throttle `setTimeout` to once a second or slower. This version uses MessageChannel instead:

```js
window.sleep = ms => new Promise(r => {
  const c = new MessageChannel(), t = Date.now();
  const f = () => { if (Date.now() - t >= ms) r(); else { c.port1.onmessage = f; c.port2.postMessage(0); } };
  c.port1.onmessage = f; c.port2.postMessage(0);
});
```

## Read a YouTube Music playlist

Scroll until the row count stops growing, then collect the rows:

```js
window.rows = () => [...document.querySelectorAll('ytmusic-playlist-shelf-renderer ytmusic-responsive-list-item-renderer')];
window.rid = r => { const a = r.querySelector('a[href*="watch?v="]'); return a ? new URL(a.href).searchParams.get('v') : null; };
await sleep(2500);
let prev = -1;
for (let i = 0; i < 12; i++) { const n = rows().length; if (n === prev && i > 3) break; prev = n; window.scrollTo(0, 1e7); await sleep(1500); }
window._pl = rows().map(r => {
  const sec = [...r.querySelectorAll('.secondary-flex-columns yt-formatted-string')].map(e => e.textContent.trim());
  return { title: r.querySelector('.title')?.textContent.trim(), artist: sec[0], videoId: rid(r) };
});
_pl.length + ' | ' + document.querySelector('.second-subtitle')?.textContent.trim();
```

Tool output gets cut off at about 1,500 characters. Print `_pl` in slices, for example `_pl.slice(0, 20)` and then `_pl.slice(20)`.

## Remove rows from Working (on the Working page)

```js
const log = [], t0 = Date.now();
for (const id of window.toRemove) {
  if (Date.now() - t0 > 30000) { log.push('timeout'); break; }
  const r = rows().find(x => rid(x) === id); if (!r) { log.push(id + ':gone'); continue; }
  r.scrollIntoView({ block: 'center' }); await sleep(300);
  r.querySelector('button[aria-label="Action menu"]').click(); await sleep(900);
  const it = [...document.querySelectorAll('ytmusic-menu-popup-renderer ytmusic-menu-service-item-renderer')]
    .find(e => e.textContent.trim() === 'Remove from playlist');
  if (!it) { document.body.click(); log.push(id + ':nomenu'); continue; }
  it.click(); await sleep(1500); log.push(id + ':ok');
}
JSON.stringify(log);
```

Run it again until every ID reports `gone`. Then reload the page to confirm, because some removals fail without an error.

## Add tracks to Working (on the Air Order page)

```js
window.pickWorking = () => {
  const o = [...document.querySelectorAll('ytmusic-add-to-playlist-renderer ytmusic-playlist-add-to-option-renderer')]
    .find(e => e.querySelector('#title')?.textContent.trim() === 'DJ Stace library show working');
  return o?.querySelector('button');
};
window.addOne = async id => {
  const r = rows().find(x => rid(x) === id); if (!r) return 'norow';
  r.scrollIntoView({ block: 'center' }); await sleep(300);
  r.querySelector('button[aria-label="Action menu"]').click(); await sleep(1000);
  const s = [...document.querySelectorAll('ytmusic-menu-popup-renderer ytmusic-menu-navigation-item-renderer, ytmusic-menu-popup-renderer ytmusic-menu-service-item-renderer')]
    .find(e => e.textContent.trim() === 'Save to playlist');
  if (!s) { document.body.click(); return 'nomenu'; }
  s.click(); let b = null; for (let i = 0; i < 10 && !b; i++) { await sleep(300); b = pickWorking(); }
  if (!b) return 'nodialog';
  b.click(); await sleep(3500); return 'ok';
};
// Loop over window.toAdd in forward Air Order order. Keep window.addDone so you can resume.
// Before each add, stop if location.href no longer contains PLSosF7JAIkaM.
```

Notes:
- Click the `button` inside the option renderer. Clicking the renderer or the "Recent" carousel tile does nothing.
- The save toast text stays in the DOM after it fades, so it can't confirm an add. Use a fixed wait, then verify by reloading Working.
- Don't touch the toast's "Change" link.

## Check Working against Air Order

```js
const target = [...window.aoIds].reverse();  // aoIds = Air Order videoIds, top to bottom
const ids = rows().map(rid);
JSON.stringify({ n: ids.length, ok: JSON.stringify(ids) === JSON.stringify(target),
  extra: ids.filter(x => !target.includes(x)), missing: target.filter(x => !ids.includes(x)) });
```

## Zookeeper API (from a zookeeper.stanford.edu tab)

```js
const h = { headers: { Accept: 'application/vnd.api+json' } };
const r = await fetch('/api/v1/album?filter[artist]=' + encodeURIComponent('Foxygen') + '&page[size]=50', h).then(r => r.json());
JSON.stringify(r.data.map(a => ({ tag: a.id, album: a.attributes.album, labelId: a.relationships?.label?.data?.id })));
// Then look up the album and its label:
const a = await fetch('/api/v1/album/1026706', h).then(r => r.json());   // a.data.attributes.tracks[] = {seq, track}
const l = await fetch('/api/v1/label/9332', h).then(r => r.json());      // l.data.attributes.name
```

- The album ID is the library tag, which goes in CSV column 4.
- `filter[artist]` is an exact match on the library form of the name ("Misch, Tom"; "New Pornographers, The"). If a lookup returns nothing, try the other form.

## FCC word count (on a Genius lyrics page)

```js
const txt = [...document.querySelectorAll('[data-lyrics-container="true"]')].map(e => e.innerText).join('\n');
const words = { fcc: ['shit', 'piss', 'fuck', 'cunt', 'cocksucker', 'cock', 'tits'], caution: ['bitch', 'asshole', 'goddamn'] };
const res = {}; let sec = '(intro)';
for (const ln of txt.split('\n')) {
  const m = ln.match(/^\[(.+)\]$/); if (m) { sec = m[1]; continue; }
  const low = ln.toLowerCase();
  for (const [k, ws] of Object.entries(words)) for (const w of ws) {
    const re = new RegExp('\\b' + w + '\\w*\\b', 'g'); const n = (low.match(re) || []).length;
    if (n) { res[w] = res[w] || { type: k, n: 0, secs: [] }; res[w].n += n; res[w].secs.push(sec); }
  }
}
JSON.stringify({ title: document.title, chars: txt.length, res });
```

- Return counts and section names only, never the text.
- A prefix match can produce false hits, for example "cockpit" or "pissarro." Check any hit on the word itself before you flag it.
- If `chars` is 0, the page has no lyrics. Try AZLyrics or Bandcamp, or mark the track UNVERIFIED.
