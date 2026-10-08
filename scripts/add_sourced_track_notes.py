#!/usr/bin/env python3
"""Append sourced track notes to Stace's finished review bodies.

What it does (for beginners):
  1. Reads each review JSON in outputs/zookeeper_upload/2026-10-08/3_reviews/.
  2. Finds each numbered track line in the review text.
  3. Adds the sourced notes from NOTES below to the END of that line,
     starting with "Sourced:" so her own words stay untouched.
  4. Writes new JSON files to 3b_reviews_sourced/ (the originals are not changed).
  5. Writes track_notes_sourced.md with every note and its URL, so she can spot-check.

All notes are short paraphrases from web search summaries. They are NOT BPM
readings. Spot-check the URLs before airing anything.

Usage: python3 scripts/add_sourced_track_notes.py
"""
import glob
import json
import os
import re

# Folder that holds the upload files for this show week.
BASE = os.path.join(os.path.dirname(__file__), "..", "outputs", "zookeeper_upload", "2026-10-08")
OUT = os.path.join(BASE, "3b_reviews_sourced")

# NOTES[album slug][track number] = list of (note text, outlet, url)
# The slug matches the start of each review file name (after the number prefix).
NOTES = {
    "twisted-teens-florida-water-blues": {
        1: [("Settles into a hypnotic pulse and leaves its central question unanswered.", "The Big Takeover", "https://bigtakeover.com/recordings/twisted-teens-florida-water-blues-chain-smoking-records")],
        3: [("Called one of the album's anchors.", "The Big Takeover", "https://bigtakeover.com/recordings/twisted-teens-florida-water-blues-chain-smoking-records")],
        4: [("Rhythmic drive pushes the record forward.", "The Big Takeover", "https://bigtakeover.com/recordings/twisted-teens-florida-water-blues-chain-smoking-records")],
        5: [
            ("Shared as a single ahead of release while the band toured with Kurt Vile & The Violators and The Breeders.", "BrooklynVegan", "https://www.brooklynvegan.com/twisted-teens-share-title-track-of-new-lp-touring-with-kurt-vile-the-breeders/"),
            ("Has a music video (August 2026).", "KLOF Mag", "https://klofmag.com/2026/08/twisted-teens-watch-the-video-for-florida-water-blues/"),
            ("Likened to a storied folk and bluegrass tune with a lo-fi garage edge.", "The Needle Drop", "https://theneedledrop.com/album-reviews/twisted-teens-florida-water-blues-album-review-szksmuf0m8k/"),
        ],
        7: [
            ("Howe Pearson on drums.", "Bandcamp credits", "https://twistedteens.bandcamp.com/album/florida-water-blues"),
            ("Calls it rollicking and apathy-laced.", "Paste", "https://www.pastemagazine.com/music/twisted-teens/twisted-teens-florida-water-blues-album-review"),
        ],
        9: [("Darcey Blye on additional vocals.", "Bandcamp credits", "https://twistedteens.bandcamp.com/album/florida-water-blues")],
        10: [("Heard as more standard country-rock.", "Elsewhere", "https://www.elsewhere.co.nz/music/11959/twisted-teens-florida-water-blues/")],
        13: [
            ("Compared to the Replacements taking on Springsteen with a country twist.", "Elsewhere", "https://www.elsewhere.co.nz/music/11959/twisted-teens-florida-water-blues/"),
            ("Darcey Blye on additional vocals.", "Bandcamp credits", "https://twistedteens.bandcamp.com/album/florida-water-blues"),
        ],
    },
    "this-is-lorelei-the-singer-in-my-band": {
        1: [
            ("Called a stripped-down, emotional goodbye.", "Paste", "https://www.pastemagazine.com/music/this-is-lorelei/this-is-lorelei-the-singer-in-my-band-review"),
            ("Low register in the chorus nods to Stephin Merritt of the Magnetic Fields.", "Spectrum Culture", "https://spectrumculture.com/2026/09/13/this-is-lorelei-the-singer-in-my-band-review/"),
        ],
        2: [
            ("Heavily indebted to Alex G, darker and grungier.", "NME", "https://www.nme.com/reviews/album/this-is-lorelei-the-singer-in-my-band-review-3967539"),
            ("Sounds like a different This Is Lorelei album, with heavier guitars.", "Northern Transmissions", "https://northerntransmissions.com/this-is-lorelei-the-singer-in-my-band/"),
        ],
        3: [
            ("Lead single. Uptempo yet melancholy, built on keys, drums and acoustic guitar.", "Americana Highways", "https://americanahighways.org/2026/09/09/review-this-is-lorelei-the-singer-in-my-band/"),
            ("Framed as immortalising a karaoke legend.", "Beats Per Minute", "https://beatsperminute.com/this-is-lorelei-immortalises-a-karaoke-legend-on-billy-came-back-from-new-album/"),
        ],
        4: [
            ("Called jaunty and rootsy.", "NME", "https://www.nme.com/reviews/album/this-is-lorelei-the-singer-in-my-band-review-3967539"),
            ("Upbeat bluegrass track with a scratchy fiddle pushed back in the mix.", "Exclaim!", "https://exclaim.ca/music/article/this-is-lorelei-the-singer-in-my-band-album-review"),
        ],
        5: [
            ("Electric guitar arpeggio in the vein of Jackson Browne and early Eagles in the verses.", "Exclaim!", "https://exclaim.ca/music/article/this-is-lorelei-the-singer-in-my-band-album-review"),
            ("Layers of harmony, gentler than the tracks before it.", "Song Bar", "https://www.song-bar.com/album-releases/this-is-lorelei-the-singer-in-my-band-album-review"),
        ],
        6: [
            ("Amos's father, bluegrass musician Bob Amos, plays banjo, and his sister Sarah sings backing vocals.", "Paste", "https://www.pastemagazine.com/music/this-is-lorelei/this-is-lorelei-the-singer-in-my-band-review"),
            ("Called the rambling, country-flecked title track.", "NME", "https://www.nme.com/reviews/album/this-is-lorelei-the-singer-in-my-band-review-3967539"),
        ],
        7: [
            ("Fingerstyle piece in an odd time signature.", "Paste", "https://www.pastemagazine.com/music/this-is-lorelei/this-is-lorelei-the-singer-in-my-band-review"),
            ("Brief instrumental of guitar and violin.", "Song Bar", "https://www.song-bar.com/album-releases/this-is-lorelei-the-singer-in-my-band-album-review"),
        ],
        8: [
            ("Called the twangiest stretch in the Lorelei catalog.", "Paste", "https://www.pastemagazine.com/music/this-is-lorelei/this-is-lorelei-the-singer-in-my-band-review"),
            ("Soaring string arrangement.", "Archynewsy", "https://www.archynewsy.com/this-is-lorelei-finds-hope-and-roots-in-the-singer-in-my-band/"),
        ],
        9: [
            ("Single with a video directed by Spencer Kelly, following kids cheering on a demolition derby racer.", "Alt Press", "https://www.altpress.com/this-is-lorelei-the-kid-with-the-crown-video-watch/"),
            ("Called the country-fried hot rod of the album.", "Paste", "https://www.pastemagazine.com/music/this-is-lorelei/this-is-lorelei-the-singer-in-my-band-review"),
            ("Layered choruses inspired by Gordon Lightfoot's production.", "Sister Ray", "https://sisterray.co.uk/collections/exclusives/products/the-singer-in-my-band"),
        ],
        10: [
            ("Bluegrass song about jilted lovers.", "Paste", "https://www.pastemagazine.com/music/this-is-lorelei/this-is-lorelei-the-singer-in-my-band-review"),
            ("Built on baritone guitar, with a verse from Al Nardo, Amos's Water From Your Eyes bandmate.", "Americana Highways", "https://americanahighways.org/2026/09/09/review-this-is-lorelei-the-singer-in-my-band/"),
        ],
        11: [
            ("Closer slows everything down.", "NME", "https://www.nme.com/reviews/album/this-is-lorelei-the-singer-in-my-band-review-3967539"),
            ("Strummed electric intro giving way to a promise of comfort.", "Americana Highways", "https://americanahighways.org/2026/09/09/review-this-is-lorelei-the-singer-in-my-band/"),
        ],
    },
    "little-barrie-gravity-freeze": {
        1: [
            ("First single. Cadogan started from the bass line, wanting an upright bass sound.", "The Listening Post", "https://thelisteningpostblog.wordpress.com/2026/02/27/song-of-the-day-little-barrie-more-bad-miles-of-road/"),
            ("Stark, menacing blues-rock with standup bass.", "AllMusic", "https://www.allmusic.com/album/gravity-freeze-mw0004772789"),
        ],
        2: [("Fuzz-heavy, with dappled psychedelia.", "Tinnitist", "https://tinnitist.com/2026/05/21/albums-of-the-week-little-barrie-gravity-freeze/")],
        3: [
            ("Nearly pretty ballad with a tenderness the rest of the record lacks.", "AllMusic", "https://www.allmusic.com/album/gravity-freeze-mw0004772789"),
            ("Wistful, Shuggie Otis-styled.", "Tinnitist", "https://tinnitist.com/2026/05/21/albums-of-the-week-little-barrie-gravity-freeze/"),
            ("Backing vocals by Holly Quin-Ankrah and Frida Touray.", "Bandcamp credits", "https://littlebarrie.bandcamp.com/album/gravity-freeze"),
        ],
        4: [("Named an album highlight.", "Song Bar", "https://www.song-bar.com/album-releases/little-barrie-gravity-freeze-album-review")],
        5: [
            ("Laid-back and swaying, guitar moving between mellow strumming and murky soloing.", "AllMusic", "https://www.allmusic.com/album/gravity-freeze-mw0004772789"),
            ("1960s-style fuzz bass as a subtle hook.", "Derek See", "https://dereksee.substack.com/p/album-of-the-week-little-barrie-gravity"),
        ],
        6: [("Slow shuffle showing Cadogan's take on his blues influences.", "Bucks Music Group", "https://www.bucksmusicgroup.com/artists/418-little-barrie")],
        7: [("Open space for gnarly guitar workouts and nimble, almost flamenco-style picking.", "AllMusic", "https://www.allmusic.com/album/gravity-freeze-mw0004772789")],
        8: [
            ("Chugging steam-train rhythm.", "Song Bar", "https://www.song-bar.com/album-releases/little-barrie-gravity-freeze-album-review"),
            ("Cadogan wanted a hypnotic, almost dance-like feel with swampy guitar over Tony Coote's steady groove.", "Tinnitist", "https://tinnitist.com/2026/05/21/albums-of-the-week-little-barrie-gravity-freeze/"),
            ("Co-producer Rupert Lyddon plays synth.", "Bandcamp credits", "https://littlebarrie.bandcamp.com/album/gravity-freeze"),
        ],
        9: [
            ("Title refers to sleep paralysis, per Cadogan.", "Guitar World", "https://www.guitarworld.com/artists/guitarists/little-barrie-gravity-freeze"),
            ("Subdued soundtrack for a bad dream.", "AllMusic", "https://www.allmusic.com/album/gravity-freeze-mw0004772789"),
        ],
    },
    "palace-ox": {
        1: [
            ("Heavy bassline, siren-like distant synths and calm vocals over darker passages.", "Silent Radio", "https://www.silentradio.co.uk/09/22/album-review-palace-ox/"),
            ("Single. Official visualiser on YouTube.", "YouTube (Palace)", "https://www.youtube.com/watch?v=8lorsmaUvFM"),
        ],
        2: [
            ("Fatherhood felt through absence, a touring musician longing for home.", "Silent Radio", "https://www.silentradio.co.uk/09/22/album-review-palace-ox/"),
            ("Single on Palace Presents, with an official video.", "YouTube", "https://www.youtube.com/watch?v=1I6zyErRijo"),
        ],
        4: [("Gentle, tender melody, but called poorly placed in the sequence.", "Silent Radio", "https://www.silentradio.co.uk/09/22/album-review-palace-ox/")],
        6: [
            ("Where the album's nostalgia is most vivid, recalling So Long Forever and Life After.", "Silent Radio", "https://www.silentradio.co.uk/09/22/album-review-palace-ox/"),
            ("Official visualiser on YouTube.", "YouTube (Palace)", "https://www.youtube.com/watch?v=_eq6opimTZs"),
        ],
        10: [
            ("Restless, with changes in tempo and key. Matt Hodges' drums hold a steady pulse.", "Silent Radio", "https://www.silentradio.co.uk/09/22/album-review-palace-ox/"),
        ],
    },
    "dread-spectre-council-thetans": {
        2: [
            ("Starts as a slow, drum-driven ballad-like song, then shifts to moody, anthemic indie rock.", "Glide Magazine", "https://glidemagazine.com/316196/listen-dread-spectre-council-powers-through-different-moods-on-explosive-hooves-cloves/"),
            ("Chiming fuzz, lo-fi charm. Channels Sub Pop-era Sebadoh with Mary Timony's melodic grit.", "Last Day Deaf", "https://lastdaydeaf.com/listening-now-dread-spectre-council-hooves-cloves/"),
        ],
    },
    "sluice-companion": {
        1: [
            ("Single ahead of the album. Reflection on community, belonging and time stood still.", "The Line of Best Fit", "https://www.thelineofbestfit.com/tracks/sluice-beadie-community-belonging-time-stood-still"),
        ],
        4: [("Singled out as a standout.", "The Ugly Hug", "https://uglyhug.com/2026/04/08/companion-by-sluice-album-review-guest-list-vol-101/")],
        7: [
            ("Eight-minute, sludgy vocoder piece built on a Thomas Merton prayer.", "Mtn. Laurel Recording Co.", "https://www.mtnlaurelrecordingco.com/artists/sluice"),
            ("Prayer is from Merton's Thoughts in Solitude (1956). Ends with about 90 seconds of field recording from outside the Abbey of Gethsemani, Kentucky.", "Matter News", "https://matternews.org/culture/music/sluice-is-still-figuring-things-out/"),
        ],
    },
    "tricky-different-when-its-silent": {
        1: [
            ("Called too close to a blunted Maxinquaye outtake.", "Metacritic excerpt", "https://www.metacritic.com/music/different-when-its-silent/tricky"),
            ("Featuring Mitch Sanders.", "Bandcamp credits", "https://tricky.bandcamp.com/album/different-when-its-silent-2"),
        ],
        2: [("Tricky and Mitch Sanders build great walls of electric sound.", "Metacritic excerpt", "https://www.metacritic.com/music/different-when-its-silent/tricky")],
        3: [("Featuring Mitch Sanders and Run Red Rambo.", "Bandcamp credits", "https://tricky.bandcamp.com/album/different-when-its-silent-2")],
        4: [("Featuring Mitch Sanders.", "Bandcamp credits", "https://tricky.bandcamp.com/album/different-when-its-silent-2")],
        5: [("Featuring Mitch Sanders.", "Bandcamp credits", "https://tricky.bandcamp.com/album/different-when-its-silent-2")],
        6: [("Abrasive vocals, too short for the verses to land.", "Northern Transmissions", "https://northerntransmissions.com/different-when-its-silent-tricky/")],
        7: [("Cathartic dirge: quivering organ and flickering pulse interrupted by noisy guitar.", "AllMusic", "https://www.allmusic.com/album/different-when-its-silent-mw0004800881")],
        8: [("Read as a plea for understanding and empathy.", "AllMusic", "https://www.allmusic.com/album/different-when-its-silent-mw0004800881")],
        9: [("Tricky experimenting with instrumental textures.", "Northern Transmissions", "https://northerntransmissions.com/different-when-its-silent-tricky/")],
        10: [("Guest rapper Radana brings the genre's raw power to a nod to trip-hop's past.", "AllMusic", "https://www.allmusic.com/album/different-when-its-silent-mw0004800881")],
        11: [("Only Mitch's vocals, plus piano, violins and a vocal choir.", "AllMusic", "https://www.allmusic.com/album/different-when-its-silent-mw0004800881")],
        12: [("Grouped with Marinade as instrumental-texture experiments.", "Northern Transmissions", "https://northerntransmissions.com/different-when-its-silent-tricky/")],
        13: [("Acoustic arrangement that leans almost into folk.", "AllMusic", "https://www.allmusic.com/album/different-when-its-silent-mw0004800881")],
        14: [
            ("First single, featuring Marta Zlakowska. Video directed by Steve Gullick.", "Joy of Violent Movement", "https://joyofviolentmovement.com/new-video-tricky-teams-up-with-marta-zlakowska-on-breakneck-out-of-place/"),
            ("Punkish rush that fades out as abruptly as it begins.", "AllMusic", "https://www.allmusic.com/album/different-when-its-silent-mw0004800881"),
        ],
    },
    "ty-segall-chrome": {
        1: [("Hypnotic synth loop and some of the album's best guitar playing.", "Treble Zine", "https://www.treblezine.com/ty-segall-chrome-review/")],
        2: [
            ("Sudden shift out of heavy garage psych into a spacious, swirling break before the choruses.", "Louder Than War", "https://louderthanwar.com/album-of-the-week-ty-segall-chrome-review/"),
            ("Gritty guitar strum, big low end from Mikal Cronin's bass, experimental-era Beatles echoes.", "New Noise Magazine", "https://newnoisemagazine.com/reviews/album-review-ty-segall-chrome/"),
        ],
        3: [
            ("Lead single, with a video of Segall's regrouped band.", "Consequence", "https://consequence.net/2026/06/ty-segall-chrome-new-album-black-paint-stream/"),
            ("Catchy riff-bomb under two minutes, twin-guitar attack, heavy fuzz.", "Stereogum", "https://stereogum.com/2501798/ty-segall-announces-new-album-chrome-new-ep-love-fuzzz-hear-black-paint/music"),
        ],
        4: [
            ("Proggy, metallic, with a guitar-duel breakdown in the middle.", "AllMusic", "https://www.allmusic.com/album/chrome-mw0004830432"),
            ("Mikal Cronin's bass in deep modulating fuzz anchors the vocals.", "Louder Than War", "https://louderthanwar.com/album-of-the-week-ty-segall-chrome-review/"),
        ],
        5: [
            ("Rambling psych-rock ballad where the keyboards shine.", "AllMusic", "https://www.allmusic.com/album/chrome-mw0004830432"),
            ("Mid-pace grunge verses on a slightly bouncing riff.", "New Noise Magazine", "https://newnoisemagazine.com/reviews/album-review-ty-segall-chrome/"),
        ],
        6: [("Bends toward straight-up 1960s American garage rock.", "New Noise Magazine", "https://newnoisemagazine.com/reviews/album-review-ty-segall-chrome/")],
        7: [("The album's dirtiest riff, with warped production.", "Far Out Magazine", "https://faroutmagazine.co.uk/ty-segall-chrome-album-review/")],
        8: [("Paired with Let Go as 1990s Seattle spirit mixed with Beatles filtered through Zappa.", "New Noise Magazine", "https://newnoisemagazine.com/reviews/album-review-ty-segall-chrome/")],
        9: [
            ("Starts aggressive, then stretches into a classic-rock groove and a psychedelic jam.", "The Fire Note", "https://thefirenote.com/reviews/ty-segall-chrome-album-review/"),
            ("Called a dirty, dusty \"ZZ Kraut boogie\".", "Treble Zine", "https://www.treblezine.com/ty-segall-chrome-review/"),
        ],
    },
    "lex-walton-ultimate-love-forever": {
        2: [
            ("Walton says she aimed for a Wolf Parade sound. Violin by Sarah Neufeld of Arcade Fire, produced by Dan Boeckner.", "Last Donut of the Night", "https://last-donut-of-the-night.ghost.io/lex-walton-on-hipster-runoff-the-strokes-castration-movie-and-the-scourge-of-millennial-nihilism/"),
            ("Framed as Suicide-meets-Wolf Parade blog-rock.", "Paste", "https://www.pastemagazine.com/music/best-new-songs/best-new-songs-august-27-2026"),
        ],
        4: [("Vinyl includes an exclusive remix of this track featuring Devi McCallion.", "Sub Pop", "https://www.subpop.com/releases/lex_walton/ultimate_love_forever")],
        6: [("Official video shot by Walton and Lev Heftler the day after her apartment burned down.", "Sub Pop", "https://www.subpop.com/news/2026/09/21/watch_lex_waltons_new_official_video_for_adrian_borland_will_have_his_revenge_on_london")],
    },
}

# Blame the Clown is already in Zookeeper, so its notes go only in the markdown file.
BLAME_THE_CLOWN = {
    3: [("Chugging, voltage-starved licks breaking anxiously.", "Paste", "https://www.pastemagazine.com/music/twisted-teens/twisted-teens-blame-the-clown-album-review")],
    4: [("Called a romp with a white-hot melody.", "Paste", "https://www.pastemagazine.com/music/twisted-teens/twisted-teens-blame-the-clown-album-review")],
    5: [("Urgency with a chorus that sticks.", "The Fire Note", "https://thefirenote.com/reviews/twisted-teens-blame-the-clown-album-review/")],
    7: [("Blues-rock swing interrupted by digital artifacts.", "The Big Takeover", "https://bigtakeover.com/recordings/twisted-teens-blame-the-clown-jazz-life-chain-smoking-records")],
    8: [("Easy-going lollop that changes the album's flow.", "Kristan Reed", "https://kristanreed.substack.com/p/review-twisted-teensblame-the-clown")],
    10: [("Near shoegaze, with whammy-bar slides over country twang.", "The Big Takeover", "https://bigtakeover.com/recordings/twisted-teens-blame-the-clown-jazz-life-chain-smoking-records")],
    11: [("Slower song that lets the arrangement breathe.", "The Fire Note", "https://thefirenote.com/reviews/twisted-teens-blame-the-clown-album-review/")],
    12: [("Cameron Snyder on synths and percussion.", "The Big Takeover", "https://bigtakeover.com/recordings/twisted-teens-blame-the-clown-jazz-life-chain-smoking-records")],
}


def sourced_text(items):
    """Join note tuples into one 'Sourced: ...' string for the end of a track line."""
    parts = [f"{text.rstrip('.')} ({outlet})" for text, outlet, _ in items]
    return "Sourced: " + "; ".join(parts) + "."


def main():
    os.makedirs(OUT, exist_ok=True)
    md = ["# Sourced track notes, week of 2026-10-08", "",
          "Paraphrases from web search summaries. Not BPM readings. Spot-check links before airing.", ""]

    for path in sorted(glob.glob(os.path.join(BASE, "3_reviews", "*.json"))):
        name = os.path.basename(path)
        slug = re.sub(r"^\d+_", "", name[:-5])  # strip the number prefix and .json
        notes = NOTES.get(slug, {})
        doc = json.load(open(path))
        text = doc["data"]["attributes"]["review"]

        new_lines = []
        for line in text.split("\r\n"):
            m = re.match(r"^(\d+)\. ", line)  # a track line starts with "N. "
            if m and int(m.group(1)) in notes:
                line = line.rstrip() + " " + sourced_text(notes[int(m.group(1))])
            new_lines.append(line)
        review = "\r\n".join(new_lines)
        # Stace's rule (Oct. 8, 2026): no "Pace: ____." or "[notes]" placeholders in reviews.
        review = review.replace("Pace: ____. ", "").replace(" [notes]", "")
        doc["data"]["attributes"]["review"] = review

        json.dump(doc, open(os.path.join(OUT, name), "w"), indent=1)

        md.append(f"## {slug}")
        for n in sorted(notes):
            for text_, outlet, url in notes[n]:
                md.append(f"- Track {n}: {text_} [{outlet}]({url})")
        md.append("")

    md.append("## twisted-teens-blame-the-clown (already in Zookeeper, notes not applied)")
    for n in sorted(BLAME_THE_CLOWN):
        for text_, outlet, url in BLAME_THE_CLOWN[n]:
            md.append(f"- Track {n}: {text_} [{outlet}]({url})")

    open(os.path.join(OUT, "track_notes_sourced.md"), "w").write("\n".join(md) + "\n")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
