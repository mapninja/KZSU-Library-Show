#!/usr/bin/env python3
"""
build_thanksgiving_2026.py
==========================

Builds the Thanksgiving 2026 specialty-show files from one list of tracks:
  1. data/recon/2026-11-26/working_playlist.json  (the plan other skills read)
  2. outputs/specialty/thanksgiving-2026.md        (track notes for Stace)

Run from the repo root:  python3 scripts/build_thanksgiving_2026.py

Each track is a tuple. Field order is explained in the TRACKS comment below.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root

# Fields: set number, artist, track, album, year, duration, YTM videoId,
#         Zookeeper tag, label, label_source, FCC note, notes
S1 = "Set 1: Thanks and gratitude"
S2 = "Set 2: The Last Waltz, Thanksgiving 1976"
S3 = "Set 3: Family, home and autumn"
S4 = "Set 4: Punk at 50 and lapsed favorites"
S5 = "Set 5: Feast and indie core"

ZKL = "zookeeper label table"          # label spelled as Zookeeper spells it
ZKA = "zookeeper album"                # label came from the library album record
WEB = "web (verify)"                   # label from the web only; not in Zookeeper
CLEAN = "CLEAN"

TRACKS = [
    (S1, "Sly & The Family Stone", "Thank You (Falettinme Be Mice Elf Agin)", "Stand! (single version)", "1969", "4:52", "09bSoxFgaRI", "", "Epic Records", ZKL, "CLEAN (Genius, 394 words)", "Opens on the theme. Library holds only a compilation (808567), so no tag."),
    (S1, "Ty Segall", "Thank You Mr. K", "Ty Segall", "2017", "2:53", "93NdWDNjYr0", "", "Drag City", ZKL, "CLEAN (Genius, 164 words)", "Core artist, 93 shows. Not in the library."),
    (S1, "Big Star", "Thank You Friends", "Third/Sister Lovers", "1978 (recorded 1974)", "3:07", "AIILzYKrwMA", "26491", "Rykodisc", ZKA, "CLEAN (Genius, 167 words)", ""),
    (S1, "Bill Withers", "Grandma's Hands", "Just As I Am", "1971", "2:02", "wSR47gxC0W4", "", "Sussex", ZKL, "CLEAN (Genius, 194 words)", "Family tribute; short."),
    (S1, "The Mountain Goats", "This Year", "The Sunset Tree", "2005", "3:54", "td5O5jfl9Xs", "774266", "4AD", ZKA, "CLEAN (Genius, 267 words)", "YTM lists the 2025 remaster."),
    (S1, "The Flaming Lips", "Do You Realize??", "Yoshimi Battles the Pink Robots", "2002", "3:34", "BhjKuOfzLB8", "662509", "Warner Brothers (Modern)", ZKA, "CLEAN (Genius, 165 words)", "Hour 1 closer candidate."),
    (S2, "The Band", "Don't Do It (Concert Version)", "The Last Waltz", "1978 (recorded Nov. 25, 1976)", "6:20", "-lRjfz4Kq_Q", "", "Warner Bros. Records", WEB, "CLEAN (Genius, 364 words)", "The Last Waltz was Thanksgiving night 1976 at Winterland, San Francisco. 50th anniversary is Nov. 25, 2026, the day before the show. Library holds only compilations."),
    (S2, "Muddy Waters", "Mannish Boy (Concert Version)", "The Last Waltz", "1978", "6:41", "iE-RSQKDTnI", "", "Warner Bros. Records", WEB, "CLEAN (Genius, 195 words)", "Long. Cull candidate."),
    (S2, "Van Morrison", "Caravan (Concert Version)", "The Last Waltz", "1978", "6:12", "4q9GDvXI0rk", "", "Warner Bros. Records", WEB, "CLEAN (Genius, 420 words)", "Long. Cull candidate."),
    (S2, "Neil Young", "Helpless (Concert Version)", "The Last Waltz", "1978", "5:54", "k02ZwnTnG9E", "", "Warner Bros. Records", WEB, "CLEAN (Genius, 230 words)", "With Joni Mitchell on backing vocals."),
    (S2, "Joni Mitchell", "Coyote (Concert Version)", "The Last Waltz", "1978", "5:29", "x73OsiAHhLA", "", "Warner Bros. Records", WEB, "CLEAN (Genius, 495 words)", ""),
    (S2, "Bob Dylan", "Forever Young (Concert Version)", "The Last Waltz", "1978", "5:52", "cfonGN0Slt8", "", "Warner Bros. Records", WEB, "CLEAN (Genius, 137 words)", "Dylan closed the concert."),
    (S2, "The Band", "The Last Waltz Suite: The Weight", "The Last Waltz", "1978", "4:36", "h7cGWmMM6Vs", "", "Warner Bros. Records", WEB, "CLEAN (Genius, 408 words)", "Set closer. Staple Singers appear in the film version."),
    (S3, "Fleetwood Mac", "The Chain", "Rumours", "1977", "4:30", "FhgFtXESdPk", "512288", "Warner Brothers (Modern)", ZKA, "CLEAN (LRCLIB). Genius page lists one \"fuck\" at line 2; likely a page artifact, confirm by ear.", "Bassist John McVie was born Nov. 26, 1945. Family-drama album."),
    (S3, "Ike & Tina Turner", "Nutbush City Limits", "Nutbush City Limits", "1973", "3:20", "DbivX78Degg", "", "United Artists", ZKL, "CLEAN (Genius, 181 words)", "Tina Turner was born Nov. 26, 1939."),
    (S3, "Dolly Parton", "Coat of Many Colors", "Coat of Many Colors", "1971", "3:04", "SyP0Sy9KFf0", "", "Rca Victor", ZKL, "CLEAN (Genius, 340 words)", "Library holds only a compilation (717960)."),
    (S3, "Neil Young", "Harvest Moon", "Harvest Moon", "1992", "5:04", "HDzHhqWZMD0", "", "Reprise Records", ZKL, "CLEAN (Genius, 180 words)", "Long. Cull candidate."),
    (S3, "The Kinks", "Autumn Almanac", "Something Else (Deluxe)", "1967", "3:14", "E3NTjsG5_Is", "", "Pye Records", ZKL, "CLEAN (Genius, 297 words)", "Library holds only Kink Kronikles (909200)."),
    (S3, "Wilco", "Heavy Metal Drummer", "Yankee Hotel Foxtrot", "2002", "3:09", "yeuIQFF7z6E", "656995", "Nonesuch Records", ZKA, "CLEAN (Genius, 227 words)", "Bassist John Stirratt was born Nov. 26, 1967."),
    (S3, "Billy Bragg & Wilco", "California Stars", "Mermaid Avenue", "1998", "4:59", "JPgLoJCX0R8", "", "Elektra (not in ZK label table)", WEB, "CLEAN (Genius, 284 words)", "Woody Guthrie lyrics."),
    (S3, "Courtney Barnett", "Depreston", "Sometimes I Sit and Think, and Sometimes I Just Sit", "2015", "4:53", "Ok2f0cTmXAo", "", "Mom + Pop", ZKL, "CLEAN (Genius, 292 words)", "Core artist. Not in the library."),
    (S3, "Spoon", "The Way We Get By", "Kill the Moonlight", "2002", "2:40", "nDHNcZDyFXE", "1094587", "Merge Records", ZKA, "CLEAN (Genius, 351 words)", "Core artist."),
    (S3, "Father John Misty", "Bored in the USA", "I Love You, Honeybear", "2015", "4:23", "BD4MDyS_glE", "1072943", "Sub Pop Records", ZKA, "CLEAN (Genius, 238 words)", "Core artist. American-holiday pick."),
    (S4, "Sex Pistols", "Pretty Vacant", "Never Mind the Bollocks, Here's the Sex Pistols", "1977", "3:19", "2sQaJNtbSzI", "903574", "Warner Bros. Records", ZKA, "CLEAN (Genius, 248 words)", "Anniversary set. The debut single \"Anarchy in the U.K.\" came out Nov. 26, 1976, 50 years before the show. That track has one \"pissed\" (see FCC Edit Needed)."),
    (S4, "Sex Pistols", "God Save the Queen", "Never Mind the Bollocks, Here's the Sex Pistols", "1977", "3:21", "GQeCiGJYoU0", "903574", "Warner Bros. Records", ZKA, "CLEAN (Genius, 207 words)", ""),
    (S4, "The Clash", "Train in Vain (Stand by Me)", "London Calling", "1979", "3:15", "b3akwA6CJ8U", "779058", "Epic Records (Modern)", ZKA, "CLEAN (Genius, 307 words)", "Lapsed favorite, last aired May 2024."),
    (S4, "Stiff Little Fingers", "Alternative Ulster", "Inflammable Material", "1979", "2:44", "PlGmYetiCjA", "", "Rough Trade", ZKL, "CLEAN (Genius, 245 words)", "Lapsed favorite, last aired 2019. Library holds only All the Best (1086364)."),
    (S4, "Big Boys", "Fun, Fun, Fun", "Fun Fun Fun", "1981", "3:15", "fvFLtKkzL-g", "", "Moment Records", ZKL, "CLEAN (Genius, 183 words)", "Texas punk slot."),
    (S4, "Ramones", "I Wanna Be Sedated", "Road to Ruin", "1978", "2:30", "V4RQsPECTdM", "", "Sire Records", ZKL, "CLEAN (Genius, 291 words)", ""),
    (S4, "Scratch Acid", "Mary Had a Little Drug Problem", "Berserker", "1986", "2:17", "4ULEdk2rIkY", "1034547", "Touch and Go", ZKA, "CLEAN (Genius, only 88 words posted; partial, confirm by ear)", "Texas punk slot. Lapsed favorite, last aired 2022."),
    (S4, "Sheer Mag", "Need to Feel Your Love", "Need to Feel Your Love", "2017", "4:02", "Gf8M0ne7Ipc", "1113680", "Wilsun Rc", ZKA, "CLEAN (Genius, 238 words)", ""),
    (S4, "Wire", "Outdoor Miner", "Chairs Missing", "1978", "2:55", "TOZ1B5ZwK9I", "94160", "Emi (Local)", ZKA, "CLEAN (Genius, 212 words)", "Post-punk bridge to Set 5."),
    (S5, "Tom Waits", "Eggs and Sausage (In a Cadillac with Susan Michelson)", "Nighthawks at the Diner", "1975", "4:19", "lRTeR2c-bzA", "", "Asylum Records", ZKL, "CLEAN (Genius, 285 words)", "Food pick."),
    (S5, "Dee Dee Sharp", "Mashed Potato Time", "It's Mashed Potato Time", "1962", "2:31", "bt9sDztUGb0", "", "Cameo-Parkway (not in ZK label table)", WEB, "CLEAN (Genius, 326 words)", "Food pick."),
    (S5, "Jonathan Richman & The Modern Lovers", "Ice Cream Man", "Rock 'n' Roll with the Modern Lovers", "1977", "3:03", "KMVkV6pHCzI", "", "Beserkley (not in ZK label table)", WEB, "CLEAN (Genius, 306 words)", "Food pick."),
    (S5, "Guided By Voices", "I Am a Scientist", "Bee Thousand", "1994", "2:25", "Z25NpUSXLNo", "176374", "Matador Records", ZKA, "CLEAN (Genius, 191 words)", "Core artist."),
    (S5, "Queens of the Stone Age", "Go with the Flow", "Songs for the Deaf", "2002", "3:08", "ZkRtdXSSuC0", "670294", "Interscope Records", ZKA, "CLEAN (Genius, 185 words)", "Core artist."),
    (S5, "Built to Spill", "Carry the Zero", "Keep It Like a Secret", "1999", "5:44", "eZ7MFTBjJS8", "485962", "Warner Brothers (Modern)", ZKA, "CLEAN (Genius, 182 words)", "Long. Cull candidate."),
    (S5, "The Wedding Present", "Brassneck", "Bizarro", "1989", "4:53", "n8tS4UI2rNo", "981389", "Rca Records (Original Vinyl)", ZKA, "CLEAN (Genius, 291 words)", "Core artist."),
    (S5, "Arlo Guthrie", "Alice's Restaurant Massacree", "Alice's Restaurant", "1967", "18:37", "WaKIX6oaSLs", "", "Reprise Records", ZKL, "CLEAN (Genius, 2,819 words)", "Radio Thanksgiving tradition. 18:37, so optional: play it or cull it."),
]

EXCLUDED = [
    {"artist": "Anarchy in the U.K. (Sex Pistols)", "track": "Anarchy in the U.K.", "fcc": "piss x1 (\"pissed\", Outro; Genius)", "note": "Released Nov. 26, 1976. Add to FCC Edit Needed. Mention on air; play Pretty Vacant or an edit."},
    {"artist": "Pavement", "track": "Range Life", "fcc": "fuck x1 (Verse 3; Genius)"},
    {"artist": "Bodega", "track": "Name Escape", "fcc": "fuck x1 (Genius)"},
]


def secs(d):
    """Turn 'm:ss' into seconds."""
    m, s = d.split(":")
    return int(m) * 60 + int(s)


def main():
    # ---- plan JSON: one set per theme, tracks in air order ----
    sets = []
    for t in TRACKS:
        name = t[0]
        if not sets or sets[-1]["set"] != name:
            sets.append({"set": name, "tracks": []})
        sets[-1]["tracks"].append({
            "artist": t[1], "track": t[2], "album": t[3], "label": t[8],
            "label_source": t[9], "tag": t[7], "released": t[4], "duration": t[5],
            "videoId": t[6], "fcc_status": "CLEAN", "fcc_note": t[10], "why": t[11],
            "priority": "R", "source": "specialty/thanksgiving",
        })
    total = sum(secs(t[5]) for t in TRACKS)
    plan = {
        "show_date": "2026-11-26",
        "theme": "Thanksgiving",
        "name": "DJ Stace library show working",
        "note": ("Thanksgiving special. Built Oct. 15, 2026 by kzsu-monthly-specialty (six weeks out) from "
                 "outputs/specialty/thanksgiving-2026.md. YTM suggestion playlist PLayCr-iEi4UA, "
                 f"{len(TRACKS)} tracks, {total // 3600}:{(total % 3600) // 60:02d}:{total % 60:02d} "
                 "(2:35 without Alice's Restaurant). Still to fold in at the Nov. 12 refresh: new releases "
                 "from Nov. 12 to Nov. 26, Bay Area shows, Thanksgiving-week Today in Music, the Thursday "
                 "Triple Shot pick and the ticket giveaway."),
        "specialty_playlist": {"id": "PLayCr-iEi4UA", "tracks": len(TRACKS)},
        "today_in_music": {
            "nov_26": [
                "1976: Sex Pistols release \"Anarchy in the U.K.\" (EMI), 50 years ago.",
                "1939: Tina Turner born.",
                "1945: John McVie (Fleetwood Mac) born.",
                "1967: John Stirratt (Wilco) born.",
                "1968: Cream play their farewell concert at Royal Albert Hall.",
                "1973: New York Dolls play their first UK show.",
            ],
            "nov_25": ["1976: The Band's Last Waltz at Winterland, San Francisco, on Thanksgiving night (50th anniversary)."],
            "source": "thisdayinmusic.com; Last Waltz date from the film and album notes",
        },
        "excluded_fcc": EXCLUDED,
        "sets": sets,
    }
    out = ROOT / "data" / "recon" / "2026-11-26"
    out.mkdir(parents=True, exist_ok=True)
    (out / "working_playlist.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n")

    # ---- markdown notes ----
    L = []
    L.append("# Library Specialty: Thanksgiving 2026\n")
    L.append(f"Show: Thursday, Nov. 26, 2026. {len(TRACKS)} tracks, {total // 3600} hr {(total % 3600) // 60} min on YouTube Music "
             "(2 hr 35 min without Alice's Restaurant; target 2.5 hr, long tracks flagged so you can cull).\n")
    L.append("Playlist: https://music.youtube.com/playlist?list=PLayCr-iEi4UA\n")
    L.append("FCC screen: Genius lyric pages, counts only, no lyrics stored. LRCLIB cross-check on The Chain. "
             "Database lyrics can be wrong, so confirm by ear.\n")
    L.append("## Today in Music\n")
    L.append("- Nov. 26, 1976: Sex Pistols release \"Anarchy in the U.K.\" on EMI. 50th anniversary on show day.")
    L.append("- Nov. 25, 1976: The Band's The Last Waltz, Thanksgiving night at Winterland, San Francisco. 50th anniversary is the day before the show.")
    L.append("- Nov. 26 birthdays: Tina Turner (1939), John McVie of Fleetwood Mac (1945), John Stirratt of Wilco (1967).")
    L.append("- Nov. 26, 1968: Cream play their farewell concert at Royal Albert Hall.")
    L.append("- Nov. 26, 1973: New York Dolls play their first UK show.")
    L.append("- Source: [This Day in Music, Nov. 26](https://www.thisdayinmusic.com/on-this-day-in-music-november-26/)\n")
    L.append("## Left out for FCC\n")
    for e in EXCLUDED:
        L.append(f"- {e['artist'] if not e['artist'].startswith('Anarchy') else 'Sex Pistols'} \"{e['track']}\": {e['fcc']}." + (f" {e['note']}" if e.get('note') else ""))
    L.append("")
    L.append("## Still to fold in at the Nov. 12 refresh\n")
    L.append("- New releases from Nov. 12 to Nov. 26 that fit the theme (none known yet).")
    L.append("- Bay Area shows break, Thursday Triple Shot (one artist, three songs), ticket giveaway.")
    L.append("- Punk focus (from Oct. 15) is covered: Set 4 has 9 of 40 tracks.\n")
    n = 0
    cur = None
    for t in TRACKS:
        if t[0] != cur:
            cur = t[0]
            L.append(f"## {cur}\n")
            L.append("| # | Artist | Track | Year | Time | Label | Tag | FCC | Notes |")
            L.append("|---|---|---|---|---|---|---|---|---|")
        n += 1
        fcc = t[10].replace("|", "/")
        L.append(f"| {n} | {t[1]} | {t[2]} | {t[4]} | {t[5]} | {t[8]} | {t[7] or '-'} | {fcc} | {t[11]} |")
        nxt = TRACKS[n] if n < len(TRACKS) else None
        if nxt is None or nxt[0] != cur:
            L.append("")
    L.append("## Notes\n")
    L.append("- Labels marked \"web (verify)\" are not in the Zookeeper album record or label table. Check at the studio.")
    L.append("- Tags are filled only where the library holds the album that contains the track.")
    L.append("- Cull candidates by length: Alice's Restaurant (18:37), Mannish Boy (6:41), Don't Do It (6:20), Caravan (6:12), Helpless (5:54), Forever Young (5:52), Carry the Zero (5:44).")
    (ROOT / "outputs" / "specialty" / "thanksgiving-2026.md").write_text("\n".join(L) + "\n")
    print(len(TRACKS), "tracks", total, "seconds")


if __name__ == "__main__":
    main()
