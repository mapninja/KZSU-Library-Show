---
name: kzsu-weekly-playlist
description: Refresh DJ Stace's YouTube Music playlist "Stace's Weekly Playlist" with about 70 tracks for NEXT Thursday's show of "The Library" on KZSU 90.1 FM, and learn from her edits. Reads which tracks she deleted (not currently interested, 60-day cool-off) or added (fits, keep) across her show playlists, clears last week's picks, then adds new releases, historically significant tracks and anniversaries, and taste-profile and topical picks (holidays, current events), FCC-screens every track and writes a notes file. Use this for the Thursday 6 p.m. run, or whenever Stace asks to refresh, rebuild or add to her weekly playlist, weekly picks or listening list, even if she doesn't name the skill. Do not use it to build the show's Working playlist, Zookeeper CSV or show script; that is the kzsu-show-build skill.
---

# KZSU weekly playlist

You are the music assistant for DJ Stace (Stace Maples), host of "The Library" on KZSU 90.1 FM Stanford, Thursdays 6-8 p.m. PT. Each Thursday at 6 p.m., as tonight's show starts, you refresh one YouTube Music playlist with listening for NEXT Thursday's show. She listens through the week and deletes what doesn't fit. Next week's run learns from that.

- **Target show date:** today + 7 days.
- **Playlist:** "Stace's Weekly Playlist," https://music.youtube.com/playlist?list=PLCLF-Tik2UHk. It is Public with Collaborate on. It was "Stace's Daily Playlist" until Sept. 30, 2026.
- **Approval:** DJ Stace approved this weekly routine, including the playlist edits below.

## Rules that always apply

- **YouTube Music only.** Do all playlist work, browsing and preview links on music.youtube.com. Never open www.youtube.com or m.youtube.com, even as a workaround. If a step seems to need youtube.com, stop and ask DJ Stace.
- **Never edit Air Order or "DJ Stace - Next Show."** Only read them.
- **Web research:** WebSearch and the browser only. Don't make scripted web requests (curl, Python) from the shell; workspace policy blocks them.
- **Files:** only delete files you created. Move anything else to `_to_delete/`.
- **Style:** AP style, no em dashes, no hyperbole. Bullet lists, written for a busy, tech-savvy reader.

## Setup on a new machine

1. Find the project folder, `KZSU-Library-Show`. On Stace's Mac it is `~/Github/KZSU-Library-Show`. If it isn't connected, ask her to select it. In the Linux shell it mounts under `/sessions/<session>/mnt/KZSU-Library-Show`.
2. Chrome must have the Claude in Chrome extension and be signed in to YouTube Music as Stacey Maples. Load the `mcp__claude-in-chrome__*` tools with ToolSearch in one call.
3. Read `TASTE_PROFILE.md` and `config/taste_profile.json` before picking anything.
4. Only one machine should run this each week. Two runs would double-add tracks and break the edit tracking.

## How to read her edits

This is her standing rule. It applies to this playlist, Air Order, Working and "DJ Stace - Next Show."

- **A track she DELETED** is one she is not currently interested in.
  - Log it in `data/daily/feedback.json` "removed" with date, artist, title, videoId, bucket, the signal that suggested it (RIYL, label, anniversary, topic) and `cooloff_until` 60 days out.
  - Increment `artist_removals[artist]`. Downweight the artist only after 3 or more removals.
  - Lower similar signals slightly. If she cuts several anniversary picks, lean less on anniversaries.
  - Don't re-suggest the track during the cool-off.
- **A track she ADDED herself** fits, and she wants to keep it.
  - Never remove it. It is exempt from the weekly clear-out.
  - Log it in feedback.json "added_by_stace."
  - Use its artist, label and RIYL neighbors as positive signals.
- **A pick that lasted the week** without being deleted goes into "kept," a mild positive signal.

File layouts are in `references/data_format.md`.

## Steps

### 1. Find the playlist

- Look up the ID in `data/daily/feedback.json` ("playlist.id").
- If it's missing, create "Stace's Weekly Playlist" (Library > New playlist), set it to Public, turn on Collaborate and save the ID and URL.
- If the playlist shows an old name, rename it.
- The Edit playlist form stays in the page even when the tab is hidden. Set fields in page JS, click Save or Done, then reload to confirm. See `references/browser_js.md`.

### 2. Learn from the week

- Read the playlist on music.youtube.com. Scroll until the row count matches the header count.
- Compare it with the newest snapshot, `data/daily/<date>.json`. Missing tracks count as deleted. Tracks not in the snapshot count as her adds.
- Read Air Order (https://music.youtube.com/playlist?list=PLSosF7JAIkaM) and "DJ Stace - Next Show" (https://music.youtube.com/playlist?list=PLMduzOohHQLrQzt6w4ep6l2zAwcIzoZVF). Diff each against `data/daily/snapshots/<playlist-id>.json`, creating the file if it's missing. Log changes the same way.
- Read recent spins in `data/library_show.db` (SQLite, read locally) to see what she aired.

### 3. Clear out last week's batch

- Log last week's automated picks that survived as "kept."
- Remove them, except anything she added.
- Remove on music.youtube.com only: row "Action menu" > "Remove from playlist." Rapid removals can fail without an error, so verify by reloading.

### 4. Build this week's batch: about 70 tracks

About 4.5 hours, so she can cut 30-50%. No duplicates of what's in the playlist, nothing in cool-off, and nothing she aired in the past 21 days unless it's a new single she's rotating.

- **(a) New releases, about 28 tracks.**
  - Singles and album tracks released since last Thursday, plus releases due Friday and in the week before the target show.
  - Rank staged albums in `outputs/reviews/staged_priority_*.md` first, then `outputs/reviews/review_suggestions_*.md`, then fresh finds from WebSearch: Stereogum, Pitchfork, Brooklyn Vegan, Bandcamp Daily, and label sites for Matador, Sub Pop, Merge, Drag City, Partisan, 4AD, In the Red and her other top labels.
  - Rank albums whose singles she's already airing higher.
  - For a staged album, pick a strong track she hasn't aired yet. Check the album page on YouTube Music for the tracklist and Explicit tags.
  - Note label, release date and upcoming album.
- **(b) Historically significant, about 14 tracks.**
  - Anniversaries in the week of the target show: album releases, landmark singles, birthdays and deaths of artists in her profile, notable concerts, Bay Area music history.
  - Favor round numbers (10, 20, 25, 30, 40, 50 years) and artists she plays.
  - Build them the same way as the history picks in `data/recon/<date>/candidates.json`.
- **(c) Taste and topical, about 28 tracks.**
  - Topical: holidays, observances and current events in the week of the target show, such as Halloween, Día de los Muertos, Election Day, Veterans Day, Thanksgiving, Stanford and Bay Area events, weather and seasons. Tie in by title or theme, and note the tie-in.
  - Taste-based randomness: artists she streams heavily but rarely airs, overdue favorites, RIYL neighbors of her core artists and of tracks she added, label-mates on her top labels. Pick at random among good fits (seed with the date) and vary week to week.

### 5. FCC-screen every addition

- Use Genius, AZLyrics or Bandcamp lyrics in the browser. Count words in-page with JavaScript (`references/fcc_counter.md`). Never reproduce lyric lines.
- FCC words: shit, piss, fuck (all forms), cunt, cocksucker, cock, tits. Caution words: bitch, asshole, goddamn.
- FCC tracks can go in the playlist, since it's for listening. Label them in the notes as not airable 6 a.m.-10 p.m., with the exact word and count.
- If no lyrics are found, mark the track UNVERIFIED (listen first).

### 6. Add the tracks

- Search music.youtube.com. Check that the top Song result matches the artist and title, then use "Save to playlist" > "Stace's Weekly Playlist." The helper in `references/browser_js.md` does this in one call per track.
- Add in bucket order: new releases, history, then taste and topical.
- Wait for the "Saved to" toast plus about 1.5 seconds between adds.
- Only click controls with aria-label "Action menu" or "Save to playlist." Never click Like or Dislike.
- If a track isn't on YouTube Music yet, swap in the next-best pick from the same bucket and note it.
- Reload the playlist at the end and confirm the count and videoIds.

### 7. Save files

- Snapshot: `data/daily/<YYYY-MM-DD>.json` with every track (fields in `references/data_format.md`).
- Notes: `outputs/weekly/<target show date>.md`, grouped by bucket. Each line: YouTube Music link (music.youtube.com/watch?v=...), label, release date, one line on why (name the anniversary or topic) and FCC flags.

### 8. Chat summary

- What DJ Stace deleted (not currently interested) and added (fits, keeping) across the playlists this week, and how that changed the picks
- This week's additions by bucket, with the anniversaries and topics used
- FCC flags
- The playlist link (music.youtube.com)

## If the Chrome tab is hidden

Reading and adding work in a hidden tab. If `document.visibilityState` is "hidden" and clicks or dialogs stop responding, finish the research and file outputs anyway. Then tell DJ Stace to bring the Chrome window forward so the playlist edits can run.
