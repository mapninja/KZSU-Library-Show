---
name: kzsu-fcc-lyrics-check
description: >-
  FCC lyric screen for DJ Stace's "The Library" on KZSU 90.1 FM. Checks every track on an album, playlist, recon plan or list of songs for FCC words (fuck, shit, piss, cunt, cocksucker, cock, tits) and caution words (bitch, asshole, goddamn). Uses lyrics databases through their APIs first: the Genius API to find the song, then LRCLIB and lyrics.ovh, with the Deezer explicit flag as a hint. Falls back to Genius, AZLyrics or Bandcamp pages in a browser only when the APIs fail. Reports the exact word, count and section for each hit and never reproduces lyrics. Use this whenever Stace asks to FCC-check, screen, clear or "check for swears" in a song, album, review, playlist or show, or when another KZSU skill needs FCC status for tracks, even if she doesn't name the skill.
---

# KZSU FCC lyrics check

FCC rules bar certain words on KZSU from 6 a.m. to 10 p.m., which covers DJ Stace's Thursday 6-8 p.m. show. This skill screens tracks before they reach her playlist, review or Zookeeper upload.

Other KZSU skills call it: review templates, staged albums, the show build and the weekly playlist.

## Rules that never change

- **Word lists.**
  - FCC: fuck (all forms, including motherfucker), shit (including bullshit), piss, cunt, cocksucker, cock, tits.
  - Caution: bitch, asshole, goddamn. These are station-policy calls, not FCC violations.
- **Report exactly.** Give the word, count and location for every hit, for example: FCC "shit" x2 (Verse 2).
  - The location is the Genius section label, or a line number such as "line 12" when the lyrics have no sections.
  - Stace wants the exact word named. Name it; don't write "an obscenity."
- **Never reproduce lyrics.** No lines, no couplets, no hooks, in files or in chat. The script keeps lyric text in memory only and saves counts.
- **API first.** Use the Genius API before any web page. Use the browser only when every API route fails for a track.
- **CLEAN has limits.** CLEAN means no flagged words in the posted lyrics. Crowd-sourced lyrics can be wrong, so flag every hit for Stace to confirm by ear.

## Requirements

- **Repo.** The GitHub repo `KZSU-Library-Show` as the workspace. Paths below are relative to its root.
- **Script.** `scripts/fcc_lyrics_check.py`. If it's missing, copy it from this skill's `scripts/` folder. It uses only the Python 3 standard library.
- **Genius token.** Put it in `.env` as `Genius_ACCESS_TOKEN` or `GENIUS_ACCESS_TOKEN`.
  - To get one: https://genius.com/api-clients, "Generate Access Token."
  - Never print or copy the token.
- **Web access.** The script needs outbound requests to api.genius.com, genius.com, lrclib.net, api.lyrics.ovh and api.deezer.com.
  - If the workspace blocks scripted requests, don't work around the block with other scripts. Use the browser fallback below.
- **Browser (fallback only).** Claude in Chrome or the built-in browser.

## Workflow

### 1. Figure out what to screen

The script accepts any of these:

| Input | How to run |
|---|---|
| One song | `python3 scripts/fcc_lyrics_check.py --artist "Gladie" --track "Fixer"` |
| Album review research | `python3 scripts/fcc_lyrics_check.py outputs/reviews/research/<slug>.json --write-back` |
| Recon plan or working playlist | `python3 scripts/fcc_lyrics_check.py data/recon/<date>/working_playlist.json --write-back` |
| A list | A `.txt` file with one `Artist - Title` per line |

If Stace names an album but there's no research file yet, build a quick `.txt` list from the album's tracklist. The review-template skill's `album_lookup.py` can make one.

`--write-back` fills in the fields other skills read:

- research files: `fcc` and `fcc_source`
- plans: `fcc_status` and `fcc_note`

The script skips tracks marked `CUT`.

### 2. Run the screen

```bash
python3 scripts/fcc_lyrics_check.py <input> --write-back
```

For each track it:

1. Searches the Genius API. The match must be the right artist and a close title (80% or better).
2. Reads the lyrics from that Genius song page.
3. If Genius has nothing, tries LRCLIB, then lyrics.ovh.
4. If still nothing, asks Deezer whether the track is marked explicit.

It writes `outputs/fcc/<input>_fcc.json` and `outputs/fcc/<input>_fcc.md`.

### 3. Check the matches

Open the `.md` table. For each row:

- **Wrong song.** `genius_match` should name the same song. A live version or remix is OK only if that's what Stace asked for. If Genius matched the wrong song, rerun that one track with `--no-genius`, or use the browser fallback.
- **SUSPECT or UNVERIFIED.** Try the browser fallback for these rows.
- **Short lyrics.** A lyrics count under about 40 words for a full-length song often means a partial transcription. Note it as "partial lyrics."

### 4. Browser fallback (only for tracks the APIs missed)

Use `references/browser_counter.md`:

- Navigate to the Genius page by URL. Don't `fetch()` Genius from the page: its search API returns HTML to scripted calls.
- If Genius has no lyrics, try AZLyrics, then the Bandcamp track page's lyrics section.
- Count words in-page with the snippet. It returns counts only.
- Close any tabs you opened.
- Add the results to the `_fcc.json` and `.md` files, with the source URL. If `--write-back` was used, add them to the input file too.

### 5. Report

Keep it short: bullets, AP style, no em dashes, no hyperbole. Name the word and count every time.

- **FCC tracks**, by track number: word, count, section. Example: `8. "Fixer": FCC "shit" x1 (Chorus). Worth editing.`
- **Caution tracks**, listed the same way.
- **SUSPECT and UNVERIFIED tracks**, with "listen first."
- **Summary line** in Stace's review format, listing the FCC track numbers: `FCCs: 4, 8, 11`.
- **Paths** to the `_fcc.md` table and to the input file, if it was updated.

When this skill runs inside another skill, return the per-track `note` strings and the FCCs line, and let the calling skill format them.

## Status values

| Status | Meaning | Airable 6 a.m.-10 p.m.? |
|---|---|---|
| FCC | At least one FCC word | No, unless edited |
| CAUTION | Caution words only | Stace's call |
| CLEAN | Lyrics found, nothing flagged | Yes, after a listen |
| INSTRUMENTAL | LRCLIB lists it as instrumental | Yes |
| SUSPECT | No lyrics, but marked explicit in stores | Listen first |
| UNVERIFIED | No lyrics anywhere | Listen first |

## Style

AP style, no em dashes, no hyperbole. Use bullet lists and write for a busy, tech-savvy reader. Code you write or edit must carry beginner-friendly inline comments.
