---
name: kzsu-notes-sheet-and-script
description: >-
  Builds and maintains DJ Stace's "Library Show Working Playlist Notes Sheet" (Google Sheet) and "Library Show Working Show Script" (Google Doc) for "The Library" on KZSU 90.1 FM. The sheet follows the order of the draft plan, with artist, track, album, original release date, label, notes, playtime, FCC status with lyrics link, thematic, topical and date notes, mic break talking points, and checkbox columns "cull" and "replace". The doc mirrors the sheet inline for each track, formatted for a laptop screen, with a Bay Area shows air break. Use after the Thursday-night draft, when Tuesday and Friday sweeps change the draft, or whenever Stace asks to rebuild the notes sheet or working script, even if she does not name the skill.
---

# KZSU notes sheet and working script

Read `references/house_rules.md` and `config/playlists.json`. Use `anthropic-skills:google-workspace` for every Drive write.

## Input
`data/recon/<show date>/working_playlist.json`, built by `kzsu-weekly-recon`, and the Air Order playlist (her edits win).

## Sheet: "Library Show Working Playlist Notes Sheet"
- One native Google Sheet in /KZSU/. One tab per show date is not needed; replace the contents each week after archiving last week's copy to /KZSU/Archive/YYYY/MM-DD/.
- Order: same as the Weekly Playlist adds and the plan (forward air order).
- Columns: #, Set, Artist, Track, Album, Original release date, Label, Playtime, Notes (why it is here), Theme/topic/date note, FCC status, Lyrics link, Mic break talking points, Source, **cull** (checkbox), **replace** (checkbox), Bay Area (venue/date if any).
- Never overwrite her ticks. On a re-run, merge by videoId and keep cull/replace values.
- Mic break points: 2 to 3 facts per break from date-in-music, release context, label, tour dates. AP style, no hyperbole. No lyrics.

## Doc: "Library Show Working Show Script"

Format: landscape, table-based Word file plus PDF per `references/show_script_landscape.md` (Stace's standing preference since Oct. 7, 2026). The notes below describe the content; present it in tables.

- Native Google Doc in /KZSU/. Readable on a laptop: big headings per set, one block per track.
- Each track block: artist, track, album, label, release date, playtime, FCC flag, notes, talk points, inline.
- FCC items are called out at the top of the doc and on the track, with the exact word and count.
- Mark the **Thursday Triple Shot** set (one artist, three songs) with a bold header and a one-line intro in the script, plus one setup line per track. Never cull the set partially without asking: if one track is culled, flag that the segment drops to two.
- Include a **Bay Area shows air break** after hour 1 or between sets: 3 to 5 upcoming shows from http://www.foopee.com/punk/the-list/ that match her taste, prioritizing KZSU giveaway venues. Venue, date, one line each.
- Include time checks, station ID reminder at the top of each hour, and total runtime vs 2:00.

## Steps
1. Read plan and Air Order. Build rows.
2. Create or update the sheet. Create or update the doc.
3. Run at: Thursday 9:30 p.m. (after the draft), and again after Tuesday and Friday sweeps if the plan changed.
4. Commit and push `data/recon/`. Summary: row count, FCC flags, links.

## Zookeeper metadata

Read `references/zookeeper_enrichment.md`. Anything YTM and Zookeeper cannot supply comes from Discogs, then Wikipedia and media sources (see the fallback section there), with source and URL recorded. Label, album and a Tag column in the sheet come from Zookeeper fields in the plan. Re-run the enrichment for tracks Stace added or that replaced a cull. Show the label as Zookeeper spells it.

## Drive placement

Follow the Drive layout in `references/house_rules.md`: drafts and next-week materials go in `/KZSU/Show Prep/`. Only final artifacts for the coming show go at the `/KZSU/` top level, and the previous week's finals move to `/KZSU/Archive/YYYY/MM-DD/` first.

## Deploying Sheets and Docs

Edit the CSV or Markdown working copy in `/KZSU/Working/`, then deploy with `skills/kzsu-drive-deploy/SKILL.md` (harvest Stace's edits first, create new, verify, retire old, update the registry).
