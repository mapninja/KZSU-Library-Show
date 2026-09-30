# Folder review: KZSU-Library-Show

Sept. 26, 2026. What's here, what works, what to fix.

## What the folder contains

| Item | What it is | Status |
|---|---|---|
| `KZSU_DJ_STACE_AGENT_MASTER_SPEC.md` | Full design: 17 notebooks, SQLite, BIG-RAG, LM Studio, YTM/Spotify publishing | Planning doc; mostly not built |
| `notebooks/kzsu_playlist_consolidator.ipynb` | Pulls all DJ Stace playlists (v1 API, `filter[airname.id]=1428`) to CSV | Works (269 playlists) |
| `notebooks/playlist_metadata_and_yt_builder.ipynb` | YouTube Music history via `ytmusicapi` | Works, but the API returns only about 200 recent plays |
| `notebooks/ytm_playlist_export.ipynb` | YTM playlist to Zookeeper CSV, with Discogs label lookup | Works, but the CSV has the wrong column layout (see bugs) |
| `notebooks/weekly_music_history_show_builder.ipynb` | Show-script builder | Won't run: syntax errors, mock data, an API filter that doesn't exist |
| `scratch/Untitled-1.ipynb` | Older copy of the consolidator | Broken; superseded |
| `data/MyActivity.html` | Google Takeout, YouTube and YouTube Music, 2008-2026 | **The best taste evidence here**: 71,859 YTM plays |
| `knowledge_base.json` | 11 "on now" station playlists from Sept. 7 | Not your shows (other DJs, airname "Unknown") |
| `src/dj_stace/agent.py`, `agents.md`, `instructions.md`, `STATUS.md` | Early agent sketch with placeholder weather and social APIs | Doesn't match the master spec |
| `sources.yml`, `scratch.txt` | Recon source list | `scratch.txt` duplicates `sources.yml` |
| `api_docs/KZSU_API/` | Zookeeper API docs | Useful |
| `config.yml` | Empty | |
| `.venv`, `.venv-1` | Two Python 3.9 environments | The spec calls for 3.12 |

## Bugs found

1. **The Zookeeper CSV column order broke the Sept. 24 playlist.**
   - Zookeeper imports by position: artist, track, album, tag, label, timestamp.
   - `ytm_playlist_export.ipynb` writes 5 columns (artist, title, album, label, duration). The label landed in the tag slot and the duration in the label slot.
   - All 26 Sept. 24 spins now show labels like "3:37".
   - The Sept. 10 file (6 columns, blank tag) imported correctly.
   - The new `scripts/build_weekly_recon.py` writes the 6-column layout.
2. **The Sept. 17 playlist has 1 spin.** It's probably incomplete.
3. **`weekly_music_history_show_builder.ipynb` won't run.** `params =` is unindented, and two f-strings contain raw newlines.
4. **YTM monthly report is empty.** `get_history()` returns dates like "Today" and "Yesterday," which don't parse.
5. **`playlist_metadata_and_yt_builder.ipynb` rewrites `browser.json` from `scratch.json` on every run.** The two files use different `x-goog-authuser` values (1 vs. 0), so you can end up signed in to the wrong account.

## Security

- `browser.json` and `src/dj_stace/scratch.json` hold live YouTube session cookies. Anyone with these files can act as your Google account on YouTube.
- The KZSU API key is hardcoded in 7 files.
- The folder sits in `~/Github` but isn't a git repo yet. Before you push it anywhere:
  - Use the new `.gitignore` (added).
  - Move keys into a `.env` file (template at `.env.example`).
  - Rotate the KZSU key and re-export YouTube headers if either file was ever shared.

## What I added

| File | Purpose |
|---|---|
| `scripts/build_music_db.py` | Builds `data/library_show.db` (SQLite) from the KZSU API, reviews and Takeout. `--refresh` re-downloads. |
| `scripts/build_taste_profile.py` | Writes `config/taste_profile.json` (artist and label scores) |
| `scripts/build_dashboard.py` + `templates/dashboard_template.html` | Builds `outputs/dashboard/index.html` |
| `scripts/build_weekly_recon.py` | Turns `data/recon/<date>/candidates.json` into the track suggestions, Zookeeper CSV and YTM list |
| `scripts/review_boilerplate.py` | Builds review drafts in your format from a research JSON file |
| `TASTE_PROFILE.md` | Readable taste profile |
| `data/raw/kzsu/` | Raw API snapshots: 269 playlists, 65 reviews |
| `outputs/recon/2026-10-01/` | This week's recon, show script and CSV |
| `outputs/reviews/` | Review suggestions and the Westside Cowboy draft |

## Suggestions

- **Trim the master spec to a weekly loop:**
  1. Refresh data (Mon).
  2. Recon (Tue and Fri).
  3. Script and CSV (Wed).
  4. FCC screen (Wed).
  5. Post-show reconcile (Thu night).
  - BIG-RAG, LM Studio and Pydantic can wait. The SQLite database now covers the "authoritative store" piece.
- **Change the 180-day repeat penalty.** You run new singles in rotation for weeks; for example, Caroline Rose's "Yip Yip Yow" aired 16 times since April. Treat repeats as rotation, not errors, and penalize only back-catalog repeats.
- **Retire files that no longer fit.** Candidates: `knowledge_base.json`, `scratch/Untitled-1.ipynb`, `scratch.txt`, `agents.md`, `instructions.md`, `src/dj_stace/agent.py`, `STATUS.md`. With your OK, I'll move them to `_to_delete/`.
- **Normalize labels.** "Self-Release," "self," "Self Release" and "unknown" are split across 260 spins. The profile script already groups them.
- **Re-export Takeout quarterly.** It's the only full listening history. The YTM API shows about 200 plays.
