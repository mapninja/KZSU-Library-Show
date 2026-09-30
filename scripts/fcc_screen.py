#!/usr/bin/env python3
"""
fcc_screen.py
=============

Screens tracks for FCC words using the Genius API through the LyricsGenius
library (https://github.com/johnwmillr/LyricsGenius).

RUN THIS ON YOUR OWN MAC (not inside Claude's sandbox). It reads your
Genius token from .env, downloads each song's lyrics into memory, counts
flagged words by song section, and writes ONLY the counts. No lyric text is
saved, so the output files are safe to share and commit.

SETUP (once):
    pip install lyricsgenius python-dotenv

USAGE:
    # screen a week's recon candidates
    python scripts/fcc_screen.py data/recon/2026-10-01/candidates.json

    # screen an album review research file
    python scripts/fcc_screen.py outputs/reviews/research/westside-cowboy-it-goes-on.json

OUTPUT:
    <input>_fcc.json next to the input, for example
    {"artist": "...", "track": "...", "status": "FCC", "hits": {"shit": 1},
     "sections": {"shit": ["Verse 2"]}, "genius_url": "..."}

Beginner notes
--------------
* A "regular expression" (regex) is a text pattern. r"\\bfuck\\w*" matches
  "fuck", "fucking" and "fucked" but not words that merely contain the letters.
* Genius marks song sections with headers like "[Chorus]". We track the most
  recent header so each hit gets a location.
* Genius transcriptions are crowd-sourced. Always spot-check by listening.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

# ---- FCC word list ----------------------------------------------------------
# "FCC" words must not air 6 a.m. to 10 p.m. "CAUTION" words are station-policy calls.
FCC_PATTERNS = {
    "fuck": r"\bf+u+c+k\w*|\bmotherf\w*",
    "shit": r"\bs+h+i+t\w*|\bbullshit\w*",
    "piss": r"\bpiss\w*",
    "cunt": r"\bcunt\w*",
    "cocksucker": r"\bcocksuck\w*",
    "cock": r"\bcock(?!tail|roach|pit|atoo|er spaniel)\b",
    "tits": r"\btits?\b|\btitties\b",
}
CAUTION_PATTERNS = {
    "bitch": r"\bbitch\w*",
    "asshole": r"\basshole\w*",
    "goddamn": r"\bgod\s?damn\w*",
}


def load_env(path: Path) -> None:
    """Minimal .env reader so python-dotenv is optional."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def scan(lyrics: str) -> tuple[dict, dict, dict]:
    """Return (fcc_hits, caution_hits, sections) for one song's lyrics."""
    fcc, caution, where = {}, {}, {}
    section = "Intro"
    for line in lyrics.splitlines():
        header = re.match(r"^\[(.+?)\]", line.strip())
        if header:
            section = header.group(1)
            continue
        low = line.lower()
        for word, pat in FCC_PATTERNS.items():
            n = len(re.findall(pat, low))
            if n:
                fcc[word] = fcc.get(word, 0) + n
                where.setdefault(word, []).append(section)
        for word, pat in CAUTION_PATTERNS.items():
            n = len(re.findall(pat, low))
            if n:
                caution[word] = caution.get(word, 0) + n
                where.setdefault(word, []).append(section)
    # Collapse repeated section names: ["Chorus","Chorus"] -> ["Chorus x2"]
    tidy = {}
    for w, secs in where.items():
        counts = {}
        for s in secs:
            counts[s] = counts.get(s, 0) + 1
        tidy[w] = [f"{s} x{c}" if c > 1 else s for s, c in counts.items()]
    return fcc, caution, tidy


def tracks_from(path: Path) -> list[tuple[str, str]]:
    """Accept a recon candidates.json or a review research JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if "sets" in data:
        return [(t["artist"], t["track"]) for s in data["sets"] for t in s["tracks"]]
    return [(data["artist"], t["title"]) for t in data.get("tracks", [])]


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    root = Path(__file__).resolve().parent.parent
    load_env(root / ".env")
    token = os.getenv("GENIUS_ACCESS_TOKEN") or os.getenv("Genius_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Add GENIUS_ACCESS_TOKEN to .env first.")

    import lyricsgenius  # pip install lyricsgenius
    genius = lyricsgenius.Genius(token, timeout=20, retries=2, verbose=False,
                                 remove_section_headers=False, skip_non_songs=True)

    src = Path(sys.argv[1])
    results = []
    for artist, track in tracks_from(src):
        row = {"artist": artist, "track": track}
        try:
            song = genius.search_song(track, artist)
        except Exception as e:  # network hiccup, rate limit, etc.
            song, row["error"] = None, str(e)
        if not song or not song.lyrics:
            row["status"] = "UNVERIFIED"
        else:
            fcc, caution, where = scan(song.lyrics)
            row.update({"genius_url": song.url, "matched_title": song.title,
                        "hits": fcc, "caution": caution, "sections": where,
                        "status": "FCC" if fcc else ("CAUTION" if caution else "CLEAN")})
        results.append(row)
        print(f"{row['status']:10} {artist} - {track}  {row.get('hits', '')}")
        time.sleep(0.5)  # be polite to Genius

    out = src.with_name(src.stem + "_fcc.json")
    out.write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out}. Check 'matched_title' to be sure Genius found the right song.")


if __name__ == "__main__":
    main()
