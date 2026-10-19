# Outside source scans (weekly)

The staged priority list merges Mark's emails with outside sources. Scan each source in the built-in browser, save what you find, then re-rank. Status per source lives in `data/releases/source_scans/status.json`. Update it every run.

## Status as of Oct. 16, 2026

- **indieisnotagenre:** works in the browser pane. Web fetch is off for this workspace, so do not use it.
- **Bandcamp:** works in the browser pane. The Discover feed is mostly unknown artists, so keep only rows that match `config/taste_profile.json` artists or `config/release_watchlist.json` labels. Artist and label Bandcamp pages are the best date source.
- **Pitchfork:** blocked. The browser pane refuses the domain, web fetch is off and WebSearch cannot reach it. Do not retry. Say "blocked" in the run notes. If Stace pastes Pitchfork picks, add them to the Review Shelf with source "Pitchfork (pasted)".
- **Others on the list** (Stereogum, albumoftheyear, newreleasesnow): Stereogum works. albumoftheyear and brooklynvegan were blocked on Sept. 29. Check `data/releases/coverage.json`.

## indieisnotagenre scan

1. Open `https://www.indieisnotagenre.com/new-indie-albums/` in the browser pane.
2. Run this in the page (javascript_tool). It parses the list into `[date, artist, title, label]` rows. Each month has a header like "OCTOBER 2026" and each release is a date line, artist, title, optional label, then "Buy album*".

```js
// Read the visible article text and split it into trimmed, non-empty lines.
const lines = (document.querySelector('article') || document.body).innerText
  .split('\n').map(s => s.trim()).filter(Boolean);
const mon = {Jan:1,Feb:2,Mar:3,Apr:4,May:5,Jun:6,Jul:7,Aug:8,Sep:9,Oct:10,Nov:11,Dec:12};
let year = 2026, cur = null, out = [];
for (const l of lines) {
  // Month header such as "OCTOBER 2026" sets the year for the rows below it.
  let m = l.match(/^(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER) (\d{4})$/);
  if (m) { year = +m[2]; continue; }
  // A date line such as "16 Oct" starts a new release.
  m = l.match(/^(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$/);
  if (m) { cur = {d: `${year}-${String(mon[m[2]]).padStart(2,'0')}-${m[1].padStart(2,'0')}`, f: []}; continue; }
  // "Buy album*" ends the release. The collected fields are artist, title and optional label.
  if (l.startsWith('Buy album')) { if (cur && cur.f.length >= 2) out.push([cur.d, ...cur.f]); cur = null; continue; }
  if (cur) cur.f.push(l);
}
out.filter(o => o[0] >= '2026-09-01').map(o => o.join('|')).join('\n')  // window: past 6 weeks and upcoming
```

3. Save the output as `data/releases/source_scans/indieisnotagenre_<today>.psv` (lines `date|ARTIST|Title|Label`). Keep only the newest file per source in the folder: move older ones to `_to_delete/`.
4. `scripts/staged_crossref.py` reads every `*.psv` there. Rows add `Scan: indieisnotagenre` to the Sources column, and a matching day confirms a researched date.

## Bandcamp scan

1. Open `https://bandcamp.com/discover/rock+punk?s=new` and the `rock+punk+alternative` variant.
2. Wait 2 seconds, then collect the first 60 item texts with javascript_tool (`li.results-grid__item-container`).
3. Keep rows whose artist matches the taste profile or a watchlist label. Save as `bandcamp_<today>.psv` using the album page's release date (open the page, read "released <date>").
4. If nothing matches, record "ok, no taste-profile matches" in `status.json`.

## Release date lookups

`scripts/staged_crossref.py` writes `data/staged/release_dates_needed.json`: every listed release whose date is single-source ("verify"), plus the best-ranked undated releases (backfill, 25 per run).

For each item:
1. Look for a day-precision date on the artist or label Bandcamp page (browser pane, `get_page_text`), then Wikipedia, Discogs, MusicBrainz, then press.
2. Record it in `data/staged/release_dates.json`, keyed by the item's `key`: `{date, precision, sources[], status, note, label, confirmed, checked_on}`.
3. `confirmed: true` only with two agreeing sources at day precision and no doubt in the note. Reissues: record the reissue date and put the original year in the note. Singles: the single's date, with the album date in the note.
4. Never guess. WebSearch snippets are acceptable as sources, but prefer page text from the browser.
5. Re-run `python3 scripts/staged_crossref.py --top 40 --outside 25 --sync-shelf`. `--sync-shelf` writes checked dates into `data/staged/review_shelf.csv`.
