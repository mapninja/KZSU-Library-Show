#!/usr/bin/env python3
"""
triple_shot_options_2026-10-29.py
One-off update for the Oct. 29, 2026 (Halloween) show. Copy it as an example for later weeks.
Do not rerun it on the same plan (it would add the tracks twice; it checks and skips if present).

What it does, in plain steps:
  1. Adds three Queens of the Stone Age Triple Shot options that DJ Stace asked for
     (Monsters in the Parasol, If I Had a Tail, Hangin' Tree) to the Triple Shot set.
  2. Adds four tracks she put in the Air Order on Oct. 29 after the last rebuild
     (Hex's Up, God Will Control the Werewolves, Fear not the Fear, Cult of Celebrity) to sets that fit.
  3. Updates the Triple Shot text and two mic breaks.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "data/recon/2026-10-29/working_playlist.json"
plan = json.loads(PLAN.read_text())
sets = {s["set"]: s for s in plan["sets"]}
have = {t["videoId"] for s in plan["sets"] for t in s["tracks"]}

def track(artist, track_, album, label, tag, released, fcc_status, fcc_note, vid, dur, why, source, change, label_source):
    return {"artist": artist, "track": track_, "album": album, "label": label, "label_source": label_source, "tag": tag,
            "released": released, "why": why, "fcc_status": fcc_status, "fcc_note": fcc_note, "priority": "O",
            "source": source, "added_by": "DJ Stace" if source == "added_by_stace" else "Claude (DJ Stace request, Oct. 29)",
            "final_change": change, "videoId": vid, "duration": dur}

QOTSA = "Queens of the Stone Age"
options = [
    track(QOTSA, "Monsters in the Parasol", "R", "Interscope Records", "555656", "2000", "CLEAN", "CLEAN (LRCLIB, 191 words)",
          "LRRPeOBygG8", "3:28", "Triple Shot option A (pick one for the third song). From Rated R (2000); the library lists the album as R. The monsters track.",
          "triple_shot_option", "TRIPLE SHOT OPTION A", "zookeeper album"),
    track(QOTSA, "If I Had a Tail", "...Like Clockwork", "Matador Records", "1038181", "2013", "CLEAN", "CLEAN (LRCLIB, 201 words)",
          "Ymnwa6RX5F4", "4:56", "Triple Shot option B (pick one for the third song). From ...Like Clockwork (2013, Matador).",
          "triple_shot_option", "TRIPLE SHOT OPTION B", "zookeeper album"),
    track(QOTSA, "Hangin' Tree", "Songs for the Deaf", "Interscope Records", "670294", "2002", "CLEAN", "CLEAN (LRCLIB, 123 words)",
          "473wEdL_GzU", "3:07", "Triple Shot option C (pick one for the third song). From Songs for the Deaf (2002), the same album as No One Knows. YTM lists it as Hanging Tree.",
          "triple_shot_option", "TRIPLE SHOT OPTION C", "zookeeper album"),
]
ts = next(s for k, s in sets.items() if "Triple Shot" in k)
for t in options:
    if t["videoId"] not in have:
        ts["tracks"].append(t); have.add(t["videoId"])

# ---- her four new Air Order adds -----------------------------------------------------------
hex_ = track("Dread Spectre Council", "Hex's Up", "Thetans", "Handmade Records", "1156474", "2026-03-29", "CLEAN",
             "DJ Stace review (Zookeeper, reviewed Oct. 8, 2026): no FCC flag on this track.", "500HxYQej8I", "3:50",
             "Added to the Air Order by DJ Stace (Oct. 29). Your review: 5 stars, 'play this one,' heir to Swervedriver. Aired earlier in October. Same album as Raven.",
             "added_by_stace", "ADDED Oct. 29", "zookeeper album")
lips = track("The Flaming Lips", "God Will Control The Werewolves", "The Teardrop Throbs", "Third Man Records", "", "2026-10-26 (verify)", "CLEAN",
             "CLEAN (Genius, 155 words)", "AIEU9qKbwQA", "4:22",
             "Added to the Air Order by DJ Stace (Oct. 29). Werewolf title. Album announced Oct. 26, due in January on Third Man (verify), the first without Steven Drozd. Not in the library yet.",
             "added_by_stace", "ADDED Oct. 29", "zookeeper label table (Third Man Records); album not in library")
bodega = track("BODEGA", "Fear not the Fear", "All Inside Aquarium", "Chrysalis Records (not in ZK)", "", "2026-10-09", "UNVERIFIED",
               "UNVERIFIED: no lyrics posted. The review template flags FCC words only on the title track (fuck x2). Listen first.", "u-OCkJD78Ec", "4:48",
               "Added to the Air Order by DJ Stace (Oct. 29). Reverbed, shimmering guitars that grow more psychedelic (Glide, SPIN, per the review template). Album out Oct. 9. Not in the library yet.",
               "added_by_stace", "ADDED Oct. 29", "review shelf (Chrysalis Records); not in Zookeeper label table")
lambrini = track("Lambrini Girls", "Cult of Celebrity", "Cult of Celebrity (single)", "City Slang", "", "2026-03-31", "CLEAN",
                 "CLEAN (LRCLIB, 224 words)", "qjf8SsATw84", "2:14",
                 "Added to the Air Order by DJ Stace (Oct. 29). UK punk single, first new music since the 2025 album Who Let The Dogs Out. Not in the library yet. Date and label: Bandcamp, Apple Music, Qobuz.",
                 "added_by_stace", "ADDED Oct. 29", "zookeeper label table (City Slang); single not in library")

def insert_after(set_key, after_artist, after_track_prefix, new):
    s = next(v for k, v in sets.items() if set_key in k)
    if new["videoId"] in have: return
    i = next(i for i, t in enumerate(s["tracks"]) if t["artist"] == after_artist and t["track"].startswith(after_track_prefix))
    s["tracks"].insert(i + 1, new); have.add(new["videoId"])
insert_after("Set 2", "Lera Lynn & Shovels & Rope", "Wolf", lips)
insert_after("Set 3", "Dread Spectre Council", "Raven", hex_)
insert_after("Set 3", "Fake Names", "Punk", lambrini)
insert_after("Set 7", "The Horrors", "Who", bodega)

# ---- Triple Shot text and mic breaks --------------------------------------------------------
plan["triple_shot"]["tracks"] = [{"artist": t["artist"], "track": t["track"], "videoId": t["videoId"]} for t in ts["tracks"]]
plan["triple_shot"]["angle"] = ("Where the Goth Girls At? (new single from Perfecth, out Fri. Oct. 30, Matador; nine tracks, produced by Josh Homme and Michael Shuman) and Burn the Witch are set. "
    "Pick ONE of three options for the third song: A Monsters in the Parasol (Rated R, 2000), B If I Had a Tail (...Like Clockwork, 2013), C Hangin' Tree (Songs for the Deaf, 2002). "
    "All are in your Air Order. Easy Street stays out (cool-off to Dec. 8).")
mb = plan["mic_breaks"]
mb["triple_shot_intro"] = [
    "Thursday Triple Shot: Queens of the Stone Age. Perfecth, the band's ninth album, is out Fri. Oct. 30 on Matador. Josh Homme and Michael Shuman produced it.",
    "Where the Goth Girls At? is the new single. Burn the Witch is from Lullabies to Paralyze (2005). Third song: Monsters in the Parasol (Rated R, 2000), If I Had a Tail (...Like Clockwork, 2013) or Hangin' Tree (Songs for the Deaf, 2002)."]
mb["after_set_2"] = mb["after_set_2"] + [
    "The Flaming Lips announced The Teardrop Throbs Oct. 26, due in January on Third Man (verify). It is the first Lips album without Steven Drozd. God Will Control the Werewolves is the first track out."]
mb["after_set_3"] = mb["after_set_3"] + [
    "Lambrini Girls released Cult of Celebrity Mar. 31 on City Slang, their first new music since the 2025 album Who Let The Dogs Out."]
plan["final"]["notes"] += (" | Oct. 29 later: she asked for Queens options. Added Monsters in the Parasol, If I Had a Tail and Hangin' Tree to the Air Order and the Triple Shot set (pick one). "
                           "She also added Hex's Up, God Will Control the Werewolves, Fear not the Fear and Cult of Celebrity to the Air Order; placed in Sets 2, 3 and 7. Air Order now 55 tracks.")
plan["ytm_air_order"]["tracks"] = 55
plan["ytm_air_order"]["verified"] += " | Oct. 29 later: appended 3 Queens options; she added 4 more; 55 tracks verified by reload."
PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n")
print("tracks:", sum(len(s["tracks"]) for s in plan["sets"]))
