#!/usr/bin/env python3
"""Build data/recon/2026-10-22/working_playlist.json (the Oct. 22, 2026 show plan).

Beginner notes:
- A "plan" is one JSON file. It holds "sets" (groups of tracks in air order) plus
  extra keys such as the Triple Shot, mic-break talking points and a bench.
- Each track is a Python dict. The helper T() fills in default fields so every
  track has the same keys.
- carry() copies a track that was already researched for last week's plan, so we
  keep its videoId, tag and label instead of looking them up again.
- Run from the repo root:  python3 scripts/build_plan_2026-10-22.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent          # repo root folder
OUT_DIR = REPO / "data" / "recon" / "2026-10-22"       # where the new plan goes
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Load last week's plan so carried-over tracks keep their metadata.
# ---------------------------------------------------------------------------
prev = json.loads((REPO / "data/recon/2026-10-15/working_playlist.json").read_text())
prev_cands = json.loads((REPO / "data/recon/2026-10-15/candidates.json").read_text())

lookup = {}  # (artist, track) -> track dict
def _index(tracks):
    for t in tracks:
        lookup[(t["artist"], t["track"])] = t
for s in prev["sets"]:
    _index(s["tracks"])
_index(prev.get("bench", []))
# candidates.json may be a dict with "sets" or a list; handle both shapes
if isinstance(prev_cands, dict):
    for s in prev_cands.get("sets", []):
        _index(s["tracks"])
    _index(prev_cands.get("bench", []))


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


def carry(artist, track, priority, why, **over):
    """Copy a track from last week's plan and change priority, why and any field."""
    d = dict(lookup[(artist, track)])
    d["priority"] = priority
    d["why"] = why
    d["source"] = "carried from Oct. 15 plan"
    d.pop("added_by", None)
    d.update(over)
    return d


CLEAN_G = lambda n: f"CLEAN (Genius, {n} words)."
REVIEWED = "DJ Stace review (Zookeeper, reviewed Oct. 4 to 8, 2026): no FCC flag on this track."

# ---------------------------------------------------------------------------
# 2. Sets (forward air order). Target: about 75 minutes of music per hour.
# ---------------------------------------------------------------------------
sets = []

# ---- Hour 1, Set 1 -------------------------------------------------------
sets.append({"set": "Hour 1, Set 1: Loud and new, plus reviews in rotation", "tracks": [
    carry("Dummy", "Full Spectrum Dominance", "R",
          "Album out today (Fri. Oct. 16) on Polyvinyl. Carried over: it did not air Oct. 15."),
    T("Heavens to Betsy", "baby's gone", "baby's gone", "Yoyo Recordings",
      "zookeeper album 58171 (Throw: The Yoyo Studio Compilation, original release); new compilation out Oct. 16",
      "58171", "2026-10-16 (compilation)", "single", "2:25", "O",
      "New Heavens to Betsy compilation out Oct. 16. Carried over: 'ain't never goin' back' did not air Oct. 15.",
      "CLEAN", CLEAN_G(150), "recon", "vHOfGp9F1Pw"),
    T("Twisted Teens", "Peekaboo Hand", "Blame the Clown", "Chain Smoking Records",
      "zookeeper album 1156418 (library spells it 'Peakaboo Hand')", "1156418",
      "2026-02-13", "album track", "3:23", "O",
      "Reviewed rotation, week 2: five stars in DJ Stace's review. Holy Cross Tigers is out Nov. 6.",
      "CLEAN", REVIEWED, "review rotation", "J2IJ6ugcmUI"),
    T("Twisted Teens", "Top Of The World Hwy No. 2", "Florida Water Blues", "Chain Smoking Records",
      "zookeeper album 1156430", "1156430", "2026-07-10", "album track", "2:12", "O",
      "Reviewed rotation, week 2: five stars in DJ Stace's review.",
      "CLEAN", REVIEWED, "review rotation", "UmRuVav12FA"),
    T("Lex Walton", "For Thee I Sing", "Ultimate Love Forever", "Sub Pop Records",
      "zookeeper album 1156519", "1156519", "2026-08-26", "album track", "2:01", "O",
      "Reviewed rotation, week 2: five stars. Opener of the album. CD and LP out Nov. 20.",
      "CLEAN", REVIEWED, "review rotation", "w7PnWZXJwoc"),
    T("Yard Act", "New Beginnings", "You're Gonna Need A Little Music", "Republic Records",
      "zookeeper album 1156564", "1156564", "2026-07-17", "album track", "3:28", "O",
      "Reviewed rotation, week 2: five stars. Over The Barrel aired Oct. 1, so a different track.",
      "CLEAN", REVIEWED, "review rotation", "WUmzu_RDflM"),
    T("Little Barrie", "More Bad Miles Of Road", "Gravity Freeze", "Easy Eye Sound",
      "zookeeper album 1156452", "1156452", "2026-05-22", "single", "3:49", "O",
      "Reviewed rotation, week 2: five stars. Lead single, heavy play on the show.",
      "CLEAN", REVIEWED, "review rotation", "QXOOzvDc3Nk"),
]})

# ---- Hour 1, Set 2: Texas punk ------------------------------------------
sets.append({"set": "Hour 1, Set 2: Texas punk (Austin and San Antonio)", "tracks": [
    T("Big Boys", "Fun Fun Fun", "Fun Fun Fun", "Moment Records",
      "zookeeper label table (Moment Records); original 1982 EP per Discogs, verify; not in library",
      "", "1982", "EP track", "3:15", "R",
      "Texas punk arc (config/show_focus.json), Austin. Funk-punk from Randy 'Biscuit' Turner's band.",
      "CLEAN", CLEAN_G(183), "recon", "fvFLtKkzL-g"),
    T("Scratch Acid", "Mary Had a Little Drug Problem", "Berserker", "Touch and Go",
      "zookeeper album 1034547", "1034547", "1986", "EP track", "2:17", "R",
      "Texas punk arc, Austin. Scratch Acid's David Yow went on to front The Jesus Lizard.",
      "CLEAN", "CLEAN (Genius, 88 words, short: may be partial lyrics; check by ear).", "recon", "4ULEdk2rIkY"),
    T("Butthole Surfers", "Pepper", "Electriclarryland", "Capitol Records (Jazz)",
      "zookeeper album 316886", "316886", "1996", "album track", "4:58", "O",
      "Texas punk arc, San Antonio. Last spin Aug. 6, 2026.",
      "CLEAN", CLEAN_G(377), "recon", "G8sGmSEehi4"),
    T("The Jesus Lizard", "Monkey Trick", "Goat", "Touch and Go",
      "zookeeper album 1086342", "1086342", "1991", "album track", "4:19", "R",
      "Texas punk arc. David Yow's band after Scratch Acid. Mouth Breather (piss x1) and Seasick (fuck x1) were skipped.",
      "CLEAN", CLEAN_G(238), "recon", "bCt7lZos7pM"),
    T("Ty Segall", "Separation", "Chrome", "Drag City",
      "zookeeper album 1156508", "1156508", "2026-08-28", "album track", "2:52", "O",
      "Reviewed rotation, week 2 (three stars: fast, snared-out punk rocker). Pairs with the Texas set. Play Cowboys aired Oct. 1 and Oct. 8; Black Paint is in cool-off.",
      "CLEAN", REVIEWED, "review rotation", "HOWV7yxxp8g"),
    T("Viagra Boys", "Medicine for Horses", "viagr aboys", "Year0001",
      "zookeeper label table (Year0001); not in library; release year unverified", "",
      "2025 (verify)", "album track", "2:51", "O",
      "Texas arc pairing named in config/show_focus.json (Ty Segall, Thee Oh Sees, Viagra Boys).",
      "CLEAN", CLEAN_G(249), "recon", "aDKGnFeLnF4"),
]})

# ---- Hour 1, Set 3: Fontaines D.C. (requested by DJ Stace) ---------------
XL = "Xl Recordings"
XLSRC = "zookeeper label table (Xl Recordings); album not in library yet"
sets.append({"set": "Hour 1, Set 3: Fontaines D.C., Dopamine Chamber (out Oct. 16)", "tracks": [
    T("Fontaines D.C.", "Six Shot Morning", "Dopamine Chamber", XL, XLSRC, "",
      "2026-10-16", "album track", "4:57", "R",
      "Requested by DJ Stace (Oct. 16). Album opener. All Genius lyrics screened Oct. 16 after release.",
      "CLEAN", CLEAN_G(179), "requested by DJ Stace", "00krktruwsM"),
    T("Fontaines D.C.", "Mimesis", "Dopamine Chamber", XL, XLSRC, "",
      "2026-10-16", "album track", "3:52", "R",
      "Requested by DJ Stace. Album track 3.",
      "CLEAN", CLEAN_G(334), "requested by DJ Stace", "zXyN6eZjlTg"),
    T("Fontaines D.C.", "Happy For You", "Dopamine Chamber", XL, XLSRC, "",
      "2026-10-16", "album track", "3:49", "R",
      "Requested by DJ Stace. Debuted live at Leeds Festival Aug. 29.",
      "CLEAN", CLEAN_G(175), "requested by DJ Stace", "wOkBZA51Z9o"),
    T("Fontaines D.C. & ROSALIA", "Where Is Gone?", "Dopamine Chamber", XL, XLSRC, "",
      "2026-10-16", "album track", "5:17", "R",
      "Requested by DJ Stace. Guest spot from Rosalia, the band's first guest on a record. Longest track on the album.",
      "CLEAN", CLEAN_G(245), "requested by DJ Stace", "3mb6YrCabso"),
]})

# ---- Hour 1, Set 4: reviewed albums -------------------------------------
sets.append({"set": "Hour 1, Set 4: Reviewed albums in rotation", "tracks": [
    T("Palace", "Denny's", "Ox", "Awal", "zookeeper album 1156463", "1156463",
      "2026-09-18", "album track", "4:50", "O",
      "Reviewed rotation, week 2: five stars. Made My Bed aired Oct. 1.",
      "CLEAN", REVIEWED, "review rotation", "vEL9U3Z1cvo"),
    T("Sluice", "Zillow", "Companion", "Mtn Laurel Recording Co.", "zookeeper album 1156485", "1156485",
      "2026-03-27", "album track", "3:13", "O",
      "Reviewed rotation, week 2: five stars. Beadie aired Oct. 15, so a different track.",
      "CLEAN", REVIEWED, "review rotation", "lpl4quk0T_g"),
    T("This Is Lorelei", "Don't You Cry in Lonesomeness", "The Singer in My Band", "Matador Records",
      "zookeeper album 1156441", "1156441", "2026-09-11", "album track", "3:19", "O",
      "Reviewed rotation, week 2: four stars. Oh No Now My (Oct. 8) and Hey Sarah (Oct. 1) already aired; Billy Came Back is in cool-off.",
      "CLEAN", REVIEWED, "review rotation", "cD_Av64P_qU"),
    T("Dread Spectre Council", "Hooves & Cloves", "Thetans", "Handmade Records",
      "zookeeper album 1156474", "1156474", "2026-03-29", "album track", "3:24", "O",
      "Reviewed rotation, week 2: five stars. Hex's Up aired Oct. 8.",
      "CLEAN", REVIEWED, "review rotation", "2fTel1iqDiQ"),
    T("Tricky", "Because I Don't Know", "Different When It's Silent", "False Idols",
      "zookeeper album 1156496", "1156496", "2026-07-17", "album track", "4:34", "O",
      "Reviewed rotation, week 2: five stars. 'The hit on the record,' per her review.",
      "CLEAN", REVIEWED, "review rotation", "gKkWSYQaxVo"),
]})

# ---- Hour 2, Set 5: Thursday Triple Shot -------------------------------
damned = [
    T("The Damned", "New Rose", "Damned Damned Damned", "Frontier",
      "zookeeper album 982492", "982492", "1976-10-22 (single, Stiff Records)", "single", "2:43", "R",
      "Triple Shot 1 of 3. Released Oct. 22, 1976: 50 years ago today. First UK punk single, produced by Nick Lowe.",
      "CLEAN", CLEAN_G(249), "triple shot", "ug3RfquyZl0"),
    T("The Damned", "Neat Neat Neat", "Damned Damned Damned", "Frontier",
      "zookeeper album 982492", "982492", "1977", "album track", "2:41", "R",
      "Triple Shot 2 of 3. From the debut LP, first UK punk album.",
      "CLEAN", CLEAN_G(356), "triple shot", "gXKDtkCzSCw"),
    T("The Damned", "Love Song", "Machine Gun Etiquette", "Emi Records",
      "zookeeper album 982504", "982504", "1979", "album track", "2:22", "R",
      "Triple Shot 3 of 3. 1979 turn toward power pop; shows range.",
      "CLEAN", CLEAN_G(242), "triple shot", "F5fHfGZENbQ"),
]
sets.append({"set": "Hour 2, Thursday Triple Shot: The Damned", "tracks": damned})

# ---- Hour 2, Set 6: Bay Area, upcoming shows only ----------------------
sets.append({"set": "Hour 2, Set 6: Bay Area, this weekend and next (upcoming shows only)", "tracks": [
    T("Cheekface", "No Fly Zone", "Podium", "Cheekface (self-released)",
      "web (Bandcamp, Tower Records; verify); not in Zookeeper label table", "",
      "2026-07-28", "album track", "4:14", "O",
      "Fri. Oct. 23, Cornerstone, Berkeley, with BODEGA ($36). Foopee lists Waitress as support on a second entry: confirm the bill. In the Weekly Playlist (Friday sweep).",
      "CLEAN", CLEAN_G(382), "weekly playlist (Friday sweep)", "RoeVGBKwnkU"),
    T("BODEGA", "Territorial Call of the Female", "Broken Equipment", "Chrysalis Records",
      "past spins (BODEGA, Chrysalis); verify for this album", "", "2022", "album track", "2:46", "R",
      "Fri. Oct. 23, Cornerstone, Berkeley, with Cheekface. DJ Stace added it to the Weekly Playlist.",
      "CLEAN", CLEAN_G(276), "added_by_stace (Weekly Playlist)", "rg1uP4mxXzE"),
    T("Frightwig", "Big Bang", "Wild Women Never Die", "Southern Records",
      "zookeeper album 820819", "820819", "1990 (verify)", "album track", "4:02", "O",
      "Fri. Oct. 23, Chapel, S.F., with AroMa and scary story time ($25). San Francisco punk band. YTM lists the track on 'We Need to Talk'; the library holds it on Wild Women Never Die.",
      "CLEAN", CLEAN_G(123), "recon", "omuKcuxMQq4"),
    carry("Julia Jacklin", "Get Away From Me (I Think I'll Love You Soon)", "O",
          "Fri. Oct. 23, Castro, S.F. (foopee: sold out). Carried over: it did not air Oct. 15.",
          label="4AD", label_source="zookeeper label table"),
    T("Protomartyr", "Feast of Stephen", "The Agent Intellect", "Hardly Art",
      "zookeeper album 1084193", "1084193", "2021", "album track", "2:25", "O",
      "Fri. Oct. 23, The Ritz, San Jose, with Accessory ($26/$30). Different track from the earlier cool-off pick.",
      "CLEAN", CLEAN_G(80), "recon", "4Yf-8hL7lzk"),
    T("Black Flag", "Rise Above", "Damaged", "Sst Records/New Alliance",
      "zookeeper album 828772", "828772", "1981", "album track", "2:27", "O",
      "Sun. Oct. 25, Cornerstone, Berkeley ($45.80, Greg Ginn lineup); Fri. Oct. 23, Felton Music Hall. Nervous Breakdown skipped (fuck x2, Outro).",
      "CLEAN", CLEAN_G(242), "recon", "wDUYCyajDcs"),
]})

# ---- Hour 2, Set 7: Machines and motorik (requested by DJ Stace) -------
sets.append({"set": "Hour 2, Set 7: Machines and motorik", "tracks": [
    carry("Kraftwerk", "Numbers (2009 Remaster)", "R",
          "Requested back by DJ Stace (Oct. 16): she liked the set and did not get to play it Oct. 15.",
          label="Elektra Classics", tag="892751", album="Computer World (2009 Remaster)",
          label_source="zookeeper album 892751 (library CD pairs The Man Machine with Computer World; contains Numbers)"),
    carry("Cabaret Voltaire", "Nag, Nag, Nag", "R",
          "Requested back by DJ Stace. Sheffield, 1979 single on Rough Trade.",
          label="Rough Trade Records", label_source="zookeeper label table (Rough Trade Records); original 1979 single"),
    carry("Fujiya & Miyagi", "No Green Light", "R",
          "Requested back by DJ Stace. New Shiny Object is out Oct. 30. It aired Oct. 15 per the Zookeeper log, so this is a second week for a new single.",
          ),
]})

# ---- Hour 2, Set 8: anniversaries, new and slow -----------------------
sets.append({"set": "Hour 2, Set 8: Anniversary, new and slow", "tracks": [
    T("Pulp", "The Trees", "We Love Life", "Sanctuary Records Inc.",
      "zookeeper album 667571", "667571", "2001-10-22", "album track", "4:53", "O",
      "25th anniversary today. We Love Life came out Oct. 22, 2001 on Island, produced by Scott Walker; UK No. 6.",
      "CLEAN", CLEAN_G(240), "recon", "dXyQj36I2Vc"),
    carry("The Avalanches", "Blue Shadows (feat. Karen O)", "O",
          "No Bad Memories out Oct. 16. Carried from the Oct. 15 bench. Karen O guest.",
          label="Modular Recordings", label_source="zookeeper label table (Modular Recordings)"),
    T("Sylvan Esso", "Concrete Glen", "Ow ∞", "Psychic Hotline",
      "zookeeper album 1156542", "1156542", "2026-09-11", "album track", "3:30", "O",
      "Reviewed rotation, week 2: four stars. Hot Slob is the one with a radio edit; skipped.",
      "CLEAN", REVIEWED, "review rotation", "PVcU0z1zPqk"),
    T("The Fall", "A Caveat", "Post Script", "Cog Sinister",
      "zookeeper album 1156531", "1156531", "2026-10-02", "album track", "4:10", "O",
      "Reviewed rotation, week 2: four stars. 30 Degrees aired Oct. 15.",
      "CLEAN", REVIEWED, "review rotation", "BSraSIhC_8A"),
    T("Pretenders", "Don't Get Me Wrong", "Get Close", "Sire Records",
      "zookeeper label table (Sire Records, US label); not in library", "",
      "1986-10-20 (UK)", "album track", "3:47", "O",
      "40 years: Get Close came out in the UK Oct. 20, 1986. In the Weekly Playlist (Friday sweep).",
      "CLEAN", CLEAN_G(179), "weekly playlist (Friday sweep)", "DD-5_lCEMHY"),
]})

# ---- Hour 2, Set 9: heavy, psych and short ----------------------------
sets.append({"set": "Hour 2, Set 9: Heavy, psych and short", "tracks": [
    carry("Goat", "I Sing in Silence", "O", "Carried over: it did not air Oct. 15."),
    carry("Allah-Las", "Sandy", "O", "Carried over: it did not air Oct. 15."),
    carry("Twin Peaks", "Walk to the One You Love", "O", "Carried over: it did not air Oct. 15."),
    carry("feeble little horse", "Doorway", "O", "Carried over: it did not air Oct. 15."),
    carry("Star Moles", "The End", "O", "Carried over: it did not air Oct. 15."),
    carry("R.M.F.C.", "The Clue", "X", "Carried over: it did not air Oct. 15. Listen first (lyrics not posted)."),
]})

# ---------------------------------------------------------------------------
# 3. Bench: extra tracks that are NOT in the Air Order (about 40 minutes).
# ---------------------------------------------------------------------------
bench = [
    T("Fontaines D.C.", "Demolition", "Dopamine Chamber", XL, XLSRC, "", "2026-10-16", "album track", "3:20", "X",
      "Bench alternate from Dopamine Chamber.", "CLEAN", CLEAN_G(327), "recon", "rklNhjSMoRU"),
    T("Fontaines D.C.", "You Miss Me", "Dopamine Chamber", XL, XLSRC, "", "2026-10-16", "album track", "3:36", "X",
      "Bench alternate from Dopamine Chamber.", "CLEAN", CLEAN_G(304), "recon", "RvziQmXK5AE"),
    T("Fontaines D.C.", "One Man", "Dopamine Chamber", XL, XLSRC, "", "2026-10-16", "album track", "4:59", "X",
      "Bench alternate from Dopamine Chamber.", "CLEAN", CLEAN_G(196), "recon", "K5lfTPIB-tg"),
    T("Fontaines D.C.", "Intimate", "Dopamine Chamber", XL, XLSRC, "", "2026-10-16", "album track", "3:58", "X",
      "Bench alternate from Dopamine Chamber. Album closer.", "CLEAN", CLEAN_G(289), "recon", "8vq2IpWFBGI"),
    T("Scratch Acid", "Unlike A Baptist", "Just Keep Eating", "Rabid Cat",
      "web (verify); not checked in Zookeeper label table", "", "1986", "album track", "2:33", "X",
      "Texas arc alternate.", "CLEAN", CLEAN_G(97) , "recon", "vfjUF3nm0hg"),
    carry("Jozef Van Wissem & Jim Jarmusch", "Never Like You Said (feat. Courtney Barnett)", "X",
          "Single Sept. 9; albums Nov. 6 on Sacred Bones."),
    carry("R.M.F.C.", "Mirror", "X", "Listen first (lyrics not posted)."),
    carry("Radio Free Alice", "Lunch Money", "X", "Carried over from the Oct. 15 closer slot."),
    carry("Perfume Genius", "Queen", "X", "Carried over twice; it did not air Oct. 15."),
    T("Heavens to Betsy", "ain't never goin' back", "baby's gone", "Kill Rock Stars",
      "zookeeper label table (Kill Rock Stars); new compilation", "", "2026-10-16", "single", "1:47", "X",
      "Lead single from baby's gone (out Oct. 16, Kill Rock Stars). In the Weekly Playlist.", "CLEAN", CLEAN_G(145), "weekly playlist (Friday sweep)", "7oGmnzdsvis"),
    T("Dummy", "Omen Globe", "do you love the color of the sky?", "Polyvinyl Record Co.",
      "zookeeper label table", "", "2026-10-16", "album track", "2:36", "X",
      "Alternate from the Dummy album out Oct. 16.", "CLEAN", CLEAN_G(113), "weekly playlist (Friday sweep)", "VUCZsqAvpNM"),
    T("Eels", "Cap In Hand", "Cookie Happened", "E Works / Play It Again Sam",
      "web (Friday sweep; verify); not in Zookeeper label table", "", "2026-10-16", "album track", "3:33", "X",
      "Eels' 16th album, out Oct. 16.", "CLEAN", CLEAN_G(134), "weekly playlist (Friday sweep)", "pZdk9sFjiw4"),
    T("@", "I Know You Are (But What Am I Thinking)", "Autosmile", "4AD",
      "zookeeper label table (4AD)", "", "2026-10-16", "single", "2:53", "X",
      "Second album, first for 4AD, out Oct. 16.", "CLEAN", CLEAN_G(201), "weekly playlist (Friday sweep)", "6btDJcSMQSQ"),
    T("Blondie", "Spectral Eyes", "Spectral Eyes (single)", "",
      "unverified", "", "2026-10-16", "single", "4:10", "X",
      "New single Oct. 16 (Shatter the Standards list only; verify).", "CLEAN", CLEAN_G(247), "weekly playlist (Friday sweep)", "_26EsYNmkAc"),
    T("Frightwig", "Hot Air Rising (Peace Now Mix)", "Hot Air Rising (single)", "",
      "unverified", "", "2026", "single", "3:43", "X",
      "New Frightwig single. Chapel, S.F., Fri. Oct. 23. Listen first: no lyrics found.", "UNVERIFIED", "UNVERIFIED: no lyrics found. Listen first.", "weekly playlist (Friday sweep)", "nmXsPvGqeHI"),
]

# FCC findings from this run (never reproduces lyrics; counts only)
excluded_fcc = [
    {"artist": "Fontaines D.C.", "track": "Tongue", "fcc": "shit x10 (Refrain)", "action": "FCC Edit Needed (single, Sept. 30)"},
    {"artist": "Fontaines D.C.", "track": "Japan", "fcc": "fuck x3, shit x3 (Chorus)", "action": "not used; Dopamine Chamber track 10"},
    {"artist": "Scratch Acid", "track": "Crazy Dan", "fcc": "fuck x2, shit x1 (unlabeled); caution bitch x2, goddamn x1", "action": "not used"},
    {"artist": "The Jesus Lizard", "track": "Mouth Breather", "fcc": "piss x1 (Verse)", "action": "Monkey Trick used instead"},
    {"artist": "The Jesus Lizard", "track": "Seasick", "fcc": "fuck x1 (unlabeled)", "action": "Monkey Trick used instead"},
    {"artist": "Black Flag", "track": "Nervous Breakdown", "fcc": "fuck x2 (Outro)", "action": "Rise Above used instead"},
    {"artist": "Frightwig", "track": "Crazy World", "fcc": "cock x1 (unlabeled)", "action": "Big Bang used instead"},
    {"artist": "Viagra Boys", "track": "Waterboy", "fcc": "fuck x2 (Verse 1, Verse 2)", "action": "Medicine for Horses used instead"},
    {"artist": "BODEGA", "track": "All Inside Aquarium", "fcc": "fuck x2", "action": "FCC Edit Needed candidate; Territorial Call of the Female used instead"},
    {"artist": "The Jesus Lizard", "track": "Then Comes Dudley", "fcc": "caution asshole x1", "action": "not used"},
    {"artist": "Sylvan Esso", "track": "Hot Slob", "fcc": "fuck x3, bitch x1 (per DJ Stace review)", "action": "DJ Stace has a radio edit; not planned"},
    {"artist": "Yard Act", "track": "Empty Pledges / Tall Tales / Janey Said / Redeemer", "fcc": "fuck, shit (per DJ Stace review)", "action": "New Beginnings used instead"},
]

# ---------------------------------------------------------------------------
# 4. Extras: Triple Shot, Bay Area (upcoming only), mic breaks, giveaways
# ---------------------------------------------------------------------------
triple_shot = {
    "artist": "The Damned",
    "angle": ("New Rose came out Oct. 22, 1976 on Stiff Records: the first UK punk single, 50 years ago on show day. "
              "Three eras: the 1976 single, the 1977 debut LP, and the 1979 turn toward power pop. "
              "No new release this week, so the anchor is the anniversary (house rule fallback)."),
    "tracks": damned,
}

bay_area_shows = [
    {"date": "Fri. Oct. 23", "venue": "Cornerstone, Berkeley",
     "what": "Cheekface with BODEGA. $36, doors 8 p.m., show 9 p.m.",
     "note": "Foopee lists a second entry with Waitress as support. Confirm the bill before air."},
    {"date": "Fri. Oct. 23", "venue": "Chapel, S.F.",
     "what": "Frightwig, AroMa, scary story time. $25, 7 p.m.", "note": ""},
    {"date": "Fri. Oct. 23", "venue": "Castro, S.F.",
     "what": "Julia Jacklin, Jordan Patterson. $48+, 7 p.m.", "note": "Sold out per foopee."},
    {"date": "Fri. Oct. 23", "venue": "The Ritz, San Jose",
     "what": "Protomartyr, Accessory. $26/$30, 8 p.m.", "note": ""},
    {"date": "Fri. Oct. 23 and Sun. Oct. 25", "venue": "Felton Music Hall, Felton (Fri.); Cornerstone, Berkeley (Sun.)",
     "what": "Black Flag (Greg Ginn, Max Zanelly, David Rodriquez, Bryce Weston). Sun. $45.80, 7 p.m.", "note": "Lineup is Ginn's."},
    {"date": "Wed. Oct. 28", "venue": "Fillmore, S.F.",
     "what": "Slow Pulp. From the KZSU ticket sheet.", "note": "Listed DJ: Cleo."},
]

mic_breaks = {
    "opening": [
        "Punk and post-punk focus, week 2 of 4: Texas punk tonight. Halloween post-punk Oct. 29, D.C. hardcore Nov. 5.",
        "Fontaines D.C. released Dopamine Chamber last Friday, Oct. 16, on XL. Produced by James Ford, 11 tracks. Set 3 plays four of them.",
        "New Rose by The Damned turns 50 tonight. Triple Shot opens Hour 2.",
    ],
    "after_texas_set": [
        "Scratch Acid formed in Austin. David Yow sang for them, then fronted The Jesus Lizard. Goat (Touch and Go) is from 1991.",
        "Butthole Surfers came out of San Antonio. Pepper is from Electriclarryland (1996). Big Boys were an Austin band; Fun Fun Fun is a 1982 EP.",
    ],
    "after_fontaines": [
        "Dopamine Chamber is the band's fifth album and the second with James Ford. Rosalia is the first guest on a Fontaines record.",
        "Two songs from it, Tongue (shit x10) and Japan (fuck x3, shit x3), stay off the air. Their Europe and UK tour starts in Lisbon on Oct. 21 (verify).",
    ],
    "end_hour_1": [
        "Reviewed this month and in rotation: Twisted Teens (two albums), Lex Walton, Yard Act, Little Barrie, Palace, Sluice, This Is Lorelei, Dread Spectre Council, Tricky, Ty Segall.",
        "Station ID at the top of the hour.",
    ],
    "triple_shot_intro": [
        "Thursday Triple Shot: The Damned. New Rose, Oct. 22, 1976, Stiff Records, Nick Lowe producing. The B-side was a fast cover of the Beatles' Help!",
        "Neat Neat Neat is from the first UK punk album (1977). Love Song is from Machine Gun Etiquette (1979).",
    ],
    "bay_area_break": [
        "Fri. Oct. 23: Cheekface with BODEGA at Cornerstone in Berkeley; Frightwig at Chapel in San Francisco; Protomartyr at The Ritz in San Jose; Julia Jacklin at the Castro (sold out).",
        "Black Flag with Greg Ginn: Fri. Oct. 23 at Felton Music Hall and Sun. Oct. 25 at Cornerstone in Berkeley. Slow Pulp at the Fillmore Wed. Oct. 28.",
    ],
    "after_machines": [
        "Numbers is from Kraftwerk's Computer World (1981). Nag, Nag, Nag is Cabaret Voltaire's 1979 Rough Trade single. Fujiya & Miyagi's New Shiny Object is out Oct. 30.",
    ],
    "anniversary": [
        "Pulp released We Love Life on Oct. 22, 2001, produced by Scott Walker. It reached No. 6 in the UK.",
        "The Avalanches' No Bad Memories came out Oct. 16 with Karen O on Blue Shadows.",
    ],
    "closing": [
        "Next week, Oct. 29: Halloween post-punk.",
    ],
}

ticket_giveaway = {
    "default_rule_result": ("No row lists Stace with a give-by date on or after Oct. 22. "
                            "Rows dated before Oct. 22 (Dinosaur Jr., Hovvdy, Brit Floyd) are skipped: the shows have passed."),
    "proposed": "None placed. Upcoming rows without Stace: Tommy Castro (Freight, Oct. 22, Sherri), Gary Clark Jr (Fox, Oct. 23, Sherri and Shineymic), War & Treaty (Chapel, Oct. 26, Mr Bones), Slow Pulp (Fillmore, Oct. 28, Cleo).",
    "flag": "If DJ Stace wants one, Slow Pulp (Oct. 28) fits best; confirm with the listed DJ. Rules, call-in number and show time are not in the sheet: confirm before air.",
    "placement": "Hour 2, after the Bay Area set, if used",
}

review_rotation = {
    "window": "Albums DJ Stace reviewed in the last 10 weeks (Aug. 7 to Oct. 16, 2026). All 13 were posted Oct. 6 to 15.",
    "rule": "Tapering: weeks 1 to 3 after review, one track per album per show; weeks 4 to 6, about half the albums per show; weeks 7 to 10, about one in four. Pick five-star, FCC-clean tracks not aired in the past 21 days.",
    "this_show": "Week 2 for all 13 albums, one track each (13 tracks).",
    "albums": [
        "Twisted Teens - Blame the Clown", "Twisted Teens - Florida Water Blues", "Dread Spectre Council - Thetans",
        "Little Barrie - Gravity Freeze", "Palace - Ox", "Ty Segall - Chrome", "Sluice - Companion",
        "This Is Lorelei - The Singer in My Band", "Tricky - Different When It's Silent",
        "Lex Walton - Ultimate Love Forever", "The Fall - Post Script", "Sylvan Esso - Ow ∞",
        "Yard Act - You're Gonna Need A Little Music"],
    "config": "config/review_rotation.json",
}

plan = {
    "show_date": "2026-10-22",
    "name": "DJ Stace library show working",
    "note": ("Oct. 16 draft (Thursday-night run, fired Fri. Oct. 16 at 9:23 a.m. PT). Forward air order. "
             "Texas punk week of the punk and post-punk arc. DJ Stace requests Oct. 16: Fontaines D.C. Dopamine Chamber tracks, "
             "the Fujiya & Miyagi / Kraftwerk / Cabaret Voltaire set back in, albums reviewed in the last 10 weeks in tapering rotation, "
             "and Bay Area highlights for upcoming shows only. Sources: Stace's Weekly Playlist (PLCLF-Tik2UHk, 156 tracks, no changes since Oct. 13), "
             "Zookeeper reviews, foopee, EverydayAlbums, Genius (FCC counts only)."),
    "ytm_air_order": {"name": "DJ Stace library show Air Order", "id": "PLSosF7JAIkaM",
                      "url": "https://music.youtube.com/playlist?list=PLSosF7JAIkaM",
                      "order": "forward", "tracks": 45, "built": "2026-10-16", "verified": "re-read after edits: 45 tracks, order matches the plan"},
    "ytm_playlist": prev.get("ytm_playlist", {}),
    "excluded_fcc": excluded_fcc,
    "sets": sets,
    "triple_shot": triple_shot,
    "ticket_giveaway": ticket_giveaway,
    "bay_area_shows": bay_area_shows,
    "mic_breaks": mic_breaks,
    "bench": bench,
    "review_rotation": review_rotation,
    "cooloff_note": ("Oct. 16 New Releases for Review deletes (cool-off to Dec. 15) kept out of the plan and bench: TV Priest Cartoons, American Motors marlboro miles, Spiral XP Faith Electric, David Byrne and Daniel Pemberton Let Me Sell You A Dream, Dummy N of 1, BODEGA Olivia, Awning, Fat Dog, DIIV, Kings of Leon, The Tallest Man On Earth. Fontaines D.C. has 3 logged removals (Big, Jackie Down the Line, Tongue); the album tracks stay because DJ Stace asked for them on Oct. 16."),
    "cut": prev.get("cut", []),   # Stace's earlier cuts stay on file (60-day cool-offs)
    "air_order_note": ("Oct. 16: Air Order rewritten by deltas (40 removed, 36 added, 38 moves, 9 kept). YTM stores some Weekly tracks under a different videoId when added: "
                       "Fontaines D.C. Six Shot Morning, Mimesis and Happy For You, and Cheekface No Fly Zone use the Air Order ids."),
    "final": {"built": "2026-10-16", "cull_ticks": [], "replace_ticks": [], "notes": "Draft. No Stace edits to harvest yet."},
}

# Convert "m:ss" strings to seconds so we can print totals.
def secs(d):
    m, s = d.split(":")
    return int(m) * 60 + int(s)

total = 0
for i, s in enumerate(plan["sets"]):
    n = sum(secs(t["duration"]) for t in s["tracks"])
    total += n
    print(f"{s['set']}: {len(s['tracks'])} tracks, {n//60}:{n%60:02d}")
print(f"TOTAL {sum(len(s['tracks']) for s in sets)} tracks, {total//3600}:{(total%3600)//60:02d}:{total%60:02d}")
bn = sum(secs(t["duration"]) for t in bench)
print(f"BENCH {len(bench)} tracks, {bn//60}:{bn%60:02d}")

(OUT_DIR / "working_playlist.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
# candidates.json: forward-order list of every candidate (sets then bench)
cands = {"show_date": "2026-10-22", "sets": sets, "bench": bench}
(OUT_DIR / "candidates.json").write_text(json.dumps(cands, indent=1, ensure_ascii=False))
print("wrote", OUT_DIR)
