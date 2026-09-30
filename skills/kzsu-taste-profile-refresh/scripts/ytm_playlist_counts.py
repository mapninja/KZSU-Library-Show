#!/usr/bin/env python3
"""
ytm_playlist_counts.py
======================

Counts how many tracks each artist has in each of DJ Stace's YouTube Music
playlists, and writes the two files that build_taste_profile.py reads:

    data/ytm/playlists.json              which playlists count, and how much
    data/ytm/playlist_artist_counts.txt  one line per artist: "Name:h12 p3"

TWO WAYS TO GET THE PLAYLISTS
-----------------------------
1. ytmusicapi (preferred, needs a signed-in browser.json):
       pip install ytmusicapi
       python3 scripts/ytm_playlist_counts.py

2. A browser scrape you already saved as JSON (fallback, no login file):
       python3 scripts/ytm_playlist_counts.py --from-dump data/ytm/playlist_dump.json
   The dump format is {playlistId: {"title": str, "data": [[title, artist, album, videoId], ...]}}.
   See the skill's references/browser_scrape.md for how to make it.

Add --dry-run to print the summary without writing files.

WEIGHTS (beginner explanation)
------------------------------
Each playlist gets a weight: how much one track in it says about Stace's taste.
Existing weights in playlists.json are kept, so if Stace changes a weight by
hand, the next run respects it. New playlists get a guessed weight and are
marked "new": true so the agent can ask her to confirm.
"""
import argparse
import json
import os
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "data" / "ytm" / "playlists.json"
COUNTS = ROOT / "data" / "ytm" / "playlist_artist_counts.txt"

# Playlists that are NOT music taste. Matched case-insensitively against titles.
# - spoken word and podcasts (Stace asked to leave these out)
# - playlists the assistant builds itself, so the profile doesn't learn from its own picks
EXCLUDE_PATTERNS = [
    r"episode",                 # "New Episodes", "Episodes for Later"
    r"god is not great",        # Hitchens audiobook
    r"audiobook", r"podcast",
    r"library show air order", r"library show working", r"stace's daily playlist",
]

# Guessed weights for playlists we haven't seen before. First match wins.
DEFAULT_WEIGHTS = [
    (r"dj stace|next show|library show", 3.0, "show"),
    (r"top 25|top tracks|recap", 2.0, "recap"),
    (r"to review", 2.0, "review"),
    (r"fcc", 1.5, "show"),
    (r"soundbed|karaoke|hallowe|christmas|holiday", 0.3, "utility"),
]


def excluded(title: str) -> bool:
    """True if a playlist title matches any exclusion pattern."""
    t = title.lower()
    return any(re.search(p, t) for p in EXCLUDE_PATTERNS)


def guess_weight(title: str):
    """Return (weight, kind) for a playlist we have no saved weight for."""
    t = title.lower()
    for pattern, weight, kind in DEFAULT_WEIGHTS:
        if re.search(pattern, t):
            return weight, kind
    return 1.0, "general"


def next_code(used: set) -> str:
    """Short codes: a..z, then aa..zz. Codes stay fixed per playlist ID."""
    letters = "abcdefghijklmnopqrstuvwxyz"
    for c in list(letters) + [x + y for x in letters for y in letters]:
        if c not in used:
            return c
    raise RuntimeError("out of playlist codes")


def load_env() -> None:
    """Read KEY=value lines from .env so YTMUSIC_AUTH_PATH can live there."""
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def fetch_with_ytmusicapi() -> dict:
    """Download every library playlist plus Liked Music.

    Returns {playlistId: {"title": str, "artists": [artist name per track]}}.
    """
    from ytmusicapi import YTMusic          # imported here so --from-dump needs no install
    load_env()
    auth = os.getenv("YTMUSIC_AUTH_PATH", str(ROOT / "browser.json"))
    ytm = YTMusic(auth)

    out = {}
    for p in ytm.get_library_playlists(limit=None):
        pid, title = p.get("playlistId"), p.get("title", "")
        if not pid or excluded(title):
            continue
        # limit=None pages through the whole playlist, however long.
        tracks = ytm.get_playlist(pid, limit=None).get("tracks", [])
        out[pid] = {"title": title, "artists": [first_artist(t) for t in tracks]}
        print(f"  {title}: {len(tracks)} tracks")
    # Liked Music ("LM") is not always in the library list.
    if "LM" not in out:
        liked = ytm.get_liked_songs(limit=None).get("tracks", [])
        out["LM"] = {"title": "Liked Music", "artists": [first_artist(t) for t in liked]}
        print(f"  Liked Music: {len(liked)} tracks")
    return out


def first_artist(track: dict) -> str:
    """ytmusicapi gives a list of artists per track. Join them the way the
    YTM web page shows them, so both input paths produce the same names."""
    names = [a.get("name", "") for a in (track.get("artists") or []) if a.get("name")]
    if not names:
        return ""
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " & " + names[-1]


def load_dump(path: Path) -> dict:
    """Read a browser-scrape dump and reshape it like fetch_with_ytmusicapi()."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for pid, o in raw.items():
        title = o.get("title", pid).replace(" - YouTube Music", "").strip()
        if excluded(title):
            continue
        out[pid] = {"title": title, "artists": [row[1] for row in o.get("data", []) if len(row) > 1]}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Count artists per YouTube Music playlist")
    ap.add_argument("--from-dump", type=Path, help="browser-scrape JSON instead of ytmusicapi")
    ap.add_argument("--dry-run", action="store_true", help="print only, write nothing")
    args = ap.parse_args()

    playlists = load_dump(args.from_dump) if args.from_dump else fetch_with_ytmusicapi()

    # Keep existing codes and weights so hand edits survive.
    old = json.loads(META.read_text()) if META.exists() else {"playlists": {}}
    by_id = {v["id"]: (code, v) for code, v in old["playlists"].items()}
    used = set(old["playlists"])

    meta, new_titles = {}, []
    counts = defaultdict(lambda: defaultdict(int))   # artist -> code -> tracks
    for pid, p in playlists.items():
        if pid in by_id:
            code, saved = by_id[pid]
            entry = dict(saved, title=p["title"], tracks=len(p["artists"]))
            entry.pop("new", None)
        else:
            code = next_code(used)
            used.add(code)
            weight, kind = guess_weight(p["title"])
            entry = {"title": p["title"], "id": pid, "tracks": len(p["artists"]),
                     "weight": weight, "kind": kind, "new": True}
            new_titles.append(f"{p['title']} (weight {weight}, {kind})")
        meta[code] = entry
        for artist in p["artists"]:
            # Drop "feat." credits so "A feat. B" counts as A.
            a = re.sub(r"\s+(feat\.|ft\.).*$", "", artist or "", flags=re.I)
            a = re.sub(r"\s+", " ", a).strip()
            if a:
                counts[a][code] += 1

    gone = [v["title"] for v in old["playlists"].values() if v["id"] not in playlists]

    print(f"{len(meta)} playlists, {sum(v['tracks'] for v in meta.values())} tracks, {len(counts)} artists")
    if new_titles:
        print("NEW playlists (confirm weights with Stace):", "; ".join(new_titles))
    if gone:
        print("No longer found (deleted, renamed or now excluded):", "; ".join(gone))
    if args.dry_run:
        return

    META.parent.mkdir(parents=True, exist_ok=True)
    META.write_text(json.dumps({
        "scraped": date.today().isoformat(),
        "note": old.get("note", "DJ Stace's YouTube Music playlists used as taste evidence."),
        "playlists": dict(sorted(meta.items(), key=lambda kv: (len(kv[0]), kv[0]))),
        "excluded_patterns": EXCLUDE_PATTERNS,
    }, indent=1, ensure_ascii=False))

    # Artists sorted by how many playlists they appear in, then total tracks.
    rows = sorted(counts.items(), key=lambda kv: (-len(kv[1]), -sum(kv[1].values()), kv[0]))
    lines = [f"# Artist counts per YouTube Music playlist, {date.today().isoformat()}.",
             "# Format: artist:<code><count> ...  Codes are defined in data/ytm/playlists.json."]
    for artist, per in rows:
        # The reader splits on the LAST ":", so names like "Songs: Ohia" are safe.
        lines.append(artist + ":" + " ".join(f"{c}{n}" for c, n in sorted(per.items())))
    COUNTS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {META} and {COUNTS}")


if __name__ == "__main__":
    main()
