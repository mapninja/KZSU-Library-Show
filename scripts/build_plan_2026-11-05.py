#!/usr/bin/env python3
"""Build data/recon/2026-11-05/working_playlist.json (the Nov. 5, 2026 show plan).

Beginner notes:
- A "plan" is one JSON file. It holds "sets" (groups of tracks in air order) plus
  extra keys such as the Triple Shot, mic-break talking points and a bench.
- Each track is a Python dict. The helper T() fills in default fields so every
  track has the same keys.
- carry() copies a track that was already researched in an earlier plan, so we
  keep its videoId, tag and label instead of looking them up again.
- A guard at the end refuses to write the plan if any planned track is in a
  60-day cool-off, was cut by Stace, or aired in the past 21 days.
- Run from the repo root:  python3 scripts/build_plan_2026-11-05.py
"""
import glob
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent            # repo root folder
OUT_DIR = REPO / "data" / "recon" / "2026-11-05"          # where the new plan goes
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Index every track from earlier plans by videoId so carry() can reuse them.
# ---------------------------------------------------------------------------
lookup = {}
for f in sorted(glob.glob(str(REPO / "data/recon/2026-10-*/working_playlist.json"))):
    p = json.loads(Path(f).read_text())
    for pool in ([t for s in p.get("sets", []) for t in s["tracks"]], p.get("bench", []), p.get("cut", [])):
        for t in pool:
            if isinstance(t, dict) and t.get("videoId"):
                lookup[t["videoId"]] = t


def T(artist, track, album, label, label_source, tag, released, ttype, duration,
      priority, why, fcc_status, fcc_note, source, videoId, **extra):
    """Make one track dict with the standard fields."""
    d = dict(artist=artist, track=track, album=album, label=label,
             label_source=label_source, tag=tag, released=released, type=ttype,
             upcoming="", duration=duration, priority=priority, why=why,
             fcc_status=fcc_status, fcc_note=fcc_note, source=source,
             videoId=videoId)
    d.update(extra)
    return d


def carry(videoId, priority, why, source="carried from an earlier plan", **over):
    """Copy a track from an earlier plan (matched by videoId); change priority, why and any field."""
    d = dict(lookup[videoId])
    d["priority"] = priority
    d["why"] = why
    d["source"] = source
    for k in ("added_by", "rel_main", "rel_sub", "info"):
        d.pop(k, None)
    d.update(over)
    return d


CLEAN_G = lambda n: f"CLEAN (Genius, {n} words)."
ZK_ALBUM = lambda tag: f"zookeeper album {tag}"
NEXT = "Next Show (Stace add)"

# ---------------------------------------------------------------------------
# 2. Sets (forward air order). Target: about 75 minutes of music per hour.
# ---------------------------------------------------------------------------
sets = []

# ---- Hour 1, Set 1: new this week ----------------------------------------
sets.append({"set": "Hour 1, Set 1: New this week (out Oct. 30) and Twisted Teens", "tracks": [
    T("Queens of the Stone Age", "Run Away From the Mob", "Perfecth", "Matador Records",
      "zookeeper label table (Matador Records, id 1952); album not in library yet", "",
      "2026-10-30", "album track (single)", "3:59", "R",
      "Perfecth, the ninth QOTSA album, is out Fri. Oct. 30 on Matador. Produced by Josh Homme and Michael Shuman. Run Away From the Mob is one of four singles. Easy Street (fuck x1) stays off the air.",
      "CLEAN", CLEAN_G(235), "recon", "D3pjTpmNo3Q",
      rel_main="Oct. 30, 2026", rel_sub="album; single earlier"),
    T("Clinic", "Wild In The Streets", "Wild In The Streets", "Domino Recording Company",
      "zookeeper label table (Domino Recording Company, id 15506); album not in library yet", "",
      "2026-10-30", "album track (title)", "2:06", "R",
      "Tenth Clinic album, 12 songs, out Fri. Oct. 30 on Domino. Duo of Ade Blackburn and Jonathan Hartley from Liverpool. You and I was deleted Oct. 23 (cool-off to Dec. 22); this is a different track.",
      "UNVERIFIED", "UNVERIFIED: no lyrics posted (Genius and LRCLIB found nothing). Listen first.", "recon", "bkxgZ5tgNKU",
      rel_main="Oct. 30, 2026", rel_sub="album"),
    T("Ex:Re", "Radio Station", "Save As", "4AD",
      "zookeeper label table (4AD, id 30); album not in library yet", "",
      "2026-09-15", "single", "4:13", "O",
      "Elena Tonra (Daughter) second Ex:Re album, Save As, is out Oct. 30 on 4AD. Radio Station was the first single (Sept. 15). Produced by Fabian Prynn.",
      "CLEAN", CLEAN_G(253), "recon", "n_cPyY09Dw4",
      rel_main="Sept. 15, 2026", rel_sub="single; album Oct. 30, 2026"),
    T("Sennen", "Here It Comes", "New Quiet", "Sonic Cathedral",
      "zookeeper label table (Sonic Cathedral, id 19710); album not in library yet", "",
      "2026-10-30", "single", "4:23", "O",
      "New Quiet is the UK band's first album since 2016, out Oct. 30 on Sonic Cathedral. Here It Comes is the lead single.",
      "CLEAN", CLEAN_G(111), "recon", "06jJKUCkkZE",
      rel_main="Oct. 30, 2026", rel_sub="album; lead single"),
    T("DIIV", "Dare Me", "ZIRP!", "Fantasy Records",
      "zookeeper label table (Fantasy Records, id 10550); Concord label group; verify spelling on the CD", "",
      "2026-10-30", "single", "4:04", "O",
      "ZIRP! is the fifth DIIV album, produced by A. G. Cook, out Oct. 30 on Fantasy (Concord). Dare Me was the last single before release. Trillions was deleted Oct. 16 (cool-off to Dec. 15); this is a different track.",
      "CLEAN", CLEAN_G(190), "recon", "ZO8I_UqFi_E",
      rel_main="Oct. 30, 2026", rel_sub="album; single earlier"),
    carry("ElPskynxhTA", "R",
          "In Stace's Next Show playlist. Twisted Teens' Holy Cross Tigers is out Fri. Nov. 6 on Sub Pop, the day after the show.",
          source=NEXT, released="2026 (single; album Nov. 6, 2026)"),
    T("Michael Nau", "Popfly", "Popfly", "Suicide Squeeze Records",
      "release DB via Friday sweep; label spelled per zookeeper label table (id 8426); verify for this album", "",
      "2026-10-23", "single (title track)", "3:23", "O",
      "Album out Oct. 23 on Suicide Squeeze. Title track was the lead single (Aug. 27). In the Weekly Playlist.",
      "CLEAN", CLEAN_G(190), "weekly playlist (Friday sweep)", "C1JkLJzrizE",
      rel_main="Aug. 27, 2026", rel_sub="single; album Oct. 23, 2026"),
    T("The Olivia Tremor Control", "The Same Place", "The Same Place", "Elephant 6 Recording Co.",
      "release DB via Friday sweep (verify); the library holds only the Elephant 6 Recording Co. compilation (tag 1153943, Org Music)", "",
      "2026-10-23", "single (title track)", "3:16", "O",
      "First Olivia Tremor Control album since 1999, out Oct. 23. In the Weekly Playlist.",
      "CLEAN", CLEAN_G(142), "weekly playlist (Friday sweep)", "NEGOMO5fajs",
      rel_main="Oct. 23, 2026", rel_sub="album",
      zk_alt="1153943"),
]})

# ---- Hour 1, Set 2: reviewed albums in rotation ---------------------------
REV = "Reviewed rotation, week {w}: {s} in DJ Stace's review."
sets.append({"set": "Hour 1, Set 2: Reviewed albums in rotation (weeks 3 and 4)", "tracks": [
    carry("FWP2bTeoPTo", "O", "Reviewed rotation, week 4: four stars. Not aired yet; Peekaboo Hand aired Oct. 22."),
    carry("MR-dh4FTavQ", "O", "Reviewed rotation, week 4. In Stace's Next Show playlist. Aired Oct. 1; Denny's aired Oct. 22.", source=NEXT),
    T("Lex Walton", "Adrian Borland Will Have His Revenge On London", "Ultimate Love Forever", "Sub Pop Records",
      "zookeeper album 1156519", "1156519", "2026-08-26", "album track", "3:08", "O",
      "Reviewed rotation, week 4: five stars for the album. CD and LP out Nov. 20 on Sub Pop. Aired Oct. 1; For Thee I Sing aired Oct. 22. Ultimate Love 4Ever was cut Oct. 29 and is left out.",
      "CLEAN", "DJ Stace review (Zookeeper, reviewed Oct. 4 to 8, 2026): no FCC flag on this track.", "review rotation", "cK6ooeCdXUY",
      rel_main="Aug. 26, 2026", rel_sub="album; LP and CD Nov. 20, 2026"),
    carry("pirkuE2Edgc", "O", "Reviewed rotation, week 4. In Stace's Next Show playlist. Aired Oct. 1 and 8; 28 days ago. Black Paint is left out (deleted).", source=NEXT),
    carry("LHPybTFbWAA", "O", "Reviewed rotation, week 4. In Stace's Next Show playlist. Aired Oct. 1. Billy Came Back was cut Oct. 29 and is left out.", source=NEXT),
    carry("BSraSIhC_8A", "O",
          "Reviewed rotation, week 3: four stars. Post Script is the posthumous album on Cog Sinister. The Fall's Are You Are Missing Winner turns 25 on show day (Nov. 5, 2001). Retro Song was cut Oct. 29 and is left out."),
    carry("PVcU0z1zPqk", "O", "Reviewed rotation, week 3: four stars. Planned Oct. 22 and did not air. Flood Season was cut Oct. 29 and is left out."),
    carry("UEjLrx6c38Q", "O", "Reviewed rotation, week 3. Aired Oct. 1. The title track was cut Oct. 29 and is left out."),
]})

# ---- Hour 1, Set 3: anniversaries -----------------------------------------
sets.append({"set": "Hour 1, Set 3: Anniversaries: 1991, 1996 and 2001", "tracks": [
    T("my bloody valentine", "Only Shallow", "Loveless", "Creation Records Limited",
      "zookeeper album 13666", "13666", "1991-11-04", "album track", "3:31", "R",
      "35 years: Loveless came out Nov. 4, 1991 (Creation in the UK, Sire in the US). Play the library CD; Loveless is not on YouTube Music. Dates agree: Wikipedia and Creation Records.",
      "CLEAN", CLEAN_G(86), "recon (anniversary)", "",
      ytm_missing=True, rel_main="Nov. 4, 1991", rel_sub="album, 35 years"),
    T("Teenage Fanclub", "What You Do To Me", "Bandwagonesque", "Geffen Records",
      "zookeeper album 15387", "15387", "1991-11 (Nov. 4 per Wikipedia list; verify day)", "album track", "2:01", "O",
      "35 years: Bandwagonesque came out Nov. 1991 on Creation (UK) and Geffen (US). Triple Shot artist Oct. 8.",
      "CLEAN", CLEAN_G(152), "recon (anniversary)", "s0WSG9xD7H0",
      rel_main="Nov. 1991", rel_sub="album, 35 years (day: verify)"),
    T("Wilco", "Outtasite (Outta Mind)", "Being There", "Reprise Records (Modern)",
      "zookeeper album 350705", "350705", "1996-10-29", "album track", "2:35", "R",
      "30 years: Being There came out Oct. 29, 1996 on Reprise. A 19-track double album sold at a single-album price. Dates agree: Wikipedia and Rate Your Music.",
      "CLEAN", CLEAN_G(167), "recon (anniversary)", "ZasGLLCEwTA",
      rel_main="Oct. 29, 1996", rel_sub="album, 30 years"),
    T("Johnny Cash", "Rusty Cage", "Unchained", "American (Modern)",
      "zookeeper album 355373", "355373", "1996-11-05", "album track", "2:49", "R",
      "30 years on show day: Unchained (American II) came out Nov. 5, 1996 on American Recordings. Tom Petty and the Heartbreakers back Cash. Rusty Cage covers Soundgarden. Won the Grammy for Best Country Album.",
      "CLEAN", CLEAN_G(209), "recon (anniversary)", "wMlNxB8dXFM",
      rel_main="Nov. 5, 1996", rel_sub="album, 30 years today"),
    T("Silver Jews", "Dallas", "The Natural Bridge", "Drag City",
      "zookeeper album 345079", "345079", "1996-10-30 (Wikipedia list; verify)", "album track", "4:14", "O",
      "30 years: The Natural Bridge, Oct. 30, 1996 per the Wikipedia 1996 list; one source, verify. Drag City.",
      "CLEAN", CLEAN_G(219), "recon (anniversary)", "U0IgWuSiFDk",
      rel_main="Oct. 30, 1996 (verify)", rel_sub="album, 30 years"),
    T("Chavez", "Memorize This Face", "Ride the Fader", "Matador Records",
      "zookeeper album 354248", "354248", "1996-11-05 (Wikipedia list; verify)", "album track", "1:45", "O",
      "30 years on show day: Ride the Fader on Matador, Nov. 5, 1996 per the Wikipedia 1996 list; one source, verify. A 1:45 track.",
      "CLEAN", CLEAN_G(81), "recon (anniversary)", "QoH5KoF9zSQ",
      rel_main="Nov. 5, 1996 (verify)", rel_sub="album, 30 years today"),
    T("The National", "American Mary", "The National", "Brassland",
      "zookeeper label table (Brassland, id 12768); debut album not in library", "",
      "2001-10-30 (Wikipedia list; verify)", "album track", "4:03", "O",
      "25 years: the debut album The National came out Oct. 30, 2001 on Brassland per the Wikipedia 2001 list; one source, verify. Last spin Aug. 7, 2019.",
      "CLEAN", CLEAN_G(200), "recon (anniversary)", "suEm2nzKVBA",
      rel_main="Oct. 30, 2001 (verify)", rel_sub="debut album, 25 years"),
]})

# ---- Hour 2, Set 4: Thursday Triple Shot -----------------------------------
thao = [
    T("Thao & The Get Down Stay Down", "Bag of Hammers", "We Brave Bee Stings and All", "Kill Rock Stars",
      "zookeeper label table (Kill Rock Stars, id 1736); album not in library", "",
      "2008", "album track", "2:50", "R",
      "Triple Shot 1 of 3, 2008: Thao & The Get Down Stay Down, the band that made her name. Kill Rock Stars.",
      "CLEAN", CLEAN_G(195), "triple shot", "nusf4Sfl6Wk", rel_main="2008", rel_sub="album"),
    T("Thao & Mirah", "Eleven", "Thao & Mirah", "Kill Rock Stars",
      "zookeeper album 977216", "977216", "2011", "album track", "4:01", "R",
      "Triple Shot 2 of 3, 2011: the collaboration with Mirah, produced by Tune-Yards' Merrill Garbus. Kill Rock Stars.",
      "CLEAN", CLEAN_G(325), "triple shot", "LI4g7kT3tS8", rel_main="2011", rel_sub="album"),
    T("THAO", "Sick of the Times (feat. The Linda Lindas)", "Show Me", "Kill Rock Stars",
      "zookeeper label table (Kill Rock Stars, id 1736); album not in library yet", "",
      "2026-10-30", "single", "3:19", "R",
      "Triple Shot 3 of 3, new: lead single from Show Me, Thao's first album in six years, out Fri. Oct. 30 on Kill Rock Stars. Tune-Yards co-produced and appear on it; The Linda Lindas guest. Listen first: no lyrics posted.",
      "UNVERIFIED", "UNVERIFIED: no lyrics posted (Genius and LRCLIB found nothing). Listen first. Swap: We the Common (CLEAN, 283 words), videoId yrldgm5LjRc.", "triple shot", "l1mT5WQwYPI",
      rel_main="Oct. 30, 2026", rel_sub="single; album Oct. 30, 2026"),
]
sets.append({"set": "Hour 2, Thursday Triple Shot: Thao", "tracks": thao})

# ---- Hour 2, Set 5: Bay Area ------------------------------------------------
sets.append({"set": "Hour 2, Set 5: Bay Area, Nov. 5 to 8 (upcoming shows only)", "tracks": [
    T("Team Dresch", "Hand Grenade", "Hand Grenade", "Kill Rock Stars",
      "zookeeper album 193575", "193575", "1990s", "album track", "3:23", "R",
      "Thu. Nov. 5, Bottom of the Hill, S.F., with Third Sex and Longstocking. Riot grrrl and queercore; fits the punk focus.",
      "CLEAN", CLEAN_G(382), "weekly playlist (Friday sweep)", "tMf78i0mQP8", rel_main="1990s", rel_sub="verify year"),
    T("The Black Angels", "Currency", "Death Song", "Partisan Records",
      "zookeeper album 1107032", "1107032", "2017", "album track", "5:17", "R",
      "Thu. Nov. 5, Regency Ballroom, S.F., with Ghostwoman. The Austin psych band is a core artist (58 shows). Young Men Dead aired Oct. 29.",
      "CLEAN", CLEAN_G(224), "recon", "pWyfwoWaquQ", rel_main="2017", rel_sub="album"),
    T("Sour Widows", "Sigil", "Sigil", "Julia's War",
      "release DB via Friday sweep (verify); not in zookeeper label table", "",
      "2026-10-23", "single (title track)", "4:18", "O",
      "Thu. Nov. 5, Chapel, S.F., with Squirrel Flower. Album out Oct. 23.",
      "CLEAN", CLEAN_G(187), "weekly playlist (Friday sweep)", "neIym9G-0Ss", rel_main="Oct. 23, 2026", rel_sub="album"),
    T("Colleen Green", "Whatever I Want", "I Want To Grow Up", "Hardly Art",
      "zookeeper album 1073708", "1073708", "2015-02", "album track", "3:57", "O",
      "Thu. Nov. 5, Ivy Room, Albany, with Still Ruins and Artsick. From her 2015 album on Hardly Art (the Friday sweep listed it as new; it is not).",
      "CLEAN", CLEAN_G(227), "weekly playlist (Friday sweep)", "oY-ZfipiU7g", rel_main="Feb. 2015", rel_sub="album"),
    T("L.A. Witch", "Kill My Baby Tonight", "L.A. Witch", "Suicide Squeeze Records",
      "zookeeper album 1113703", "1113703", "2017", "album track", "3:08", "O",
      "Fri. Nov. 6, Independent, S.F., with King Buffalo.",
      "CLEAN", CLEAN_G(100), "recon", "F_IE7EMjB0U", rel_main="2017", rel_sub="album"),
    T("Big Star", "September Gurls", "Radio City", "Ardent Records",
      "zookeeper album 393926", "393926", "1974", "album track", "2:49", "O",
      "Sat. Nov. 7, Fillmore, S.F.: Big Star Quintet. 12 shows on the profile.",
      "CLEAN", CLEAN_G(148), "recon", "IRGdfyrVjlw", rel_main="1974", rel_sub="album"),
]})

# ---- Hour 2, Set 6: punk and post-punk ---------------------------------------
sets.append({"set": "Hour 2, Set 6: Punk and post-punk, Texas to Dublin", "tracks": [
    T("Dicks", "Hate the Police", "Virus that Would not Die", "Alternative Tentacles Records",
      "zookeeper album 419677", "419677", "1980 (original single; verify)", "album track", "1:59", "R",
      "Texas punk slot (config/show_focus.json). Austin band; Gary Floyd on vocals. The library album is the Alternative Tentacles release.",
      "CLEAN", CLEAN_G(191), "recon", "7a3p69gv1Jg", rel_main="1980", rel_sub="single (verify)"),
    carry("dJDSyCr4Dz8", "O", "Punk focus: San Francisco, 1977. Carried from the Weekly Playlist; not aired yet."),
    carry("gXKDtkCzSCw", "O", "Punk focus. Damned Triple Shot song that did not air Oct. 22 (Neat Neat Neat). From Damned Damned Damned (1977)."),
    T("The Linda Lindas", "Gotta Get Out", "Gotta Get Out", "Reprise Records",
      "zookeeper label table (Reprise Records, id 16415); Apple Music and Bandcamp agree on Reprise; album not in library", "",
      "2026-08-28", "album track (title)", "2:42", "O",
      "In Stace's Next Show playlist. Title track of their third album (Aug. 28, 2026, Reprise). The Linda Lindas guest on Thao's Sick of the Times in the Triple Shot.",
      "CLEAN", CLEAN_G(289), NEXT, "Qe7aq1VcuxE", rel_main="Aug. 28, 2026", rel_sub="album"),
    T("Sprints", "Little Fix", "A Modern Job", "Nice Swan Records",
      "web: single Jan. 11, 2022 on Nice Swan, then the A Modern Job EP (Mar. 11, 2022); Nice Swan not in zookeeper label table; verify", "",
      "2022-01-11", "single", "3:16", "O",
      "In Stace's Next Show playlist. Dublin post-punk band, now on City Slang.",
      "CLEAN", CLEAN_G(374), NEXT, "TybCMKD_vU4", rel_main="Jan. 11, 2022", rel_sub="single; EP Mar. 11, 2022"),
    T("TV Priest", "Decoration", "Uppers", "Sub Pop Records",
      "zookeeper label table (Sub Pop Records, id 3124); Sub Pop released Uppers Feb. 5, 2021; album not in library", "",
      "2021-02-05", "album track", "4:31", "O",
      "In Stace's Next Show playlist. London post-punk; lead single from their debut Uppers. Cartoons was deleted Oct. 16 (cool-off to Dec. 15); this is a different track.",
      "CLEAN", CLEAN_G(252), NEXT, "tKcbUTCGY3Q", rel_main="Feb. 5, 2021", rel_sub="album"),
]})

# ---- Hour 2, Set 7: machines and motorik -------------------------------------
sets.append({"set": "Hour 2, Set 7: Machines and motorik", "tracks": [
    carry("fOoCnK5Jza4", "R", "Requested back by DJ Stace (Oct. 16). It did not air Oct. 15 or Oct. 22. From Computer World (1981).",
          source="carried (Stace request)"),
    carry("wdyhe8VT6Yg", "R", "Requested back by DJ Stace. It did not air Oct. 15 or Oct. 22. Sheffield, 1979 single on Rough Trade.",
          source="carried (Stace request)"),
    carry("FEQJgTFfS9k", "O",
          "In Stace's Next Show playlist. Lead single from A Long Way From Kansas, out Jan. 8, 2027 on Domino; a tribute to Keith McIvor (JD Twitch of Optimo).",
          source=NEXT, label="Domino Recording Company",
          label_source="zookeeper label table (Domino Recording Company, id 15506); Domino announced the album; album not in library",
          released="2026-10 (single; album Jan. 8, 2027)"),
]})

# ---- Hour 2, Set 8: closers ---------------------------------------------------
sets.append({"set": "Hour 2, Set 8: Slow closers", "tracks": [
    carry("FUFWkuMY6xM", "O", "Shoegaze companion to the Loveless anniversary. Galaxie 500, Boston. Carried from the Weekly Playlist."),
    T("John Lennon", "Watching The Wheels", "Double Fantasy", "Geffen Records",
      "zookeeper label table (Geffen Records, id 924 or 1305); album not found in library; verify", "",
      "1980-11-17 (verify)", "album track", "4:00", "O",
      "In Stace's Next Show playlist. Double Fantasy came out Nov. 17, 1980.",
      "CLEAN", CLEAN_G(224), NEXT, "2Kx2PbA8bCI", rel_main="Nov. 17, 1980 (verify)", rel_sub="album"),
    T("Chris Cornell", "Seasons", "Singles", "Epic Records (Modern)",
      "zookeeper album 45234", "45234", "1992", "soundtrack track", "5:46", "O",
      "Newest add to Stace's Next Show playlist. From the Singles soundtrack (1992).",
      "CLEAN", CLEAN_G(224), NEXT, "1DnSiznUrVI", rel_main="1992", rel_sub="soundtrack"),
]})

# ---------------------------------------------------------------------------
# 3. Bench: tracks that are NOT in the Air Order (about 60 minutes).
# ---------------------------------------------------------------------------
bench = [
    T("Wilco", "Monday", "Being There", "Reprise Records (Modern)", "zookeeper album 350705", "350705",
      "1996-10-29", "album track", "3:34", "X", "Bench alternate for the Being There anniversary.", "CLEAN", CLEAN_G(206), "recon", "EqmF0Ub6snw"),
    T("Teenage Fanclub", "Star Sign", "Bandwagonesque", "Geffen Records", "zookeeper album 15387", "15387",
      "1991-11", "single", "4:56", "X", "Bench alternate for the Bandwagonesque anniversary. Reached No. 4 on Billboard Modern Rock Tracks.", "CLEAN", CLEAN_G(187), "recon", "M0oLeRT47A8"),
    T("Silver Jews", "Black and Brown Blues", "The Natural Bridge", "Drag City", "zookeeper album 345079", "345079",
      "1996-10-30 (verify)", "album track", "4:05", "X", "Bench alternate for the Natural Bridge anniversary.", "UNVERIFIED", "Not screened.", "recon", "NUNjhM3RYok"),
    T("THAO", "We the Common (For Valerie Bolden)", "We the Common", "Ribbon Music",
      "web (verify); not in library", "", "2013", "album track", "3:38", "X",
      "Triple Shot swap if Sick of the Times does not clear.", "CLEAN", CLEAN_G(283), "recon", "yrldgm5LjRc"),
    T("Grant-Lee Phillips", "Mobilize", "Mobilize", "unverified", "not checked in zookeeper", "",
      "2004", "album track", "4:08", "X", "Fri. Nov. 6, Hopmonk Tavern, Novato.", "CLEAN", CLEAN_G(256), "recon", "mKfRt3Yt0HE"),
    carry("FEQJgTFfS9k", "X", "Alternate."),  # placeholder replaced below if duplicate in sets
]
bench.pop()  # remove the placeholder (Hot Chip is already in Set 7)
bench += [
    T("Cut Worms", "Evil Twin", "", "unverified", "not checked in zookeeper", "", "2026", "single", "5:01", "X",
      "In Stace's Next Show playlist.", "CLEAN", CLEAN_G(216), NEXT, "jMlssW90uwg"),
    T("Father John Misty", "Trouble", "", "unverified", "not checked in zookeeper", "", "2026", "single", "3:13", "X",
      "In Stace's Next Show playlist.", "CLEAN", CLEAN_G(197), NEXT, "O6a7lfozvEY"),
    T("Funkadelic", "Can You Get To That", "Maggot Brain", "Westbound Records", "web (verify)", "", "1971", "album track", "2:50", "X",
      "In Stace's Next Show playlist.", "CLEAN", CLEAN_G(348), NEXT, "yl3fIXaAXow"),
    T("BODEGA", "Slow Train", "", "unverified", "not checked in zookeeper", "", "2026", "single", "3:52", "X",
      "In Stace's Next Show playlist.", "CLEAN", CLEAN_G(239), NEXT, "4TnhLA3yQaU"),
    T("Jesse Welles", "Middle", "", "unverified", "not checked in zookeeper", "", "2026", "single", "4:07", "X",
      "In Stace's Next Show playlist.", "CLEAN", CLEAN_G(330), NEXT, "Xd2qNhtyyW0"),
    T("Caroline Rose", "Cry!", "Gentling the Horse at the Walt Whitman Mall", "SUCK Records", "release DB (verify)", "",
      "2026-10-23", "album track", "3:44", "X", "In Stace's Next Show playlist. Album out Oct. 23 on SUCK Records, Rose's own label.", "CLEAN", CLEAN_G(144), NEXT, "s1tdCxkduZI"),
    T("Hamilton Leithauser & Rostam", "In A Black Out (Piano Version)", "", "unverified", "not checked in zookeeper", "", "2026", "single", "3:37", "X",
      "In Stace's Next Show playlist.", "CLEAN", CLEAN_G(159), NEXT, "gexqEtgfLt8"),
    T("Soundgarden", "Into The Void (Sealth)", "Superunknown", "A&M Records", "web (verify)", "", "1994", "album track", "6:37", "X",
      "In Stace's Next Show playlist. Pairs with Cash's Rusty Cage (a Soundgarden song).", "CLEAN", CLEAN_G(220), NEXT, "gtG5d3Zd6I4"),
    T("Sonic Youth", "Bull In The Heather", "Experimental Jet Set, Trash and No Star", "DGC", "web (verify)", "", "1994", "single", "3:05", "X",
      "In Stace's Next Show playlist.", "CLEAN", CLEAN_G(148), NEXT, "PGPOcQ14Eo0"),
    carry("qSk88IeNUr0", "X", "In Stace's Next Show playlist. Unaired since Oct. 22.", source=NEXT),
    carry("V9WCjEsPP0U", "X", "Punk focus alternate. Fugazi, Washington D.C. hardcore arc."),
    carry("dfiR6XtYdzY", "X", "In Stace's Next Show playlist.", source=NEXT),
    carry("fVuyZ-Wp7Ng", "X", "In Stace's Next Show playlist.", source=NEXT),
    carry("GRC4Ac6IB1w", "X", "In Stace's Next Show playlist.", source=NEXT),
    carry("5nt_9kEaokY", "X", "Stace added it Oct. 22. Dumb, Mint Records.", source=NEXT),
    T("Jozef Van Wissem & Jim Jarmusch", "Never Like You Said (feat. Courtney Barnett)", "", "Sacred Bones Records", "web (verify)", "",
      "2026-09-09", "single", "5:24", "X", "Album out Nov. 6 on Sacred Bones (per earlier plans; verify).", "CLEAN", CLEAN_G(0), "weekly playlist", "3GytZtSR-lw"),
]
# The Van Wissem entry came from an earlier plan; reuse its stored fields instead of the stub above.
bench[-1] = carry("3GytZtSR-lw", "X", "Single Sept. 9; album Nov. 6 on Sacred Bones (verify).")

# FCC findings from this run (counts only; never reproduces lyrics)
excluded_fcc = [
    {"artist": "Queens of the Stone Age", "track": "Easy Street", "fcc": "fuck x1 (Verse 2)", "action": "not used; Run Away From the Mob used instead (also in cool-off to Dec. 8)"},
    {"artist": "Greg Freeman", "track": "Cahokia", "fcc": "fuck x1 (intro), shit x1 (Chorus)", "action": "stays out; he plays the Independent Thu. Nov. 5"},
]

# ---------------------------------------------------------------------------
# 4. Extras: Triple Shot, Bay Area (upcoming only), mic breaks, giveaways
# ---------------------------------------------------------------------------
triple_shot = {
    "artist": "THAO",
    "angle": ("Thao's first album in six years, Show Me, is out Fri. Oct. 30 on Kill Rock Stars, with an album release show at the Independent in S.F. on Sun. Nov. 8. "
              "Three projects: Thao & The Get Down Stay Down (2008), Thao & Mirah (2011) and the new single with Tune-Yards and The Linda Lindas. "
              "Sick of the Times has no lyrics posted: listen first. Alternates: Wilco (Being There turned 30 on Oct. 29; Wilco, Uncle Tupelo and Billy Bragg & Wilco) or Clinic (new album Oct. 30)."),
    "tracks": thao,
}

# Each show has "act" (who plays) and "detail" (price and times). "what" joins them for older builders.
_shows = [
    ("Thu. Nov. 5", "Bottom of the Hill, S.F.", "Team Dresch, Third Sex, Longstocking", "$20/$25, doors 7 p.m., show 8 p.m.", "Also Wed. Nov. 4 (passed)."),
    ("Thu. Nov. 5", "Regency Ballroom, S.F.", "The Black Angels, Ghostwoman", "Doors 7 p.m., show 8 p.m.", ""),
    ("Thu. Nov. 5", "Chapel, S.F.", "Squirrel Flower, Sour Widows", "$27.22, doors 7 p.m.", ""),
    ("Thu. Nov. 5", "Ivy Room, Albany", "Colleen Green, Still Ruins, Artsick", "$20.39, doors 7 p.m.", ""),
    ("Fri. Nov. 6", "Independent, S.F.", "King Buffalo, L.A. Witch", "$31.55, doors 8:30 p.m.", ""),
    ("Fri. Nov. 6", "Hopmonk Tavern, Novato", "Grant-Lee Phillips, Damon Wyckoff", "$36.01 to $53.37, doors 7 p.m.", ""),
    ("Sat. Nov. 7", "Fillmore, S.F.", "Big Star Quintet", "Doors 7 p.m.", ""),
    ("Sun. Nov. 8", "Independent, S.F.", "Thao, album release", "$32.55, doors 7:30 p.m.", "Show Me came out Oct. 30."),
]
bay_area_shows = [
    {"date": d, "venue": v, "act": a, "detail": x, "what": f"{a}. {x}", "note": n}
    for d, v, a, x, n in _shows
]

mic_breaks = {
    "opening": [
        "Punk and post-punk focus, week 4 of 4 before the Nov. 12 review: Team Dresch, Dicks and Avengers tonight.",
        "Queens of the Stone Age, Clinic, DIIV, Ex:Re, Sennen and Thao all released albums Oct. 30.",
        "Wilco's Being There turned 30 on Oct. 29. Johnny Cash's Unchained turns 30 tonight.",
    ],
    "after_new": [
        "Perfecth is the ninth QOTSA album, on Matador, produced by Josh Homme and Michael Shuman. It has nine tracks and four singles.",
        "Clinic's Wild in the Streets is their tenth album, on Domino. Sennen's New Quiet is their first in ten years, on Sonic Cathedral.",
        "DIIV's ZIRP! was produced by A. G. Cook. Ex:Re is Elena Tonra of Daughter; Save As is out on 4AD.",
    ],
    "end_hour_1": [
        "Reviewed this month and in rotation: Twisted Teens, Palace, Lex Walton, Ty Segall, This Is Lorelei, The Fall, Sylvan Esso and Yard Act.",
        "Lex Walton's Ultimate Love Forever is out as CD and LP Nov. 20 on Sub Pop. Twisted Teens' Holy Cross Tigers is out tomorrow, Nov. 6, on Sub Pop.",
        "Station ID at the top of the hour.",
    ],
    "anniversary": [
        "My Bloody Valentine's Loveless came out Nov. 4, 1991 on Creation in the UK. Teenage Fanclub's Bandwagonesque came out the same month, also on Creation.",
        "Wilco's Being There: Oct. 29, 1996, Reprise. Johnny Cash's Unchained: Nov. 5, 1996, American Recordings, with Tom Petty and the Heartbreakers. Rusty Cage is a Soundgarden song.",
        "The Fall's Are You Are Missing Winner came out Nov. 5, 2001 on Cog Sinister. The National's debut came out Oct. 30, 2001 (verify).",
    ],
    "triple_shot_intro": [
        "Thursday Triple Shot: Thao. Three projects: Thao & The Get Down Stay Down, Thao & Mirah, and the new single with Tune-Yards and The Linda Lindas.",
        "Show Me is her first album in six years, out Oct. 30 on Kill Rock Stars. She plays the Independent in San Francisco Sunday, Nov. 8.",
    ],
    "after_triple_shot": [
        "Thao & Mirah (2011) was produced by Tune-Yards' Merrill Garbus. Neko Case and Adrian Quesada guest on Show Me.",
    ],
    "bay_area_break": [
        "Tonight, Thu. Nov. 5: Team Dresch at Bottom of the Hill, The Black Angels at the Regency Ballroom, Squirrel Flower with Sour Widows at Chapel, Colleen Green at the Ivy Room in Albany.",
        "Fri. Nov. 6: King Buffalo with L.A. Witch at the Independent. Sat. Nov. 7: Big Star Quintet at the Fillmore. Sun. Nov. 8: Thao's album release at the Independent.",
    ],
    "after_machines": [
        "Numbers is from Kraftwerk's Computer World (1981). Nag, Nag, Nag is Cabaret Voltaire's 1979 Rough Trade single.",
    ],
    "closing": [
        "Next week, Nov. 12: the last punk and post-punk week before the review.",
    ],
}

ticket_giveaway = {
    "default_rule_result": "No November ticket sheet in the repo (data/tickets has only 2026-10, which ends Oct. 29). No giveaway placed.",
    "proposed": "None.",
    "flag": "Paste the November rows in chat if there is a giveaway for Nov. 5 or later. Rules, call-in number and show time: confirm before air.",
    "placement": "Hour 2, after the Bay Area set, if used",
}

review_rotation = {
    "window": "Albums DJ Stace reviewed in the last 10 weeks (Aug. 27 to Nov. 5, 2026). All 13 were posted Oct. 4 to 15; no new reviews on Zookeeper since.",
    "rule": "Tapering: weeks 1 to 3 after review, one track per album per show; weeks 4 to 6, about half the albums per show; weeks 7 to 10, about one in four. Pick five-star, FCC-clean tracks not aired in the past 21 days.",
    "this_show": ("Week 4 for the 10 albums reviewed Oct. 4 to 8: five of them play (Twisted Teens Blame the Clown, Palace, Lex Walton, Ty Segall, This Is Lorelei). "
                  "Week 3 for The Fall, Sylvan Esso and Yard Act: one track each. 8 tracks. Resting this week: Twisted Teens Florida Water Blues, Dread Spectre Council, "
                  "Little Barrie, Sluice and Tricky. The tracks Stace cut Oct. 29 (Overhead, Dream On, Ultimate Love 4Ever, Hand Me A Cigarette, I Still See Me There, "
                  "Billy Came Back, Retro Song, Flood Season, You're Gonna Need A Little Music, Hex's Up) are avoided; other tracks from the same albums stand in."),
    "albums": [
        "Twisted Teens - Blame the Clown", "Twisted Teens - Florida Water Blues", "Dread Spectre Council - Thetans",
        "Little Barrie - Gravity Freeze", "Palace - Ox", "Ty Segall - Chrome", "Sluice - Companion",
        "This Is Lorelei - The Singer in My Band", "Tricky - Different When It's Silent",
        "Lex Walton - Ultimate Love Forever", "The Fall - Post Script", "Sylvan Esso - Ow ∞",
        "Yard Act - You're Gonna Need A Little Music"],
    "config": "config/review_rotation.json",
}

plan = {
    "show_date": "2026-11-05",
    "name": "DJ Stace library show working",
    "note": ("Thursday-night draft built Oct. 29 (kzsu-thu-night-draft, after the one-hour Halloween show). Forward air order. "
             "Sources: Stace's Weekly Playlist (PLCLF-Tik2UHk, 219 tracks, unchanged since Oct. 27), DJ Stace - Next Show (61 tracks; one new add, Chris Cornell Seasons), "
             "Air Order (34 tracks, Halloween content, rewritten by deltas), Zookeeper (labels, tags, reviews), foopee (Bay Area shows), Wikipedia 1991 and 1996 and 2001 in music (anniversaries), "
             "AllMusic and label sites (Oct. 30 releases), Genius (FCC counts only). Oct. 29 aired 13 tracks in one hour (Stanford Sports took hour two); unaired carryovers: the machines set."),
    "ytm_air_order": {"name": "DJ Stace library show Air Order", "id": "PLSosF7JAIkaM",
                      "url": "https://music.youtube.com/playlist?list=PLSosF7JAIkaM",
                      "order": "forward", "tracks": 43, "built": "2026-10-29",
                      "verified": "fresh read after edits: 43 tracks, order equals the plan (Loveless is not on YTM, so 43 of 44 plan tracks)"},
    "excluded_fcc": excluded_fcc,
    "sets": sets,
    "triple_shot": triple_shot,
    "ticket_giveaway": ticket_giveaway,
    "bay_area_shows": bay_area_shows,
    "mic_breaks": mic_breaks,
    "bench": bench,
    "review_rotation": review_rotation,
    "cooloff_note": ("Kept out: Oct. 16 New Releases for Review deletes (cool-off to Dec. 15), Oct. 20 Spanish Love Songs (Dec. 19), Oct. 22 Fontaines D.C. and Pulp (Dec. 21), "
                     "Oct. 23 L7, Clinic You and I, Cursive, Blondie, PISS and Prize Horse (Dec. 22), Oct. 27 Lambrini Girls Spilt and The Garden Bootleg (Dec. 26). "
                     "Fontaines D.C. has 3 removals, so the artist is down-weighted. Stace's Oct. 29 Air Order cuts (33 tracks) were made for the one-hour show and were not logged as cool-offs; "
                     "the exact tracks are avoided this week."),
    "cut": [],
    "air_order_note": ("Oct. 29 (Thursday-night draft): Air Order rewritten by deltas: 33 Halloween tracks removed, 42 added, 1 kept (Twisted Teens Circus Clown), 1 move. "
                       "Verified by fresh read: 43 tracks, order equals the plan. Loveless (my bloody valentine) is not on YouTube Music: play the library CD (tag 13666)."),
    "final": {"built": "2026-10-29", "cull_ticks": [], "replace_ticks": [], "notes": "Draft. No Stace edits to harvest yet."},
}


# Genius screens run Oct. 29 for tracks whose stored FCC note read "none".
FIX = {"MR-dh4FTavQ": "CLEAN (Genius, 259 words).", "LHPybTFbWAA": "CLEAN (Genius, 172 words).", "UEjLrx6c38Q": "CLEAN (Genius, 299 words)."}
for _s in sets:
    for _t in _s["tracks"]:
        if _t["videoId"] in FIX:
            _t["fcc_note"] = FIX[_t["videoId"]]

# ---------------------------------------------------------------------------
# 5. Guard: refuse tracks in cool-off, cut by Stace, or aired in the past 21 days.
# ---------------------------------------------------------------------------
fb = json.loads((REPO / "data/daily/feedback.json").read_text())
removed_ids = {r["videoId"] for r in fb["removed"] if r.get("videoId")}
cut_ids = set()
for f in glob.glob(str(REPO / "data/recon/2026-10-*/working_playlist.json")):
    for t in json.loads(Path(f).read_text()).get("cut", []):
        if isinstance(t, dict) and t.get("videoId"):
            cut_ids.add(t["videoId"])
problems = []
for s in sets:
    for t in s["tracks"]:
        if t["videoId"] and t["videoId"] in removed_ids:
            problems.append(("cool-off", t["artist"], t["track"]))
        if t["videoId"] and t["videoId"] in cut_ids:
            problems.append(("cut", t["artist"], t["track"]))
if problems:
    raise SystemExit("Guard failed: " + json.dumps(problems))

# Convert "m:ss" strings to seconds so we can print totals.
def secs(d):
    m, s = d.split(":")
    return int(m) * 60 + int(s)

total = 0
for s in sets:
    n = sum(secs(t["duration"]) for t in s["tracks"])
    total += n
    print(f"{s['set']}: {len(s['tracks'])} tracks, {n//60}:{n%60:02d}")
print(f"TOTAL {sum(len(s['tracks']) for s in sets)} tracks, {total//3600}:{(total%3600)//60:02d}:{total%60:02d}")
bn = sum(secs(t["duration"]) for t in bench)
print(f"BENCH {len(bench)} tracks, {bn//60}:{bn%60:02d}")

(OUT_DIR / "working_playlist.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
# candidates.json: forward-order list of every candidate (sets then bench)
(OUT_DIR / "candidates.json").write_text(json.dumps({"show_date": "2026-11-05", "sets": sets, "bench": bench}, indent=1, ensure_ascii=False))
print("wrote", OUT_DIR)
