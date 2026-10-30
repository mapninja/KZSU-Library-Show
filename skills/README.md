# KZSU skills

Source of truth for all KZSU Library Show skills. Each folder has `SKILL.md` and a packaged `<name>.skill` zip that can be installed in Claude.

| Skill | Purpose |
|---|---|
| kzsu-radar | Continuous new-release watch: daily light pass, Tue/Fri full pass (replaces intake, album sweep, health, Tue/Fri sweeps) |
| kzsu-thu-draft | Thursday 8 a.m. draft of show prep from her Next Show and Air Order edits |
| kzsu-thu-final | Thursday 1:30 p.m. final: Working, Zookeeper CSV, final script PDF |
| kzsu-bay-area-shows | Monday upkeep of the 4 to 6 month Bay Area shows sheet and giveaway requests |
| kzsu-taste-profile-refresh | Rebuild taste profile and dashboard (Sun) |
| kzsu-intake | Staged albums, Current Adds, Top 50, Filtered Review Shelf (Mon) |
| kzsu-staged-albums-weekly | Music Dept email ranking (called by intake) |
| kzsu-album-sweep | New and announced albums from favorite labels, Weekly and Review playlists, and lead singles aired (Mon) |
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


## Schedule (Oct. 30, 2026)

| When | Task |
|---|---|
| Daily 6:30 a.m. | kzsu-radar-daily (Mon adds intake, album sweep, health email; Fri adds archive retry) |
| Tue, Fri 7:30 a.m. and 1:30 p.m. | kzsu-radar-playlists |
| Mon 9 a.m. | kzsu-bay-area-shows |
| Thu 8 a.m. | kzsu-thu-draft |
| Thu 1:30 p.m. | kzsu-thu-final |
| Thu 8:30 p.m. | kzsu-thu-archive (titles start `03 Archive - `, no Air Order) |
| Thu 9:30 p.m. | kzsu-thu-night-draft (seeds next week) |
| Sun 8 p.m. | kzsu-sun-taste-profile |
| 1st and 15th | kzsu-monthly-specialty |

Disabled, not deleted: wed-final-script, thu-show-sync, fri-archive-retry, tue-releases, fri-releases, tue-fri-new-releases-review, tue-fri-review-templates, mon-intake, mon-health, mon-album-sweep, daily-mark-email-check. Their skills are still called by the new ones.
