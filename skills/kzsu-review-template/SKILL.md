---
name: kzsu-review-template
description: >-
  Makes KZSU library review templates in Markdown for DJ Stace ("The Library," KZSU 90.1 FM). Works for any album she names, and for every album she ticks in the "Make review templates" checklist of her weekly staged_priority list. Templates follow the layout, tone and style of her past KZSU reviews and pre-fill label, release date, release notes and credits, a one-line draft take in her voice, short pull quotes from authoritative outlets, RIYL, the FCC track numbers, and a tracklist with runtimes. Each track gets only very basic objective notes: pace from BPM data, plus FCC flags or suspicions from the kzsu-fcc-lyrics-check skill. Saves templates to her KZSU Drive folder and marks the checklist item done. Use this whenever Stace asks for a review template, boilerplate, review draft or "review prep" for an album, or on the scheduled check for ticked boxes, even if she doesn't name the skill. Not for ranking staged albums (kzsu-staged-albums-weekly) or for her final opinions and star ratings.
---

# KZSU review template

You prepare the paperwork for DJ Stace's KZSU library reviews so she can listen and write. She is Stace Maples, host of "The Library," Thursdays 6-8 p.m. PT.

- She adds her real take, her star ratings and her listening notes.
- You add everything objective, and a short draft take she can keep or throw out.

## What triggers a run

1. **She names an album.** For example, "Make a review template for the new Widowspeak." Run for that album.
2. **Ticked boxes.** The weekly staged list has a "Make review templates" checklist. Stace changes `- [ ]` to `- [x]` on the albums she wants.
   - Find the newest `staged_priority_<date>.md` in Drive: KZSU > Staged Reviews (folder ID `1egd_cdhuaEPbsSQyReTAIQq3O8ZHP92M`). The Drive copy is the one she edits, so read it, not the repo copy.
   - Download it to `outputs/reviews/`, overwriting the local copy of the same name.
   - Then list what's waiting:

     ```bash
     python3 scripts/review_requests.py pending outputs/reviews/staged_priority_<date>.md
     ```

     This prints ticked items that don't have a template yet.
   - No ticked items: stop and say so in one line.

Don't make templates for albums she didn't ask for.

## Rebuild update (Oct. 2026)

- **Trigger source is now the Google Sheet** "Stace's KZSU Filtered Review Shelf" in Drive /KZSU/. Rows where the Request checkbox is ticked and "Boilerplate done" is empty are pending. The staged_priority checklist still works as a fallback.
- **Save templates to the `KZSU-Album-Reviews` repo** (`/Users/maples/Github/KZSU-Album-Reviews`), plus a copy in Drive. Reviews, boilerplate and finals all live in that repo. Commit and push it too.
- **After each template:** add the album's lead tracks to the "To Review" YTM playlist (ID in `config/playlists.json`) by delta, fill "Boilerplate done" and "Added to To Review" in the sheet. The old "To Review" list is stale; do not clear it without Stace's OK. Just add.
- **Schedule:** Tuesday and Friday 9 a.m., after the release sweeps.
- Read `references/house_rules.md` first.

## Requirements

- **Repo.** The GitHub repo `KZSU-Library-Show` as the workspace. Paths below are relative to its root.
- **Scripts.** These are in the repo's `scripts/`. If any are missing, copy them from this skill's `scripts/` folder:
  - `album_lookup.py`
  - `review_boilerplate.py`
  - `review_requests.py`
  - `fcc_lyrics_check.py`
  - `staged_crossref.py`

  They use only the Python 3 standard library.
- **Keys in `.env`.** Never print them.
  - `Genius_ACCESS_TOKEN`: FCC screening
  - `KZSU_LIBRARY_API_KEY`: Zookeeper
  - `DISCOGS_TOKEN`: credits (optional)
- **Web access.** Scripts call the Deezer, MusicBrainz, Discogs, Genius, LRCLIB and Zookeeper APIs. If the workspace blocks scripted requests, don't work around the block. Do the lookups in the browser and fill the research JSON by hand.
- **Other tools.**
  - WebSearch and a browser, for press quotes, BPM gaps and Bandcamp credits.
  - Google Drive connector: search, download, create and update files. Find its tools with ToolSearch, for example "google drive search files."
- **Related skill.** `kzsu-fcc-lyrics-check`, for FCC screening. This skill runs its script.

## Workflow (per album)

### 1. Pull the objective facts

```bash
python3 scripts/album_lookup.py --artist "<Artist>" --album "<Album>" [--tag <Zookeeper tag>]
```

- **Zookeeper tag.** Pass it if the album is in the KZSU library:
  - look for `zookeeper_tag` in `data/staged/afile_adds.json`, or
  - search Zookeeper's `/api/v1/album?filter[artist]=...` in the browser. The filter is exact and uses library forms such as "Last, First" or "Band, The."
- **What it writes.** `outputs/reviews/research/<slug>.json`, with:
  - the tracklist, runtimes, BPM, pace words and explicit flags
  - label, release date and format
  - Discogs credits
- **Tracklist.** Check it against Bandcamp or the label page. Staged promos sometimes differ from the streaming release. If Deezer and MusicBrainz both miss the album (common for self-released records), copy the tracklist and runtimes from Bandcamp into the JSON.
- **Missing BPM.** For each track with no BPM, look it up on songbpm.com or tunebat.com through WebSearch or the browser. Then set `bpm`, and set `pace` using the table in `references/style_guide.md`. If nothing turns up, leave both blank. The template prints `Pace: ____.`

### 2. FCC screen every track

```bash
python3 scripts/fcc_lyrics_check.py outputs/reviews/research/<slug>.json --write-back
```

- This follows the kzsu-fcc-lyrics-check skill: Genius API first, then LRCLIB and lyrics.ovh, with the Deezer explicit flag as a hint.
- For SUSPECT or UNVERIFIED tracks, use that skill's browser fallback.
- Never reproduce lyrics anywhere.

### 3. Research the words

Read `references/style_guide.md` first. Then read 3 or 4 of her past reviews in a similar genre:

```bash
python3 -c "import sqlite3;c=sqlite3.connect('file:data/library_show.db?mode=ro',uri=True);[print(r[0],'\n') for r in c.execute(\"SELECT review_text FROM kzsu_reviews WHERE review_text LIKE '%post-punk%' LIMIT 4\")]"
```

Add these fields to the research JSON:

- **`release_notes`.** Three to six short paraphrased facts:
  - hometown and lineup, with instruments
  - producer, studio and mastering
  - notable guests
  - where this record sits in the band's catalog

  Sources: Bandcamp, the label, press. Don't paste bios.
- **`pull_quotes`.** One to three quotes, each under 15 words, from authoritative outlets listed in the style guide, each with its `source` and `url`. Quote exactly. No quote from a real review is better than a weak one.
- **`draft_comment`.** One or two sentences in her voice: stacked genre adjectives, a comparison, dry and never hype. The render marks it `[DRAFT, edit or replace]`. Base it only on research facts. You haven't heard the record, so don't describe songs.
- **`riyl_suggestions`.** Three to five artists, following the style guide.
- **Track `notes`.** Objective tags only: "Lead single." "Instrumental." "Features Kim Deal." Nothing about how it sounds. Pace comes from BPM.

### 4. Render

```bash
python3 scripts/review_boilerplate.py outputs/reviews/research/<slug>.json
```

- This writes `outputs/reviews/<slug>.md`.
- If a template already exists, the script saves the new one as `<slug>_<date>.md`, so it never writes over a draft she has started. Use `--overwrite` only when she asks.

Read the result top to bottom:

- Layout matches the style guide.
- FCC track numbers match the track lines.
- No lyric text anywhere.
- No em dashes. Replace any that crept in from source text.

### 5. Deliver

- **Drive.** Upload to KZSU > Staged Reviews > **Review Templates** (folder ID `1tHnkXsNSidy9BDtjnYBXwxibyqWl6een`).
  - Title: `<Artist> - <Album> review template.md`.
  - `contentMimeType: text/markdown`, `disableConversionToGoogleType: true`.
  - If a file with that title exists, move the old one to `KZSU/_to_delete` (ID `1b2cmq-T--n7Ge2iQL3K5ajwDMK53zPMC`) first. Never delete Drive files.
- **Checklist.** For requests from the checklist, mark each item done with the Drive link:

  ```bash
  python3 scripts/review_requests.py done outputs/reviews/staged_priority_<date>.md "<Artist>" "<Album>" "<Drive link>"
  ```

  Then update the Drive copy of that staged list with the edited file, same file ID, so her ticks and the new links stay in one place.
- **GitHub.** Commit and push the new research JSON, template and updated list:

  ```bash
  git add outputs/reviews && git commit -m "Review templates <date>" && git push
  ```

  Never commit `.env` or `browser.json`. If the push fails, say so and give Stace the command.
- **Files.** Only delete files you created. Move anything else to `_to_delete/`.

### 6. Summary

Keep it short: bullets, AP style, no em dashes, no hyperbole.

- One line per template: Drive link, track count, and the FCCs line. For example: `FCCs: 4,8 ("shit" x1, "fuck" x3)`.
- Tracks to check by ear (SUSPECT or UNVERIFIED), and tracks missing BPM.
- Anything you couldn't verify: tracklist differences, missing label.

## Style

AP style in your summaries. Inside the template, follow her format, including her `Label:` and `Release Date:` conventions. No em dashes anywhere, no hyperbole. Code you write or edit must carry beginner-friendly inline comments.
