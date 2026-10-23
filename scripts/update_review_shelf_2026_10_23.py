#!/usr/bin/env python3
"""Add the Oct. 22, 2026 Music Dept promo releases to the Review Shelf working copy.

Steps, in plain terms:
1. Read data/staged/review_shelf.csv (the clean working copy kept in the repo).
2. Build one new row per announced album from the Tuesday sweep.
3. Skip any row whose artist and album are already on the shelf (no duplicates).
4. Put new rows at the top (the shelf is newest first).
5. Write the working copy back with the same columns, then write the upload CSV
   for Google Sheets (link columns dropped, Album and Label as =HYPERLINK()).

It never removes a row and never touches Stace's ticks, notes or date cells.
"""
import csv
from pathlib import Path
from urllib.parse import quote_plus

REPO = Path(__file__).resolve().parent.parent
WORKING = REPO / "data" / "staged" / "review_shelf.csv"
UPLOAD = REPO / "outputs" / "review_shelf_upload_2026-10-23.csv"
TODAY = "2026-10-23"
STATUS = "Music Dept promo (Vitriol Radio) Oct. 22; GOING FOR ADDS 10/27; library check pending"


def ytm_search(artist, album):
    """YouTube Music search link (music.youtube.com only)."""
    return "https://music.youtube.com/search?q=" + quote_plus(f"{artist} {album}")


NEW = [
    dict(Artist="Iceberg Black", Album="WTF", Label="Babygrande",
         date="2026-10 (verify; promo ADDS 10/27, day not found)", Type="single", Lead="WTF",
         FCC="CLEAN EDITED per promo (digital only; not screened by Claude)",
         Notes="New York phonk and underground hip-hop. First release since Frost Tape. Vitriol Radio promo. RIYL JPEGMAFIA, Denzel Curry, Ghostemane.",
         LabelUrl="https://babygrande.com"),
    dict(Artist="Jon Green", Album="Blue Hour", Label="Birthday Cake",
         date="2026-10-23 (verify; label site only)", Type="album", Lead="4, 1, 3, 9, 10, 6 (promo focus tracks)",
         FCC="CLEAN EDITED per promo (explicit versions also included; not screened by Claude)",
         Notes="Toronto. ADDS 10/27 at Top 200, R&B, Hip-Hop. RIYL Twin Shadow, Tyler, The Creator, Steve Lacy, Blood Orange, Tame Impala. Previous LP reached NACC Hip Hop top 15.",
         LabelUrl="https://birthdaycakerecords.com"),
]

with open(WORKING, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)

existing = {(r["Artist"].lower(), r["Album"].lower()) for r in rows}
added = []
for n in NEW:
    if (n["Artist"].lower(), n["Album"].lower()) in existing:
        continue
    row = {k: "" for k in fields}
    row.update({
        "Artist": n["Artist"], "Album": n["Album"], "Label": n["Label"],
        "Release date": n["date"], "Type": n["Type"], "Fit": "", "Status": STATUS,
        "Lead track": n["Lead"], "FCC status": n["FCC"], "Notes": n["Notes"],
        "Added": TODAY, "Album link": ytm_search(n["Artist"], n["Album"]), "Label link": n["LabelUrl"],
    })
    added.append(row)
rows = added + rows

with open(WORKING, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)


def link_formula(url, text):
    """Return a Sheets =HYPERLINK formula, or plain text if there is no link."""
    if not url or not text:
        return text
    return '=HYPERLINK("{}","{}")'.format(url.replace('"', '""'), text.replace('"', '""'))


upload_fields = [c for c in fields if c not in ("Album link", "Label link")]
with open(UPLOAD, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=upload_fields, lineterminator="\n")
    w.writeheader()
    for r in rows:
        out = {c: r[c] for c in upload_fields}
        out["Album"] = link_formula(r.get("Album link", ""), r["Album"])
        out["Label"] = link_formula(r.get("Label link", ""), r["Label"])
        w.writerow(out)

print("rows added:", len(added), "total rows:", len(rows),
      "ticks:", sum(1 for r in rows if r["Request (x)"].strip()))
