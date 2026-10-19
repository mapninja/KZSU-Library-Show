# DJ Stace's KZSU review style

This guide is drawn from her 65 KZSU library reviews, written 2016 to 2023. Read the real ones with `SELECT review_text FROM kzsu_reviews` in `data/library_show.db`. Before drafting, skim three or four in the same genre as the album.

## Layout (the 2022-23 format she settled on)

```
Album / Artist: <Album> / <Artist>

Label: <Label>

Release Date: <Month D, YYYY>
Review Date: <M/D/YYYY>
Reviewer: DJ Stace

General Comments / Reviews:

<her one- or two-line take> - DJ Stace

"<short press quote>" - <Outlet>

Release Notes:

<facts: origin, lineup, where and by whom it was recorded, release date>

FCCs: <track numbers, or None>

RIYL: <3-5 artists>

Play: All but FCCs, Favs Rated with up to *****

Tracklist:
1. <Title> <mm:ss> - <notes>
```

- Stars are added by hand before the title: `2. **** Born Yesterday 03:22 - ...`. Leave them out of drafts. Rating is Stace's job.
- If the album has no FCC tracks, the Play line reads `Play: All, Favs Rated with up to *****`.
- The FCC line uses track numbers only: `FCCs: 4,8,11` or `FCCs: None`. The per-track notes give the word.

## General comments: her voice

- **Short.** One to three sentences, often a fragment. Recent reviews are one line.
  - "Well crafted post-punk art pop."
  - "Everything a Built To Spill fan could hope for."
  - "Contemporary, but ass-kicking alt rock. If you've been craving a Breeders album, give this a try."
- **Genre stacks.** Stacked genre adjectives with commas and hyphens: "Fuzzy, artsy, slacker rock with moments of brilliance." "Swampy, dark, bluesy, sometimes trip-hoppy."
- **Comparisons.** Name the artist it evokes: "If you've been waiting for The Pixies to put out another great album..." "Reminiscent of Early Radiohead."
- **Casual and dry.** Mild swearing in her own prose is normal ("ass-kicking," "batshit"). Never hype. No "masterpiece," "stunning" or "must-hear" unless she has already written it.
- **Signature.** Her own line ends with ` - DJ Stace` when press quotes follow.

When drafting for her:

- Write **one or two sentences** in this voice, based only on facts from the research: genre, lineup, producer, comparisons critics make.
- Mark the draft `[DRAFT, edit or replace]`.
- Never describe how a song sounds as if you'd heard it. Pace notes come from BPM data. The subjective listening is hers.

## Press quotes

- Use 1 to 3 short quotes, each under 15 words, from authoritative sources. Examples: Pitchfork, Stereogum, Paste, NME, AllMusic, The Quietus, Exclaim!, Uncut, Mojo, Rolling Stone, Brooklyn Vegan, Bandcamp Daily, Aquarium Drunkard, KEXP, The Line of Best Fit, DIY, Loud and Quiet.
- Format is `"quote" - Outlet`. The opening and closing quote marks can be straight or curly.
- Quote exactly and keep each source URL in the research sources list. Don't piece quotes together from several sentences.
- Skip label press releases for quotes. Use them for release notes instead, paraphrased.

## Release notes

- Purpose (Stace, Oct. 18, 2026): a DJ should be able to play a track from the album without ever having heard it. Keep what helps a DJ and a listener place the record.
- **Keep:** lineup with instruments, producer, studio, mastering, guests, production connections (who else the producer or engineer has worked with), lineage (members' other bands, side projects, the band's earlier records, label family), and what the record is about when the band says so.
- **Drop:** release metadata. No single release dates, video dates or directors, CD versus vinyl versus digital formats, catalog numbers, chart positions, review scores or "out on <date>" lines. The Release Date field already carries the date. Mention pre-release status once in the draft comment only if the album is not out yet.
- Paraphrase in short plain sentences. Don't copy the label's bio. About four or five lines. Personnel as one line: `Name - guitar, vocals; Name - drums`.

## Track notes: FCC first, then what it sounds like

The notes exist so a DJ can pick and cue a track cold. Order inside each track comment:

1. **FCC flag first.** Exact word, count, section. This is the most important part.
2. **Tempo.** Pace word plus BPM when known (table below).
3. **Observational description.** Sound and feel: lead instruments, rhythm, mood, vocal style (male, female, shared, spoken, screamed, whispered), intro or outro (cold start, long fade, slow build), dynamics, sounds like <artist or era>. Short fragments, plain words.
4. **Radio-useful facts.** Instrumental, features <guest>, cover of <song> by <artist> (writer, year), spoken-word or sample, long intro, abrupt ending, runtime oddities.

Rules:

- Sources for descriptions: critics' track-by-track descriptions, the band's own descriptions and the audio itself when it can be heard. Attribute outside descriptions in parentheses, for example "(Paste)". Never invent a sound. If nothing credible is found, write only FCC and tempo.
- **No single or release metadata in track comments.** Cut "Lead single", "Second single (Sept. 30)", "video by...", "debuted live at...", chart and review-score talk. Say "Lead single" only if it helps the DJ choose (it does not unless Stace asks).
- Keep each comment to one or two short sentences after the FCC and tempo.

Pace wording comes from her own most-used terms:

| BPM (from Deezer, songbpm or tunebat) | Write |
|---|---|
| under 75 | Slow |
| 75-94 | Slow to midtempo |
| 95-114 | Midtempo |
| 115-129 | Mid to uptempo |
| 130-154 | Uptempo |
| 155 and up | Fast |

- Add the BPM in parentheses: `Midtempo (~108 BPM).`
- BPM data can be off by double or half. If the result contradicts an objective fact, such as a ballad listed at 150 BPM, write `Pace: check (source says ~150 BPM).`
- No BPM anywhere (common for unreleased albums): print nothing for tempo and describe the feel in words if a source supports it. Never add `Pace: ____.`
- FCC styles:
  - `FCC "shit" x2 (Verse 2).`
  - `Caution "bitch" x1 (Chorus).`
  - `FCC suspect: marked explicit, no lyrics posted.`
  - `FCC unverified: no lyrics posted.`
- No `[notes]` or `Pace: ____` placeholders. Each track line holds: number, title, runtime, FCC flag if any, tempo, short observational notes.

Example drafted lines:

```
4. Hit the Ground Running 03:55 - FCC "fucker" x1 (Chorus). Mid to uptempo (~126 BPM). Driving bass, shouted gang vocals, cold start.
7. Lake Winnebago 03:52 - Slow (~68 BPM). Acoustic guitar and baritone voice, sparse, long fade. Cover of a song by <artist> (<writer>, <year>).
```

## RIYL

- Use 3 to 5 names.
- Pull from the staged email's RIYL list first, then from critics' comparisons.
- Prefer artists in her taste profile (`config/taste_profile.json`) when they fit honestly.

## Voice notes (Oct. 2026, from her reviews in KZSU-Album-Reviews)

- Read 3 or 4 of her reviews in the KZSU-Album-Reviews repo before drafting (for example GBV-Warp&Woof.md, Fontaines DC Dogrel.md, Bodega - Shiny New Model.md, KingTuff The Other.md).
- Wry, punchy openers: "There's something wrong with Robert Pollard. This is his 4 millionth release. This year." Callbacks to her own past lines are welcome.
- Plain enthusiasm is fine ("Killer song. Play this.", "catchy as hell"), as are pop-culture comparisons and one specific image ("Put the top down and crank it down the 1.").
- Stack genre adjectives, name the band it sounds like, mention practical radio notes ("Too bad it's FCC").
- Drafts stay short (one to three sentences). The general comment can name a sound or comparison that critics make; do not claim to have heard the record.
- Track notes follow the "Track notes" section above: FCC, tempo, observational sound and feel. No single or release-date metadata (Stace, Oct. 18, 2026).
- End with a plain `Sources:` list; she keeps it.
