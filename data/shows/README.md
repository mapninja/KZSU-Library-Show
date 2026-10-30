# Bay Area shows tracker

- `bay_area_shows.csv`: working copy of the running shows sheet (next 4 to 6 months). Deployed to Drive as "Bay Area Shows" in `KZSU/Show Prep/`.
- Updated every Monday by `kzsu-bay-area-shows` (skills/kzsu-bay-area-shows/SKILL.md).
- Columns `Giveaway listed (ticket sheet)`, `Requested (x)` and `Request status` track ticket giveaways. Stace ticks `Requested (x)`; Claude fills `Request status` from the monthly ticket sheet (`data/tickets/`).
- Past shows move to `bay_area_shows_past.csv`; never delete rows.
