#!/usr/bin/env python3
"""
final_update_2026-10-22b.py
Thursday Oct. 22 update after DJ Stace edited the Air Order again (YTM read Oct. 22, 55 tracks).
 * Removes the tracks she cut (3 Fontaines D.C., Pulp The Trees) and logs them.
 * Adds nine new tracks: three she placed inside the list and the last six, which she asked
   to be placed where they fit best.
 * Re-orders every set to follow her Air Order.
Beginner notes: the plan is JSON. We index every track by its YouTube videoId, describe the
new tracks, then rebuild each set from an explicit list of videoIds in air order.
"""
import json
from pathlib import Path

PLAN = Path("data/recon/2026-10-22/working_playlist.json")
FB = Path("data/daily/feedback.json")
plan = json.loads(PLAN.read_text(encoding="utf-8"))
old = {t["videoId"]: t for s in plan["sets"] for t in s["tracks"]}
names = [s["set"] for s in plan["sets"]]
S1, S2, S3, S4, TS, S6, S7, S8, S9 = names
S2 = "Hour 1, Set 2: Texas punk (Austin, San Antonio and Dallas)"

def new(artist, track, album, label, tag, released, typ, dur, why, fcc_status, fcc_note, vid, label_source, **extra):
    d = dict(artist=artist, track=track, album=album, label=label, label_source=label_source, tag=tag,
             released=released, type=typ, upcoming="", duration=dur, priority="R", why=why,
             fcc_status=fcc_status, fcc_note=fcc_note, source="added_by_stace", videoId=vid, added_by="DJ Stace")
    d.update(extra); return d

NEW = [
 new("Nervebreakers", "My Girlfriend is a Rock (Radio Edit)", "Politics EP", "Wild Child Records", "",
     "1978 (Politics EP)", "radio edit", "2:59",
     "Stace added this to the Air Order (Oct. 22). Dallas punk band; the song is from the 1978 Politics EP on Wild Child Records (Get Hip reissued it in 2021). The library has it only on the compilation Bloodstains Across Texas (Swedish Meathead Products, tag 487829). Label source conflict: one seller lists the EP as self-released.",
     "CLEAN", "CLEAN (Genius, 259 words). YTM lists the Radio Edit.", "NhfruZ2cHZo",
     "wikipedia + Get Hip Bandcamp (original 1978 label; not in ZK); library holds the Bloodstains Across Texas compilation only",
     source_url="https://en.wikipedia.org/wiki/The_Nervebreakers", zk_alt="Bloodstains Across Texas, tag 487829, Swedish Meathead Products"),
 new("Loco Gringos", "Ain't No Corndogs", "Loco Gringos", "Existential Vacuum", "1089648",
     "1992 (posthumous album; reissued 2006 and 2020)", "album track", "2:28",
     "Stace added this to the Air Order (Oct. 22). Dallas punk band. Their only album came out after singer Tom Foote died in 1990. In the library. No lyrics posted anywhere checked: listen first.",
     "UNVERIFIED", "UNVERIFIED: no lyrics posted on Genius or the Bandcamp page. Listen first.", "eF4RiUfPRNs",
     "zookeeper album 1089648", source_url="https://locogringosdallas.bandcamp.com/album/loco-gringos"),
 new("This Is Lorelei & MJ Lenderman", "Dancing in the Club (MJ Lenderman Version) (Radio Edit)", "Box for Buddy, Box for Star (Deluxe)",
     "Double Double Whammy", "", "2025-04-25", "radio edit", "4:56",
     "Stace added this to the Air Order (Oct. 22). Lenderman's cover of Lorelei's own song, from the 2025 deluxe edition of Box for Buddy, Box for Star. Second Lorelei track tonight (the album track comes just before it). The original has fuck x2 (Verse 4); YTM lists this as the Radio Edit: confirm the edit by ear.",
     "UNVERIFIED", "LISTEN FIRST: original has fuck x2 (Verse 4). YTM version is labeled Radio Edit; confirm the edit covers both.", "5X718hNafSM",
     "zookeeper label table 21310 (album not in library)", source_url="https://thisislorelei.bandcamp.com/track/dancing-in-the-club-mj-lenderman-version"),
 new("Royal Blood", "Ten Over Ten", "Ten Over Ten", "Warner Records", "",
     "2026-08-12 (single; album Dead Company out Nov. 13, verify)", "single", "3:18",
     "Last six, placed at the end of Set 1 (loud and new, after Little Barrie). New single, first music since Back to the Water Below (2023). Dead Company is due Nov. 13 on Warner Records; sources list Nov. 6, 12 and 13, so verify. Zookeeper has Warner Bros. Records but not Warner Records.",
     "CLEAN", "CLEAN (Genius, 275 words).", "HzkJsKXCjvg",
     "media: Radio X, DIY (Warner Records); not in ZK label table as spelled", source_url="https://www.radiox.co.uk/artists/royal-blood/announce-details-of-dead-company-album-and-release-ten-over-ten-track/"),
 new("Westside Cowboy", "Kick Stones (The Boys)", "It Goes On", "Island Records", "",
     "2026-08-21 (album; single May 20)", "single", "3:57",
     "Last six, placed in Set 1 after Yard Act (British guitar bands). Manchester four-piece, debut album It Goes On out Aug. 21 on Island, lead single, album opener. Uptempo (about 139 BPM), Velvet Underground fuzz sped up. NACC #11. Your review draft is dated Oct. 21 and is not posted, so it is not in the rotation count.",
     "CLEAN", "CLEAN (Genius, 300 words; matches your review draft).", "W51Ik_1noH8",
     "zookeeper label table 10827 (album not in library)", source_url="https://westsidecowboy.bandcamp.com/album/it-goes-on"),
 new("Bauhaus", "The Passion of Lovers", "Mask", "Beggars Banquet", "273046",
     "1981 (single June, album Oct.)", "album track", "3:52",
     "Last six, placed in Set 7 after Cabaret Voltaire (1979 to 1981 post-punk). Single came out June 1981 on Beggars Banquet (BEG 59, UK No. 56); the album is Mask. Halloween post-punk is next week.",
     "CLEAN", "CLEAN (Genius, 256 words).", "qSk88IeNUr0",
     "zookeeper album 273046", source_url="https://en.wikipedia.org/wiki/The_Passion_of_Lovers"),
 new("Stef Chura", "Sweet Sweet Midnight", "Midnight", "Saddle Creek", "1135774",
     "2019", "album track", "5:30",
     "Last six, placed at the end of Set 8 (new and slow). From Midnight (Saddle Creek, 2019), produced by Will Toledo of Car Seat Headrest, who plays on this duet. Four stars in your 2019 review: the standout track. Midtempo.",
     "CLEAN", "CLEAN (Genius, 362 words). Your 2019 review flags FCC on tracks 4 and 7 only.", "JcEeRS8DDPA",
     "zookeeper album 1135774", source_url="https://en.wikipedia.org/wiki/Midnight_(Stef_Chura_album)"),
 new("Consolidated", "Friendly Fascism (Radio Edit)", "Friendly Fascism", "Nettwerk Records", "2866",
     "1991", "radio edit", "5:02",
     "Last six, placed in Set 7 after Bauhaus. San Francisco industrial hip-hop; the album was recorded at Razor's Edge in S.F. and released on Nettwerk in 1991. YTM lists a Radio Edit at 5:02, the same length as the album cut: confirm the edit by ear.",
     "CLEAN", "CLEAN (Genius, 447 words). YTM lists the Radio Edit.", "rbI494XYNi4",
     "zookeeper album 2866", source_url="https://en.wikipedia.org/wiki/Friendly_Fa$cism"),
 new("Dumb", "Pull Me Up", "Pray 4 Tomorrow", "Mint Records Inc.", "1148228",
     "2022-11-11 (album; single Aug. 23, 2022)", "album track", "2:57",
     "Last six, placed in Set 9 (short, upbeat) before Star Moles. Vancouver post-punk. Four stars in your review: a bouncing rocker with a great hook.",
     "CLEAN", "CLEAN (Genius, 200 words). Your review flags FCC on tracks 8 and 9 only.", "5nt_9kEaokY",
     "zookeeper album 1148228", source_url="https://dumbband.bandcamp.com/track/pull-me-up"),
]
allt = dict(old); allt.update({t["videoId"]: t for t in NEW})

ORDER = {
 S1: ["w7PnWZXJwoc","vHOfGp9F1Pw","J2IJ6ugcmUI","UmRuVav12FA","WUmzu_RDflM","W51Ik_1noH8","FEeoIbUM60s","QXOOzvDc3Nk","HzkJsKXCjvg"],
 S2: ["NhfruZ2cHZo","fvFLtKkzL-g","b-NO3Y2kKm0","G8sGmSEehi4","bCt7lZos7pM","eF4RiUfPRNs","HOWV7yxxp8g","aDKGnFeLnF4"],
 S3: ["wOkBZA51Z9o"],
 S4: ["vEL9U3Z1cvo","lpl4quk0T_g","cD_Av64P_qU","5X718hNafSM","2fTel1iqDiQ","gKkWSYQaxVo"],
 TS: ["ug3RfquyZl0","7Sm385a-tqc","gXKDtkCzSCw","F5fHfGZENbQ"],
 S6: ["RoeVGBKwnkU","rg1uP4mxXzE","omuKcuxMQq4","DL9Ac9pcKqI","4Yf-8hL7lzk","wDUYCyajDcs"],
 S7: ["fOoCnK5Jza4","wdyhe8VT6Yg","qSk88IeNUr0","rbI494XYNi4","K5l80OdiCzM"],
 S8: ["nybyN7_98zw","PVcU0z1zPqk","BSraSIhC_8A","DD-5_lCEMHY","JcEeRS8DDPA"],
 S9: ["7XhgcajHhcM","OpeaILsddHc","adRswyRcJmM","rmd21czLZFw","5nt_9kEaokY","C4KZlei2zk8","pcFnJEXsvWc","72heAMH_l5s","VFIcDRKCxoU","qjf8SsATw84","TVTmQTcV-iE"],
}
flat = [v for ids in ORDER.values() for v in ids]
live = json.loads(Path("/tmp/live_ids.json").read_text()) if Path("/tmp/live_ids.json").exists() else None
assert len(flat) == len(set(flat)) == 55, len(flat)
if live: assert set(flat) == set(live), set(flat) ^ set(live)
plan["sets"] = [{"set": nm, "tracks": [allt[i] for i in ids]} for nm, ids in ORDER.items()]

# Tweak a few existing notes
for t in plan["sets"][2]["tracks"]:
    t["why"] = "Requested by DJ Stace (Oct. 16). She cut the other three Dopamine Chamber tracks from the Air Order on Oct. 22; this one stays. Debuted live at Leeds Festival Aug. 29."

# Cuts
CUTS = [("Fontaines D.C.","Six Shot Morning","00krktruwsM"),("Fontaines D.C.","Mimesis","zXyN6eZjlTg"),
        ("Fontaines D.C. & ROSALIA","Where Is Gone?","3mb6YrCabso"),("Pulp","The Trees","dXyQj36I2Vc")]
for a, t, v in CUTS:
    plan["cut"].append({"artist": a, "track": t, "videoId": v, "cut_on": "2026-10-22", "source": "Stace edited Air Order (PLSosF7JAIkaM) Oct. 22: cut from Air Order"})
fb = json.loads(FB.read_text(encoding="utf-8"))
for a, t, v in CUTS:
    fb["removed"].append({"date": "2026-10-22", "source_playlist": "Air Order (PLSosF7JAIkaM)", "artist": a, "title": t, "videoId": v,
                          "note": "cut from Air Order Oct. 22", "cooloff_until": "2026-12-21"})
fb.setdefault("added_by_stace", [])
for t in NEW:
    fb["added_by_stace"].append({"date": "2026-10-22", "source_playlist": "Air Order (PLSosF7JAIkaM)", "artist": t["artist"], "title": t["track"], "videoId": t["videoId"]})
FB.write_text(json.dumps(fb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

# Talk breaks
mb = plan["mic_breaks"]
mb["opening"][1] = ("Fontaines D.C. released Dopamine Chamber last Friday, Oct. 16, on XL. Produced by James Ford, 11 tracks. Set 3 plays one of them, Happy For You.")
mb["after_texas_set"] = [
 "Dallas first: Nervebreakers, My Girlfriend Is a Rock, from the 1978 Politics EP on Wild Child Records. Loco Gringos, also Dallas, released their only album after singer Tom Foote died in 1990.",
 "Scratch Acid formed in Austin. Greatest Gift is from their 1984 self-titled EP, collected on The Greatest Gift (Touch and Go, 1991). David Yow sang for them, then fronted The Jesus Lizard. Monkey Trick is from Goat (Touch and Go, 1991).",
 "Butthole Surfers came out of San Antonio. Pepper is from Electriclarryland (1996). Big Boys were an Austin band; Fun Fun Fun is a 1982 EP.",
]
mb["after_fontaines"] = [
 "Dopamine Chamber is the band's fifth album and the second with James Ford. Happy For You debuted live at Leeds Festival on Aug. 29.",
 "Two songs from it, Tongue (shit x10) and Japan (fuck x3, shit x3), stay off the air. Their Europe and UK tour started in Lisbon on Oct. 21 (verify).",
]
mb["end_hour_1"] = [
 "Reviewed this month and in rotation: Twisted Teens (two albums), Lex Walton, Yard Act, Little Barrie, Palace, Sluice, This Is Lorelei, Dread Spectre Council, Tricky, Ty Segall.",
 "This Is Lorelei twice: the album track, then MJ Lenderman's version of Dancing in the Club (2025, Double Double Whammy). Radio edit: confirm by ear.",
 "Station ID at the top of the hour.",
]
mb["after_machines"] = [
 "Numbers is from Kraftwerk's Computer World (1981). Nag, Nag, Nag is Cabaret Voltaire's 1979 Rough Trade single. Bauhaus released The Passion of Lovers in June 1981 on Beggars Banquet; it is on Mask.",
 "Consolidated are from San Francisco: Friendly Fascism is the title track of their 1991 Nettwerk album, recorded at Razor's Edge in the city. Fujiya & Miyagi's New Shiny Object is out Oct. 30.",
]
mb["anniversary"] = [
 "Pulp released We Love Life on Oct. 22, 2001, produced by Scott Walker (25 years today; no Pulp track tonight, since The Trees came off the Air Order).",
 "The Avalanches' No Bad Memories came out Oct. 16 with Karen O on Blue Shadows. Stef Chura's Sweet Sweet Midnight is from Midnight (Saddle Creek, 2019); Will Toledo of Car Seat Headrest produced the album and plays on it.",
]
mb["after_heavy_set"] = [
 "Dumb, from Vancouver: Pull Me Up is from Pray 4 Tomorrow (Mint, 2022).",
 "Last stretch is new and loud: Queens of the Stone Age, Insignificant Other, from Perfecth (Matador, out Oct. 30).",
 "Jozef Van Wissem and Jim Jarmusch, Bocca di Lupo and Mouth of the Wolf, Sacred Bones, Nov. 6. Courtney Barnett sings on Never Like You Said.",
 "Eagles of Death Metal cover Careless Whisper on Boots Electric Performing the Best Songs We Never Wrote (2019). Lambrini Girls, Cult of Celebrity, City Slang.",
]
mb["opening"] = mb["opening"][:2] + ["New and loud: Westside Cowboy of Manchester (Island, debut It Goes On out Aug. 21) and Royal Blood, Ten Over Ten, the lead single from Dead Company (Warner, due Nov. 13)."] + mb["opening"][2:]

plan["review_rotation"]["this_show"] = ("Week 2 for all 13 albums. Fontaines cuts do not affect the rotation. Lorelei has two tracks tonight (album track plus the Lenderman radio edit, which is from a different release). Westside Cowboy review is a draft, not posted.")
plan["final"] = {
 "built": "2026-10-21",
 "updated": "2026-10-22",
 "cull_ticks": [], "replace_ticks": [],
 "air_order_edits_oct22": {
   "cut": [f"{a}, {t}" for a, t, _ in CUTS],
   "added_inline": ["Nervebreakers My Girlfriend is a Rock (Radio Edit)", "Loco Gringos Ain't No Corndogs", "This Is Lorelei & MJ Lenderman Dancing in the Club (Radio Edit)"],
   "last_six_placed": {"Set 1": ["Westside Cowboy", "Royal Blood"], "Set 7": ["Bauhaus", "Consolidated"], "Set 8": ["Stef Chura"], "Set 9": ["Dumb"]},
   "reordered": "Set 1 order follows her Air Order (Lex Walton first, Dummy after Yard Act)."},
 "air_order_note": "YTM Air Order still lists the six tracks at the end (positions 50 to 55). The plan places them in sets; Air Order was not changed.",
 "open_flags": [
   "Triple Shot has four Damned tracks (Nasty added Oct. 20). Confirm or cut one.",
   "Loco Gringos: no lyrics found. Listen first.",
   "Lorelei and Lenderman, Nervebreakers and Consolidated are radio edits on YTM. Original Lorelei lyrics have fuck x2 (Verse 4). Confirm the edits by ear.",
   "No ticket giveaway placed: no sheet row lists Stace on or after Oct. 22.",
 ]}
PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("sets:", {s["set"][:22]: len(s["tracks"]) for s in plan["sets"]}, "total", sum(len(s["tracks"]) for s in plan["sets"]))
