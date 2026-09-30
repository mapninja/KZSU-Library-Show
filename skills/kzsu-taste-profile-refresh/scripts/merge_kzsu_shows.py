#!/usr/bin/env python3
"""
merge_kzsu_shows.py
===================

Fallback for when `build_music_db.py --refresh` can't reach the KZSU API
(for example, a workspace that blocks scripted web requests).

An agent fetches ONLY the new shows in a browser tab on zookeeper.stanford.edu,
saves them as a JSON list, and this script merges them into the raw file:

    data/raw/kzsu/playlists_dj1428_raw.json

USAGE:
    python3 scripts/merge_kzsu_shows.py data/raw/kzsu/new_shows.json

Input format: a list in the same shape the API returns, for example
    [{"type": "show", "id": "58240",
      "attributes": {"name": "The Library", "date": "2026-10-01", "time": "1800-2000",
                     "airname": "DJ Stace", "rebroadcast": false,
                     "events": [{"type": "spin", "artist": "...", "track": "...",
                                 "album": "...", "label": "...", "created": "18:03:10"}]}}]

Shows are matched by "id". A new copy of an existing show replaces the old one
(playlists can be edited after air). Nothing is ever deleted.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "kzsu" / "playlists_dj1428_raw.json"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    new = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if isinstance(new, dict):                  # allow {"data": [...]} too
        new = new.get("data", [])
    raw = json.loads(RAW.read_text())

    # Index existing shows by id so we can replace or append.
    pos = {str(pl["id"]): i for i, pl in enumerate(raw)}
    added = replaced = 0
    for pl in new:
        if pl.get("type") != "show" or "attributes" not in pl:
            continue                            # skip anything that isn't a playlist
        pid = str(pl["id"])
        if pid in pos:
            raw[pos[pid]] = pl
            replaced += 1
        else:
            pos[pid] = len(raw)
            raw.append(pl)
            added += 1

    RAW.write_text(json.dumps(raw))
    dates = sorted(pl["attributes"].get("date") or "" for pl in raw)
    print(f"Added {added}, replaced {replaced}. {len(raw)} shows, newest {dates[-1]}.")


if __name__ == "__main__":
    main()
