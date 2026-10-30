# Bay Area shows tracker

- `bay_area_shows.csv`: working copy of the running shows sheet (next 4 to 6 months). Deployed to Drive as "Bay Area Shows" in `KZSU/Show Prep/`.
- Updated every Monday by `kzsu-bay-area-shows` (skills/kzsu-bay-area-shows/SKILL.md).
- Columns `Giveaway listed (ticket sheet)`, `Requested (x)` and `Request status` track ticket giveaways. Stace ticks `Requested (x)`; Claude fills `Request status` from the monthly ticket sheet (`data/tickets/`).
- Past shows move to `bay_area_shows_past.csv`; never delete rows.
- `plan_feed_2026-11-12.json`: upcoming shows for the Nov. 12 plan's `bay_area_shows` (that plan does not exist yet). Copy into it when it is built. Upcoming only.
- Oct. 30 run: foopee.com was blocked in the browser, so rows came from venue calendars (Bottom of the Hill, Independent, Chapel page 1, Great American Music Hall, Freight). The Guild blocked the browser. Ivy Room, Gilman, Fillmore, Regency and the Chapel's later pages need a click-through or another source. No ticket sheet exists for Nov. 2026 yet; the Oct. sheet has no overlap.
