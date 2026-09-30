# Browser JavaScript for YouTube Music

Run these with the Claude in Chrome `javascript_exec` tool. Top-level `await` works. Keep each call under about 40 seconds. Work on music.youtube.com only.

## Sleep that works in background tabs

Chrome slows `setTimeout` to about once a second in hidden tabs. A MessageChannel message is not slowed, so this sleep stays accurate.

```js
// Returns a Promise that resolves after `ms` milliseconds.
// Each postMessage schedules the next check right away instead of waiting on a throttled timer.
const sleep = ms => new Promise(resolve => {
  const channel = new MessageChannel();       // two linked message ports
  const start = Date.now();                    // when we started waiting
  const tick = () => {
    if (Date.now() - start >= ms) resolve();   // waited long enough: done
    else { channel.port1.onmessage = tick; channel.port2.postMessage(0); } // check again
  };
  channel.port1.onmessage = tick;
  channel.port2.postMessage(0);                // start the loop
});
```

## Read a playlist

```js
// Scroll to the last row until the row count stops growing, then collect rows.
const rows = () => [...document.querySelectorAll('ytmusic-responsive-list-item-renderer')];
// videoId lives in the row's watch link, e.g. /watch?v=dfiR6XtYdzY
const vid = r => { const a = r.querySelector('a[href*="watch?v="]'); return a ? new URL(a.href).searchParams.get('v') : null; };
await sleep(2500);                              // let the page load
let prev = -1;
for (let i = 0; i < 15; i++) {
  const rs = rows();
  if (rs.length === prev && i > 3) break;       // nothing new loaded: stop
  prev = rs.length;
  rs[rs.length - 1]?.scrollIntoView();          // trigger the next batch
  await sleep(1500);
}
window._pl = rows().map(r => ({
  title: r.querySelector('.title-column .title')?.textContent.trim(),
  artist: [...r.querySelectorAll('.secondary-flex-columns yt-formatted-string')].map(e => e.textContent.trim())[0],
  videoId: vid(r)
}));
// Compare with the header count ("35 tracks"); one unavailable track can make them differ by 1.
_pl.length + ' | ' + document.querySelector('ytmusic-responsive-header-renderer')?.innerText.match(/\d+ tracks?/)?.[0];
```

Tool output gets cut off around 1,000-1,500 characters. Print `_pl` in slices, such as `_pl.slice(0, 20)`.

## Search and save one track (store once, run per page)

Every `navigate` reloads the page and clears `window`. To keep calls short, store the helper as text in music.youtube.com `localStorage`, then run it with `eval()` after each navigation. Remove the key when done.

```js
// STORE (run once on any music.youtube.com page)
localStorage.setItem('kz_tmp', '(' + (async function (A, T) {
  const sleep = ms => new Promise(r => { const c = new MessageChannel(), t = Date.now();
    const f = () => { if (Date.now() - t >= ms) r(); else { c.port1.onmessage = f; c.port2.postMessage(0); } };
    c.port1.onmessage = f; c.port2.postMessage(0); });
  // Lowercase, strip accents and punctuation so "Basht." matches "Basht"
  const norm = s => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');
  // Wait for search results to render
  for (let i = 0; i < 25 && !document.querySelector('ytmusic-card-shelf-renderer, ytmusic-responsive-list-item-renderer'); i++) await sleep(400);
  await sleep(1000);
  // A result matches if it is a "Song" and the title and artist both appear
  const ok = txt => { const p = txt.split('\n').map(x => x.trim()).filter(Boolean);
    return p.includes('Song') && norm(p[0]).includes(norm(T).slice(0, 12)) && norm(txt).includes(norm(A).slice(0, 8)); };
  let el = null;
  const card = document.querySelector('ytmusic-card-shelf-renderer');   // the big "Top result" card
  if (card && ok(card.innerText.split('\n').slice(0, 8).join('\n'))) el = card;
  if (!el) el = [...document.querySelectorAll('ytmusic-responsive-list-item-renderer')].find(r => ok(r.innerText));
  if (!el) return { A, T, status: 'NOT_FOUND' };                        // swap in another pick
  const videoId = new URL((el.querySelector('a[href*="watch?v="]') || { href: 'https://x/?v=' }).href).searchParams.get('v');
  // The top card has its own "Save to playlist" button; list rows need the Action menu first
  let save = el.querySelector('button[aria-label="Save to playlist"]');
  if (!save) {
    el.querySelector('button[aria-label="Action menu"]').click(); await sleep(1200);
    save = [...document.querySelectorAll('ytmusic-menu-navigation-item-renderer, ytmusic-menu-service-item-renderer')].find(m => /Save to playlist/.test(m.innerText));
  }
  save.click();
  // In the dialog, click the BUTTON whose aria-label starts with the playlist name
  let b = null;
  for (let i = 0; i < 20 && !b; i++) { await sleep(300);
    const d = document.querySelector('ytmusic-add-to-playlist-renderer');
    b = d && [...d.querySelectorAll('button')].find(x => (x.getAttribute('aria-label') || '').startsWith("Stace's Weekly Playlist")); }
  if (!b) return { A, T, videoId, status: 'NO_DIALOG' };
  const before = b.getAttribute('aria-label');                           // e.g. "Stace's Weekly Playlist 12 tracks"
  b.click();
  let toast = ''; for (let i = 0; i < 20 && !toast; i++) { await sleep(300);
    toast = [...document.querySelectorAll('tp-yt-paper-toast')].map(t => t.innerText.trim()).join(' '); }
  await sleep(1500);                                                     // spacing between adds
  return { A, T, videoId, before, toast: toast.replace(/\s+/g, ' ').slice(0, 40) };
}).toString() + ')');
'stored';
```

Per track, batch these two actions:

1. `navigate` to `https://music.youtube.com/search?q=<artist+title>`
2. `javascript_exec`: `await eval(localStorage.kz_tmp)('Artist', 'Title')`

When finished: `localStorage.removeItem('kz_tmp')`.

Typing into the YouTube Music search box from JS does not trigger a search, so use `navigate`.

## Remove rows (on the playlist page)

```js
// window.toRemove = ['videoId1', 'videoId2', ...]
const log = [], t0 = Date.now();
for (const id of window.toRemove) {
  if (Date.now() - t0 > 30000) { log.push('timeout'); break; }        // stay under the call limit
  const r = rows().find(x => vid(x) === id);
  if (!r) { log.push(id + ':gone'); continue; }
  r.scrollIntoView({ block: 'center' }); await sleep(300);
  r.querySelector('button[aria-label="Action menu"]').click(); await sleep(900);
  const item = [...document.querySelectorAll('ytmusic-menu-popup-renderer ytmusic-menu-service-item-renderer')]
    .find(e => e.textContent.trim() === 'Remove from playlist');
  if (!item) { document.body.click(); log.push(id + ':nomenu'); continue; }
  item.click(); await sleep(1500); log.push(id + ':ok');
}
JSON.stringify(log);
```

Run again until every ID reports `gone`, then reload to confirm. Some removals fail without an error.

## Rename, privacy and Collaborate (works in a hidden tab)

The Edit playlist dialog doesn't display in a hidden tab, but its form is in the DOM and responds to JS.

```js
document.querySelector('button[aria-label="Edit playlist"]').click(); await sleep(2500);
const d = document.querySelector('ytmusic-dialog');
// Title field is the required input
const title = d.querySelector('input[required]');
title.focus(); title.value = "Stace's Weekly Playlist";
title.dispatchEvent(new Event('input', { bubbles: true }));
title.dispatchEvent(new Event('change', { bubbles: true }));
[...d.querySelectorAll('button')].find(b => b.innerText.trim() === 'Save').click();
await sleep(3000); location.reload();
```

Collaborate: open Edit playlist, click the "Collaborate" tab, then the button with aria-label "Collaborate," then "Done." After a reload, the Collaborate tab shows "Copy invite link" and the owner when it's on.
