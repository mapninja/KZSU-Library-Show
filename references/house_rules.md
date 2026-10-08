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
- Reviews live in the KZSU-Album-Reviews repo. KZSU-Album-Reviews pushes go to branch `master` (not main). Add only your own files there; Stace keeps uncommitted work in that repo.
- Commit and push after each run using the token in `.env`. Never print secrets.

## Ticket giveaways
- Ticket sheet: `data/tickets/ticket_giveaways_<yyyy-mm>.csv` (columns: Genre, Artists, Date, Venue, City, DJs to Give Away Tix, give by, # tix, Show time of tix*). Stace pastes updates in chat.
- For each show, default to rows where Stace is listed in the DJs column and the give-by date is on or after the show date. She may pick another row (Oct. 7: Hovvdy, listed for Francis); then flag "confirm with the listed DJ." Add one giveaway to Hour 2 (after the Bay Area shows break, or after a set that fits) and promo teasers on earlier mic breaks (opening break, end of Hour 1, after the Triple Shot). Show it in the landscape script as a giveaway table plus MIC BREAK call-outs.
- Do not invent contest rules, call-in numbers or show times; flag them as "confirm before air."

## Show script format
- All show scripts (Working, Final, specialty) are landscape, table-based Word + PDF files, not prose Docs. Stace's standing preference (Oct. 7, 2026): she scans them on air. Layout and build steps: `references/show_script_landscape.md`.

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

## Drive: working copies and deployed artifacts
- Claude edits only CSV and Markdown working copies in `/KZSU/Working/` (local path `working_dir` in `config/paths.json`, written with the file tools; Drive for desktop syncs).
- Stace sees Google Sheets and Docs, deployed from the working copies by `skills/kzsu-drive-deploy/SKILL.md`: harvest her edits, create the new file, verify, move the old one to `/KZSU/_to_delete/`, update `data/drive_registry.json`. Links change on redeploy.
- The Zookeeper CSV stays a raw CSV.
- Ticks in Sheets: any mark (x, TRUE) counts.

## Promo images
- Images live in Drive `KZSU/Promo and Merch` (index: `config/promo_images.json`).
- Stace sets playlist thumbnails by hand each week (playlist page > Edit thumbnail). Skills do not upload thumbnails. In the weekly summary, remind her which new playlists need one.

## YTM write limits
- After about 30 API playlist writes in one session (Oct. 4), YTM returned 403 PERMISSION_DENIED for all edits. Batch adds in one edit_playlist call per playlist, pause between playlists, and queue failures in `data/daily/pending_ytm_writes.json` for the next run.
- Reads (`/youtubei/v1/browse`, `search`, `next`, `player`) kept working after the block.
- Working write route (tested Oct. 4, 17 adds, no failures): open the album page `music.youtube.com/playlist?list=OLAK5uy_...`, find the row by normalized title, click its "Action menu", click the `tp-yt-paper-item` inside "Save to playlist" (never the anchor), click the target option button, then "Skip duplicates" if shown. For singles with no album page, use the search page: the row whose link has `v=<videoId>`, or the top-result card (`ytmusic-card-shelf-renderer`) header menu. Verify by reading the playlist back.
- To find a track's album and year: `next` endpoint with the videoId; the matching `playlistPanelVideoRenderer.longBylineText` gives "Artist • Album[MPREb_id] • Year".

## Run notes (Oct. 4 simulation)
- Rebuild show files from the plan with `python3 scripts/render_show_files.py <show date> [--ticks harvested.csv]`. It writes the Notes Sheet CSV, the reversed Zookeeper CSV (no header, 6 quoted columns, "(verify)" stripped from labels), working_playlist.md and the set lists in show_script.md (talk-break text above "## Sets" is kept). Copy results to `KZSU/Working/` before deploying.
- Snapshot every playlist you diff in `data/daily/snapshots/<playlistId>.json` after each run (Weekly, Next Show, Air Order, FCC Edit Needed). Diff against the last snapshot to find Stace's adds and deletions; log them in `data/daily/feedback.json`.
- Stace's adds to FCC Edit Needed mean "fits, needs an edit." Keep them out of plans and the Zookeeper CSV until she supplies an edited file.
- Air Order edits: her cuts go to `plan['cut']`; her adds get `added_by: "DJ Stace"` and full metadata. Place an add in the set that fits its angle (anniversary tracks go to the anniversary set).
- Review Shelf deploy: the working copy keeps "Album link" and "Label link" columns; the uploaded CSV drops them and writes Album and Label as `=HYPERLINK()` formulas.
- Git in the sandbox: commit with `git -c user.name="DJ Stace (Claude)" -c user.email="maples@stanford.edu" commit ...`; the token is `github_token` in `.env`. Push with `HEAD:main` (reviews repo: `HEAD:master`) and confirm with `git ls-remote`.
- FCC audio edits: `scripts/fcc_audio_edit.py` exists but is parked (Whisper model download blocked in the sandbox). Do not run it on a schedule.
