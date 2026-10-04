#!/usr/bin/env python3
"""Pull KZSU Current Adds (A-File) from the Zookeeper API and save them as JSON.

Run this on your Mac (not in Claude's sandbox), from the repo root:
    python3 scripts/zk_current_adds.py

What it does, step by step:
  1. Reads your API key from the .env file (KZSU_LIBRARY_API_KEY). The key never
     leaves your Mac except in the request to zookeeper.stanford.edu.
  2. Asks the API for albums whose library location is the A-File (current adds).
  3. Looks up each album's label name.
  4. Writes data/zookeeper/current_adds_<today>.json for the Monday intake run.

Only the Python standard library is used, so there is nothing to install.
"""
import datetime
import json
import os
import pathlib
import time
import urllib.parse
import urllib.request

BASE = "https://zookeeper.stanford.edu/api/v1"
REPO = pathlib.Path(__file__).resolve().parent.parent


def read_key():
    """Find KZSU_LIBRARY_API_KEY in .env (lines look like NAME=value)."""
    for line in (REPO / ".env").read_text().splitlines():
        if line.startswith("KZSU_LIBRARY_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("KZSU_LIBRARY_API_KEY not found in .env")


def get(path, key):
    """GET one API URL and return the parsed JSON. Waits 1 second to be polite."""
    req = urllib.request.Request(
        BASE + path,
        headers={"Accept": "application/vnd.api+json", "X-APIKEY": key},
    )
    time.sleep(1)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main():
    key = read_key()
    albums, labels = [], {}
    # Try the common spellings of the A-File location; stop at the first that returns data.
    for loc in ("A-File", "A File", "AFile"):
        path = "/album?filter[location]=" + urllib.parse.quote(loc) + "&page[size]=100"
        while path:
            data = get(path, key)
            albums += data.get("data", [])
            nxt = (data.get("links") or {}).get("next")
            # The next link is a full URL; keep only the part after /api/v1
            path = nxt.split("/api/v1", 1)[1] if nxt else None
        if albums:
            break
    rows = []
    for a in albums:
        attr = a["attributes"]
        lid = (((a.get("relationships") or {}).get("label") or {}).get("data") or {}).get("id")
        if lid and lid not in labels:  # look up each label once
            labels[lid] = get("/label/" + lid, key)["data"]["attributes"]["name"]
        rows.append({
            "tag": a["id"],
            "artist": attr.get("artist"),
            "album": attr.get("album"),
            "label": labels.get(lid, ""),
            "category": attr.get("category"),
            "location": attr.get("location"),
            "updated": attr.get("updated"),
            "tracks": [t.get("track") for t in attr.get("tracks", [])],
        })
    out = REPO / "data" / "zookeeper" / f"current_adds_{datetime.date.today()}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"pulled": str(datetime.datetime.now()), "count": len(rows), "albums": rows}, indent=1))
    print(f"Saved {len(rows)} current adds to {out}")
    if not rows:
        print("No albums came back. The A-File location name may differ; tell Claude what Zookeeper calls it.")


if __name__ == "__main__":
    main()
