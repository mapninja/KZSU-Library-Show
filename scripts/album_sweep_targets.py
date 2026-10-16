#!/usr/bin/env python3
"""
album_sweep_targets.py
======================

Step 1 of the weekly ALBUM SWEEP (skills/kzsu-album-sweep/SKILL.md).

This script does NOT touch the web. It reads files already in the repo and
builds the list of "who and what to look up" for this week:

    data/album_sweep/targets_<date>.json

The browser step in the skill then checks label sites, Wikipedia and music
news for new or announced ALBUMS from these targets.

Three target buckets
--------------------
1. LABELS   Favorite labels from config/release_watchlist.json (tier 1 and 2).
2. PLAYLIST Artists on "Stace's Weekly Playlist" and "New Releases for
            Review" (read from the snapshots in data/daily/snapshots/).
3. LEAD     Lead singles Stace has aired lately. Detected from airplay in
            data/library_show.db: a spin where the album name equals the
            track name, has "(single)" in it, is blank, or matches a single
            listed in data/releases/upcoming_releases.csv.
            The parent album is what we want to find.

HOW TO RUN (from the repository root):

    python scripts/album_sweep_targets.py
    python scripts/album_sweep_targets.py --days 56 --date 2026-10-19

Beginner notes
--------------
* "Normalizing" a name means lowercasing it and stripping punctuation, so
  "Segall, Ty" and "Ty Segall." can be compared fairly.
* SQLite cannot open a database on some mounted folders, so we copy the
  database to a temporary folder first (same trick as build_release_watchlist.py).
"""

# ---------------------------------------------------------------------------
# Imports. All of these ship with Python.
# ---------------------------------------------------------------------------
import argparse      # read options typed on the command line
import csv           # read upcoming_releases.csv
import json          # read and write JSON files
import re            # pattern matching for name cleanup
import shutil        # copy the database file
import sqlite3       # the built-in database engine
import tempfile      # temporary folder for the database copy
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths. ROOT is the repository folder (one level above scripts/).
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "library_show.db"
WATCHLIST = ROOT / "config" / "release_watchlist.json"
PLAYLISTS = ROOT / "config" / "playlists.json"
SNAPSHOT_DIR = ROOT / "data" / "daily" / "snapshots"
UPCOMING = ROOT / "data" / "releases" / "upcoming_releases.csv"
OUT_DIR = ROOT / "data" / "album_sweep"

# Playlists whose artists count as "current interest". Keys match
# config/playlists.json. Order of the list does not matter.
PLAYLIST_KEYS = ["weekly", "new_releases_review"]

# Label tiers to sweep. Tier 1 = core labels, tier 2 = secondary labels.
LABEL_TIERS = (1, 2)


def norm(text):
    """Lowercase and strip punctuation so names compare fairly."""
    text = (text or "").lower()
    text = re.sub(r"\(.*?\)|\[.*?\]", " ", text)   # drop (Remastered), [Deluxe]
    text = re.sub(r"[^a-z0-9 ]+", " ", text)       # keep letters, digits, spaces
    return re.sub(r"\s+", " ", text).strip()


def flip_artist(name):
    """The DB stores some artists as 'Segall, Ty'. Turn that into 'Ty Segall'."""
    if name and name.count(",") == 1 and " & " not in name:
        last, first = [p.strip() for p in name.split(",")]
        return f"{first} {last}"
    return name


def load_labels(limit_tier=LABEL_TIERS):
    """Return favorite labels from the watchlist, tier 1 first, by spins."""
    data = json.loads(WATCHLIST.read_text())
    rows = []
    for key, info in data["labels"].items():
        if info.get("tier") in limit_tier:
            rows.append({
                "key": key,
                "label": info["label"],
                "tier": info["tier"],
                "spins": info.get("spins", 0),
                "recent_spins": info.get("recent_spins", 0),
                "top_artists": info.get("top_artists", [])[:6],
                "url": info.get("url", ""),
            })
    rows.sort(key=lambda r: (r["tier"], -r["recent_spins"], -r["spins"]))
    return rows


def load_playlist_artists():
    """Collect artist -> {tracks, playlists} from the two snapshots."""
    registry = json.loads(PLAYLISTS.read_text())["playlists"]
    found = {}
    for key in PLAYLIST_KEYS:
        info = registry.get(key, {})
        pid = info.get("id")
        snap = SNAPSHOT_DIR / f"{pid}.json"
        if not pid or not snap.exists():
            print(f"  note: no snapshot for {key} ({pid}); skipped")
            continue
        for track in json.loads(snap.read_text()).get("tracks", []):
            # Snapshot rows are [artist, title, videoId].
            artist, title = track[0], track[1]
            entry = found.setdefault(norm(artist), {
                "artist": artist, "tracks": [], "playlists": set()})
            entry["tracks"].append(title)
            entry["playlists"].add(info.get("title", key))
    out = []
    for entry in found.values():
        out.append({
            "artist": entry["artist"],
            "tracks": entry["tracks"][:4],
            "playlists": sorted(entry["playlists"]),
        })
    out.sort(key=lambda r: r["artist"].lower())
    return out


def load_known_singles():
    """Singles named in upcoming_releases.csv: {(artist, track): album_row}."""
    known = {}
    if not UPCOMING.exists():
        return known
    with UPCOMING.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("latest_single"):
                known[(norm(row["artist"]), norm(row["latest_single"]))] = row
    return known


def load_lead_singles(days, today):
    """Find recently aired tracks that look like singles ahead of an album."""
    since = (today - timedelta(days=days)).isoformat()
    known = load_known_singles()

    # Copy the DB to a temp folder, then query the copy.
    tmp = Path(tempfile.mkdtemp()) / "lib.db"
    shutil.copy(DB_PATH, tmp)
    con = sqlite3.connect(tmp)
    rows = con.execute(
        "SELECT date, artist, track, album, label FROM v_airplay "
        "WHERE date >= ? ORDER BY date", (since,)).fetchall()
    # Tracks aired BEFORE the window are not new singles (for example
    # "Transmission" by Joy Division), so remember them and skip them.
    older = {
        (norm(flip_artist(a)), norm(t))
        for a, t in con.execute(
            "SELECT artist, track FROM v_airplay WHERE date < ?", (since,))
    }
    con.close()

    leads = {}
    for day, artist, track, album, label in rows:
        artist = flip_artist(artist)
        t, a = norm(track), norm(album)
        if (norm(artist), t) in older:
            continue
        reasons = []
        if not a:
            reasons.append("blank album")
        if a and a == t:
            reasons.append("album name equals track name")
        if "single" in (album or "").lower():
            reasons.append("'single' in album name")
        if (norm(artist), t) in known:
            reasons.append("listed in upcoming_releases.csv")
        if not reasons:
            continue
        key = (norm(artist), t)
        item = leads.setdefault(key, {
            "artist": artist, "track": track, "aired": [],
            "label": label or "", "reasons": set()})
        item["aired"].append(day)
        item["reasons"].update(reasons)
        if key in known:
            item["known_album"] = known[key]["title"]
            item["known_status"] = known[key]["status"]
    out = []
    for item in leads.values():
        item["reasons"] = sorted(item["reasons"])
        item["times_aired"] = len(item["aired"])
        item["last_aired"] = max(item["aired"])
        out.append(item)
    out.sort(key=lambda r: (r["last_aired"], r["times_aired"]), reverse=True)
    return out


def main():
    ap = argparse.ArgumentParser(description="Build album sweep targets.")
    ap.add_argument("--days", type=int, default=56,
                    help="how far back to look for aired lead singles")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="run date (YYYY-MM-DD)")
    args = ap.parse_args()
    today = date.fromisoformat(args.date)

    print("Reading labels, playlists and airplay...")
    targets = {
        "generated": today.isoformat(),
        # Window the browser step should cover: albums out in the last 14 days
        # and albums announced or due in the next 60 days.
        "window": {
            "released_since": (today - timedelta(days=14)).isoformat(),
            "upcoming_until": (today + timedelta(days=60)).isoformat(),
        },
        "labels": load_labels(),
        "playlist_artists": load_playlist_artists(),
        "lead_singles": load_lead_singles(args.days, today),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"targets_{today.isoformat()}.json"
    out.write_text(json.dumps(targets, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {out.relative_to(ROOT)}")
    print(f"  labels: {len(targets['labels'])}")
    print(f"  playlist artists: {len(targets['playlist_artists'])}")
    print(f"  lead singles aired: {len(targets['lead_singles'])}")


if __name__ == "__main__":
    main()
