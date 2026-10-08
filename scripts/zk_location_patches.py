#!/usr/bin/env python3
"""Write one PATCH body per album to change its location in Zookeeper.

Zookeeper's docs show PATCH as one album per request (PATCH api/v1/album/:id).
They do not document a bulk update, so this makes one small file per album.

Usage: python3 scripts/zk_location_patches.py
Output: outputs/zookeeper_upload/2026-10-08/5_location_pending_appr/PATCH_<tag>_<artist>_<album>.json
"""
import json
import re
from pathlib import Path

LOCATION = "Pending Appr"   # the exact location value Zookeeper uses
OUT = Path(__file__).resolve().parent.parent / "outputs" / "zookeeper_upload" / "2026-10-08" / "5_location_pending_appr"

# (tag, artist, album) as listed by Stace on Oct. 8, 2026.
ALBUMS = [
    ("1138339", "Felice Brothers, The", "Undress"),
    ("1138340", "Spoon", "Everything Hits At Once: The Best Of Spoon"),
    ("1138373", "Segall, Ty", "First Taste"),
    ("1138519", "Goon Sax, The", "We're Not Talking"),
    ("1138676", "Tinariwen", "Amadjar"),
    ("1138687", "She Keeps Bees", "Kinship"),
    ("1138698", "Furman, Ezra", "Twelve Nudes"),
    ("1139341", "Cave, Nick & The Bad Seeds", "Ghosteen"),
    ("1139352", "Black Pumas", "Black Pumas"),
    ("1139363", "Fruit Bats", "Gold Past Life"),
    ("1139408", "Bodega", "Shiny New Model"),
    ("1139431", "Wives", "So Removed"),
    ("1139453", "Seratones", "Power"),
    ("1139464", "L’epée", "Diabolique"),
    ("1139475", "Victoria, Adia", "Silences"),
    ("1139486", "A Giant Dog", "Neon Bible"),
    ("1139497", "Banhart, Devendra", "Ma"),
    ("1139903", "Desert Sessions", "Vol. 11 & 12"),
    ("1143818", "Segall, Ty", "Segall Smeagol"),
    ("1143829", "Garcia, Angélica", "Cha Cha Palace"),
    ("1148228", "Dumb", "Pray 4 Tomorrow"),
    ("1148239", "King Gizzard and the Lizard Wizard", "Changes"),
    ("1148240", "Panda Bear & Sonic Boom", "Reset"),
    ("1148251", "Mars Volta, The", "Mars Volta, The"),
    ("1148262", "Big Moon, The", "Here Is Everything"),
    ("1148284", "Gladie", "Don't Know What You're in Until You're Out"),
    ("1148295", "Backseat Lovers", "Waiting To Spill"),
    ("1148307", "Built to Spill", "When the Wind Forgets Your Name"),
    ("1148363", "Kepi Ghoulie", "Full Moon Forever"),
    ("1148374", "Moon, Suzi", "Dumb & in Luv"),
]

OUT.mkdir(parents=True, exist_ok=True)
slug = lambda t: re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
for tag, artist, album in ALBUMS:
    # Only the location changes; attributes left out of a PATCH stay unchanged.
    body = {"data": {"type": "album", "id": tag, "attributes": {"location": LOCATION}}}
    name = "PATCH_%s_%s_%s.json" % (tag, slug(artist), slug(album))
    (OUT / name).write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n")
print(len(ALBUMS), "files in", OUT)
