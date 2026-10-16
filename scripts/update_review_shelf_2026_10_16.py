#!/usr/bin/env python3
"""Add the Oct. 16, 2026 Friday sweep releases to the Review Shelf working copy.

What this does, step by step:
1. Reads data/staged/review_shelf.csv (the clean working copy kept in the repo).
2. Builds one new row per release from the Friday sweep (new singles and albums).
3. Skips any row whose artist and album are already on the shelf (never duplicates).
4. Updates only the Status cell of three rows already on the shelf (the albums came
   out today and their lead tracks were added to Weekly).
5. Puts the new rows at the top, because the shelf is newest first.
6. Writes the working copy back with the same columns, then writes an upload CSV
   for Google Sheets. The upload CSV drops the two link columns and turns Album
   and Label into =HYPERLINK() formulas, which is how the Sheet shows clickable names.

It never removes a row and never touches Stace's ticks, notes or date cells.
"""
import csv
from pathlib import Path
from urllib.parse import quote_plus

# Paths are built from this file's location so the script runs from any folder.
REPO = Path(__file__).resolve().parent.parent
WORKING = REPO / "data" / "staged" / "review_shelf.csv"
UPLOAD = REPO / "outputs" / "review_shelf_upload_2026-10-16.csv"
TODAY = "2026-10-16"
STATUS = "Friday sweep Oct. 16; library check pending (Zookeeper blocked)"


def ytm_search(artist, album):
    """YouTube Music search link (music.youtube.com only) for an album or single."""
    return "https://music.youtube.com/search?q=" + quote_plus(f"{artist} {album}")


def bandcamp_artist(name):
    """Bandcamp artist search, used when we do not know the label's own site."""
    return "https://bandcamp.com/search?q=" + quote_plus(name) + "&item_type=b"


# One dict per release. Keys match the shelf's column names.
# "Fit" comes from data/releases/upcoming_releases.csv where the release is listed.
NEW = [
    dict(Artist="@", Album="Autosmile", Label="4AD", date="2026-10-16", Type="album",
         Fit="40.0", Lead="Autosmile", FCC="CLEAN (Autosmile, I Know You Are (But What Am I Thinking))",
         Notes="Philadelphia art-folk duo, second album, first for 4AD. Title track runs nearly 7 minutes.",
         Plays="", Single="", LabelUrl="https://4ad.com"),
    dict(Artist="Eels", Album="Cookie Happened", Label="E Works / Play It Again Sam", date="2026-10-16",
         Type="album", Fit="13.0", Lead="Cap In Hand", FCC="CLEAN (Cap In Hand)",
         Notes="16th album. Cap In Hand was the lead single in June.", Plays="", Single="",
         LabelUrl="https://www.playitagainsam.com"),
    dict(Artist="Radie Peat", Album="No Human Tongue Can Tell", Label="Rough Trade Records",
         date="2026-11-13", Type="album", Fit="40.0", Lead="Hares on The Mountain",
         FCC="UNVERIFIED (no lyrics posted)",
         Notes="Debut solo album by the Lankum vocalist. Hares on The Mountain is a traditional song, single out Oct. 15.",
         Plays="", Single="", LabelUrl="https://roughtraderecords.com"),
    dict(Artist="Blondie", Album="Spectral Eyes (single)", Label="unverified", date="2026-10-16",
         Type="single", Fit="9.1", Lead="Spectral Eyes", FCC="CLEAN (Spectral Eyes)",
         Notes="New single, date from the Shatter the Standards Oct. 16 list only (verify). Blondie have 3 shows on air.",
         Plays="Blondie", Single="", LabelUrl=bandcamp_artist("Blondie")),
    dict(Artist="The Smashing Pumpkins", Album="Black Stars (single)", Label="unverified",
         date="2026-10-16", Type="single", Fit="", Lead="Black Stars", FCC="CLEAN (Black Stars)",
         Notes="From The Hunger Games: Sunrise on the Reaping soundtrack. Stereogum, Oct. 16.",
         Plays="Smashing Pumpkins", Single="", LabelUrl=bandcamp_artist("Smashing Pumpkins")),
    dict(Artist="Now, Now", Album="Slide (single)", Label="unverified", date="2026-10-15",
         Type="single", Fit="", Lead="Slide", FCC="CLEAN (Slide)",
         Notes="New single. Stereogum, Oct. 15.", Plays="", Single="",
         LabelUrl=bandcamp_artist("Now, Now")),
    dict(Artist="Bodywash", Album="La Renommée (single)", Label="unverified", date="2026-10-15",
         Type="single", Fit="", Lead="La Renommée", FCC="UNVERIFIED (no lyrics posted)",
         Notes="New single, French title. Stereogum, Oct. 15.", Plays="", Single="",
         LabelUrl=bandcamp_artist("Bodywash")),
]

# Rows already on the shelf whose albums came out today. Only the Status cell changes.
STATUS_UPDATES = {
    ("heavens to betsey", "baby's gone"):
        "Out Oct. 16 (Kill Rock Stars). Three tracks added to Weekly Oct. 16. Plays Bottom of the Hill Oct. 18.",
    ("dummy", "do you love the color of the sky?"):
        "Out Oct. 16 (Polyvinyl). Three tracks added to Weekly Oct. 16; Full Spectrum Dominance aired Oct. 15.",
    ("fontaines d.c.", "dopamine chamber"):
        "Out Oct. 16 (XL Recordings). Six Shot Morning, Mimesis, Happy For You added to Weekly Oct. 16.",
}

# Step 1: read the working copy.
with open(WORKING, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames  # keep the same column order
    rows = list(reader)

# Step 4: update Status on the three existing rows (match artist plus album, ignoring case).
updated = []
for r in rows:
    key = (r["Artist"].lower(), r["Album"].lower())
    if key in STATUS_UPDATES:
        r["Status"] = STATUS_UPDATES[key]
        updated.append(r["Artist"])

# Steps 2 and 3: build rows, skipping duplicates.
existing = {(r["Artist"].lower(), r["Album"].lower()) for r in rows}
added = []
for n in NEW:
    if (n["Artist"].lower(), n["Album"].lower()) in existing:
        continue
    row = {k: "" for k in fields}  # start blank so every column exists
    row.update({
        "Artist": n["Artist"], "Album": n["Album"], "Label": n["Label"],
        "Release date": n["date"], "Type": n["Type"], "Fit": n["Fit"], "Status": STATUS,
        "Lead track": n["Lead"], "FCC status": n["FCC"], "Notes": n["Notes"],
        "Plays artist": n["Plays"], "Single aired": n["Single"], "Added": TODAY,
        "Album link": ytm_search(n["Artist"], n["Album"]), "Label link": n["LabelUrl"],
    })
    added.append(row)

# Step 5: new rows go first (newest additions at the top).
rows = added + rows

# Step 6a: write the working copy back (same columns, same order).
with open(WORKING, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)


def link_formula(url, text):
    """Return a Sheets =HYPERLINK formula, or the plain text if there is no link."""
    if not url or not text:
        return text
    return '=HYPERLINK("{}","{}")'.format(url.replace('"', '""'), text.replace('"', '""'))


# Step 6b: build the upload CSV for Google Sheets (no link columns, formulas instead).
upload_fields = [c for c in fields if c not in ("Album link", "Label link")]
with open(UPLOAD, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=upload_fields, lineterminator="\n")
    w.writeheader()
    for r in rows:
        out = {c: r[c] for c in upload_fields}
        out["Album"] = link_formula(r.get("Album link", ""), r["Album"])
        out["Label"] = link_formula(r.get("Label link", ""), r["Label"])
        w.writerow(out)

print("rows added:", len(added), "status updated:", updated, "total rows:", len(rows),
      "ticks:", sum(1 for r in rows if r["Request (x)"].strip()))
