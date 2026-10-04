#!/usr/bin/env python3
"""Convert a Markdown working file to simple HTML for upload to Google Drive.

Why: the Drive connector turns an uploaded HTML file into a Google Doc.
Usage:  python3 md_to_html.py input.md output.html
Beginner notes:
  - 'markdown' is a library that turns Markdown text into HTML.
  - The 'tables' extension handles pipe tables; 'sane_lists' keeps numbered lists numbered.
"""
import sys
import markdown

src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()          # read the Markdown file
html = markdown.markdown(text, extensions=["tables", "sane_lists"])  # convert
# Wrap in a minimal page with readable laptop-screen styling (Docs keeps basic styles).
page = f"<html><body style='font-family:Arial;font-size:11pt'>{html}</body></html>"
open(dst, "w", encoding="utf-8").write(page)          # write the HTML file
print(f"wrote {dst} ({len(page)} chars)")
