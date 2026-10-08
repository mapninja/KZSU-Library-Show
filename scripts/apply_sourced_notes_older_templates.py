#!/usr/bin/env python3
"""Add sourced track notes to the research JSONs of four older review templates.

Albums: Sharp Pins, Guided By Voices, Sylvan Esso, Yard Act.
These have NOT been uploaded to Zookeeper and have no edits from Stace in Drive,
so it is safe to regenerate their templates.

How it works (for beginners):
  1. Load each research JSON from outputs/reviews/research/.
  2. For each track number in NOTES, append the new text to the track's existing "notes".
  3. Append extra lines to "release_notes" (EXTRA_RELEASE_NOTES).
  4. Save the JSON. Then run review_boilerplate.py to re-render the Markdown.

Running it twice is safe: text already present is not added again.
All notes are short paraphrases from web search summaries. Spot-check before airing.
"""
import json
from pathlib import Path

RESEARCH = Path(__file__).resolve().parent.parent / "outputs" / "reviews" / "research"

# NOTES[slug][track number] = text to append to that track's notes.
NOTES = {
    "sharp-pins-mod-mayday-23": {
        1: 'Cover of "It\'s A Mod Mod World" by Squire (Mods Mayday \'79, 1979), written by Anthony Meynell (SecondHandSongs).',
        2: 'Cover of "The Face of Youth Today" by Squire (1979 UK 7-inch, per Discogs).',
        4: 'Cover of "B-A-B-Y Baby Love" by Squire (Mods Mayday \'79, 1979).',
        5: 'Original is from the live compilation Mods Mayday \'79 (May 1979, Bridge House show).',
        6: 'Cover of a Squire song (Mods Mayday \'79). Slater adds psychedelic soloing and harmonica (POST-TRASH). Bonus track on the limited CD (Bandcamp).',
        7: 'One review credits the original to Beggar, another Mods Mayday \'79 act, and hears a live-sounding recording with feedback (Pop Fantasma).',
        8: 'Cover of a song by The Mods (Mods Mayday \'79). POST-TRASH calls it and Let Me Be The One more energetic, almost punk.',
        9: 'Cover of a song by The Mods (Mods Mayday \'79). POST-TRASH: more energetic, but whimsical.',
        10: 'One of the more subdued tracks: no percussion, Slater on acoustic guitar with muffled vocals (POST-TRASH).',
        11: 'Not a cover (POST-TRASH).',
    },
    "guided-by-voices-crawlspace-of-the-pantheon": {
        1: 'ecoustics compares it to The Who and The Cars, with Mellotron strings and tight harmonies.',
        2: 'Starts with Pollard and heavy electric guitar; the full band enters about halfway (The Fire Note).',
        4: 'Announced with the album Feb. 25, 2026. Pollard says it was written in one take (Rolling Stone). Called a triumphant anthem (Maximum Volume Music).',
        5: 'Sgt. Pepper-style psych pop carnival in 1:18 (The Fire Note).',
        6: 'Builds to a strutting riff over sinister vocals (PopMatters). Some of the album\'s strongest guitar work (Maximum Volume Music).',
        7: 'Aggressive punk energy with melodic turns; GBV at their punkiest (Maximum Volume Music).',
        9: 'New Wave-leaning rocker that veers prog (Maximum Volume Music). ecoustics hears a cousin of the 1969 pre-Tommy Who.',
        10: 'Called a pretty, psychedelic ballad (PopMatters). Altrevue\'s favorite.',
        11: 'Chord sequence echoes "The Punk and the Godfather" from The Who\'s Quadrophenia (ecoustics).',
        12: 'Epic closer: heavy chugging riff, then an acoustic-driven coda (ecoustics).',
    },
    "sylvan-esso-ow": {
        1: 'Opens with a high-pitched wail that gives way to a soft melody (Plus One).',
        2: 'Reviewers read it as about a new climate normal or ongoing struggle (Song Bar, Treble).',
        3: 'Single and video June 10, 2026 (Shore Fire Media). Stereogum calls the guitar-heavy sound a surprising new direction. Song Bar hears 1990s alt rock, glam guitar and electro-pop. Drums by TJ Maiani, guitar by Jenn Wasner of Wye Oak (verify at Shore Fire or FLOOD).',
        4: 'Samples Sigur Ros\' "Svefn-g-englar" (Agaetis Byrjun, 1999) (mxdwn). Consequence calls it hazy electronic pop inspired by a surreal night out.',
        5: 'Video game synth riffs and big percussion pads (Treble). Wonky clarinet bridge (Spectrum Culture).',
        6: 'Includes an a cappella chorale (Treble).',
        7: 'Distorted guitar and a repeated chant refrain (Treble).',
        8: 'Spectrum Culture hears peace found in one\'s own collapse.',
        10: 'About the duo\'s friend Jessica, who died of sudden liver failure in 2023 (Paste).',
        11: 'Grew from a seedling in the band\'s session files (Shore Fire press).',
        12: 'Scat-style pseudo-bluegrass syllables (Treble).',
    },
    "yard-act-you-re-gonna-need-a-little-music": {
        1: 'Treble calls it the record\'s full-fledged rap moment.',
        2: 'Second single and video, June 23, 2026 (Stereogum). Rolling Stone cites muscular guitars and a shout-along chorus.',
        3: 'NME cites a wonky piano.',
        4: 'Producer ran a drum machine through the vocals (Apple Music). Line of Best Fit: vocals battle Sam Shipstone\'s crunching riffs.',
        5: 'NME cites a euphoric chorus. Rolling Stone: it glides where New Beginnings surges. Lyric video on YouTube.',
        6: 'Title nods to cherophobe, fear of happiness (Treble). DIY notes crunching vocals.',
        7: 'Apple Music: a drum \'n\' bass groove slowed down, with live drums and James Brown-style guitars. Rolling Stone calls it arguably the strongest track.',
        8: 'Apple Music calls it the heart of the album. Mojo calls it a mournful Streets shuffle.',
        9: 'Announced the album May 7, 2026 (Our Culture). BrooklynVegan calls it smouldering and bluesy, the most rock Yard Act have sounded.',
        10: 'DIY compares the mood to a Blur B-side.',
        11: 'Barroom piano and a big indie-rock chorus, ending in a rush of noise (New Noise).',
    },
}

# Extra lines for the Release Notes section.
EXTRA_RELEASE_NOTES = {
    "sharp-pins-mod-mayday-23": ["Title nods to Mods Mayday '79, a compilation from a London show with Secret Affair, Beggar, The Mods and Squire (Why Now)."],
    "guided-by-voices-crawlspace-of-the-pantheon": ["Produced by Travis Harrison (Wikipedia). Pollard says it was recorded in a studio with members living in different places (Rolling Stone)."],
    "sylvan-esso-ow": ["Written over about four years. Bandcamp says six different drummers play on it (via WUNC)."],
    "yard-act-you-re-gonna-need-a-little-music": ["Recorded between Leeds and Los Angeles. No guest artists found (NME). Outlets differ on label: Republic (Under the Radar) or Island."],
}

for slug, by_track in NOTES.items():
    path = RESEARCH / (slug + ".json")
    data = json.loads(path.read_text())
    for t in data["tracks"]:
        add = by_track.get(t["num"])
        if add and add not in t.get("notes", ""):
            old = t.get("notes", "").strip()
            t["notes"] = (old.rstrip(".") + ". " if old else "") + add
    for line in EXTRA_RELEASE_NOTES.get(slug, []):
        if line not in data["release_notes"]:
            data["release_notes"].append(line)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print("updated", slug)
