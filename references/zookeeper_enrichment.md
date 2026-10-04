# Zookeeper enrichment (every workflow uses this)

Rule: every track that goes into a plan, playlist note, Notes Sheet, script, CSV or archive gets checked against the KZSU Zookeeper library. Label names come from Zookeeper, not from the web, whenever the album is in the library.

## What to pull per track

- `tag`: the library album ID (CSV column 4). Only if that album really contains the track.
- `label`: the label name exactly as Zookeeper spells it (for example "Matador Records" vs "Matador"). Follow the album's label relationship to `/api/v1/label/<id>`.
- `album`: the album title as the library spells it.
- `artist_lib`: the library's artist form ("New Pornographers, The"). Use the normal form in scripts. Keep `artist_lib` for lookups.
- Any other album attributes the API returns (year, category/genre, format, new/current-add status). Store them under `zk` in the plan.
- `label_source`: one of `zookeeper album`, `zookeeper label table`, `past spin`, `web`, `unverified`.

## Source order

1. Library album record (tag + label).
2. Zookeeper label table, exact name search (`/api/v1/label?filter[name]=...`).
3. Past spins from `/api/v2/playlist/<id>/events` (label as aired).
4. Web, only if the above find nothing. Mark `label_source: web` and show "(verify)" in notes.

Never use a web label when a Zookeeper label exists. If the web and Zookeeper disagree, Zookeeper wins; note the difference.

## How to run it

Use a `https://zookeeper.stanford.edu/` browser tab (the sandbox cannot reach it). Reuse the API key and session from `skills/kzsu-show-build/references/browser_js.md`.

```js
// Run in a zookeeper.stanford.edu tab. Input: [{artist, album, track}]. Output: one result per input.
const h = { headers: { Accept: 'application/vnd.api+json' } };
// "The X" <-> "X, The" so exact-match lookups can succeed
const forms = a => [...new Set([a, a.replace(/^The (.+)$/i, '$1, The'),
  (a.split(' ').length === 2 ? a.split(' ').reverse().join(', ') : a)])];
async function zk(artist, album, track) {
  for (const f of forms(artist)) {
    const r = await fetch('/api/v1/album?filter[artist]=' + encodeURIComponent(f) + '&page[size]=100', h).then(r => r.json());
    for (const a of (r.data || [])) {
      const full = await fetch('/api/v1/album/' + a.id, h).then(r => r.json());
      const tr = (full.data.attributes.tracks || []).map(t => t.track.toLowerCase());
      if (!tr.some(t => t.includes(track.toLowerCase()))) continue;   // track must be on the album
      const lid = full.data.relationships?.label?.data?.id;
      const lab = lid ? (await fetch('/api/v1/label/' + lid, h).then(r => r.json())).data.attributes.name : '';
      return { tag: a.id, album: full.data.attributes.album, label: lab, artist_lib: f, attrs: full.data.attributes };
    }
  }
  return { tag: '', label: '', note: 'not in library' };
}
```

Throttle: one lookup at a time, short pause between. Cache results in `data/zk_cache.json` (key: artist|track) so later weeks reuse them. Refresh a cache entry when its album is still empty after 14 days.

## Fields written to the plan

Each track in `working_playlist.json` gets `tag`, `label`, `label_source`, and `zk` (raw extras). Notes Sheet, script, Zookeeper CSV and archive all read these fields. No track ships with an empty label unless every source failed; then it says `label: ""` and `label_source: unverified`, and the script lists it under "Fill in at the studio."

## Where each skill runs it

- Recon / weekly playlist / specialty: enrich every candidate as it is added to a plan (label and tag). Skip tracks with no album match; they stay `tag: ""`.
- Show build, Notes Sheet, Final script: re-run for any track added or changed since recon (Stace's adds, replacements).
- Archive: compare Zookeeper's aired tracks to the plan; use Zookeeper's label and tag as the record.
- Intake and review templates: use the library record for label, tag and "already in library" checks.
- Health check: report any plan with tracks still missing a label.

## Matching rules (learned Oct. 4)

- The library often holds compilations, live albums and singles that also contain the track (for example a Talking Heads best-of for "Once in a Lifetime"). Prefer the album whose title matches the plan's album (case and punctuation ignored). If the plan has no album, prefer the earliest studio album.
- Apply `tag` and the Zookeeper `label` only on an album match. On a non-match, keep the plan's label, mark it "(verify)", and store the hit under `zk_alt` (tag, album, label) for Stace to choose.
- Zookeeper sometimes returns an HTML page (rate limit or challenge). Wait 1.5 seconds and retry up to 3 times. Never treat HTML as "not in library."
- A blank Zookeeper label stays blank; fall back to the label table or past spins.
- Library labels can differ from the band's usual label (reissues, UK vs US). Use the library spelling anyway.

## Fallback sources for missing metadata (any field)

Order of authority for every field (label, tag, album, release date, duration, credits, genre, upcoming album):

1. YouTube Music: videoId, duration, album as listed, artist.
2. Zookeeper: library tag, library album title, label name, category.
3. Discogs (discogs.com release and master pages): label, catalog number, original release date, country, format, credits, genre/style. Prefer the master release's earliest pressing for original dates, and the US release for the label when Zookeeper has none.
4. Wikipedia (album and song articles): original release date, label, track listing, chart facts, "on this date" history.
5. Media: Stereogum, Pitchfork, Bandcamp, label sites and press releases, for new releases and announcements (release date, label, upcoming album).

Rules:
- Use the browser (Discogs, Wikipedia, media pages) or WebSearch. No scripted web requests from the shell.
- Set `label_source` and a `date_source` to the source used (`discogs`, `wikipedia`, `media`) and keep the URL in `source_url`.
- Two sources must agree for a release date on air. If only one source, add "(verify)".
- Fill every field you can before shipping. Remaining gaps go to "Fill in at the studio" in the script.
- Never overwrite a Zookeeper value with a lower-ranked one. Show a conflict in notes.
