---
name: kzsu-thu-draft
description: Thursday morning DRAFT of show prep for DJ Stace's "The Library" on KZSU. Harvests Stace's edits to "01 KZSU - Next Show", "01 KZSU - Air Order" and the Weekly Playlist, updates the plan, writes the draft tracklist-first show script, Notes Sheet and draft Zookeeper CSV into KZSU/Show Prep. Replaces the old thu-show-sync morning half and the Wednesday final script.
---

# Thursday morning draft (8:00 a.m. PT)

Read `references/house_rules.md` and `config/playlists.json` first.

1. Harvest. Diff `01 KZSU - Next Show`, `01 KZSU - Air Order` and `01 KZSU - Stace's Weekly Playlist` against `data/daily/snapshots/`. Her adds are kept; her deletes get a 60-day cool-off (`data/daily/feedback.json`). New tracks from Next Show that are not in the plan join the set that fits their angle (`added_by: "DJ Stace"`).
2. Update `data/recon/<show date>/working_playlist.json`. Fill labels and ZK tags from Zookeeper (`references/zookeeper_enrichment.md`), FCC-screen new tracks (`skills/kzsu-fcc-lyrics-check/SKILL.md`).
3. Track notes. For every airable track fill `credits` (producer, studio, year), `related` (related bands, members' other bands) and `notes` (one sentence a DJ can say). Sources: Zookeeper, Discogs, Wikipedia, Bandcamp credits, media. Keep each under 30 words. Missing facts stay blank; never guess.
4. Bay Area shows and giveaways from `data/shows/bay_area_shows.csv` and `data/tickets/` (upcoming only, one giveaway in Hour 2).
5. Build the draft script: `scripts/build_show_script.sh <show date> draft outputs/recon/<show date>`. Tracklist first, general info last, landscape, PDF made by LibreOffice.
6. Build the draft Notes Sheet and Zookeeper CSV (`scripts/render_show_files.py`, reversed order). Put everything in `KZSU/Show Prep/` through `skills/kzsu-drive-deploy/SKILL.md`.
7. Do not write to YTM. Do not rewrite `01 KZSU - Working` (that is the afternoon run).
8. Commit explicit paths and push (token in `.env`).
