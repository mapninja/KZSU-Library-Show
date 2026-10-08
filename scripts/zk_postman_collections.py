#!/usr/bin/env python3
"""Bundle the one-file-per-request JSON bodies into three Postman collections.

Reads   outputs/zookeeper_upload/<date>/1_labels, 2_albums, 3_reviews
Writes  outputs/zookeeper_upload/<date>/postman_1_labels.json, postman_2_albums.json,
        postman_3_reviews.json

Each collection has one request per body file, in posting order. The API key is a
Postman variable ({{zk_apikey}}), so no key is stored in these files.
Run again after zk_review_payloads.py refills labels or tags.

Usage: python3 scripts/zk_postman_collections.py [YYYY-MM-DD]
"""
import json
import sys
from pathlib import Path

DATE = sys.argv[1] if len(sys.argv) > 1 else "2026-10-08"
BASE = Path(__file__).resolve().parent.parent / "outputs" / "zookeeper_upload" / DATE
HOST = "https://zookeeper.stanford.edu"

# Headers every Zookeeper write needs.
HEADERS = [
    {"key": "X-APIKEY", "value": "{{zk_apikey}}"},
    {"key": "Content-Type", "value": "application/vnd.api+json"},
    {"key": "Accept", "value": "application/vnd.api+json"},
]


def make_request(name, method, path, body_text):
    """Build one Postman request item. `path` looks like 'api/v1/label'."""
    return {
        "name": name,
        "request": {
            "method": method,
            "header": HEADERS,
            "body": {"mode": "raw", "raw": body_text},
            "url": {"raw": "%s/%s" % (HOST, path), "protocol": "https",
                    "host": ["zookeeper", "stanford", "edu"], "path": path.split("/")},
        },
    }


def build(folder, title, post_path):
    """One collection per folder. Files named PATCH_<id>_*.json become PATCH requests."""
    items = []
    for f in sorted((BASE / folder).glob("*.json")):
        text = f.read_text()
        if f.name.startswith("PATCH_"):
            album_id = f.name.split("_")[1]
            items.append(make_request("PATCH " + f.stem, "PATCH", "api/v1/album/" + album_id, text))
        else:
            items.append(make_request("POST " + f.stem, "POST", post_path, text))
    collection = {
        "info": {"name": title,
                 "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
        "item": items,
        "variable": [{"key": "zk_apikey", "value": ""}],
    }
    return collection


for folder, title, path, out in [
    ("1_labels", "Zookeeper 1: new labels (POST api/v1/label)", "api/v1/label", "postman_1_labels.json"),
    ("2_albums", "Zookeeper 2: albums (POST api/v1/album, one PATCH)", "api/v1/album", "postman_2_albums.json"),
    ("3_reviews", "Zookeeper 3: reviews (POST api/v1/review)", "api/v1/review", "postman_3_reviews.json"),
]:
    c = build(folder, title, path)
    (BASE / out).write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n")
    print(out, len(c["item"]), "requests")
