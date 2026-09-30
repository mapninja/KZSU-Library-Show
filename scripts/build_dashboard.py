#!/usr/bin/env python3
"""
build_dashboard.py
==================

Makes a single-file HTML dashboard you can open in any browser:

    outputs/dashboard/index.html

It reads the template (templates/dashboard_template.html) and pastes the
JSON data (outputs/dashboard/dashboard_data.json) into it. Because the data
is inside the HTML file, the dashboard works offline and needs no server.
(Charts load Chart.js from a CDN, so charts need an internet connection.)

HOW TO RUN:
    python scripts/build_music_db.py     # refresh database + JSON
    python scripts/build_dashboard.py    # rebuild the HTML
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "dashboard_template.html"
DATA = ROOT / "outputs" / "dashboard" / "dashboard_data.json"
OUT = ROOT / "outputs" / "dashboard" / "index.html"


def main() -> None:
    html = TEMPLATE.read_text(encoding="utf-8")
    data = DATA.read_text(encoding="utf-8")
    # "</" inside JSON could end the <script> tag early; escape it to be safe.
    data = data.replace("</", "<\\/")
    OUT.write_text(html.replace("/*__DATA__*/null", data), encoding="utf-8")
    print(f"Dashboard written to {OUT} ({OUT.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
