#!/usr/bin/env python3
"""
ytm_build_playlist.py
=====================

Creates or overwrites a YouTube Music playlist from a week's playlist plan,
using ytmusicapi (https://ytmusicapi.readthedocs.io).

RUN THIS ON YOUR OWN MAC. It signs in with your browser headers file
(browser.json), so it acts as your Google account.

SETUP (once):
    pip install ytmusicapi
    # browser.json must exist; see "ytmusicapi browser" in the docs

USAGE:
    # 1. Dry run (default): look up every track and show what would be added
    python scripts/ytm_build_playlist.py outputs/recon/2026-10-01/working_ytm_playlist.json

    # 2. Create or overwrite the playlist for real
    python scripts/ytm_build_playlist.py outputs/recon/2026-10-01/working_ytm_playlist.json --apply

    # Studio copy: reverse order so the first on-air track is last
    python scripts/ytm_build_playlist.py <plan.json> --apply --reverse --name "DJ Stace studio"

    # Post-show archive with the week's date
    python scripts/ytm_build_playlist.py <plan.json> --apply --name "The Library with DJ Stace 2026-10-01" --public

Playlist order (important)
--------------------------
DJ Stace plays show playlists BOTTOM-UP with autoplay off, so the first
on-air track must be the LAST item. Use --reverse for the working and studio
playlists. Post-show archives stay in forward order (no --reverse).
Note: "DJ Stace library show working" (PLLXFGCRcu_qc) is set on youtube.com to
sort "Date added (newest)", which already reverses the add order. If you keep
that setting, run WITHOUT --reverse; if you switch it back to "Manual", use --reverse.

What it does, step by step
--------------------------
1. Reads the plan JSON (artist, track, optional videoId).
2. Tracks without a videoId are searched with ytm.search(..., filter="songs").
   The top match is used. Check the dry-run printout for wrong matches.
3. Saves the resolved IDs next to the plan (<plan>_resolved.json), so the
   next run reuses them. Fix a wrong match by editing the videoId there.
4. With --apply: if a playlist with that exact name exists in your library,
   it removes every item and adds the new list (so the playlist URL stays
   the same week to week). Otherwise it creates a new playlist.
5. Rereads the playlist and confirms the order matches.
"""
import argparse
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NAME = "DJ Stace library show working"


def load_env() -> None:
    """Read KEY=value lines from .env into environment variables."""
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def resolve(ytm, tracks: list[dict]) -> list[dict]:
    """Fill in missing videoIds by searching YouTube Music."""
    for t in tracks:
        if t.get("videoId"):
            t["match"] = "given"
            continue
        results = ytm.search(f"{t['artist']} {t['track']}", filter="songs", limit=3)
        if results:
            top = results[0]
            t["videoId"] = top.get("videoId", "")
            t["match"] = f"{', '.join(a['name'] for a in top.get('artists', []))} - {top.get('title')}"
        else:
            t["match"] = "NOT FOUND"
        time.sleep(0.3)  # small pause between searches
    return tracks


def find_playlist(ytm, name: str):
    """Return the playlistId of a library playlist with this exact name, or None."""
    for p in ytm.get_library_playlists(limit=None):
        if p.get("title") == name:
            return p["playlistId"]
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a YouTube Music playlist from a plan JSON")
    ap.add_argument("plan")
    ap.add_argument("--apply", action="store_true", help="actually write to YouTube Music")
    ap.add_argument("--name", default=DEFAULT_NAME)
    ap.add_argument("--reverse", action="store_true", help="studio order (last on-air track first)")
    ap.add_argument("--public", action="store_true", help="make the playlist public (default private)")
    args = ap.parse_args()

    load_env()
    from ytmusicapi import YTMusic
    auth = os.getenv("YTMUSIC_AUTH_PATH", str(ROOT / "browser.json"))
    ytm = YTMusic(auth)

    plan_path = Path(args.plan)
    cache = plan_path.with_name(plan_path.stem + "_resolved.json")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    tracks = [t for t in plan["tracks"] if t.get("priority") != "SKIP"]

    # Reuse earlier lookups so fixes you make by hand are kept.
    if cache.exists():
        known = {(t["artist"], t["track"]): t for t in json.loads(cache.read_text())["tracks"]}
        for t in tracks:
            if not t.get("videoId") and (t["artist"], t["track"]) in known:
                t["videoId"] = known[(t["artist"], t["track"])].get("videoId", "")

    tracks = resolve(ytm, tracks)
    cache.write_text(json.dumps({"tracks": tracks}, indent=1, ensure_ascii=False), encoding="utf-8")

    order = list(reversed(tracks)) if args.reverse else tracks
    print(f"{'#':>3}  {'Planned':<55} Matched")
    for i, t in enumerate(order, 1):
        print(f"{i:>3}  {(t['artist'] + ' - ' + t['track'])[:55]:<55} {t['match']}")
    ids = [t["videoId"] for t in order if t.get("videoId")]
    missing = [t for t in order if not t.get("videoId")]
    print(f"\n{len(ids)} tracks ready, {len(missing)} not found.")

    if not args.apply:
        print(f"Dry run only. Edit {cache.name} to fix matches, then rerun with --apply.")
        return

    privacy = "PUBLIC" if args.public else "PRIVATE"
    pid = find_playlist(ytm, args.name)
    if pid:
        # Overwrite: remove current items (needs videoId + setVideoId pairs).
        current = ytm.get_playlist(pid, limit=None).get("tracks", [])
        if current:
            ytm.remove_playlist_items(pid, [{"videoId": c["videoId"], "setVideoId": c["setVideoId"]}
                                            for c in current if c.get("setVideoId")])
        ytm.add_playlist_items(pid, ids, duplicates=True)
        print(f"Overwrote '{args.name}' ({pid}).")
    else:
        pid = ytm.create_playlist(args.name, plan.get("note", "The Library with DJ Stace, KZSU 90.1 FM"),
                                  privacy_status=privacy, video_ids=ids)
        print(f"Created '{args.name}' ({pid}).")

    # Verify: reread and compare order.
    time.sleep(2)
    got = [t["videoId"] for t in ytm.get_playlist(pid, limit=None).get("tracks", [])]
    print("Order verified." if got == ids else f"Check order: expected {len(ids)}, found {len(got)}.")
    print(f"https://music.youtube.com/playlist?list={pid}")


if __name__ == "__main__":
    main()
