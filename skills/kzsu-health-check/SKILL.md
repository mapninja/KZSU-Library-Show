---
name: kzsu-health-check
description: >-
  Monday status check for the KZSU Library Show automation. Lists every scheduled KZSU task with last run and next run, flags tasks that did not run or were paused, checks YTM sign-in, Drive and repo state (uncommitted files, git locks), and reads outputs/health notes left by other runs. Emails Stace a short status. Use on the Monday 8:30 a.m. run, or whenever Stace asks if the KZSU workflows are healthy, even if she does not name the skill.
---

# KZSU health check

1. List scheduled tasks with the scheduled-tasks tool. For each KZSU task show last run, next run, enabled. Flag any that should have run since the last check and did not.
2. Open music.youtube.com/library in the browser and report signed in or out.
3. Check the repo: uncommitted files, `.git/*.lock`, last push time. Check Drive /KZSU/ has this week's current files.
4. Read `outputs/health/*.md` from the last 7 days and quote the reasons for any stops.
5. Email maples@stanford.edu a 5-line status: OK or what needs her. AP style.
6. Quarterly (Jan, Apr, Jul, Oct 1): remind her to re-export Google Takeout.

## Zookeeper metadata

Read `references/zookeeper_enrichment.md`. Anything YTM and Zookeeper cannot supply comes from Discogs, then Wikipedia and media sources (see the fallback section there), with source and URL recorded. Report plans that still have tracks with no tag or label, and cache misses in `data/zk_cache.json`.
