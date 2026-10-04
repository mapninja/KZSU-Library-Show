# House rules (all KZSU skills read this first)

## Show
- "The Library" with DJ Stace, KZSU 90.1 FM Stanford, Thursdays 6-8 p.m. PT. Airname id 1428.
- Air Order target: 75 minutes of music per show hour (about 2:30 total). Stace culls the rest.
- Working playlist and Zookeeper CSV run REVERSED (last on-air track first). Confirmed by Stace.
- Zookeeper CSV: `library_show_playlist_YYYY-MM-DD.csv`, UTF-8, 6 columns: artist, track, album, tag, label, timestamp. All fields quoted, comma delimited. Blank row = mic break. Tag only if that album really has the track.

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
- Drive: current files at /KZSU/ top level. Prior weeks to /KZSU/Archive/YYYY/MM-DD/.
- Reviews live in the KZSU-Album-Reviews repo.
- Commit and push after each run using the token in `.env`. Never print secrets.

## Style
- AP style, no em dashes, no hyperbole. Bullets. Busy, tech-savvy reader.
