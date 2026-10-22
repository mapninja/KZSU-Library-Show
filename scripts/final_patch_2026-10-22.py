#!/usr/bin/env python3
"""
final_patch_2026-10-22.py
Wednesday final-script patch for the Oct. 22, 2026 show.
Fills labels and tags for tracks Stace added to the Air Order (Zookeeper first, then
Discogs/Wikipedia/media), fixes the Fujiya & Miyagi "(verify)" fields, refreshes talk
breaks, and stamps the plan's "final" block. Run from the repo root.
Beginner notes: the plan is a JSON file; we load it, change fields on specific tracks,
and save it again. Nothing is deleted.
"""
import json
from pathlib import Path

PLAN = Path("data/recon/2026-10-22/working_playlist.json")
plan = json.loads(PLAN.read_text(encoding="utf-8"))

# (artist, track) -> fields to set. label_source says where the label came from.
FIX = {
    ("Scratch Acid", "Greatest Gift"): dict(
        album="The Greatest Gift", label="Touch and Go", tag="1082955",
        released="1984 (EP; collected on the 1991 compilation)",
        label_source="zookeeper album 1082955 (compilation holding the 1984 S/T EP tracks)",
        source_url="https://en.wikipedia.org/wiki/Scratch_Acid_(EP)",
        label_note="Original 1984 EP label not confirmed; library copy is the Touch and Go compilation."),
    ("The Damned", "Nasty"): dict(
        label="Damned", tag="",
        released="1984-05-28 (B-side of Thanks for the Night)",
        label_source="wikipedia: Thanks for the Night, label 'Damned DAMNED 1'",
        source_url="https://en.wikipedia.org/wiki/Thanks_for_the_Night",
        zk_alt="Sessions of the Damned (Fuel Records, tag 576154) and Seasons of the Damned (Dutch East India Trading, tag 167767) hold the track; both are compilations.",
        label_note="Not the 1976-79 era: Nasty was recorded in 1984 for The Young Ones."),
    ("R.M.F.C.", "The Clue"): dict(
        label="Warttmann Inc.", tag="",
        released="2019-03-01 (Hive Vol. 2)",
        label_source="media: Bandcamp, Warttmann Inc. WART010 (single source; verify)",
        source_url="https://warttmanninc.bandcamp.com/track/the-clue"),
    ("Jozef Van Wissem & Jim Jarmusch", "Never Like You Said (feat. Courtney Barnett)"): dict(
        label="Sacred Bones Records", tag="",
        released="2026-11-06 (album; lead single out now)",
        label_source="zookeeper label table 17966; release facts from Stereogum and Consequence",
        source_url="https://stereogum.com/2510869/jozef-van-wissem-jim-jarmusch-announce-new-double-album-bocca-di-lupo-mouth-of-the-wolf-hear-never-like-you-said-feat-courtney-barnett/music"),
    ("Eagles Of Death Metal", "Careless Whisper"): dict(
        label="Universal", tag="",
        released="2019-06-07",
        label_source="media: Universal Music imprints (UMC, UMe); ZK label table has 'Universal' 8548",
        source_url="https://www.discogs.com/release/13717168-Eagles-Of-Death-Metal-Presents-Boots-Electric-Eagles-Of-Death-Metal-Presents-Boots-Electric-Performi"),
    ("Queens of the Stone Age", "Insignificant Other"): dict(
        label="Matador Records", tag="",
        released="2026-08-28 (single; album Perfecth out Oct. 30)",
        label_source="zookeeper label table 1952; Matador release page",
        source_url="https://matadorrecords.com/blogs/news/coming-october-30-queens-of-the-stone-age-perfecth"),
    ("Fujiya & Miyagi", "No Green Light"): dict(
        album="New Shiny Object", label="Impossible Objects of Desire", tag="",
        label_source="media: Under the Radar, Stereogum, Wikipedia (band's own label; two sources agree)",
        source_url="https://fujiyamiyagi.bandcamp.com/album/new-shiny-object-2"),
}
hit = set()
for s in plan["sets"]:
    for t in s["tracks"]:
        k = (t["artist"], t["track"])
        if k in FIX:
            t.update(FIX[k]); hit.add(k)
assert hit == set(FIX), set(FIX) - hit
# Short notes appended to the 'why' field so the script shows where each label came from
SUFFIX = {
    ("Scratch Acid", "Greatest Gift"): " Library copy is the Touch and Go compilation The Greatest Gift; original 1984 EP label not confirmed.",
    ("The Damned", "Nasty"): " Label from Wikipedia (band's own Damned label), not in Zookeeper. Recorded 1984 for The Young Ones; B-side of Thanks for the Night.",
    ("R.M.F.C.", "The Clue"): " Label from Bandcamp (single source), not in Zookeeper: verify.",
    ("Jozef Van Wissem & Jim Jarmusch", "Never Like You Said (feat. Courtney Barnett)"): " Double album Bocca di Lupo and Mouth of the Wolf out Nov. 6.",
    ("Eagles Of Death Metal", "Careless Whisper"): " Label from press listings (Universal group); verify. Cover of the George Michael song.",
    ("Queens of the Stone Age", "Insignificant Other"): " Second single from Perfecth, out Oct. 30 on Matador.",
    ("Fujiya & Miyagi", "No Green Light"): " Label is the band's own imprint, not in Zookeeper.",
}
for s_ in plan["sets"]:
    for t in s_["tracks"]:
        k = (t["artist"], t["track"])
        if k in SUFFIX and SUFFIX[k].strip() not in t.get("why", ""):
            t["why"] = (t.get("why", "") + SUFFIX[k]).strip()

# Use the live Air Order videoIds (YTM read Oct. 21) for four tracks the plan still had under older ids
LIVE_IDS = {("Fontaines D.C.", "Six Shot Morning"): "00krktruwsM", ("Fontaines D.C.", "Mimesis"): "zXyN6eZjlTg",
            ("Fontaines D.C.", "Happy For You"): "wOkBZA51Z9o", ("Cheekface", "No Fly Zone"): "RoeVGBKwnkU"}
for s_ in plan["sets"]:
    for t in s_["tracks"]:
        if (t["artist"], t["track"]) in LIVE_IDS:
            t["videoId"] = LIVE_IDS[(t["artist"], t["track"])]

# Talk-break fixes
mb = plan["mic_breaks"]
mb["after_texas_set"][0] = ("Scratch Acid formed in Austin. Greatest Gift is from their 1984 self-titled EP, collected on The Greatest Gift (Touch and Go, 1991). "
                            "David Yow sang for them, then fronted The Jesus Lizard. Monkey Trick is from Goat (Touch and Go, 1991).")
mb["after_fontaines"][1] = ("Two songs from it, Tongue (shit x10) and Japan (fuck x3, shit x3), stay off the air. "
                            "Their Europe and UK tour started in Lisbon on Oct. 21 (verify).")
mb["after_heavy_set"] = [
    "Last stretch is new and loud: Queens of the Stone Age, Insignificant Other, from Perfecth (Matador, out Oct. 30).",
    "Jozef Van Wissem and Jim Jarmusch, Bocca di Lupo and Mouth of the Wolf, Sacred Bones, Nov. 6. Courtney Barnett sings on Never Like You Said.",
    "Eagles of Death Metal cover Careless Whisper on Boots Electric Performing the Best Songs We Never Wrote (2019). Lambrini Girls, Cult of Celebrity, City Slang.",
]
plan["final"] = {
    "built": "2026-10-21",
    "cull_ticks": [], "replace_ticks": [],
    "air_order_edits": "none since the Oct. 20 sync (YTM read Oct. 21: 50 tracks, same order; four Fontaines D.C. and Cheekface videoIds differ from the snapshot only because the snapshot kept old ids)",
    "notes_sheet": "unmodified since Oct. 20 deploy (no ticks)",
    "enrichment": "Zookeeper API read Oct. 21 via API route; labels filled for 7 tracks (see label_source on each track)",
    "open_flags": [
        "Triple Shot has four Damned tracks (Nasty added by Stace). Confirm or cut one.",
        "Stace's four tail adds sit at the end of Set 9; placement is her call.",
        "No ticket giveaway placed: no sheet row lists Stace on or after Oct. 22.",
    ],
}
PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("patched", len(hit), "tracks")
