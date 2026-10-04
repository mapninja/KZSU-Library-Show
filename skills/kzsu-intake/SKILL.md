---
name: kzsu-intake
description: >-
  Monday intake for DJ Stace's "The Library" on KZSU 90.1 FM. Runs the staged-albums check (Music Dept and Mark Mollineaux emails), refreshes the "KZSU Current Adds" YouTube Music playlist from the Zookeeper Current Adds list filtered to her taste profile, refreshes the "College Radio Top 50" playlist from the current indie, rock and alt college charts, and updates the Google Sheet "Stace's KZSU Filtered Review Shelf" with a checkmark column she ticks to request review boilerplate and a To Review add. Use on the Monday morning run, or whenever Stace asks to update the review shelf, current adds, college charts or what Mark sent, even if she does not name the skill. Not for the Thursday show build or outside new-release research.
---

# KZSU intake (Monday)

Read `references/house_rules.md` and `config/playlists.json` first. Pre-flight: YTM signed in (music.youtube.com/library) and Drive connector available. If not, write `outputs/health/<date>.md` and stop.

## Steps

1. **Staged albums.** Invoke `kzsu-staged-albums-weekly`. It reads Outlook (read only), updates `data/staged/`, ranks with `scripts/staged_crossref.py`, FCC-screens top picks.
2. **KZSU Current Adds.**
   - Pull Current Adds from Zookeeper (API docs in `api_docs/KZSU_API/`; run `fetch()` from a zookeeper.stanford.edu tab in the browser if the shell is blocked).
   - Keep albums that fit the taste profile (score against `config/taste_profile.json`). Drop the rest.
   - Delta-update playlist `kzsu_current_adds` (create it if `id` is null, then save the ID in `config/playlists.json`). Pick the lead track per album, preferring tracks already getting spins and FCC-clean tracks.
3. **College Radio Top 50.** Read the current indie/rock/alt charts (NACC, collegeradiocharts.com, radiowavemonitor; use the browser). Delta-update `college_top50` to the current 50. Chart order, one lead track per album.
4. **Filtered Review Shelf (Google Sheet).** Create or update "Stace's KZSU Filtered Review Shelf" in Drive /KZSU/ using the `anthropic-skills:google-workspace` skill. Rows: suggested new releases, KZSU review-shelf albums from the Music Dept, and albums or tracks she added to To Review. Columns: Request (checkbox), Artist, Album, Label, Release date, Source, Taste score, Lead track, FCC status (with lyrics link), Notes, Boilerplate done (date), Added to To Review (date). Never clear her ticks.
5. **FCC-screen** new lead tracks with `kzsu-fcc-lyrics-check`.
6. **Save, archive, commit.** Prior-week files go to /KZSU/Archive/YYYY/MM-DD/. Commit and push.
7. **Summary.** New staged albums, adds and chart changes, ticked requests waiting.

Tick handling is done by `kzsu-review-template` (Tue and Fri).

## Zookeeper metadata

Read `references/zookeeper_enrichment.md`. Anything YTM and Zookeeper cannot supply comes from Discogs, then Wikipedia and media sources (see the fallback section there), with source and URL recorded. Check each staged and Current Adds album against the library record. Store tag, label and in-library status on the shelf rows. Use Zookeeper label names.
