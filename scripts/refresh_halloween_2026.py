#!/usr/bin/env python3
"""
refresh_halloween_2026.py
=========================

Oct. 15, 2026 refresh of the Halloween specialty show (two weeks out).
Reads  data/recon/2026-10-29/working_playlist.json  (seeded Oct. 4),
adds YouTube Music videoIds, durations, Zookeeper tags and labels, the
Today in Music items, Bay Area shows and a Triple Shot, then rewrites:
  1. data/recon/2026-10-29/working_playlist.json
  2. outputs/specialty/halloween-2026.md

Run from the repo root:  python3 scripts/refresh_halloween_2026.py
It is safe to run twice: it only fills fields, and it rebuilds the sets
from the track table below.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "data" / "recon" / "2026-10-29" / "working_playlist.json"
MD = ROOT / "outputs" / "specialty" / "halloween-2026.md"

# label_source values used in the plan
ZKL = "zookeeper label table"   # label spelled as Zookeeper spells it
ZKA = "zookeeper album"         # label from the library album record
WEB = "web (verify)"            # not in Zookeeper; check at the studio
UNV = "unverified"              # nothing found

# Per-track facts, keyed by "artist|track" as written in the plan.
# Fields: videoId, duration, album, year, tag, label, label_source, extra note
# 'zk_alt' holds a library compilation or single that contains the track
# (kept so Stace can pull the CD, but not used as the tag).
F = {
 "Ministry|Every Day Is Halloween": ("D2MH5c2sTvc", "6:37", "Twelve Inch Singles", "1984", "", "Wax Trax! Records", ZKL, "", "470607"),
 "Misfits|Halloween": ("jfJkvnXx8vw", "1:53", "Halloween (single)", "1981", "", "Plan 9 (not in ZK label table)", WEB, "", "291721"),
 "Screamin' Jay Hawkins|I Put a Spell on You": ("JD-qp1HMMIc", "2:25", "At Home with Screamin' Jay Hawkins", "1956", "", "Okeh", ZKL, "", "861667"),
 "The Sonics|The Witch": ("HGBsxpnRhMk", "2:41", "Here Are the Sonics!!!", "1965", "1086140", "Norton Records", ZKA, "", ""),
 "The Cramps|Goo Goo Muck": ("zGNLqyVXRpI", "3:07", "Psychedelic Jungle", "1981", "", "I.R.S. Records", ZKL, "", "1087938"),
 "Misfits|Night of the Living Dead": ("2cDvymU9D-M", "1:58", "Walk Among Us", "1982 (single 1979)", "933858", "Ruby Records", ZKA, "", ""),
 "Roky Erickson|I Walked with a Zombie": ("ErhXr2_QoPk", "2:47", "The Evil One", "1981", "", "415 Records", ZKL, "", ""),
 "The Lemonheads|Roky (feat. The Bevis Frond)": ("hfY_ED9xAnw", "3:03", "Roky (feat. The Bevis Frond)", "2026", "", "Fire Records", ZKL, "", ""),
 "Queens of the Stone Age|Where the Goth Girls At?": ("9jA_Bg_r_cw", "3:29", "Perfecth", "2026", "", "Matador Records", ZKL, "", ""),
 "Queens of the Stone Age|Burn the Witch": ("ZYydAkq6nTc", "3:36", "Lullabies to Paralyze", "2005", "", "Interscope Records", ZKL, "", ""),
 "Queens of the Stone Age|No One Knows": ("z_59a_hnYdU", "4:39", "Songs for the Deaf", "2002", "670294", "Interscope Records", ZKA, "", ""),
 "Death Valley Girls|Basic Witch": ("m2g-drNGOFE", "3:10", "Welcome to Earth", "2026", "", "Suicide Squeeze (not in ZK label table)", WEB, "", ""),
 "The Black Angels|Young Men Dead": ("gvLJZKdrDZ4", "5:33", "Passover", "2006", "816320", "Light In The Attic Records", ZKA, "", ""),
 "The Black Angels|Black Grease": ("6G7yLulp4oI", "4:33", "Passover", "2006", "816320", "Light In The Attic Records", ZKA, "", ""),
 "Thee Oh Sees|Dead Man's Gun": ("BB74rsWzJjw", "3:29", "A Weird Exits", "2016", "1096073", "Castle Face Records", ZKA, "", ""),
 "Ty Segall|Despoiler of Cadaver": ("oWDKts8eESY", "3:53", "Manipulator", "2014", "", "Drag City", ZKL, "", ""),
 "The Wytches|Gravedweller": ("SWGkfg396yo", "2:49", "Annabel Dream Reader", "2014", "1059870", "Partisan Records", ZKA, "", ""),
 "Black Rebel Motorcycle Club|Beat the Devil's Tattoo": ("Ay3Izb6sGAo", "3:46", "Beat the Devil's Tattoo", "2010", "932330", "Vagrant Records", ZKA, "", ""),
 "Alex G|Witch": ("dQWdpG1q6VQ", "2:41", "Rocket", "2017", "1110812", "Domino Recording Company", ZKA, "", ""),
 "Bauhaus|Bela Lugosi's Dead": ("Yy9h2q_dr9k", "9:37", "Bela Lugosi's Dead (single)", "1979", "1084070", "Small Wonder Records", ZKA, "", ""),
 "Siouxsie and the Banshees|Spellbound": ("n_bXdEA6nSM", "3:18", "Juju", "1981", "", "Polydor", ZKL, "", "935030"),
 "The Cure|Lullaby": ("CXHz_6qmHFg", "4:11", "Lullaby (single)", "1989", "938954", "Elektra Records (Local)", ZKA, "On Disintegration. Library holds the single.", ""),
 "Joy Division|Dead Souls": ("mKWHa65cmns", "4:55", "Still", "1981 (recorded 1979)", "939427", "Factory Communications", ZKA, "", ""),
 "Love and Rockets|Haunted When the Minutes Drag": ("izoST3hMBNA", "8:02", "Seventh Dream of Teenage Heaven", "1985", "1082494", "Beggars Banquet", ZKA, "", ""),
 "The Horrors|Who Can Say": ("TnHVCh6sBKA", "3:42", "Primary Colours", "2009", "895046", "Xl Recordings", ZKA, "", ""),
 "Interpol|Evil": ("uUOMQzQdU34", "3:36", "Antics", "2004", "760878", "Matador Records", ZKA, "", ""),
 "Bambara|Steel Dust Ocean": ("KdRQN6g8Z-s", "2:58", "", "2018", "", "Wharf Cat (not in ZK label table)", WEB, "", ""),
 "Pixies|Dead": ("UgWgDWgNBzQ", "2:22", "Doolittle", "1989", "943354", "4AD", ZKA, "", ""),
 "Radiohead|Burn the Witch": ("qIm0fsMo0Rg", "3:41", "A Moon Shaped Pool", "2016", "1094868", "Xl Recordings", ZKA, "", ""),
 "Nick Cave & The Bad Seeds|Red Right Hand": ("lBVFdSFV2lQ", "6:11", "Let Love In", "1994", "", "Mute Records", ZKL, "", ""),
 "Tom Waits|What's He Building?": ("WaTZe6x7WUw", "3:21", "Mule Variations", "1999", "", "Anti-", ZKL, "", ""),
 "Black Sabbath|Black Sabbath": ("MOefQyJumI8", "9:26", "Black Sabbath", "1970", "937537", "Warner Bros. Records", ZKA, "YTM version runs 9:26. Oct. 30, 1998: the four original members reunited to play \"Paranoid\" on Letterman.", ""),
 "Diet Cig|Blob Zombie": ("ewh_srl5Vuk", "2:01", "Swear I'm Good at This", "2017", "1110069", "Frenchkiss Records", ZKA, "", ""),
 "Mr. Gnome|Heave Yer Skeleton": ("ta8cFX5g_WE", "3:56", "", "2012", "", "", UNV, "", ""),
 "Jealous of the Birds|Plastic Skeletons": ("MTw_XekYufI", "3:13", "", "2021", "", "", UNV, "", ""),
 "Hurray for the Riff Raff|Hungry Ghost": ("UYcvh2zTdPE", "3:26", "The Navigator", "2017", "1107155", "Ato Records", ZKA, "", ""),
 "The Flaming Lips|One Night While Hunting for Faeries and Witches and Wizards to Kill": ("hc1RxBX8R60", "6:08", "Oczy Mlody", "2017", "1104040", "Warner Bros. Records", ZKA, "Year corrected from 2002 to 2017 (Oczy Mlody, per the library record).", ""),
 "Spoon|The Ghost of You Lingers": ("D1BQcGRF46w", "3:36", "Ga Ga Ga Ga Ga", "2007", "1094598", "Merge Records", ZKA, "", ""),
 "The Kills|Doing It To Death": ("S7xdUYzVFf0", "4:08", "Ash & Ice", "2016", "1093531", "Domino Recording Company", ZKA, "Year corrected from 2008 to 2016 (Ash & Ice, per the library record).", ""),
 "The Dead Weather|Treat Me Like Your Mother": ("aUmtARqY_ro", "4:11", "Horehound", "2009", "900931", "Third Man Records", ZKA, "", ""),
 "Mitski|Your Best American Girl": ("CsfLdu5ij74", "3:33", "Puberty 2", "2016", "1094475", "Dead Oceans", ZKA, "Puberty 2 10th Anniversary Edition out Oct. 30 (Dead Oceans).", ""),
 "Stef Chura|Sweet Sweet Midnight": ("JcEeRS8DDPA", "5:30", "", "2026", "", "", UNV, "", ""),
 "Car Seat Headrest|Sober to Death": ("ipaTDwWTYiE", "5:05", "Twin Fantasy", "2018", "1120228", "Matador Records", ZKA, "", ""),
 "Zeal & Ardor|Devil Is Fine": ("gqD0YiOhRe8", "3:13", "Devil Is Fine", "2016", "1117987", "Mvka", ZKA, "Year corrected from 2018 to 2016 (library record).", ""),
 "Alice Cooper|Feed My Frankenstein": ("9xC459XOAfs", "4:45", "Hey Stoopid", "1991", "", "Epic Records", ZKL, "", "28022"),
 "Bobby \"Boris\" Pickett|Monster Mash": ("bRLML36HnzU", "3:13", "The Original Monster Mash", "1962", "", "Garpax (not in ZK label table)", WEB, "", ""),
 "King Gizzard & The Lizard Wizard|The Acrid Corpse": ("M_vDovWJBtE", "1:01", "", "2019", "", "", UNV, "", ""),
}

# Note: the YTM playlist API also returns a "Suggestions" shelf (7 rows) after the real
# tracks. Those are not playlist tracks, so they are not in this plan.
ADDED_LATER = {}  # (the seven YTM "Suggestions" rows are NOT playlist tracks; ignored)
NEW_FCC = {
 "Black Sabbath|Black Sabbath": "CLEAN (Genius, 98 words)",
 "Queens of the Stone Age|No One Knows": "CLEAN (Genius, 228 words)",
}

# Where each new track goes: (set name prefix, insert after this "artist|track")
INSERT = {
 "Black Sabbath|Black Sabbath": ("Set 3", "Joy Division|Dead Souls"),
}

TRIPLE = ["Queens of the Stone Age|Where the Goth Girls At?",
          "Queens of the Stone Age|No One Knows",
          "Queens of the Stone Age|Burn the Witch"]


def key(t):
    """Same key format as the table above."""
    return f"{t['artist']}|{t['track']}"


def secs(d):
    m, s = d.split(":")
    return int(m) * 60 + int(s)


def main():
    plan = json.loads(PLAN.read_text())
    by_key = {}
    sets = []
    for s in plan["sets"]:
        if s["set"].startswith("Thursday Triple Shot"):
            continue  # rebuilt below on re-run
        tr = [t for t in s["tracks"]]
        sets.append({"set": s["set"], "tracks": tr})
        for t in tr:
            by_key[key(t)] = t

    # enrich every existing track from the table
    for k, t in by_key.items():
        if k not in F:
            raise SystemExit("missing facts for " + k)
        vid, dur, album, year, tag, label, src, note, alt = F[k]
        t.update({"videoId": vid, "duration": dur, "album": album, "tag": tag,
                  "label": label, "label_source": src})
        if year:
            t["released"] = year
        if note:
            t["why"] = (t.get("why", "") + " " + note).strip()
        if alt:
            t["zk_alt"] = alt
    # new tracks
    new = {}
    for k, fcc in {**ADDED_LATER, **NEW_FCC}.items():
        artist, track = k.split("|")
        vid, dur, album, year, tag, label, src, note, alt = F[k]
        t = {"artist": artist, "track": track, "album": album, "label": label,
             "label_source": src, "tag": tag, "released": year, "duration": dur,
             "videoId": vid, "fcc_status": "CLEAN", "fcc_note": fcc,
             "why": note, "priority": "R", "source": "specialty/halloween"}
        if k in ADDED_LATER:
            t["added_by"] = "DJ Stace (added to the playlist after Oct. 4)"
        else:
            t["added_by"] = "kzsu-monthly-specialty (Oct. 15)"
        if alt:
            t["zk_alt"] = alt
        new[k] = t
        by_key[k] = t
    for k, (setname, after) in INSERT.items():
        for s in sets:
            if s["set"].startswith(setname):
                idx = [key(x) for x in s["tracks"]].index(after)
                s["tracks"].insert(idx + 1, new[k])
    # Triple Shot: pull the three QOTSA tracks out of their sets into their own set
    shot = []
    for k in TRIPLE:
        t = by_key[k] if k in by_key else new[k]
        for s in sets:
            s["tracks"] = [x for x in s["tracks"] if key(x) != k]
        shot.append(t)
    # QOTSA No One Knows is new, so make sure it is in `shot`
    nok = "Queens of the Stone Age|No One Knows"
    if nok in new and nok not in [key(x) for x in shot]:
        shot.insert(1, new[nok])
    shot_set = {"set": "Thursday Triple Shot: Queens of the Stone Age", "tracks": shot}
    # put the Triple Shot after Set 2 (start of Hour 2 area)
    out_sets = []
    for s in sets:
        out_sets.append(s)
        if s["set"].startswith("Set 2"):
            out_sets.append(shot_set)
    plan["sets"] = out_sets

    plan["triple_shot"] = {
        "artist": "Queens of the Stone Age",
        "angle": "New single from Perfecth (out Oct. 30, Matador), a Halloween-titled deep cut and the band's biggest single. Core artist: 73 shows.",
        "tracks": [{"artist": t["artist"], "track": t["track"], "videoId": t["videoId"]} for t in shot],
        "history_check": "Not in the last 8 Triple Shot artists (Teenage Fanclub Oct. 8, Fontaines D.C. Oct. 15).",
    }
    plan["today_in_music"] = {
        "oct_29": [
            "1965: The Who release \"My Generation\" in the UK.",
            "1971: Duane Allman dies in a motorcycle crash.",
            "1996: The Stone Roses split.",
            "Birthdays: Peter Green (Fleetwood Mac, 1946), Roger O'Donnell (The Cure, 1955), Peter Timmins (Cowboy Junkies, 1965).",
        ],
        "oct_30": [
            "1968: Marvin Gaye's \"I Heard It Through the Grapevine\" reaches No. 1 on the Hot 100.",
            "1971: John Lennon's Imagine tops the UK chart.",
            "1998: All four original members of Black Sabbath reunite on Letterman to play \"Paranoid\".",
            "Birthdays: Grace Slick (Jefferson Airplane, 1939), Gavin Rossdale (Bush, 1967).",
        ],
        "fits": "O'Donnell's birthday fits The Cure \"Lullaby\" (Set 3). The Sabbath reunion fits Black Sabbath \"Black Sabbath\" (Set 3).",
        "source": "thisdayinmusic.com Oct. 29 and Oct. 30 pages",
    }
    plan["new_releases"] = [
        "Death Valley Girls, Welcome to Earth (Oct. 9, Suicide Squeeze).",
        "The Lemonheads with The Bevis Frond, \"Roky\" 12-inch (Oct. 16, Fire Records).",
        "Queens of the Stone Age, Perfecth (Oct. 30, Matador). \"Where the Goth Girls At?\" is the lead single.",
        "Ministry, Hate to Go (Oct. 30, Cleopatra), the band's final album.",
        "Mitski, Puberty 2 10th Anniversary Edition (Oct. 30, Dead Oceans).",
    ]
    plan["bay_area_shows"] = [
        "Thu Oct. 29, Kilowatt, S.F.: Halloween covers show (Spencer Noble, Band Yo!, Bromf, Mitch Rocket), 7 p.m.",
        "Thu Oct. 29, Bottom of the Hill, S.F.: Astrozombies SF, Rusty Chains, Caution (tribute night), 8 p.m.",
        "Thu Oct. 29, The Independent, S.F.: Patrick Wolf, 7:30 p.m.",
        "Fri Oct. 30, Great American Music Hall, S.F.: Cold Cave (solo), SRSQ, Houses of Heaven and more.",
        "Fri Oct. 30 and Sat Oct. 31, Thee Stork Club, Oakland: Halloween tribute band extravaganza, 8 p.m.",
        "Fri Oct. 30, Bottom of the Hill, S.F.: Temptation, Dead Souls, Flippy Floppy (tribute night), 8 p.m.",
        "Source: foopee.com, week of Oct. 26. Confirm times and prices before air.",
    ]
    plan["note"] = ("Halloween special. Seeded Oct. 4; refreshed Oct. 15 by kzsu-monthly-specialty: videoIds, "
                    "durations, Zookeeper tags and labels filled; Today in Music, new releases, Bay Area shows "
                    "and a Queens of the Stone Age Triple Shot added. Still to do on the regular tasks: "
                    "ticket giveaway, mic-break text, final cull by Stace.")
    plan["specialty_playlist"] = {"id": "PLPKWMgnm3SDs", "tracks": sum(len(s["tracks"]) for s in out_sets)}
    PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n")

    # ---------- markdown ----------
    allt = [t for s in out_sets for t in s["tracks"]]
    total = sum(secs(t["duration"]) for t in allt)
    L = ["# Library Specialty: Halloween 2026\n",
         f"Show: Thursday, Oct. 29, 2026. {len(allt)} tracks, {total // 3600} hr {(total % 3600) // 60} min on YouTube Music (target 2.5 hr; long tracks flagged so you can cull). Refreshed Oct. 15.\n",
         "Playlist: https://music.youtube.com/playlist?list=PLPKWMgnm3SDs\n",
         "FCC screen: LRCLIB and Genius lyric databases. Counts only, no lyrics stored. Database lyrics can be wrong, so confirm by ear.\n",
         "## Today in Music\n"]
    for line in plan["today_in_music"]["oct_29"]:
        L.append("- Oct. 29, " + line)
    for line in plan["today_in_music"]["oct_30"]:
        L.append("- Oct. 30, " + line)
    L.append("- Fits: " + plan["today_in_music"]["fits"])
    L.append("- Sources: [This Day in Music, Oct. 29](https://www.thisdayinmusic.com/on-this-day-in-music-october-29/), [Oct. 30](https://www.thisdayinmusic.com/on-this-day-in-music-october-30/)\n")
    L.append("## New releases that fit\n")
    for r in plan["new_releases"]:
        L.append("- " + r)
    L.append("- Checked, not added: Pause & Play lists Car Seat Headrest and Fontaines D.C. for Oct. 16 (titles not confirmed). No Halloween fit found.\n")
    L.append("## Triple Shot\n")
    L.append(f"- {plan['triple_shot']['artist']}: " + ", ".join(f"\"{t['track']}\"" for t in plan['triple_shot']['tracks']) + ".")
    L.append(f"- Angle: {plan['triple_shot']['angle']}")
    L.append(f"- {plan['triple_shot']['history_check']}\n")
    L.append("## Bay Area shows\n")
    for b in plan["bay_area_shows"]:
        L.append("- " + b)
    L.append("")
    L.append("## Left out for FCC\n")
    L.append("- Ministry \"Burned Out\": \"shit\" x1 (Verse 3).")
    L.append("- Black Lips \"Bad Kids\": \"shit\" x1.")
    L.append("- Tropical Fuck Storm: band name contains an FCC word. Not added.")
    L.append("- Unverified, not added: The Pleasure Routine \"Bloody Nose\", Ministry \"We Hate\".\n")
    L.append("## Changes since Oct. 4\n")
    L.append("- Added: Black Sabbath \"Black Sabbath\" and Queens of the Stone Age \"No One Knows\" (Triple Shot).")
    L.append("- Year fixes from the library record: Flaming Lips (2017, Oczy Mlody), The Kills (2016, Ash & Ice), Zeal & Ardor (2016).")
    L.append("- Radiohead \"Burn the Witch\" still duplicates the QOTSA title; the QOTSA track now sits in the Triple Shot.\n")
    n = 0
    for s in out_sets:
        L.append(f"## {s['set']}\n")
        L.append("| # | Artist | Track | Year | Time | Label | Tag | FCC | Notes |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for t in s["tracks"]:
            n += 1
            note = t.get("why", "") or ""
            L.append(f"| {n} | {t['artist']} | {t['track']} | {t.get('released','')} | {t['duration']} | {t.get('label') or 'unverified'} | {t.get('tag') or '-'} | {t.get('fcc_note','')} | {note} |")
        L.append("")
    L.append("## Notes\n")
    L.append("- Labels marked \"not in ZK label table\" or \"unverified\" need a check at the studio. Tags are filled only where the library holds the album that contains the track.")
    L.append("- Long tracks to cull if needed: Bela Lugosi's Dead (9:37), Black Sabbath (9:26 on YTM), Love and Rockets (8:02), Red Right Hand (6:11), Flaming Lips (6:08).")
    MD.write_text("\n".join(L) + "\n")
    print(len(allt), "tracks", total, "seconds")


if __name__ == "__main__":
    main()
