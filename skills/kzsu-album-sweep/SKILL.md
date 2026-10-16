---
name: kzsu-album-sweep
description: >-
  Weekly (Monday) sweep of new and announced ALBUMS for DJ Stace's "The Library" on KZSU 90.1 FM. Looks for albums released in the last 14 days or announced for the next 60 days from three sources: her favorite labels (config/release_watchlist.json), artists on her "Stace's Weekly Playlist" and "New Releases for Review" playlists, and the parent albums of lead singles she has aired on the show. Records label, release date, lead single, fit and FCC status, writes outputs/albums/<date>.md plus a CSV and a ledger so nothing is reported twice, adds new releases to the Filtered Review Shelf, and commits. Use on the Monday run, or whenever Stace asks for an album sweep, new albums from her labels, or "what albums are coming", even if she does not name the skill. Not for the Tuesday and Friday single sweeps (kzsu-weekly-playlist, kzsu-new-releases-review) or the show plan (kzsu-weekly-recon).
---

# KZSU album sweep

Read `references/house_rules.md` first. This sweep finds ALBUMS. The Tuesday and Friday sweeps handle singles and playlist adds. It is read only on YouTube Music: it never edits a playlist.

## Inputs

- Favorite labels: `config/release_watchlist.json` (tier 1 and 2). Top artists per label are listed there.
- Playlist artists: snapshots of "Stace's Weekly Playlist" and "New Releases for Review" in `data/daily/snapshots/` (written by the Tuesday and Friday sweeps).
- Lead singles she has aired: airplay in `data/library_show.db`, last 8 weeks.
- Fit and focus: `config/taste_profile.json`, `config/show_focus.json` (punk and post-punk share), `config/review_rotation.json`.
- Cool-offs: `data/daily/feedback.json` "removed". Skip an artist or track she deleted within its 60-day cool-off.
- Already known: `data/album_sweep/ledger.json` and `data/releases/upcoming_releases.csv`.

## Steps

1. **Build targets.** From the repo root run `python scripts/album_sweep_targets.py --date <today>`. It writes `data/album_sweep/targets_<date>.json` with three lists: `labels`, `playlist_artists`, `lead_singles`. Window: out since 14 days ago, announced through 60 days ahead.
   - Refresh the playlist snapshots first if the last Tuesday or Friday sweep did not write them. Reading a playlist in the browser is allowed.
   - Lead singles are detected by heuristic (album name equals track name, blank album, "single" in the album name, or listed in `upcoming_releases.csv`). Drop classics and reissues. Keep only tracks that are new releases.
2. **Check labels (bucket `label`).** For each tier 1 label, then tier 2 labels with recent spins, open the label's new-release page (`url` in the targets file) in the browser. Use Bandcamp pages and Shopify `/products.json` feeds where the site allows. Wikipedia "List of 2026 albums" and "List of 2027 albums" fill gaps. Keep full albums and EPs. Skip reissues unless the artist is a top favorite. Respect the blocked-site notes in `data/releases/coverage.json`.
3. **Check playlist artists (bucket `playlist`).** For each artist in `playlist_artists`, find a new or announced album. Search Wikipedia lists first, then the artist's label page, then music news (Stereogum, Pitchfork, Brooklyn Vegan, Bandcamp Daily). WebSearch is capped per session, so batch by label or by list page, not by artist.
4. **Check lead singles (bucket `lead_single`).** For each kept lead single, find its parent album, release date and label. If the track is a stand-alone single, skip it.
5. **Confirm and enrich.** For each album record artist, title, label, release date, status (`released` or `announced`), lead single with a link, and a one-line fit reason. Use two sources for a date, or mark "(verify)" and set `sources` to 1. Use Zookeeper label names where the album is in the library (`references/zookeeper_enrichment.md`).
6. **FCC screen** the lead track of each album with `skills/kzsu-fcc-lyrics-check/SKILL.md`. Record the exact word and count in `fcc_note`, or "CLEAN" or "UNVERIFIED". Never reproduce lyrics. Flag, do not drop: this report is for review.
7. **Save findings** as `data/album_sweep/findings_<date>.json` (a list of records). Field list is in the docstring of `scripts/album_sweep_report.py`.
8. **Render.** Run `python scripts/album_sweep_report.py --date <date>`. It writes `outputs/albums/<date>.md`, `data/album_sweep/albums_<date>.csv` and updates `data/album_sweep/ledger.json`. Albums already reported show as "seen". Announced albums are flagged again once, as "NOW RELEASED".
9. **Feed the Review Shelf.** Add `released` albums flagged new (not "seen") to the Filtered Review Shelf with the procedure in `skills/kzsu-intake/SKILL.md` ("Filtered Review Shelf refresh"). Source: "Album sweep". Never clear her ticks. Log in `data/staged/shelf_log.json`.
10. **Copy** the report to Drive `/KZSU/Show Prep/` (KZSU folder only, always pass the parent folder). Do not leave stray files in My Drive root.
11. **Commit and push** with the token in `.env` (never print it). Add explicit paths only: `data/album_sweep/`, `outputs/albums/`, `data/staged/` changes, `config/` changes. Never `git add -A`.
12. **Summary** (short bullets): new albums out now, announced albums with dates, FCC flags, albums that were announced before and are now out, anything blocked or unverified.

## Rules

- Never guess a date. Two sources, or mark "(verify)".
- Albums only. If a label's page lists only a single, note it as "single, album not announced" in the report and move on.
- Skip artists and tracks in a 60-day cool-off, and anything she deleted from Weekly or Review. Her adds to those playlists count as positive signals: rank them first.
- Weight toward the punk and post-punk focus and toward albums whose singles she is airing (see `review-weighting-new-releases` in memory).
- Overlap: the Monday 7:30 intake and 8:30 health runs touch shared files. Check `git status` first and commit only your own paths.
- If the browser is signed out of YouTube Music or blocked everywhere, write `outputs/health/<date>.md` and stop.
- AP style, no em dashes.
