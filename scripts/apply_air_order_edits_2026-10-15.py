#!/usr/bin/env python3
"""
apply_air_order_edits_2026-10-15.py
===================================

Applies DJ Stace's Oct. 15, 2026 morning Air Order edits to the show plan.

What changed in the YouTube Music "Air Order" playlist since the Oct. 14 final build
-----------------------------------------------------------------------------------
- Swapped: IDLES "Colossus" -> "The Beachland Ballroom"
- Swapped: Bad Brains "Banned in D.C." -> "I Against I"
- Swapped: Fontaines D.C. "Big" and "Jackie Down the Line" -> "The Cuckoo Is A-Callin'" and
  "Chequeless Reckless (Darklands Version)" (Triple Shot, "Marianne" stays)
- Cut: Blondshell "Heart Has To Work So Hard", Brigitte Calls Me Baby "Altitude",
  Michael Kiwanuka "Summer Clothes", Beth Orton "Waiting"
- Moved: Stef Chura "The Concrete" now follows Heavens to Betsy in the Bay Area set
- Added at the end (from her listening this week): Twisted Teens, Sampa the Great, MJ Lenderman,
  Sluice, Firewater, BODEGA, SAULT, Cameron Winter, Fujiya & Miyagi

Her later request: pair Fujiya & Miyagi with Cabaret Voltaire and Kraftwerk tonight.

Her nine tail tracks and the two pairing tracks are placed in sets here. Her order for the
first 40 Air Order tracks is kept exactly. Only the new tracks are slotted in.

What this script writes
-----------------------
- data/recon/2026-10-15/working_playlist.json   (the plan, rewritten in place)
- data/daily/feedback.json                      (her removals, adds and moves, logged once)
- scratch/docx_build/plan_for_docx.json, mic_breaks.json, bench.json  (inputs for the Word build)

It never talks to YouTube Music or Zookeeper. Run it from the repo root:
    python3 scripts/apply_air_order_edits_2026-10-15.py
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # repo root
PLAN_PATH = ROOT / "data/recon/2026-10-15/working_playlist.json"
FEEDBACK_PATH = ROOT / "data/daily/feedback.json"
BUILD_DIR = ROOT / "scratch/docx_build"                # inputs for the Word script builder

TODAY = "2026-10-15"
COOLOFF = "2026-12-14"                                 # 60 days after today


def new_track(**kw):
    """Build one plan track with sensible defaults. Fields match references/data_format.md."""
    t = {"artist": "", "track": "", "album": "", "label": "", "label_source": "", "tag": "",
         "released": "", "type": "album track", "upcoming": "", "duration": "", "priority": "R",
         "why": "", "fcc_status": "CLEAN", "fcc_note": "", "source": "added_by_stace",
         "added_by": "DJ Stace", "videoId": ""}
    t.update(kw)
    return t


# ---------------------------------------------------------------------------
# New tracks. Durations come from YouTube Music. FCC counts come from LRCLIB or Genius
# (words counted in the browser, lyrics never stored). Labels: see label_source.
# ---------------------------------------------------------------------------
NEW = {
    "VJ7esiIHMp8": new_track(
        artist="IDLES", track="The Beachland Ballroom", album="CRAWLER", label="Partisan Records",
        label_source="zookeeper label table (IDLES, Partisan)", released="2021", duration="4:01",
        why="Added by DJ Stace Oct. 15. Replaces Colossus as the opener.",
        fcc_note="CLEAN (LRCLIB, 167 words)."),
    "6bfORnkyuBw": new_track(
        artist="Bad Brains", track="I Against I", album="I Against I", label="SST Records (verify)",
        label_source="web (verify)", released="1986", duration="2:51",
        why="Added by DJ Stace Oct. 15. Replaces Banned in D.C. Bad Brains played CBGB's final week in 2006.",
        fcc_note="CLEAN (LRCLIB, 249 words)."),
    "FXty6vOg0a0": new_track(
        artist="Fontaines D.C.", track="The Cuckoo Is A-Callin'", album="Too Real",
        label="Partisan Records", label_source="web (Partisan store, KEXP; verify)", released="2018",
        type="b-side", duration="2:12",
        why="Triple Shot 1 of 3, chosen by DJ Stace. B-side of Too Real, the band's first 7-inch on Partisan (late 2018).",
        fcc_note="CLEAN (LRCLIB, 98 words).", source="triple shot"),
    "Y-dA3yt8m8s": new_track(
        artist="Fontaines D.C.", track="Chequeless Reckless (Darklands Version)",
        album="Chequeless Reckless / Boys in the Better Land", label="", label_source="unverified",
        released="2018", type="single", duration="2:19",
        why="Triple Shot 2 of 3, chosen by DJ Stace. 2018 double A-side single.",
        fcc_note="CLEAN (LRCLIB, 205 words, a live version's lyrics): check by ear.", source="triple shot"),
    "mDYeisr6Gro": new_track(
        artist="Twisted Teens", track="Stalks", album="The Holy Cross Tigers", label="Sub Pop Records",
        label_source="past spins (Oct. 8, When We First Met)", released="2026-11-06 (album)", type="single",
        duration="2:48",
        why="Added by DJ Stace Oct. 15. Opens The Holy Cross Tigers (Sub Pop, Nov. 6), the band's third album of 2026.",
        fcc_note="CLEAN (Genius, Oct. 13)."),
    "u-OCkJD78Ec": new_track(
        artist="BODEGA", track="Fear not the Fear", album="All Inside Aquarium", label="Chrysalis Records",
        label_source="past spins (Oct. 8, Slow Train)", released="2026", type="single", duration="4:48",
        why="Added by DJ Stace Oct. 15. New BODEGA. The title track, All Inside Aquarium, has fuck x2 and stays out.",
        fcc_note="CLEAN (Genius, Oct. 15)."),
    "6AK9bbwsK7s": new_track(
        artist="Sampa the Great", track="Location", album="Nu Zamrock", label="Loma Vista Recordings",
        label_source="web (BroadwayWorld; verify)", released="2026-10-30 (album)", type="single",
        duration="2:35",
        why="Added by DJ Stace Oct. 15. Third single from Nu Zamrock (Oct. 30). Produced by Cadenza.",
        fcc_note="CLEAN (Genius, Oct. 15)."),
    "K5l80OdiCzM": new_track(
        artist="Fujiya & Miyagi", track="No Green Light", album="New Shiny Object (verify)",
        label="Impossible Objects of Desire (verify)", label_source="web (verify)",
        released="2026-10-30 (album)", type="single", duration="5:51",
        why="Added by DJ Stace Oct. 15. She hears Kraftwerk and Cabaret Voltaire in it, so it closes a machines set after both.",
        fcc_status="UNVERIFIED", fcc_note="UNVERIFIED: no lyrics posted on Genius or LRCLIB. Listen first."),
    "m1suappFvag": new_track(
        artist="MJ Lenderman", track="She's Leaving You", album="Manning Fireworks",
        label="Anti- Records (verify)", label_source="web (verify)", released="2024", duration="4:39",
        why="Added by DJ Stace Oct. 15. Also in her Next Show playlist.",
        fcc_note="CLEAN (LRCLIB, 181 words)."),
    "elKyn7L-Ddw": new_track(
        artist="Sluice", track="Beadie", album="Companion", label="Mtn Laurel Recording Co.",
        label_source="zookeeper album 1156485 (keyed Oct. 8)", tag="1156485", released="2026-03-27",
        duration="4:01",
        why="Added by DJ Stace Oct. 15. Opener of Companion. Her review: 5 stars, clean (FCCs are tracks 3, 4, 6 and 10).",
        fcc_note="CLEAN (her review, Oct. 4)."),
    "9_K08CnbR7E": new_track(
        artist="Firewater", track="Another Perfect Catastrophe", album="The Ponzi Scheme",
        label="Jetset Records (verify)", label_source="web (Rate Your Music; verify)", released="1998",
        duration="4:20",
        why="Added by DJ Stace Oct. 15. Tod Ashley's band after Cop Shoot Cop.",
        fcc_note="CLEAN (LRCLIB, 213 words)."),
    "GRC4Ac6IB1w": new_track(
        artist="SAULT", track="Wildfires", album="Untitled (Black Is)",
        label="Forever Living Originals (verify)", label_source="web (verify)", released="2020",
        duration="3:27",
        why="Added by DJ Stace Oct. 15.", fcc_note="CLEAN (LRCLIB, 109 words)."),
    "i4J2mM3DY1Q": new_track(
        artist="Cameron Winter", track="Love Takes Miles (Live at Carnegie Hall)",
        album="Live at Carnegie Hall", label="Partisan Records", label_source="release DB (Partisan)",
        released="2026-10-09", type="live", duration="4:14",
        why="Added by DJ Stace Oct. 15. Recorded at a December 2025 show.",
        fcc_note="CLEAN (LRCLIB studio-version lyrics, 214 words): live version, check by ear."),
    # Added at her request after the edits: Kraftwerk and Cabaret Voltaire to pair with Fujiya & Miyagi.
    "fOoCnK5Jza4": new_track(
        artist="Kraftwerk", track="Numbers (2009 Remaster)", album="Computer World (2009 Remaster)",
        label="", label_source="unverified", released="1981", duration="3:21", priority="R",
        why="Requested by DJ Stace Oct. 15: pair with Fujiya & Miyagi. Computer World, 1981.",
        fcc_note="CLEAN (LRCLIB, 138 words, counting).", source="request",
        added_by="DJ Stace (request)"),
    "wdyhe8VT6Yg": new_track(
        artist="Cabaret Voltaire", track="Nag, Nag, Nag", album="The Living Legends",
        label="Rough Trade Records (verify)", label_source="web (original 1979 single; verify)",
        released="1979", type="single", duration="4:40", priority="R",
        why="Requested by DJ Stace Oct. 15: pair with Fujiya & Miyagi. Sheffield, 1979.",
        fcc_note="CLEAN (LRCLIB, 108 words).", source="request", added_by="DJ Stace (request)"),
}

# Tracks she removed from the Air Order (their videoIds in the plan) and the reason to log.
REMOVED = {
    "hoDWTZYkTDY": "replaced by The Beachland Ballroom",
    "grixlGSNS6U": "replaced by I Against I",
    "iqtAP6szsPg": "cut from Air Order",
    "akcyM1qcfuM": "cut from Air Order",
    "Q19tYEHCfP0": "cut from Air Order",
    "7eM4MkqvDiY": "Triple Shot: replaced by The Cuckoo Is A-Callin'",
    "tWTU4y_t3a8": "Triple Shot: replaced by Chequeless Reckless (Darklands Version)",
    "4AEdJyRdtHI": "cut from Air Order",
}

# The final show order, by set. Her first 40 Air Order tracks keep her order exactly.
# Within these sets, her tail tracks and the two requested tracks are slotted in.
SETS = [
    ("Hour 1, Set 1: Loud and new",
     "VJ7esiIHMp8 qjf8SsATw84 gnSZhI4beE4 mDYeisr6Gro UoBEFx1r4tk W51Ik_1noH8"),
    ("Hour 1, Set 2: UK 1977, Belfast and the Warfield",
     "1qQ0MG9OPzA u6ZWV7cCK5A csGl5yVoHk8 PlGmYetiCjA 2sQaJNtbSzI 9mebsxe970U Kx3EqNYQklg"),
    ("Hour 1, Set 3: CBGB closed 20 years ago, plus Oct. 9 to 15 anniversaries",
     "skdE0KAFCEA 6bfORnkyuBw bXXQNtsBXYU tx6ZlKdKwK4 Xt5JDwDX3xA"),
    ("Hour 1, Set 4: New this month", "DL9Ac9pcKqI HDFgZYq0-zo u-OCkJD78Ec 6AK9bbwsK7s"),
    ("Hour 2, Thursday Triple Shot: Fontaines D.C.", "FXty6vOg0a0 Y-dA3yt8m8s ikKBcZg9jUc"),
    ("Hour 2, Set 5: Bay Area this week and next",
     "LwGiIir7q8M oQWmM_9F954 FEeoIbUM60s hBK-7j_K5i0 OUrRKjY2DkI PS4WMDhV2As"),
    ("Hour 2, Set 6: Songwriters and slow",
     "RfnnUQYE5Fw elKyn7L-Ddw m1suappFvag i4J2mM3DY1Q oRc4eohqlaM E_LiLwsfhV8 GRC4Ac6IB1w"),
    ("Hour 2, Set 7: Machines and motorik", "fOoCnK5Jza4 wdyhe8VT6Yg K5l80OdiCzM"),
    ("Hour 2, Set 8: Heavy, psych and short",
     "7XhgcajHhcM dXVE5NZl6G4 OpeaILsddHc adRswyRcJmM 9_K08CnbR7E rmd21czLZFw C4KZlei2zk8 pcFnJEXsvWc yQt5aOzytyA"),
    ("Closers and bench", "jef6-SwnwEY"),
]

TRIPLE_ANGLE = ("Dopamine Chamber (XL) comes out Fri. Oct. 16. Lead single Marianne plus two 2018 singles "
                "from before Dogrel, chosen by DJ Stace: The Cuckoo Is A-Callin' (B-side of Too Real) and "
                "Chequeless Reckless (Darklands version). The band opens a Europe and UK tour in Lisbon Oct. 21.")

MIC_BREAKS = {
    "opening": [
        "Punk and post-punk focus starts tonight: UK 1977 first, Texas punk next week, Halloween post-punk Oct. 29, D.C. hardcore Nov. 5.",
        "Sex Pistols signed to EMI Oct. 8, 1976 (50 years). The reunion lineup (Steve Jones, Paul Cook, Glen Matlock, Frank Carter) was booked at the Warfield last night, Oct. 14.",
    ],
    "after_uk_set": [
        "The Clash single Complete Control: fall 1977. Stiff Little Fingers released Alternative Ulster Oct. 17, 1978.",
        "The Damned New Rose turns 50 next Thursday, Oct. 22. Held for that show.",
    ],
    "after_cbgb_set": [
        "CBGB closed Oct. 15, 2006. Patti Smith played the last night, a three-hour set that ran past 1 a.m.",
        "Bad Brains played the club's final week (I Against I is from 1986). Death Cab's The Photo Album turns 25 (Oct. 9, 2001). JSBX Now I Got Worry turns 30 today (Oct. 15, 1996, Matador).",
    ],
    "end_hour_1": [
        "New this month: Julia Jacklin (The Gem, Sept. 25), BODEGA (All Inside Aquarium, Chrysalis), Sampa the Great (Location, third single from Nu Zamrock, Oct. 30, Loma Vista). Twisted Teens, Stalks, earlier this hour: The Holy Cross Tigers is out Nov. 6 on Sub Pop.",
        "Station ID at the top of the hour.",
    ],
    "after_triple_shot": [
        "Fontaines D.C. album Dopamine Chamber is out tomorrow on XL. Tour starts Oct. 21 in Lisbon.",
        "The Cuckoo Is A-Callin' is the B-side of Too Real, the band's first 7-inch on Partisan (late 2018; sources give Nov. 12 and Dec. 14). Chequeless Reckless is from the 2018 single with Boys in the Better Land.",
        "Tongue (shit x10) is not airable and sits in FCC Edit Needed.",
    ],
    "bay_area_break": [
        "Boy Harsher at the Fox in Oakland and Imperial Teen at Bottom of the Hill tonight.",
        "Heavens to Betsy first release since 1994 (baby's gone, Kill Rock Stars, Oct. 16). Bottom of the Hill Oct. 17 and 18.",
        "Dinosaur Jr. with Stef Chura at the Castro Oct. 18 (sold out). Giveaway: Dinosaur Jr. at the Guild in Menlo Park Mon. Oct. 19. Confirm with Suzi.",
    ],
    "after_songwriters_set": [
        "Sluice, Beadie: opener of Companion (Mtn Laurel Recording Co., Mar. 27). MJ Lenderman, She's Leaving You, from Manning Fireworks (2024).",
        "Cameron Winter, Live at Carnegie Hall: recorded at a December 2025 show, out Oct. 9 on Partisan. SAULT, Wildfires, from 2020.",
    ],
    "after_machines_set": [
        "Kraftwerk, Numbers, from Computer World (1981). Cabaret Voltaire, Nag, Nag, Nag, a 1979 single from Sheffield.",
        "Fujiya & Miyagi, No Green Light, from New Shiny Object (Oct. 30). Stace's pairing: the Brighton band reads as Kraftwerk and Cabaret Voltaire.",
    ],
}


def main():
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    fb = json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))

    # Every track already in the plan, keyed by videoId (cut tracks included).
    old = {t["videoId"]: t for s in plan["sets"] for t in s["tracks"]}

    # 1. Mark her removals as CUT and log them. Keep the entries in the plan file.
    cut_rows = []
    for vid, reason in REMOVED.items():
        t = old[vid]
        t["priority"] = "CUT"
        t["why"] = (t.get("why", "") + f" Removed from Air Order by DJ Stace ({reason}; cool-off to {COOLOFF}).").strip()
        cut_rows.append({"artist": t["artist"], "track": t["track"], "videoId": vid, "cut_on": TODAY,
                         "source": f"Stace edited Air Order (PLSosF7JAIkaM) Oct. 15: {reason}"})
        if not any(r.get("videoId") == vid for r in fb["removed"]):
            fb["removed"].append({"date": TODAY, "source_playlist": "Air Order (PLSosF7JAIkaM)",
                                  "artist": t["artist"], "title": t["track"], "videoId": vid,
                                  "note": reason, "cooloff_until": COOLOFF})
            # artist_removals counts removals per artist. Downweight only at 3 or more.
            fb["artist_removals"][t["artist"]] = fb["artist_removals"].get(t["artist"], 0) + 1
    plan.setdefault("cut", []).extend(cut_rows)

    # 2. Log her adds (the nine tail tracks plus the swap-ins). The pairing tracks are requests, not adds.
    logged = {a["videoId"] for a in fb["added_by_stace"]}
    set_of = {}
    for name, ids in SETS:
        for v in ids.split():
            set_of[v] = name
    for vid, t in NEW.items():
        if t["added_by"] != "DJ Stace" or vid in logged:
            continue
        fb["added_by_stace"].append({"date": TODAY, "source_playlist": "Air Order (PLSosF7JAIkaM)",
                                     "artist": t["artist"], "title": t["track"], "album": t["album"],
                                     "videoId": vid, "set": set_of[vid], "label": t["label"], "tag": t["tag"]})
    # Her move: Stef Chura now follows Heavens to Betsy in the Bay Area set.
    fb["moved_by_stace"].append({"date": TODAY, "source_playlist": "Air Order", "artist": "Stef Chura",
                                 "track": "The Concrete", "from": "Hour 2, Set 5, fifth track (Oct. 14 order)",
                                 "to": "Hour 2, Set 5, second track (after Heavens to Betsy)",
                                 "signal": "moved in Air Order; keep, follow her order"})
    fb.setdefault("housekeeping", []).append(
        "2026-10-15 show sync: Air Order 49 tracks. 8 removals logged (60-day cool-off), 13 adds logged, "
        "Fujiya & Miyagi paired with Kraftwerk and Cabaret Voltaire at her request.")

    # 3. Rebuild the sets in the final order. Existing tracks are reused; new ones come from NEW.
    pool = dict(old)
    for vid, t in NEW.items():
        t["videoId"] = vid          # the dict key is the YouTube Music video ID
    pool.update(NEW)
    new_sets = []
    for name, ids in SETS:
        tracks = [copy.deepcopy(pool[v]) for v in ids.split()]
        new_sets.append({"set": name, "tracks": tracks})
    plan["sets"] = new_sets

    # Cut tracks are listed once, under "cut", with priority CUT, and stay out of every set so the
    # Word script and the Zookeeper CSV never show them. Their full records live in plan["cut_tracks"].
    plan["cut_tracks"] = [old[v] for v in REMOVED]

    # 4. Triple Shot object.
    ts = plan["triple_shot"]
    ts["angle"] = TRIPLE_ANGLE
    ts["tracks"] = [copy.deepcopy(pool[v]) for v in "FXty6vOg0a0 Y-dA3yt8m8s ikKBcZg9jUc".split()]

    # 5. Mic breaks and the bench (drop any bench track that is now in a set).
    plan["mic_breaks"] = MIC_BREAKS
    in_sets = {t["videoId"] for s in plan["sets"] for t in s["tracks"]}
    plan["bench"] = [b for b in plan["bench"] if b.get("videoId") not in in_sets
                     and not (b["artist"] == "Fujiya & Miyagi" or (b["artist"] == "Twisted Teens" and b["track"] == "Stalks"))]

    # 6. Note the Air Order sync in the plan.
    plan["ytm_air_order"].update({"tracks": 49, "built": TODAY,
        "note": "Stace edited Air Order Oct. 15: 4 swaps, 4 cuts, 1 move, 9 adds at the end. Air Order is read only. "
                "Show order differs from Air Order in one way: her 9 tail tracks (and Kraftwerk and Cabaret Voltaire, added at her request) "
                "sit in their sets here, not at the end. Air Order order for the first 40 tracks is kept."})
    plan["final"] = {"built": TODAY, "cull_ticks": [], "replace_ticks": [],
                     "notes": "Oct. 15 morning sync from Air Order (49 tracks) plus 2 requested tracks. 51 airable tracks."}
    plan["note"] = plan["note"] + " Oct. 15 morning: Air Order edits applied, tail tracks placed in sets, Kraftwerk and Cabaret Voltaire added for Fujiya & Miyagi."

    PLAN_PATH.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    FEEDBACK_PATH.write_text(json.dumps(fb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    # 7. Inputs for the Word script builder.
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "plan_for_docx.json").write_text(json.dumps(
        {"sets": plan["sets"], "triple": TRIPLE_ANGLE}, ensure_ascii=False), encoding="utf-8")
    (BUILD_DIR / "mic_breaks.json").write_text(json.dumps(MIC_BREAKS, ensure_ascii=False), encoding="utf-8")
    (BUILD_DIR / "bench.json").write_text(json.dumps(plan["bench"], ensure_ascii=False), encoding="utf-8")

    n = sum(len(s["tracks"]) for s in plan["sets"])
    print(f"Plan rewritten: {len(plan['sets'])} sets, {n} airable tracks, {len(plan['cut_tracks'])} cut tracks logged.")


if __name__ == "__main__":
    main()
