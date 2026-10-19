#!/usr/bin/env python3
"""
staged_crossref.py
==================

Ranks the albums the KZSU music department has STAGED for review (from Mark's
"New Music Filtering" emails) against DJ Stace's taste profile, and checks
them against the A-File adds and the Zookeeper library.

INPUTS (every source below feeds ONE merged list; each row shows its sources)
    data/staged/filtering_albums.json   Mark Mollineaux emails + Music Dept promo list
    data/staged/afile_adds.json         "KZSU Music: Adds" (already reviewed)
    data/staged/review_shelf.csv        Review Shelf: Tue/Fri sweeps, album sweep, NACC chart, your requests
    data/releases/upcoming_releases.csv label feeds, Wikipedia, Stereogum, Bandcamp, Pitchfork, indieisnotagenre, etc.
    data/album_sweep/findings_*.json    Monday album sweep (labels, playlist artists, lead singles)
    data/daily/snapshots/*.json         Weekly Playlist + New Releases for Review contents
    data/daily/feedback.json            tracks you added (keep) or deleted (cool-off)
    data/staged/release_dates.json      CHECKED release dates (wins over every other date source)
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
    python scripts/staged_crossref.py --sync-shelf  # also copy checked dates into review_shelf.csv

Release dates
-------------
Every row in the output has a release date and a date check:
    confirmed = in data/staged/release_dates.json with 2+ sources, or day-precision in two feeds
    verify    = one source only (treat as unconfirmed)
    needed    = no date found. These are listed in data/staged/release_dates_needed.json
                so the weekly run can look them up and add them to release_dates.json.

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

    playlist_bonus = +15 if you added the artist to a show playlist (kept = positive),
                    +8 if the artist is on Stace's Weekly Playlist or New Releases for Review,
                    -25 if you deleted the artist's track and it is still in the 60-day cool-off
    staged_bonus  = +15 if the release came through Mark or the Music Dept (you can claim it)

fit = artist_match + 0.6 * riyl_match (capped at 120) + label_match
      + overlap_bonus + rotation_bonus + newness + playlist_bonus + staged_bonus
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


# ---------------------------------------------------------------------------
# Merged pool: every source feeds one list
# ---------------------------------------------------------------------------
from review_requests import item_key  # same loose artist|title key used by the checklist

TODAY = date.today().isoformat()
SCAN_SOURCES = {Path(f).stem.split("_")[0] for f in glob.glob(str(ROOT / "data/releases/source_scans/*.psv"))}


def clean_date(raw: str):
    """Turn '2026-10-02 (verify)', '2026-10' or '2026' into (iso text, precision, verify flag)."""
    raw = (raw or "").strip()
    verify = "verify" in raw.lower()
    m = re.search(r"\d{4}(-\d{2})?(-\d{2})?", raw)
    if not m:
        return "", "", verify
    txt = m.group(0)
    precision = {4: "year", 7: "month", 10: "day"}[len(txt)]
    return txt, precision, verify


def source_from_status(status: str) -> str:
    """Map the free-text Status on a Review Shelf row to a short source name."""
    st = status or ""
    if st.startswith("Album sweep") or st.startswith("Out Oct"):
        return "Album sweep (labels, playlists, lead singles)"
    if "sweep" in st:
        return "Tue/Fri new-release sweep"
    if st.startswith("NACC"):
        return "NACC college chart"
    if st.startswith("requested by Stace"):
        return "Your request"
    if st.startswith("promo"):
        return "Music Dept promo list"
    if st.startswith("A-File"):
        return "A-File adds"
    if st.startswith("staged"):
        return ""  # already counted as a Mark email
    return "Review Shelf"


def host_of(url: str) -> str:
    m = re.match(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1) if m else ""


def load_release_dates() -> dict:
    """Checked dates written by the weekly run: {item_key: {date, precision, sources[], note}}."""
    f = ROOT / "data/staged/release_dates.json"
    return load_json(f) if f.exists() else {}


def playlist_signals() -> dict:
    """What your playlists say about each artist.

    Returns {artist_key: {"weekly": bool, "review": bool, "added": bool, "cooloff": 'YYYY-MM-DD' or ''}}
    - weekly / review: artist has a track on Stace's Weekly Playlist or New Releases for Review
    - added: you added one of their tracks to a show playlist (positive signal, keep)
    - cooloff: you deleted a track and the 60-day cool-off has not ended
    """
    sig = {}
    snap_dir = ROOT / "data/daily/snapshots"
    names = {"PLCLF-Tik2UHk": "weekly", "PLIl7VQi0nzk0": "review"}
    for pid, flag in names.items():
        f = snap_dir / f"{pid}.json"
        if f.exists():
            for t in load_json(f).get("tracks", []):
                sig.setdefault(artist_key(t[0]), {})[flag] = True
    fb_file = ROOT / "data/daily/feedback.json"
    if fb_file.exists():
        fb = load_json(fb_file)
        for a in fb.get("added_by_stace", []):
            sig.setdefault(artist_key(a.get("artist", "")), {})["added"] = True
        for r in fb.get("removed", []):
            until = r.get("cooloff_until", "")
            if until >= TODAY:
                d = sig.setdefault(artist_key(r.get("artist", "")), {})
                d["cooloff"] = max(until, d.get("cooloff", ""))
    return sig


def scan_status_line() -> str:
    """One line per outside source scan, read from data/releases/source_scans/status.json."""
    f = ROOT / "data/releases/source_scans/status.json"
    if not f.exists():
        return "no scan status recorded."
    st = load_json(f)
    return "; ".join(f"{k} {v['status']} ({v['last_scan']})" for k, v in st.items() if not k.startswith("_")) + "."


def build_pool(staged: list) -> list:
    """Merge every source into one list of releases, one row per artist + title.

    Each entry keeps a set of source names, the best release date found, and
    whether Mark or the Music Dept sent it (staged = you can claim it).
    """
    pool = {}

    def add(artist, title, typ, label, source, date_raw="", date_src="", riyl=None,
            email_date="", flags="", staged=False):
        if not artist or not title:
            return
        k = item_key(artist, title)
        e = pool.setdefault(k, {"artist": artist, "title": title, "type": typ or "album", "label": label or "",
                                "sources": [], "dates": [], "riyl": [], "email_date": "", "flags": "",
                                "staged": False})
        if source and source not in e["sources"]:
            e["sources"].append(source)
        if label and not e["label"]:
            e["label"] = label
        if typ and e["type"] in ("", "album") and typ != "album":
            e["type"] = typ
        if riyl and not e["riyl"]:
            e["riyl"] = list(riyl)
        if email_date and not e["email_date"]:
            e["email_date"] = email_date
        if flags and not e["flags"]:
            e["flags"] = flags
        e["staged"] = e["staged"] or staged
        d, prec, verify = clean_date(date_raw)
        if d:
            e["dates"].append({"date": d, "precision": prec, "verify": verify, "src": date_src})

    # 1. Mark's emails and the Music Dept promo list (staged = claimable)
    for s in staged:
        src = "Music Dept promo list" if s.get("source") == "md_list_promo" else "Mark Mollineaux email"
        add(s["artist"], s["title"], s.get("type", "album"), s.get("label", ""), src,
            riyl=s.get("riyl", []), email_date=s["email_date"], flags=s.get("flags", ""), staged=True)

    # 2. Review Shelf rows (sweeps, NACC, your requests). Dates here are often one source: "(verify)"
    shelf_f = ROOT / "data/staged/review_shelf.csv"
    if shelf_f.exists():
        with shelf_f.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                add(r["Artist"], r["Album"], r.get("Type", "album"), r.get("Label", ""),
                    source_from_status(r.get("Status", "")), date_raw=r.get("Release date", ""),
                    date_src="Review Shelf")

    # 3. Label feeds, Wikipedia lists, Stereogum, Bandcamp, Pitchfork, indieisnotagenre (research DB)
    up_f = ROOT / "data/releases/upcoming_releases.csv"
    if up_f.exists():
        with up_f.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                via = (r.get("found_via", "") or "").split(":")[0]
                host = host_of(r.get("source_url", "")) or r.get("source_name", "")
                name = {"label": f"Label feed ({host})", "aggregator": f"Release news ({r.get('source_name') or host})",
                        "artist": f"Artist watch ({host})"}.get(via, host or "Release DB")
                add(r["artist"], r["title"], r.get("type", "album"), r.get("label", ""), name,
                    date_raw=r.get("release_date", ""), date_src=host)

    # 4. Monday album sweep findings
    for f in sorted(glob.glob(str(ROOT / "data/album_sweep/findings_*.json"))):
        for r in load_json(f):
            add(r["artist"], r["album"], "album", r.get("label", ""),
                f"Album sweep ({r.get('bucket', 'sweep')})", date_raw=r.get("release_date", ""),
                date_src=host_of(r.get("source_url", "")))

    # 4b. Weekly outside-source scans (indieisnotagenre and others): data/releases/source_scans/<source>_<date>.psv
    #     Each line is date|ARTIST|Title|Label. The file name before the first "_" names the source.
    for f in sorted(glob.glob(str(ROOT / "data/releases/source_scans/*.psv"))):
        src_name = Path(f).stem.split("_")[0]
        for line in Path(f).read_text(encoding="utf-8").splitlines():
            parts = (line.split("|") + ["", "", "", ""])[:4]
            d, art, title, lab = parts
            if art and title:
                add(art.title() if art.isupper() else art, title, "album", lab.strip(), f"Scan: {src_name}",
                    date_raw=d, date_src=f"{src_name}.com")

    # 5. Checked dates win over everything else
    checked = load_release_dates()
    for k, e in pool.items():
        c = checked.get(k)
        if c:
            e["checked"] = c
            if c.get("label"):
                e["label"] = c["label"]  # researcher found a clearer label than the feed
    return list(pool.values())


def resolve_date(e: dict):
    """Pick the best release date for a pool entry. Returns (date, precision, check, note)."""
    c = e.get("checked")
    if c and c.get("date"):
        # "confirmed" is set by the researcher (2+ agreeing sources, day precision, no doubts in the note)
        n = len(c.get("sources", []))
        ok = c["confirmed"] if "confirmed" in c else n >= 2
        # A weekly scan (indieisnotagenre, etc.) that shows the same day counts as a second source.
        if not ok and c.get("precision", "day") == "day" and \
                any(d["date"] == c["date"] and d["src"].endswith(".com") and d["src"].split(".")[0] in SCAN_SOURCES
                    for d in e["dates"]):
            ok = True
        return c["date"], c.get("precision", "day"), ("confirmed" if ok else "verify"), c.get("note", "")
    dates = [d for d in e["dates"] if d["precision"] == "day"] or e["dates"]
    if not dates:
        return "", "", "needed", ""
    best = sorted(dates, key=lambda d: ({"day": 0, "month": 1, "year": 2}[d["precision"]], d["verify"]))[0]
    agree = {d["date"] for d in dates if d["precision"] == "day"}
    sources = {d["src"] for d in dates if d["date"] == best["date"]}
    if best["precision"] == "day" and not best["verify"] and (len(sources) >= 2):
        check = "confirmed"
    elif best["precision"] == "day":
        check = "verify"
    else:
        check = "verify"  # month or year only
    note = "sources disagree" if len(agree) > 1 else ""
    return best["date"], best["precision"], check, note


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
    ap.add_argument("--outside", type=int, default=25,
                    help="how many outside-pick albums to list after the staged ones")
    ap.add_argument("--backfill", type=int, default=25,
                    help="also queue this many of the best-ranked UNLISTED releases that have no release date")
    ap.add_argument("--sync-shelf", action="store_true",
                    help="write checked release dates back into data/staged/review_shelf.csv")
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

    pool = build_pool(staged)          # every source merged, one entry per artist + title
    signals = playlist_signals()       # Weekly / Review playlist, your adds, cool-offs
    rows = []
    for s in pool:
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
        # Playlist activity: adds are positive, a live cool-off pushes the release down.
        sg = signals.get(k, {})
        playlist_bonus = (15 if sg.get("added") else 0) + (8 if (sg.get("weekly") or sg.get("review")) else 0) \
            - (25 if sg.get("cooloff") else 0)
        staged_bonus = 15 if s["staged"] else 0
        fit = a_score.get(k, 0) + 0.6 * riyl + lab + overlap + rotation + newness + playlist_bonus + staged_bonus
        is_added = (k[:10], artist_key(s["title"])[:10]) in added
        rel_date, rel_prec, date_check, date_note = resolve_date(s)
        playlist_notes = []
        if sg.get("added"):
            playlist_notes.append("you added a track")
        if sg.get("weekly"):
            playlist_notes.append("on Weekly Playlist")
        if sg.get("review"):
            playlist_notes.append("on Review playlist")
        if sg.get("cooloff"):
            playlist_notes.append(f"cool-off until {sg['cooloff']}")
        rows.append({
            "fit": round(fit, 1), "artist": s["artist"], "title": s["title"], "type": s["type"],
            "label": s.get("label", ""), "release_date": rel_date, "date_check": date_check,
            "date_note": date_note, "email_date": s["email_date"],
            "sources": "; ".join(s["sources"]), "playlist_activity": "; ".join(playlist_notes),
            "you_play_artist": a_name.get(k, ""),
            "riyl_matches": ", ".join(f"{a_name.get(artist_key(r), r)}" for r, _ in
                                      sorted(riyl_hits, key=lambda x: -x[1])[:5]),
            "riyl": ", ".join(s.get("riyl", [])),
            "label_spins": l_spins.get(label_key(s.get("label", "")), 0),
            "in_outside_picks": "yes" if overlap else "",
            "recent_shows": n_recent,
            "single_aired": "yes" if rotation >= 50 and artist_key(s["title"])[:12] in recent_albums.get(k, set()) else "",
            "status": "A-File add (already reviewed)" if is_added else ("staged" if s["staged"] else "outside pick"),
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
        out = ["| # | Fit | Artist, title | Type | Label | Release date | Why | Sources | Status |",
               "|---|---|---|---|---|---|---|---|---|"]
        for i, r in enumerate(items, 1):
            why = []
            if r["single_aired"]:
                why.append(f"**you've aired a single from it** ({r['recent_shows']} shows in 120 days)")
            elif r["recent_shows"]:
                why.append(f"**in rotation** ({r['recent_shows']} shows in 120 days)")
            if r["playlist_activity"]:
                why.append(r["playlist_activity"])
            if r["you_play_artist"]:
                why.append(f"you play {r['you_play_artist']}")
            if r["riyl_matches"]:
                why.append(f"RIYL {r['riyl_matches']}")
            if r["label_spins"]:
                why.append(f"label: {r['label_spins']} spins")
            if r["in_outside_picks"]:
                why.append("also in outside research")
            # Date cell: the date, plus a mark when it is not confirmed by two sources.
            dcell = r["release_date"] or "NEEDED"
            if r["date_check"] == "verify":
                dcell += " (verify)"
            if "disagree" in r["date_note"].lower() or "reissue" in r["date_note"].lower():
                dcell += " (see CSV note)"
            out.append(f"| {i} | {r['fit']} | {r['artist']}, *{r['title']}* | {r['type']} | {r['label']} "
                       f"| {dcell} | {'; '.join(why)} | {r['sources']} "
                       f"| {r['status']}{' ' + r['flags'] if r['flags'] else ''} |")
        return out

    # Staged releases (Mark, Music Dept) keep their own ranking ahead of outside picks.
    # "Outside" = everything that came only from the other sources (label feeds, sweeps, NACC, requests).
    def pick(kind_is_single, staged_only, n):
        out = [r for r in rows if r["fit"] > 0 and (r["type"] == "single") == kind_is_single
               and (r["status"] != "outside pick") == staged_only]
        return out[:n]

    staged_albums = pick(False, True, args.top)
    outside_albums = pick(False, False, args.outside)
    albums = staged_albums + outside_albums
    staged_singles = pick(True, True, 25)
    outside_singles = pick(True, False, 10)
    singles = staged_singles + outside_singles

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
          f"Merged from {len(rows)} releases across all sources: Mark Mollineaux's New Music Filtering emails "
          f"({len(staged)} items, latest {max(s['email_date'] for s in staged)}), the Music Dept promo list, "
          "label feeds, Wikipedia lists, Stereogum and other release news, Bandcamp artist and label pages, "
          "the indieisnotagenre list, the Review Shelf sweeps, the NACC chart and your Weekly and Review playlist activity. "
          "Scored against `config/taste_profile.json`.",
          "Staged releases (Mark and Music Dept) get a bonus. Claim them through the music department's form. "
          "Release date shows (verify) when only one source has it and NEEDED when none does.", "",
          "Source scans: " + scan_status_line(), "",
          "## Make review templates", "",
          "Tick a box (change `[ ]` to `[x]`) to request a review template. Order matches the table below.",
          "Finished templates get a link after the last `|`.", ""] + checklist + \
         ["", f"## Staged albums and EPs (top {len(staged_albums)})", ""] + table(staged_albums) + \
         ["", f"## Outside picks: albums and EPs from other sources (top {len(outside_albums)})", ""] + table(outside_albums) + \
         ["", f"## Staged singles worth airing (top {len(staged_singles)})", ""] + table(staged_singles) + \
         ["", f"## Outside singles worth airing (top {len(outside_singles)})", ""] + table(outside_singles) + \
         ["", "Full scored list: `staged_priority_%s.csv`." % today, ""]
    (out_dir / f"staged_priority_{today}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {out_dir / f'staged_priority_{today}.md'}  ({len(albums)} albums, {len(singles)} singles)")

    # ---- Dates to look up -------------------------------------------------------
    # Any listed release whose date is missing or single-source goes in this file.
    # The weekly run researches them and records the answer in data/staged/release_dates.json.
    listed = albums + singles
    needed = [{"artist": r["artist"], "title": r["title"], "type": r["type"], "label": r["label"],
               "current_date": r["release_date"], "date_check": r["date_check"], "key": item_key(r["artist"], r["title"])}
              for r in listed if r["date_check"] != "confirmed"]
    # Backfill: the highest-ranked releases that are not on the lists above and still have no date.
    # Working through these every run slowly gives the whole pool a date.
    listed_keys = {item_key(r["artist"], r["title"]) for r in listed}
    backfill = [{"artist": r["artist"], "title": r["title"], "type": r["type"], "label": r["label"],
                 "current_date": r["release_date"], "date_check": r["date_check"],
                 "key": item_key(r["artist"], r["title"])}
                for r in rows if r["fit"] > 0 and not r["release_date"]
                and item_key(r["artist"], r["title"]) not in listed_keys][:args.backfill]
    needed += backfill
    (ROOT / "data/staged/release_dates_needed.json").write_text(json.dumps(needed, indent=1, ensure_ascii=False),
                                                                encoding="utf-8")
    n_conf = sum(1 for r in listed if r["date_check"] == "confirmed")
    undated = sum(1 for r in rows if not r["release_date"])
    print(f"Release dates on the lists: {n_conf} confirmed, {len(listed) - n_conf} verify, "
          f"{sum(1 for r in listed if not r['release_date'])} missing. Queue for lookup: {len(needed)} "
          f"({len(backfill)} backfill). Undated in the full pool: {undated} "
          f"(data/staged/release_dates_needed.json)")

    # ---- Optional: write checked dates back to the Review Shelf ----------------------
    if args.sync_shelf:
        checked = load_release_dates()
        shelf_f = ROOT / "data/staged/review_shelf.csv"
        with shelf_f.open(encoding="utf-8", newline="") as f:
            rdr = csv.DictReader(f)
            cols = rdr.fieldnames
            shelf = list(rdr)
        changed = 0
        for row in shelf:
            c = checked.get(item_key(row["Artist"], row["Album"]))
            if c and c.get("date"):
                txt = c["date"] if c.get("confirmed") else c["date"] + " (verify)"
                # Keep hand-written reissue notes such as "2026-09-04 (reissue; orig. 2023)".
                if "reissue" in row["Release date"].lower() and row["Release date"].startswith(c["date"]):
                    continue
                if row["Release date"] != txt:
                    row["Release date"] = txt
                    changed += 1
        with shelf_f.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_MINIMAL)
            w.writeheader()
            w.writerows(shelf)
        print(f"Review Shelf: {changed} release dates updated")

    for r in albums[:25]:
        print(f"{r['fit']:6.1f}  {r['artist']} - {r['title']} [{r['label']}] {r['release_date'] or 'NEEDED'} "
              f"({r['date_check']})  {r['status']}  | {r['sources'][:60]}")


if __name__ == "__main__":
    main()
