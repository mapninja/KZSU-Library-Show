#!/usr/bin/env python3
"""Add the Oct. 20, 2026 Tuesday sweep releases to the Review Shelf working copy.

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
UPLOAD = REPO / "outputs" / "review_shelf_upload_2026-10-20.csv"
TODAY = "2026-10-20"
STATUS = "Tuesday sweep Oct. 20; lead track in Weekly; library check pending (Zookeeper blocked)"


def ytm_search(artist, album):
    """YouTube Music search link (music.youtube.com only)."""
    return "https://music.youtube.com/search?q=" + quote_plus(f"{artist} {album}")


NEW = [
    dict(Artist="Soul Glo", Album="NA I'M GON GRAB ALLAT", Label="Epitaph Records",
         date="2027-01-15 (verify; Stereogum only)", Type="album", Lead="Ppl Worried (feat. Tunde Adebimpe)",
         FCC="UNVERIFIED (no lyrics posted yet; check before air)",
         Notes="Philadelphia punk band. Follow-up to Diaspora Problems. Singles: February Theory, Ppl Worried with Tunde Adebimpe of TV on the Radio (Oct. 20).",
         LabelUrl="https://epitaph.com"),
    dict(Artist="Hot Chip", Album="A Long Way From Kansas", Label="unverified",
         date="2027-01 (verify; Stereogum only)", Type="album", Lead="Random Violence",
         FCC="CLEAN (Random Violence, Genius)",
         Notes="Ninth album, first in almost five years. Guests: Beth Ditto, Eddie Chacon. Random Violence honors Keith McIvor of Optimo.",
         LabelUrl="https://bandcamp.com/search?q=Hot+Chip&item_type=b"),
    dict(Artist="Fake Names", Album="Punk Ruins", Label="Epitaph Records",
         date="2026-10-23", Type="album", Lead="Punk Ruins",
         FCC="CLEAN (Punk Ruins, Genius; short, check by ear)",
         Notes="Punk supergroup. Title track is 2:37. Fits the punk focus.",
         LabelUrl="https://epitaph.com"),
    dict(Artist="Disfear", Album="The Last Nail", Label="Relapse Records",
         date="2026-11-20 (verify; Stereogum only)", Type="album", Lead="Shackled To Our Vice",
         FCC="UNVERIFIED (no lyrics posted)",
         Notes="Last album recorded before two members died. D-beat punk from Sweden.",
         LabelUrl="https://relapse.com"),
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
