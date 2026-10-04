---
name: kzsu-specialty-show
description: >-
  Builds suggestion playlists for seasonal and topical shows (Halloween, Thanksgiving, Christmas, New Year's Eve, Valentine's and similar) for DJ Stace's "The Library" on KZSU 90.1 FM. Each is 2.5 hours of music in YouTube Music drawn from her taste profile, with FCC-clean picks and overlap with Today in Music and new releases when possible. Looks six weeks ahead on the first of each month. Use on the monthly run, or whenever Stace asks for a holiday, themed or special show playlist, even if she does not name the skill.
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
