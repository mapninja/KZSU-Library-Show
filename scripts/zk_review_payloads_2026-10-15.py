#!/usr/bin/env python3
"""Build Zookeeper JSON:API request bodies for the reviews DJ Stace finished the week of Oct. 12, 2026.

Reviews covered (Drive: KZSU / Staged Reviews / Review Templates, renamed and edited Oct. 12):
  - The Fall, Post Script
  - Sylvan Esso, Ow Infinity
  - Yard Act, You're Gonna Need A Little Music

What this does (and does NOT do)
--------------------------------
- Writes one JSON file per request into outputs/zookeeper_upload/2026-10-15/.
- It never talks to Zookeeper. Nothing is POSTed, PATCHed or deleted from here.
- Send the folders with scripts/zk_send_folder.py, in this order:
    1_labels_if_missing -> 2_albums -> 3_reviews
- Zookeeper's Cloudflare check blocked the browser on Oct. 15, so label IDs and album tags
  could not be looked up. Those fields hold placeholders (LABEL_ID_<name>, TAG_PENDING_<key>).
  zk_send_folder.py skips any file that still has a placeholder.
- Fill in the real IDs by running this script again:
    python3 scripts/zk_review_payloads_2026-10-15.py --labels labels.json --tags tags.json
      labels.json: {"Cog Sinister": "12345", "Psychic Hotline": "23456", "Republic Records": "3456"}
      tags.json:   {"the-fall-post-script": "1156600", ...}   (album IDs, after the albums are keyed)
"""
import argparse
import json
import re
from pathlib import Path

# Where the request files get written (relative to the repo root).
REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "outputs" / "zookeeper_upload" / "2026-10-15"
SRC_DIR = OUT_DIR / "source_docs"   # her review text, saved as exported from Google Docs

AIRNAME = "DJ Stace"          # airname string used on her past reviews
REVIEW_DATE = "2026-10-08"    # matches "Review Date: 10/8/2026" in each review body

# Labels already known in the Zookeeper label table (from the Oct. 8 run). None of this week's
# three labels were checked yet, so the table is empty here. Add IDs with --labels.
KNOWN_LABEL_IDS = {"Republic Records": "8396"}   # found in the Zookeeper label table Oct. 15

# The three albums. "lib_artist" is the library form of the artist name ("Fall, The").
# "art" is the cover image URL that Zookeeper downloads and caches.
ALBUMS = [
    {
        "key": "the-fall-post-script",
        "src": "the-fall-post-script.txt",
        "lib_artist": "Fall, The",
        "album": "Post Script",
        # The review says "Cog Sinister / Gonzo". Cog Sinister is the label; Gonzo is the
        # Cog Sinister / Gonzo catalog imprint (cat. COGGZ154). Confirm which one the library uses.
        "label": "Cog Sinister",
        "art": "https://yt3.googleusercontent.com/teuFpxaD8UYn8ShzdB23y10bfb9AnMzLkpBD2aofMJePMrhG66IdO96IPncoQhYrW-sQavM17Du9ouZccQ=w544-h544-l90-rj",
        "track_urls": {},
        "doc_id": "1jc1NXD49RnkT8jPB41AAV-1mXHZSAC2jZx3DmRxglo4",
    },
    {
        "key": "sylvan-esso-ow-infinity",
        "src": "sylvan-esso-ow-infinity.txt",
        "lib_artist": "Sylvan Esso",
        "album": "Ow \u221e",   # the infinity sign, as on Bandcamp
        "label": "Psychic Hotline",
        "art": "https://f4.bcbits.com/img/a0712120107_5.jpg",
        "track_urls": {
            1: "entertainment-coca-cola", 2: "flood-season", 3: "hot-slob", 4: "concrete-glen",
            5: "back-again", 6: "ribbon", 7: "sledge", 8: "right-to-left", 9: "good-at-pain",
            10: "jessica", 11: "on-on", 12: "plastic-sword",
        },
        "track_site": "https://sylvanesso.bandcamp.com",
        "doc_id": "12B4lfI08Vr2iXiLz21odNGV18ruXkX4OIv6fXKFq_e0",
    },
    {
        "key": "yard-act-youre-gonna-need-a-little-music",
        "src": "yard-act-youre-gonna-need-a-little-music.txt",
        "lib_artist": "Yard Act",
        "album": "You're Gonna Need A Little Music",
        "label": "Republic Records",
        "art": "https://yt3.googleusercontent.com/7VQ3nfK96QRioXgKpu_IfAwtDYRsWflcVEwCqFP8v8AEdxOsNBCbeUI9XuZt9wDDYvdliw9HNRUUeH8AlA=w544-h544-l90-rj",
        "track_urls": {},
        "doc_id": "1cc5IBkE_hzxpuhryFdH8Ak9Pj4xbOsxlo-J7ht6xL8k",
    },
]

# Matches one track line: "7. ***** Title 03:12 - notes". Stars and notes are optional.
TRACK_RE = re.compile(r"^(\d+)\.\s+(?:\*+\s+)?(.+?)\s+(\d{1,2}:\d{2})(?:\s*-.*|\s*\.?\s*)$")


def clean_review(raw):
    """Turn the Google Docs Markdown export into the plain text Zookeeper stores.

    - Removes italic markers (*like this*), but keeps star ratings (****).
    - Removes Markdown backslash escapes (\\*, \\!, \\&).
    - Renumbers the tracklist 1, 2, 3 (the export numbers every item "1.").
    - Keeps one blank line between paragraphs and no blank lines inside the tracklist.
    """
    text = raw.replace("\r\n", "\n")
    # Italic: a single * pair around text, not preceded by a backslash. Star ratings are escaped.
    text = re.sub(r"(?<![\\*])\*([^*\\\n]+)\*(?!\*)", r"\1", text)
    # Un-escape Markdown characters.
    text = re.sub(r"\\([*!&_#.()\[\]-])", r"\1", text)
    out, n, in_tracks = [], 0, False
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("Tracklist:"):
            in_tracks = True
        if in_tracks and re.match(r"^\d+\.\s", line):
            n += 1
            line = "%d. %s" % (n, re.sub(r"^\d+\.\s+", "", line))
        out.append(line)
    # Collapse blank-line runs. Inside the tracklist, drop blanks entirely.
    final, started = [], False
    for line in out:
        if line.startswith("Tracklist:"):
            started = True
            final.append(line)
            final.append("")
            continue
        if not line:
            if started:
                continue
            if final and final[-1] == "":
                continue
        final.append(line)
    return "\n".join(final).strip() + "\n"


def parse_tracks(body, album):
    """Pull seq, title and hh:mm:ss out of the Tracklist section of a review."""
    tracks, in_list = [], False
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("Tracklist:"):
            in_list = True
            continue
        m = TRACK_RE.match(line) if in_list else None
        if not m:
            continue
        seq, title, mmss = m.groups()
        minutes, seconds = mmss.split(":")
        url = ""
        slug = album["track_urls"].get(int(seq))
        if slug:
            url = "%s/track/%s" % (album["track_site"], slug)
        tracks.append({"seq": int(seq), "track": title.strip(),
                       "duration": "00:%02d:%02d" % (int(minutes), int(seconds)), "url": url})
    return tracks


def album_payload(album, body, label_ids):
    """POST /api/v1/album body. The label is linked by ID so Zookeeper never makes a duplicate."""
    label_id = KNOWN_LABEL_IDS.get(album["label"]) or label_ids.get(album["label"]) \
        or "LABEL_ID_" + album["label"]
    attributes = {
        "artist": album["lib_artist"],
        "album": album["album"],
        "category": "General",        # all prior reviewed albums use General
        "medium": "CD",               # CONFIRM: her new releases are digital
        "size": "Full",
        "location": "Pending Appr",   # keyed albums with reviews wait here for approval
        "bin": None,
        "coll": False,
        "tracks": parse_tracks(body, album),
        "albumart": album["art"],
    }
    return {"data": [{"type": "album", "attributes": attributes,
                      "relationships": {"label": {"data": {"type": "label", "id": label_id}}}}]}


# Contact details for the new labels, checked Oct. 15, 2026 on each label's own site.
# Only facts the label publishes are filled in. A missing key means "not published".
# Field names and types match what GET /api/v1/label returns (international is a bool).
LABEL_DETAILS = {
    # Source: gonzomultimedia.co.uk contact page (Cog Sinister is one of Gonzo Multimedia's labels,
    # catalog COGGZ). The only published contact is a customer-service email for orders and products,
    # not a music-submission address. No postal address is published. UK company.
    "Cog Sinister": {
        "email": "customerservicesgonzo@gmail.com", "international": True,
        "url": "https://www.gonzomultimedia.co.uk/labels/categories/cog-sinister",
    },
    # Source: psychic-hotline.net/about. Artist-run label in Durham, N.C. (Sylvan Esso's Amelia Meath and
    # Nick Sanborn with manager Martin Anderson). General email and toll-free line are published; no
    # demos accepted. No mailing address is published (the Holland Street address is the Mailroom
    # pop-up shop, not the label's office). The licensing email goes to Ato Records, so it is not used.
    # 1-888-PSY-HTLN dials as 1-888-779-4856.
    "Psychic Hotline": {
        "city": "Durham", "state": "NC", "phone": "1-888-779-4856",
        "email": "info@psychic-hotline.net", "url": "https://psychic-hotline.net/",
    },
}


def label_payload(name):
    """POST /api/v1/label body. Only needed if a label is missing from the Zookeeper table."""
    attributes = {"name": name}
    attributes.update(LABEL_DETAILS.get(name, {}))   # add the published contact details
    return {"data": [{"type": "label", "attributes": attributes}]}


def review_payload(album, body, tags):
    """POST /api/v1/review body. Zookeeper stores line breaks as \\r\\n."""
    tag = tags.get(album["key"], "TAG_PENDING_" + album["key"])
    return {"data": {"type": "review",
                     "attributes": {"airname": AIRNAME, "published": True, "date": REVIEW_DATE,
                                    "review": body.replace("\n", "\r\n").rstrip("\r\n")},
                     "relationships": {"album": {"data": {"type": "album", "id": tag}}}}}


def write_one(folder, name, body):
    """Write ONE request body to its own file. The file holds only what gets sent."""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tags", help="JSON file: album key -> Zookeeper album ID")
    parser.add_argument("--labels", help="JSON file: label name -> Zookeeper label ID")
    args = parser.parse_args()
    tags = json.loads(Path(args.tags).read_text()) if args.tags else {}
    label_ids = json.loads(Path(args.labels).read_text()) if args.labels else {}

    for n, album in enumerate(ALBUMS, start=1):
        body = clean_review((SRC_DIR / album["src"]).read_text())
        # 1. Label, only if it is not in the table and has no ID yet.
        if album["label"] not in KNOWN_LABEL_IDS and album["label"] not in label_ids:
            write_one(OUT_DIR / "1_labels_if_missing", "%02d_%s.json" % (n, re.sub(r"[^a-z0-9]+", "-", album["label"].lower()).strip("-")),
                      label_payload(album["label"]))
        # 2. Album record.
        write_one(OUT_DIR / "2_albums", "%02d_%s.json" % (n, album["key"]), album_payload(album, body, label_ids))
        # 3. Review.
        write_one(OUT_DIR / "3_reviews", "%02d_%s.json" % (n, album["key"]), review_payload(album, body, tags))
    print("Wrote request files to", OUT_DIR)


if __name__ == "__main__":
    main()
