---
name: kzsu-new-releases-review
description: >-
  Tuesday and Friday morning upkeep of DJ Stace's YouTube Music playlist "New Releases for Review" for "The Library" on KZSU 90.1 FM. Holds new singles and lead tracks (from the last two weeks) that fit her taste profile, favorite bands, labels and genres. Newest on top. A track Claude added drops off 14 days after it was added, or sooner if Stace deletes it. Reads her deletions as "not interested now" (60-day cool-off), never removes tracks she added herself, FCC-screens every track and keeps a ledger. Use on the Tue/Fri 8:20 a.m. run, or whenever Stace asks to refresh, rebuild or check "New Releases for Review", even if she does not name the skill. Not for the rolling Weekly Playlist (kzsu-weekly-playlist) or the show plan (kzsu-weekly-recon).
---

# KZSU New Releases for Review

Read `references/house_rules.md` and `config/playlists.json` first. The playlist is `new_releases_review` in that file. If its `id` is null, create it (steps below) and save the id.

## What the list is

- A short, current review shelf: new singles, or the lead track of a new album, from artists, labels and genres in her taste profile.
- One track per release. The newest tracks sit at the top.
- Size: usually 15 to 30 tracks. Cap at 40. If more qualify, keep the highest fit and say so in the notes.
- A track stays 14 days from the day Claude added it (not from the release date), or until Stace deletes it, whichever is first.

## Rules

- **Exception to the "never remove" rule.** This is the only playlist where Claude removes tracks, and only tracks Claude added whose 14 days are up. Never remove a track Stace added.
- **Her deletes are signals.** A track missing from the playlist before its expiry date means she deleted it. Log it in `data/daily/feedback.json` "removed" with date, artist, title, videoId, `cooloff_until` (+60 days) and increment `artist_removals`. Never re-add it. Downweight an artist only after 3 removals.
- **Her adds are signals.** A track in the playlist that is not in the ledger is hers. Log it in "added_by_stace", mark it `owner: "stace"` in the ledger, and never expire it. Use its artist, label and RIYL neighbors as positive signals.
- **Cool-off.** Skip anything in cool-off (`feedback.json` removed) and anything she deleted from Weekly, Air Order or Next Show.
- **YTM only.** music.youtube.com. Never youtube.com.
- **Read-only:** "DJ Stace - Next Show", Air Order, Weekly Playlist. Never email.
- **Write limits and route.** Use the signed-in built-in browser. Reads go through the page's `browse` and `search` calls (`references/house_rules.md`, "YTM write limits"). Do not build auth headers from cookies. Add and remove with the row menus (Action menu > Save to playlist, Action menu > Remove from playlist). Verify by reading the playlist back. If YTM refuses writes, queue them in `data/daily/pending_ytm_writes.json` and say so.
- **Overlap.** The 6:30 a.m. sweeps and the 7:07 a.m. mail check can run late. Check `git status` and file mtimes before writing shared files. Commit only your own paths, never `git add -A`. Do not overwrite `data/daily/snapshots/*` that another run wrote.
- Pre-flight: open music.youtube.com/library. If YTM is signed out, write `outputs/health/<date>.md` and stop.

## Files

- Ledger: `data/new_releases_review/ledger.json`. One entry per track Claude added: `videoId, artist, title, album, label, released, added, expires (added + 14 days), bucket, fit, fcc_status, fcc_note, source, status`. `status` is `active`, `expired`, `deleted_by_stace` or `stace_added`.
- Notes: `outputs/new_releases_review/<date>.md`. What changed, with links, label, release date, FCC flags, fit reason.
- Log in `data/daily/feedback.json` as above. Snapshot the playlist in `data/daily/snapshots/<playlistId>.json` after each run.

## Steps

1. **Pre-flight and read.** Read the playlist through `browse` (follow continuation tokens; the page renders only 100 rows). Compare with the ledger.
   - Active ledger tracks missing from the playlist: Stace deleted them. Log and mark `deleted_by_stace`.
   - Playlist tracks not in the ledger: Stace added them. Log and mark `stace_added`.
2. **Expire.** For ledger entries with `status: active` and `expires` on or before today, remove them from the playlist and mark `expired`. Confirm the playlist count by reload. Removals can fail silently, so re-run until the count matches.
3. **Find candidates.** Window: released, or first single out, from 14 days before today through today.
   - Reuse the day's sweep output first: `data/daily/<today>.json` and `outputs/weekly/*.md` from `kzsu-tue-releases` and `kzsu-fri-releases`.
   - Then scan Stereogum (new music and best songs of the week), Pitchfork, Brooklyn Vegan, The Indy Review New Music Friday, Bandcamp Daily, and label pages in `config/release_watchlist.json`. Use `data/releases/upcoming_releases.csv` for fit scores.
   - Fit test (any one): artist in `config/taste_profile.json` or `config/show_focus.json`; label in the watchlist or her top labels; genre in her lane (indie rock, punk and post-punk, garage, psych, alt-country and folk rock, art pop, shoegaze); on her Weekly or Next Show lists.
   - Take the single, or the lead track of an album. One track per release. Never guess a date: two sources, or mark "(verify)".
4. **FCC screen** every pick with `kzsu-fcc-lyrics-check`. Scripted lyric APIs return 403 in the sandbox, so screen from a genius.com tab (`fetch('/api/search/song?q=...')`, then the lyrics page, count words with a regex, keep counts only). FCC and UNVERIFIED tracks stay on the list, flagged in the notes with the exact word, count and section. This playlist is for review, not air.
5. **Add.** Playlist Sort must be "Newest first" so a save lands on top. Add in ascending release order (oldest first), so the newest release ends up on top. Wait for the saved toast between adds. Skip duplicates. Reload and confirm count, order and videoIds.
6. **Record.** Update the ledger, snapshot, notes and `feedback.json`. Refresh `config/playlists.json` `last_refresh`.
7. **Commit and push** with the token in `.env` (never print it), explicit paths only. Stale zero-byte `.git/*.lock` files can block commits; see `overnight-run-pitfalls` in memory for the temp-index workaround.
8. **Summary.** Her deletes and adds, expired tracks, new adds by release date, FCC flags, playlist link, anything that failed.

## First run and rebuilds

- If `id` is null: create the playlist with the title "New Releases for Review" and this description: "New singles and lead tracks from the last two weeks that fit DJ Stace's taste profile. Updated Tuesday and Friday mornings for The Library on KZSU 90.1 FM. Newest on top. Tracks drop off 14 days after they are added, or when deleted." Set Sort to "Newest first". Save the id in `config/playlists.json`. Remind Stace to set the thumbnail by hand.
- `data/new_releases_review/ledger.json` may hold a seeded `pending` list from the first build. Add those first (oldest release first), then continue with step 3.
- Do not add anything released before 14 days ago, except the seeded first build.
