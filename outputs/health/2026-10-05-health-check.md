# KZSU health check, Oct. 5, 2026

## Status: needs attention (minor)

- Scheduled tasks: 11 of 19 enabled KZSU/related tasks look healthy. Only kzsu-mon-intake (Oct. 5, 7:41 a.m.) and kzsu-daily-mark-email-check (Oct. 5, 7:07 a.m.) have run since enabling; the rest have not reached their first slot (next: Tue releases Oct. 6, Wed final script Oct. 7, Thu sync Oct. 8).
- Disabled (old duplicates, expected): morning-brief, weekday-inbox-triage, kzsu-staged-albums-weekly, kzsu-thursday-working-rewrite, kzsu-daily-playlist, kzsu-review-templates.
- YTM: signed in. Library loads with Weekly (91), Air Order (42), Working (39), Next Show (35), FCC Edit Needed (24).
- Repo: HEAD (51ed787) matches origin/main. One untracked file: newinstructions.md. Stale locks in .git: HEAD.lock, index.lock, objects/maintenance.lock. The sandbox cannot delete them, so no commit was made. Remove them on the Mac: `rm .git/*.lock .git/objects/maintenance.lock`.
- Drive: local KZSU folder is not mounted in this session. Show Prep on Drive (via connector) holds the Oct. 8 Working Show Script and Notes Sheet (built Oct. 5, 4 a.m.). Oct. 1 files are still in Show Prep and the Zookeeper CSV for Oct. 8 is registered; archive move is due Wed night.
- Health notes, last 7 days: 2026-10-05 (intake). Reason for skips: Drive not mounted, so tick harvest and Sheet redeploy were skipped.
- Zookeeper metadata: data/zk_cache.json does not exist, so no cache to audit. In the Oct. 8 plan, 29 tracks have an empty tag field (most are not in the library; confirm in the Wednesday build).
- Quarterly: Oct. 1 Google Takeout re-export reminder is due. Re-export Takeout (YouTube Music activity).
- Also: newinstructions.md in the repo root describes a project rescaffold. Not acted on.
