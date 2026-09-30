# Browser fallbacks

Use these only when the scripted path fails:

- ytmusicapi can't sign in (no `browser.json`, or it expired).
- The shell can't reach the web (the workspace blocks scripted requests).

Run them with the browser `javascript_exec` tool. Top-level `await` works.

Limits to plan around:

- Each call must finish in under about 35 seconds. Split long loops across calls and keep state on `window`.
- Tool output gets cut off at about 1,000 characters.
- Text that looks like a query string (lots of `&` and `=`) can be blocked. So when exporting data, write `&` as `+` and send it in 950-character chunks.

## Sleep that works in hidden tabs

Hidden tabs slow `setTimeout` down to once a second or less. This version uses MessageChannel instead:

```js
// Wait `ms` milliseconds without relying on setTimeout.
window.sleep = ms => new Promise(res => {
  const end = performance.now() + ms, ch = new MessageChannel();
  ch.port1.onmessage = () => performance.now() >= end ? res() : ch.port2.postMessage(0);
  ch.port2.postMessage(0);
});
```

## A. YouTube Music playlists

### 1. List the playlists

Go to `https://music.youtube.com/library/playlists` and run:

```js
// Every playlist tile: title plus ID (from the link).
[...document.querySelectorAll('a[href*="playlist?list="]')]
  .map(a => [a.textContent.trim(), new URL(a.href).searchParams.get('list')])
  .filter(([t]) => t).map(x => x.join(' | ')).join('\n')
```

Skip these:

- Spoken word: "God is not Great", "New Episodes", "Episodes for Later", and any podcast or audiobook.
- Playlists the assistant builds: "DJ Stace library show Air Order", "DJ Stace library show working" and "Stace's Daily Playlist".

Liked Music always has the ID `LM`.

### 2. Load every row of one playlist

Open `https://music.youtube.com/playlist?list=<ID>` and define the loader. Scrolling doesn't work in a hidden tab, so the loader calls the page's own "load more" hook directly.

```js
window.__load = async (budget) => {
  const q = () => document.querySelectorAll('ytmusic-playlist-shelf-renderer ytmusic-responsive-list-item-renderer');
  const t0 = performance.now(); let last = -1, stable = 0, done = false;
  while (performance.now() - t0 < budget) {
    const n = q().length;
    if (n === last) { if (++stable >= 10) { done = true; break; } } else { stable = 0; last = n; }
    // The continuation element loads the next page when "seen".
    const c = document.querySelector('ytmusic-playlist-shelf-renderer ytmusic-continuation-item-renderer');
    if (!c && stable > 2) { done = true; break; }
    try { c && c.onVisible(); } catch (e) {}
    await sleep(500);
  }
  return q().length + (done ? ' DONE' : ' more');
};
await __load(20000)
```

Call `await __load(20000)` again until it returns `DONE`. That takes about 300 rows per call. The code has to be defined again after every navigation.

### 3. Save the rows in the page

Save each playlist to localStorage so it survives navigation:

```js
(() => {
  const rows = document.querySelectorAll('ytmusic-playlist-shelf-renderer ytmusic-responsive-list-item-renderer');
  const id = new URLSearchParams(location.search).get('list');
  const data = [...rows].map(r => {
    const sec = [...r.querySelectorAll('.secondary-flex-columns yt-formatted-string')].map(x => x.innerText.trim());
    const a = r.querySelector('a[href*="watch?v="]');
    return [r.querySelector('.title')?.innerText.trim(), sec[0] || '', sec[1] || '', (a && a.href.match(/v=([\w-]{11})/) || [])[1] || ''];
  });
  localStorage.setItem('kzsu_pl_' + id, JSON.stringify({ title: document.title.replace(' - YouTube Music', ''), n: data.length, data }));
  return id + ' ' + data.length;
})()
```

### 4. Export the artist counts

The script only needs each playlist's title and the artist column. Build one compact dump, then read it out in chunks:

```js
(() => {
  const keys = Object.keys(localStorage).filter(k => k.startsWith('kzsu_pl_'));
  // Compact form: one line per playlist -> "ID\tTitle\tartist1|artist2|..."
  const lines = keys.map(k => {
    const o = JSON.parse(localStorage[k]);
    return k.slice(8) + '\t' + o.title + '\t' + o.data.map(r => (r[1] || '').replace(/\s+/g, ' ')).join('|');
  });
  window.__blob = lines.join('\n').replace(/&/g, '+');
  window.__ch = [];
  for (let i = 0; i < __blob.length; i += 950) __ch.push(__blob.slice(i, i + 950));
  return __ch.length + ' chunks';
})()
```

Read `window.__ch[0]`, `window.__ch[1]` and so on, batching about 10 per `browser_batch`. Join the chunks exactly as returned and save them to `data/ytm/playlist_dump.tsv`. Then convert the file to the dump format and run the counter:

```bash
# Turn the TSV into the JSON dump ytm_playlist_counts.py expects.
python3 - <<'EOF'
import json
out = {}
for line in open("data/ytm/playlist_dump.tsv", encoding="utf-8"):
    pid, title, artists = line.rstrip("\n").split("\t")
    # "+" was "&" before export; each row needs 4 slots: [title, artist, album, videoId]
    out[pid] = {"title": title, "data": [["", a.replace(" + ", " & "), "", ""] for a in artists.split("|")]}
json.dump(out, open("data/ytm/playlist_dump.json", "w"), ensure_ascii=False)
EOF
python3 scripts/ytm_playlist_counts.py --from-dump data/ytm/playlist_dump.json
```

A 3,000-track playlist comes to about 60,000 characters, or about 65 chunks. If that's too many, export only the playlists that changed since `scraped` in `data/ytm/playlists.json`. The counter keeps the saved weights for every playlist, so check its "No longer found" warning. If the only reason a playlist is missing is that it was left out of this export, merge the old counts back in.

## B. New KZSU shows (Zookeeper)

Open any `https://zookeeper.stanford.edu/` page so `fetch()` runs from the same site. Get the date of the newest saved show from `data/library_show.db` (`SELECT MAX(date) FROM kzsu_shows`). Then pull only the shows after it:

```js
// Newest 20 DJ Stace playlists, with all events. Keep only shows after the saved date.
const since = '2026-09-24';   // <- replace with the newest date in the DB
const r = await fetch('/api/v1/playlist?filter[airname.id]=1428&page[size]=20', { headers: { Accept: 'application/vnd.api+json' } });
const j = await r.json();
window.__new = j.data.filter(p => p.attributes.date > since).map(p => ({
  type: 'show', id: p.id,
  attributes: {
    name: p.attributes.name, date: p.attributes.date, time: p.attributes.time,
    airname: p.attributes.airname, rebroadcast: p.attributes.rebroadcast,
    // Keep only the fields build_music_db.py reads.
    events: (p.attributes.events || []).map(e => ({ type: e.type, artist: e.artist, track: e.track, album: e.album, label: e.label, created: e.created }))
  }
}));
window.__blob = JSON.stringify(__new).replace(/&/g, '\\u0026');   // JSON-safe "&"
window.__ch = []; for (let i = 0; i < __blob.length; i += 950) __ch.push(__blob.slice(i, i + 950));
__new.length + ' shows, ' + __ch.length + ' chunks'
```

Check that the API returns the newest shows first. If it doesn't, add `&sort=-date`. Read the chunks, join them, save them as `data/raw/kzsu/new_shows.json`, then run:

```bash
python3 scripts/merge_kzsu_shows.py data/raw/kzsu/new_shows.json   # adds or replaces shows by id
python3 scripts/build_music_db.py                                   # rebuild the DB from raw files
```

Reviews change rarely. The browser path skips them. Refresh them with `--refresh` when the API is reachable.
