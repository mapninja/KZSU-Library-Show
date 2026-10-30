#!/usr/bin/env bash
# build_show_script.sh <YYYY-MM-DD> <draft|final> [outDir]
# Builds the tracklist-first landscape show script (Word) and converts it to PDF with LibreOffice.
# Run from the repo root. Needs: node with the "docx" package, and soffice (LibreOffice).
set -euo pipefail
DATE="${1:?show date, e.g. 2026-11-05}"
STAGE="${2:-final}"
OUT="${3:-outputs/recon/$DATE}"
node scripts/build_show_script.js "$DATE" "$STAGE" "$OUT"
UP=$(echo "$STAGE" | tr '[:lower:]' '[:upper:]')
DOCX="$OUT/Library Show Script $DATE ($UP).docx"
# --convert-to pdf writes the PDF next to the Word file
soffice --headless --convert-to pdf --outdir "$OUT" "$DOCX" >/dev/null 2>&1
ls -1 "$OUT" | grep "Library Show Script $DATE ($UP)"
