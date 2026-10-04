---
name: kzsu-weekly-playlist
description: >-
  Twice-weekly (Tuesday and Friday) new-release sweep that ADDS tracks to DJ Stace's rolling YouTube Music review list "Stace's Weekly Playlist" for "The Library" on KZSU 90.1 FM. Adds new singles and albums from Stereogum, Pitchfork, indieisnotagenre, label feeds and Music Dept emails, Today-in-Music tracks, alternative tracks from albums she is playing, and tracks tied to Bay Area shows from foopee.com. Learns from her deletions (60-day cool-off) and her own adds, replaces deleted Today-in-Music tracks when taste warrants, FCC-screens every track, and sends strong FCC tracks to the FCC Edit Needed playlist. Never clears the playlist. Use on the Tuesday and Friday sweeps, or whenever Stace asks to refresh, add to or review her weekly playlist or listening list, even if she does not name the skill. Not for building Working, the Zookeeper CSV or scripts; that is kzsu-show-build.
---

# KZSU weekly playlist (rolling review list)

Read `references/house_rules.md` and `config/playlists.json` first. IDs live there, not here.

"Stace's Weekly Playlist" is her review list. She listens through the week and deletes what feels stale. The Air Order and Working drafts are built from it.

## Rules

- **Add, do not clear.** Never remove a track. Only she removes tracks.
- **YTM only.** music.youtube.com. Never youtube.com.
- **Read only:** "DJ Stace - Next Show" and Air Order (except the draft build in `kzsu-weekly-recon`).
- **Playlist writes:** try ytmusicapi first if the shell can reach YTM. If it cannot (the sandbox returns 403), use the signed-in built-in browser. Verify by reload after every batch. See `references/browser_js.md`.
- **Pre-flight:** open music.youtube.com/library. If YTM shows signed out, stop, write the reason to `outputs/health/<date>.md` and stop.
- **Web research:** WebSearch and the browser only. No scripted web requests from the shell. WebSearch is capped per session, so use feeds and label pages in the browser where possible.
- Only one machine runs this. It is this Mac.

## Learn from her edits (every run, first)

- Deleted track = not interested now. Log in `data/daily/feedback.json` "removed" with date, artist, title, videoId, bucket, signal, `cooloff_until` (+60 days). Increment `artist_removals`. Downweight an artist only after 3 removals. Lean less on a signal she keeps cutting.
- If she deleted a Today-in-Music track, find a replacement for that date or topic if the music fits her profile. Say so in the notes.
- Track she added = fits. Never touch it. Log in "added_by_stace". Use its artist, label and RIYL neighbors as positive signals.
- Survived 2+ checks = "kept", a mild positive.
- Diff Air Order and "DJ Stace - Next Show" against `data/daily/snapshots/<playlist-id>.json`. Log changes. New artists or labels in Next Show are new interests.

## Sources

- Reviews and news: Stereogum, Pitchfork, indieisnotagenre, Bandcamp Daily, Brooklyn Vegan, similar sites.
- Label new-release pages for labels she plays (see `config/release_watchlist.json` and `sources.yml`).
- Mark Mollineaux and Music Dept emails (read only, via Outlook).
- `data/staged/` and `outputs/reviews/staged_priority_*.md`.
- Today in Music: thisdayinmusic.com and similar, for the target show date and the week around it.
- Bay Area shows: http://www.foopee.com/punk/the-list/ filtered by the taste profile. Prefer KZSU giveaway venues (Mountain Winery, Yoshi's, The Independent, Fox Oakland, Fox Redwood City, Chapel, The Lab, Freight & Salvage, Guild, Fillmore).

## Steps

1. **Pre-flight and learn** (above).
2. **Pick adds.** Target 25 to 35 per run. No duplicates, nothing in cool-off, nothing aired in the last 21 days unless it is a new single she is rotating.
   - **New releases (Tue: singles and announcements; Fri: full sweep).** Rank staged albums first, then albums whose singles she airs, then fresh finds. Include singles and albums. Note label, release date, upcoming album.
   - **Alternates.** For albums she has been playing, add other strong tracks from the album, or label-mates and RIYL neighbors.
   - **Today in Music.** Anniversaries for the target show week. Favor round numbers and her artists.
   - **Bay Area.** Tracks from artists playing upcoming Bay Area dates. Note venue and date.
   - **Taste/topical.** Holidays and events, plus overdue favorites. Seed random picks with the date.
3. **FCC-screen every pick** with `kzsu-fcc-lyrics-check`. FCC hits can stay in this listening playlist but are labeled not airable 6 a.m. to 10 p.m. with exact word and count. If the track is strong, also add it to "FCC Edit Needed" and flag it for a possible radio edit. No lyrics found = UNVERIFIED.
4. **Add** to the playlist in bucket order. Wait for the "Saved to" toast plus 1.5 seconds between adds. Never click Like or Dislike. Reload and confirm count and videoIds.
5. **Save.**
   - Snapshot: `data/daily/<date>.json`.
   - Notes: `outputs/weekly/<target show date>.md`, with YTM links, label, release date, why, FCC flags, and Bay Area date if any.
   - Copy notes to Drive /KZSU/ (current) and move last week's to /KZSU/Archive/YYYY/MM-DD/.
6. **Commit and push** (token in `.env`; never print it).
7. **Chat summary.** Her deletes and adds, this run's adds by bucket, FCC flags, playlist link.

Target show date: the next Thursday that has not aired. If today is Thursday after 8 p.m., use +7 days.

## If the browser tab is hidden

Reading and adds work in a hidden tab. If clicks stop responding, finish research and files, then ask Stace to bring the browser pane forward (Cmd+Shift+B).

## Zookeeper metadata

Read `references/zookeeper_enrichment.md`. Anything YTM and Zookeeper cannot supply comes from Discogs, then Wikipedia and media sources (see the fallback section there), with source and URL recorded. For each pick, look up tag and label in Zookeeper and put the Zookeeper label in the notes file. Mark web-only labels "(verify)".

## Drive placement

Follow the Drive layout in `references/house_rules.md`: drafts and next-week materials go in `/KZSU/Show Prep/`. Only final artifacts for the coming show go at the `/KZSU/` top level, and the previous week's finals move to `/KZSU/Archive/YYYY/MM-DD/` first.

## Review Shelf

After each Tuesday and Friday sweep, run the Filtered Review Shelf refresh in `skills/kzsu-intake/SKILL.md` (new releases only).

## Deploying Sheets and Docs

Edit the CSV or Markdown working copy in `/KZSU/Working/`, then deploy with `skills/kzsu-drive-deploy/SKILL.md` (harvest Stace's edits first, create new, verify, retire old, update the registry).
