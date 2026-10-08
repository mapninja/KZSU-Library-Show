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

- These are the facts she pastes from Bandcamp or the label: hometown, lineup with instruments, producer, studio, mastering, guests, release date.
- Paraphrase in short plain sentences. Don't copy the label's bio.
- Keep it to about five lines. Personnel lists are fine as one line: `Name - guitar, vocals; Name - drums`.

## Track notes: VERY basic and objective

Stace asked for pace plus FCC, nothing more. Pace wording comes from her own most-used terms:

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
- No BPM anywhere: print nothing. Never add `Pace: ____.`
- **Allowed extras.** Only objective facts:
  - "Instrumental."
  - "Lead single."
  - "Features <guest>."
  - "Only track with <X> on vocals," when the credits say so.
  - Runtime oddities: "Under a minute." "Over 7 minutes."
- **FCC goes FIRST in the track comment**, before pace and any other note (Stace, Oct. 8, 2026). Use her style:
  - `FCC "shit" x2 (Verse 2).`
  - `Caution "bitch" x1 (Chorus).`
  - `FCC suspect: marked explicit, no lyrics posted.`
  - `FCC unverified: no lyrics posted.`
- No `[notes]` or `Pace: ____` placeholders. Each track line holds only: number, title, runtime, FCC flag if any, and sourced notes.

Example drafted line:

```
4. Hit the Ground Running 03:55 - FCC "fucker" x1 (Chorus). Mid to uptempo (~126 BPM).
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
- Drafts stay short (one to three sentences) and never describe songs as if heard.
- Track notes may include objective facts found in press: single and video dates, guests, covers, what a song is about, and short attributed reviewer descriptions in parentheses, e.g. "(Paste)".
- End with a plain `Sources:` list; she keeps it.
