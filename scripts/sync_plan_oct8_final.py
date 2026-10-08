#!/usr/bin/env python3
"""Sync the Oct. 8, 2026 plan with Stace's Air Order (45 tracks) and the Zookeeper library.

What it does (for beginners):
  1. Loads data/recon/2026-10-08/working_playlist.json (the plan).
  2. Adds the two tracks Stace appended to Air Order: My Morning Jacket "Mahgeetah"
     and BODEGA "Slow Train".
  3. Fills in Zookeeper library tags and labels found by an API lookup on Oct. 8
     (artist, then album, then the track on the album record).
  4. Fixes Morphine "Cocoon": it is the 2026 title track of the new Partisan album,
     not a track on Cure for Pain (1993).
  5. Copies every track's playing time from the Air Order, since her list wins.

Run from the repo root:  python3 scripts/sync_plan_oct8_final.py
Then:                    python3 scripts/render_show_files.py 2026-10-08
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "data/recon/2026-10-08/working_playlist.json"
plan = json.loads(PLAN.read_text(encoding="utf-8"))

# Playing times from the Air Order page, keyed by YouTube Music videoId
DURATIONS = {
    "ElPskynxhTA": "1:53", "dfiR6XtYdzY": "2:17", "3PLNnRBXq4c": "5:13", "xoB-7eET8sw": "2:25",
    "bSbNyNFLQT8": "3:50", "wgqLAlFKtXA": "6:57", "NfQD1QiQ9o4": "5:52", "CHatn3_UxEU": "4:20",
    "FUFWkuMY6xM": "3:57", "CO5GaVJiRwo": "5:15", "pirkuE2Edgc": "4:59", "TR8_FmGDXQU": "5:14",
    "D757lJMBDk0": "3:43", "1c9YDg__yLc": "3:11", "q15sZK-8sPw": "4:13", "ItkZHJwmeN4": "4:19",
    "1ZX98VQcVl0": "3:32", "kIRXNnh6NdU": "3:07", "iGafqQemNUw": "3:06", "3VEaOLLkDi4": "3:11",
    "Kemyow8A4XY": "3:36", "4AEdJyRdtHI": "4:39", "UrSKhNkbsM8": "2:55", "PS4WMDhV2As": "2:22",
    "Ws3XVUlKXQ4": "5:00", "mUHfoV0ccEg": "5:28", "tsmxdk686wg": "3:09", "KRc6QLhw834": "4:43",
    "oRc4eohqlaM": "3:51", "7XhgcajHhcM": "3:29", "dXVE5NZl6G4": "3:30", "jTI5dX83NZc": "5:19",
    "Zsepy5ogQxU": "5:12", "uJY5H3Hala8": "6:15", "Bw6BlzTg0Rc": "3:54", "IRGdfyrVjlw": "2:49",
    "AyWKWcEfE-Y": "3:18", "bu6nzpkoFyo": "2:21", "W51Ik_1noH8": "3:57", "K07Yq4zGTcI": "3:32",
    "M1Zz7QWbS-w": "3:41", "aGTuvSf85-s": "4:41", "cZnaU3_Sr7U": "4:49",
    "2xbVokrLutc": "5:57", "HODdJZkPMIU": "3:52",
}

# Zookeeper library matches, by videoId: tag, plus album/label when the library record differs.
# Each album record was opened and the track confirmed on it (Oct. 8 API lookup).
ZK = {
    "bSbNyNFLQT8": {"tag": "1156474", "album": "Thetans", "label": "Handmade Records"},
    "CHatn3_UxEU": {"tag": "826860", "album": "Remain in Light"},
    "FUFWkuMY6xM": {"tag": "378727", "label": "Rykodisc"},
    "pirkuE2Edgc": {"tag": "1156508"},
    "TR8_FmGDXQU": {"tag": "719074", "label": "Jetset Records"},   # library copy is a 1991 compilation
    "D757lJMBDk0": {"tag": "395502", "label": "Creation Records"},
    "mUHfoV0ccEg": {"tag": "1135099", "label": "Mexican Summer"},
    "IRGdfyrVjlw": {"tag": "393926"},
    "bu6nzpkoFyo": {"tag": "697990", "album": "No Depression", "label": "Columbia Legacy"},
    "7XhgcajHhcM": {"tag": "1102420", "album": "Requiem"},
    "tsmxdk686wg": {"tag": "1156441"},
}

# Morphine "Cocoon" is the 2026 title track, not on Cure for Pain (1993). Not in the library yet.
MORPHINE = {
    "album": "Cocoon", "label": "Partisan Records", "tag": "", "released": "2026 single; album 2026-12-04",
    "label_source": "Partisan (Rolling Stone, Stereogum); not in the KZSU library",
    "why": "Carried over. Title track of the new album Cocoon (Partisan, Dec. 4, 2026), a newly mixed 1998 recording. "
           "An earlier version is on Sandbox: The Music of Mark Sandman (2004).",
}

NEW_TRACKS = [
    {"artist": "My Morning Jacket", "track": "Mahgeetah", "album": "It Still Moves", "label": "Ato Records",
     "label_source": "Zookeeper album 722281 (It Still Moves Deluxe Reissue), label 12950", "tag": "722281",
     "released": "2003", "type": "album track", "upcoming": "", "priority": "O",
     "why": "Added by DJ Stace (Air Order, seen Oct. 8). MMJ plays the Fillmore, S.F., Oct. 9, 10 and 11.",
     "fcc_status": "CLEAN", "fcc_note": "CLEAN (Genius, Oct. 8)", "source": "added_by_stace",
     "added_by": "DJ Stace", "videoId": "2xbVokrLutc", "duration": "5:57"},
    {"artist": "BODEGA", "track": "Slow Train", "album": "All Inside Aquarium", "label": "Chrysalis Records",
     "label_source": "web (Maximum Volume Music, Beatport); album not in the KZSU library yet", "tag": "",
     "released": "2026-10-09 (album); single Oct. 6", "type": "cover", "upcoming": "", "priority": "O",
     "why": "Added by DJ Stace (Air Order, seen Oct. 8). Cover of Bob Dylan's \"Slow Train\" (1979). Album out Fri. Oct. 9.",
     "fcc_status": "UNVERIFIED",
     "fcc_note": "UNVERIFIED: BODEGA's lyrics are not posted. Dylan's original is clean on Genius (Oct. 8). Listen first.",
     "source": "added_by_stace", "added_by": "DJ Stace", "videoId": "HODdJZkPMIU", "duration": "3:52"},
]

# ---- apply ------------------------------------------------------------------------------
closers = plan["sets"][-1]["tracks"]
have = {t["videoId"] for s in plan["sets"] for t in s["tracks"]}
for t in NEW_TRACKS:
    if t["videoId"] not in have:
        closers.append(t)

for s in plan["sets"]:
    for t in s["tracks"]:
        vid = t["videoId"]
        if vid in DURATIONS:
            t["duration"] = DURATIONS[vid]
        t.update(ZK.get(vid, {}))
        if vid == "Bw6BlzTg0Rc":
            t.update(MORPHINE)

n = sum(len(s["tracks"]) for s in plan["sets"])
plan["ytm_air_order"].update({"tracks": n, "built": "2026-10-08"})
plan["ytm_playlist"].update({"tracks": n, "built": "2026-10-08"})
plan["note"] += (" Oct. 8 midday sync: Stace appended My Morning Jacket Mahgeetah and BODEGA Slow Train to Air Order "
                 "(45 rows, Sex Pistols held out). Library tags matched for every track found; Morphine Cocoon corrected "
                 "to the 2026 title track.")
PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("plan now has", n, "tracks;", sum(1 for s in plan['sets'] for t in s['tracks'] if t.get('tag')), "with tags")
