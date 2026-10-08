# Show script format: landscape tables (Stace's standing preference, Oct. 7, 2026)

Every show script (Working, Final, specialty) is delivered as a landscape, table-based file. Stace needs to find things fast while on air. Reference build: the Oct. 8 Final Show Script.

## Layout
- US Letter, landscape, 0.5 in margins, Arial 9 pt in tables, footer with show date and page number.
- Page 1: title line, "Run of show" table (set, tracks, set time, track numbers, running total, total vs the 2:30 target), "What changed" table, then talk-break tables (Today in music, new and coming up).
- Hour 1 and Hour 2 each start on a new page. One table per set, never split across pages.
  - Band row: set name | track count | set time | on-air-through time. Triple Shot gets an intro row.
  - Columns: #, Artist, Track, Album, Label, Tag, Time, FCC, Notes. Track title is the largest text.
  - FCC column color: green CLEAN, amber LISTEN FIRST or CLEAN, check ear, red HOLD. Held-out tracks stay in the table (row shaded red, "--" for number and time) but do not count toward time.
- Mid-show talk breaks are tables placed right after the set they follow (for example the Bay Area shows table after Set 4: Date | Act | Venue | Status | Track tonight).
- Back pages: FCC watch list table, Weekly Playlist bench table (Artist | Track | Release | Label | Date | FCC).
- No long prose. Tables only, with short notes. AP style, no em dashes.

## How to build
1. Export the plan's sets to `plan_for_docx.json` (`{"sets":[{"set","tracks":[...]}],"triple":"<Triple Shot angle>"}`; track fields: artist, track, album, label, tag, released, why, fcc_status, fcc_note, priority, duration).
2. Copy `scripts/build_landscape_script.js` next to the JSON. Update the show date text and the hand-coded talk-break, FCC watch list and bench tables for the week (they are written as arrays in the script).
3. `node build_landscape_script.js "<out>.docx"` (docx npm package is preinstalled). Validate with the docx skill's `validate.py`, convert to PDF with its `soffice.py`, render pages with `pdftoppm` and look at them before shipping.
4. Deliver both the `.docx` and the `.pdf` to the `/KZSU/` top level (Wednesday final) or `/KZSU/Show Prep/` (working draft), named `Library Show Final Show Script <show date> (Landscape Tables)` or `Library Show Working Show Script <show date> (Landscape Tables)`. Copies in `outputs/recon/<show date>/`.
5. The Drive connector cannot set page orientation on a native Google Doc, so the Word file and PDF are the deliverables. Stace can open the .docx in Google Docs; orientation is kept. The PDF is the on-air copy.

## Notes
- The Markdown `show_script.md` stays as the working data record in the repo.
- Wording for "Screened" in the bench table: the earlier FCC screen flagged nothing or was not noted as a hit. Never call a track CLEAN unless a lyric check said so.
