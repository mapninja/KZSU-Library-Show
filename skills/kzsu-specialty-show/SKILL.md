---
name: kzsu-specialty-show
description: >-
  Builds seasonal and topical shows (Halloween, Thanksgiving, Christmas, New Year's Eve, Valentine's and similar) for DJ Stace's "The Library" on KZSU 90.1 FM. A specialty show gets the same full package as a regular week: a 2.5 hour suggestion playlist, a plan, Air Order and Working drafts, Notes Sheet, Working and Final scripts, reversed Zookeeper CSV and archive playlist. Picks come from her taste profile, are FCC-clean, and fold in Today in Music and new releases that fit the theme. Looks six weeks ahead on the first of each month. Use on the monthly run, or whenever Stace asks for a holiday, themed or special show playlist, even if she does not name the skill.
---

# KZSU specialty shows

Read `references/house_rules.md`, `config/playlists.json`, `TASTE_PROFILE.md`.

## Calendar (Thursday shows)
2026: Halloween Thu Oct 29; Thanksgiving Thu Nov 26; Christmas Eve Thu Dec 24; New Year's Eve Thu Dec 31. 2027: Valentine's falls on Sunday Feb 14, so use Thu Feb 11. Check others (Election Day, Earth Day, Pride, 4th of July, Stanford events) each month.

## Steps
1. Find specialty shows in the next 6 weeks.
2. Build ~2.5 hours (about 40 to 45 tracks). Mix: her profile artists, covers, thematic classics, new releases and Today in Music that fit the theme. Example Halloween: Ministry "Everyday Is Halloween", an FCC-clean Misfits track.
3. FCC-screen every track via `kzsu-fcc-lyrics-check`. Radio-edit candidates go to "FCC Edit Needed".
4. Create playlist `Library Specialty: {name} {yyyy}`, public, via the browser. Save the ID to `config/playlists.json`.
5. Write `outputs/specialty/<name>-<yyyy>.md` with track notes. Copy to Drive /KZSU/Specialty/.
6. Commit and push. Summary: playlist link, runtime, FCC flags.

## Specialty shows get the full weekly pipeline (rule from Stace, Oct. 2026)

A specialty show is a regular Thursday show with a theme. It needs every artifact a normal week needs:

1. **Suggestion playlist** (2.5 hours, `Library Specialty: {name} {yyyy}`), built from her profile.
2. **Plan JSON** at `data/recon/<show date>/working_playlist.json`, `"theme": "<name>"`, sets named by theme. The Thursday-night draft for that week (`kzsu-weekly-recon`) starts from this plan instead of a blank slate. It still fills gaps from Stace's Weekly Playlist.
3. **Air Order and Working** playlists built from the plan the same way (Air Order forward, Working reversed).
4. **Notes Sheet and Working Show Script** (`kzsu-notes-sheet-and-script`), with theme talking points.
5. **Final Show Script** (Wednesday), **Zookeeper CSV** (reversed, Thursday morning) and **archive playlist** (Thursday night). The regular tasks already run these; they just use the specialty plan for that week.
6. **Bay Area shows break** and FCC callouts as usual.

### Fold in the calendar, when it fits the theme

- **Today in Music** for the show date and the week around it: anniversaries, birthdays, deaths, landmark releases whose title, subject or sound fits the theme. Example: Halloween on Oct. 29 should note what happened on Oct. 29 and Oct. 30.
- **New releases** from the previous two weeks through the show date that fit the theme (for example Ministry's final album and Queens of the Stone Age's "Where the Goth Girls At?" for Halloween).
- **Bay Area shows** with themed or covers nights (foopee.com often lists Halloween covers shows).
- Do not force a fit. Skip an item that does not suit the theme.

### Scheduling

- The monthly task builds the suggestion playlist and the plan six weeks out, and again refreshes it two weeks before the show so new releases and Today in Music are current.
- The Thursday-night draft, Wednesday final script, Thursday sync and Thursday archive tasks check `data/recon/<show date>/working_playlist.json` for a `"theme"` field and use it if present.
