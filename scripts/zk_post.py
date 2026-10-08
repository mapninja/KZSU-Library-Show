#!/usr/bin/env python3
"""Post ONE album or review payload to Zookeeper. Run this on your own Mac.

Safety
------
- Default is a dry run: it prints what it WOULD send and sends nothing.
- Add --send to really POST.
- It posts exactly one entry per run (chosen by --key), never the whole file.
- The API key is read from your environment or the repo's .env file
  (KZSU_LIBRARY_API_KEY). It is never printed.

Examples
--------
    # Look at what would be sent for the Blame the Clown album:
    python3 scripts/zk_post.py albums twisted-teens-blame-the-clown

    # Really post it:
    python3 scripts/zk_post.py albums twisted-teens-blame-the-clown --send

    # Later, post its review (fill in the album tag first, see zk_review_payloads.py --tags):
    python3 scripts/zk_post.py reviews twisted-teens-blame-the-clown --send
"""
import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UPLOAD_DIR = REPO / "outputs" / "zookeeper_upload" / "2026-10-06"
BASE_URL = "https://zookeeper.stanford.edu"


def get_api_key():
    """Read the key from the environment, or from the repo's .env file."""
    key = os.environ.get("KZSU_LIBRARY_API_KEY")
    env_file = REPO / ".env"
    if not key and env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("KZSU_LIBRARY_API_KEY"):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    return key


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=["albums", "reviews"], help="which file to read from")
    parser.add_argument("key", help="entry key, for example twisted-teens-blame-the-clown")
    parser.add_argument("--send", action="store_true", help="really POST (default is a dry run)")
    args = parser.parse_args()

    # Load the approved file and find the one entry we were asked for.
    file_name = "albums_for_approval.json" if args.kind == "albums" else "reviews_for_upload.json"
    entries = json.loads((UPLOAD_DIR / file_name).read_text())
    entry = next((e for e in entries if e["key"] == args.key), None)
    if entry is None:
        raise SystemExit("No entry with key " + args.key)

    body = json.dumps(entry["payload"]).encode("utf-8")
    url = BASE_URL + entry["post_to"]

    # A review whose album tag is still a placeholder must not be sent.
    if args.kind == "reviews" and "TAG_PENDING" in body.decode("utf-8"):
        raise SystemExit("Review still has a TAG_PENDING album tag. Fill in the tag first.")

    print("POST", url)
    print("Entry:", args.key, "| body bytes:", len(body))
    if not args.send:
        print("Dry run only. Add --send to post.")
        return

    api_key = get_api_key()
    if not api_key:
        raise SystemExit("No KZSU_LIBRARY_API_KEY found in the environment or .env")

    request = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json",
        "X-APIKEY": api_key,
    })
    try:
        with urllib.request.urlopen(request) as response:
            print("Status:", response.status)
            print("Location:", response.headers.get("Location"))
            print(response.read().decode("utf-8")[:2000])
    except urllib.error.HTTPError as err:
        # Zookeeper explains failures in the response body (401 = key missing or wrong group).
        print("HTTP error:", err.code)
        print(err.read().decode("utf-8")[:2000])


if __name__ == "__main__":
    main()
