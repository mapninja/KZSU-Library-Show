# Data formats

## working_playlist.json

```json
{
  "show_date": "2026-10-01",
  "name": "DJ Stace library show working",
  "note": "free text; append a line for each sync",
  "ytm_playlist":  { "name": "...working", "id": "PLLXFGCRcu_qc", "url": "...", "order": "reversed ...", "tracks": 39, "built": "YYYY-MM-DD" },
  "ytm_air_order": { "name": "...Air Order", "id": "PLSosF7JAIkaM", "url": "...", "order": "forward ...", "tracks": 39, "built": "..." },
  "sets": [
    { "set": "Hour 1, Set 1: Loud and new", "tracks": [ { "...track fields..." } ] }
  ]
}
```

### Track fields

| Field | Meaning |
|---|---|
| artist, track, album | Display names. The album may end in " (advance single)"; the build script strips that for the CSV. |
| label | Zookeeper label name, such as "Matador Records," "Domino Recording Company," "Xl Recordings," "Pias Recordings," "Mom + Pop," "Bmg" or "Awal." The CSV leaves "unverified" blank, so fix it. |
| label_source | For example, "ZK library album 1026706 (track 4)," "ZK label table," "past spins" or "web: <site>." |
| tag | KZSU library album ID. Leave it blank if the library album doesn't contain the track. |
| released, type, upcoming, duration | Metadata. `type` is single, album track and so on. |
| priority | `R` required, `O` optional, `X` opportunistic, `SKIP` for FCC problems, `CUT` for tracks Stace removed. SKIP and CUT stay out of every output. |
| why | One-line reason for the pick. Append edit notes, such as "Removed from Air Order by DJ Stace (cool-off to Nov. 26)." |
| fcc_status, fcc_note | `CLEAN`, `FCC`, `CAUTION` or `UNVERIFIED`. The note names the word, count and section, for example "fuck x1 (outro)." |
| explicit_tag | Apple Music or streaming explicit flag, if known. |
| source | recon, running playlist, staged, or added_by_stace. |
| added_by | "DJ Stace" for her own adds. |
| videoId | YouTube Music video ID. Take it from Air Order. |
| ytm_missing | True if the track isn't on YouTube Music (Bandcamp only). It stays in the CSV and out of the YTM playlists. |

## feedback.json (data/daily/)

```json
{
  "removed": [ { "date": "2026-09-27", "source_playlist": "Air Order (PLSosF7JAIkaM)", "artist": "...", "title": "...", "videoId": "...", "cooloff_until": "2026-11-26" } ],
  "added_by_stace": [ { "date": "...", "source_playlist": "...", "artist": "...", "title": "...", "album": "...", "videoId": "...", "position": "Set 4 (Bay Area), after Fruit Bats", "set": "...", "label": "...", "tag": "..." } ],
  "kept": [],
  "artist_removals": { "Artist": 1 }
}
```

Before you append, look for the same videoId. Earlier daily or Thursday runs may have logged it already.

## Zookeeper CSV

Positional, with no header row and every field quoted:

```
"artist","track","album","tag","label",""
```

The last column is the timestamp. Leave it blank; Zookeeper stamps it when she marks the track played.
