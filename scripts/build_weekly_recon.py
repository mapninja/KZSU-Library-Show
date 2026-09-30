#!/usr/bin/env python3
"""
build_weekly_recon.py
=====================

Turns one week's candidate list into the files you use for the show.

INPUT (you or the assistant edit this):
    data/recon/<SHOW_DATE>/candidates.json

OUTPUTS (regenerated every run, safe to overwrite):
    outputs/recon/<SHOW_DATE>/track_suggestions.md   preview links, metadata, FCC flags
    outputs/recon/<SHOW_DATE>/zookeeper_upload.csv    KZSU Zookeeper import file
    outputs/recon/<SHOW_DATE>/ytm_playlist.json        track list for the YTM playlist
    (a "working_" prefix is added when the input is working_playlist.json)

HOW TO RUN:
    python scripts/build_weekly_recon.py 2026-10-01                        # recon candidates
    python scripts/build_weekly_recon.py 2026-10-01 working_playlist.json  # working playlist

Zookeeper CSV format (beginner note)
------------------------------------
Zookeeper reads columns by POSITION, not by name, and there is no header row:

    artist, track, album, tag, label, timestamp

* tag       = the KZSU library tag number (leave blank if you don't know it)
* timestamp = leave blank; Zookeeper stamps times when you mark a track played
This order is inferred from your Sept. 10 import, which loaded correctly.
The Sept. 24 import used a 5-column file (no tag column), so every label
became a duration like "3:37". Keeping 6 columns avoids that.
"""
import csv
import json
import sys
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent


def ytm_link(artist: str, track: str) -> str:
    """Build a YouTube Music search link so you can preview a track in one click."""
    return "https://music.youtube.com/search?q=" + quote_plus(f"{artist} {track}")


def fcc_badge(t: dict) -> str:
    """Short FCC label for the Markdown table."""
    status = t.get("fcc_status", "UNVERIFIED")
    note = t.get("fcc_note", "")
    if status == "CLEAN" and note in ("", "none"):
        return "CLEAN"
    return f"**{status}**: {note}" if status != "CLEAN" else f"CLEAN ({note})"


def preview_link(t: dict) -> str:
    """Direct watch link when we know the YouTube videoId, otherwise a search link."""
    if t.get("videoId"):
        return f"https://music.youtube.com/watch?v={t['videoId']}"
    return ytm_link(t["artist"], t["track"])


def main(show_date: str, input_name: str = "candidates.json") -> None:
    src = ROOT / "data" / "recon" / show_date / input_name
    out_dir = ROOT / "outputs" / "recon" / show_date
    out_dir.mkdir(parents=True, exist_ok=True)
    data = json.loads(src.read_text(encoding="utf-8"))
    # "candidates.json" -> no prefix; "working_playlist.json" -> "working_" prefix
    prefix = "" if input_name == "candidates.json" else input_name.split("_")[0] + "_"

    # ---- 1. Markdown track suggestions ------------------------------------
    title = "Working playlist" if prefix else "Track suggestions"
    lines = [f"# {title}: The Library, {show_date}", "",
             "Priority: **R** required, **O** optional, **X** opportunistic, **SKIP** FCC problem, **CUT** removed by DJ Stace.",
             "FCC screen: Genius, AZLyrics, Bandcamp lyrics and Apple Music explicit tags. "
             "Words are named; lyric lines are not reproduced.", ""]
    if data.get("ytm_playlist"):
        y = data["ytm_playlist"]
        lines += [f"YouTube Music (studio, reversed): [{y['name']}]({y['url']}), {y['tracks']} tracks, {y['order']}.", ""]
    if data.get("ytm_air_order"):
        y = data["ytm_air_order"]
        lines += [f"YouTube Music (review, air order): [{y['name']}]({y['url']}), {y['tracks']} tracks. Edit this one.", ""]
    n_air = 0
    ytm_pos = 0  # running count of tracks placed in the YTM playlist
    for s in data["sets"]:
        # Where this set sits in the YouTube Music playlist, counted from the BOTTOM
        # (DJ Stace plays bottom-up). Skipped and not-on-YTM tracks are not counted.
        on_ytm = [t for t in s["tracks"] if t["priority"] not in ("SKIP", "CUT") and not t.get("ytm_missing")]
        pos = f" (YTM {ytm_pos + 1}-{ytm_pos + len(on_ytm)}: from the top of Air Order, from the bottom of Working)" if on_ytm and data.get("ytm_playlist") else ""
        ytm_pos += len(on_ytm)
        lines += [f"## {s['set']}{pos}", "",
                  "| # | Pri | Artist | Track | Album | Label | Released | Time | FCC | Why |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for t in s["tracks"]:
            if t["priority"] not in ("SKIP", "CUT"):
                n_air += 1
            num = n_air if t["priority"] not in ("SKIP", "CUT") else "-"
            upcoming = f" Upcoming: {t['upcoming']}." if t.get("upcoming") else ""
            lines.append(
                f"| {num} | {t['priority']} | {t['artist']} | [{t['track']}]({preview_link(t)}) "
                f"| {t['album']} | {t['label']} | {t['released']} | {t.get('duration', '')} | {fcc_badge(t)} | {t['why']}{upcoming} |")
        lines.append("")
    est_min = n_air * 4
    lines.insert(4, f"Airable tracks: {n_air} (about {est_min // 60} hr {est_min % 60} min at 4 min each). "
                    "Plan to drop 30-50%.")
    lines.insert(5, "")
    (out_dir / f"{prefix or 'track_'}{'playlist' if prefix else 'suggestions'}.md").write_text("\n".join(lines), encoding="utf-8")

    # ---- 2. Zookeeper CSV (forward order, SKIP tracks removed) ------------
    with (out_dir / f"{prefix}zookeeper_upload.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        for s in data["sets"]:
            for t in s["tracks"]:
                if t["priority"] in ("SKIP", "CUT"):
                    continue
                album = t["album"].replace(" (advance single)", "")
                label = "" if t["label"] == "unverified" else t["label"]
                w.writerow([t["artist"], t["track"], album, t.get("tag", ""), label, ""])

    # ---- 3. YTM working playlist plan -------------------------------------
    ytm = [{"artist": t["artist"], "track": t["track"], "album": t["album"], "priority": t["priority"],
            "videoId": t.get("videoId", "")}
           for s in data["sets"] for t in s["tracks"] if t["priority"] not in ("SKIP", "CUT")]
    (out_dir / f"{prefix}ytm_playlist.json").write_text(json.dumps(
        {"playlist_name": "DJ Stace library show working", "order": "forward", "tracks": ytm}, indent=1,
        ensure_ascii=False), encoding="utf-8")

    print(f"{n_air} airable tracks written to {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-10-01",
         sys.argv[2] if len(sys.argv) > 2 else "candidates.json")
