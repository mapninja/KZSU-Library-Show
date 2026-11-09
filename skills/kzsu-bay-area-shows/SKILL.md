---
name: kzsu-bay-area-shows
description: Weekly upkeep of DJ Stace's running Bay Area shows sheet (every date the sources list, no cap) for shows that overlap her playlists, taste profile and KZSU interests, with giveaway-request tracking.
---

# Bay Area shows tracker (Mondays, 9:00 a.m. PT)

Read `references/house_rules.md` first. Files: `data/shows/bay_area_shows.csv` (working copy), Drive sheet "Bay Area Shows (running tracker)" in the KZSU folder (id in `data/drive_registry.json` key `bay_area_shows_sheet`), ticket sheets `data/tickets/ticket_giveaways_<yyyy-mm>.csv`.

1. Harvest the sheet first. Read it with the Sheets API. Keep her ticks in `Requested (x)` and any notes she wrote.
2. Sources, in order: The List at `http://www.foopee.com/punk/the-list/` (use plain `http://`; read every `by-date.N.html` page through the page's own `fetch` in the browser, all dates through the last page, about Sep. of next year), venue calendars (Bottom of the Hill, Chapel, Independent, Fillmore, Great American Music Hall, Regency, Warfield, Fox, Ritz, Ivy Room, Freight, Guild, Cornerstone), Songkick or Bandsintown pages for artists in `config/taste_profile.json` top 150 and the Weekly Playlist. Venue calendars go further than The List for some rooms: click the Independent calendar forward month by month, and click through all Chapel pages (`li[data-see-ajax-page]`) and all GAMH "Load more events". If a site is blocked (the Regency returns 403), say so in the run note and do not bypass it.
3. Keep a row when the act is in the taste profile (all of it, not just the top 150), the Review Shelf, the release watchlist, a current YTM playlist, a new-release artist, or fits `config/show_focus.json` (punk and post-punk first). Match The List band names exactly after normalizing (lowercase, drop "the", drop punctuation). No cap on rows. Drop duplicates by date, venue and act.
4. Window: today through the last date any source lists. Stace asked for no 6-month cap on Nov. 9, 2026. Move rows with a past date to `data/shows/bay_area_shows_past.csv`; never delete.
5. Giveaways: match each row against the monthly ticket sheets. Fill `Giveaway listed (ticket sheet)` with the DJ names and give-by date. Where Stace is listed, set `Request status` to "Listed with Stace". When she ticks `Requested (x)`, set `Request status` to "Requested" and add the date. When the ticket sheet marks it won or given away, set "Confirmed" or "Given away".
6. Sold out and likely sell-outs (Stace, Nov. 9, 2026: she must never request those). On The List, `(sold out)` text means sold out and a standalone `$` symbol means "will probably sell out". Venue pages: a SOLD OUT button or "MORE INFO" in place of "BUY TICKETS". For every kept row set `Request status` to `SOLD OUT, do not request` or `LIKELY TO SELL OUT, do not request`, prefix `Why it fits` with `SOLD OUT.` or `LIKELY SOLD OUT.`, and add a Notes line. These flags win over giveaway statuses. Never put a sold-out show in the plan's giveaway pick.
7. Request by: Stace can request giveaway tickets until 2 weeks before the show. Fill `Request by (2 weeks before show)` with the show date minus 14 days. Use `Closed (under 2 weeks out)` when that date is before today and `n/a (sold out or likely to)` for flagged rows.
8. Patch the Drive sheet in place (insert and update rows; do not redeploy, so the link and ticks stay).
9. Feed the shows for the next two Thursdays into the plan's `bay_area_shows` (upcoming only, fields date, venue, act, detail, note).
10. Commit explicit paths and push (the local `.git` locks can block; use the temp-index method in CLAUDE.md).

Sheet note: the Drive sheet has no Notes column. Columns A to N are fixed; column O is `Request by (2 weeks before show)`. Rewrite A2:O<last row> in place after re-reading B, K and L for ticks.
