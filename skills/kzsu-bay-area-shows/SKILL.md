---
name: kzsu-bay-area-shows
description: Weekly upkeep of DJ Stace's running Bay Area shows sheet (next 4 to 6 months) for shows that overlap her playlists, taste profile and KZSU interests, with giveaway-request tracking.
---

# Bay Area shows tracker (Mondays, 9:00 a.m. PT)

Read `references/house_rules.md` first. Files: `data/shows/bay_area_shows.csv` (working copy), Drive sheet "Bay Area Shows (running tracker)" in the KZSU folder (id in `data/drive_registry.json` key `bay_area_shows_sheet`), ticket sheets `data/tickets/ticket_giveaways_<yyyy-mm>.csv`.

1. Harvest the sheet first. Read it with the Sheets API. Keep her ticks in `Requested (x)` and any notes she wrote.
2. Sources, in order: foopee.com the-list (all dates, text pages), venue calendars (Bottom of the Hill, Chapel, Independent, Fillmore, Great American Music Hall, Regency, Warfield, Fox, Ritz, Ivy Room, Freight, Guild, Cornerstone), Songkick or Bandsintown pages for artists in `config/taste_profile.json` top 150 and the Weekly Playlist. If foopee.com is blocked in the browser, say so in the run note and use venue calendars; do not bypass the block.
3. Keep a row when the act is in the taste profile, in a current YTM playlist, a new-release artist, or fits `config/show_focus.json` (punk and post-punk first). Cap each run at about 40 new rows; drop duplicates by date, venue and act.
4. Window: today through 6 months. Move rows with a past date to `data/shows/bay_area_shows_past.csv`; never delete.
5. Giveaways: match each row against the monthly ticket sheets. Fill `Giveaway listed (ticket sheet)` with the DJ names and give-by date. Where Stace is listed, set `Request status` to "Listed with Stace". When she ticks `Requested (x)`, set `Request status` to "Requested" and add the date. When the ticket sheet marks it won or given away, set "Confirmed" or "Given away".
6. Patch the Drive sheet in place (insert and update rows; do not redeploy, so the link and ticks stay).
7. Feed the shows for the next two Thursdays into the plan's `bay_area_shows` (upcoming only, fields date, venue, act, detail, note).
8. Commit explicit paths and push.
