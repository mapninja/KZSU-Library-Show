# Thursday-night draft run: Fri. Nov. 13, 2026 (kzsu-thu-night-draft)

Status: done. Plan and Air Order are ready for Stace to edit.

## Target
- Show date: Thu. Nov. 19, 2026 (next Thursday after today). The run fired Friday afternoon, not Thursday night.
- Plan: `data/recon/2026-11-19/working_playlist.json`. 37 tracks, 2:26 of music (Hour 1 1:11, Hour 2 1:14).

## Pre-flight
- YTM signed in (`LOGGED_IN` true); video paused and muted, no audio played.
- Zookeeper signed in (API reads worked).
- Repo and Drive (`KZSU`) connected.
- Nov. 12 show did not air: Zookeeper shows Zootopia (Team KZSU, 58672) in the 6 to 8 p.m. slot and no log under airname 1428. Same finding as `outputs/health/2026-11-13.md`.
- No Nov. 12 finals exist in Drive (no script, CSV or Notes Sheet), so nothing to move to `Archive/2026/11-12`.
- The Nov. 12 plan was carried over, not rebuilt.

## What changed from the Nov. 12 plan
- New: Wavves "Layover in Dublin" (Cherry Soda, Nov. 13), Land of Talk "4:44" (LASTS, Saddle Creek, Nov. 13).
- Triple Shot: Kim Deal (Pixies, The Breeders, solo), tied to Live at the Barbican (4AD, Nov. 13). Neil Young pick dropped (birthday passed, never aired). History file notes it.
- History set: Petty and Cohen kept a week late; Led Zeppelin dropped; Beastie Boys "Fight for Your Right" added (Licensed to Ill, Nov. 15, 1986, one source, verify).
- Bay Area: rebuilt from `data/shows/plan_feed_2026-11-19.json`. Jon Spencer dropped (Nov. 13 show passed). The English Beat added (Napa Nov. 20, Berkeley Nov. 23).
- Trimmed for length: Editors, Nick Cave, Twisted Teens "I Spend My Time Crying" (moved to bench).

## Stace's Air Order edits (read Nov. 13)
- Cut: Chastity Belt, 2nd Grade, Clash "Complete Control", Sennen, The Big Moon, Gilla Band. Logged as 60-day cool-offs (to Jan. 12, 2027) per the house rule. She can reclassify them as length cuts.
- Added: Television "Marquee Moon" (10:39), The Cult "She Sells Sanctuary". Both placed in Set 2. Car Seat Headrest (earlier add) stays last, outside the plan.

## Air Order
- Deltas only: 8 removed, 7 added, 12 moves in one call each. Fresh read: 38 rows, equals plan order plus Car Seat Headrest.

## FCC
- Wavves "Layover in Dublin": UNVERIFIED (no lyrics on Genius).
- Land of Talk, Pixies, The Breeders, Kim Deal, Beastie Boys, The English Beat, Television, The Cult: CLEAN (Genius, no hits).
- Still UNVERIFIED from earlier plans: THAO "Show Me", Dread Spectre Council "Spiderette".

## Zookeeper metadata
- Library tag and label checked for every new track. Compilation-only hits (Pixies, Beastie Boys, The Cult) have a blank tag, original label per the label table, and `zk_alt`.
- Wavves: I Surrender Records is not in the label table; shown as "(verify)".

## Needs Stace
- UNKLE giveaway request is due Mon. Nov. 16 (two weeks before Nov. 30).
- Confirm the six cuts are cool-offs or length cuts.
- Notes Sheet and Working Show Script were not built (the Thursday 8 a.m. draft run does that).
- Playlist thumbnails: no new playlists this run.
- Alreadyheard.com returned a Cloudflare page; not retried. Pitchfork not tried.
- Git: stale `.git/index.lock`, `.git/HEAD.lock` and `.git/next-index-8.lock` (Nov. 8) still block the local checkout. Delete them from a terminal.
