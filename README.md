# KZSU Library Show Repository

This repository contains tools and notebooks for managing the KZSU Library Show, a music program that curates and broadcasts library tracks from various artists.

## Overview
The KZSU Library Show is designed to help DJs discover and organize new music releases, historical rock content, and chart information. This repository provides tools for downloading, consolidating, and analyzing playlist data using the KZSU Zookeeper API.

## Key Components

### 1. Notebooks
- **playlist_metadata_and_yt_builder.ipynb**: A Jupyter notebook that downloads metadata from YouTube Music playlists and builds a skeletal playlist based on weekly music history aggregations. This notebook is used to prepare playlist data for the KZSU Library Show.
- **weekly_aggregation.ipynb**: (Not found) - A notebook for aggregating weekly music history data, which may be used in conjunction with other notebooks to generate comprehensive reports.

### 2. Configuration Files
- **sources.yml**: Contains a list of sources for new music releases, chart information, and historical rock data. This file is used to gather relevant content for the KZSU Library Show.
- **config.yml**: (Not found) - A configuration file that may contain settings for the repository's operations.

### 3. Data Files
- **outputs/2026-09-10.csv**: A CSV file containing track data from a specific date, including artist names, song titles, album information, and other metadata. This file is used to store consolidated playlist data for the KZSU Library Show.

## Workflow
The typical workflow involves using the **playlist_metadata_and_yt_builder.ipynb** notebook to download metadata from YouTube Music playlists and build a skeletal playlist based on weekly music history aggregations. The resulting data is then stored in the **outputs/2026-09-10.csv** file, which can be used for further analysis or reporting.

## Future Enhancements
- Create a new notebook that uses the KZSU Zookeeper API to download and consolidate all playlists for a given DJ_ID into a single CSV file conforming to the zookeeper CSV upload requirements.
- Add metadata such as date, time, show name, and other relevant information to each track in the consolidated CSV file to enable sorting and filtering by various criteria (e.g., data, show name, DJ name, label, artist).

## Contact
For questions or feedback about this repository, please contact [Your Name] at [your.email@example.com].

---

This README.md file provides an overview of the KZSU Library Show Repository and its key components. It also outlines the current workflow and future enhancements for the project.
## Upcoming releases database

- `scripts/build_release_watchlist.py` writes `config/release_watchlist.json`: labels you air (from KZSU spins, reviews and `sources.yml`) plus the top 200 profile artists.
- Research findings go in `data/releases/research/` (JSON lists or JSONL, fields in `RESEARCH_BRIEF.md`). `data/releases/coverage.json` records which labels were checked.
- `scripts/build_release_db.py` merges duplicates, scores each release against your taste profile, and writes:
  - `upcoming_releases` and `release_watch_labels` tables in `data/library_show.db`
  - `data/releases/upcoming_releases.csv`
  - `outputs/releases/upcoming_releases.md` (by week, with YouTube Music preview links)
- Re-run `build_release_db.py` after `build_music_db.py`, which rebuilds the database from scratch.
