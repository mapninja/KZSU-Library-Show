#!/usr/bin/env python3
"""Send every JSON file in a folder to Zookeeper, building each URL from the JSON itself.

How the URL and method are chosen (read from each file's "data" object):
  - data has an "id"      -> PATCH  https://zookeeper.stanford.edu/api/v1/<type>/<id>
  - data has no "id"      -> POST   https://zookeeper.stanford.edu/api/v1/<type>
where <type> is the "type" value in the file: "album", "label" or "review".
"data" can be an object or a one-item list. Both work.

Safety
------
  - Default is a DRY RUN. It prints each method and URL and sends nothing.
  - Add --send to really send.
  - Files that still hold a placeholder (TAG_PENDING or LABEL_ID) are skipped.
  - It stops at the first error, so one bad file does not turn into 30 bad requests.
  - The API key is read from the environment or the repo .env file (KZSU_LIBRARY_API_KEY).
    It is never printed or logged.

Examples (run from the repo folder)
-----------------------------------
    # 1. See what would happen:
    python3 scripts/zk_send_folder.py outputs/zookeeper_upload/2026-10-08/5_location_pending_appr

    # 2. Send just the first file as a test:
    python3 scripts/zk_send_folder.py outputs/zookeeper_upload/2026-10-08/5_location_pending_appr --send --limit 1

    # 3. Send them all:
    python3 scripts/zk_send_folder.py outputs/zookeeper_upload/2026-10-08/5_location_pending_appr --send

    # If PATCH says "must specify id", try wrapping "data" in a list:
    python3 scripts/zk_send_folder.py <folder> --send --limit 1 --wrap-list
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
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


def craft_request(body, wrap_list):
    """Return (method, url, bytes_to_send) for one parsed JSON body."""
    data = body["data"]
    # "data" may be a one-item list; look inside it to find the type and id.
    item = data[0] if isinstance(data, list) else data
    kind = item["type"]                      # album, label or review
    item_id = item.get("id")                 # only present for updates (PATCH)

    if item_id:
        method = "PATCH"
        url = "%s/api/v1/%s/%s" % (BASE_URL, kind, item_id)
    else:
        method = "POST"
        url = "%s/api/v1/%s" % (BASE_URL, kind)

    # Optional: send "data" as a one-item list (POST bodies already use a list).
    if wrap_list and not isinstance(data, list):
        body = dict(body, data=[data])
    return method, url, json.dumps(body).encode("utf-8")


def send(method, url, payload, api_key):
    """Send one request. Retries a few times if Zookeeper says 429 (too many requests)."""
    headers = {
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json",
        "X-APIKEY": api_key,
    }
    for attempt in range(4):
        request = urllib.request.Request(url, data=payload, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, response.read().decode("utf-8")
        except urllib.error.HTTPError as err:
            text = err.read().decode("utf-8")
            if err.code == 429 and attempt < 3:
                wait = 20 * (attempt + 1)
                print("   429 too many requests, waiting %d s and retrying" % wait)
                time.sleep(wait)
                continue
            return err.code, text
    return 429, "gave up after retries"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", help="folder of .json request bodies")
    parser.add_argument("--send", action="store_true", help="really send (default is a dry run)")
    parser.add_argument("--limit", type=int, default=0, help="only handle the first N files (0 = all)")
    parser.add_argument("--delay", type=float, default=3.0, help="seconds to wait between requests")
    parser.add_argument("--wrap-list", action="store_true", help="wrap a plain-object data in a list")
    args = parser.parse_args()

    folder = Path(args.folder)
    files = sorted(folder.glob("*.json"))
    if args.limit:
        files = files[:args.limit]
    if not files:
        raise SystemExit("No .json files in " + str(folder))

    api_key = None
    if args.send:
        api_key = get_api_key()
        if not api_key:
            raise SystemExit("No KZSU_LIBRARY_API_KEY found in the environment or .env")

    log = []                                  # one line per file, saved next to the files
    for number, path in enumerate(files, start=1):
        text = path.read_text()
        # Never send a file that still has a fill-in-later placeholder.
        if "TAG_PENDING" in text or "LABEL_ID" in text:
            print("%2d. SKIP (placeholder) %s" % (number, path.name))
            log.append("SKIP %s" % path.name)
            continue

        method, url, payload = craft_request(json.loads(text), args.wrap_list)
        print("%2d. %s %s   <- %s" % (number, method, url, path.name))

        if not args.send:
            continue

        status, answer = send(method, url, payload, api_key)
        print("    status", status)
        log.append("%s %s %s %s" % (status, method, url, path.name))
        if status >= 300:
            # Show the server's explanation, then stop.
            print("    ", answer[:600])
            log.append(answer[:600])
            print("Stopped at the first error. Fix it, then re-run (finished files will re-send, so move them out first).")
            break
        time.sleep(args.delay)

    if args.send:
        (folder / "_send_log.txt").write_text("\n".join(log) + "\n")
        print("Log written to", folder / "_send_log.txt")
    else:
        print("Dry run only. Add --send to send.")


if __name__ == "__main__":
    main()
