#!/usr/bin/env python3
"""
fcc_lyrics_check.py
===================

Checks songs for FCC words using lyrics databases, API first:

  1. Genius API    finds the exact song (needs Genius_ACCESS_TOKEN in .env).
                   The API has no lyrics field, so the script then reads the
                   lyrics from that song's Genius page.
  2. LRCLIB API    free, no key (https://lrclib.net). Used when Genius has no
                   lyrics or no match.
  3. lyrics.ovh    free, no key. Last resort.
  Also: the Deezer API's "explicit_lyrics" flag. It's a hint only, used to mark
  songs as SUSPECT when no lyrics were found anywhere.

It only ever saves COUNTS and locations (section name or line number). Lyric
text stays in memory and is never printed or written to disk.

USAGE (from the repo root):
    # One song
    python3 scripts/fcc_lyrics_check.py --artist "Gladie" --track "Fixer"

    # Every track in a review research file, and write results back into it
    python3 scripts/fcc_lyrics_check.py outputs/reviews/research/gladie-dont-know.json --write-back

    # A week's recon plan or working playlist
    python3 scripts/fcc_lyrics_check.py data/recon/2026-10-01/working_playlist.json

    # A plain text list, one "Artist - Title" per line
    python3 scripts/fcc_lyrics_check.py my_tracks.txt

OUTPUT:
    outputs/fcc/<input name>_fcc.json   one result per track
    outputs/fcc/<input name>_fcc.md     a table to read or paste

STATUS VALUES:
    FCC         at least one FCC word. Not airable 6 a.m.-10 p.m. without an edit.
    CAUTION     only caution words (bitch, asshole, goddamn). Station-policy call.
    CLEAN       lyrics found, no flagged words.
    SUSPECT     no lyrics found, but a store marks the track explicit.
    UNVERIFIED  no lyrics found anywhere. Listen before airing.
    INSTRUMENTAL  LRCLIB lists the track as instrumental.

Beginner notes
--------------
* An API is a web address that returns data (JSON) for programs instead of a
  page for people. We call it with urllib, which ships with Python.
* A "regular expression" (regex) is a text pattern. r"\\bshit\\w*" matches
  "shit" and "shitty". The (?!ake) part stops it from matching "shitake".
  Patterns still miss creative spellings, so spot-check every result by ear.
* Crowd-sourced lyrics are sometimes wrong or incomplete. A CLEAN result means
  "no flagged words in the posted lyrics," not a guarantee.
"""
import argparse
import difflib
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "fcc"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) KZSU-LibraryShow-FCC/1.0 (DJ Stace)"

# ---- Word lists (same as the station screen used everywhere else) ------------
FCC_PATTERNS = {
    "fuck": r"\bf+u+c+k\w*|\bmotherf\w*",
    "shit": r"\bs+h+i+t(?!ake)\w*|\bbullshit\w*",
    "piss": r"\bpiss\w*",
    "cunt": r"\bcunt\w*",
    "cocksucker": r"\bcocksuck\w*",
    "cock": r"\bcock(?!tail|roach|pit|atoo|er spaniel)s?\b",
    "tits": r"\btits?\b|\btitties\b",
}
CAUTION_PATTERNS = {
    "bitch": r"\bbitch\w*",
    "asshole": r"\bassholes?\b",
    "goddamn": r"\bgod\s?damn\w*",
}


# =============================================================================
# Small helpers
# =============================================================================
def load_env() -> None:
    """Read KEY=value lines from .env into environment variables."""
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def get(url: str, headers=None, as_json=True, timeout=20):
    """Download a URL. Returns parsed JSON (or text), or None on any error."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
        return json.loads(body) if as_json else body
    except Exception as e:                       # 404, timeout, blocked, bad JSON...
        print(f"    (request failed: {type(e).__name__} {str(e)[:80]})", file=sys.stderr)
        return None


def norm(s: str) -> str:
    """Simplify a title or name for matching: 'Pin-Up Boys (Remastered)' -> 'pin up boys'."""
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\s*[\(\[].*?(remaster|feat|ft\.|with |live|version|edit|mono|stereo|demo).*?[\)\]]", "", s)
    s = re.sub(r"\s+-\s+.*(remaster|version|edit|live).*$", "", s)
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"^the\s+", "", " ".join(s.split()))


def similar(a: str, b: str) -> float:
    """0.0-1.0 similarity of two normalized strings."""
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def artist_ok(wanted: str, found: str) -> bool:
    """True when the found artist is the one we asked for (allows 'X & Y' credits)."""
    w, f = norm(wanted), norm(found)
    return bool(w and f) and (w == f or w in f or f in w or similar(w, f) >= 0.85)


# =============================================================================
# Counting (never keeps lyric text)
# =============================================================================
def scan(lyrics: str) -> dict:
    """Count flagged words. Location = Genius section label, or line number."""
    fcc, caution, where = {}, {}, {}
    section, n_lines, words = None, 0, 0
    has_sections = bool(re.search(r"^\[.+?\]", lyrics, re.M))
    for raw in lyrics.splitlines():
        line = raw.strip()
        if not line:
            continue
        header = re.match(r"^\[(.+?)\]$", line)
        if header:
            section = header.group(1).split(":")[0].strip()   # "[Chorus: Artist]" -> "Chorus"
            continue
        n_lines += 1
        words += len(re.findall(r"\w+", line))
        low = line.lower()
        spot = section if (has_sections and section) else f"line {n_lines}"
        for table, bucket in ((FCC_PATTERNS, fcc), (CAUTION_PATTERNS, caution)):
            for word, pat in table.items():
                n = len(re.findall(pat, low))
                if n:
                    bucket[word] = bucket.get(word, 0) + n
                    where.setdefault(word, []).append(spot)
    # Tidy locations: ["Chorus", "Chorus"] -> ["Chorus x2"]
    tidy = {}
    for w, spots in where.items():
        counts = {}
        for s in spots:
            counts[s] = counts.get(s, 0) + 1
        tidy[w] = [f"{s} x{c}" if c > 1 else s for s, c in counts.items()]
    return {"hits": fcc, "caution": caution, "where": tidy, "lines": n_lines, "words": words}


# =============================================================================
# Source 1: Genius (API to find the song, song page for the lyrics)
# =============================================================================
class GeniusLyricsParser(HTMLParser):
    """Collects text inside <div data-lyrics-container="true"> blocks.

    Genius nests tags inside those divs, so we count open <div>s to know when
    the container ends. <br> becomes a line break. Parts marked
    data-exclude-from-selection (contributor headers) are skipped.
    """
    def __init__(self):
        super().__init__()
        self.depth = 0          # >0 while inside a lyrics container
        self.skip = 0           # >0 while inside an excluded block
        self.parts = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.depth:
            if tag == "div":
                self.depth += 1
            if self.skip or a.get("data-exclude-from-selection") == "true":
                self.skip += 1 if tag == "div" else 0
            if tag == "br":
                self.parts.append("\n")
        elif tag == "div" and a.get("data-lyrics-container") == "true":
            self.depth = 1
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if self.depth and tag == "div":
            if self.skip:
                self.skip -= 1
            self.depth -= 1

    def handle_data(self, data):
        if self.depth and not self.skip:
            self.parts.append(data)

    def text(self):
        return html.unescape("".join(self.parts))


def genius_find(artist: str, title: str, token: str):
    """Search the Genius API and return the best matching song, or None."""
    q = urllib.parse.quote(f"{title} {artist}")
    data = get(f"https://api.genius.com/search?q={q}", {"Authorization": f"Bearer {token}"})
    best, best_score = None, 0.0
    for hit in (data or {}).get("response", {}).get("hits", []):
        if hit.get("type") != "song":
            continue
        s = hit["result"]
        if not artist_ok(artist, s.get("primary_artist", {}).get("name", "") or s.get("artist_names", "")):
            continue
        score = similar(title, s.get("title", ""))
        if score > best_score:
            best, best_score = s, score
    return best if best_score >= 0.8 else None


def genius_lyrics(url: str):
    """Read lyrics from a Genius song page. Returns text or None."""
    page = get(url, as_json=False)
    if not page:
        return None
    p = GeniusLyricsParser()
    p.feed(page)
    text = p.text().strip()
    return text or None


# =============================================================================
# Source 2: LRCLIB (free lyrics API, no key)
# =============================================================================
def lrclib(artist: str, title: str, album: str = "", seconds: int = 0):
    """Return (lyrics or None, instrumental flag, record id)."""
    params = {"artist_name": artist, "track_name": title}
    if album:
        params["album_name"] = album
    if seconds:
        params["duration"] = seconds
    rec = get("https://lrclib.net/api/get?" + urllib.parse.urlencode(params))
    if not rec:   # exact lookup missed; try the search endpoint
        res = get("https://lrclib.net/api/search?" + urllib.parse.urlencode({"track_name": title, "artist_name": artist})) or []
        rec = next((r for r in res if artist_ok(artist, r.get("artistName", ""))
                    and similar(title, r.get("trackName", "")) >= 0.8), None)
    if not rec:
        return None, False, None
    return rec.get("plainLyrics") or None, bool(rec.get("instrumental")), rec.get("id")


# =============================================================================
# Source 3: lyrics.ovh, and the Deezer explicit flag
# =============================================================================
def lyrics_ovh(artist: str, title: str):
    url = "https://api.lyrics.ovh/v1/" + urllib.parse.quote(artist) + "/" + urllib.parse.quote(title)
    data = get(url, timeout=15)
    return (data or {}).get("lyrics") or None


def deezer_explicit(artist: str, title: str):
    """True/False from Deezer's explicit_lyrics flag, or None when not found."""
    q = urllib.parse.quote(f'artist:"{artist}" track:"{title}"')
    data = get(f"https://api.deezer.com/search?q={q}&limit=5")
    for t in (data or {}).get("data", []):
        if artist_ok(artist, t.get("artist", {}).get("name", "")) and similar(title, t.get("title", "")) >= 0.8:
            return bool(t.get("explicit_lyrics"))
    return None


# =============================================================================
# One track, start to finish
# =============================================================================
def check_track(artist, title, album="", seconds=0, token="", sources=("genius", "lrclib", "ovh")):
    row = {"artist": artist, "title": title}
    lyrics, source, url = None, None, None

    if "genius" in sources and token:
        song = genius_find(artist, title, token)
        if song:
            row["genius_match"] = f"{song.get('artist_names') or song['primary_artist']['name']} - {song['title']}"
            url = song.get("url")
            if song.get("lyrics_state") == "complete" or song.get("lyrics_state") is None:
                lyrics = genius_lyrics(url)
            if lyrics and re.search(r"lyrics for this song have yet to be released", lyrics, re.I):
                lyrics = None
            source = "Genius" if lyrics else None

    instrumental = False
    if not lyrics and "lrclib" in sources:
        lyrics, instrumental, rid = lrclib(artist, title, album, seconds)
        if lyrics:
            source, url = "LRCLIB", url or f"https://lrclib.net/api/get/{rid}"
    if not lyrics and not instrumental and "ovh" in sources:
        lyrics = lyrics_ovh(artist, title)
        if lyrics:
            source = "lyrics.ovh"

    row["source"], row["url"] = source, url
    if lyrics:
        row.update(scan(lyrics))
        row["status"] = "FCC" if row["hits"] else ("CAUTION" if row["caution"] else "CLEAN")
        del lyrics                                   # never keep the text around
    elif instrumental:
        row["status"] = "INSTRUMENTAL"
    else:
        row["explicit_flag"] = deezer_explicit(artist, title)
        row["status"] = "SUSPECT" if row["explicit_flag"] else "UNVERIFIED"
    return row


def summary(row: dict) -> str:
    """One-line FCC note in DJ Stace's review style: 'FCC "shit" x2 (Verse 2)'."""
    def fmt(d):
        return ", ".join(f"“{w}” x{n} ({'; '.join(row['where'].get(w, []))})" for w, n in d.items())
    st = row["status"]
    if st == "FCC":
        s = "FCC " + fmt(row["hits"])
        return s + ("; caution " + fmt(row["caution"]) if row.get("caution") else "")
    if st == "CAUTION":
        return "CAUTION " + fmt(row["caution"])
    if st == "SUSPECT":
        return "SUSPECT: marked explicit in stores, no lyrics posted. Listen first."
    if st == "UNVERIFIED":
        return "UNVERIFIED: no lyrics posted. Listen first."
    return st   # CLEAN or INSTRUMENTAL


# =============================================================================
# Inputs
# =============================================================================
def mmss_to_sec(t) -> int:
    try:
        m, s = str(t).split(":")[-2:]
        return int(m) * 60 + int(s)
    except (ValueError, AttributeError):
        return 0


def read_tracks(path: Path):
    """Return (kind, data, [track dicts]) for any supported input file."""
    if path.suffix == ".txt":
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if " - " in line and not line.startswith("#"):
                a, t = line.split(" - ", 1)
                rows.append({"artist": a.strip(), "title": t.strip()})
        return "txt", None, rows
    data = json.loads(path.read_text(encoding="utf-8"))
    if "sets" in data:                                    # recon plan or working playlist
        rows = [{"artist": t["artist"], "title": t.get("track") or t.get("title"), "album": t.get("album", ""),
                 "ref": t} for s in data["sets"] for t in s["tracks"] if t.get("priority") != "CUT"]
        return "plan", data, rows
    rows = [{"artist": t.get("artist") or data["artist"], "title": t["title"], "album": data.get("album", ""),
             "seconds": mmss_to_sec(t.get("runtime")), "num": t.get("num"), "ref": t}
            for t in data.get("tracks", [])]
    return "research", data, rows


def main() -> None:
    ap = argparse.ArgumentParser(description="FCC-screen songs with lyrics APIs (Genius first)")
    ap.add_argument("input", nargs="?", help="research JSON, recon plan JSON or .txt list")
    ap.add_argument("--artist")
    ap.add_argument("--track")
    ap.add_argument("--write-back", action="store_true", help="put fcc results into the input JSON")
    ap.add_argument("--no-genius", action="store_true", help="skip Genius (for testing other sources)")
    args = ap.parse_args()

    load_env()
    token = os.getenv("GENIUS_ACCESS_TOKEN") or os.getenv("Genius_ACCESS_TOKEN") or ""
    if not token and not args.no_genius:
        print("No Genius token in .env (Genius_ACCESS_TOKEN). Falling back to LRCLIB and lyrics.ovh.", file=sys.stderr)
    sources = ("lrclib", "ovh") if args.no_genius else ("genius", "lrclib", "ovh")

    if args.artist and args.track:
        kind, data, rows, stem = "one", None, [{"artist": args.artist, "title": args.track}], norm(args.artist + " " + args.track).replace(" ", "-")
    elif args.input:
        path = Path(args.input)
        kind, data, rows = read_tracks(path)
        stem = path.stem
    else:
        raise SystemExit(ap.format_usage())

    results = []
    for r in rows:
        res = check_track(r["artist"], r["title"], r.get("album", ""), r.get("seconds", 0), token, sources)
        res["num"] = r.get("num")
        res["note"] = summary(res)
        results.append(res)
        print(f"{res['status']:12} {r['artist']} - {r['title']}  {res['note'] if res['status'] not in ('CLEAN',) else ''}")
        if "ref" in r and args.write_back:
            # Research files use "fcc"/"fcc_source"; plans use "fcc_status"/"fcc_note".
            if kind == "research":
                r["ref"]["fcc"], r["ref"]["fcc_source"] = res["note"], res.get("url") or ""
            else:
                r["ref"]["fcc_status"], r["ref"]["fcc_note"] = res["status"], res["note"]
        time.sleep(0.4)                       # be polite to free APIs

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{stem}_fcc.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    md = [f"# FCC check: {stem}", "", "| # | Artist | Title | Status | Detail | Source |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(results, 1):
        src = f"[{r['source']}]({r['url']})" if r.get("url") and r.get("source") else (r.get("source") or "none")
        md.append(f"| {r.get('num') or i} | {r['artist']} | {r['title']} | {r['status']} | {r['note']} | {src} |")
    md += ["", "Counts only. Lyrics are crowd-sourced, so spot-check every FCC hit by ear."]
    (OUT_DIR / f"{stem}_fcc.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    if args.write_back and data is not None:
        Path(args.input).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    n = {s: sum(1 for r in results if r["status"] == s) for s in ("FCC", "CAUTION", "SUSPECT", "UNVERIFIED")}
    print(f"\n{len(results)} tracks: {n}. Wrote {OUT_DIR / (stem + '_fcc.md')}")


if __name__ == "__main__":
    main()
