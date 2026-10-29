#!/usr/bin/env python3
"""
final_update_2026-10-29.py
One-off Wednesday-night update for the Oct. 29, 2026 (Halloween) show.
Copy it as an example for later weeks. Do not rerun it on a new week's plan.

What it does, in plain steps:
  1. Reads the show plan (data/recon/2026-10-29/working_playlist.json).
  2. Fills labels, tags, albums and release years for DJ Stace's Air Order adds
     (Zookeeper API lookups run in a browser tab on Oct. 28; web sources for the rest).
  3. Adds the one new Air Order track found Oct. 28 (Coil) to Set 5.
  4. Fixes two stale mic-break lines and clears the "(verify)" on the Sabbath fact.
  5. Writes the "final" block (cull ticks, replace ticks, change list) back to the plan.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "data/recon/2026-10-29/working_playlist.json"
plan = json.loads(PLAN.read_text())

# ---- 1. Enrichment values, keyed by (artist, track prefix) -------------------------------
# label_source says where each value came from. Zookeeper wins over web values.
ZK_NOTE = "zookeeper (Oct. 28 API lookup)"
FIX = {
    ("The Sonics", "The Witch", "6C4YDg14Wxo"): dict(
        album="Maintaining My Cool", label="Norton Records", tag="1081730", released="1965",
        label_source="zookeeper album (The Witch single, Sonics, library)",
        source_url="Zookeeper album 1081730"),
    ("The Kills", "I Put a Spell on You", None): dict(
        album="I Put a Spell on You (single)", label="Domino Recording Company", tag="",
        released="2020 (recorded 2009)",
        label_source="zookeeper label table (Domino Recording Company); not in library; label per Domino news post",
        source_url="https://www.dominomusic.com/news/us/the-kills-share-unreleased-version-of-i-put-a-spell-on-you-from-2009-with-official-video-of-archive-footage"),
    ("Alien Sex Fiend", "Now I'm Feeling Zombiefied", None): dict(
        album="Alien Sex Fiend Halloween", label="Anagram Records (not in ZK)", tag="",
        released="1987 12-inch (verify)",
        label_source="discogs (not in Zookeeper label table; library holds other ASF albums)",
        source_url="https://www.discogs.com/release/466708-Alien-Sex-Fiend-Now-Im-Feeling-Zombiefied"),
    ("Talking Heads", "Psycho Killer", None): dict(
        album="Talking Heads: 77", label="Sire Records", tag="826769", released="1977",
        label_source="zookeeper album", source_url="Zookeeper album 826769"),
    ("Nick Cave and The Bad Seeds", "Up Jumped the Devil", None): dict(
        album="Tender Prey", label="Mute Records", tag="", released="1988",
        label_source="zookeeper label table (Mute Records); album not in library",
        source_url="Zookeeper label 2124"),
    ("The Rolling Stones", "Sympathy For The Devil", None): dict(
        album="Beggars Banquet", label="London Records", tag="871242", released="1968",
        label_source="zookeeper album (original LP; YTM plays the 50th Anniversary Edition)",
        source_url="Zookeeper album 871242"),
    ("Skinny Puppy", "Love", None): dict(
        album="Bites", label="Nettwerk Records", tag="", released="1985 (CD edition; verify)",
        label_source="zookeeper label table (Nettwerk Records); Bites not in library",
        source_url="https://en.wikipedia.org/wiki/Bites_(album)"),
    ("Andy Shauf", "Satan", None): dict(
        album="Satan / Jacob Rose (single)", label="Anti-", tag="", released="2022-02-07",
        label_source="zookeeper label table (Anti-); single not in library; date per Anti-, Bandcamp and Apple Music",
        source_url="https://www.anti.com/releases/satan-jacob-rose/"),
    ("Lera Lynn & Shovels & Rope", "Wolf Like Me", None): dict(
        label="Single Lock", tag="",
        label_source="zookeeper label table (Single Lock); album not in library; label per web (verify)"),
}

for s in plan["sets"]:
    for t in s["tracks"]:
        for (a, tr, vid), vals in FIX.items():
            if t["artist"] == a and t["track"].startswith(tr) and (vid is None or t.get("videoId") == vid):
                t.update(vals)
                t["zk_checked"] = "2026-10-28"

# ---- 2. New Air Order add: Coil (found in the Air Order on Oct. 28) ------------------------
coil = {
    "artist": "Coil", "track": "Where Even the Darkness Is Something to See",
    "album": "Love's Secret Domain", "label": "!K7 Records", "tag": "870689",
    "label_source": "zookeeper album (library copy is the !K7 issue; original 1991 Torso and Wax Trax!)",
    "released": "1991",
    "why": "Added to the Air Order by DJ Stace (Oct. 28). Industrial, didgeridoo-led; pairs with Skinny Puppy at the end of Set 5. Library tag is the !K7 issue of Love's Secret Domain.",
    "fcc_status": "UNVERIFIED",
    "fcc_note": "UNVERIFIED: no lyrics posted on LRCLIB or Genius; mostly instrumental with a sample. Listen first.",
    "priority": "O", "source": "added_by_stace", "added_by": "DJ Stace",
    "videoId": None, "duration": "3:05",
    "source_url": "https://www.discogs.com (Love's Secret Domain, Wax Trax! WAXCD 7143); https://archive.org/details/CoilLovesSecretDomain1991",
}
set5 = next(s for s in plan["sets"] if "Set 5" in s["set"])
if not any(t["artist"] == "Coil" for t in set5["tracks"]):
    i = next(i for i, t in enumerate(set5["tracks"]) if t["artist"] == "Skinny Puppy")
    set5["tracks"].insert(i + 1, coil)

# ---- 3. Mic-break and fact fixes ------------------------------------------------------------
mb = plan["mic_breaks"]
mb["anniversary"] = [
    ln.replace("Fake Names released Punk Ruins today (Oct. 23) on Epitaph.", "Fake Names released Punk Ruins Oct. 23 on Epitaph.")
      .replace("reunited on Letterman Oct. 30, 1998 (verify).", "reunited on Letterman Oct. 30, 1998 to play Paranoid.")
    for ln in mb["anniversary"]]
for s in plan["sets"]:
    for t in s["tracks"]:
        if t["artist"] == "Black Sabbath":
            t["why"] = t["why"].replace("Fits the Oct. 30, 1998 reunion fact (verify; thisdayinmusic only).",
                                        "Fits the Oct. 30, 1998 reunion on Letterman (confirmed: IMDb episode listing, Louder, Black Sabbath Online).")
plan["today_in_music"]["oct_30"] = [ln.replace("reunite on Letterman", "reunite on Letterman (confirmed, three sources)") if "Black Sabbath" in ln else ln
                                    for ln in plan["today_in_music"]["oct_30"]]

# ---- 4. Final block ------------------------------------------------------------------------
plan["final"] = {
    "built": "2026-10-28",
    "cull_ticks": [],
    "replace_ticks": [],
    "notes": ("Wed. Oct. 28 final. Notes Sheet (id 12my1phBCX00y-l3EefaD7Cy-AjbwjHNilARe7lx60Yw) read at 8 p.m.: no cull or replace ticks, no edited cells. "
              "Air Order (PLSosF7JAIkaM) read back: 52 tracks. One new add since the Oct. 27 sync: Coil, Where Even the Darkness Is Something to See (Air Order #45), placed in Set 5 after Skinny Puppy. "
              "Stace's other nine appended tracks (Air Order #43-52) stay in their sets. Both Sonics 'The Witch' versions kept (her call). "
              "Labels and tags filled from Zookeeper Oct. 28 for the ten added tracks; Alien Sex Fiend label is not in the Zookeeper label table. "
              "No ticket giveaway: no sheet row lists Stace with a give-by on or after Oct. 29."),
}
plan["ytm_air_order"]["tracks"] = 52
plan["ytm_air_order"]["verified"] += " | Oct. 28: read back 52 tracks; one new add (Coil, #45); no removals; not rewritten by Claude."

PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n")
n = sum(1 for s in plan["sets"] for t in s["tracks"] if t.get("priority") not in ("SKIP", "CUT"))
print("plan updated; airable tracks:", n)
