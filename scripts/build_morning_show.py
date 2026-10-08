#!/usr/bin/env python3
"""
build_morning_show.py
=====================

Builds the one-off "Morning ZSU" show for DJ Stace (Wed., Oct. 7, 2026, 7-9 a.m. PT).
This is separate from the Thursday "The Library" plan. It never reads or writes
data/recon/ or outputs/recon/, so the Thursday build is not affected.

HOW TO RUN (from the repo root):
    python3 scripts/build_morning_show.py

WRITES:
    data/morning/2026-10-07/plan.json                       the plan (sets of tracks)
    outputs/morning/2026-10-07/morning_show_playlist_2026-10-07.csv   Zookeeper upload (track 1 first)
    outputs/morning/2026-10-07/notes_sheet_2026-10-07.csv   forward-order notes sheet
    outputs/morning/2026-10-07/morning_playlist.md          forward-order table with preview links
    outputs/morning/2026-10-07/show_script.md               script with talk breaks

Beginner notes:
* "Forward" order is the order tracks go on air. "Reversed" is last track first,
  because Stace's playout list runs bottom-up.
* Each track is a Python dictionary built by the helper t(...) below.
* FCC status came from Genius lyric pages (counts only, no lyrics stored).
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # repo root
sys.path.insert(0, str(ROOT / "scripts"))
from render_show_files import secs, watch, fcc_text    # reuse the Thursday helpers

DATE = "2026-10-07"
PLAN_DIR = ROOT / "data" / "morning" / DATE
OUT_DIR = ROOT / "outputs" / "morning" / DATE


def t(artist, track, album, label, label_src, released, dur, vid, why, fcc="CLEAN", fcc_note="CLEAN (Genius, Oct. 6)",
      tag="", cat="new", prio="R"):
    """Build one track record. cat is new, favorite, topical or wildcard."""
    return {"artist": artist, "track": track, "album": album, "label": label, "label_source": label_src,
            "tag": tag, "released": released, "duration": dur, "videoId": vid, "why": why,
            "fcc_status": fcc, "fcc_note": fcc_note, "priority": prio, "category": cat}


ZK_T = "ZK label table"
NOT_ZK = "not in ZK label table; spelled per press/Bandcamp"
STACE_REV = "CLEAN (Stace's review; no Genius page)"

SETS = [
    {"set": "Hour 1, Set 1: Wake-up, loud and new", "tracks": [
        t("Twisted Teens", "Peekaboo Hand", "Blame the Clown", "Chain Smoking Records", ZK_T + " (22350, created Oct. 6)",
          "2026-02-13 (album)", "3:23", "J2IJ6ugcmUI",
          "Core artist. Stace's 5-star pick on Blame the Clown. Album keyed in Zookeeper Oct. 6 (tag 1156418, Pending Appr); add tag after approval.",
          fcc_note=STACE_REV),
        t("Little Barrie", "More Bad Miles Of Road", "Gravity Freeze", "Easy Eye Sound", "ZK label 21304",
          "2026-05-22 (album)", "3:49", "QXOOzvDc3Nk", "Lead single from Gravity Freeze. Stace's 5-star pick."),
        t("Brigitte Calls Me Baby", "Altitude", "Altitude (single)", "Ato Records", "ZK label 12950",
          "2026-10-02 (single)", "3:03", "akcyM1qcfuM", "New this week."),
        t("Dinosaur Jr.", "Several Got Away", "There Near", "Jagjaguwar", "ZK label 9332",
          "2026-08-28 (album)", "3:34", "2XwYVWnYMB8", "Core artist. NACC #3 the week of Oct. 1. Castro Theatre Oct. 18."),
        t("Yard Act", "New Beginnings", "You're Gonna Need A Little Music", "Republic Records", "ZK label 8396",
          "2026-07-17 (album)", "3:28", "WUmzu_RDflM", "Single from the third album. Track 2 is the clean one on this record."),
    ]},
    {"set": "Hour 1, Set 2: Oct. 7 on the dial", "tracks": [
        t("Joy Division", "Transmission", "Transmission (single)", "Factory Records", "ZK label 20660; original release",
          "1979-10-07 (single)", "3:36", "Kx3EqNYQklg",
          "Factory released it Oct. 7, 1979, 47 years ago today. Library has Substance (tag 204354, Qwest); original not held, so tag left blank.",
          cat="topical"),
        t("The Beach Boys", "Shut Down", "Little Deuce Coupe", "Capitol Records", "ZK label 5761",
          "1963-10-07 (album)", "1:51", "pw8z14oW-gw",
          "Little Deuce Coupe, an all-cars album, came out Oct. 7, 1963.", cat="topical"),
        t("Radiohead", "Lotus Flower", "The King of Limbs", "XL Recordings", "ZK label 13409 (verify)",
          "2011 (album)", "5:01", "HgMAwBZ2M3w", "Thom Yorke was born Oct. 7, 1968. He turns 58 today. Overdue favorite artist.",
          cat="topical"),
        t("John Mellencamp", "Pink Houses", "Uh-Huh", "Mercury Records", "ZK label 9854 (verify; US release on Riva)",
          "1983 (album)", "4:44", "vBJCesNT9TM", "Mellencamp was born Oct. 7, 1951.", cat="topical", prio="O"),
    ]},
    {"set": "Hour 1, Set 3: New albums off the review shelf", "tracks": [
        t("Palace", "Made My Bed", "Ox", "Awal", "ZK label 21943 (Palace Presents not in ZK)",
          "2026-09-18 (album)", "4:01", "MR-dh4FTavQ", "Stace's 5-star pick. Fifth album, written as the band became fathers."),
        t("Sluice", "Zillow", "Companion", "Mtn Laurel Recording Co.", NOT_ZK,
          "2026-03-27 (album)", "3:13", "lpl4quk0T_g", "Stace's 5-star pick. Lyrics drawn from Zillow listings."),
        t("Lex Walton", "For Thee I Sing", "Ultimate Love Forever", "Sub Pop Records", "ZK label 3124",
          "2026-08-26 (album)", "2:01", "w7PnWZXJwoc", "Stace's 5-star pick. Seven songs, about 20 minutes, Sub Pop debut."),
        t("Dread Spectre Council", "Raven", "Thetans", "Handmade Records", "ZK label 17538",
          "2026-03-29 (album)", "4:54", "KZkx50Y-Cyg", "Stace's 5-star pick. One person from Norway. Segues with Built To Spill.",
          fcc_note=STACE_REV),
        t("Cut Worms", "Long Weekend", "Transmitter", "Jagjaguwar", "ZK label 9332",
          "2026-03-13 (album)", "2:54", "7-SzF72go3Q", "Produced by Jeff Tweedy. Library holds the 2023 self-titled only."),
        t("Tricky", "Because I Don't Know", "Different When It's Silent", "False Idols", NOT_ZK,
          "2026-07-17 (album)", "4:34", "gKkWSYQaxVo", "Stace's 5-star pick and 'the hit on the record.' Mitch Sanders falsetto."),
    ]},
    {"set": "Hour 1, Set 4: Favorites to start the day", "tracks": [
        t("Spoon", "The Underdog", "Ga Ga Ga Ga Ga", "Merge Records", "ZK library album 1094598",
          "2007 (album)", "3:43", "VaUOE8xv-zA", "Core artist, 93 shows aired.", tag="1094598", cat="favorite", prio="O"),
        t("Pixies", "Here Comes Your Man", "Doolittle", "4AD", "ZK library album 943354",
          "1989 (album)", "3:22", "XYrOmT72xZk", "Overdue favorite (last aired 2024). Morning pop hook.", tag="943354", cat="favorite", prio="O"),
        t("The Strokes", "Hard To Explain", "Is This It", "RCA Records", "Discogs spelling; not in ZK label table",
          "2001 (album)", "3:45", "2iF9-LAVcjE", "Garage-rock favorite. Recent YTM rotation.", cat="favorite", prio="O"),
        t("Mr. Gnome", "Mustangs", "The Heart of a Dark Star", "El Marko", "Stace's 2016 KZSU review; not in ZK label table",
          "2016 (album)", "4:53", "qtolJ-O4F80", "Core artist. Stace's 6-star pick in her 2016 review: 'play this song too much.'",
          cat="favorite"),
        t("Arcade Fire", "Wake Up", "Funeral", "Merge Records", "ZK label 1993 (US release)",
          "2004 (album)", "5:36", "gKNIMRGUQBA", "Hour 1 closer into the 8 a.m. turn. Overdue favorite (last aired 2022).", cat="topical"),
    ]},
    {"set": "Hour 2, Set 5: Fuzz and fast", "tracks": [
        t("Twisted Teens", "Riding", "Florida Water Blues", "Going Underground", NOT_ZK,
          "2026-07-10 (album)", "3:54", "qyMXk41TU7Y", "Stace's 5-star pick. Next album, The Holy Cross Tigers, is due Nov. 6 on Sub Pop."),
        t("Ty Segall", "Chrome", "Chrome", "Drag City", "ZK label 989",
          "2026-08-28 (album)", "5:08", "apwTEl0Lfew", "Title track. Ty's 18th solo album."),
        t("Lex Walton", "Ultimate Love 4Ever", "Ultimate Love Forever", "Sub Pop Records", "ZK label 3124",
          "2026-08-26 (album)", "3:06", "uan9YB7O8nU", "Stace's 5-star pick. Title track."),
        t("Sharp Pins", "Days of Change", "Mod Mayday 23", "K Records", "ZK label 1709",
          "2026-09-04 (reissue; orig. 2023)", "4:19", "45CJxgz5Zt0", "Recent like. NACC #15 the week of Oct. 1."),
        t("Chinese American Bear", "Turn Up The Radio", "Dim Sum and Then Some", "Moshi Moshi Records", "ZK label 18208",
          "2026-05-08 (album)", "2:42", "9S4KnK5IMQ4", "A song about turning up the radio. Good fit for a morning show."),
    ]},
    {"set": "Hour 2, Set 6: Midweek groove", "tracks": [
        t("This Is Lorelei", "Hey Sarah Is It Gonna Rain Forever", "The Singer in My Band", "Matador Records", "ZK label 1952",
          "2026-09-11 (album)", "3:28", "LHPybTFbWAA", "Core artist. Stace's 5-star pick."),
        t("Palace", "Denny's", "Ox", "Awal", "ZK label 21943 (Palace Presents not in ZK)",
          "2026-09-18 (album)", "4:50", "vEL9U3Z1cvo", "Stace's 5-star pick. Yacht-rock anthem about home."),
        t("Michael Kiwanuka", "Summer Clothes", "Fudge", "Polydor", "ZK label 2461",
          "2026-10-23 (album)", "4:26", "Q19tYEHCfP0", "New single. Album Fudge is due Oct. 23."),
        t("Teens in Trouble", "I Do", "I Do (single)", "Lauren Records", "ZK label 21542",
          "2026-10-05 (single; verify)", "3:00", "HDFgZYq0-zo", "New this week."),
        t("Sylvan Esso", "Concrete Glen", "Ow ∞", "Psychic Hotline", NOT_ZK,
          "2026-09-11 (album; single July 21)", "3:30", "PVcU0z1zPqk", "Lead single from Ow ∞. NACC #7 the week of Oct. 1."),
    ]},
    {"set": "Hour 2, Set 7: Favorites, round two", "tracks": [
        t("Wilco", "Heavy Metal Drummer", "Yankee Hotel Foxtrot", "Nonesuch Records", "ZK library album 656995",
          "2002 (album)", "3:09", "yeuIQFF7z6E", "Core artist.", tag="656995", cat="favorite", prio="O"),
        t("Father John Misty", "Chateau Lobby #4 (in C for Two Virgins)", "I Love You, Honeybear", "Sub Pop Records",
          "ZK library album 1072943", "2015 (album)", "2:52", "C664y0eYBaE", "Core artist, 81 shows aired.",
          tag="1072943", cat="favorite", prio="O"),
        t("Queens of the Stone Age", "Go With The Flow", "Songs for the Deaf", "Interscope Records", "ZK library album 670294",
          "2002 (album)", "3:08", "ZkRtdXSSuC0", "Core artist. Easy Street has an FCC word, so this is the clean swap.",
          tag="670294", cat="favorite", prio="O"),
        t("Sheer Mag", "Expect The Bayonet", "Need to Feel Your Love", "Wilsun Rc", "ZK library album 1113680",
          "2017 (album)", "3:46", "gnSZhI4beE4", "Next-tier favorite.", tag="1113680", cat="favorite", prio="O"),
        t("Bodega", "Thrown", "Broken Equipment", "Domino Recording Company", "ZK label 15506 (verify)",
          "2022 (album)", "2:48", "AJmXNZQvzZg", "Core artist, 67 shows aired.", cat="favorite", prio="O"),
    ]},
    {"set": "Hour 2, Set 8: Wildcards and the last stretch", "tracks": [
        t("Allah-Las", "Catamaran", "Allah-Las", "Innovative Leisure", "Discogs spelling; not in ZK label table",
          "2012 (album)", "3:33", "EUc2pNk5OwY", "Heard a lot, never aired.", cat="wildcard", prio="O"),
        t("Nilüfer Yanya", "midnight sun", "PAINLESS", "Ninja Tune", "ZK label 9404",
          "2022 (album)", "4:43", "E_LiLwsfhV8", "Heard a lot, never aired.", cat="wildcard", prio="O"),
        t("Khruangbin", "Time (You and I)", "Mordechai", "Dead Oceans", "ZK label 16748",
          "2020 (album)", "5:43", "5Y0da_fSK8I", "192 plays, never aired.", cat="wildcard", prio="O"),
        t("Hovvdy", "Life So Wide", "Big World", "Arts & Crafts", "ZK label 15095",
          "2026-08-14 (album)", "2:11", "DwNY8K04K6A", "NACC #32. Short.", prio="O"),
        t("Fontaines D.C.", "Marianne", "Marianne (single)", "XL Recordings", "ZK label 13409",
          "2026-08-18 (single)", "3:46", "ikKBcZg9jUc", "Core artist. Album Dopamine Chamber is due Oct. 16.", prio="O"),
    ]},
    {"set": "Closers and bench", "tracks": [
        t("Interpol", "See Out Loud", "See Out Loud / This Mirror Weighs a Ton", "Matador Records", "ZK label 1952",
          "2026-06-09 (single)", "4:57", "hrK12SX8Z98", "Bench. Core artist.", prio="O"),
        t("Dread Spectre Council", "Summon the Sparks", "Thetans", "Handmade Records", "ZK label 17538",
          "2026-03-29 (album)", "3:38", "2BXy9z_o868", "Bench. Stace's 5-star pick.", prio="O", fcc_note=STACE_REV),
        t("Twisted Teens", "Hand Me A Cigarette", "Florida Water Blues", "Going Underground", NOT_ZK,
          "2026-07-10 (album)", "3:26", "IY_J7QS6tMo", "Bench. Stace's 5-star pick.", prio="O"),
    ]},
]

# ----- Talk breaks (short, factual). One per set, read before the set starts. -----
BREAKS = {
    "Hour 1, Set 1: Wake-up, loud and new": [
        "7:00 Legal ID: KZSU Stanford, 90.1 FM. Morning ZSU with DJ Stace. It's Wednesday, Oct. 7.",
        "Open with the Twisted Teens. They have two albums out this year and a third on Sub Pop Nov. 6.",
        "Back-announce: Twisted Teens, Little Barrie, Brigitte Calls Me Baby (out Friday on Ato), Dinosaur Jr. (Castro Theatre Oct. 18), Yard Act.",
    ],
    "Hour 1, Set 2: Oct. 7 on the dial": [
        "Three Oct. 7 anchors: Joy Division's Transmission came out on Factory on this date in 1979. The Beach Boys' Little Deuce Coupe came out Oct. 7, 1963.",
        "Thom Yorke turns 58 today. John Mellencamp was born Oct. 7, 1951.",
        "Optional aside: Spotify launched Oct. 7, 2008. Radio is still here.",
    ],
    "Hour 1, Set 3: New albums off the review shelf": [
        "These are albums from this year that Stace reviewed in the library: Palace, Sluice, Lex Walton, Dread Spectre Council, Cut Worms and Tricky.",
        "Palace: fifth album, written as the members became fathers. Sluice: a song built from Zillow listings. Lex Walton: seven songs on Sub Pop, about 20 minutes.",
        "Dread Spectre Council is one person in Norway. Cut Worms' Transmitter was produced by Jeff Tweedy.",
    ],
    "Hour 1, Set 4: Favorites to start the day": [
        "Favorites run: Spoon, Pixies, the Strokes, Mr. Gnome, then Arcade Fire into the 8 a.m. hour.",
        "Mr. Gnome: Stace reviewed The Heart of a Dark Star in 2016 and rated Mustangs top of the record.",
        "8:00 Legal ID after Wake Up. Fleet Week is on in San Francisco this week, so the Bay may be loud. Read weather and traffic here.",
    ],
    "Hour 2, Set 5: Fuzz and fast": [
        "Fuzz set: Twisted Teens, Ty Segall, Lex Walton, Sharp Pins, Chinese American Bear.",
        "Turn Up The Radio is the cue to remind listeners the show streams at kzsu.stanford.edu.",
    ],
    "Hour 2, Set 6: Midweek groove": [
        "Slower pace, same morning energy. This Is Lorelei and Palace again from the review shelf.",
        "Michael Kiwanuka's Fudge is due Oct. 23. Teens in Trouble and Sylvan Esso round out the set. Sylvan Esso's Ow ∞ is at #7 on the college chart.",
    ],
    "Hour 2, Set 7: Favorites, round two": [
        "Back to the rotation: Wilco, Father John Misty, Queens of the Stone Age, Sheer Mag, Bodega.",
        "Queens of the Stone Age Easy Street is held out because it has an FCC word. Go With The Flow is the clean pick.",
    ],
    "Hour 2, Set 8: Wildcards and the last stretch": [
        "Wildcards: Allah-Las, Nilüfer Yanya and Khruangbin are artists Stace streams often and has not aired.",
        "Fontaines D.C. closes the plan. Their album Dopamine Chamber is out Oct. 16 on XL.",
        "8:58 Final ID and sign-off. Hand off to the next show.",
    ],
    "Closers and bench": [
        "Bench tracks, in case the plan runs short: See Out Loud, Summon the Sparks, Hand Me A Cigarette.",
    ],
}


def airable():
    """Yield (set name, track) in forward air order, skipping SKIP and CUT tracks."""
    for s in SETS:
        for tr in s["tracks"]:
            if tr["priority"] not in ("SKIP", "CUT"):
                yield s["set"], tr


def fmt(total):
    """Seconds to h:mm."""
    return "{}:{:02d}".format(total // 3600, total % 3600 // 60)


def main():
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(airable())
    main_rows = [r for r in rows if r[0] != "Closers and bench"]
    h1 = sum(secs(x["duration"]) for s, x in main_rows if s.startswith("Hour 1"))
    h2 = sum(secs(x["duration"]) for s, x in main_rows if s.startswith("Hour 2"))
    total = sum(secs(x["duration"]) for _, x in rows)
    mix = {}
    for _, x in main_rows:
        mix[x["category"]] = mix.get(x["category"], 0) + secs(x["duration"])
    main_total = h1 + h2

    # 1. plan JSON
    plan = {"show_date": DATE, "name": "Morning ZSU with DJ Stace, 7-9 a.m. PT",
            "note": "One-off morning show. Clean tracks only (FCC safe harbor). Separate from the Thursday Library plan.",
            "sets": SETS}
    (PLAN_DIR / "plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")

    # 2. Zookeeper CSV: no header, 6 quoted columns (artist, track, album, tag, label, timestamp)
    zk = [[x["artist"], x["track"], x["album"].replace(" (single)", ""), x["tag"],
           x["label"].replace(" (verify)", ""), ""] for _, x in rows]
    # Upload file: ALWAYS last on-air track first (confirmed by Stace, Oct. 7, 2026).
    # reversed() flips the list so the final track is row 1 and the opening track is the last row.
    with (OUT_DIR / ("morning_show_playlist_%s.csv" % DATE)).open("w", newline="", encoding="utf-8") as f:
        csv.writer(f, quoting=csv.QUOTE_ALL).writerows(list(reversed(zk)))

    # 3. Notes sheet CSV (forward order)
    with (OUT_DIR / ("notes_sheet_%s.csv" % DATE)).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "Set", "Type", "Artist", "Track", "Album", "Released", "Label", "Tag", "Time",
                    "FCC status", "YTM link", "Notes / talk points", "Cull"])
        for i, (s, x) in enumerate(rows, 1):
            w.writerow([i, s, x["category"], x["artist"], x["track"], x["album"], x["released"], x["label"], x["tag"],
                        x["duration"], fcc_text(x), watch(x), x["why"], ""])

    # 4. playlist table (forward)
    md = ["# Morning ZSU playlist: Wed., Oct. 7, 2026, 7-9 a.m. PT (draft)", "",
          "%d tracks, %s total (%s main plan + bench). Hour 1: %s. Hour 2: %s." % (
              len(rows), fmt(total), fmt(main_total), fmt(h1), fmt(h2)), "",
          "Mix by minutes (main plan): " + ", ".join(
              "%s %d%%" % (k, round(100 * v / main_total)) for k, v in sorted(mix.items(), key=lambda kv: -kv[1])) + ".", "",
          "| # | Set | Artist | Track | Album | Label | Tag | Time | FCC |", "|---|---|---|---|---|---|---|---|---|"]
    for i, (s, x) in enumerate(rows, 1):
        md.append("| %d | %s | %s | [%s](%s) | %s | %s | %s | %s | %s |" % (
            i, s, x["artist"], x["track"], watch(x), x["album"], x["label"], x["tag"], x["duration"], fcc_text(x)))
    md += ["", "## Left out for FCC", "",
           "- Queens of the Stone Age, \"Easy Street\": fuck x1 (Verse 2). Swapped for \"Go With The Flow\".",
           "- Guided By Voices, \"We Outlast Them All\": shit x1 (intro). Not used.",
           "", "## Checks", "",
           "- Every track was screened on Genius (counts only). Three have no Genius page and rely on Stace's own review notes: Peekaboo Hand, Raven, Summon the Sparks.",
           "- Tracks with `(verify)` in the label: Lotus Flower, Pink Houses, Thrown. Labels not in the Zookeeper table are marked in the Notes Sheet."]
    (OUT_DIR / "morning_playlist.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # 5. show script
    sc = ["# Morning ZSU script: Wed., Oct. 7, 2026, 7-9 a.m. PT", "",
          "DJ Stace on KZSU 90.1 FM Stanford. Clean tracks only. Plan runs %s of music; cull to fit around IDs, weather and talk." % fmt(main_total), "",
          "## Before the show", "",
          "- [ ] Load the Zookeeper CSV (`morning_show_playlist_2026-10-07.csv`). Track 1 (Peekaboo Hand) is the first row after upload.",
          "- [ ] Open the YTM playlist \"DJ Stace Morning ZSU Working\". It is reversed too; play bottom-up.",
          "- [ ] Pull weather and traffic for the 8:00 break.",
          "- [ ] Listen first: Peekaboo Hand, Raven, Summon the Sparks have no Genius page. Stace's review lists no FCC words on them.",
          "- [ ] Today is the anniversary of Oct. 7, 2023. Memorial events are happening around the Bay Area. Keep the talk breaks straight; nothing here ties to it.",
          "", "## Sets"]
    n = 0
    for s in SETS:
        sc += ["", "### " + s["set"], ""]
        for line in BREAKS.get(s["set"], []):
            sc.append("- " + line)
        sc.append("")
        for x in s["tracks"]:
            n += 1
            tag = " Tag %s." % x["tag"] if x["tag"] else ""
            sc.append("%d. **%s, \"%s\"** (%s) %s.%s %s FCC: %s." % (
                n, x["artist"], x["track"], x["duration"], x["label"], tag, x["why"], fcc_text(x)))
    (OUT_DIR / "show_script.md").write_text("\n".join(sc).replace("..", ".") + "\n", encoding="utf-8")

    print("%d tracks, %s total; main plan %s (H1 %s, H2 %s). Mix: %s" % (
        len(rows), fmt(total), fmt(main_total), fmt(h1), fmt(h2), mix))
    print("Upload CSV first row:", zk[0][1], "| last row:", zk[-1][1])


if __name__ == "__main__":
    main()
