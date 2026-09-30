#!/usr/bin/env python3
"""
build_taste_profile.py
======================

Reads data/library_show.db (made by build_music_db.py) and writes a
machine-readable taste profile:

    config/taste_profile.json

Recon scripts use this file to score new releases ("does this fit DJ Stace?").
The human-readable version lives in TASTE_PROFILE.md.

HOW TO RUN:
    python scripts/build_music_db.py      # first, refresh the database
    python scripts/build_taste_profile.py

How the artist score works (beginner explanation)
-------------------------------------------------
Each artist gets points from three kinds of evidence:

* airplay      = number of distinct shows the artist was played on
                 (on-air choices are the strongest evidence of taste)
* recent_air   = shows in the last 12 months (weighted x2, taste changes)
* ytm          = YouTube Music plays, compressed with log() so that
                 1,600 Glenn Gould plays don't drown out everything else
* reviews      = albums you reviewed for the KZSU library
* playlists    = how often the artist shows up in your own YouTube Music
                 playlists (data/ytm/playlist_artist_counts.txt). Each
                 playlist has a weight in data/ytm/playlists.json, and track
                 counts are compressed with log2() so one 80-track artist
                 in All-Time Favorites doesn't swamp everything else.

score = 3*airplay + 6*recent_air + 4*log(1+ytm) + 5*reviews + 4*playlists
Then we scale so the top artist = 100. Weights are easy to change below.
"""
import json
import math
import re
import sqlite3
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "library_show.db"
OUT = ROOT / "config" / "taste_profile.json"
HISTORY = ROOT / "config" / "history"      # dated copies of older profiles

# ---- Tunable weights -------------------------------------------------------
W_AIRPLAY, W_RECENT_AIR, W_YTM, W_REVIEW = 3.0, 6.0, 4.0, 5.0
W_PLAYLIST = 4.0          # weight for the playlist-evidence term
PL_META = ROOT / "data" / "ytm" / "playlists.json"
PL_COUNTS = ROOT / "data" / "ytm" / "playlist_artist_counts.txt"
TODAY = date.today()
ONE_YEAR_AGO = (TODAY - timedelta(days=365)).isoformat()
NINETY_DAYS_AGO = (TODAY - timedelta(days=90)).isoformat()


def display_name(name: str) -> str:
    """Flip library-style names for display: 'Esso, Sylvan' -> 'Sylvan Esso'."""
    if name.count(",") == 1:
        last, first = [p.strip() for p in name.split(",")]
        if 0 < len(first.split()) <= 3 and "&" not in first and len(last.split()) <= 3:
            return f"{first} {last}"
    return name


def load_playlist_evidence():
    """Read the scraped playlist counts and return per-artist evidence.

    Returns (meta, evidence) where:
      meta     = {code: {"title", "weight", ...}} from playlists.json
      evidence = {artist_key: {"name": str, "raw": float, "in": {title: count}}}

    Beginner note: each line in the .txt file looks like
        Ty Segall:d1 f2 h12
    meaning 1 track in playlist "d", 2 in "f", 12 in "h".
    """
    # artist_key comes from the database builder so names match the DB
    # ("The Walkmen" and "Walkmen, The" both become "walkmen").
    from build_music_db import artist_key, primary_artist

    if not (PL_META.exists() and PL_COUNTS.exists()):
        return {}, {}
    meta = json.loads(PL_META.read_text())["playlists"]
    evidence = {}
    for line in PL_COUNTS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        # rsplit on the LAST colon: artist names can contain ":" ("Songs: Ohia").
        name, codes = line.rsplit(":", 1)
        name = name.replace(" + ", " & ").strip()    # undo the export's "&" -> "+"
        key = artist_key(primary_artist(name))
        if not key:
            continue
        e = evidence.setdefault(key, {"name": name, "raw": 0.0, "in": {}})
        for token in codes.split():
            # A token is letters + digits: "h12" or "aa3" (codes grow past "z").
            m = re.fullmatch(r"([a-z]+)(\d+)", token)
            if not m:
                continue
            code, count = m.group(1), int(m.group(2))
            p = meta.get(code)
            if not p:
                continue
            # log2(1 + count): 1 track = 1 point, 3 tracks = 2, 7 tracks = 3 ...
            e["raw"] += p["weight"] * math.log2(1 + count)
            e["in"][p["title"]] = e["in"].get(p["title"], 0) + count
    return meta, evidence


def main() -> None:
    # Read-only connection: we never change the database here.
    con = sqlite3.connect(f"file:{DB}?mode=ro&immutable=1", uri=True)
    q = lambda sql, *a: con.execute(sql, a).fetchall()

    # ---- 1. Artist evidence ------------------------------------------------
    # The most common spelling of each artist becomes the display name.
    names = {}
    for key, name, n in q("SELECT artist_key, artist, COUNT(*) FROM v_airplay GROUP BY artist_key, artist"):
        if key not in names or n > names[key][1]:
            names[key] = (name.strip(), n)
    for key, name, n in q("SELECT artist_key, artist, COUNT(*) FROM v_ytm_plays WHERE artist<>'' GROUP BY artist_key, artist"):
        names.setdefault(key, (name.strip(), n))

    air = {k: (s, f, l) for k, s, f, l in q(
        "SELECT artist_key, COUNT(DISTINCT playlist_id), MIN(date), MAX(date) FROM v_airplay GROUP BY artist_key")}
    recent_air = dict(q("SELECT artist_key, COUNT(DISTINCT playlist_id) FROM v_airplay WHERE date >= ? GROUP BY artist_key", ONE_YEAR_AGO))
    ytm = dict(q("SELECT artist_key, COUNT(*) FROM v_ytm_plays WHERE artist_key<>'' GROUP BY artist_key"))
    ytm_90 = dict(q("SELECT artist_key, COUNT(*) FROM v_ytm_plays WHERE artist_key<>'' AND played_at >= ? GROUP BY artist_key", NINETY_DAYS_AGO))
    reviews = dict(q("SELECT artist_key, COUNT(*) FROM kzsu_reviews GROUP BY artist_key"))
    pl_meta, pl = load_playlist_evidence()
    for key, e in pl.items():                 # playlist-only artists need a name too
        names.setdefault(key, (e["name"], 0))

    artists = []
    for key in set(air) | set(ytm) | set(reviews) | set(pl):
        if not key or key in {"kzsu", "unknown"}:
            continue
        shows, first, last = air.get(key, (0, None, None))
        pl_raw = pl.get(key, {}).get("raw", 0.0)
        raw = (W_AIRPLAY * shows + W_RECENT_AIR * recent_air.get(key, 0)
               + W_YTM * math.log1p(ytm.get(key, 0)) + W_REVIEW * reviews.get(key, 0)
               + W_PLAYLIST * pl_raw)
        artists.append({
            "artist": display_name(names.get(key, (key, 0))[0]), "key": key, "raw": raw,
            "shows": shows, "shows_12mo": recent_air.get(key, 0),
            "ytm_plays": ytm.get(key, 0), "ytm_plays_90d": ytm_90.get(key, 0),
            "reviews": reviews.get(key, 0), "first_spin": first, "last_spin": last,
            "playlist_score": round(pl_raw, 2),
            # {playlist title: number of tracks by this artist}
            "playlists": pl.get(key, {}).get("in", {}),
        })
    top = max(a["raw"] for a in artists)
    for a in artists:
        a["score"] = round(100 * a.pop("raw") / top, 1)
    artists.sort(key=lambda a: -a["score"])

    # ---- 2. Label affinity -------------------------------------------------
    label_rows = q("""SELECT label_key, label, COUNT(*), COUNT(DISTINCT artist_key), MAX(date)
                      FROM v_airplay WHERE label_key NOT IN ('', 'self', 'self release', 'unknown', 'none')
                      GROUP BY label_key, label""")
    labels = {}
    for key, name, spins, n_art, last in label_rows:
        d = labels.setdefault(key, {"label": name, "spins": 0, "artists": 0, "last": last, "_n": 0})
        d["spins"] += spins
        d["artists"] = max(d["artists"], n_art)
        d["last"] = max(d["last"], last)
        if spins > d["_n"]:
            d["label"], d["_n"] = name, spins
    label_list = sorted(labels.values(), key=lambda d: -d["spins"])[:80]
    for d in label_list:
        d.pop("_n")

    # ---- 3. RIYL graph from reviews (who you compare artists to) ----------
    riyl = Counter()
    for (text,) in q("SELECT riyl FROM kzsu_reviews WHERE riyl <> ''"):
        for part in re.split(r"[,;/]| and ", text):
            p = part.strip(" .*-()")
            if 2 < len(p) < 40 and p.lower() not in {"none", "n/a"}:
                riyl[p] += 1

    # ---- 4. Show format ----------------------------------------------------
    fmt = q("""SELECT AVG(n_spins) FROM kzsu_shows WHERE rebroadcast = 0 AND n_spins >= 15
               AND date >= ?""", ONE_YEAR_AGO)[0][0]

    profile = {
        "generated": TODAY.isoformat(),
        "weights": {"airplay": W_AIRPLAY, "recent_air": W_RECENT_AIR, "ytm_log": W_YTM,
                    "review": W_REVIEW, "playlist": W_PLAYLIST},
        # Which YouTube Music playlists fed the profile, and how much each counts.
        "playlists": {v["title"]: {"tracks": v["tracks"], "weight": v["weight"], "kind": v["kind"]}
                      for v in pl_meta.values()},
        # Strong in her playlists but never aired: candidates for the show.
        "playlist_not_aired": [
            {"artist": a["artist"], "playlist_score": a["playlist_score"], "playlists": a["playlists"]}
            for a in sorted(artists, key=lambda a: -a["playlist_score"])
            if a["shows"] == 0 and a["playlist_score"] >= 4][:60],
        "show_format": {"avg_spins_per_2hr_show_12mo": round(fmt or 0, 1)},
        "artists": artists[:600],
        "labels": label_list,
        "riyl_mentions": riyl.most_common(80),
    }
    OUT.parent.mkdir(exist_ok=True)
    # Keep the previous profile so scripts/taste_profile_changes.py can show
    # what moved. File name uses the OLD profile's "generated" date.
    if OUT.exists():
        try:
            old_date = json.loads(OUT.read_text()).get("generated", "unknown")
        except json.JSONDecodeError:
            old_date = "unknown"
        HISTORY.mkdir(parents=True, exist_ok=True)
        archive = HISTORY / f"taste_profile_{old_date}.json"
        if old_date != TODAY.isoformat() and not archive.exists():
            archive.write_text(OUT.read_text())
    OUT.write_text(json.dumps(profile, indent=1, ensure_ascii=False))
    print(f"Wrote {OUT} with {len(profile['artists'])} artists and {len(label_list)} labels")
    for a in artists[:25]:
        print(f"  {a['score']:5.1f}  {a['artist']:<35} shows={a['shows']:<3} 12mo={a['shows_12mo']:<3} ytm={a['ytm_plays']}")


if __name__ == "__main__":
    main()
