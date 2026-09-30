#!/usr/bin/env python3
"""
staged_crossref.py
==================

Ranks the albums the KZSU music department has STAGED for review (from Mark's
"New Music Filtering" emails) against DJ Stace's taste profile, and checks
them against the A-File adds and the Zookeeper library.

INPUTS
    data/staged/filtering_albums.json   albums/singles pulled from the emails
    data/staged/afile_adds.json         "KZSU Music: Adds" (already reviewed)
    config/taste_profile.json           built by build_taste_profile.py
    data/recon/*/candidates.json        this week's recon (for overlap)
    outputs/reviews/review_suggestions_*.md  outside research picks (overlap)

OUTPUTS
    outputs/reviews/staged_priority_<date>.md
    outputs/reviews/staged_priority_<date>.csv

HOW TO RUN
    python scripts/staged_crossref.py            # scoring only
    python scripts/staged_crossref.py --library  # also ask Zookeeper whether
                                                 # each top album is in the library

How the fit score works (beginner explanation)
----------------------------------------------
Promoters list "RIYL" (recommended if you like) artists for every release.
If those RIYL artists are artists you already play, the release probably fits.

    artist_match  = your profile score for the artist itself (0-100)
    riyl_match    = sum of your profile scores for each RIYL artist
    label_match   = 10 points per log-step of how often you play the label
    overlap_bonus = +15 if the release is also in this week's recon or
                    in the outside review suggestions

    rotation_bonus = you have been airing this artist lately (your show leans
                    new, so an album whose singles you already play ranks high):
                    +30 if the artist aired in the last 120 days,
                    +5 per show they aired on in that window (max +25),
                    +20 more if a recent spin came from this same release
    newness       = +10 for albums from the most recent staged email batch

fit = artist_match + 0.6 * riyl_match (capped at 120) + label_match
      + overlap_bonus + rotation_bonus + newness
"""
import argparse
import csv
import glob
import json
import math
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_music_db import artist_key, label_key  # reuse the same name matching


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def outside_picks() -> set:
    """Artist keys named in this week's recon and the review-suggestion files."""
    keys = set()
    for f in glob.glob(str(ROOT / "data/recon/*/candidates.json")):
        for s in load_json(f)["sets"]:
            keys |= {artist_key(t["artist"]) for t in s["tracks"]}
    for f in glob.glob(str(ROOT / "outputs/reviews/review_suggestions_*.md")):
        for m in re.finditer(r"^\| \d+ \| ([^,|]+),", Path(f).read_text(encoding="utf-8"), re.M):
            keys.add(artist_key(m.group(1)))
    return keys


def library_status(artist: str, title: str, headers: dict) -> str:
    """Ask Zookeeper if the album exists. Tries 'Name' and 'Last, First' forms."""
    import requests
    forms = [artist]
    parts = artist.split()
    if len(parts) == 2:
        forms.append(f"{parts[1]}, {parts[0]}")
    if artist.lower().startswith("the "):
        forms.append(artist[4:] + ", The")
    for form in forms:
        try:
            r = requests.get("https://zookeeper.stanford.edu/api/v1/album", headers=headers,
                             params={"filter[artist]": form, "page[size]": 25,
                                     "fields[album]": "artist,album,location"}, timeout=60)
            data = r.json().get("data", []) if r.text.strip().startswith("{") else []
        except Exception:
            data = []
        for a in data:
            if title.lower()[:12] in a["attributes"]["album"].lower():
                return f"in library ({a['attributes'].get('location')}, tag {a['id']})"
        time.sleep(0.3)
    return "not in library"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", action="store_true", help="check Zookeeper for the top albums")
    ap.add_argument("--top", type=int, default=60)
    args = ap.parse_args()

    prof = load_json(ROOT / "config/taste_profile.json")
    a_score = {a["key"]: a["score"] for a in prof["artists"]}
    a_name = {a["key"]: a["artist"] for a in prof["artists"]}
    l_spins = {label_key(l["label"]): l["spins"] for l in prof["labels"]}
    staged = load_json(ROOT / "data/staged/filtering_albums.json")
    adds = load_json(ROOT / "data/staged/afile_adds.json")
    # artist_key() also works on titles: "Former Site Of, The" -> "former site of"
    added = {(artist_key(a["artist"])[:10], artist_key(a["album"])[:10]) for a in adds}
    picks = outside_picks()

    # ---- Recent airplay (last 120 days) from the local database ------------
    # Read-only SQLite query; no network needed.
    import sqlite3
    from datetime import timedelta
    since = (date.today() - timedelta(days=120)).isoformat()
    con = sqlite3.connect(f"file:{ROOT / 'data' / 'library_show.db'}?mode=ro&immutable=1", uri=True)
    recent_shows = dict(con.execute(
        "SELECT artist_key, COUNT(DISTINCT playlist_id) FROM v_airplay WHERE date >= ? GROUP BY artist_key", (since,)))
    recent_albums = {}
    for k, alb in con.execute("SELECT DISTINCT artist_key, album FROM v_airplay WHERE date >= ?", (since,)):
        recent_albums.setdefault(k, set()).add(artist_key(alb)[:12])
    con.close()
    newest_batch = max(s["email_date"] for s in staged)

    rows = []
    for s in staged:
        k = artist_key(s["artist"])
        riyl_hits = [(r, a_score[artist_key(r)]) for r in s.get("riyl", []) if artist_key(r) in a_score]
        riyl = min(120, sum(v for _, v in riyl_hits))
        lab = 10 * math.log10(1 + l_spins.get(label_key(s.get("label", "")), 0))
        overlap = 15 if k in picks else 0
        n_recent = recent_shows.get(k, 0)
        rotation = 0
        if n_recent:
            rotation = 30 + min(25, 5 * n_recent)
            if artist_key(s["title"])[:12] in recent_albums.get(k, set()):
                rotation += 20  # you already aired a single from this release
        newness = 10 if s["email_date"] == newest_batch and s["type"] != "single" else 0
        fit = a_score.get(k, 0) + 0.6 * riyl + lab + overlap + rotation + newness
        is_added = (k[:10], artist_key(s["title"])[:10]) in added
        rows.append({
            "fit": round(fit, 1), "artist": s["artist"], "title": s["title"], "type": s["type"],
            "label": s.get("label", ""), "email_date": s["email_date"],
            "you_play_artist": a_name.get(k, ""),
            "riyl_matches": ", ".join(f"{a_name.get(artist_key(r), r)}" for r, _ in
                                      sorted(riyl_hits, key=lambda x: -x[1])[:5]),
            "riyl": ", ".join(s.get("riyl", [])),
            "label_spins": l_spins.get(label_key(s.get("label", "")), 0),
            "in_outside_picks": "yes" if overlap else "",
            "recent_shows": n_recent,
            "single_aired": "yes" if rotation >= 50 and artist_key(s["title"])[:12] in recent_albums.get(k, set()) else "",
            "status": "A-File add (already reviewed)" if is_added else "staged",
            "flags": s.get("flags", ""),
        })
    rows.sort(key=lambda r: -r["fit"])

    if args.library:
        key = os.getenv("KZSU_LIBRARY_API_KEY", "")
        headers = {"X-APIKEY": key, "Accept": "application/vnd.api+json"}
        for r in rows[:args.top]:
            if r["status"] == "staged" and r["type"] != "single":
                r["status"] = library_status(r["artist"], r["title"], headers)

    today = date.today().isoformat()
    out_dir = ROOT / "outputs" / "reviews"
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / f"staged_priority_{today}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def table(items):
        out = ["| # | Fit | Artist, title | Type | Label | Email | Why | Status |",
               "|---|---|---|---|---|---|---|---|"]
        for i, r in enumerate(items, 1):
            why = []
            if r["single_aired"]:
                why.append(f"**you've aired a single from it** ({r['recent_shows']} shows in 120 days)")
            elif r["recent_shows"]:
                why.append(f"**in rotation** ({r['recent_shows']} shows in 120 days)")
            if r["you_play_artist"]:
                why.append(f"you play {r['you_play_artist']}")
            if r["riyl_matches"]:
                why.append(f"RIYL {r['riyl_matches']}")
            if r["label_spins"]:
                why.append(f"label: {r['label_spins']} spins")
            if r["in_outside_picks"]:
                why.append("also in outside research")
            out.append(f"| {i} | {r['fit']} | {r['artist']}, *{r['title']}* | {r['type']} | {r['label']} "
                       f"| {r['email_date']} | {'; '.join(why)} | {r['status']}{' ' + r['flags'] if r['flags'] else ''} |")
        return out

    albums = [r for r in rows if r["type"] != "single" and r["fit"] > 0][:args.top]
    singles = [r for r in rows if r["type"] == "single" and r["fit"] > 0][:25]

    # ---- Review-template checklist -------------------------------------------
    # Stace ticks a box ("- [ ]" -> "- [x]") to ask for a review template.
    # The kzsu-review-template skill reads ticked boxes and appends
    # "| template: <path>" once the draft exists. Earlier lists may hold ticks
    # and finished templates, so carry that state forward into this week's list.
    from review_requests import parse_checklist, checklist_line, item_key
    carried = {}
    for old in sorted(out_dir.glob("staged_priority_*.md")):
        if old.name != f"staged_priority_{today}.md":
            for item in parse_checklist(old.read_text(encoding="utf-8")):
                if item["checked"]:
                    carried[item_key(item["artist"], item["title"])] = item
    checklist = []
    for r in albums:
        if str(r["status"]).startswith("A-File"):
            continue                     # already reviewed for the library
        prev = carried.pop(item_key(r["artist"], r["title"]), None)
        checklist.append(checklist_line(r["artist"], r["title"], r["label"],
                                        checked=bool(prev), template=(prev or {}).get("template", "")))
    # Ticked items that dropped out of the top list stay on it, so no request is lost.
    for prev in carried.values():
        checklist.append(checklist_line(prev["artist"], prev["title"], prev["label"],
                                        checked=True, template=prev.get("template", "")))

    md = [f"# Staged for review: priority list ({today})", "",
          f"From {len(staged)} releases in Mark Mollineaux's New Music Filtering emails "
          f"(latest: {max(s['email_date'] for s in staged)}), scored against `config/taste_profile.json`.",
          "Staged releases rank ahead of outside research picks. Claim them through the music department's form.", "",
          "## Make review templates", "",
          "Tick a box (change `[ ]` to `[x]`) to request a review template. Order matches the table below.",
          "Finished templates get a link after the last `|`.", ""] + checklist + \
         ["", f"## Albums and EPs (top {len(albums)})", ""] + table(albums) + \
         ["", "## Singles worth airing (top 25)", ""] + table(singles) + \
         ["", "Full scored list: `staged_priority_%s.csv`." % today, ""]
    (out_dir / f"staged_priority_{today}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {out_dir / f'staged_priority_{today}.md'}  ({len(albums)} albums, {len(singles)} singles)")
    for r in albums[:25]:
        print(f"{r['fit']:6.1f}  {r['artist']} - {r['title']} [{r['label']}] {r['email_date']}  {r['riyl_matches'][:70]}  {r['status']}")


if __name__ == "__main__":
    main()
