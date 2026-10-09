#!/usr/bin/env python3
"""Mark the Oct. 9, 2026 review templates as done in the Review Shelf working copy.

What this does, step by step:
1. Reads data/staged/review_shelf.csv (the clean working copy kept in the repo).
2. Ticks the Request column for the rows Stace ticked in her Drive sheet.
3. Fills "Boilerplate done", "Added to To Review", the FCC status and a Template link.
4. Adds a row for The Tallest Man On Earth, which Stace typed into the sheet by hand.
5. Writes the updated working copy, plus an upload CSV for Google Sheets.
   The upload CSV drops the two link columns and turns Album and Label into
   =HYPERLINK() formulas, which is how the Sheet shows clickable names.
"""
import csv
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKING = REPO / "data" / "staged" / "review_shelf.csv"
UPLOAD = REPO / "outputs" / "review_shelf_upload_2026-10-09.csv"
DOC = "https://docs.google.com/document/d/{}/edit"  # pattern for a Google Doc link
TODAY = "2026-10-09"

# One entry per finished template: (artist, album) -> fields to write.
# "doc" is the Google Doc ID of the template in Drive (Staged Reviews > Review Templates).
DONE = {
    ("Death Valley Girls", "Welcome to Earth"): dict(
        doc="1wgiimd-P-K4Demw-zbjqhFwOo3i8QuA1t7MHhiwUeTg", added=f"{TODAY} (full album)",
        fcc="CLEAN (5 unverified)"),
    ("Stef Chura", "Dancing Alone on the Concrete"): dict(
        doc="1dk3ifv-R1W4_7oCQT1ZeJL7NqJ3ppImgL6oR0wNrkJ8", added=f"{TODAY} (full album)",
        fcc="CLEAN"),
    ("Teenage Fanclub", "Do Not Dare To Dream"): dict(
        doc="1s66tbge4KzWv79WSKvD4trscDBY4ArWhEoxA16n_qHA", added=f"{TODAY} (full album)",
        fcc="CLEAN"),
    ("Fontaines D.C.", "Dopamine Chamber"): dict(
        doc="1AZtFJqo61sRASX71q8XByR6PqV0FGhTcv3gTBWSqnJE",
        added=f"{TODAY} (Marianne only; album not on YTM until Oct. 16)",
        fcc='FCC "shit" x10 (Tongue, Refrain); Marianne, Six Shot Morning, Happy For You CLEAN; 7 unverified'),
    ("L7", "Loma Linda"): dict(
        doc="1mH5iPGLW1Wiq4_XGWjX-ew-gOh3TOR53eZZMsHZxetU", added=f"{TODAY} (single)",
        fcc="UNVERIFIED"),
    ("Little Barrie", "Luggin' Hurt"): dict(
        doc="1_9PgEkU6UDIcFy8M69CP85smBsuvzMwITEp22Nj7WrQ", added=f"{TODAY} (single)",
        fcc="UNVERIFIED"),
}

with open(WORKING, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames          # keep the same column order
    rows = list(reader)

# Step 2 and 3: tick and fill the finished rows.
found = set()
for r in rows:
    key = (r["Artist"], r["Album"])
    if key in DONE:
        d = DONE[key]
        found.add(key)
        r["Request (x)"] = "x"
        r["Boilerplate done"] = TODAY
        r["Added to To Review"] = d["added"]
        r["FCC status"] = d["fcc"]
        link = "Template: " + DOC.format(d["doc"])
        # Keep any older note and add the template link after it.
        r["Notes"] = (r["Notes"] + " " + link).strip() if "Template:" not in r["Notes"] else r["Notes"]
missing = set(DONE) - found
assert not missing, f"rows not found: {missing}"

# Step 4: add the Tallest Man On Earth row (template made Oct. 8, album added to To Review today).
tmoe = {k: "" for k in fields}
tmoe.update({
    "Request (x)": "x", "Artist": "The Tallest Man On Earth", "Album": "Just Beyond Endless Mountain",
    "Label": "ANTI-", "Release date": "2026-10-09", "Type": "album",
    "Status": "requested by Stace; not in library", "FCC status": "UNVERIFIED (no lyrics posted)",
    "Notes": "Template: " + DOC.format("1iPgNjerHf-vwZorz2BKWH8KpTNiUhm-B3mzK3wPUajA"),
    "Boilerplate done": "2026-10-08", "Added to To Review": f"{TODAY} (full album)", "Added": "2026-10-08",
    "Album link": "https://music.youtube.com/browse/MPREb_FFgH4K6rbJJ",
})
if not any(r["Artist"] == tmoe["Artist"] for r in rows):
    # Insert after the Oct. 9 rows and before the Oct. 6 rows, to keep newest-first order.
    idx = next(i for i, r in enumerate(rows) if r["Added"] <= "2026-10-08")
    rows.insert(idx, tmoe)

# Step 5a: write the working copy back (same columns, same order).
with open(WORKING, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

# Step 5b: build the upload CSV for Google Sheets.
def link_formula(url, text):
    """Return a Sheets =HYPERLINK formula, or the plain text if there is no link."""
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

print("rows:", len(rows), "ticked:", sum(1 for r in rows if r["Request (x)"] == "x"))
print("pending (ticked, no boilerplate date):",
      [(r["Artist"], r["Album"]) for r in rows if r["Request (x)"] == "x" and not r["Boilerplate done"]])
