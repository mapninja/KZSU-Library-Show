#!/usr/bin/env python3
"""Write five review-research JSON files by hand (Oct. 8, 2026 run).

Why by hand: the sandbox blocked Deezer, MusicBrainz and Discogs, so scripts/album_lookup.py
could not fill these in. The facts below come from Bandcamp, Wikipedia, YouTube Music and
press pages read in the browser, and the FCC counts come from Genius pages read in the
browser (counts only, no lyrics are stored).

After this runs, make the Markdown templates with:
    python3 scripts/review_boilerplate.py outputs/reviews/research/<slug>.json --overwrite

BPM is blank on purpose (no BPM source was reachable), so every track prints "Pace: ____."
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "outputs" / "reviews" / "research"


def tracks(rows):
    """rows = [(runtime, title, fcc, notes), ...] -> list of track dicts numbered from 1."""
    out = []
    for i, (runtime, title, fcc, notes) in enumerate(rows, start=1):
        out.append({"num": i, "title": title, "runtime": runtime, "bpm": None, "pace": "",
                    "fcc": fcc, "notes": notes})
    return out


UNVERIFIED = "UNVERIFIED"   # no lyrics posted anywhere we could read
CLEAN = "CLEAN"

ALBUMS = {}

# ---------------------------------------------------------------- Bill Callahan
ALBUMS["bill-callahan-my-days-of-58"] = {
    "artist": "Bill Callahan", "album": "My Days of 58", "label": "Drag City",
    "release_date": "2026-02-27",
    "release_notes": [
        "Eighth album under his own name and his first since 2022's YTILAER; the title refers to his age while writing.",
        "Recorded at Cedar Creek Studios in Austin, Texas, with his YTILAER touring band: Matt Kinsey - guitar; Dustin Laurenzi - saxophone; Jim White - drums.",
        "12 songs, about 61 minutes. Callahan has called it a \"living room record\" (AllMusic).",
        "Drag City cat. DC964 (LP).",
    ],
    "pull_quotes": [{"text": "facing down mortality with his signature candor and sense of humor",
                     "source": "Slant",
                     "url": "https://www.slantmagazine.com/music/bill-callahan-my-days-of-58-album-review/"}],
    "draft_comment": "Deadpan baritone storytelling from the guy who used to be Smog, with Jim White on drums. Lived-in, low-key, a little jazzy.",
    "riyl_suggestions": ["Smog", "Bonnie \"Prince\" Billy", "Leonard Cohen", "Silver Jews", "Lambchop"],
    "tracks": tracks([
        ("6:58", "Why Do Men Sing", CLEAN, "Opener. Reviewers hear Lou Reed as a spirit guide (KLOF, The Line of Best Fit)."),
        ("3:42", "The Man I'm Supposed To Be", CLEAN, ""),
        ("6:03", "Pathol O.G.", CLEAN, ""),
        ("7:23", "Stepping Out For Air", CLEAN, "Over 7 minutes."),
        ("5:10", "Lonely City", CLEAN, "Called a love song to Austin (The Line of Best Fit). AllMusic picks it among the stronger tracks."),
        ("5:19", "Empathy", CLEAN, ""),
        ("4:51", "West Texas", "FCC cock x1", ""),
        ("3:47", "Computer", CLEAN, ""),
        ("3:51", "Lake Winnebago", CLEAN, ""),
        ("4:47", "Highway Born", CLEAN, "Western swing-tinged road song (AllMusic)."),
        ("4:25", "And Dream Land", CLEAN, ""),
        ("4:29", "The World is Still", CLEAN, ""),
    ]),
    "sources": [
        "https://billcallahan.bandcamp.com/album/my-days-of-58",
        "https://www.slantmagazine.com/music/bill-callahan-my-days-of-58-album-review/",
        "https://www.allmusic.com/album/my-days-of-58-mw0004659238",
        "https://echoesanddust.com/2026/04/bill-callahan-my-days-of-58/",
        "https://thefirenote.com/reviews/bill-callahan-my-days-of-58-album-review/",
        "https://rateyourmusic.com/release/album/bill-callahan/my-days-of-58.p/",
        "Lyrics screened on Genius (counts only): https://genius.com/Bill-callahan-west-texas-lyrics",
    ],
    "links": {"ytm": "https://music.youtube.com/browse/MPREb_4a1518pLlpA"},
}

# ---------------------------------------------------------------- Mandy, Indiana
ALBUMS["mandy-indiana-urgh"] = {
    "artist": "Mandy, Indiana", "album": "URGH", "label": "Sacred Bones",
    "release_date": "2026-02-06",
    "release_notes": [
        "Manchester and Berlin quartet: Valentine Caulfield - vocals; Scott Fair - guitar, production; Simon Catling - synth; Alex Macdougall - drums.",
        "Second album and first for Sacred Bones (debut: i've seen a way, 2023). Co-production from Gilla Band's Daniel Fox (POST-TRASH). Stereogum named it album of the week.",
        "Written during a residency at a studio house outside Leeds, recorded in Berlin and Greater Manchester.",
        "10 tracks, about 35 minutes. Reviews say much of it is sung in French.",
    ],
    "pull_quotes": [{"text": "bracing, anxious, and important listen", "source": "POST-TRASH",
                     "url": "http://post-trash.com/news/2026/2/27/mandy-indiana-urgh-album-review"}],
    "draft_comment": "Industrial, noisy, electronic-body-music post-punk from Manchester by way of Berlin, mostly sung in French. If you like Model/Actriz or Special Interest, start here.",
    "riyl_suggestions": ["Model/Actriz", "Special Interest", "Kim Gordon", "TR/ST", "Sextile"],
    "tracks": tracks([
        ("2:22", "Sevastopol", CLEAN, "Opener."),
        ("3:30", "Magazine", CLEAN, "First single (The Indie Scene)."),
        ("2:32", "try saying", CLEAN, ""),
        ("3:22", "Dodecahedron", "FCC piss x1 (Verse)", ""),
        ("3:05", "A Brighter Tomorrow", CLEAN, ""),
        ("4:19", "Life Hex", CLEAN, ""),
        ("3:58", "ist halt so", CLEAN, ""),
        ("3:25", "Sicko! ft. billy woods", CLEAN, "Features billy woods. Named an album highlight in reviews."),
        ("4:26", "Cursive", CLEAN, "Second single. Stereogum calls it the closest thing to a club jam."),
        ("3:29", "I'll Ask Her", "FCC fuck x30 (Chorus x16, Bridge x13, 1 unlabeled), shit x1 (Verse 2). Caution bitch x1", "Closer. The Alternative reads it as an attack on misogyny in the music industry."),
    ]),
    "sources": [
        "https://mandyindiana.bandcamp.com/album/urgh",
        "http://post-trash.com/news/2026/2/27/mandy-indiana-urgh-album-review",
        "https://www.sacredbonesrecords.com/products/sbr-373-mandy-indiana-urgh",
        "https://everythingisnoise.net/reviews/mandy-indiana-urgh/",
        "https://www.godisinthetvzine.co.uk/2026/01/30/mandy-indiana-urgh-sacred-bones-records/",
        "Lyrics screened on Genius (counts only): https://genius.com/Mandy-indiana-ill-ask-her-lyrics",
    ],
    "links": {"ytm": "https://music.youtube.com/browse/MPREb_WV271L0w9kp"},
}

# ---------------------------------------------------------------- Viagra Boys
ALBUMS["viagra-boys-viagr-aboys"] = {
    "artist": "Viagra Boys", "album": "viagr aboys", "label": "Shrimptech Enterprises",
    "release_date": "2025-04-25",
    "release_notes": [
        "Fourth album from the Stockholm band, and the first on their own Shrimptech Enterprises. Produced by the band and Pelle Gunnerfeldt.",
        "Sebastian Murphy - vocals; Oskar Carls - guitar, saxophone; Linus Hillborg - guitar; Henrik Höckert - bass; Elias Jungqvist - synthesizer; Tor Sjödén - drums.",
        "Singles: Man Made of Meat (Jan. 23, 2025), Uno II (Feb. 27) and The Bog Body (Mar. 24). Murphy calls the record \"a bit simple and stupid.\"",
        "Standard edition is 11 tracks, 37:21. The Japanese Deluxe in the To Review playlist adds Therapy II, Middleage(d) Humanoid, Watching You and Cumboy (bonus tracks not screened).",
    ],
    "pull_quotes": [{"text": "the inner workings of a corroded mind in musical form", "source": "The Skinny",
                     "url": "https://www.theskinny.co.uk/music/reviews/albums/viagra-boys-viagr-aboys"}],
    "draft_comment": "Swedish dance-punk, post-punk, art-punk weirdos back for a fourth, this time on their own label.",
    "riyl_suggestions": ["IDLES", "Amyl and the Sniffers", "Fat White Family", "Shame", "Suicide"],
    "tracks": tracks([
        ("3:09", "Man Made of Meat", CLEAN, "Lead single (Jan. 23, 2025). NME calls it a highlight."),
        ("2:53", "The Bog Body", CLEAN, "Single."),
        ("2:15", "Uno II", "FCC shit x4 (Verse 1, Bridge x2, 1 unlabeled). Caution bitch x7 (Bridge x5, Verse 1, 1 unlabeled)", "Second single (Feb. 27, 2025). Named after Murphy's Italian greyhound."),
        ("3:15", "Pyramid of Health", CLEAN, ""),
        ("3:44", "Dirty Boyz", "FCC fuck x1, shit x1 (Verse 2)", "Occult Magazine hears a return to sleazy dance-punk."),
        ("2:55", "Medicine for Horses", CLEAN, ""),
        ("2:58", "Waterboy", "FCC fuck x2 (Verse 1, Verse 2)", ""),
        ("3:35", "Store Policy", CLEAN, ""),
        ("3:53", "You N33d Me", "FCC fuck x1 (Verse 2)", ""),
        ("5:28", "Best in Show Pt. IV", CLEAN, "Longest track."),
        ("3:16", "River King", CLEAN, ""),
    ]),
    "sources": [
        "https://en.wikipedia.org/wiki/Viagr_Aboys",
        "https://www.theskinny.co.uk/music/reviews/albums/viagra-boys-viagr-aboys",
        "https://glidemagazine.com/309160/viagra-boys-announce-new-album-viagr-aboys-out-april-25th-shares-leas-single-man-made-of-meat/",
        "https://readdork.com/news/viagra-boys-new-album-single",
        "Label note: The Skinny lists Year0001; Wikipedia and Glide list Shrimptech Enterprises.",
        "Lyrics screened on Genius (counts only), tracks 1-11.",
    ],
    "links": {"ytm": "https://music.youtube.com/browse/MPREb_HktfvauKp0i"},
}

# ---------------------------------------------------------------- HELP(2)
ALBUMS["various-artists-help-2"] = {
    "artist": "Various Artists", "album": "HELP(2)", "label": "War Child Records",
    "release_date": "2026-03-06",
    "release_notes": [
        "Charity compilation for War Child, a follow-up to the 1995 HELP album. 23 tracks, about 86 minutes.",
        "Recorded mostly in one week in November 2025 at Abbey Road Studios. James Ford is executive producer; Jonathan Glazer is creative director.",
        "Contributors include Arctic Monkeys, Pulp, Wet Leg, Depeche Mode, Fontaines D.C., Big Thief, Olivia Rodrigo and Beck.",
        "The gatefold vinyl comes with a bonus Oasis live 7\" (Acquiesce, from Wembley, Sept. 28, 2025).",
        "Six covers (tracks 5, 6, 8, 12, 14, 23). Everything else is new material. Metacritic score 82.",
    ],
    "pull_quotes": [{"text": "generally more hushed and jazzier than its predecessor", "source": "Bandcamp Daily",
                     "url": "https://daily.bandcamp.com/album-of-the-day/various-artists-help-2-review"}],
    "draft_comment": "Star-studded charity comp, mostly new songs plus six covers, cut in about a week at Abbey Road with James Ford producing. Arctic Monkeys open it.",
    "riyl_suggestions": ["HELP (1995)", "Arctic Monkeys", "Wet Leg", "Pulp", "Fontaines D.C."],
    "tracks": tracks([
        ("4:19", "Arctic Monkeys - Opening Night", CLEAN, "New song. Single (Jan. 22, 2026). Reviews call it the band's first new music since 2022."),
        ("5:06", "Damon Albarn, Grian Chatten & Kae Tempest - Flags", CLEAN, "New song. Single (Feb. 12, 2026). Choir includes members of English Teacher, Pulp and Black Country, New Road."),
        ("4:29", "Black Country, New Road - Strangers", CLEAN, ""),
        ("4:31", "The Last Dinner Party - Let's Do It Again!", CLEAN, "New song. Single (Feb. 17, 2026)."),
        ("4:49", "Beth Gibbons - Sunday Morning", CLEAN, "Cover of \"Sunday Morning\" by The Velvet Underground (The Velvet Underground & Nico, 1967), written by Lou Reed and John Cale."),
        ("3:46", "Arooj Aftab & Beck - Lilac Wine", CLEAN, "Cover of \"Lilac Wine\", written by James Shelton for the 1950 Broadway revue Dance Me a Song. Earlier versions by Eartha Kitt (1953), Nina Simone (1966) and Jeff Buckley (Grace, 1994). Produced by Beck."),
        ("2:06", "King Krule - The 343 Loop", UNVERIFIED, "New song. Under 2:30."),
        ("3:20", "Depeche Mode - Universal Soldier", CLEAN, "Cover of \"Universal Soldier\", written and first recorded by Buffy Sainte-Marie (1964)."),
        ("3:58", "Ezra Collective & Greentea Peng - Helicopters", CLEAN, "New song. Single (Feb. 26, 2026)."),
        ("2:57", "Arlo Parks - Nothing I Could Hide", CLEAN, ""),
        ("3:09", "English Teacher & Graham Coxon - Parasite", CLEAN, ""),
        ("2:36", "beabadoobee - Say Yes", "FCC shit x1 (Verse 2), fuck x1 (Bridge)", "Cover of \"Say Yes\" by Elliott Smith (Either/Or, 1997). Produced by Catherine Marks."),
        ("3:23", "Big Thief - Relive, Redie", CLEAN, ""),
        ("3:34", "Fontaines D.C. - Black Boys on Mopeds", CLEAN, "Cover of \"Black Boys on Mopeds\" by Sinead O'Connor (I Do Not Want What I Haven't Got, 1990). The band chose a cover over an original."),
        ("4:32", "Cameron Winter - Warning", "FCC fuck x2", "New song. With cellist Amy Langley."),
        ("2:27", "Young Fathers - Don't Fight the Young", CLEAN, ""),
        ("4:20", "Pulp - Begging for Change", CLEAN, "New song. Single (Feb. 19, 2026)."),
        ("3:14", "Sampha - Naboo", CLEAN, ""),
        ("3:31", "Wet Leg - Obvious", CLEAN, ""),
        ("3:57", "Foals - When the War is Finally Done", CLEAN, ""),
        ("3:55", "Bat For Lashes - Carried my girl", CLEAN, ""),
        ("4:02", "Anna Calvi, Ellie Rowsell, Nilüfer Yanya & Dove Ellis - Sunday Light", CLEAN, ""),
        ("4:08", "Olivia Rodrigo - The Book of Love", CLEAN, "Cover of \"The Book of Love\" by The Magnetic Fields (69 Love Songs, 1999), written by Stephin Merritt. Graham Coxon of Blur plays on it. Closes the album."),
    ]),
    "sources": [
        "https://warchildrecords.bandcamp.com/album/help-2",
        "https://daily.bandcamp.com/album-of-the-day/various-artists-help-2-review",
        "https://en.wikipedia.org/wiki/Help(2)",
        "https://www.radiox.co.uk/news/music/war-child-help-2-album-tracklist-artists-release-date/",
        "https://variety.com/2026/music/reviews/olivia-rodrigo-cameron-winter-war-child-help2-album-review-1236681030/",
        "Lyrics screened on Genius (counts only). Track 7 had no lyrics page.",
    ],
    "links": {"ytm": "https://music.youtube.com/browse/MPREb_QeefTasdpbO"},
}

# ---------------------------------------------------------------- The Fall
ALBUMS["the-fall-post-script"] = {
    "artist": "The Fall", "album": "Post Script", "label": "Cog Sinister / Gonzo",
    "release_date": "2026-10-02",
    "release_notes": [
        "Billed as the band's final studio album. Nine tracks built from unused Mark E. Smith vocal recordings dating from 2001 to 2014. Per Louder Than War, not every vocal is Smith: Blaney sings on three tracks and Archer on a couple.",
        "Recorded and assembled by Ed Blaney and Simon \"Ding\" Archer (a former Fall bassist and engineer, 6DB studio; also worked with PJ Harvey and Pixies). Cog Sinister / Gonzo cat. COGGZ154 (LP, CD).",
        "Reports conflict on whether Smith's family and estate approved the release; his former manager Pamela Vander says she and Smith's sister did not.",
        "Announced June 2026. 9 tracks, about 44 minutes.",
    ],
    "pull_quotes": [],
    "draft_comment": "Posthumous Fall: unused Mark E. Smith vocals from 2001 to 2014, pieced into nine tracks by Ed Blaney and Simon Archer, with some added vocals from the two of them. One more Fall album, with asterisks.",
    "riyl_suggestions": ["Wire", "Gang of Four", "Magazine", "The Birthday Party", "Pavement"],
    "tracks": tracks([
        ("4:03", "30 Degrees", UNVERIFIED, "Lead single (June 12, 2026). Written by Smith with Archer and Blaney."),
        ("4:08", "So Long", UNVERIFIED, ""),
        ("5:03", "Colonel's Retreat", UNVERIFIED, ""),
        ("4:10", "A Caveat", UNVERIFIED, ""),
        ("5:32", "Final Position", UNVERIFIED, ""),
        ("4:10", "Retro Song", UNVERIFIED, ""),
        ("7:03", "Irish Northern Man", UNVERIFIED, "Over 7 minutes."),
        ("3:55", "Dehydrated", UNVERIFIED, ""),
        ("6:23", "The Book", UNVERIFIED, ""),
    ]),
    "sources": [
        "https://thequietus.com/news/the-fall-reveal-final-studio-album-post-script/",
        "https://en.wikipedia.org/wiki/Post_Script",
        "https://www.artistdirect.com/news/2026-06-14-the-fall-to-release-final-studio-album-post-script-in-september-2026",
        "https://propermusic.com/products/thefall-postscript",
        "https://newreleases.discogs.com/release/769992-the-fall-post-script-the-final-studio-album",
        "Runtimes from YouTube Music. No lyrics pages found on Genius, so no track is FCC-screened.",
    ],
    "links": {"ytm": "https://music.youtube.com/browse/MPREb_YvzLNWq7M6a"},
}

for slug, data in ALBUMS.items():
    (OUT / (slug + ".json")).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print("wrote", slug, len(data["tracks"]), "tracks")
