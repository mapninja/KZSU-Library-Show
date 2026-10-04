# House rules (all KZSU skills read this first)

## Show
- "The Library" with DJ Stace, KZSU 90.1 FM Stanford, Thursdays 6-8 p.m. PT. Airname id 1428.
- Air Order target: 75 minutes of music per show hour (about 2:30 total). Stace culls the rest.
- Working playlist and Zookeeper CSV run REVERSED (last on-air track first). Confirmed by Stace.
- Zookeeper CSV: `library_show_playlist_YYYY-MM-DD.csv`, UTF-8, 6 columns: artist, track, album, tag, label, timestamp. All fields quoted, comma delimited. Blank row = mic break. Tag only if that album really has the track.

## Thursday Triple Shot (weekly segment)
- One artist, three songs, played back to back as a named segment. Plan it every week, specialty weeks included.
- Flexible: the artist can span bands, side projects, solo work or collabs (for example Jack White across The White Stripes, The Raconteurs and solo).
- Best case: at least one track is a new release (this month's single or album). Otherwise anchor to an anniversary or a Bay Area date.
- Pick three tracks that show range. All three FCC-clean or flagged. No repeats of last 8 Triple Shot artists (see `data/triple_shot_history.json`).
- Place it as its own set at the start of Hour 2. Counts toward the 75 minutes per hour.
- Plan JSON field: `"triple_shot": {"artist": "", "angle": "", "tracks": [3 track objects]}` plus a set named "Thursday Triple Shot: <artist>". Script gets a short intro line and a one-line setup per track.

## Zookeeper metadata (all workflows)
- Every track gets its library tag, album title and label name checked against the Zookeeper API. Zookeeper label names win over web labels. Method, cache and field names: `references/zookeeper_enrichment.md`.
- Missing metadata (label, dates, credits, genre): YTM, then Zookeeper, then Discogs, then Wikipedia and media sources. Order and rules in the same file.
- Tag only if the album really contains the track. Missing label = `unverified` and listed in the script.

## Playlists
- music.youtube.com only. Never youtube.com.
- Prefer ytmusicapi for playlist work when the shell can reach YTM. Sandbox currently gets 403, so the signed-in browser is the working route. Verify every edit by reload.
- Deltas only. Never remove and re-add tracks already in place.
- Never edit "DJ Stace - Next Show". Read only.
- Weekly Playlist: add, do not clear. A deleted track = not interested now (60-day cool-off, artist downweight after 3). Tracks Stace adds are kept.

## FCC
- FCC words: fuck, shit, piss, cunt, cocksucker, cock, tits. Caution: bitch, asshole, goddamn.
- Name the exact word, count and section. Never reproduce lyrics.
- Strong FCC tracks go to "FCC Edit Needed" and are flagged in notes and script. Never in the Zookeeper CSV.

## Files
- Only delete files Claude created. Move others to `_to_delete/`.
- Drive layout:
  - `/KZSU/` top level: this week's FINAL show artifacts only (Final Show Script, final Notes Sheet, Zookeeper CSV, working_playlist.md).
  - `/KZSU/Archive/YYYY/MM-DD/`: the previous week's finals. Move them here when the new week's finals are published (Wednesday night build).
  - `/KZSU/Show Prep/`: next week's staged materials (drafts, Working Show Script, Notes Sheet draft, recon, review suggestions, specialty plans). Promote to top level when final.
  - Never write to the Drive root. Never delete; move to `/KZSU/_to_delete/`.
- Reviews live in the KZSU-Album-Reviews repo.
- Commit and push after each run using the token in `.env`. Never print secrets.

## Style
- AP style, no em dashes, no hyperbole. Bullets. Busy, tech-savvy reader.

## Playlist ordering tips (from Stace and first runs)

- On any playlist page, the Edit (pencil) button lets you enable manual sort and drag tracks. Use it to fix individual positions by hand when needed.
- Air Order: adds land at the bottom, so add in forward air order.
- Working: with the default sort, new saves land on top, so adding in forward Air Order sequence yields the reversed list. Verify: first row = last on-air track, last row = first on-air track.
- Fastest way to fill Working: on the Air Order page, use each row's Action menu > Save to playlist > Working, in forward order.
- Removals can fail silently. Reload and re-run until the count matches.

## Archive playlist naming

- Title: `The Library Show on KZSU 90.1 Stanford, CA with DJ Stace (Month d, yyyy Show)`. Always include KZSU. Always add a description (template in `skills/kzsu-archive-playlist/SKILL.md`).
