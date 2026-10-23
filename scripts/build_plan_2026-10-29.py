#!/usr/bin/env python3
"""Rebuild data/recon/2026-10-29/working_playlist.json (Halloween specialty show).

Beginner notes:
- A "plan" is one JSON file: "sets" (groups of tracks in air order) plus extra keys
  (Triple Shot, mic-break text, bench, and so on).
- carry() copies a track that was researched earlier (keeps its videoId, tag, label).
- rev() builds a reviewed-album track using album-level facts from last week's plan.
- Run from the repo root:  python3 scripts/build_plan_2026-10-29.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "data" / "recon" / "2026-10-29"

# ---------------------------------------------------------------------------
# 1. Load the existing Halloween plan (theme stays) and last week's plan.
# ---------------------------------------------------------------------------
# The Oct. 15 specialty seed is kept next to the plan so this script can be re-run.
cur = json.loads((OUT_DIR / "halloween_seed_2026-10-15.json").read_text())
prev = json.loads((REPO / "data/recon/2026-10-22/working_playlist.json").read_text())

by_name = {}          # (artist, track) -> track dict from the current Halloween plan
for s in cur["sets"]:
    for t in s["tracks"]:
        by_name[(t["artist"], t["track"])] = t

by_tag = {}           # library tag -> album-level fields from last week's plan
def _scan(tracks):
    for t in tracks:
        if t.get("tag"):
            by_tag.setdefault(t["tag"], t)
for s in prev["sets"]:
    _scan(s["tracks"])
_scan(prev.get("bench", []))
_scan(prev["triple_shot"]["tracks"])


def carry(artist, track, priority, why=None, **over):
    """Copy a Halloween-plan track; set priority; optionally replace the 'why' line."""
    d = dict(by_name[(artist, track)])
    d["priority"] = priority
    if why is not None:
        d["why"] = why
    d.update(over)
    return d


REVIEWED = ("DJ Stace review (Zookeeper, reviewed Oct. 4 to 15, 2026): "
            "no FCC flag on this track.")


def rev(tag, artist, track, vid, dur, why, album=None, label=None):
    """Reviewed-album track. Album, label and dates come from last week's plan by tag."""
    base = by_tag[tag]
    return dict(
        artist=artist, track=track, album=album or base["album"],
        label=label or base["label"], label_source=base["label_source"], tag=tag,
        released=base["released"], type="album track", upcoming="", duration=dur,
        priority="O", why=why, fcc_status="CLEAN", fcc_note=REVIEWED,
        source="review rotation", videoId=vid)


# ---------------------------------------------------------------------------
# 2. Sets (forward air order). Target: about 75 minutes of music per hour.
# ---------------------------------------------------------------------------
sets = []

sets.append({"set": "Hour 1, Set 1: Horror-punk and garage classics", "tracks": [
    carry("Ministry", "Every Day Is Halloween", "R",
          "Station favorite. Final album Hate to Go (Take Out or Delivery) out Fri. Oct. 30 on Cleopatra."),
    carry("Misfits", "Halloween", "R", "Clean Misfits. Single from 1981."),
    carry("Screamin' Jay Hawkins", "I Put a Spell on You", "R", "1956 original."),
    carry("The Sonics", "The Witch", "R", "Tacoma garage, 1965."),
    carry("The Cramps", "Goo Goo Muck", "R", "From Psychedelic Jungle (1981)."),
    carry("Misfits", "Night of the Living Dead", "R", "Single 1979; on Walk Among Us (1982)."),
    carry("Roky Erickson", "I Walked with a Zombie", "R", "Sets up the Lemonheads tribute."),
    carry("The Lemonheads", "Roky (feat. The Bevis Frond)", "R",
          "New: 12-inch out Oct. 16 on Fire Records."),
]})

sets.append({"set": "Hour 1, Set 2: Garage, psych and fuzz, plus reviews in rotation", "tracks": [
    rev("1156508", "Ty Segall", "Black Paint", "DG4Z4W1vG38", "2:00",
        "Reviewed rotation, week 3: five stars. Lead single from Chrome (Drag City). Fits Halloween."),
    rev("1156474", "Dread Spectre Council", "Raven", "KZkx50Y-Cyg", "4:54",
        "Reviewed rotation, week 3: five stars. Oslo one-man band. Segues from Ty Segall."),
    carry("The Black Angels", "Young Men Dead", "R", "Core artist."),
    carry("Thee Oh Sees", "Dead Man's Gun", "R"),
    rev("1156418", "Twisted Teens", "Circus Clown", "FWP2bTeoPTo", "2:06",
        "Reviewed rotation, week 3: four stars. Holy Cross Tigers is out Nov. 6 on Sub Pop."),
    rev("1156452", "Little Barrie", "It Isn't Soul", "N5_MhlEVILU", "2:49",
        "Reviewed rotation, week 3: three stars. More Bad Miles Of Road and Luggin' Hurt already aired."),
    carry("The Wytches", "Gravedweller", "R"),
    carry("Black Rebel Motorcycle Club", "Beat the Devil's Tattoo", "R"),
]})

# PiL: YTM carries the studio cut as "Swan Lake" (Second Edition); the song is Death Disco.
pil = dict(
    artist="Public Image Ltd.", track="Swan Lake (Death Disco)", album="Second Edition",
    label="Virgin Records", label_source="original release (Virgin, UK 1979); label spelled per Zookeeper label table; library holds PiL compilations only",
    tag="", released="1979", type="single", upcoming="", duration="4:14", priority="R",
    why=("Post-punk arc, week 3. Single titled Death Disco (July 1979); YTM lists the studio cut as Swan Lake. "
         "Last PiL spin Sept. 10."),
    fcc_status="CLEAN", fcc_note="CLEAN (Genius, 142 words).", source="recon", videoId="fiQk5hy54oE")
sets.append({"set": "Hour 1, Set 3: Goth and post-punk", "tracks": [
    carry("Siouxsie and the Banshees", "Spellbound", "R", "From Juju (1981)."),
    carry("The Cure", "Lullaby", "R", "Roger O'Donnell (keyboards) was born Oct. 29, 1955. Library holds the single."),
    carry("Joy Division", "Dead Souls", "R", "Post-punk arc. Last Joy Division spin Oct. 15 was Transmission."),
    pil,
    rev("1156531", "The Fall", "Retro Song", "ycqGbAOXpZ8", "4:10",
        "Reviewed rotation, week 2: four stars. Post Script out Oct. 2 on Cog Sinister."),
    carry("Pixies", "Dead", "R"),
]})

# Triple Shot: first set of Hour 2.
ts_tracks = [
    carry("Queens of the Stone Age", "Where the Goth Girls At?", "R",
          "Triple Shot 1 of 3. New single from Perfecth (out Fri. Oct. 30, Matador). Aired Oct. 1."),
    carry("Queens of the Stone Age", "No One Knows", "R", "Triple Shot 2 of 3. Biggest single, Songs for the Deaf (2002)."),
    carry("Queens of the Stone Age", "Burn the Witch", "R", "Triple Shot 3 of 3. Lullabies to Paralyze (2005). Halloween title."),
]
sets.append({"set": "Hour 2, Thursday Triple Shot: Queens of the Stone Age", "tracks": ts_tracks})

sets.append({"set": "Hour 2, Set 5: Dark classics and modern shadows", "tracks": [
    carry("Interpol", "Evil", "R"),
    carry("The Horrors", "Who Can Say", "R"),
    carry("Bambara", "Steel Dust Ocean", "R"),
    carry("Nick Cave & The Bad Seeds", "Red Right Hand", "R", "Core artist."),
    carry("Black Sabbath", "Black Sabbath", "R",
          "Long. Fits the Oct. 30, 1998 reunion fact (verify; thisdayinmusic only)."),
]})

sets.append({"set": "Hour 2, Set 6: Reviewed albums in rotation", "tracks": [
    rev("1156441", "This Is Lorelei", "Billy Came Back", "rpHYQQQKmos", "3:10",
        "Reviewed rotation, week 3: four stars. NACC No. 12 the week of Oct. 1."),
    rev("1156485", "Sluice", "Overhead", "UWCiupsV4Go", "3:57",
        "Reviewed rotation, week 3: five stars. Beadie and Zillow already aired."),
    rev("1156463", "Palace", "Dream On", "cpV4IHb0blw", "4:23",
        "Reviewed rotation, week 3: four stars. Lead single from Ox. Library lists the label as Awal (Palace Presents is the band's own label).",
        label="Awal"),
    rev("1156519", "Lex Walton", "Ultimate Love 4Ever", "uan9YB7O8nU", "3:06",
        "Reviewed rotation, week 3: five stars. CD and LP out Nov. 20 on Sub Pop."),
    rev("1156542", "Sylvan Esso", "Flood Season", "hwKqNONtRgE", "2:24",
        "Reviewed rotation, week 2: four stars."),
    rev("1156430", "Twisted Teens", "Hand Me A Cigarette", "IY_J7QS6tMo", "3:26",
        "Reviewed rotation, week 3: five stars."),
    rev("1156496", "Tricky", "I Still See Me There", "q3F5VkxFW4E", "3:39",
        "Reviewed rotation, week 3: four stars. Described in the review as sinister and hypnotic."),
    rev("1156564", "Yard Act", "You're Gonna Need A Little Music", "aGTuvSf85-s", "4:41",
        "Reviewed rotation, week 2: five stars."),
]})

fake_names = dict(
    artist="Fake Names", track="Punk Ruins", album="Punk Ruins", label="Epitaph Records",
    label_source="zookeeper label table (Epitaph Records 1094); album not in library yet",
    tag="", released="2026-10-23", type="album track (title track)", upcoming="", duration="2:37",
    priority="R",
    why=("New: third album out Fri. Oct. 23 on Epitaph. Brian Baker, Michael Hampton, Dennis Lyxzen, "
         "Johnny Temple, Mario Rubalcaba. Punk focus."),
    fcc_status="CLEAN", fcc_note="CLEAN (Genius, short; check by ear).", source="recon", videoId="D4S-TxPpaI8")
sets.append({"set": "Hour 2, Set 7: New, anniversary and novelty", "tracks": [
    fake_names,
    carry("Mitski", "Your Best American Girl", "R",
          "Puberty 2 10th Anniversary Edition out Fri. Oct. 30 (Dead Oceans)."),
    dict(artist="Lera Lynn & Shovels & Rope", track="Wolf Like Me (ft. Shovels & Rope)",
         album="Plays Well With Others", label="", label_source="unverified (not in library; Zookeeper has no Lera Lynn albums)",
         tag="", released="2018", type="album track", upcoming="", duration="4:06", priority="O",
         why=("DJ Stace added it to Next Show Oct. 20 to 22. Cover of the TV on the Radio song; werewolf theme fits Halloween. "
              "Shovels & Rope are on her Weekly Playlist."),
         fcc_status="CLEAN", fcc_note="CLEAN (Genius, 396 words).", source="Next Show (Stace add)",
         videoId="Lmyd9LTkpfk", added_by="DJ Stace"),
    carry("Bobby \"Boris\" Pickett", "Monster Mash", "R", "Novelty closer."),
]})

# ---------------------------------------------------------------------------
# 3. Bench (priority X): swap-ins, not in the draft Air Order.
# ---------------------------------------------------------------------------
bench = [
    carry("Bauhaus", "Bela Lugosi's Dead", "X", "Hour closer if time allows. 9:37."),
    carry("Love and Rockets", "Haunted When the Minutes Drag", "X", "Long. 8:02."),
    carry("Tom Waits", "What's He Building?", "X", "Spoken word; mic-break neighbor."),
    carry("Radiohead", "Burn the Witch", "X", "Same title as the QOTSA Triple Shot track; use one."),
    carry("Ty Segall", "Despoiler of Cadaver", "X", "Core artist. Black Paint is in Set 2."),
    carry("The Black Angels", "Black Grease", "X"),
    carry("Alex G", "Witch", "X"),
    carry("Spoon", "The Ghost of You Lingers", "X", "Core artist."),
    carry("The Kills", "Doing It To Death", "X"),
    carry("The Dead Weather", "Treat Me Like Your Mother", "X"),
    carry("Car Seat Headrest", "Sober to Death", "X", "Core artist."),
    carry("Zeal & Ardor", "Devil Is Fine", "X", "Aired 5 times."),
    carry("Alice Cooper", "Feed My Frankenstein", "X", "Novelty."),
    carry("The Flaming Lips", "One Night While Hunting for Faeries and Witches and Wizards to Kill", "X", "Long. 6:08."),
    carry("Diet Cig", "Blob Zombie", "X", "2:01. Short filler."),
    carry("Hurray for the Riff Raff", "Hungry Ghost", "X"),
    carry("Mr. Gnome", "Heave Yer Skeleton", "X", "Core artist. Label unverified."),
    carry("Jealous of the Birds", "Plastic Skeletons", "X", "Aired Aug. 2026. Label unverified."),
    carry("King Gizzard & The Lizard Wizard", "The Acrid Corpse", "X", "Bumper, 1:01. FCC unverified (instrumental interlude)."),
    dict(artist="Spirit Ghost", track="Dungeon Crawler", album="Dark Magic EP", label="Happen Twice (not in ZK label table)",
         label_source="web (verify)", tag="", released="2026-10-19 (single; EP Jan. 29, 2027)", type="single",
         upcoming="Dark Magic EP, Jan. 29, 2027", duration="3:18", priority="X",
         why="New single Oct. 19. Halloween title. Date rests on Stereogum alone (verify).",
         fcc_status="UNVERIFIED", fcc_note="UNVERIFIED (no lyrics on Genius yet).", source="weekly playlist",
         videoId="mvq1-dpQNXY"),
]

# ---------------------------------------------------------------------------
# 4. Extras: Triple Shot, Bay Area, mic breaks, giveaway, rotation.
# ---------------------------------------------------------------------------
triple_shot = {
    "artist": "Queens of the Stone Age",
    "angle": ("New single Where the Goth Girls At? from Perfecth (out Fri. Oct. 30, Matador; nine tracks, produced by Josh Homme "
              "and Michael Shuman), a Halloween-titled deep cut and the band's biggest single. Easy Street stays out (cool-off to Dec. 8)."),
    "tracks": [{"artist": t["artist"], "track": t["track"], "videoId": t["videoId"]} for t in ts_tracks],
    "history_check": "Not in the last 8 Triple Shot artists (Teenage Fanclub Oct. 8, Fontaines D.C. Oct. 15, The Damned Oct. 22).",
}

bay_area_shows = [
    {"date": "Thu. Oct. 29", "venue": "Bottom of the Hill, S.F.",
     "what": "Astrozombies SF, Rusty Chains, Caution (tribute night). $20/$25, 8 p.m.", "note": ""},
    {"date": "Thu. Oct. 29", "venue": "Kilowatt, S.F.",
     "what": "Halloween covers show: Spencer Noble, Band Yo!, Bromf, Mitch Rocket. $13.39, 7 p.m.", "note": ""},
    {"date": "Thu. Oct. 29", "venue": "Chapel, S.F.",
     "what": "Katie Pruitt, Olivia Barton. $25/$30, 7 p.m.", "note": "On the KZSU ticket sheet (Mr Bones); give-by 10/28 has passed."},
    {"date": "Fri. Oct. 30", "venue": "Great American Music Hall, S.F.",
     "what": "Cold Cave (solo), SRSQ, Houses of Heaven, Laura Krieg and more. $22 to $39, 6:30 p.m.", "note": "Post-punk and darkwave bill."},
    {"date": "Fri. Oct. 30", "venue": "Bottom of the Hill, S.F.",
     "what": "Temptation, Dead Souls, Flippy Floppy (tribute night). $20/$25, 8 p.m.", "note": ""},
    {"date": "Sat. Oct. 31", "venue": "Thee Stork Club, Oakland; UC Theater, Berkeley",
     "what": "Halloween tribute band extravaganza ($13/$15, 8 p.m.); Rocky Horror Picture Show with live cast ($16.50+, 7 p.m.).", "note": ""},
    {"date": "Sat. Oct. 31", "venue": "Uptown Theater, Napa",
     "what": "Oingo Boingo Former Members. $61.95, 7 p.m.", "note": ""},
    {"date": "Sun. Nov. 1", "venue": "Great American Music Hall, S.F.",
     "what": "Frankie And The Witch Fingers, Carrion Kids, Starzdust. $30/$53, 7 p.m.", "note": ""},
    {"date": "Source", "venue": "foopee.com the-list, week of Oct. 26, read Oct. 22",
     "what": "Confirm times and prices before air. Upcoming shows only.", "note": ""},
]

mic_breaks = {
    "opening": [
        "Halloween show. Punk and post-punk focus, week 3 of 4: goth and post-punk tonight. D.C. hardcore Nov. 5.",
        "Tonight: Ministry, Misfits, The Cramps, Siouxsie, Joy Division, then a Queens of the Stone Age Triple Shot to open Hour 2.",
        "Reviewed albums in rotation: one track each from 13 albums, spread through both hours.",
    ],
    "after_set_1": [
        "Screamin' Jay Hawkins recorded I Put a Spell on You in 1956. Misfits released Halloween as a single in 1981. The Cramps' Goo Goo Muck is from Psychedelic Jungle (1981).",
        "The Lemonheads released a 12-inch of Roky, with The Bevis Frond, on Oct. 16 on Fire Records. Roky Erickson's I Walked with a Zombie is from 1981.",
        "Ministry's final album, Hate to Go (Take Out or Delivery), is out Fri. Oct. 30 on Cleopatra. Closing track features former bassist Paul Barker. Farewell tour starts April 2, 2027 in Utrecht.",
    ],
    "end_hour_1": [
        "Joy Division, Siouxsie and The Cure tonight. Roger O'Donnell of The Cure was born Oct. 29, 1955.",
        "Public Image Ltd. released Death Disco in July 1979. YouTube Music lists the studio cut as Swan Lake.",
        "Station ID at the top of the hour.",
    ],
    "triple_shot_intro": [
        "Thursday Triple Shot: Queens of the Stone Age. Perfecth, the band's ninth album, is out Fri. Oct. 30 on Matador. Josh Homme and Michael Shuman produced it.",
        "Where the Goth Girls At? is the new single. No One Knows is from Songs for the Deaf (2002). Burn the Witch is from Lullabies to Paralyze (2005).",
    ],
    "after_triple_shot": [
        "On Oct. 30, 1938, CBS aired Orson Welles' War of the Worlds on The Mercury Theatre on the Air. The FCC investigated afterward and found no law was broken.",
    ],
    "bay_area_break": [
        "Tonight: Bottom of the Hill tribute night, a Halloween covers show at Kilowatt, Katie Pruitt at Chapel.",
        "Fri. Oct. 30: Cold Cave, SRSQ and Houses of Heaven at Great American Music Hall. Sat. Oct. 31: Halloween tribute bands at Thee Stork Club and Rocky Horror with a live cast at the UC Theater in Berkeley. Sun. Nov. 1: Frankie And The Witch Fingers at Great American Music Hall.",
    ],
    "anniversary": [
        "Mitski's Puberty 2 turns 10. The 10th Anniversary Edition is out Fri. Oct. 30 on Dead Oceans.",
        "Fake Names released Punk Ruins today (Oct. 23) on Epitaph. Recorded in five days at Electrical Audio in Chicago.",
        "Black Sabbath: the four original members reunited on Letterman Oct. 30, 1998 (verify).",
    ],
    "closing": [
        "Next week, Nov. 5: US hardcore and Washington D.C. Fugazi, Husker Du, Bad Brains, short songs.",
    ],
}

ticket_giveaway = {
    "default_rule_result": ("No sheet row lists Stace with a give-by date on or after Oct. 29. "
                            "The only Stace row (Brit Floyd, Oct. 14) has passed."),
    "proposed": "None placed. Katie Pruitt (Chapel, Oct. 29, Mr Bones) has a give-by of 10/28, before the show.",
    "flag": "If DJ Stace wants a giveaway, ask for a current row. Rules, call-in number and show time are not in the sheet: confirm before air.",
    "placement": "Hour 2, after the Bay Area break, if used",
}

review_rotation = {
    "window": "Albums DJ Stace reviewed in the last 10 weeks (Aug. 20 to Oct. 29, 2026). All 13 were posted Oct. 4 to 15.",
    "rule": "Tapering: weeks 1 to 3 after review, one track per album per show; weeks 4 to 6, about half the albums per show; weeks 7 to 10, about one in four. Pick five-star, FCC-clean tracks not aired in the past 21 days.",
    "this_show": "Week 3 for 10 albums (reviewed Oct. 4 to 8) and week 2 for The Fall, Sylvan Esso and Yard Act (posted Oct. 15). One track each (13 tracks). Next show (Nov. 5) is week 4 for the first 10: about half.",
    "albums": [
        "Twisted Teens - Blame the Clown", "Twisted Teens - Florida Water Blues", "Dread Spectre Council - Thetans",
        "Little Barrie - Gravity Freeze", "Palace - Ox", "Ty Segall - Chrome", "Sluice - Companion",
        "This Is Lorelei - The Singer in My Band", "Tricky - Different When It's Silent",
        "Lex Walton - Ultimate Love Forever", "The Fall - Post Script", "Sylvan Esso - Ow ∞",
        "Yard Act - You're Gonna Need A Little Music"],
    "config": "config/review_rotation.json",
}

excluded = [dict(x, action=x.get("action", "Held out of the plan")) for x in cur.get("excluded_fcc", [])] + [
    {"artist": "Death Valley Girls", "track": "Basic Witch",
     "fcc": "cool-off to Dec. 8 (Stace deleted from Weekly Oct. 9)", "action": "Dropped from the plan"},
]

plan = {
    "show_date": "2026-10-29",
    "theme": "Halloween",
    "name": "DJ Stace library show working",
    "note": (cur.get("note", "") + " Oct. 22 (Thursday-night run): resized to 75 minutes per hour; Triple Shot moved to the start of Hour 2; "
             "13 reviewed-album tracks added (tapering rotation); Death Valley Girls Basic Witch dropped (60-day cool-off to Dec. 8); "
             "Joy Division and Fall added to the post-punk set; Bay Area list refreshed from foopee. "
             "Stace's Weekly Playlist: 173 tracks (20 removals since Oct. 20, logged as housekeeping)."),
    "specialty_playlist": cur.get("specialty_playlist", {}),
    "excluded_fcc": excluded,
    "sets": sets,
    "triple_shot": triple_shot,
    "ticket_giveaway": ticket_giveaway,
    "today_in_music": {
        "oct_29": cur["today_in_music"]["oct_29"],
        "oct_30": cur["today_in_music"]["oct_30"] + [
            "1938: Orson Welles' War of the Worlds airs on CBS (Mercury Theatre on the Air, 8 p.m. ET).",
            "2026: Queens of the Stone Age, Perfecth (Matador), Ministry, Hate to Go (Cleopatra) and Mitski, Puberty 2 10th Anniversary Edition (Dead Oceans) are out."],
        "fits": cur["today_in_music"]["fits"],
        "source": "thisdayinmusic.com Oct. 29 and 30; Wikipedia and History.com (War of the Worlds); Matador, Side-Line (releases)",
    },
    "new_releases": cur["new_releases"] + [
        "Fake Names, Punk Ruins (Oct. 23, Epitaph).",
        "Spirit Ghost, Dungeon Crawler (single Oct. 19; Dark Magic EP Jan. 29, 2027; bench).",
    ],
    "bay_area_shows": bay_area_shows,
    "mic_breaks": mic_breaks,
    "bench": bench,
    "review_rotation": review_rotation,
    "cooloff_note": ("Kept out: Death Valley Girls Basic Witch and QOTSA Easy Street (Weekly deletes Oct. 9, cool-off to Dec. 8). "
                     "Oct. 16 New Releases for Review deletes (cool-off to Dec. 15) and Oct. 20 Spanish Love Songs (Dec. 19) stay out. "
                     "Iceage cool-off to Nov. 29."),
    "cut": cur.get("cut", []),
    "final": {"built": "2026-10-22", "cull_ticks": [], "replace_ticks": [], "notes": "Draft. No Stace edits to harvest yet."},
}


# Keep the label field clean for the Zookeeper CSV: move "(not in ZK label table)" notes to label_source.
for _t in [t for s in sets for t in s["tracks"]] + bench:
    for _note in (" (not in ZK label table)", " (verify)"):
        if _note in _t.get("label", ""):
            _t["label"] = _t["label"].replace(_note, "")
            _t["label_source"] = (_t.get("label_source", "") + f" [label{_note}]").strip()


def secs(d):
    m, s = d.split(":")
    return int(m) * 60 + int(s)


total = 0
for s in plan["sets"]:
    n = sum(secs(t["duration"]) for t in s["tracks"])
    total += n
    print(f"{s['set']}: {len(s['tracks'])} tracks, {n // 60}:{n % 60:02d}")
print(f"TOTAL {sum(len(s['tracks']) for s in sets)} tracks, {total // 3600}:{(total % 3600) // 60:02d}:{total % 60:02d}")
bn = sum(secs(t["duration"]) for t in bench)
print(f"BENCH {len(bench)} tracks, {bn // 60}:{bn % 60:02d}")

(OUT_DIR / "working_playlist.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
cands = {"show_date": "2026-10-29", "sets": sets, "bench": bench}
(OUT_DIR / "candidates.json").write_text(json.dumps(cands, indent=1, ensure_ascii=False))
print("wrote", OUT_DIR)
