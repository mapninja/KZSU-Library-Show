---
name: kzsu-archive-playlist
description: >-
  After DJ Stace's "The Library" airs Thursday 6-8 p.m. on KZSU 90.1 FM, builds a playable YouTube Music archive playlist named "The Library Show with DJ Stace (Month d, yyyy Show)" from the official KZSU Zookeeper playlist, so on-air changes and requests are captured. Lists tracks that Zookeeper has but YouTube Music cannot find. Also feeds the next taste profile refresh. Use on the Thursday 8:30 p.m. run (retry Friday 7 a.m. if the log is incomplete), or whenever Stace asks to archive a show, even if she does not name the skill.
---

# KZSU archive playlist

Read `references/house_rules.md` and `config/playlists.json`. Pre-flight: YTM signed in.

## Steps
1. **Show date** = most recent Thursday (today if after 8 p.m.).
2. **Pull the aired playlist** from Zookeeper (airname 1428, filter by date; see `api_docs/KZSU_API/Playlists.md`). If the shell is blocked, run `fetch()` from a zookeeper.stanford.edu tab. Spin events only. Keep air order. If it has fewer than 15 tracks or looks cut off, write a note, stop, and let the Friday retry run.
3. **Compare** to the final plan: tracks played, skipped, added on the fly (requests).
4. **Create** the playlist titled `The Library Show with DJ Stace (Month d, yyyy Show)` on music.youtube.com, public, forward order. Add each track by searching and verifying artist and title. Prefer the video ID already in the plan. Reload and verify the count.
5. **Report** tracks not found on YTM, and any on-air changes.
6. **Save** `data/archive/<date>.json` (aired list, YTM ids, misses). Add the playlist ID to `config/playlists.json` under `archive` list. Commit and push.
7. **Learn:** write which planned tracks were not aired into `data/daily/feedback.json` ("not_aired") as a weak signal only.
