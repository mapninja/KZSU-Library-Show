---
name: kzsu-thu-final
description: Thursday afternoon FINAL show package for DJ Stace's "The Library" on KZSU. Re-reads "01 KZSU - Air Order" (her morning edits win), rebuilds "01 KZSU - Working" in reverse, writes the reversed Zookeeper upload CSV, the final tracklist-first landscape show script (Word and PDF), and moves last week's finals to Archive.
---

# Thursday afternoon final (1:30 p.m. PT, show airs 6 p.m.)

Read `references/house_rules.md` and `config/playlists.json` first. Follow `skills/kzsu-show-build/SKILL.md` for the YTM and Zookeeper mechanics.

1. Read `01 KZSU - Air Order` by reloading it. Stace's edits since the morning draft win: sync the plan (cuts to `plan['cut']`, adds with metadata, place adds in the set that fits). Anything she cut is not printed.
2. Rewrite `01 KZSU - Working` as the exact reverse of Air Order. Deltas only; fix order with MOVE actions in Manual order, then verify by reload (first row is the last on-air track).
3. Zookeeper CSV `library_show_playlist_<show date>.csv`: reversed, six quoted columns, blank rows for mic breaks, library tag and label on every track, FCC-flagged tracks left out.
4. Final script: `scripts/build_show_script.sh <show date> final outputs/recon/<show date>`. Check the PDF: tracklist starts on page 1, Notes column filled, nothing cut left in.
5. Drive: move last week's finals from the KZSU top level to `Archive/YYYY/MM-DD/`; put this week's finals (Final Show Script Word and PDF, Notes Sheet, CSV, working_playlist.md) at the KZSU top level. Never the Drive root.
6. Email maples@stanford.edu one line with the PDF location and a list of anything flagged (FCC, unverified labels, missing tags).
7. Commit explicit paths and push.
