#!/usr/bin/env python3
"""
review_boilerplate.py
=====================

Creates a KZSU album-review draft in DJ Stace's usual format, pre-filled
with researched metadata, so you only add your own comments and star ratings.

INPUT: a research file (JSON) saved at
    outputs/reviews/research/<slug>.json
Example structure (every field except artist/album/tracks is optional):
    {
      "artist": "Westside Cowboy",
      "album": "It Goes On",
      "label": "Island",
      "release_date": "2026-08-14",
      "format": "LP",
      "hometown": "Manchester, UK",
      "zookeeper_tag": "",
      "producer": "…",
      "release_notes": ["short factual notes, paraphrased"],
      "pull_quote": {"text": "under 15 words", "source": "Outlet", "url": "https://…"},
      "riyl_suggestions": ["Pavement", "Television"],
      "links": {"bandcamp": "…", "ytm": "…"},
      "tracks": [
        {"num": 1, "title": "Song", "runtime": "3:21",
         "notes": "single / video / guest / press note",
         "fcc": "CLEAN" | "FCC: word x2 (chorus)" | "UNVERIFIED",
         "fcc_source": "https://genius.com/…"}
      ],
      "sources": ["https://…"]
    }

OUTPUT: outputs/reviews/<slug>.md, ready to paste into Zookeeper's review box.

HOW TO RUN:
    python scripts/review_boilerplate.py outputs/reviews/research/westside-cowboy-it-goes-on.json

Optional: add "--zookeeper TAG" to pull the official library track list and
label from the KZSU API (needs KZSU_LIBRARY_API_KEY). Library data fills
any blanks; researched values win when both exist.
"""
import argparse
import json
import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "reviews"


def slugify(text: str) -> str:
    """'Westside Cowboy - It Goes On' -> 'westside-cowboy-it-goes-on'."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def us_date(iso: str) -> str:
    """'2026-08-14' -> '8/14/2026', matching your past reviews."""
    try:
        y, m, d = iso.split("-")
        return f"{int(m)}/{int(d)}/{y}"
    except (ValueError, AttributeError):
        return iso or "____"


def merge_zookeeper(info: dict, tag: str) -> dict:
    """Fill blanks from the Zookeeper album record (tracks, label, tag)."""
    import requests  # only needed for this option
    key = os.getenv("KZSU_LIBRARY_API_KEY", "")
    r = requests.get(f"https://zookeeper.stanford.edu/api/v1/album/{tag}",
                     headers={"X-APIKEY": key, "Accept": "application/vnd.api+json"}, timeout=60)
    r.raise_for_status()
    alb = r.json()["data"]
    info.setdefault("zookeeper_tag", tag)
    info["label"] = info.get("label") or alb["relationships"]["label"]["meta"]["name"]
    if not info.get("tracks"):
        info["tracks"] = [{"num": t["seq"], "title": t["track"], "runtime": t.get("duration") or ""}
                          for t in alb["attributes"]["tracks"]]
    return info


def fcc_summary(tracks: list) -> str:
    """Build the 'FCCs:' line using track numbers, like '4,7'."""
    flagged = [str(t["num"]) for t in tracks if str(t.get("fcc", "")).upper().startswith("FCC")]
    unknown = [str(t["num"]) for t in tracks if str(t.get("fcc", "")).upper().startswith("UNVERIFIED")]
    line = ",".join(flagged) if flagged else "None found"
    if unknown:
        line += f"  (not screened: {','.join(unknown)})"
    return line


def render(info: dict) -> str:
    t = info["tracks"]
    lines = [
        f"Album / Artist: {info['album']} / {info['artist']}",
        f"Label: {info.get('label', '____')}",
        f"Release date: {us_date(info.get('release_date', ''))}"
        + (f"   Format: {info['format']}" if info.get("format") else ""),
        "",
        f"Reviewed: {us_date(date.today().isoformat())}",
        "DJ Stace",
        "",
        "General Comments / Release Notes",
        "[Your take here.]",
        "",
    ]
    # Researched context, written as notes for you to keep, cut or rewrite.
    facts = []
    if info.get("hometown"):
        facts.append(f"From {info['hometown']}.")
    if info.get("producer"):
        facts.append(f"Produced by {info['producer']}.")
    facts += info.get("release_notes", [])
    if facts:
        lines += ["Release notes (research, edit freely):"] + [f"- {f}" for f in facts] + [""]
    q = info.get("pull_quote")
    if q:
        lines += [f"From {q['source']}:", f"“{q['text']}”", ""]

    lines += [
        f"FCCs: {fcc_summary(t)}",
        "RIYL: " + (", ".join(info.get("riyl_suggestions", [])) or "____") + "  [edit]",
        "",
        "Play: ____",
        "Rated with ____",
        "",
        "Tracks:",
    ]
    for tr in t:
        fcc = str(tr.get("fcc", "UNVERIFIED"))
        fcc_txt = "" if fcc.upper() == "CLEAN" else f" {fcc} -"
        note = f" [{tr['notes']}]" if tr.get("notes") else ""
        lines.append(f"{tr['num']}. ____ “{tr['title']}” {tr.get('runtime') or '__:__'} -{fcc_txt}"
                     f" [your notes]{note}")
    lines += ["", "---", "Research sources (delete before posting):"]
    lines += [f"- {s}" for s in info.get("sources", [])]
    for tr in t:
        if tr.get("fcc_source"):
            lines.append(f"- Track {tr['num']} lyrics checked: {tr['fcc_source']}")
    for k, v in (info.get("links") or {}).items():
        lines.append(f"- {k}: {v}")
    if info.get("zookeeper_tag"):
        lines.append(f"- Zookeeper tag: {info['zookeeper_tag']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Make a KZSU review boilerplate")
    ap.add_argument("research_json")
    ap.add_argument("--zookeeper", help="KZSU library tag number to pull tracks and label")
    args = ap.parse_args()

    info = json.loads(Path(args.research_json).read_text(encoding="utf-8"))
    if args.zookeeper:
        info = merge_zookeeper(info, args.zookeeper)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{slugify(info['artist'] + ' ' + info['album'])}.md"
    out.write_text(render(info), encoding="utf-8")
    print(f"Review draft written to {out}")


if __name__ == "__main__":
    main()
