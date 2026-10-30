---
name: kzsu-radar
description: Continuous new-release monitoring for DJ Stace's "The Library" on KZSU. Runs daily (light pass) and Tue and Fri (full pass with playlist writes). Reads Music Dept email, scans labels and Bandcamp, backfills release dates, ranks staged albums, refreshes "01 KZSU - New Releases for Review", adds to "01 KZSU - Stace's Weekly Playlist", and builds review templates for ticked shelf rows. Replaces the old daily-mark-email-check, mon-intake, mon-album-sweep, mon-health, tue-releases, fri-releases, tue-fri-new-releases-review and tue-fri-review-templates tasks.
---

# KZSU radar (one pipeline, three depths)

Read `references/house_rules.md`, `references/source_scans.md` and `config/playlists.json` first. Playlist titles now carry prefixes (`01 KZSU - `, `02 Personal - `, `03 Archive - `); ids in `config/playlists.json` do not change.

## Depth 1: daily light pass (task `kzsu-radar-daily`, 6:30 a.m., every day)
1. Email (read only). Search Outlook for Music Dept mail ("New Music Filtering", "KZSU Music: Adds") and Mark Mollineaux newer than `data/staged/email_index.json`. If any, follow `skills/kzsu-staged-albums-weekly/SKILL.md` steps 1 and 2.
2. Source scans. Follow step 3b of the same skill: indieisnotagenre and Bandcamp scans to `data/releases/source_scans/`, update `status.json`. Pitchfork is blocked; do not retry.
3. Release dates. Work about 25 items from `data/staged/release_dates_needed.json`. Day precision, two named sources before `confirmed: true`.
4. Staged priority list and Review Shelf. Run `python3 scripts/staged_crossref.py --top 40 --outside 25 --sync-shelf`. Patch the Review Shelf Sheet in place (read it first; keep ticks).
5. Queue. Retry anything in `data/daily/pending_ytm_writes.json`.

### Day-of-week extras on the daily run
- Monday: run `skills/kzsu-intake/SKILL.md` (Current Adds, College Radio Top 50 refresh) and `skills/kzsu-album-sweep/SKILL.md` (favorite labels, announced albums, lead singles aired). Finish with the health summary from `skills/kzsu-health-check/SKILL.md`, folded into the one email below.
- Friday: if `data/archive/<last Thursday>.json` is missing or the archive playlist id is not in `config/playlists.json`, run `skills/kzsu-archive-playlist/SKILL.md` (this replaces the Friday archive retry task).

## Depth 2: Tue and Fri full pass (task `kzsu-radar-playlists`, 7:30 a.m. and 1:30 p.m.)
Tuesday is new singles and announcements. Friday is albums and singles out today, plus Bay Area picks. The 1:30 p.m. run is a catch-up: only items released or announced since the morning run. Both runs:
1. `skills/kzsu-weekly-playlist/SKILL.md` sweep into `01 KZSU - Stace's Weekly Playlist`. ADD only. FCC-screen every track.
2. `skills/kzsu-new-releases-review/SKILL.md` refresh of `01 KZSU - New Releases for Review` (new singles and lead tracks on top, Sort > Newest first, expire only Claude's own adds after 14 days, log her deletes).
3. If a draft Air Order exists for the next show, delta-update the plan only (`skills/kzsu-weekly-recon/SKILL.md`). Do not edit `01 KZSU - Air Order` or `01 KZSU - Next Show` in YTM; Stace owns them until Thursday morning.
4. Review templates: `skills/kzsu-review-template/SKILL.md` for every ticked "Request (x)" row in the Review Shelf. None ticked: skip with one line.
5. Friday also: pull Bay Area picks from the shows tracker (`data/shows/bay_area_shows.csv`).

## Output
- One short email to maples@stanford.edu only on Mondays (health summary plus what changed) and when something needs her. Other days write `outputs/daily/<date>.md` and stop.
- Commit explicit paths only and push with the token in `.env` (never print it).
