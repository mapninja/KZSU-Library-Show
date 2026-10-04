# KZSU skills

Source of truth for all KZSU Library Show skills. Each folder has `SKILL.md` and a packaged `<name>.skill` zip that can be installed in Claude.

| Skill | Purpose |
|---|---|
| kzsu-taste-profile-refresh | Rebuild taste profile and dashboard (Sun) |
| kzsu-intake | Staged albums, Current Adds, Top 50, Filtered Review Shelf (Mon) |
| kzsu-staged-albums-weekly | Music Dept email ranking (called by intake) |
| kzsu-weekly-playlist | Add-only sweeps into Stace's Weekly Playlist (Tue, Fri) |
| kzsu-review-template | Review boilerplate for ticked shelf rows (Tue, Fri) |
| kzsu-weekly-recon | Thursday-night draft plan and Air Order |
| kzsu-notes-sheet-and-script | Notes Sheet and Working Show Script |
| kzsu-final-script | Final Show Script (Wed night) |
| kzsu-show-build | Working playlist (reversed) and Zookeeper CSV (Thu a.m.) |
| kzsu-archive-playlist | Archive playlist of the aired show (Thu night) |
| kzsu-specialty-show | Holiday and topical 2.5 hr playlists (monthly) |
| kzsu-fcc-lyrics-check | FCC lyric screen (called by others) |
| kzsu-health-check | Monday status email |

Shared inputs: `references/house_rules.md`, `config/playlists.json`, `config/paths.json`. Task prompts live in `config/scheduled_tasks/`.

To reinstall tasks on a machine: create each task with the prompt in `config/scheduled_tasks/<id>.md`.
