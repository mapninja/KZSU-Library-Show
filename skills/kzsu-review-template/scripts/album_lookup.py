#!/usr/bin/env python3
"""
album_lookup.py
===============

Starts (or fills in) a review research file for one album by asking free
music APIs for the objective facts: tracklist, runtimes, BPM, explicit flags,
label, release date, format and credits.

    outputs/reviews/research/<artist>-<album>.json

Sources, in order (each one only fills blanks the earlier ones left):
  1. KZSU Zookeeper   the station library record, when you pass --tag
                      (needs KZSU_LIBRARY_API_KEY in .env)
  2. Deezer API       tracklist, durations, BPM, explicit flag, label, date (no key)
  3. MusicBrainz API  tracklist and label when Deezer has nothing (no key)
  4. Discogs API      format and credits: producer, studio, players
                      (needs DISCOGS_TOKEN in .env)

It never overwrites something already in the research file, so hand-checked
facts win. Press quotes, release notes and RIYL are added by the agent, not here.

USAGE (from the repo root):
    python3 scripts/album_lookup.py --artist "Widowspeak" --album "Roses"
    python3 scripts/album_lookup.py --artist "Widowspeak" --album "Roses" --tag 1123456
    python3 scripts/album_lookup.py --artist "Widowspeak" --album "Roses" --dry-run

Beginner notes
--------------
* BPM means beats per minute. Deezer reports it per track, but sometimes as 0
  (unknown), and sometimes doubled or halved. pace_label() turns it into the
  words DJ Stace uses ("Midtempo"), and the review template shows the number
  so she can sanity-check it.
* APIs return JSON: nested dictionaries and lists. dict.get("key", default)
  reads a value without crashing when the key is missing.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "outputs" / "reviews" / "research"
UA = "KZSU-LibraryShow/1.0 (DJ Stace review prep; maples@stanford.edu)"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fcc_lyrics_check import norm, similar, artist_ok, load_env  # shared helpers


def get(url, headers=None):
    """GET a URL and parse JSON. Returns None on any error (and says why)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"  request failed: {url.split('?')[0]} ({type(e).__name__})", file=sys.stderr)
        return None


def mmss(seconds) -> str:
    """215 -> '3:35'"""
    try:
        s = int(round(float(seconds)))
        return f"{s // 60}:{s % 60:02d}"
    except (TypeError, ValueError):
        return ""


def pace_label(bpm) -> str:
    """BPM -> DJ Stace's pace words. Thresholds live in the skill's style guide."""
    try:
        b = float(bpm)
    except (TypeError, ValueError):
        return ""
    if b <= 0:
        return ""
    for limit, word in ((75, "Slow"), (95, "Slow to midtempo"), (115, "Midtempo"),
                        (130, "Mid to uptempo"), (155, "Uptempo")):
        if b < limit:
            return word
    return "Fast"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ---- 1. Zookeeper ------------------------------------------------------------
def from_zookeeper(tag: str) -> dict:
    key = os.getenv("KZSU_LIBRARY_API_KEY", "")
    data = get(f"https://zookeeper.stanford.edu/api/v1/album/{tag}",
               {"X-APIKEY": key, "Accept": "application/vnd.api+json"})
    if not data:
        return {}
    alb = data["data"]
    at = alb.get("attributes", {})
    return {
        "zookeeper_tag": str(tag),
        "label": alb.get("relationships", {}).get("label", {}).get("meta", {}).get("name", ""),
        "format": at.get("medium", ""),
        "tracks": [{"num": t.get("seq"), "title": t.get("track"), "runtime": t.get("duration") or ""}
                   for t in at.get("tracks", [])],
        "sources": [f"https://zookeeper.stanford.edu/?s=byAlbumKey&n={tag}&action=search"],
    }


# ---- 2. Deezer ---------------------------------------------------------------
def from_deezer(artist: str, album: str) -> dict:
    q = urllib.parse.quote(f'artist:"{artist}" album:"{album}"')
    res = get(f"https://api.deezer.com/search/album?q={q}&limit=10") or {}
    pick = None
    for a in res.get("data", []):
        if artist_ok(artist, a.get("artist", {}).get("name", "")) and similar(album, a.get("title", "")) >= 0.8:
            pick = a
            break
    if not pick:
        return {}
    full = get(f"https://api.deezer.com/album/{pick['id']}") or {}
    tracks = []
    for i, t in enumerate(full.get("tracks", {}).get("data", []), 1):
        detail = get(f"https://api.deezer.com/track/{t['id']}") or {}   # BPM lives here
        time.sleep(0.15)                                                 # stay under the rate limit
        bpm = round(detail.get("bpm") or 0)
        tracks.append({
            "num": detail.get("track_position") or i,
            "disc": detail.get("disk_number") or 1,
            "title": t.get("title", ""),
            "runtime": mmss(t.get("duration")),
            "bpm": bpm or None,
            "pace": pace_label(bpm),
            "explicit": bool(t.get("explicit_lyrics")),
        })
    return {
        "label": full.get("label", ""),
        "release_date": full.get("release_date", ""),
        "format": {"album": "LP", "ep": "EP", "single": "Single"}.get(full.get("record_type", ""), ""),
        "tracks": tracks,
        "links": {"deezer": full.get("link", "")},
        "sources": [full.get("link", "")] if full.get("link") else [],
    }


# ---- 3. MusicBrainz ----------------------------------------------------------
def from_musicbrainz(artist: str, album: str) -> dict:
    q = urllib.parse.quote(f'release:"{album}" AND artist:"{artist}"')
    res = get(f"https://musicbrainz.org/ws/2/release/?query={q}&fmt=json&limit=5") or {}
    pick = next((r for r in res.get("releases", [])
                 if similar(album, r.get("title", "")) >= 0.8
                 and artist_ok(artist, (r.get("artist-credit") or [{}])[0].get("name", ""))), None)
    if not pick:
        return {}
    time.sleep(1.1)                     # MusicBrainz asks for one request per second
    rel = get(f"https://musicbrainz.org/ws/2/release/{pick['id']}?inc=recordings+labels&fmt=json") or {}
    tracks = []
    for disc, medium in enumerate(rel.get("media", []), 1):
        for t in medium.get("tracks", []):
            tracks.append({"num": t.get("position"), "disc": disc, "title": t.get("title", ""),
                           "runtime": mmss((t.get("length") or 0) / 1000) if t.get("length") else ""})
    labels = [li.get("label", {}).get("name", "") for li in rel.get("label-info", []) if li.get("label")]
    url = f"https://musicbrainz.org/release/{pick['id']}"
    return {"label": labels[0] if labels else "", "release_date": rel.get("date", ""),
            "tracks": tracks, "sources": [url]}


# ---- 4. Discogs --------------------------------------------------------------
def from_discogs(artist: str, album: str) -> dict:
    token = os.getenv("DISCOGS_TOKEN", "")
    if not token:
        return {}
    q = urllib.parse.urlencode({"artist": artist, "release_title": album, "type": "release", "token": token})
    res = get(f"https://api.discogs.com/database/search?{q}") or {}
    hit = next((r for r in res.get("results", []) if similar(album, r.get("title", "").split(" - ")[-1]) >= 0.8), None)
    if not hit:
        return {}
    rel = get(f"https://api.discogs.com/releases/{hit['id']}?token={token}") or {}
    credits = [f"{c.get('name')} - {c.get('role')}" for c in rel.get("extraartists", []) if c.get("name")]
    fmt = ", ".join(f.get("name", "") for f in rel.get("formats", []) if f.get("name"))
    return {"format": fmt, "credits": credits[:25],
            "sources": [rel.get("uri", "")] if rel.get("uri") else []}


# ---- Merge -------------------------------------------------------------------
def merge(base: dict, new: dict) -> dict:
    """Fill blanks in base from new. Lists of sources are combined."""
    for k, v in new.items():
        if k == "sources":
            base["sources"] = list(dict.fromkeys((base.get("sources") or []) + v))
        elif k == "links":
            base["links"] = {**v, **(base.get("links") or {})}
        elif k == "tracks":
            if not base.get("tracks"):
                base["tracks"] = v
            else:
                # Same album from two sources: copy missing per-track fields by title.
                by_title = {norm(t["title"]): t for t in v}
                for t in base["tracks"]:
                    other = by_title.get(norm(t["title"]))
                    if other:
                        for field, val in other.items():
                            if val not in ("", None) and t.get(field) in ("", None):
                                t[field] = val
        elif v and not base.get(k):
            base[k] = v
    return base


def main() -> None:
    ap = argparse.ArgumentParser(description="Look up album facts for a review template")
    ap.add_argument("--artist", required=True)
    ap.add_argument("--album", required=True)
    ap.add_argument("--tag", help="KZSU Zookeeper album tag, if the library has it")
    ap.add_argument("--dry-run", action="store_true", help="print, don't write")
    args = ap.parse_args()
    load_env()

    path = RESEARCH / f"{slugify(args.artist + ' ' + args.album)}.json"
    info = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    info.setdefault("artist", args.artist)
    info.setdefault("album", args.album)

    steps = [("Zookeeper", lambda: from_zookeeper(args.tag) if args.tag else {}),
             ("Deezer", lambda: from_deezer(args.artist, args.album)),
             ("MusicBrainz", lambda: from_musicbrainz(args.artist, args.album)),
             ("Discogs", lambda: from_discogs(args.artist, args.album))]
    for name, fn in steps:
        found = fn()
        print(f"{name:12} {'found' if found else 'nothing'}"
              + (f" ({len(found.get('tracks', []))} tracks)" if found.get("tracks") else ""))
        info = merge(info, found)

    # Pace words for tracks that got a BPM from any source
    for t in info.get("tracks", []):
        if t.get("bpm") and not t.get("pace"):
            t["pace"] = pace_label(t["bpm"])

    if args.dry_run:
        print(json.dumps(info, indent=1, ensure_ascii=False)[:3000])
        return
    RESEARCH.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    no_bpm = [t["title"] for t in info.get("tracks", []) if not t.get("bpm")]
    print(f"Wrote {path}: {len(info.get('tracks', []))} tracks, label {info.get('label') or '?'}, "
          f"date {info.get('release_date') or '?'}")
    if no_bpm:
        print(f"No BPM for {len(no_bpm)} tracks. Look them up on songbpm.com or tunebat.com, or leave pace blank.")


if __name__ == "__main__":
    main()
