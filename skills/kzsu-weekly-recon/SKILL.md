---
name: kzsu-weekly-recon
description: >-
  Thursday-night draft plan for NEXT Thursday's "The Library" on KZSU 90.1 FM (6-8 p.m. PT). Builds data/recon/(show date)/working_playlist.json from Stace's Weekly Playlist, taste profile, staged albums, her playlist edits, new releases, Today in Music and topical picks, sized to 75 minutes of music per show hour (about 2:30 total). Then builds the draft Air Order playlist, the Notes Sheet rows and the Working Show Script via kzsu-notes-sheet-and-script. FCC-screens every candidate. Use on the Thursday 9:30 p.m. run after the show, or whenever Stace asks to run recon, draft next week's show, pick candidates or build the plan. Not for the final script (kzsu-final-script), Working playlist and Zookeeper CSV (kzsu-show-build), or the rolling review list (kzsu-weekly-playlist).
---

# KZSU weekly recon and plan

You turn her taste, her staged albums and the week's music news into a plan for the next show. The output is `data/recon/<target show date>/working_playlist.json` in the repo `/Users/maples/Github/KZSU-Library-Show`. The kzsu-show-build skill reads it on show day. If this plan is missing on Thursday morning, the show build stops.

## Specialty weeks

If `data/recon/<target>/working_playlist.json` already exists with a `"theme"` field (built by `kzsu-specialty-show`), this is a specialty show. Keep the theme, update the plan in place, and fold in Today in Music, new releases and Bay Area items that fit the theme. Everything else in this skill (Air Order, Notes Sheet, scripts, CSV) applies unchanged.

## Dates
- Target show date = the next Thursday strictly after today. Run Thursday at 9:30 p.m. (after the show and the archive playlist) and it is today + 7. If today is Thursday before 6 p.m. and no plan exists for today, build for today and say so in the summary.
- Check `data/recon/` first. If a plan for the target date exists, update it instead of overwriting. Keep her edits (`added_by`, `CUT`).

## Order of skills
1. Research first (steps 1-4). Do not read output-format skills until the content is ready.
2. Read `skills/kzsu-show-build/references/data_format.md` in the repo before writing the JSON.
3. Invoke `anthropic-skills:google-workspace` before any Drive write.

## Setup
- If the repo is not connected, request it with `mcp__cowork__request_cowork_directory`.
- Browser: built-in browser (`mcp__Claude_Browser__*`) signed in to YouTube Music, or Claude in Chrome. Read `references/house_rules.md` and `config/playlists.json` first.
- music.youtube.com only. Never www.youtube.com or m.youtube.com.
- No curl, Python or other scripted web requests. Use WebSearch and the browser.
- Read-only on every YouTube Music playlist. Do not email.

## Workflow

### 1. Load inputs
- `TASTE_PROFILE.md` and `config/taste_profile.json`: core artists, labels, lanes.
- `data/daily/feedback.json`: removed (60-day cool-off), added_by_stace, kept, artist_removals.
- Newest `outputs/reviews/staged_priority_*.md`, newest `outputs/weekly/<target>.md` if present, and the last two `data/recon/*/working_playlist.json` (avoid repeats, copy the set structure).
- Recent spins from `data/library_show.db` if present (read locally). Skip anything aired in the past 21 days unless it is a new single she is rotating.
- Her playlists on music.youtube.com, for videoIds and taste signals: "Stace's Weekly Playlist" (`PLCLF-Tik2UHk`), "DJ Stace - Next Show" (`PLMduzOohHQLrQzt6w4ep6l2zAwcIzoZVF`), Air Order (`PLSosF7JAIkaM`). Read only.

### 2. Find candidates
Cover releases from 2 weeks before today through the target show date.
- New releases (about 40 percent): singles and albums, staged albums first, then fresh finds. Sources: Stereogum, Pitchfork, Brooklyn Vegan, Bandcamp Daily, and label sites (Matador, Sub Pop, Merge, Drag City, Partisan, 4AD, In the Red, Domino, Rough Trade). Weight albums whose singles she already airs.
- History (about 20 percent): anniversaries in the target week (10, 20, 25, 30, 40, 50 years), artist birthdays and deaths, landmark concerts, Bay Area music history. Favor artists in her profile.
- Taste and topical (about 40 percent): holidays and events in the target week, Bay Area and Stanford events, overdue favorites, RIYL neighbors of core artists and of tracks she added, label-mates.
- Skip anything in cool-off. Do not down-weight an artist until 3 or more removals.
- Every candidate needs release date, label, genre, one-line reason and a verified link. Never guess a date.

### 3. Rank and group
- Priority: R required, O optional, X opportunistic. Staged albums and singles she already airs rank higher.
- Plan 75 minutes of music per show hour, about 2:30 total, so she culls about 30 minutes. Hour 1 Sets 1-3, Hour 2 Sets 4-7, then "Closers and bench." Source first from Stace's Weekly Playlist, then fill gaps. Name sets by theme. Group Bay Area acts together.
- **Thursday Triple Shot (every week):** pick one artist and three tracks per `references/house_rules.md`. Prefer a core artist with a new release in the window. The artist may span bands or collabs. Skip artists in `data/triple_shot_history.json` (last 8). Make it the first set of Hour 2, named "Thursday Triple Shot: <artist>", and add `triple_shot` to the plan. Append the pick to the history file. FCC-screen all three.
- Write `data/recon/<target>/candidates.json` first (forward air order, same format), then the plan.

### 4. FCC screen
Invoke `anthropic-skills:kzsu-fcc-lyrics-check` on every candidate. Record word, count and section. Never reproduce lyrics.
- FCC words: shit, piss, fuck (all forms), cunt, cocksucker, cock, tits. Caution: bitch, asshole, goddamn.
- A track with an FCC word gets priority SKIP. No lyrics posted gets UNVERIFIED.

### 5. Write the plan
- `data/recon/<target>/working_playlist.json` in the data_format.md format: sets, priority, label, label_source, released, type, upcoming, why, fcc_status, fcc_note, source, videoId.
- Take videoIds from her playlists where the track appears. Otherwise search music.youtube.com, confirm artist and title, and use that ID. If it is not on YouTube Music, set `ytm_missing: true`.
- Labels and tags: look up in the KZSU Zookeeper API from a `https://zookeeper.stanford.edu/` tab (see `skills/kzsu-show-build/references/browser_js.md`). Leave `tag` blank if the library lacks the album.
- Write the draft Air Order (forward) from the plan by deltas. Stace may edit it any time; her edits win on later runs. Do not touch Working here (kzsu-show-build does) and never edit "DJ Stace - Next Show".

### 6. Review suggestions
- Write `outputs/reviews/review_suggestions_<today>.md` in the repo: picks by set, with release date, label, genre, abstract, link, FCC status. AP style, no em dashes, no adjectives or hyperbole.
- Upload it as raw Markdown (no conversion) to Drive: KZSU (`1KhuroWaBTvKo5i5voVk2iB_GwRgpfKfA`) > Show Prep (find or create). Never write to the Drive root. Never delete Drive files. Move prior weeks to KZSU/Archive/YYYY/MM-DD/.

### 7. Repo
Commit `data/recon/<target>/` and the review_suggestions file, then push. Never commit `.env`, `browser.json` or secrets. If the push fails, give the one command to run.

## Summary
Short bullets, AP style, no em dashes, no hyperbole.
- Target show date and the plan path.
- Picks by set with counts, and how many are R.
- FCC flags (word, count, section), UNVERIFIED tracks, tracks missing from YouTube Music.
- Stale or missing inputs.
- Drive and repo paths. Say which step failed, if any.

## Handoff
On show day, kzsu-show-build reads this plan, syncs it to Air Order, and builds the files. Scheduled task: `kzsu-thursday-recon`, Thursday 9:30 p.m. PT. Next: invoke `kzsu-notes-sheet-and-script` to build the Notes Sheet and Working Show Script.

## Zookeeper metadata

Read `references/zookeeper_enrichment.md`. Enrich every candidate in the plan (tag, label, album, `zk`) before writing `working_playlist.json`. Labels from Zookeeper, not the web.
