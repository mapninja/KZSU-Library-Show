#!/usr/bin/env python3
"""
review_boilerplate.py
=====================

Turns a research file into a KZSU album-review template in DJ Stace's format
(the layout of her 2022-23 reviews). She adds her own take, stars and
listening notes; everything else is pre-filled.

INPUT:  outputs/reviews/research/<slug>.json
        (start one with scripts/album_lookup.py, screen it with
         scripts/fcc_lyrics_check.py --write-back, then add quotes and notes)
OUTPUT: outputs/reviews/<slug>.md

Research file fields (all optional except artist, album and tracks):
    {
      "artist": "...", "album": "...", "label": "...",
      "release_date": "2026-08-21", "format": "LP", "zookeeper_tag": "",
      "draft_comment": "One or two lines in Stace's voice, from the research.",
      "pull_quotes": [{"text": "under 15 words", "source": "Pitchfork", "url": "https://..."}],
      "release_notes": ["short paraphrased facts"],
      "credits": ["Name - producer", "Name - drums"],
      "riyl_suggestions": ["Artist", "Artist"],
      "tracks": [{"num": 1, "title": "Song", "runtime": "3:21", "bpm": 112,
                  "pace": "Midtempo", "explicit": false,
                  "notes": "Lead single.",            # objective tags only
                  "fcc": "CLEAN" | "FCC “shit” x2 (Verse 2)" | "UNVERIFIED: ..." | "SUSPECT: ...",
                  "fcc_source": "https://genius.com/..."}],
      "links": {"bandcamp": "...", "deezer": "..."},
      "sources": ["https://..."]
    }
An older single "pull_quote" object still works.

HOW TO RUN:
    python3 scripts/review_boilerplate.py outputs/reviews/research/widowspeak-roses.json
"""
import argparse
import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "reviews"


def slugify(text: str) -> str:
    """'Westside Cowboy - It Goes On' -> 'westside-cowboy-it-goes-on'."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def long_date(iso: str) -> str:
    """'2026-08-21' -> 'August 21, 2026' (the Release Date style in her reviews)."""
    try:
        return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%B %-d, %Y")
    except (ValueError, TypeError):
        return iso or "____"


def us_date(d: date) -> str:
    """date(2026, 9, 30) -> '9/30/2026' (her Review Date style)."""
    return f"{d.month}/{d.day}/{d.year}"


def two_digit_runtime(rt: str) -> str:
    """'3:05' -> '03:05', matching her tracklists. Leaves blanks as '__:__'."""
    m = re.match(r"^(\d+):(\d{2})$", str(rt or "").strip())
    return f"{int(m.group(1)):02d}:{m.group(2)}" if m else (rt or "__:__")


def fcc_kind(t: dict) -> str:
    """Normalize a track's fcc field to FCC, CAUTION, CLEAN, SUSPECT, UNVERIFIED or INSTRUMENTAL."""
    f = str(t.get("fcc") or "").upper()
    for k in ("FCC", "CAUTION", "SUSPECT", "UNVERIFIED", "INSTRUMENTAL", "CLEAN"):
        if f.startswith(k):
            return k
    # Not screened yet: an explicit tag makes it a suspect, otherwise unknown.
    return "SUSPECT" if t.get("explicit") else "UNVERIFIED"


def fcc_text(t: dict) -> str:
    """The FCC part of a track line, in her style."""
    kind, raw = fcc_kind(t), str(t.get("fcc") or "")
    if kind == "FCC":
        return raw.rstrip(".") + "."                      # e.g. FCC “shit” x2 (Verse 2).
    if kind == "CAUTION":
        return raw.replace("CAUTION", "Caution", 1).rstrip(".") + "."
    if kind == "SUSPECT":
        return "FCC suspect: marked explicit, no lyrics posted. Listen first."
    if kind == "UNVERIFIED":
        return "FCC unverified: no lyrics posted." if raw else "FCC not screened."
    return ""                                             # CLEAN / INSTRUMENTAL: say nothing


def pace_text(t: dict) -> str:
    """'Midtempo (~112 BPM).' or '' when no pace is known (no blank placeholder, Stace's rule Oct. 8, 2026)."""
    if t.get("pace") and t.get("bpm"):
        return f"{t['pace']} (~{int(t['bpm'])} BPM)."
    if t.get("pace"):
        return f"{t['pace']}."
    return ""


def render(info: dict) -> str:
    tracks = info.get("tracks", [])
    fcc_nums = [str(t.get("num")) for t in tracks if fcc_kind(t) == "FCC"]
    open_nums = [str(t.get("num")) for t in tracks if fcc_kind(t) in ("SUSPECT", "UNVERIFIED")]
    quotes = info.get("pull_quotes") or ([info["pull_quote"]] if info.get("pull_quote") else [])

    out = [f"Album / Artist: {info['album']} / {info['artist']}", "",
           f"Label: {info.get('label') or '____'}", "",
           f"Release Date: {long_date(info.get('release_date', ''))}",
           f"Review Date: {us_date(date.today())}",
           "Reviewer: DJ Stace", "",
           "General Comments / Reviews:", ""]
    comment = info.get("draft_comment", "").strip()
    out.append(f"{comment} - DJ Stace  [DRAFT, edit or replace]" if comment else "[Your take here.] - DJ Stace")
    for q in quotes[:3]:
        text = q["text"].strip(' "“”')            # drop quote marks already in the text
        out += ["", "“" + text + "” - " + q["source"]]

    out += ["", "Release Notes:", ""]
    notes = list(info.get("release_notes", []))
    if info.get("release_date"):
        notes.append(f"released {long_date(info['release_date'])}")
    out += notes or ["____"]
    if info.get("credits"):
        out += ["", "; ".join(info["credits"])]

    fcc_line = ",".join(fcc_nums) if fcc_nums else "None found"
    if open_nums:
        fcc_line += f"  (check by ear: {','.join(open_nums)})"
    play = "All but FCCs" if fcc_nums else "All"
    out += ["", f"FCCs: {fcc_line}", "",
            "RIYL: " + (", ".join(info.get("riyl_suggestions", [])) or "____"), "",
            f"Play: {play}, Favs Rated with up to *****", "",
            "Tracklist:"]
    multi_disc = len({t.get("disc", 1) for t in tracks}) > 1
    for t in tracks:
        num = f"{t.get('disc', 1)}-{t['num']}" if multi_disc else str(t.get("num"))
        # FCC and caution notes come FIRST in the track comment (Stace's rule, Oct. 8, 2026),
        # then the pace words, then any other objective notes.
        bits = []
        if fcc_text(t):
            bits.append(fcc_text(t))
        if pace_text(t):
            bits.append(pace_text(t))
        if t.get("notes"):
            bits.append(t["notes"].rstrip(".") + ".")
        line = f"{num}. {t['title']} {two_digit_runtime(t.get('runtime'))}"
        # No "Pace: ____" or "[notes]" placeholders: only what is known (FCC, pace, sourced notes).
        out.append(line + (" - " + " ".join(bits) if bits else ""))

    # Sources stay in the posted review (Stace keeps them), so no "delete" note.
    out += ["", "Sources:"]
    out += [f"- {s}" for s in info.get("sources", []) if s]
    for q in quotes:
        if q.get("url"):
            out.append(f"- Quote, {q['source']}: {q['url']}")
    for t in tracks:
        if t.get("fcc_source"):
            out.append(f"- Track {t['num']} lyrics checked: {t['fcc_source']}")
    for k, v in (info.get("links") or {}).items():
        if v:
            out.append(f"- {k}: {v}")
    if info.get("zookeeper_tag"):
        out.append(f"- Zookeeper tag: {info['zookeeper_tag']}")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Make a KZSU review template")
    ap.add_argument("research_json")
    ap.add_argument("--overwrite", action="store_true", help="replace an existing template")
    args = ap.parse_args()
    info = json.loads(Path(args.research_json).read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{slugify(info['artist'] + ' ' + info['album'])}.md"
    if out.exists() and not args.overwrite:
        # Stace may have started writing in the old template. Never clobber it.
        out = out.with_name(out.stem + f"_{date.today().isoformat()}.md")
        print(f"A template already exists, so this one is saved separately. Use --overwrite to replace it.")
    out.write_text(render(info), encoding="utf-8")
    print(f"Review template written to {out}")


if __name__ == "__main__":
    main()
