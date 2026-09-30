# Data files

All paths are relative to the `KZSU-Library-Show` project folder.

## data/daily/feedback.json

Taste feedback from DJ Stace's playlist edits. Shared with the kzsu-show-build skill.

```json
{
  "playlist": {"name": "Stace's Weekly Playlist", "id": "PLCLF-Tik2UHk",
               "url": "https://music.youtube.com/playlist?list=PLCLF-Tik2UHk",
               "privacy": "Public", "cadence": "weekly, Thursdays 6 p.m. PT"},
  "removed": [
    {"date": "2026-09-30", "source_playlist": "Stace's Daily Playlist (PLCLF-Tik2UHk)",
     "artist": "Wishy", "title": "Mona Lisa", "videoId": "pm2d3dXkJ4w",
     "bucket": "show", "signal": "new single", "cooloff_until": "2026-11-29"}
  ],
  "added_by_stace": [
    {"date": "2026-09-27", "source_playlist": "Air Order (PLSosF7JAIkaM)",
     "artist": "Foxygen", "title": "San Francisco", "videoId": "mdB1QlEPodk", "position": "Set 4"}
  ],
  "kept": [
    {"date": "2026-10-08", "artist": "...", "title": "...", "videoId": "...", "bucket": "new"}
  ],
  "artist_removals": {"Wishy": 1}
}
```

- `cooloff_until` = date of removal + 60 days.
- Downweight an artist only when `artist_removals` reaches 3.

## data/daily/<YYYY-MM-DD>.json (weekly snapshot)

```json
{
  "date": "2026-10-01",
  "target_show_date": "2026-10-08",
  "playlist": {"name": "Stace's Weekly Playlist", "id": "PLCLF-Tik2UHk"},
  "tracks": [
    {"artist": "Guided By Voices", "title": "Lost In The Sun",
     "album": "Crawlspace Of The Pantheon", "label": "GBV Inc.", "released": "2026",
     "videoId": "dfiR6XtYdzY", "bucket": "new",
     "reason": "Staged No. 1; you aired a single from it.",
     "fcc_status": "CLEAN", "fcc_note": "Genius: none", "date_added": "2026-10-01"}
  ]
}
```

- `bucket`: `new`, `history`, `topical`, `taste` or `added_by_stace`. Older snapshots also use `review`, `show` and `wildcard`.
- `fcc_status`: `CLEAN`, `CAUTION`, `FCC` or `UNVERIFIED`.
- The next run diffs the live playlist against the newest snapshot by videoId.

## data/daily/snapshots/<playlist-id>.json

Read-only snapshots of Air Order (`PLSosF7JAIkaM`) and "DJ Stace - Next Show" (`PLMduzOohHQLrQzt6w4ep6l2zAwcIzoZVF`).

```json
{"playlist": "DJ Stace - Next Show", "id": "PLMduzOohHQLrQzt6w4ep6l2zAwcIzoZVF",
 "snapshot": "2026-09-29", "tracks": [["Sylvan Esso", "Hot Slob", "S3mL5LETIQg"]]}
```

Each track is `[artist, title, videoId]`. Update `snapshot` and `tracks` after each diff.

## data/library_show.db (SQLite)

- `kzsu_spins`: `date`, `artist`, `track`, `album`, `label`, `rebroadcast`, `artist_key`. Filter `rebroadcast = 0`.
- `kzsu_shows`, `kzsu_reviews`, `yt_activity`.

Albums she's airing singles from (past 120 days, 2+ shows):

```sql
-- Count distinct show dates per artist and album; high counts mean "review this album first"
SELECT artist, album, label, COUNT(DISTINCT date) AS shows, MAX(date) AS last_aired
FROM kzsu_spins
WHERE date >= date('now', '-120 days') AND rebroadcast = 0
GROUP BY artist_key, album
HAVING shows >= 2
ORDER BY shows DESC;
```

## outputs/weekly/<target show date>.md

Grouped by bucket. One line per track:

```
- [Artist, "Title"](https://music.youtube.com/watch?v=VIDEOID) from *Album* (Label, release date). Why it's here. **FCC:** word x count.
```
