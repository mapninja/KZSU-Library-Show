#!/usr/bin/env python3
"""Write six review-research JSON files by hand (Oct. 9, 2026 run).

Why by hand: the sandbox blocks Deezer, MusicBrainz and Discogs, so scripts/album_lookup.py
returns nothing. The facts below come from Bandcamp, Wikipedia, YouTube Music and press pages
read in the browser. FCC counts come from Genius pages read in the browser (counts only,
no lyrics are stored anywhere).

After this runs, make the Markdown templates with:
    python3 scripts/review_boilerplate.py outputs/reviews/research/<slug>.json --overwrite

BPM is blank on purpose (no BPM source was reachable), so no pace text is printed.
"""
import json
from pathlib import Path

# Folder where the research JSON files are written (outputs/reviews/research).
OUT = Path(__file__).resolve().parent.parent / "outputs" / "reviews" / "research"

CLEAN = "CLEAN"            # lyrics were posted and no FCC word was found
UNVERIFIED = "UNVERIFIED"  # no lyrics posted yet, so Stace must check by ear


def tracks(rows):
    """rows = [(runtime, title, fcc, notes, genius_url), ...] -> list of track dicts numbered from 1."""
    out = []
    for i, (runtime, title, fcc, notes, src) in enumerate(rows, start=1):
        t = {"num": i, "title": title, "runtime": runtime, "bpm": None, "pace": "",
             "fcc": fcc, "notes": notes}
        if src:
            t["fcc_source"] = src  # where the lyric count came from (page link only)
        out.append(t)
    return out


def genius(artist_slug, title_slug):
    """Build a Genius lyrics page link from slugs."""
    return f"https://genius.com/{artist_slug}-{title_slug}-lyrics"


ALBUMS = {}

# ---------------------------------------------------------------- Death Valley Girls
dvg = "Death-valley-girls"
ALBUMS["death-valley-girls-welcome-to-earth"] = {
    "artist": "Death Valley Girls", "album": "Welcome to Earth", "label": "Suicide Squeeze Records",
    "release_date": "2026-10-09",
    "release_notes": [
        "Sixth album from the Los Angeles band. Written after bandleader Bonnie Bloomgarden lost her Altadena home in the Eaton Fire, and her dog Tommy soon after.",
        "Produced by Mark Rains and Bonnie Bloomgarden. Rains engineered and mixed at Station House; Stephen C Common mastered at Twin Hills Recording.",
        "Bonnie Bloomgarden - organ, Juno 60, vocals; Laena Myers - guitar, vocals; Alana Amram - bass; Bailey Chapman - drums; Sarah Safaie - saxophone; Gregg Foreman - Wurlitzer, Rhodes, synth.",
        "Guest voices include Laura Kelsey (The Kid), Seth Bogart (Hunx & His Punx), jazz singer Gretchen Parlato and a children's chorus (AllMusic, Bandcamp).",
        "9 tracks, about 27 minutes. Fire and Brimstone first came out as a 2025 single, b/w Sisters of the Moon. Final single: How Losing Everything in the Fire Taught Me to Love Myself (Oct. 5, video by Dylan Mars Greenberg).",
        "Out Oct. 9, 2026. Lyrics are posted for four of nine tracks; the other five are unscreened.",
    ],
    "pull_quotes": [
        {"text": "an especially community-minded one", "source": "AllMusic",
         "url": "https://www.allmusic.com/album/welcome-to-earth-mw0004867433"},
        {"text": "isn't your typical grief record", "source": "The Spill Magazine",
         "url": "https://spillmagazine.com/spill-album-review-death-valley-girls-welcome-to-earth/"},
    ],
    "draft_comment": "Psychedelic garage punk with a sax and a crowd of guest singers, written after the Eaton Fire. AllMusic hears it as mostly uplifting.",
    "riyl_suggestions": ["Thee Oh Sees", "The Black Angels", "L.A. Witch", "Hunx & His Punx"],
    "tracks": tracks([
        ("3:08", "Welcome to Earth", UNVERIFIED, "Opener. AllMusic hears saxophones and wah-wah guitar.", None),
        ("3:09", "Basic Witch", CLEAN, "Features Seth Bogart (AllMusic). Already on the Weekly playlist.", genius(dvg, "basic-witch")),
        ("2:50", "Plant Magic", UNVERIFIED, "AllMusic calls it a song dedicated to renewal.", None),
        ("3:45", "Sing For Yourself", UNVERIFIED, "Longest track.", None),
        ("2:42", "Message From the Venus Flower", CLEAN, "Tribute to Bloomgarden's dog Tommy (AllMusic).", genius(dvg, "message-from-the-venus-flower")),
        ("2:50", "I love you", UNVERIFIED, "", None),
        ("3:54", "Fire and Brimstone", CLEAN, "Earlier single (2025). Sarah Safaie on saxophone. The Spill Magazine calls it the best song.", genius(dvg, "fire-and-brimstone")),
        ("2:05", "Life So Far", UNVERIFIED, "Shortest track.", None),
        ("2:55", "How Losing Everything in the Fire Taught Me to Love Myself", UNVERIFIED, "Closer and final single (Oct. 5), with a Dylan Mars Greenberg video.", None),
    ]),
    "sources": [
        "https://deathvalleygirls.bandcamp.com/album/welcome-to-earth",
        "https://www.allmusic.com/album/welcome-to-earth-mw0004867433",
        "https://spillmagazine.com/spill-album-review-death-valley-girls-welcome-to-earth/",
        "https://suicidesqueeze.net/2026/10/death-valley-girls-release-welcome-to-earth-lp-this-friday-share-new-single/",
        "Lyrics screened on Genius (counts only), tracks 2, 5 and 7. Tracks 1, 3, 4, 6, 8 and 9 have no lyrics posted on Genius or LRCLIB.",
    ],
    "links": {"ytm": "https://music.youtube.com/search?q=Death+Valley+Girls+Welcome+to+Earth"},
}

# ---------------------------------------------------------------- Stef Chura
sc = "Stef-chura"
ALBUMS["stef-chura-dancing-alone-on-the-concrete"] = {
    "artist": "Stef Chura", "album": "Dancing Alone on the Concrete", "label": "Saddle Creek",
    "release_date": "2026-10-02",
    "release_notes": [
        "Third album from the Detroit songwriter and her second for Saddle Creek. First since Midnight (2019).",
        "Recorded at Chase Park Transduction in Athens, Georgia. Mixed by David Barbe (Sugar) and Andy LeMaster; mastered by Joe Lambert. Thunder and Lightning was recorded at Casa de LeMaster, with extra tracking in New Orleans (Bandcamp).",
        "Danny features Peter Buck and Mike Mills of R.E.M. (Bandcamp Daily, Brooklyn Vegan). Other guests per AllMusic: Scott Spillane (mellophone), Peter Alvanos (drums), John Fernandes (clarinet).",
        "Written on piano as well as guitar (Bandcamp Daily).",
        "9 tracks, about 27 minutes. Opens for Dinosaur Jr. on Oct. 18 and 19.",
    ],
    "pull_quotes": [
        {"text": "Songs are more suave and notably less punk.", "source": "Bandcamp Daily",
         "url": "https://daily.bandcamp.com/album-of-the-day/stef-chura-dancing-alone-on-the-concrete-review"},
    ],
    "draft_comment": "Detroit punk-turned-piano-and-guitar songwriter, recorded in Athens with R.E.M. alumni on Danny. Short, smoother and less scrappy than Midnight.",
    "riyl_suggestions": ["R.E.M.", "Waxahatchee", "Courtney Barnett", "The Apples in Stereo", "Sleater-Kinney"],
    "tracks": tracks([
        ("2:48", "Leadweight", CLEAN, "Opener.", genius(sc, "leadweight")),
        ("4:07", "The Concrete", CLEAN, "Longest track.", genius(sc, "the-concrete")),
        ("2:29", "Babydoll", CLEAN, "", genius(sc, "babydoll")),
        ("3:09", "Lovesick", CLEAN, "Piano ballad with no drums (Bandcamp Daily).", genius(sc, "lovesick")),
        ("2:52", "Wishin'", CLEAN, "", genius(sc, "wishin")),
        ("1:58", "Thunder and Lightning", CLEAN, "Shortest track. Organ and drum machine (Bandcamp Daily).", genius(sc, "thunder-and-lightning")),
        ("3:35", "Danny", CLEAN, "Lead single. Features Peter Buck and Mike Mills of R.E.M. Bandcamp Daily calls it the best song.", genius(sc, "danny")),
        ("2:56", "Be My Hound", CLEAN, "", genius(sc, "be-my-hound")),
        ("3:16", "Heavy Hitter", CLEAN, "Closer.", genius(sc, "heavy-hitter")),
    ]),
    "sources": [
        "https://stefchuraband.bandcamp.com/album/dancing-alone-on-the-concrete",
        "https://daily.bandcamp.com/album-of-the-day/stef-chura-dancing-alone-on-the-concrete-review",
        "https://www.allmusic.com/album/dancing-alone-on-the-concrete-mw0004856580",
        "https://www.brooklynvegan.com/stef-chura-announces-first-lp-in-7-years-ft-mems-r-e-m-sugar-apples-in-stereo-shares-danny/",
        "Lyrics screened on Genius (counts only): all nine tracks, linked per track below.",
    ],
    "links": {"ytm": "https://music.youtube.com/search?q=Stef+Chura+Dancing+Alone+on+the+Concrete"},
}

# ---------------------------------------------------------------- Fontaines D.C.
fd = "Fontaines-dc"
ALBUMS["fontaines-d-c-dopamine-chamber"] = {
    "artist": "Fontaines D.C.", "album": "Dopamine Chamber", "label": "Xl Recordings",
    "release_date": "2026-10-16",
    "release_notes": [
        "Fifth album from the Dublin band, after Romance (2024). Produced by James Ford, who also made Romance.",
        "Recorded February 2025 to March 2026 at Narcissus Studios in London and Decoy Studios in Suffolk. Marta Salogni engineered; Matt Colton mastered (Wikipedia).",
        "Grian Chatten - vocals, guitar; Carlos O'Connell - guitar, synths; Conor Curley - guitar; Conor Deegan - bass; Tom Coll - drums.",
        "Rosalía guests on Where Is Gone?, the band's first guest on a record. Strings arranged by Chatten, Richard Jones, Laura Moody and Elysian Collective.",
        "Singles: Marianne (Aug. 18) and Tongue (Sept. 30). 11 tracks, 43:59. Out Oct. 16, 2026.",
        "Not out yet: lyrics are posted for four tracks only. Seven are unscreened.",
    ],
    "pull_quotes": [
        {"text": "more mechanical extremes and orchestral noir flourishes", "source": "NME",
         "url": "https://www.nme.com/reviews/track/fontaines-d-c-marianne-track-review-new-album-dopamine-machine-lyrics-3963231"},
    ],
    "draft_comment": "Dublin's finest, again with James Ford. Early press hears more synths, drum machines and strings than guitars. Tongue is an FCC edit.",
    "riyl_suggestions": ["IDLES", "Shame", "Interpol", "Yard Act", "Joy Division"],
    "tracks": tracks([
        ("4:56", "Six Shot Morning", CLEAN, "Opener. Teased Aug. 15 and played live in Cádiz in August.", genius(fd, "six-shot-morning")),
        ("3:45", "Marianne", CLEAN, "Lead single (Aug. 18), with a Dave Meyers video. NME hears Depeche Mode synths and Lynchian strings.", genius(fd, "marianne")),
        ("3:51", "Mimesis", UNVERIFIED, "", None),
        ("3:48", "Happy For You", CLEAN, "Debuted live at Leeds Festival, Aug. 29.", genius(fd, "happy-for-you")),
        ("3:19", "Demolition", UNVERIFIED, "", None),
        ('3:13', "Tongue", 'FCC "shit" x10 (Refrain)', "Second single (Sept. 30). In FCC Edit Needed.", genius(fd, "tongue")),
        ("4:58", "One Man", UNVERIFIED, "", None),
        ("5:16", "Where Is Gone? (with ROSALÍA)", UNVERIFIED, "Features Rosalía. Longest track.", None),
        ("3:35", "You Miss Me", UNVERIFIED, "", None),
        ("3:15", "Japan", UNVERIFIED, "", None),
        ("3:57", "Intimate", UNVERIFIED, "Closer.", None),
    ]),
    "sources": [
        "https://fontainesdc.bandcamp.com/album/dopamine-chamber",
        "https://en.wikipedia.org/wiki/Dopamine_Chamber",
        "https://www.nme.com/reviews/track/fontaines-d-c-marianne-track-review-new-album-dopamine-machine-lyrics-3963231",
        "https://www.nme.com/news/music/fontaines-d-c-share-dopamine-chamber-tracklist-featuring-collab-with-rosalia-3969431",
        "Lyrics screened on Genius (counts only): tracks 1, 2, 4 and 6. Others unreleased.",
    ],
    "links": {"ytm": "https://music.youtube.com/search?q=Fontaines+D.C.+Dopamine+Chamber"},
}

# ---------------------------------------------------------------- Teenage Fanclub (rebuild: album out today)
tf = "Teenage-fanclub"
ALBUMS["teenage-fanclub-do-not-dare-to-dream"] = {
    "artist": "Teenage Fanclub", "album": "Do Not Dare To Dream", "label": "Merge Records",
    "release_date": "2026-10-09",
    "release_notes": [
        "Thirteenth studio album, after Nothing Lasts Forever (2023). Merge cat. MRG892.",
        "Produced by the band. Full-band parts recorded at Black Bay Studio in Kirkibost on Great Bernera, Outer Hebrides; vocals added at home in Glasgow; mixed and mastered in Glasgow by Dexter George.",
        "Norman Blake - vocals, guitar; Raymond McGinley - vocals, guitar; Euros Childs - keyboards, vocals; Francis Macdonald - drums; David McGowan - bass.",
        "Singles: Day In The Sun (announced July 23, 2026) and There Was You (Aug. 19), both with Donald Milne videos.",
        "10 tracks, about 39 minutes. Blake wrote 1, 4, 6, 8 and 9; McGinley wrote 2, 3, 5, 7 and 10 (Bandcamp). No covers.",
        "Out Oct. 9, 2026. Lyrics are posted for all ten tracks and all screened clean.",
    ],
    "pull_quotes": [
        {"text": "wrap up sombre reflections on life in a gentle melodic glow", "source": "MOJO",
         "url": "https://www.mojo4music.com/articles/new-music/teenage-fanclub-do-not-dare-to-dream-review/"},
        {"text": "sunny harmonies, chiming guitars and a general warm demeanour", "source": "musicOMH",
         "url": "https://www.musicomh.com/reviews/albums/teenage-fanclub-do-not-dare-to-dream"},
    ],
    "draft_comment": "Glasgow's harmony pop veterans, recorded in 14 days in the Outer Hebrides with Euros Childs on keys. Mid-tempo, warm and Byrds-leaning.",
    "riyl_suggestions": ["Crosby, Stills, Nash & Young", "The Byrds", "Big Star", "The Beach Boys", "Cat Stevens"],
    "tracks": tracks([
        ("3:28", "There Was You", CLEAN, "Blake song. Second single (Aug. 19). The Indy Review hears Big Star-ish guitar pop.", genius(tf, "there-was-you")),
        ("5:15", "Tomorrow People", CLEAN, "McGinley song, the longest track. Childs adds a Solina String Ensemble (MOJO).", genius(tf, "tomorrow-people")),
        ("4:22", "Over And Over", CLEAN, "McGinley song. Church organ under chiming guitars (The Indy Review).", genius(tf, "over-and-over")),
        ("3:30", "Be With You Tonight", CLEAN, "Blake song.", genius(tf, "be-with-you-tonight")),
        ("4:08", "The Same Air", CLEAN, "McGinley song.", genius(tf, "the-same-air")),
        ("4:36", "I Do Not Dare To Dream", CLEAN, "Blake song, title track. MOJO hears CSNY; The Indy Review hears 1970s Laurel Canyon.", genius(tf, "i-do-not-dare-to-dream")),
        ("3:50", "Take Time", CLEAN, "McGinley song. Childs on Mellotron flutes; Far Out places it in 1960s psychedelic tradition.", genius(tf, "take-time")),
        ("3:10", "Day In The Sun", CLEAN, "Blake song. First single, with a Donald Milne video. musicOMH calls it shimmering and optimistic.", genius(tf, "day-in-the-sun")),
        ("3:29", "Somewhere To Land", CLEAN, "Blake song (Bandcamp). musicOMH attributes it to McGinley.", genius(tf, "somewhere-to-land")),
        ("3:06", "Young And Wise", CLEAN, "McGinley song. Closer and shortest track.", genius(tf, "young-and-wise")),
    ]),
    "sources": [
        "https://teenage-fanclub.bandcamp.com/album/do-not-dare-to-dream",
        "https://www.mojo4music.com/articles/new-music/teenage-fanclub-do-not-dare-to-dream-review/",
        "https://www.musicomh.com/reviews/albums/teenage-fanclub-do-not-dare-to-dream",
        "https://theindyreview.com/2026/10/07/album-review-teenage-fanclub-do-not-dare-to-dream/",
        "https://faroutmagazine.co.uk/teenage-fanclub-do-not-dare-to-dream-album-review/",
        "Rebuilt Oct. 9 from the live Bandcamp tracklist (10 tracks; the Oct. 8 draft listed 9). Lyrics screened on Genius (counts only).",
    ],
    "links": {"ytm": "https://music.youtube.com/search?q=Teenage+Fanclub+Do+Not+Dare+To+Dream"},
}

# ---------------------------------------------------------------- L7 (single)
ALBUMS["l7-loma-linda"] = {
    "artist": "L7", "album": "Loma Linda", "label": "Self-released (verify)",
    "release_date": "2026-10-05",
    "release_notes": [
        "Single released Oct. 5, 2026, one day before The Last Hurrah, the band's farewell tour. It is 2:35 long (YouTube Music).",
        "Free download from the band's site for the first week, then streaming.",
        "Began as a 2003 demo from the era when Janis Tanaka played bass. Donita Sparks found it in the archives and recorded new vocals, new lyrics and extra parts in a couple of days (Stereogum).",
        "Tanaka returns for the tour. Original bassist Jennifer Finch died in July 2026 at age 59, and asked the band to go ahead with the tour.",
        "Last Hurrah runs Oct. 6 to Nov. 14. Bay Area date: Nov. 13, The Regency Ballroom, San Francisco. Finale: Nov. 14, The Wiltern, Los Angeles.",
        "Label is unconfirmed.",
    ],
    "pull_quotes": [
        {"text": "hooky and anthemic new single", "source": "Stereogum",
         "url": "https://stereogum.com/2513619/l7-loma-linda/music"},
    ],
    "draft_comment": "L7's farewell-tour single, built from a 2003 demo with Janis Tanaka on bass. Grunge-punk veterans, free download the first week.",
    "riyl_suggestions": ["Hole", "Babes in Toyland", "Bikini Kill", "7 Year Bitch"],
    "tracks": tracks([
        ("2:35", "Loma Linda", UNVERIFIED, "Single. Features Janis Tanaka on bass.", None),
    ]),
    "sources": [
        "https://stereogum.com/2513619/l7-loma-linda/music",
        "https://consequence.net/2026/10/l7-loma-linda-final-world-tour/",
        "https://wildfiremusic.net/2026/10/06/janis-tanaka-returns-to-l7-ahead-of-the-last-hurrah-tour-and-features-on-new-track-loma-linda/",
        "https://www.rollingstone.com/music/music-news/l7-new-song-single-loma-linda-1235636955/ (headline only; page was blocked)",
        "No lyrics found on Genius or LRCLIB.",
    ],
    "links": {"ytm": "https://music.youtube.com/playlist?list=OLAK5uy_nJXLfqW2W1xo7TXUtqxn0Hb3xuHkSH3mA"},
}

# ---------------------------------------------------------------- Little Barrie (single)
ALBUMS["little-barrie-luggin-hurt"] = {
    "artist": "Little Barrie", "album": "Luggin' Hurt", "label": "Easy Eye Sound",
    "release_date": "2026-04-23",
    "release_notes": [
        "Single from Gravity Freeze (Easy Eye Sound, May 22, 2026), the London trio's sixth album. Single date is unconfirmed; the video ran in April 2026.",
        "The album version is 7:08 and closes Side A. The video uses a trimmed single edit, directed by Robert Schober (The Fire Note).",
        "Barrie Cadogan - vocals, guitar, bass, percussion; Lewis Wharton - bass; Tony Coote - drums, percussion; Holly Quin-Ankrah and Frida Touray - backing vocals.",
        "Produced by Rupert Lyddon and Barrie Cadogan. Recorded at Rat Salad Studios, London. Mastered by Tom Forrest.",
        "Cadogan says it grew out of a long jam and was added to Side A to balance the record.",
    ],
    "pull_quotes": [],
    "draft_comment": "Seven-minute fuzz-guitar boogie from the London trio, now with Tony Coote on drums. A trimmed single edit has its own video.",
    "riyl_suggestions": ["The Black Keys", "Allah-Las", "Oh Sees", "The Mystery Lights"],
    "tracks": tracks([
        ("7:08", "Luggin' Hurt", UNVERIFIED, "Single. Album version is over 7 minutes; a trimmed single edit has a video. Closes Side A of Gravity Freeze.", None),
    ]),
    "sources": [
        "https://littlebarrie.bandcamp.com/track/luggin-hurt",
        "https://thefirenote.com/videos/little-barrie-luggin-hurt-single-edit-video/",
        "No lyrics found on Genius or LRCLIB.",
    ],
    "links": {"ytm": "https://music.youtube.com/search?q=Little+Barrie+Luggin%27+Hurt"},
}

# Write every album to outputs/reviews/research/<slug>.json.
OUT.mkdir(parents=True, exist_ok=True)
for slug, data in ALBUMS.items():
    (OUT / f"{slug}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", slug)
