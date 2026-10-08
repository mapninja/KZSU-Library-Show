#!/usr/bin/env python3
"""Research JSONs for two albums added Oct. 8, 2026: Teenage Fanclub and The Tallest Man on Earth.

Both albums are out Oct. 9, 2026, so no lyrics are posted yet and every track is
marked UNVERIFIED for FCC words. Re-screen after release.

Run, then render each file:
    python3 scripts/build_review_research_2026_10_08b.py
    python3 scripts/review_boilerplate.py outputs/reviews/research/<slug>.json --overwrite

Runtimes come from third-party pages (jazz-jazz.com, Boomkat, Qobuz), not the label.
Verify against Bandcamp or Zookeeper once the albums are live.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "outputs" / "reviews" / "research"
UNVERIFIED = "UNVERIFIED"  # no lyrics posted yet


def tracks(rows):
    """rows = [(runtime, title, notes), ...] -> list of track dicts numbered from 1."""
    return [{"num": i, "title": title, "runtime": runtime, "bpm": None, "pace": "",
             "fcc": UNVERIFIED, "notes": notes}
            for i, (runtime, title, notes) in enumerate(rows, start=1)]


ALBUMS = {}

# ---------------------------------------------------------------- Teenage Fanclub
ALBUMS["teenage-fanclub-do-not-dare-to-dream"] = {
    "artist": "Teenage Fanclub", "album": "Do Not Dare To Dream", "label": "Merge Records",
    "release_date": "2026-10-09",
    "release_notes": [
        "Thirteenth studio album, after Nothing Lasts Forever (2023). Merge cat. MRG892.",
        "Produced by the band. Recorded in 14 days at Black Bay Studio in Kirkibost on Great Bernera, Outer Hebrides; mixed and mastered in Glasgow by Dexter George. A church organ at the studio is on several songs.",
        "Norman Blake - vocals, guitar; Raymond McGinley - vocals, guitar; Euros Childs - keyboards, vocals; Francis Macdonald - drums; David McGowan - bass.",
        "Singles: Day In The Sun (announced July 23, 2026) and There Was You (Aug. 19), both with Donald Milne videos.",
        "10 tracks, about 39 minutes. Blake wrote 1, 4, 6, 8 and 9; McGinley wrote 2, 3, 5, 7 and 10 (Bandcamp). No covers.",
        "Out Oct. 9, 2026, so no lyrics are posted yet. All tracks are unscreened for FCC words.",
    ],
    "pull_quotes": [{"text": "wrap up sombre reflections on life in a gentle melodic glow",
                     "source": "MOJO",
                     "url": "https://www.mojo4music.com/articles/new-music/teenage-fanclub-do-not-dare-to-dream-review/"}],
    "draft_comment": "Glasgow's harmony pop veterans, recorded in 14 days in the Outer Hebrides with Euros Childs on keys. Mid-tempo, warm and Byrds-leaning.",
    "riyl_suggestions": ["Crosby, Stills, Nash & Young", "The Byrds", "Big Star", "The Beach Boys", "Cat Stevens"],
    "tracks": tracks([
        ("3:29", "There Was You", "Blake song. Second single (Aug. 19). The Indy Review hears Big Star-ish guitar pop."),
        ("5:16", "Tomorrow People", "McGinley song, the longest track. Childs adds a Solina String Ensemble (MOJO)."),
        ("4:23", "Over And Over", "McGinley song. Church organ under chiming guitars (The Indy Review)."),
        ("3:31", "Be With You Tonight", "Blake song."),
        ("4:08", "The Same Air", "McGinley song."),
        ("4:37", "I Do Not Dare To Dream", "Blake song, title track. MOJO hears CSNY; The Indy Review hears 1970s Laurel Canyon."),
        ("3:50", "Take Time", "McGinley song. Childs on Mellotron flutes; Far Out places it in 1960s psychedelic tradition."),
        ("3:10", "Day In The Sun", "Blake song. First single, with a Donald Milne video."),
        ("3:29", "Somewhere To Land", "Blake song."),
        ("3:06", "Young And Wise", "McGinley song. Closer."),
    ]),
    "sources": [
        "https://teenage-fanclub.bandcamp.com/album/do-not-dare-to-dream",
        "https://www.mergerecords.com/product/do_not_dare_to_dream",
        "https://www.mergerecords.com/news/6521",
        "https://boomkat.com/artists/teenage-fanclub/releases/a8nrazut/do-not-dare-to-dream",
        "https://www.qobuz.com/no-en/album/do-not-dare-to-dream-teenage-fanclub/mcw8fl1efniwu",
        "https://www.mojo4music.com/articles/new-music/teenage-fanclub-do-not-dare-to-dream-review/",
        "https://theindyreview.com/2026/10/07/album-review-teenage-fanclub-do-not-dare-to-dream/",
        "https://faroutmagazine.co.uk/teenage-fanclub-do-not-dare-to-dream-album-review/",
        "Runtimes from third-party listings (jazz-jazz.com, Boomkat, Qobuz). Verify once the album is live Oct. 9.",
    ],
    "links": {},
}

# ---------------------------------------------------------------- The Tallest Man on Earth
ALBUMS["the-tallest-man-on-earth-just-beyond-endless-mountain"] = {
    "artist": "The Tallest Man on Earth", "album": "Just Beyond Endless Mountain", "label": "ANTI-",
    "release_date": "2026-10-09",
    "release_notes": [
        "Eighth album from Kristian Matsson and first since Henry St. (2023). Written and produced by Matsson (Bandcamp); mastered by Huntley Miller.",
        "Recorded at home to reel-to-reel machines, including a Swiss Nagra used for vocal distortion (Glide). Matsson plays most instruments, including violins.",
        "Martin Hederos (viola, violin, piano) co-wrote and plays on Colors. Sofia HK sings on Overboda.",
        "Singles: Colors (May 27, 2026), Deliver Me From Trying (Aug. 11, the lead single and album announcement), Overboda and In The Silver Wire Up The Hill.",
        "Matsson moved back to Dalarna in central Sweden. Stereogum, Rough Trade and Consequence say the record draws on Swedish polska, fiddle and old field recordings.",
        "11 tracks, about 40 minutes. No covers found. Cover and press photo by Anton Corbijn (Stereogum).",
        "Out Oct. 9, 2026, so no lyrics are posted yet. All tracks are unscreened for FCC words.",
    ],
    "pull_quotes": [{"text": "gurgles into life with a fingerpicking pattern that follows expanding intervals",
                     "source": "Glide Magazine (on Deliver Me From Trying)",
                     "url": "https://glidemagazine.com/331323/the-tallest-man-on-earth-embraces-his-swedish-roots-on-just-beyond-endless-mountain-album-review/"}],
    "draft_comment": "Kristian Matsson back in Sweden, recorded at home on reel-to-reel with Swedish fiddle and polska in the mix. Fingerpicked folk with more band than usual.",
    "riyl_suggestions": ["Bob Dylan", "Bon Iver", "Fleet Foxes", "Sufjan Stevens"],
    "tracks": tracks([
        ("3:12", "The Wildest of His Dreams", "Opener."),
        ("5:15", "Colors", "First single. Written by Matsson and Martin Hederos; violin and guitar (JamBase)."),
        ("3:14", "We Got the Pony", ""),
        ("3:17", "Scully, It's Me", ""),
        ("4:05", "Just Beyond Endless Mountain", "Title track. Glide compares its full-band treatment to a blues stomp."),
        ("3:11", "Overboda", "Duet with Sofia HK (Apple Music)."),
        ("3:54", "Deliver Me From Trying", "Lead single (Aug. 11). BroadwayWorld cites driving guitar and propulsive drums."),
        ("3:23", "Times", ""),
        ("2:50", "The Forest Keeper", "Rhythmic strumming with ramshackle percussion (Apple Music)."),
        ("3:42", "In The Silver Wire Up The Hill", "Single with video (Northern Transmissions)."),
        ("4:10", "The Village", "Closer."),
    ]),
    "sources": [
        "https://thetallestmanonearth.bandcamp.com/album/just-beyond-endless-mountain",
        "https://glidemagazine.com/331323/the-tallest-man-on-earth-embraces-his-swedish-roots-on-just-beyond-endless-mountain-album-review/",
        "https://stereogum.com/2507950/the-tallest-man-on-earth-announces-new-album-just-beyond-endless-mountain-hear-deliver-me-from-trying/music",
        "https://consequence.net/2026/08/tallest-man-on-earth-new-album-just-beyond-endless-mountain/",
        "https://www.jambase.com/article/tallest-man-on-earth-new-album-just-beyond-endless-mountain",
        "https://northerntransmissions.com/the-tallest-man-on-earth-releases-in-the-silver-wire-up-the-hill/",
        "Runtimes from third-party listings (jazz-jazz.com). Verify once the album is live Oct. 9.",
        "RIYL names come from general career coverage, not reviews of this album.",
    ],
    "links": {},
}

for slug, data in ALBUMS.items():
    (OUT / (slug + ".json")).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print("wrote", slug, len(data["tracks"]), "tracks")
