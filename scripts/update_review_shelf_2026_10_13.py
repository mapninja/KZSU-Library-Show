#!/usr/bin/env python3
"""Add the Oct. 13, 2026 Tuesday sweep releases to the Review Shelf working copy.

What this does, step by step:
1. Reads data/staged/review_shelf.csv (the clean working copy kept in the repo).
2. Builds one new row per release from the Tuesday sweep (new singles and albums).
3. Skips any row whose artist and album are already on the shelf (never duplicates).
4. Puts the new rows at the top, because the shelf is newest first.
5. Writes the working copy back with the same columns, then writes an upload CSV
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
UPLOAD = REPO / "outputs" / "review_shelf_upload_2026-10-13.csv"
TODAY = "2026-10-13"


def ytm_search(artist, album):
    """YouTube Music search link (music.youtube.com only) for an album or single."""
    return "https://music.youtube.com/search?q=" + quote_plus(f"{artist} {album}")


def bandcamp_label(name):
    """Bandcamp label search, used when we do not know the label's own site."""
    return "https://bandcamp.com/search?q=" + quote_plus(name) + "&item_type=b"


# One dict per release. Keys match the shelf's column names.
# "fit" comes from data/releases/upcoming_releases.csv where the release is listed.
NEW = [
    dict(Artist="Queens of the Stone Age", Album="Perfecth", Label="Matador Records (verify)",
         date="2026-10-30", Type="album", Fit="99.1", Lead="Where The Goth Girls At?",
         FCC="CLEAN (Where The Goth Girls At?, Insignificant Other)",
         Notes="Ninth album, produced by Josh Homme and Michael Shuman. Third single is Where The Goth Girls At? Easy Street (feat. Nikki Lane) is in cool-off to Dec. 8.",
         Plays="Queens of the Stone Age", Single="", LabelUrl="https://matadorrecords.com"),
    dict(Artist="Twisted Teens", Album="The Holy Cross Tigers", Label="Sub Pop Records (verify)",
         date="2026-11-06", Type="album", Fit="88.7", Lead="Stalks", FCC="CLEAN (Stalks)",
         Notes="Third Twisted Teens album of 2026. Stalks opens the record; When We First Met is already in Weekly. She requested Blame the Clown and Florida Water Blues earlier.",
         Plays="Twisted Teens", Single="", LabelUrl="https://www.subpop.com"),
    dict(Artist="Jozef Van Wissem & Jim Jarmusch", Album="Bocca di Lupo / Mouth of the Wolf",
         Label="Sacred Bones Records (verify)", date="2026-11-06", Type="album", Fit="67.2",
         Lead="Never Like You Said (feat. Courtney Barnett)", FCC="CLEAN (Never Like You Said)",
         Notes="Double album recorded in Bologna. Barnett duets on the lead single. Mostly instrumental otherwise.",
         Plays="", Single="", LabelUrl="https://www.sacredbonesrecords.com"),
    dict(Artist="TV Priest", Album="Cartoons", Label="AMK / Kartel Music Group (verify)",
         date="2026-11-06", Type="album", Fit="40.8", Lead="Cartoons",
         FCC="UNVERIFIED (no lyrics posted)",
         Notes="Third album. Title track out Oct. 9. London post-punk; adds piano and fiddle.",
         Plays="TV Priest", Single="", LabelUrl=bandcamp_label("Kartel Music Group")),
    dict(Artist="PISS", Album="you made me / skin on linen", Label="Sub Pop Records (verify)",
         date="2026-10-30", Type="album", Fit="40.0", Lead="time loop at hot slit",
         FCC="CAUTION: bitch x1 (time loop at hot slit)",
         Notes="Vancouver noise-punk debut. Lead single is 1:57. Title may draw attention on air. Fits the punk focus.",
         Plays="", Single="", LabelUrl="https://www.subpop.com"),
    dict(Artist="The Avalanches", Album="No Bad Memories", Label="Modular Recordings (verify)",
         date="2026-10-16", Type="album", Fit="31.2", Lead="Blue Shadows (feat. Karen O)",
         FCC="CAUTION: goddamn x2 (Can't Get Over Losing You); Blue Shadows CLEAN",
         Notes="Fourth album, 31 tracks, first since 2020. Singles with Karen O and Portraits Of Tracy are in Weekly.",
         Plays="The Avalanches", Single="", LabelUrl="https://www.modularrecordings.com"),
    dict(Artist="Fujiya & Miyagi", Album="New Shiny Object", Label="Impossible Objects of Desire (verify)",
         date="2026-10-30", Type="album", Fit="13.0", Lead="No Green Light",
         FCC="UNVERIFIED (no lyrics posted)",
         Notes="Brighton band. No Green Light runs 5:51.", Plays="", Single="",
         LabelUrl=bandcamp_label("Impossible Objects of Desire")),
    dict(Artist="Spiral XP", Album="Blue Earth (EP)", Label="Danger Collective / Den Tapes (verify)",
         date="2026-10-16", Type="EP", Fit="", Lead="Faith Electric",
         FCC="UNVERIFIED (no lyrics posted)",
         Notes="Seattle dream-rock. Faith Electric out Oct. 12.", Plays="", Single="",
         LabelUrl="https://dentapes.bandcamp.com"),
    dict(Artist="American Motors", Album="Functional Music", Label="Expert Work / The Ghost Is Clear (verify)",
         date="2026-11-06", Type="album", Fit="", Lead="marlboro miles",
         FCC="UNVERIFIED (no lyrics posted)",
         Notes="Recorded with Jawbox's J Robbins at Magpie Cage. marlboro miles is the final pre-release single (2:29). Punk focus.",
         Plays="", Single="", LabelUrl="https://theghostisclearrecords.bandcamp.com"),
    dict(Artist="David Byrne & Daniel Pemberton", Album="Let Me Sell You A Dream", Label="Matador Records (verify)",
         date="2026-10-08", Type="single", Fit="", Lead="Let Me Sell You A Dream", FCC="CLEAN",
         Notes="Song for Alex Gibney's film MUSK. Exclusive license to Matador.", Plays="", Single="",
         LabelUrl="https://matadorrecords.com"),
]

# Step 1: read the working copy.
with open(WORKING, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames  # keep the same column order
    rows = list(reader)

# Steps 2 and 3: build rows, skipping duplicates (artist plus album, ignoring case).
existing = {(r["Artist"].lower(), r["Album"].lower()) for r in rows}
added = []
for n in NEW:
    if (n["Artist"].lower(), n["Album"].lower()) in existing:
        continue
    row = {k: "" for k in fields}  # start blank so every column exists
    row.update({
        "Artist": n["Artist"], "Album": n["Album"], "Label": n["Label"],
        "Release date": n["date"], "Type": n["Type"], "Fit": n["Fit"],
        "Status": "Tuesday sweep Oct. 13; library check pending (Zookeeper blocked)",
        "Lead track": n["Lead"], "FCC status": n["FCC"], "Notes": n["Notes"],
        "Plays artist": n["Plays"], "Single aired": n["Single"], "Added": TODAY,
        "Album link": ytm_search(n["Artist"], n["Album"]), "Label link": n["LabelUrl"],
    })
    added.append(row)

# Step 4: new rows go first (newest additions at the top).
rows = added + rows

# Step 5a: write the working copy back (same columns, same order).
with open(WORKING, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)


def link_formula(url, text):
    """Return a Sheets =HYPERLINK formula, or the plain text if there is no link."""
    if not url or not text:
        return text
    return '=HYPERLINK("{}","{}")'.format(url.replace('"', '""'), text.replace('"', '""'))


# Step 5b: build the upload CSV for Google Sheets (no link columns, formulas instead).
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
      "ticked:", sum(1 for r in rows if r["Request (x)"].strip()))
