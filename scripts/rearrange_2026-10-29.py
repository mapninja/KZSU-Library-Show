#!/usr/bin/env python3
"""
rearrange_2026-10-29.py
One-off Thursday-morning rebuild for the Oct. 29, 2026 (Halloween) show. Copy it as an
example for later weeks. Do not rerun it on a new week's plan.

What it does, in plain steps:
  1. Reads the plan (data/recon/2026-10-29/working_playlist.json).
  2. Reads DJ Stace's current Air Order (videoIds read from YouTube Music on Oct. 29, 40 tracks).
     Tracks she cut go to plan["cut"]. Her new add (Sisters of Mercy) is enriched and added.
  3. Adds 8 Halloween-themed tracks from her Zookeeper reviews (black, cats, devils, ghosts).
     Label and tag come from the Zookeeper album record. FCC status comes from her review.
  4. Rebuilds plan["sets"] into eight Halloween-themed sets (4 in Hour 1, 4 in Hour 2).
  5. Rewrites the mic breaks so they match the new sets.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "data/recon/2026-10-29/working_playlist.json"
plan = json.loads(PLAN.read_text())

# ---- 1. Her Air Order as read from YouTube Music on Oct. 29 (video IDs, her order) --------
AIR = """D2MH5c2sTvc jfJkvnXx8vw JD-qp1HMMIc HGBsxpnRhMk zGNLqyVXRpI 2cDvymU9D-M ErhXr2_QoPk hfY_ED9xAnw
DG4Z4W1vG38 KZkx50Y-Cyg gvLJZKdrDZ4 BB74rsWzJjw FWP2bTeoPTo N5_MhlEVILU SWGkfg396yo Ay3Izb6sGAo
n_bXdEA6nSM CXHz_6qmHFg mKWHa65cmns fiQk5hy54oE UgWgDWgNBzQ 9jA_Bg_r_cw ZYydAkq6nTc uUOMQzQdU34
TnHVCh6sBKA lBVFdSFV2lQ MOefQyJumI8 D4S-TxPpaI8 Lmyd9LTkpfk 6C4YDg14Wxo Yy9h2q_dr9k 4DUkHIl7D1E
NyaOYfpq9Fc rmC81sW2OPg Q0lzvB3Hnb8 uWepTCBBnLo ZNSgn4i3WnM yJ6LaqDDEHU -VdWLfjBknk dWkSkvMi_28""".split()

pool = {t["videoId"]: t for s in plan["sets"] for t in s["tracks"] if t.get("videoId")}
plan["cut"] = [
    {"artist": t["artist"], "track": t["track"], "videoId": v, "cut_by": "DJ Stace (Air Order, read Oct. 29)",
     "from_set": next(s["set"] for s in plan["sets"] if t in s["tracks"])}
    for v, t in pool.items() if v not in AIR]

# ---- 2. Her new add: Sisters of Mercy, This Corrosion --------------------------------------
pool["dWkSkvMi_28"] = {
    "artist": "The Sisters Of Mercy", "track": "This Corrosion", "album": "Floodland", "label": "Elektra Records (Local)",
    "label_source": "zookeeper label table (US label for Floodland); library holds only the compilation A Slight Case of Overbombing",
    "tag": "", "zk_alt": "127022", "released": "1987",
    "why": "Added to the Air Order by DJ Stace (Oct. 28 to 29). Goth landmark, produced by Jim Steinman. Long (9:31). Library copy is the Overbombing compilation (tag 127022).",
    "fcc_status": "CLEAN", "fcc_note": "CLEAN (LRCLIB, 662 words)", "priority": "O", "source": "added_by_stace",
    "added_by": "DJ Stace", "videoId": "dWkSkvMi_28", "duration": "9:31"}

# ---- 3. Eight Halloween-themed tracks from her Zookeeper reviews ---------------------------
def rev(artist, track, album, label, tag, year, stars, why, vid, dur, review_date, fcc):
    return {"artist": artist, "track": track, "album": album, "label": label, "label_source": "zookeeper album",
            "tag": str(tag), "released": year, "why": why, "fcc_status": "CLEAN", "fcc_note": fcc,
            "priority": "O", "source": "your_review_halloween", "added_by": "Claude (from DJ Stace's reviews, Oct. 29)",
            "final_change": "NEW from your reviews", "videoId": vid, "duration": dur, "review": f"{stars} reviewed {review_date}"}
NOFLAG = "No FCC flag in your review."
for t in [
    rev("Adia Victoria", "Devil Is A Lie", "Silences", "Canvasback/atl", 1139475, "2019", "5 stars",
        "Your review: 5 stars; midtempo, talk-sung vocals over hi-hat and drum roll, fuzzed and wah'd guitars, bass fade out.",
        "QHIvgPfLg7k", "4:28", "Oct. 12, 2019", "CLEAN (LRCLIB, 337 words). Your review flags tracks 2 and 8, not this one."),
    rev("Angélica Garcia", "Lucifer Waiting", "Cha Cha Palace", "Spacebomb", 1143829, "2020", "4 stars",
        "Your review: 4 stars; starts a bit like Blondie, morphs into Latin rhythm, wailing psych guitar. Album out Feb. 28, 2020.",
        "0c-yZuS4l34", "4:31", "Apr. 5, 2020", NOFLAG + " (Your review flags track 2 only; no lyrics posted.)"),
    rev("L’epée", "Ghost Rider", "Diabolique", "A Recordings", 1139464, "2019", "4 stars",
        "Your review: 4 stars; krautrock-style opening rhythm, spaghetti western psych guitar. L'Epee is Anton Newcombe and Lionel Liminana; Emmanuelle Seigner sings in English.",
        "UynYaH54GkA", "5:50", "Oct. 12, 2019", "CLEAN (LRCLIB, 133 words). Your review lists no FCC words."),
    rev("The Mars Volta", "Graveyard Love", "The Mars Volta", "Clouds Hill", 1148251, "2022-09-16", "4 stars",
        "Your review: 4 stars; uptempo, drum-driven, soaring vocals, abrupt ending.",
        "EnFwHLkGWyI", "3:15", "Jan. 8, 2023", NOFLAG + " (Your review flags track 13 only.)"),
    rev("Black Pumas", "Black Moon Rising", "Black Pumas", "Ato Records", 1139352, "2019", "4 stars",
        "Your review: 4 stars; opens with a drum roll, midtempo head-nodder, falsetto riffs.",
        "6-oBy2GGL6k", "3:42", "Oct. 8, 2019", "CLEAN (LRCLIB, 241 words). Your review lists no FCC words."),
    rev("A Giant Dog", "Black Mirror", "Neon Bible", "Merge Records", 1139486, "2019", "4 stars",
        "Your review: 4 stars; cover of the Arcade Fire opener, 'more urgent and serrated than the original.'",
        "QjnBCWMZLo4", "3:07", "Oct. 12, 2019", NOFLAG + " (Your review lists none; no lyrics posted.)"),
    rev("So Pitted", "cat scratch", "Neo", "Sub Pop Records", 1091090, "2016", "unrated",
        "Your review: fast, driving, overwhelming noise punk. The cat track. Album is Neo on Sub Pop.",
        "NFs07lWw4l4", "2:40", "Apr. 4, 2016", NOFLAG + " (Your review flags track 4 only; no lyrics posted.)"),
    rev("Stef Chura", "Eyes Without a Face", "Midnight", "Saddle Creek", 1135774, "2019", "4 stars",
        "Your review: 4 stars; Billy Idol cover, quiet and breathy, then a plodding rocker. Idol's song is named for the 1960 French horror film.",
        "12UXdKkfNd4", "3:53", "July 5, 2019", "CLEAN (LRCLIB, 237 words). Your review flags tracks 4 and 7, not this one."),
]:
    pool[t["videoId"]] = t

# Fix two display details on tracks she already had
pool["Lmyd9LTkpfk"]["why"] = pool["Lmyd9LTkpfk"]["why"].replace("DJ Stace added it to Next Show Oct. 20 to 22. ", "")
pool["6C4YDg14Wxo"]["why"] = "Second version of The Witch (YTM plays the Maintaining My Cool recording). Both versions are in your Air Order; cut one on air if you want only one."

# ---- 4. Eight Halloween sets ----------------------------------------------------------------
LAYOUT = [
 ("Hour 1, Set 1: Halloween anthems and horror-punk",
  "D2MH5c2sTvc jfJkvnXx8vw 2cDvymU9D-M zGNLqyVXRpI ErhXr2_QoPk hfY_ED9xAnw"),
 ("Hour 1, Set 2: Spells, wolves and haunted covers",
  "JD-qp1HMMIc ZNSgn4i3WnM HGBsxpnRhMk 6C4YDg14Wxo Lmyd9LTkpfk 12UXdKkfNd4 QjnBCWMZLo4"),
 ("Hour 1, Set 3: Black, cats and fuzz",
  "DG4Z4W1vG38 NFs07lWw4l4 D4S-TxPpaI8 BB74rsWzJjw SWGkfg396yo FWP2bTeoPTo KZkx50Y-Cyg gvLJZKdrDZ4 Ay3Izb6sGAo N5_MhlEVILU"),
 ("Hour 1, Set 4: The devil's set",
  "QHIvgPfLg7k 0c-yZuS4l34 -VdWLfjBknk rmC81sW2OPg lBVFdSFV2lQ uWepTCBBnLo"),
 ("Hour 2, Thursday Triple Shot: Queens of the Stone Age",
  "9jA_Bg_r_cw ZYydAkq6nTc"),
 ("Hour 2, Set 6: Ghosts, graveyards and black moons",
  "UynYaH54GkA EnFwHLkGWyI 6-oBy2GGL6k"),
 ("Hour 2, Set 7: Goth and post-punk",
  "n_bXdEA6nSM CXHz_6qmHFg mKWHa65cmns fiQk5hy54oE UgWgDWgNBzQ uUOMQzQdU34 TnHVCh6sBKA NyaOYfpq9Fc"),
 ("Hour 2, Set 8: Industrial, the long dark and the closer",
  "Q0lzvB3Hnb8 4DUkHIl7D1E yJ6LaqDDEHU dWkSkvMi_28 Yy9h2q_dr9k MOefQyJumI8"),
]
new_sets, used = [], set()
for name, ids in LAYOUT:
    tracks = []
    for v in ids.split():
        t = pool[v]; used.add(v); tracks.append(t)
    new_sets.append({"set": name, "tracks": tracks})
leftover = [v for v in AIR if v not in used]
assert not leftover, leftover
# Triple Shot now has two tracks because she cut No One Knows
plan["triple_shot"]["tracks"] = [t for t in plan["triple_shot"]["tracks"] if t["track"] != "No One Knows"]
plan["triple_shot"]["angle"] = ("New single Where the Goth Girls At? from Perfecth (out Fri. Oct. 30, Matador; nine tracks, produced by Josh Homme and Michael Shuman) "
    "and the Halloween-titled Burn the Witch. You cut No One Knows, so this is a two-song run; the third slot is open (No One Knows or Phantom Limb from Perfecth). Easy Street stays out (cool-off to Dec. 8).")
plan["sets"] = new_sets
for s in new_sets:
    for t in s["tracks"]:
        t.pop("final_change", None) if t["source"] != "your_review_halloween" else None
        if t.get("artist") == "Coil": t["final_change"] = "ADDED Oct. 28"
        if t.get("artist") == "The Sisters Of Mercy": t["final_change"] = "ADDED Oct. 29"

# ---- 5. Mic breaks for the new sets -------------------------------------------------------
plan["mic_breaks"] = {
 "opening": [
  "Halloween show. Punk and post-punk focus, week 3 of 4: goth and post-punk tonight. D.C. hardcore Nov. 5.",
  "Tonight: Ministry, Misfits, The Cramps, a run of spells and covers, a devil's set to close Hour 1, then a Queens of the Stone Age run to open Hour 2.",
  "New this week from the library reviews: Adia Victoria, L'Epee, Angelica Garcia, The Mars Volta, Black Pumas, A Giant Dog, So Pitted and Stef Chura."],
 "after_set_1": [
  "Misfits released Halloween as a single in 1981. The Cramps' Goo Goo Muck is from Psychedelic Jungle (1981). Roky Erickson's I Walked with a Zombie is from 1981.",
  "The Lemonheads released a 12-inch of Roky, with The Bevis Frond, on Oct. 16 on Fire Records.",
  "Ministry's final album, Hate to Go (Take Out or Delivery), is out Fri. Oct. 30 on Cleopatra. Closing track features former bassist Paul Barker. Farewell tour starts April 2, 2027 in Utrecht."],
 "after_set_2": [
  "Screamin' Jay Hawkins recorded I Put a Spell on You in 1956. The Kills' version was recorded in 2009 and came out in 2020 on Domino.",
  "Wolf Like Me is a TV on the Radio song; Lera Lynn and Shovels & Rope cover it. Eyes Without a Face is a Billy Idol song, named for a 1960 French horror film; Stef Chura covers it on Midnight (Saddle Creek). Black Mirror is an Arcade Fire song, covered by A Giant Dog."],
 "after_set_3": [
  "Black Paint is from Ty Segall's Chrome (Drag City). So Pitted's cat scratch is from Neo on Sub Pop (2016).",
  "Fake Names released Punk Ruins Oct. 23 on Epitaph. Recorded in five days at Electrical Audio in Chicago.",
  "Twisted Teens: The Holy Cross Tigers is out Nov. 6 on Sub Pop."],
 "end_hour_1": [
  "Adia Victoria, Angelica Garcia, Andy Shauf, Nick Cave and the Stones, all talking to the devil.",
  "Station ID at the top of the hour. Next: the Thursday Triple Shot, Queens of the Stone Age."],
 "triple_shot_intro": [
  "Thursday Triple Shot: Queens of the Stone Age. Perfecth, the band's ninth album, is out Fri. Oct. 30 on Matador. Josh Homme and Michael Shuman produced it.",
  "Where the Goth Girls At? is the new single. Burn the Witch is from Lullabies to Paralyze (2005)."],
 "after_triple_shot": [
  "On Oct. 30, 1938, CBS aired Orson Welles' War of the Worlds on The Mercury Theatre on the Air. The FCC investigated afterward and found no law was broken."],
 "bay_area_break": [
  "Tonight: Bottom of the Hill tribute night, a Halloween covers show at Kilowatt, Katie Pruitt at Chapel.",
  "Fri. Oct. 30: Cold Cave, SRSQ and Houses of Heaven at Great American Music Hall. Sat. Oct. 31: Halloween tribute bands at Thee Stork Club and Rocky Horror with a live cast at the UC Theater in Berkeley. Sun. Nov. 1: Frankie And The Witch Fingers at Great American Music Hall."],
 "after_goth": [
  "Roger O'Donnell of The Cure was born Oct. 29, 1955. Public Image Ltd. released Death Disco in July 1979; YouTube Music lists the studio cut as Swan Lake.",
  "Queens of the Stone Age, Ministry and Mitski's Puberty 2 anniversary edition are all out Fri. Oct. 30."],
 "closing": [
  "Black Sabbath: the four original members reunited on Letterman Oct. 30, 1998 to play Paranoid.",
  "Next week, Nov. 5: US hardcore and Washington D.C. Fugazi, Husker Du, Bad Brains, short songs."],
}
plan["final"] = {
  "built": "2026-10-29",
  "cull_ticks": [], "replace_ticks": [],
  "notes": ("Thu. Oct. 29 rebuild at Stace's request. Air Order read back: 40 tracks (was 52). She cut 13: The Fall Retro Song, QOTSA No One Knows, Bambara, "
            "the eight reviewed-rotation tracks (Billy Came Back, Overhead, Dream On, Ultimate Love 4Ever, Flood Season, Hand Me A Cigarette, I Still See Me There, "
            "You're Gonna Need A Little Music), Mitski and Monster Mash. She added The Sisters Of Mercy, This Corrosion, and reordered the bottom of the list. "
            "Plan rebuilt into eight Halloween sets and eight Halloween-themed tracks from her reviews added at the bottom of the Air Order."),
}
plan["note"] = plan["note"] + " Oct. 29: rebuilt into eight Halloween sets after Stace's Air Order cuts; eight reviewed Halloween tracks added."
PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n")
n = [t for s in new_sets for t in s["tracks"]]
print("sets:", len(new_sets), "tracks:", len(n), "cut:", len(plan["cut"]))
