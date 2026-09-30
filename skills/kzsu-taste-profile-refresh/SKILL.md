---
name: kzsu-taste-profile-refresh
description: >-
  Refreshes DJ Stace's music taste profile for "The Library" on KZSU 90.1 FM on a regular schedule (weekly by default). Pulls new on-air playlists from the KZSU Zookeeper API, recounts her YouTube Music playlists (skipping spoken word, podcasts and assistant-built playlists), checks her YouTube Music Takeout, rebuilds config/taste_profile.json with scripts/build_taste_profile.py, writes a report of what moved, updates TASTE_PROFILE.md, and puts both in her KZSU Google Drive folder. Use this whenever Stace asks to update, refresh, rebuild or check her taste profile, asks what changed in her taste or rotation, adds or renames YouTube Music playlists, or on the scheduled run, even if she doesn't name the skill. Do not use it for weekly new-release recon, staged-album ranking (kzsu-staged-albums-weekly) or building the Thursday show (kzsu-show-build). Those skills read the profile this one writes.
---

# KZSU taste profile refresh

You keep DJ Stace's taste profile current. She is Stace Maples, host of "The Library" on KZSU 90.1 FM Stanford, Thursdays 6-8 p.m. PT.

Every other show-prep skill scores music against `config/taste_profile.json`:

- the daily playlist
- staged-album ranking
- weekly recon
- the show build

If the profile goes stale, all of them drift.

The profile combines five kinds of evidence:

| Evidence | Source | Weight in the score |
|---|---|---|
| Airplay | KZSU Zookeeper playlists (airname 1428) | 3 per show, plus 6 per show in the last 12 months |
| Listening | Google Takeout YouTube Music history | 4 × log(1 + plays) |
| Reviews | KZSU library reviews | 5 per review |
| Playlists | Her YouTube Music playlists | 4 × Σ playlist weight × log2(1 + tracks) |
| Edits | `data/daily/feedback.json` (her adds and deletes) | Reported here. Used by the pick-making skills. |

Scores are scaled so the top artist is 100. The weights live at the top of `scripts/build_taste_profile.py`. Per-playlist weights live in `data/ytm/playlists.json`.

## Schedule

- Run it weekly, **Sunday at 8 p.m. PT**. That picks up Thursday's show and lands before the Monday staged-album run.
- Also run it whenever Stace asks.
- If no new show aired and nothing changed, still run it. It's quick, and the 90-day rotation window moves every day.

## Requirements

- **The repo.** The GitHub repo `KZSU-Library-Show`, checked out or connected as the workspace folder. All paths below are relative to the repo root.
- **Personal data.** These files aren't in git, so copy them to a new machine by hand:
  - `data/MyActivity.html`: the Google Takeout "My Activity" HTML for YouTube and YouTube Music, about 80 MB.
  - `data/library_show.db`: optional. The build script recreates it.
  - `.env`: needs `KZSU_LIBRARY_API_KEY`, and optionally `YTMUSIC_AUTH_PATH`.
  - `browser.json`: ytmusicapi browser headers for Stace's Google account.
- **Python.** Python 3.10 or later. Also `pip install requests ytmusicapi`. Add `--break-system-packages` if pip refuses.
- **Scripts.** The bundled copies are in this skill's `scripts/` folder. If any are missing from the repo's `scripts/`, copy them in:
  - `build_taste_profile.py`
  - `ytm_playlist_counts.py`
  - `taste_profile_changes.py`
  - `merge_kzsu_shows.py`

  They also need the repo's own `scripts/build_music_db.py`.
- **Connectors.**
  - Google Drive: search, create and update files.
  - A browser, for the fallbacks only. Claude in Chrome signed in to Stace's Google account, or the built-in browser.
  - Find connector tools with ToolSearch keywords, for example "google drive search files" or "google drive create file."

Never print or copy secret values from `.env` or `browser.json`.

## Workflow

### 1. Preflight

```bash
# From the repo root. Shows how old each source is before anything changes.
ls -la data/library_show.db data/MyActivity.html data/ytm/ config/taste_profile.json
python3 -c "import json; print(json.load(open('data/ytm/playlists.json'))['scraped'])"
```

Note the newest show date:

```bash
python3 -c "import sqlite3; print(sqlite3.connect('file:data/library_show.db?mode=ro', uri=True).execute('SELECT MAX(date) FROM kzsu_shows').fetchone()[0])"
```

### 2. Refresh airplay and reviews from KZSU

```bash
python3 scripts/build_music_db.py --refresh   # downloads playlists + reviews, rebuilds the DB
```

- If it fails because `KZSU_LIBRARY_API_KEY` is missing, tell Stace which `.env` key to add, then use the browser fallback.
- If it fails because the workspace blocks scripted web requests, don't work around the block with other scripts. Use the browser fallback in `references/browser_scrape.md`, section B. It fetches only the new shows from a zookeeper.stanford.edu tab, then runs `scripts/merge_kzsu_shows.py` and `python3 scripts/build_music_db.py`.
- If the build reports spins with a duration in the label field, that's a known CSV-import problem. List the affected show dates in the summary.

### 3. Check the YouTube Music Takeout

Google Takeout can't be pulled automatically. Look at "Newest YouTube Music play" in step 5's report. If it's more than 60 days old, ask Stace to export a new copy:

1. Go to takeout.google.com.
2. Select only "YouTube and YouTube Music."
3. Under "history," choose **HTML** format.
4. Replace `data/MyActivity.html` with the new file.

Then rerun `python3 scripts/build_music_db.py`. Keep going with the old file in the meantime.

### 4. Recount her YouTube Music playlists

```bash
python3 scripts/ytm_playlist_counts.py --dry-run   # check the playlist list first
python3 scripts/ytm_playlist_counts.py             # writes data/ytm/playlists.json + playlist_artist_counts.txt
```

**Exclusions:** spoken word ("God is not Great"), podcasts ("New Episodes," "Episodes for Later"), and the playlists the assistant builds ("DJ Stace library show Air Order," "DJ Stace library show working," "Stace's Daily Playlist"). The script skips these by title. If Stace adds another audiobook or podcast list, add its title to `EXCLUDE_PATTERNS`.

**New playlists** get a guessed weight and `"new": true`. Weights:

- 3: show playlists
- 2: recaps, Liked Music, To Review
- 1.5: FCC and Love Songs
- 1: general
- 0.5: Crawfish Boil, which mostly duplicates All-Time Favorites
- 0.3: utility or seasonal lists, such as Soundbed, Karaoke or Halloweenie

Report new playlists and their guessed weights so Stace can change them. Keep weights she has set by hand. The script already does this.

**If ytmusicapi can't sign in** (missing or expired `browser.json`), use `references/browser_scrape.md`, section A. Also tell Stace how to renew the headers: run `ytmusicapi browser` on her Mac and paste in the request headers from a signed-in music.youtube.com tab.

**Treat her playlists as read only.** Never add, remove, reorder or rename anything in them. Use music.youtube.com only, never youtube.com.

### 5. Rebuild the profile and the changes report

```bash
python3 scripts/build_taste_profile.py     # archives the old profile to config/history/, writes the new one
python3 scripts/taste_profile_changes.py   # writes outputs/taste_profile/changes_<today>.md
```

The report covers:

- data freshness, with anything stale flagged
- movers
- Stace's playlist edits since the last run
- ready-to-paste sections for TASTE_PROFILE.md

Sanity-check the result before going on:

- The top 10 should look like her core: Ty Segall, Guided By Voices, Father John Misty, Queens of the Stone Age, Bodega, Spoon and similar.
- A big jump for a utility playlist's artist, such as a Soundbed-only act entering the top 50, means a weight is wrong. Fix it in `data/ytm/playlists.json` and rerun.
- Duplicate spellings, such as "Guided By Voices" and "Guided by Voices," should merge. If one shows up twice, look at `artist_key()` in `build_music_db.py`.

### 6. Update TASTE_PROFILE.md

Edit the file in place. Replace only the parts the numbers drive, using the report's "Paste into TASTE_PROFILE.md" section:

| TASTE_PROFILE.md part | Replace with |
|---|---|
| "Generated ..." line under the title | Today's date, AP style |
| Evidence base table | Current counts (shows, spins, reviews, plays, playlists and tracks) |
| "Core artists" table and "Next tier" line | Core artists table, Next tier |
| "Labels you return to" table and the year-to-date line | Labels table |
| "What's in rotation now" first bullet | In rotation now |
| "Opportunities in the data" bullets | Heard a lot, rarely aired; Overdue favorites |
| "What your playlists add": signal and never-aired lists | Strong in playlists, never aired; top playlist scores |

Leave the narrative sections alone: style clusters, reviewing voice, show format. Revise them only when the evidence clearly shifts. For example, a new cluster appears across several weeks, or a style drops out of rotation for months. When you do change one, say so in the summary. Don't rewrite them in a new voice.

### 7. Rebuild the dashboard (optional)

```bash
python3 scripts/build_dashboard.py   # outputs/dashboard/index.html
```

If this environment can publish artifacts, republish the dashboard artifact `dj-stace-music-explorer`. Otherwise, leave the file in the repo.

### 8. Deliver to Google Drive

Put the files in Stace's **KZSU** folder (ID `1KhuroWaBTvKo5i5voVk2iB_GwRgpfKfA`, in My Drive), subfolder **Show Prep**:

- `TASTE_PROFILE.md`: replace the existing copy.
- `<YYYY-MM-DD> taste_profile_changes.md`: a new file each run.

Upload rules:

- Upload as raw Markdown: `contentMimeType: text/markdown`, `disableConversionToGoogleType: true`.
- Find Show Prep by searching for a folder titled "Show Prep" whose parent is the KZSU folder. Create it there if it's missing. Never write to the Drive root.
- To replace a file, move the old copy to `KZSU/_to_delete` (ID `1b2cmq-T--n7Ge2iQL3K5ajwDMK53zPMC`), then upload the new one. Never delete Drive files.
- If there's no Drive connector, keep the files in the repo and give Stace the paths.

### 9. Save locally

- Keep `config/history/` and `outputs/taste_profile/`. Other skills compare against them.
- If git is available, commit these with the message `Taste profile refresh <date>`:
  - `config/taste_profile.json`
  - `config/history/`
  - `data/ytm/`
  - `TASTE_PROFILE.md`
  - `outputs/taste_profile/`

  Push only if Stace has approved pushing on this machine.
- Only delete files you created in this run. Move any other file to `_to_delete/`.

### 10. Summary for Stace

Keep it short: bullets, AP style, no em dashes, no hyperbole.

- Data freshness: newest show, Takeout date, playlists scraped, anything stale and what she needs to do about it
- Top movers up and down, and new entries in the top 100
- New "strong in playlists, never aired" artists: candidates for air
- Her playlist edits since the last run, and any artist now downweighted (3+ removals)
- New or missing playlists, and the weights you guessed
- The Drive link to the changes report

## Style

AP style, no em dashes, no hyperbole. Use bullet lists and write for a busy, tech-savvy reader. Code you write or edit must carry beginner-friendly inline comments.

## Files this skill touches

| Path | Role |
|---|---|
| `data/raw/kzsu/playlists_dj1428_raw.json`, `reviews_dj1428_raw.json` | Raw Zookeeper data. Written only by `--refresh` or `merge_kzsu_shows.py`. |
| `data/MyActivity.html` | Takeout, supplied by Stace |
| `data/library_show.db` | Built by `build_music_db.py` in a temp dir and copied in, because SQLite can fail on mounted folders |
| `data/ytm/playlists.json`, `playlist_artist_counts.txt` | Playlist evidence and weights |
| `data/daily/feedback.json` | Her playlist edits. Read only here. |
| `config/taste_profile.json`, `config/history/` | The profile and its dated archive |
| `outputs/taste_profile/changes_<date>.md` | This run's report |
| `TASTE_PROFILE.md` | Human-readable profile |
