#!/usr/bin/env python3
"""
review_requests.py
==================

Reads and updates the "Make review templates" checklist in a
staged_priority_<date>.md file.

Each checklist line looks like this:

    - [ ] Guided By Voices | Crawlspace of the Pantheon | GBV Inc.
    - [x] Widowspeak | Roses | Captured Tracks
    - [x] Sluice | Companion | Mtn. Lauren | template: outputs/reviews/sluice-companion.md

- "[ ]" means not requested. "[x]" means Stace wants a template.
- A 4th field, "template: ...", means the template is done.

USAGE:
    # List ticked albums that still need a template (JSON on stdout)
    python3 scripts/review_requests.py pending outputs/reviews/staged_priority_2026-10-05.md

    # Record that a template is finished (edits the file in place)
    python3 scripts/review_requests.py done outputs/reviews/staged_priority_2026-10-05.md \
        "Widowspeak" "Roses" "https://drive.google.com/file/d/..."

Other scripts import parse_checklist(), checklist_line() and item_key().
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

# "- [ ]" or "- [x]" (also "[X]"), then 3 or 4 fields split by " | ".
LINE = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+(.+)$")


def item_key(artist: str, title: str) -> str:
    """Loose match key: lowercase, no accents, no punctuation, no leading 'the'."""
    def norm(s):
        s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
        s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
        return re.sub(r"^the\s+", "", " ".join(s.split()))
    return norm(artist) + "|" + norm(title)


def checklist_line(artist, title, label, checked=False, template=""):
    """Build one checklist line. Pipes inside names are swapped for slashes."""
    clean = lambda s: str(s or "").replace("|", "/").strip()
    parts = [clean(artist), clean(title), clean(label) or "label unknown"]
    if template:
        parts.append("template: " + clean(template))
    return f"- [{'x' if checked else ' '}] " + " | ".join(parts)


def parse_checklist(text: str) -> list:
    """Return every checklist item as a dict. Lines that don't fit are skipped."""
    items, in_section = [], False
    for n, line in enumerate(text.splitlines()):
        if line.startswith("## "):
            in_section = line.strip().lower().startswith("## make review templates")
            continue
        m = LINE.match(line)
        if not (in_section and m):
            continue
        fields = [f.strip() for f in m.group(2).split(" | ")]
        if len(fields) < 2:
            continue
        template = ""
        if len(fields) >= 4 and fields[3].lower().startswith("template:"):
            template = fields[3].split(":", 1)[1].strip()
        items.append({"line": n, "checked": m.group(1).lower() == "x",
                      "artist": fields[0], "title": fields[1],
                      "label": fields[2] if len(fields) > 2 else "",
                      "template": template})
    return items


def pending(text: str) -> list:
    """Ticked items without a finished template."""
    return [i for i in parse_checklist(text) if i["checked"] and not i["template"]]


def mark_done(text: str, artist: str, title: str, template: str) -> str:
    """Return the file text with this item's line updated to include the template link."""
    lines = text.splitlines()
    key = item_key(artist, title)
    for item in parse_checklist(text):
        if item_key(item["artist"], item["title"]) == key:
            lines[item["line"]] = checklist_line(item["artist"], item["title"], item["label"],
                                                 checked=True, template=template)
            return "\n".join(lines) + "\n"
    raise SystemExit(f"Not in the checklist: {artist} - {title}")


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in {"pending", "done"}:
        raise SystemExit(__doc__)
    path = Path(sys.argv[2])
    text = path.read_text(encoding="utf-8")
    if sys.argv[1] == "pending":
        print(json.dumps(pending(text), indent=1, ensure_ascii=False))
    else:
        artist, title, template = sys.argv[3:6]
        path.write_text(mark_done(text, artist, title, template), encoding="utf-8")
        print(f"Marked done: {artist} - {title}")


if __name__ == "__main__":
    main()
