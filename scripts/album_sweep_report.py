#!/usr/bin/env python3
"""
album_sweep_report.py
=====================

Step 3 of the weekly ALBUM SWEEP (skills/kzsu-album-sweep/SKILL.md).

After the browser step, the assistant saves what it found as:

    data/album_sweep/findings_<date>.json      (a list of album records)

This script turns that file into:

    outputs/albums/<date>.md                   the weekly report (read by Stace)
    data/album_sweep/albums_<date>.csv         the same rows as a table
    data/album_sweep/ledger.json               every album ever reported, so the
                                               same album is not flagged twice

HOW TO RUN (from the repository root):

    python scripts/album_sweep_report.py --date 2026-10-19

Each record in findings_<date>.json uses these keys (all text unless noted):

    artist, album, label, release_date (YYYY-MM-DD, or YYYY-MM if unknown),
    status ("released" or "announced"),
    bucket ("label", "playlist" or "lead_single"; a list is fine for several),
    via       why it matched: label name, playlist name, or the lead single,
    lead_single, lead_single_url   (optional) the single Stace has aired
    fit       one line on why it fits her taste
    fcc_note  FCC screen result on the lead track, "not screened" if skipped
    source_url, ytm_url
    sources   how many independent sources confirm the date (number)

Beginner notes
--------------
* A "ledger" is just a JSON file that remembers past results. Before writing
  the report we check it, so an album that was already reported is marked
  "seen" instead of "new". Announced albums are reported again once, when
  they are released, because their status changes.
"""

# ---------------------------------------------------------------------------
# Imports. All of these ship with Python.
# ---------------------------------------------------------------------------
import argparse      # read options typed on the command line
import csv           # write the table version
import json          # read and write JSON files
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SWEEP_DIR = ROOT / "data" / "album_sweep"
REPORT_DIR = ROOT / "outputs" / "albums"
LEDGER = SWEEP_DIR / "ledger.json"

# CSV columns, in order.
COLUMNS = ["artist", "album", "label", "release_date", "status", "bucket",
           "via", "lead_single", "fit", "fcc_note", "sources",
           "source_url", "ytm_url", "report_flag"]


def album_key(rec):
    """Identify an album: lowercase artist + album title."""
    return f"{rec['artist'].strip().lower()}|{rec['album'].strip().lower()}"


def as_list(value):
    """Buckets may be one string or a list. Always return a list."""
    if isinstance(value, list):
        return value
    return [value] if value else []


def load_ledger():
    """Read the ledger, or start an empty one."""
    if LEDGER.exists():
        return json.loads(LEDGER.read_text())
    return {"_note": "Albums reported by the weekly album sweep. "
                     "Key = artist|album.", "albums": {}}


def flag_records(records, ledger, today):
    """Mark each record 'new', 'now released' or 'seen' against the ledger."""
    for rec in records:
        old = ledger["albums"].get(album_key(rec))
        if old is None:
            rec["report_flag"] = "new"
        elif old["status"] == "announced" and rec["status"] == "released":
            rec["report_flag"] = "now released"
        else:
            rec["report_flag"] = "seen"
        # Remember it for next week.
        ledger["albums"][album_key(rec)] = {
            "artist": rec["artist"], "album": rec["album"],
            "label": rec.get("label", ""),
            "release_date": rec.get("release_date", ""),
            "status": rec["status"],
            "first_reported": old["first_reported"] if old else today,
            "last_reported": today,
        }


def md_line(rec):
    """One report bullet for an album."""
    buckets = ", ".join(as_list(rec.get("bucket")))
    text = (f"- **{rec['artist']}, *{rec['album']}*** "
            f"({rec.get('label') or 'label unverified'}; "
            f"{rec.get('release_date') or 'date unverified'})")
    if rec.get("lead_single"):
        single = rec["lead_single"]
        if rec.get("lead_single_url"):
            single = f"[{single}]({rec['lead_single_url']})"
        text += f" Lead single: {single}."
    if rec.get("fit"):
        text += f" Fit: {rec['fit']}"
        if not rec["fit"].endswith("."):
            text += "."
    if rec.get("via"):
        text += f" Via {buckets}: {rec['via']}."
    if rec.get("fcc_note"):
        text += f" FCC: {rec['fcc_note']}."
    links = []
    if rec.get("ytm_url"):
        links.append(f"[YTM]({rec['ytm_url']})")
    if rec.get("source_url"):
        links.append(f"[source]({rec['source_url']})")
    if links:
        text += " " + " | ".join(links)
    if rec.get("sources") in (0, 1):
        text += " (verify date: one source)"
    return text


def build_markdown(records, today):
    """Assemble the weekly report text."""
    out = [f"# Album sweep, {today}", ""]
    out.append("New and announced albums from favorite labels, the Weekly and "
               "New Releases for Review playlists, and albums behind lead "
               "singles aired on The Library. Sorted by release date within "
               "each section.")
    out.append("")
    sections = [
        ("Out now (last 14 days)", lambda r: r["status"] == "released"),
        ("Announced (next 60 days)", lambda r: r["status"] == "announced"),
    ]
    for title, test in sections:
        rows = sorted((r for r in records if test(r)),
                      key=lambda r: r.get("release_date", ""),
                      reverse=(title.startswith("Out")))
        out.append(f"## {title}")
        out.append("")
        fresh = [r for r in rows if r["report_flag"] != "seen"]
        seen = [r for r in rows if r["report_flag"] == "seen"]
        if not rows:
            out.append("None found.")
            out.append("")
            continue
        for rec in fresh:
            tag = "NEW" if rec["report_flag"] == "new" else "NOW RELEASED"
            out.append(md_line(rec) + f" [{tag}]")
        if seen:
            out.append("")
            out.append(f"Already reported earlier ({len(seen)}): " +
                       "; ".join(f"{r['artist']}, {r['album']}" for r in seen))
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Render the album sweep report.")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="sweep date (YYYY-MM-DD)")
    args = ap.parse_args()

    findings = SWEEP_DIR / f"findings_{args.date}.json"
    if not findings.exists():
        raise SystemExit(f"Missing {findings.relative_to(ROOT)}. "
                         "Save the browser findings there first.")
    records = json.loads(findings.read_text())

    # De-duplicate: one row per album. If an album shows up in several
    # buckets, merge the buckets into one list.
    merged = {}
    for rec in records:
        key = album_key(rec)
        if key in merged:
            merged[key]["bucket"] = sorted(
                set(as_list(merged[key].get("bucket")) +
                    as_list(rec.get("bucket"))))
            if not merged[key].get("lead_single") and rec.get("lead_single"):
                merged[key]["lead_single"] = rec["lead_single"]
                merged[key]["lead_single_url"] = rec.get("lead_single_url", "")
        else:
            merged[key] = rec
    records = list(merged.values())

    ledger = load_ledger()
    flag_records(records, ledger, args.date)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORT_DIR / f"{args.date}.md"
    report.write_text(build_markdown(records, args.date))

    table = SWEEP_DIR / f"albums_{args.date}.csv"
    with table.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            row = dict(rec)
            row["bucket"] = "; ".join(as_list(rec.get("bucket")))
            writer.writerow(row)

    LEDGER.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n")

    new = sum(r["report_flag"] != "seen" for r in records)
    print(f"Wrote {report.relative_to(ROOT)} ({len(records)} albums, {new} new)")
    print(f"Wrote {table.relative_to(ROOT)} and updated the ledger")


if __name__ == "__main__":
    main()
