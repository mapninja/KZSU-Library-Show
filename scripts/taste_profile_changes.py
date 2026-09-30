#!/usr/bin/env python3
"""
taste_profile_changes.py
========================

Compares the new config/taste_profile.json with the most recent older copy in
config/history/, then writes a Markdown report:

    outputs/taste_profile/changes_<today>.md

The report has two jobs:
1. Tell Stace what changed (movers, new air candidates, her playlist edits).
2. Hand the agent ready-made tables to paste into TASTE_PROFILE.md, so the
   human-readable profile stays in sync with the numbers.

USAGE (after build_taste_profile.py):
    python3 scripts/taste_profile_changes.py
    python3 scripts/taste_profile_changes.py --against config/history/taste_profile_2026-09-26.json
"""
import argparse
import json
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "config" / "taste_profile.json"
HISTORY = ROOT / "config" / "history"
DB = ROOT / "data" / "library_show.db"
FEEDBACK = ROOT / "data" / "daily" / "feedback.json"
PL_META = ROOT / "data" / "ytm" / "playlists.json"
OUT_DIR = ROOT / "outputs" / "taste_profile"
TODAY = date.today()


def ap_date(iso: str) -> str:
    """'2026-09-30' -> 'Sept. 30, 2026' (AP style month abbreviations)."""
    if not iso:
        return "unknown"
    d = datetime.strptime(iso[:10], "%Y-%m-%d")
    months = ["Jan.", "Feb.", "March", "April", "May", "June", "July",
              "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]
    return f"{months[d.month - 1]} {d.day}, {d.year}"


def previous_profile(explicit):
    """Pick the file to compare against: --against, else the newest history file."""
    if explicit:
        return Path(explicit).resolve()
    files = sorted(HISTORY.glob("taste_profile_*.json"))
    return files[-1] if files else None


def freshness() -> dict:
    """How current each data source is. Stale sources get flagged in the report."""
    info = {}
    if DB.exists():
        con = sqlite3.connect(f"file:{DB}?mode=ro&immutable=1", uri=True)
        info["newest_show"] = con.execute("SELECT MAX(date) FROM kzsu_shows WHERE rebroadcast = 0").fetchone()[0]
        info["newest_ytm_play"] = (con.execute("SELECT MAX(played_at) FROM v_ytm_plays").fetchone()[0] or "")[:10]
        # Label spins this calendar year, for the "2026 so far" line.
        info["labels_this_year"] = con.execute(
            """SELECT MAX(label), COUNT(*) FROM v_airplay
               WHERE date >= ? AND label_key NOT IN ('', 'self', 'self release', 'unknown', 'none')
               GROUP BY label_key ORDER BY COUNT(*) DESC LIMIT 6""", (f"{TODAY.year}-01-01",)).fetchall()
        con.close()
    if PL_META.exists():
        info["playlists_scraped"] = json.loads(PL_META.read_text()).get("scraped", "")
    return info


def main() -> None:
    ap = argparse.ArgumentParser(description="Report what changed in the taste profile")
    ap.add_argument("--against", help="older taste_profile JSON to compare with")
    args = ap.parse_args()

    new = json.loads(PROFILE.read_text())
    prev_path = previous_profile(args.against)
    old = json.loads(prev_path.read_text()) if prev_path else {"artists": [], "generated": ""}

    new_rank = {a["key"]: i + 1 for i, a in enumerate(new["artists"])}
    old_rank = {a["key"]: i + 1 for i, a in enumerate(old["artists"])}
    by_key = {a["key"]: a for a in new["artists"]}
    fresh = freshness()
    md = []

    md.append(f"# Taste profile changes, {ap_date(new['generated'])}")
    md.append("")
    md.append(f"Compared with the profile from {ap_date(old.get('generated'))}"
              f" (`{prev_path.relative_to(ROOT) if prev_path else 'none'}`).")
    md.append("")

    # ---- Data freshness: flag anything more than 14 / 60 days old ----------
    md.append("## Data freshness")
    md.append("")
    def age(iso):
        return (TODAY - datetime.strptime(iso[:10], "%Y-%m-%d").date()).days if iso else 9999
    rows = [("Newest KZSU show in the database", fresh.get("newest_show"), 10),
            ("Newest YouTube Music play (Takeout)", fresh.get("newest_ytm_play"), 60),
            ("YouTube Music playlists scraped", fresh.get("playlists_scraped"), 14)]
    for label, iso, limit in rows:
        flag = " **STALE**" if age(iso) > limit else ""
        md.append(f"- {label}: {ap_date(iso)}{flag}")
    md.append("")

    # ---- Movers -------------------------------------------------------------
    ups, downs, entered, left = [], [], [], []
    for key, r in new_rank.items():
        o = old_rank.get(key)
        if o and r <= 200 and o - r >= 15:
            ups.append((o - r, by_key[key]["artist"], o, r))
        if o and o <= 100 and r - o >= 15:
            downs.append((r - o, by_key[key]["artist"], o, r))
        if r <= 100 and (not o or o > 100):
            entered.append((r, by_key[key]["artist"], o))
    for a in old["artists"][:100]:
        if new_rank.get(a["key"], 9999) > 100:
            left.append(a["artist"])
    md.append("## What moved")
    md.append("")
    if not old["artists"]:
        md.append("- No earlier profile to compare with. Next run will show movers.")
    for _, name, o, r in sorted(ups, reverse=True)[:15]:
        md.append(f"- Up: {name}, {o} to {r}")
    for _, name, o, r in sorted(downs, reverse=True)[:10]:
        md.append(f"- Down: {name}, {o} to {r}")
    if entered:
        md.append("- New in the top 100: " + ", ".join(f"{n} ({r})" for r, n, _ in sorted(entered)))
    if left:
        md.append("- Left the top 100: " + ", ".join(left))
    if old["artists"] and not (ups or downs or entered or left):
        md.append("- No artist moved 15 or more places.")
    md.append("")

    # ---- Her playlist edits since the last profile --------------------------
    if FEEDBACK.exists():
        fb = json.loads(FEEDBACK.read_text())
        since = old.get("generated") or "0000"
        rem = [f"{x['artist']} \"{x['title']}\"" for x in fb.get("removed", []) if x.get("date", "") >= since]
        add = [f"{x['artist']} \"{x['title']}\"" for x in fb.get("added_by_stace", []) if x.get("date", "") >= since]
        repeat = [a for a, n in fb.get("artist_removals", {}).items() if n >= 3]
        md.append("## Stace's playlist edits since the last profile")
        md.append("")
        md.append("- Added by Stace (fits, keep): " + (", ".join(add) or "none"))
        md.append("- Removed (not interested right now): " + (", ".join(rem) or "none"))
        if repeat:
            md.append("- Removed 3+ times, now downweighted in picks: " + ", ".join(repeat))
        md.append("")

    # ---- Ready-to-paste sections for TASTE_PROFILE.md ------------------------
    md.append("## Paste into TASTE_PROFILE.md")
    md.append("")
    md.append("### Core artists table")
    md.append("")
    md.append("| Rank | Artist | Shows aired | Last 12 mo. | YTM plays | Playlist score |")
    md.append("|---|---|---|---|---|---|")
    for i, a in enumerate(new["artists"][:20]):
        md.append(f"| {i + 1} | {a['artist']} | {a['shows']} | {a['shows_12mo']} | {a['ytm_plays']} | {a.get('playlist_score', 0)} |")
    md.append("")
    md.append("Next tier: " + ", ".join(a["artist"] for a in new["artists"][20:45]) + ".")
    md.append("")

    md.append("### Labels table")
    md.append("")
    md.append("| Label | Spins | Artists |")
    md.append("|---|---|---|")
    for lab in new["labels"][:14]:
        md.append(f"| {lab['label']} | {lab['spins']} | {lab['artists']} |")
    if fresh.get("labels_this_year"):
        md.append("")
        md.append(f"{TODAY.year} so far: " + ", ".join(f"{l} ({n})" for l, n in fresh["labels_this_year"]) + ".")
    md.append("")

    md.append("### In rotation now (last 90 days of YouTube Music)")
    md.append("")
    rot = sorted(new["artists"], key=lambda a: -a["ytm_plays_90d"])[:10]
    md.append("- " + ", ".join(f"{a['artist']} ({a['ytm_plays_90d']})" for a in rot) + ".")
    md.append("")

    md.append("### Heard a lot, rarely or never aired")
    md.append("")
    heard = [a for a in sorted(new["artists"], key=lambda a: -a["ytm_plays_90d"])
             if a["shows"] <= 2 and a["ytm_plays_90d"] >= 5][:14]
    md.append("- " + (", ".join(f"{a['artist']} ({a['ytm_plays_90d']} plays in 90 days, {a['shows']} spin{'' if a['shows'] == 1 else 's'} ever)"
                                for a in heard) or "none") + ".")
    md.append("")

    md.append("### Overdue favorites")
    md.append("")
    cutoff = (TODAY - timedelta(days=365)).isoformat()
    overdue = [a for a in new["artists"] if a["shows"] >= 12 and a["last_spin"] and a["last_spin"] < cutoff
               and a["ytm_plays"] > 0][:12]
    md.append("- " + (", ".join(f"{a['artist']} (last aired {a['last_spin'][:4]})" for a in overdue) or "none") + ".")
    md.append("")

    md.append("### Strong in playlists, never aired")
    md.append("")
    old_na = {a["artist"] for a in old.get("playlist_not_aired", [])}
    na = new.get("playlist_not_aired", [])[:25]
    md.append("- " + (", ".join(a["artist"] + ("" if a["artist"] in old_na or not old_na else " (new)")
                                for a in na) or "none") + ".")
    md.append("")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"changes_{TODAY.isoformat()}.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
