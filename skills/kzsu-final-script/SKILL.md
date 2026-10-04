---
name: kzsu-final-script
description: >-
  Wednesday-night run that builds DJ Stace's "Library Show Final Show Script" (Google Doc) for "The Library" on KZSU 90.1 FM. Reads the cull and replace checkboxes in the Notes Sheet and her edits to the Air Order playlist, drops culled tracks, finds same-purpose alternatives for replace requests (FCC-screened), rewrites mic breaks that depended on cut tracks, and mirrors the Working script with the changes marked. Emails her the link so she can review and request changes Thursday before the show. Use on the Wednesday 8 p.m. run, or whenever Stace asks to build or rebuild the final script, even if she does not name the skill.
---

# KZSU final show script (Wednesday night)

Read `references/house_rules.md` and `config/playlists.json`. Use `anthropic-skills:google-workspace` for Drive.

## Steps
1. **Read inputs.** Notes Sheet (cull and replace checkboxes), Air Order (additions, removals, order), plan JSON.
2. **Cull.** Drop checked tracks from the plan and log them in `data/daily/feedback.json` "removed" (60-day cool-off).
3. **Replace.** For each replace tick, pick an alternative with the same purpose (set role, theme, date tie, tempo). Draw from Weekly Playlist first, then Next Show, then new research. FCC-screen. Write the swap in the sheet's Notes column.
4. **Air Order edits.** Her Air Order changes win over everything. Added tracks go into the script at their position with label, release date, FCC status.
5. **Rewrite** any mic break that mentions a cut track.
6. **Build "Library Show Final Show Script"** in /KZSU/. Same layout as the working script, with a changes section at the top: culled, replaced (old to new), added, moved. Update the sheet to match.
7. **Sync the plan JSON** so `kzsu-show-build` Thursday starts from the final list.
8. **Email** Stace (Outlook draft/send to maples@stanford.edu is allowed for this notice only) with the doc link and the list of changes.
9. Archive the previous final script to /KZSU/Archive/. Commit and push.

If Wednesday inputs look untouched, still build, and say "no cull or replace ticks found" in the email.

Specialty weeks: same process. If the plan has a `"theme"`, keep theme talking points and Today in Music/new-release tie-ins in the final script.
