#!/usr/bin/env python3
"""
render_show_files.py
====================

Rebuilds the show files for one week from the plan JSON.

INPUT:
    data/recon/<SHOW_DATE>/working_playlist.json   (the plan: sets of tracks)
    outputs/recon/<SHOW_DATE>/show_script.md       (optional; its talk-break text
                                                    above "## Sets" is kept)

OUTPUTS (in outputs/recon/<SHOW_DATE>/):
    notes_sheet_<date>.csv              Notes Sheet (uploaded as a Google Sheet)
    library_show_playlist_<date>.csv    Zookeeper import file, REVERSED order
    working_playlist.md                 forward-order table with preview links
    show_script.md                      talk breaks (kept) + regenerated set lists

HOW TO RUN (from the repo root):
    python3 scripts/render_show_files.py 2026-10-08
    python3 scripts/render_show_files.py 2026-10-08 --ticks harvested.csv

--ticks: a CSV harvested from Stace's deployed Notes Sheet. Any mark in her
"Cull" or "Replace" column is copied onto the matching row (matched by
artist + track), so a redeploy never erases her ticks.

Beginner notes:
* "Forward" order = the order tracks go on air. The Notes Sheet, script and
  working_playlist.md are forward because people read them top to bottom.
* The Zookeeper CSV is REVERSED (last on-air track first) because Stace's
  playback setup runs bottom-up.
* Tracks with priority SKIP (FCC problem) or CUT (Stace removed it) are left
  out of every file.
"""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root (one level above scripts/)


def secs(duration):
    """Turn "m:ss" into seconds. Blank or odd values count as 0."""
    try:
        m, s = duration.split(":")
        return int(m) * 60 + int(s)
    except (ValueError, AttributeError):
        return 0


def watch(t):
    """YouTube Music preview link for a track (music.youtube.com only)."""
    return f"https://music.youtube.com/watch?v={t['videoId']}" if t.get("videoId") else ""


def fcc_text(t):
    """FCC status for display, for example "CLEAN (LRCLIB)"."""
    note = t.get("fcc_note") or ""
    return note if note else t.get("fcc_status", "UNVERIFIED")


def airable(plan):
    """Yield (set name, track) in forward air order, skipping SKIP and CUT tracks."""
    for s in plan["sets"]:
        for t in s["tracks"]:
            if t.get("priority") not in ("SKIP", "CUT"):
                yield s["set"], t


def load_ticks(path):
    """Read Stace's Cull/Replace marks from a harvested Notes Sheet CSV."""
    ticks = {}
    if not path:
        return ticks
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row.get("Artist", "").lower(), row.get("Track", "").lower())
            marks = {c: row.get(c, "").strip() for c in ("Cull", "Replace")}
            # FALSE and blank are "not ticked"; anything else counts
            marks = {c: ("x" if v and v.upper() != "FALSE" else "") for c, v in marks.items()}
            ticks[key] = marks
    return ticks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("show_date")
    ap.add_argument("--ticks", help="harvested Notes Sheet CSV with Stace's Cull/Replace marks")
    a = ap.parse_args()

    plan = json.loads((ROOT / "data/recon" / a.show_date / "working_playlist.json").read_text(encoding="utf-8"))
    out = ROOT / "outputs/recon" / a.show_date
    out.mkdir(parents=True, exist_ok=True)
    ticks = load_ticks(a.ticks)
    rows = list(airable(plan))
    total = sum(secs(t.get("duration")) for _, t in rows)
    runtime = f"{total // 3600}:{total % 3600 // 60:02d}"

    # ---- 1. Notes Sheet CSV (forward order) --------------------------------
    with (out / f"notes_sheet_{a.show_date}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "Set", "Artist", "Track", "Album", "Orig. release", "Label", "Tag", "Time",
                    "FCC status", "YTM link", "Notes / talk points", "Cull", "Replace"])
        for i, (set_name, t) in enumerate(rows, 1):
            mark = ticks.get((t["artist"].lower(), t["track"].lower()), {})
            w.writerow([i, set_name, t["artist"], t["track"], t.get("album", ""), t.get("released", ""),
                        t.get("label", ""), t.get("tag", ""), t.get("duration", ""), fcc_text(t), watch(t),
                        t.get("why", ""), mark.get("Cull", ""), mark.get("Replace", "")])

    # ---- 2. Zookeeper CSV (REVERSED, no header, 6 quoted columns) ----------
    # Columns by position: artist, track, album, tag, label, timestamp (blank)
    zk = [[t["artist"], t["track"], t.get("album", ""), t.get("tag", ""),
           # strip "(verify)" notes so the label field holds only the label name
           "" if t.get("label") == "unverified" else t.get("label", "").replace(" (verify)", ""), ""] for _, t in rows]
    zk.reverse()  # first row = last track on air
    with (out / f"library_show_playlist_{a.show_date}.csv").open("w", newline="", encoding="utf-8") as f:
        csv.writer(f, quoting=csv.QUOTE_ALL).writerows(zk)

    # ---- 3. working_playlist.md (forward) ----------------------------------
    ao, wk = plan.get("ytm_air_order", {}), plan.get("ytm_playlist", {})
    md = [f"# Working playlist: {a.show_date} show (draft)", "",
          f"Air Order (forward): https://music.youtube.com/playlist?list={ao.get('id', 'PLSosF7JAIkaM')}",
          f"Working (reversed): https://music.youtube.com/playlist?list={wk.get('id', 'PLLXFGCRcu_qc')}", "",
          f"{len(rows)} tracks, {runtime}. FCC screen: LRCLIB and Genius, counts only.", "",
          "| # | Set | Artist | Track | Album | Label | Tag | Time | FCC | Why |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for i, (set_name, t) in enumerate(rows, 1):
        md.append(f"| {i} | {set_name} | {t['artist']} | [{t['track']}]({watch(t)}) | {t.get('album', '')} "
                  f"| {t.get('label', '')} | {t.get('tag', '')} | {t.get('duration', '')} | {fcc_text(t)} | {t.get('why', '')} |")
    if plan.get("excluded_fcc"):
        md += ["", "## Left out for FCC", ""]
        md += [f"- {x['artist']} \"{x['track']}\": {x['fcc']}. {x['action']}." for x in plan["excluded_fcc"]]
    if plan.get("cut"):
        md += ["", "## Cut by Stace", ""] + [f"- {x['artist']}, \"{x['track']}\"" for x in plan["cut"]]
    (out / "working_playlist.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # ---- 4. show_script.md: keep talk breaks, rebuild the set lists --------
    script_path = out / "show_script.md"
    head = script_path.read_text(encoding="utf-8").split("\n## Sets")[0] if script_path.exists() else \
        f"# Working Show Script: {a.show_date}\n"
    body = ["", "## Sets"]
    current = None
    for i, (set_name, t) in enumerate(rows, 1):
        if set_name != current:
            current = set_name
            body += ["", f"### {set_name}", ""]
            if "Triple Shot" in set_name and plan.get("triple_shot"):
                body += [f"Intro: {plan['triple_shot'].get('intro') or plan['triple_shot'].get('angle', '')}", ""]
        tag = f" Tag {t['tag']}." if t.get("tag") else ""
        label = t.get("label") or "Label: fill in at the studio"
        body.append(f"{i}. **{t['artist']}, \"{t['track']}\"** ({t.get('duration') or 'n/a'}) {label}.{tag} "
                    f"{t.get('why', '')} FCC: {fcc_text(t)}.")
    missing = [f"- {t['artist']}, \"{t['track']}\"" for _, t in rows if not t.get("label")]
    if missing:
        body += ["", "## Fill in at the studio", ""] + missing
    script_path.write_text(head.rstrip() + "\n" + "\n".join(body).replace("..", ".") + "\n", encoding="utf-8")

    print(f"{len(rows)} tracks, {runtime}. First on air: {rows[0][1]['track']}. "
          f"Zookeeper CSV first row: {zk[0][1]}, last row: {zk[-1][1]}.")


if __name__ == "__main__":
    main()
