---
name: kzsu-show-build
description: Build the final show package for DJ Stace's "The Library" on KZSU 90.1 FM (Thursdays 6-8 p.m. PT) from the week's finished recon and plan. Syncs the plan to her YouTube Music "Air Order" edits, rewrites the reversed "Working" playlist in YouTube Music, fills labels and library tags from the KZSU Zookeeper API, FCC-screens new tracks, and writes the Zookeeper upload CSV, working_playlist.md and show_script.md, then puts them in her KZSU Google Drive folder. Use this whenever Stace asks to build, finalize, sync or rebuild the show, the Working playlist, the Zookeeper upload or the show script, or on the Thursday morning run, even if she doesn't name the skill. Do not use it for weekly recon, new-release research or picking candidates; that is a separate recon and planning skill.
---

# KZSU show build

You turn a finished weekly plan into the files DJ Stace takes into the studio. Recon and planning happen upstream, in a separate skill. This skill starts from that output and ends with three files in Google Drive and a YouTube Music playlist she can play.

## What you start with and what you deliver

**Input**, from the recon and planning skill, in the project repo (`KZSU-Library-Show`):
- `data/recon/<show date>/working_playlist.json`: the plan, grouped into sets. See `references/data_format.md` for the fields.
- `data/daily/feedback.json`: her taste feedback so far.
- The YouTube Music "Air Order" playlist, which she edits by hand. **Her edits are the source of truth.**

**Deliverables**, all in `outputs/recon/<show date>/` and then copied to Google Drive:
1. `working_zookeeper_upload.csv`: the Zookeeper import file.
2. `working_playlist.md`: the track table with preview links, labels and FCC notes.
3. `show_script.md`: the on-air script with sets, talk breaks and the checklist.
4. The YouTube Music "Working" playlist, rewritten to match Air Order in reverse.

The show date is the upcoming Thursday. If today is Thursday, it's today. Use the newest `data/recon/<date>/` folder that matches.

## Playlists

Both live in Stace's signed-in Chrome. Both are Public, with Collaborate on.

| Playlist | ID | Order | You may |
|---|---|---|---|
| DJ Stace library show Air Order | `PLSosF7JAIkaM` | Forward, first on-air track at the top | **Read only.** Never add, remove or reorder. |
| DJ Stace library show working | `PLLXFGCRcu_qc` | **Reversed**, first on-air track at the bottom | Add, remove, reorder |

Working is reversed because Stace plays it bottom-up with autoplay off, so each track stops when it ends.

**Use music.youtube.com only.** Don't use www.youtube.com, not even for its "Move to top" menu. Stace has been clear about this. If a step seems to need youtube.com, stop and ask her.

## Workflow

### 1. Load the plan
- Read `working_playlist.json` and `feedback.json`.
- Load the Chrome tools with a single ToolSearch call: tabs_context, tabs_create, navigate, javascript_tool, computer, find.

### 2. Read Air Order
- Open `https://music.youtube.com/playlist?list=PLSosF7JAIkaM`.
- Scroll until the row count stops growing.
- Collect title, artist and videoId for each row, in order. Use the reader in `references/browser_js.md`.
- Check the count against the header, for example "39 tracks."

### 3. Diff and log her edits
Compare Air Order with the plan's airable tracks. Airable means priority is not SKIP or CUT, and `ytm_missing` is not set. Also check feedback.json, because an earlier run may already have logged some of these edits. Don't log anything twice.

- **She removed a track** because she isn't interested in it right now.
  - Set its priority to `CUT`. Keep the entry in the file.
  - Add it to feedback.json `removed` with `cooloff_until` set 60 days out.
  - Add 1 to `artist_removals`.
  - Downweight an artist only after 3 or more removals.
- **She added a track** because it fits.
  - Keep it in every automated rewrite. Never remove it.
  - Log it in `added_by_stace` with its position and set.
  - Treat its artist, label and RIYL neighbors as positive signals for later picks.
- **She moved a track.** Follow her order. If it crossed a set boundary, move it to that set.
- **videoIds:** copy each Air Order videoId into the plan. When the plan has a different ID for the same track, Air Order's ID wins.

### 4. Fill in new tracks
Each track she added needs album, label, tag, label_source and an FCC status. Put it in the set its neighbors belong to, and set `added_by: "DJ Stace"`.

**Labels and tags come from Zookeeper.** Query the API with fetch() from a `https://zookeeper.stanford.edu/` tab. See `references/browser_js.md`.
- Albums: `/api/v1/album?filter[artist]=...`
  - The match is exact and uses the library's name form, such as "Last, First" or "Band, The."
  - Open the album record and confirm the track is on it before you use its tag. For example, the library's "Killing Joke" is the 2003 album, not the 1980 one.
- Label names: follow the album's label relationship to `/api/v1/label/<id>`. You can also search `/api/v1/label?filter[name]=...`, which is exact-match.
- Source order:
  1. The library album record, which gives you the label and the tag.
  2. The Zookeeper label table.
  3. Her past spins.
  4. Web research, only if the database has nothing.
- Every track needs a label. Record where it came from in `label_source`.

**FCC screen.** Open the track's lyrics page on Genius, AZLyrics or Bandcamp in the browser and count words in the page with JavaScript. See `references/browser_js.md`.
- FCC words: shit, piss, fuck (all forms), cunt, cocksucker, cock, tits.
- Caution words: bitch, asshole, goddamn.
- Record the exact word, count and song section, for example "fuck x1 (outro)." Never quote lyric lines.
- If a new track has an FCC word:
  - Set priority `SKIP` so it stays out of the Zookeeper file.
  - Flag it prominently in your summary, since Stace added it herself.
- If no lyrics are posted, mark it `UNVERIFIED` and add a "Listen first" item to the checklist.

Don't make scripted web requests from the shell with curl or Python. Workspace policy blocks them. Do all web and API work in the browser.

### 5. Rebuild the files
- Run `python3 scripts/build_weekly_recon.py <show date> working_playlist.json`.
  - Run it from the repo root.
  - If the repo doesn't have the script, copy it from this skill's `scripts/` folder.
  - It writes `working_playlist.md`, `working_zookeeper_upload.csv` and `working_ytm_playlist.json`, and it leaves SKIP and CUT tracks out.
- Check the CSV:
  - It has no header row and 6 positional columns: artist, track, album, tag, label, timestamp. A 5-column file shifts durations into the label field.
  - No row has an empty label.
  - Tracks with `ytm_missing` (Bandcamp-only) stay in the CSV.
- Update `show_script.md` by hand. See `references/show_script.md` for the layout.
  - Numbering follows Air Order.
  - Set lists match the plan.
  - Rename a set whose theme depended on a cut track.
  - Rewrite any talk break that mentions a cut track. Keep the date facts that still stand on their own, and drop anything that would lead her to back-announce a song she didn't play.

### 6. Rewrite Working in YouTube Music
Stace's rule: **change only the deltas, then move tracks into position.** Don't remove and re-add tracks that are already there. It wastes time and tokens.

1. Read Working at `https://music.youtube.com/playlist?list=PLLXFGCRcu_qc`. The target is Air Order reversed.
2. **Remove** Working rows that aren't in Air Order. Use the row's "Action menu" and then "Remove from playlist."
3. **Add** Air Order tracks that are missing.
   - On the Air Order page, use the row's "Action menu," then "Save to playlist," then the `ytmusic-playlist-add-to-option-renderer` button titled "DJ Stace library show working."
   - Wait about 3.5 seconds between adds.
   - New saves land at the **top** of Working, which is the end of the show.
   - Add missing tracks in forward Air Order sequence, so later tracks land on top.
4. **Move** tracks into position. In September 2026, YouTube Music web showed no Move option and no drag handles for this collaborative playlist. So:
   - Check first whether YTM now offers a move option or drag handles. If it does, use it.
   - If it doesn't, list the out-of-place tracks for Stace. Offer two fixes: she drags them in the YTM app, or you remove and re-add only the tracks above each misplaced one. Wait for her answer. Don't switch to youtube.com.
   - Plan the adds in step 3 so that most tracks land in the right place and moves stay rare.
5. **Verify.** Reload Working. The videoId list must equal Air Order reversed, with the same count. UI removals sometimes fail without an error, so repeat the fix until it matches.

**Browser safety:**
- Click only buttons with aria-label "Action menu" and the menu items named above.
- Never click Like or Dislike. If you toggle one by accident, toggle it back.
- Toast notifications have a "Change" link. Don't click it, and don't remove the toast elements. One run jumped to another page when that happened.
- Never delete either playlist.
- Background tabs throttle `setTimeout`. Use the MessageChannel `sleep` in `references/browser_js.md`, and keep each javascript_exec call under about 35 seconds.
- If `document.visibilityState` is "hidden" and clicks or dialogs stop responding, finish the file work and ask Stace to bring the Chrome window forward.
- Close any tabs you opened.

### 7. Deliver to Google Drive
Put the three files in Stace's **KZSU** folder in Google Drive. Folder ID is `1KhuroWaBTvKo5i5voVk2iB_GwRgpfKfA`, in My Drive. Don't put them in the Drive root.
- Use the Google Drive connector (create or update file). Find it with ToolSearch, for example "google drive create file."
- Name them `<show date> working_zookeeper_upload.csv`, `<show date> working_playlist.md` and `<show date> show_script.md`.
- If files with those names are already in the folder, update them instead of creating duplicates.
- If no Drive connector is available, keep the files in `outputs/recon/<show date>/`. Tell Stace which connector to add, and share the local paths.

### 8. Summary
Keep it short: bullets, AP style, no em dashes, no hyperbole.
- Her Air Order changes: added (kept as fits), removed (logged as not currently interested) and moved.
- New FCC flags, with the word and count.
- New labels and tags, with sources.
- Final counts: Air Order, Working and CSV rows.
- Links to both playlists.
- Drive links, or local paths, for the three files.
- Anything left for her, such as tracks to drag or songs to listen to first.

## Standing rules
- Follow AP style. Don't use em dashes. Keep adjectives and hyperbole out of the script and the summaries.
- Delete only files you created. Move anything else to `_to_delete/`.
- Never reproduce lyrics.
