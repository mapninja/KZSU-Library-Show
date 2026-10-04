# KZSU rebuild plan (draft for approval)

Oct. 4, 2026. Single machine (this Mac). Nothing has been changed yet.

## 1. Goals

- Run everything on this Mac only. No Windows copy, no cross-machine sync.
- Match `newinstructions.md`: 13 YTM playlists, 2 Sheets, 2 Docs, 1 Zookeeper CSV, 1 dashboard.
- Make each weekly step small, restartable and checked.

## 2. Weekly clock (Pacific)

Show: Thursday 6-8 p.m. New releases land Fridays; Tuesdays catch singles and announcements.

| Day / time | Task | What it does |
|---|---|---|
| Sun 8:00 p.m. | `kzsu-taste-profile` | Pull Thursday's Zookeeper playlist, recount YTM playlists, rebuild profile and dashboard. |
| Mon 7:30 a.m. | `kzsu-intake` | Read Mark/Music Dept emails, Zookeeper Current Adds, college Top 50. Refresh "KZSU Current Adds" and "College Radio Top 50" playlists. Update Filtered Review Shelf sheet. |
| Mon 8:30 a.m. | `kzsu-health` | Report which tasks ran, failed or stalled. Emails a 5-line status. |
| Tue 6:30 a.m. | `kzsu-releases-tue` | Singles, announcements, label feeds, review sites. ADD to Weekly Playlist. Delta-update Air Order draft. |
| Tue / Fri 9:00 a.m. | `kzsu-review-templates` | Build boilerplate for ticked shelf rows. Save to KZSU-Album-Reviews. Add to "To Review". |
| Fri 6:30 a.m. | `kzsu-releases-fri` | Full new-release sweep. ADD to Weekly Playlist. Check "DJ Stace - Next Show" for new interests. |
| Fri 11:00 a.m. | `kzsu-show-draft` | Build NEXT Thursday's Air Order, Working, Notes Sheet and Working Show Script (6 days out). |
| Wed 8:00 p.m. | `kzsu-final-script` | Apply cull/replace boxes and Air Order edits. Build Final Script. Email link. |
| Thu 9:00 a.m. | `kzsu-show-sync` | Re-sync Working (reversed) and Zookeeper CSV from her Thursday-morning edits. Update Final Script if needed. |
| Thu 8:30 p.m. | `kzsu-archive` | Pull the aired playlist from Zookeeper. Build "The Library Show with DJ Stace (Month d, yyyy Show)". Retry Fri 7 a.m. if the log is incomplete. |
| 1st of month, 9 a.m. | `kzsu-specialty` | Look 6 weeks ahead. Build 2.5-hr suggestion playlists for holiday and topical shows. |
| Quarterly (Jan/Apr/Jul/Oct 1) | reminder | Re-export Google Takeout. |

Existing tasks to retire: `kzsu-thursday-working-rewrite`, `kzsu-daily-playlist`, `kzsu-staged-albums-weekly`. `kzsu-review-templates` is kept, with its new inputs. The non-KZSU tasks (morning brief, inbox triage) are untouched.

## 3. Skills

Keep and rework (7): `kzsu-taste-profile-refresh`, `kzsu-staged-albums-weekly` (becomes intake), `kzsu-weekly-recon` + `kzsu-weekly-playlist` (merged into releases), `kzsu-show-build`, `kzsu-review-template`, `kzsu-fcc-lyrics-check`.

New (5): `kzsu-notes-sheet-and-script`, `kzsu-final-script`, `kzsu-archive-playlist`, `kzsu-specialty-show`, `kzsu-health-check`.

Shared reference, read by all: `config/playlists.json` (every playlist ID and rule, one place), `config/paths.json`, `references/house_rules.md` (AP style, no em dashes, YTM only, delete rule, FCC rules, CSV format).

## 4. Artifacts and where they live

- Drive `/KZSU/` top level: current files only. `/KZSU/Archive/YYYY/MM-DD/` for last week's.
- Repo `KZSU-Library-Show`: all code, config, data.
- Repo `KZSU-Album-Reviews`: review boilerplate and finals. Not yet mounted here, so I need you to connect it.
- Zookeeper CSV name: `library_show_playlist_DATE.csv`, 6 columns (artist, track, album, tag, label, timestamp), reversed, blank row = mic break.

## 5. Shortcomings found in past work

**Conflicts with the new doc**
- The old weekly playlist skill clears last week's picks. The new doc says add, mostly never delete. Fix: no clearing; flag stale rows only.
- Air Order target was 3 to 4 hr. New doc is 1:15 per hour, so about 2:30.
- No skill exists for the Notes Sheet (cull/replace boxes), Final Script, archive playlist, specialty shows, Current Adds, Top 50 or Bay Area breaks.

**Reliability**
- The sandbox has no GitHub credentials. Every run needed you to push by hand. Stale `.git` lock files block commits.
- Sandbox network returns 403 for lyric APIs. FCC checks fell back to old results and left 6 tracks "unverified". Fix: browser fallback is the default, and unverified tracks are labeled not airable.
- Oct. 1 run died on a usage limit. Fix: stagger runs, split big ones, add retry runs.
- Tasks run only when the Mac is awake with the app open. Wed 8 p.m. and Thu 9 a.m. are the critical ones.
- Each task needs one manual "Run now" to pre-approve tools. Only `kzsu-review-templates` is enabled now.
- WebSearch caps at 200 per session. Cloudflare blocks AOTY and BrooklynVegan; Pitchfork is blocked in the browser. Fix: use RSS/label pages and Stereogum, indieisnotagenre, Bandcamp via browser; spread research across tasks.
- YTM browser automation is fragile (hidden tab, throttled timers, silent failures). Fix: try `ytmusicapi` for playlist writes first; keep the browser as fallback. Always reload and verify. Needs fresh `browser.json` headers; add an expiry check.
- Mounted folders break SQLite. Scripts must build in a temp dir and copy.
- Prompts hardcode `/Users/maples/...`. Fix: one `paths.json`.
- The Working-rewrite task prompt differs from its skill and still describes the old "Move to top" flip. Correct method is Sort > Newest first.

**Data and process**
- Reversed CSV: you asked for it, then it was uploaded forward, and the question was never closed. Fix: after upload, read the playlist back from the Zookeeper API and confirm first on-air track.
- The 9/24 import had durations in the label column. Whether it was patched is unrecorded.
- Staged-album data is stale (last filtering email June 20, last A-File adds Sept 3). Confirm sources.
- Review-template checklist has never had a ticked box. The new Review Shelf sheet replaces it.
- Takeout is the only full history; YTM API shows about 200 plays.
- Sheet checkboxes: Drive connector uploads raw files. Native Google Sheets with checkbox columns need the google-workspace route. I'll test this first.
- The KZSU API key is hardcoded in 7 files and `STATUS.md`. `browser.json` holds live cookies. Rotate and move to `.env`.
- Old files to retire to `_to_delete/`: `agents.md`, `instructions.md`, `STATUS.md`, `knowledge_base.json`, `scratch.txt`, `src/dj_stace`, broken notebooks, `.venv-1`, `config.yml`.
- Memory notes are stale (Sept. 26 pending approvals). I'll refresh them.

**Overlooked**
- Halloween show is Thu Oct. 29, and the build window is now. Also Thu Nov. 26 (Thanksgiving), Dec. 24, Dec. 31 and Feb. 11 (Valentine's is a Sunday).
- DST ends Nov. 1. Cron is local time, so no change, but the Thursday sync should be checked once.
- Bay Area shows break needs a source list (venue calendars, Bandsintown/Songkick, local press). Not in `sources.yml`.
- Legal ID and underwriting/PSA reminders are not in the script template. Optional.
- If a CULL removes a track that anchored a talk break, the break needs rewriting.
- On-air changes and requests: the archive playlist should show tracks Zookeeper has that YTM can't find, as a list.
- FCC-flagged strong tracks go to "FCC Edit needed", marked not airable 6 a.m. to 10 p.m., and called out in the script.
- No alert when a task fails. `kzsu-health` fixes that.

## 6. Rebuild order

1. Cleanup and security: rotate key, `.env`, retire old files, fix git locks, refresh memory.
2. Config: `playlists.json`, `paths.json`, `house_rules.md`.
3. Baseline taste profile and dashboard (Takeout + Zookeeper + YTM playlists).
4. Drive test: native Sheet with checkboxes, Doc, archive folders.
5. Rework existing skills, build 5 new ones, repackage `.skill` files, confirm they open.
6. Dry run of one full week against Oct. 8 and Oct. 15.
7. Create tasks, run each once to approve tools, enable.
8. Halloween playlist for Oct. 29 in parallel with step 5.

## 7. Decisions needed

1. Is Sat/Fri 11 a.m. right for the draft, or do you want it Sunday?
2. Reversed CSV: confirm Zookeeper expects last track first.
3. Playlist API: OK to use `ytmusicapi` with your headers, browser as fallback?
4. Can I rotate the KZSU API key, or do you do it?
5. Connect `KZSU-Album-Reviews` as a workspace folder?
6. Bay Area venues to prioritize?
7. OK to pause or delete the old Mac tasks listed above?
8. Push method: you push each week, or add a GitHub token in `.env`?

---

## 8. As built (Oct. 4, 2026)

Decisions applied:
- Early draft now runs Thursday 9:30 p.m. after the show (task `kzsu-thu-night-draft`). Archive runs 8:30 p.m., retry Friday 8 a.m.
- Zookeeper CSV and Working are reversed.
- ytmusicapi is blocked in the sandbox (403), so the signed-in built-in browser is the working route. Skills try the API first only if the shell can reach YTM.
- Bay Area source: foopee.com, filtered by taste, giveaway venues first.
- GitHub token in `.env`. KZSU key unchanged.
- All new tasks are created PAUSED. Old tasks paused for deletion after testing.

Built:
- `config/playlists.json`, `config/paths.json`, `references/house_rules.md`.
- Baseline DB, taste profile JSON and dashboard rebuilt from saved data.
- Skills (repo `skills/` is the source of truth; task prompts read them from the repo): reworked `kzsu-weekly-playlist`, `kzsu-weekly-recon`, `kzsu-show-build`, `kzsu-review-template`; new `kzsu-intake`, `kzsu-notes-sheet-and-script`, `kzsu-final-script`, `kzsu-archive-playlist`, `kzsu-specialty-show`, `kzsu-health-check`.
- 12 new paused tasks. 6 old tasks paused.

Not done yet:
- Dry run of each skill (Sheets with checkboxes, archive playlist, final script are untested).
- `TASTE_PROFILE.md` regeneration and report.
- Halloween (Oct. 29) playlist.
- Creating the 3 new playlists (Current Adds, Top 50, archive) and resetting To Review.
- Stale `.git/*.lock` files need delete permission.

## 9. Oct. 4 progress

- Halloween 2026 playlist built (45 tracks, PLPKWMgnm3SDs). Plan JSON with a theme field still to be written so the regular pipeline can run it.
- Oct. 1 archive playlist built (PLTqLTSGi_8aY).
- Oct. 8 draft: Air Order (37 tracks, 2:25) and Working (reversed) replaced. Files in `outputs/recon/2026-10-08/`.
- Rule added: specialty shows get the full weekly pipeline, with Today in Music and new releases folded in when they fit.
- Rule added: playlist Edit (pencil) enables manual sort and drag.
