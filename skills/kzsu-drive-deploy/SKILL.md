---
name: kzsu-drive-deploy
description: >-
  Shared workflow for DJ Stace's KZSU project: keep working copies as CSV and Markdown in a Working folder that Claude manages, and deploy them to Drive as native Google Sheets and Docs for Stace to view and edit. Covers the Working folder layout, the file registry, harvesting Stace's edits (ticks and notes) from the Sheets and Docs before redeploying, creating the new Sheet or Doc, moving the old version to _to_delete, and verifying. Use whenever any KZSU skill creates or updates a Notes Sheet, Review Shelf, Working or Final Show Script, or any Sheet or Doc in the KZSU Drive folder, or when Stace asks to redeploy, refresh or republish a Sheet or Doc.
---

# KZSU Drive deploy (Working copies to Sheets and Docs)

Read `references/house_rules.md` and `config/paths.json` first.

## Why this exists

The Drive connector can create, rename, move and read files, but cannot edit a Google Sheet or Doc in place. So Claude never edits the Google versions. Claude edits plain working files (CSV, Markdown), then publishes a new Sheet or Doc from them and retires the old one.

## Layout

- **Working folder** (Claude manages, Stace can look): `<drive_local>/Working/` (local path in `config/paths.json`, syncs to Drive `/KZSU/Working/`). Files: `review_shelf.csv`, `notes_sheet_<show date>.csv`, `working_show_script_<show date>.md`, `final_show_script_<show date>.md`, `library_show_playlist_<show date>.csv`, `working_playlist_<show date>.md`.
- **What Stace sees** (Google formats):
  - `/KZSU/` top level: this week's finals, the Review Shelf Sheet, the Final Show Script Doc, the final Notes Sheet.
  - `/KZSU/Show Prep/`: next week's draft Sheets and Docs.
  - `/KZSU/Archive/YYYY/MM-DD/`: last week's finals.
- The Zookeeper CSV is uploaded raw (no conversion) because Zookeeper needs the CSV.
- Repo copies in `outputs/` stay the git record. Working/ is the live copy.
- Registry: `data/drive_registry.json` maps each artifact key to its Drive file ID, title, folder, deployed date and a content hash. Always read it first and update it last.

## Deploy procedure (every update of a Sheet or Doc)

1. **Harvest first.** Cheap gate: `get_file_metadata` on the deployed ID. If `modifiedTime` is within a minute of the deploy time in the registry, Stace has not edited it; skip the full read. Otherwise If a deployed version exists, read it back with the Drive `read_file_content` tool (by ID from the registry). Pull out Stace's changes:
   - Sheets: ticks in Cull, Replace, Request (TRUE, x or any other non-empty mark counts as ticked; FALSE and blank do not), edited notes, added rows, and edited cells.
   - Docs: edits to the script text, since she may have rewritten talk breaks. Merge her edits into the Markdown working file; when she changed a paragraph, her version wins.
   Write the harvested changes into the working file before regenerating. Never regenerate over her ticks.
2. **Edit the working file** (CSV or Markdown) with the new data. Keep a one-line change note in `data/drive_changelog.md`.
3. **Skip if unchanged.** If the content hash equals the registry hash, do nothing.
4. **Build the upload.**
   - Sheet: upload the CSV with `contentMimeType: text/csv` (converts to a Sheet). Mark columns with `x` for ticks (Cull, Replace, Request). Do not rely on TRUE/FALSE or native checkboxes.
   - Doc: run `python3 skills/kzsu-drive-deploy/scripts/md_to_html.py in.md out.html`, then upload the HTML with `contentMimeType: text/html` (converts to a Doc). Read the HTML back in and pass it as `textContent`.
5. **Create** the new file in the right folder (`parentId`), using the standard title (below). Never put anything in the Drive root.
6. **Retire the old version.** With `update_file`, move the old file to `/KZSU/_to_delete/` (id `1b2cmq-T--n7Ge2iQL3K5ajwDMK53zPMC`) and rename it `<title> (replaced YYYY-MM-DD HHMM)`. For a finished week, finals move to `/KZSU/Archive/YYYY/MM-DD/` instead. Claude cannot empty the trash, so Stace deletes `_to_delete` contents when she wants. Do not delete anything.
7. **Verify.** `read_file_content` on the new ID. Check row count (Sheet) or headings (Doc). If it fails, keep the old file where it was, report the error, and do not retire anything.
8. **Update the registry** (new ID, URL, hash, date), commit and push the repo, and tell Stace that the link changed.

Order matters: create the new file, verify, then retire the old one. Never retire first.

## Titles

- `Stace's KZSU Filtered Review Shelf`
- `Library Show Working Playlist Notes Sheet <show date>`
- `Library Show Working Show Script <show date>`
- `Library Show Final Show Script <show date>`

## Rules

- Redeploy only when content changed, since each redeploy changes the link. Batch changes: Tuesday and Friday sweeps, then Thursday night. The Wednesday Final Script is always a new file.
- If Stace is likely mid-edit (file modified in the last 10 minutes), harvest, wait and re-harvest before retiring.
- Mark conflicts in the changelog when both Stace and Claude changed the same cell. Stace wins.
- AP style, no em dashes.
- Drive for desktop caveat: files in `<drive_local>` are real only for CSV, Markdown and text. `.gsheet` and `.gdoc` there are pointers; do not edit them.

## Tested Oct. 4, 2026

- Harvest from a deployed Sheet works (`read_file_content` returns a table; a tick showed as TRUE). Cost is about 12k tokens for a 40-row sheet, so use the metadata gate.
- CSV upload converts to a Sheet; HTML upload converts to a Doc. Raw CSV needs `disableConversionToGoogleType: true`.
- Writes to the Working folder go through the Write tool at `working_dir`; Drive for desktop syncs them.
