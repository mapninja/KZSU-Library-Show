#!/usr/bin/env python3
"""
build_release_watchlist.py
==========================

Makes the "watchlist" that new-release research starts from:

    config/release_watchlist.json

The watchlist has two parts:

1. LABELS you return to. Pulled from your KZSU airplay (data/library_show.db),
   your KZSU reviews, and the label websites listed in sources.yml.
2. ARTISTS you care about. Pulled from config/taste_profile.json (airplay,
   YouTube Music plays and reviews combined).

HOW TO RUN (from the repository root):

    python scripts/build_release_watchlist.py

Beginner notes
--------------
* A "label key" is a simplified label name ("Matador Records" -> "matador").
  build_music_db.py already stores one in the `label_key` column, so
  "Sub Pop Records" and "Sub Pop" count as the same label.
* Major labels (Columbia, Warner, Atlantic...) release thousands of records
  that aren't your taste. We skip them as LABELS, but any artist you like who
  records for a major still shows up through the ARTIST list.
* Vanity labels (a label owned by one band, such as GBV Records) are skipped
  as labels for the same reason: the artist list already covers them.
"""

# ---------------------------------------------------------------------------
# Imports. All of these ship with Python.
# ---------------------------------------------------------------------------
import json          # read and write JSON files
import re            # pattern matching, used to read URLs out of sources.yml
import shutil        # copy files (SQLite can't open the DB on a mounted folder)
import sqlite3       # the built-in database engine
import tempfile      # make a temporary folder for the DB copy
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths. ROOT is the repository folder (one level above scripts/).
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "library_show.db"
PROFILE_PATH = ROOT / "config" / "taste_profile.json"
SOURCES_PATH = ROOT / "sources.yml"
OUT_PATH = ROOT / "config" / "release_watchlist.json"

# ---------------------------------------------------------------------------
# Rules for which labels make the list.
# Change these numbers to widen or narrow the net.
# ---------------------------------------------------------------------------
MIN_TOTAL_SPINS = 12      # aired at least this many times, ever
MIN_RECENT_SPINS = 3      # ...or at least this many times since RECENT_SINCE
RECENT_SINCE = "2024-01-01"
TOP_ARTISTS = 200         # how many artists from the taste profile to watch

# Label keys that are majors, catch-alls or one-band vanity labels.
# Their artists are still watched through the artist list.
SKIP_LABEL_KEYS = {
    # majors and major imprints
    "columbia", "warner bros", "warner brothers modern", "island", "atlantic",
    "atlantic modern", "interscope", "interscope modern", "geffen", "polydor",
    "a m", "rhino", "virgin", "virgin emi", "virgin modern", "epic",
    "epic modern", "emi", "capitol", "sire", "sire modern", "island modern",
    "island world", "elektra local", "polygram modern", "rca", "american",
    "motown", "30th century columbia", "columbia legacy", "bmg distribution",
    "mammoth", "chrysalis", "i r s", "blue horizon", "fuel 2000",
    # catch-alls
    "self release", "self", "unknown", "a",
    # vanity labels for a single artist
    "el marko", "gbv", "bad seed", "wilsun rc", "eodm", "the arcs",
    "contender", "sofaburn", "scopitones", "rifle bird", "first warning",
    "tomplicated", "marshall", "radicalis", "sidecho", "kglw",
}

# Home pages for labels, used by the research step.
# Keys are label keys; add new ones as you find them.
LABEL_URLS = {
    "matador": "https://matadorrecords.com/",
    "sub pop": "https://www.subpop.com/",
    "subpop": "https://www.subpop.com/",
    "merge": "https://www.mergerecords.com/",
    "drag city": "https://www.dragcity.com/",
    "nonesuch": "https://www.nonesuch.com/",
    "new west": "https://www.newwestrecords.com/",
    "4ad": "https://4ad.com/",
    "partisan": "https://partisanrecords.com/",
    "ato": "https://www.atorecords.com/",
    "domino company": "https://www.dominorecordco.com/",
    "domino": "https://www.dominorecordco.com/",
    "jagjaguwar": "https://jagjaguwar.com/",
    "touch and go": "https://www.touchandgorecords.com/",
    "anti": "https://anti.com/",
    "mom pop": "https://www.momandpopmusic.com/",
    "in the red": "https://intheredrecords.com/",
    "what s your rupture": "https://whatsyourrupture.com/",
    "dirty water": "https://www.dirtywaterrecords.com/",
    "rough trade": "https://www.roughtraderecords.com/",
    "beggars banquet": "https://www.beggars.com/",
    "secretly canadian": "https://secretlycanadian.com/",
    "saddle creek": "https://saddle-creek.com/",
    "polyvinyl": "https://www.polyvinylrecords.com/",
    "suicide squeeze": "https://suicidesqueeze.net/",
    "castle face": "https://castlefacerecords.com/",
    "fat possum": "https://www.fatpossum.com/",
    "innovative leisure": "https://innovativeleisure.net/",
    "light in the attic": "https://lightintheattic.net/",
    "dead oceans": "https://deadoceans.com/",
    "loma vista": "https://lomavistarecordings.com/",
    "city slang": "https://cityslang.com/",
    "xl": "https://www.xlrecordings.com/",
    "hardly art": "https://www.hardlyart.com/",
    "dbpm": "https://www.dbpmrecords.com/",
    "man s ruin": "https://www.mansruinrecords.com/",
    "mute": "https://mute.com/",
    "dine alone": "https://dinealonerecords.com/",
    "rykodisc": "https://www.rykodisc.com/",
    "captured tracks": "https://capturedtracks.com/",
    "fire": "https://www.firerecords.com/",
    "barsuk": "https://www.barsuk.com/",
    "yep roc": "https://www.yeproc.com/",
    "easy eye sound": "https://www.easyeyesound.com/",
    "third man": "https://thirdmanrecords.com/",
    "wharf cat": "https://wharfcatrecords.com/",
    "vagrant": "https://www.vagrant.com/",
    "shangri la": "https://www.shangri-la.com/",
    "thrill jockey": "https://thrilljockey.com/",
    "ipecac": "https://ipecac.com/",
    "burger": "https://burgerrecords.org/",
    "wichita": "https://www.wichita-recordings.com/",
    "carpark": "https://carparkrecords.com/",
    "bella union": "https://www.bellaunion.com/",
    "slovenly": "https://slovenly.com/",
    "young god": "https://younggodrecords.com/",
    "heavenly": "https://www.heavenlyrecordings.com/",
    "dirtnap": "https://www.dirtnaprecords.com/",
    "joyful noise": "https://www.joyfulnoiserecordings.com/",
    "darla": "https://www.darla.com/",
    "tiny engines": "https://tinyengines.net/",
    "norton": "https://nortonrecords.com/",
    "loosegroove": "https://loosegrooverecords.com/",
    "goner": "https://goner-records.com/",
    "clouds hill": "https://www.cloudshill.de/",
    "bloodshot": "https://www.bloodshotrecords.com/",
    "single lock": "https://singlelock.com/",
    "leaf label": "https://www.theleaflabel.com/",
    "dangerbird": "https://dangerbirdrecords.com/",
    "chain smoking": "https://chainsmokingrecords.com/",
    "sacred bones": "https://www.sacredbonesrecords.com/",
    "epitaph": "https://www.epitaph.com/",
    "thirty tigers": "https://www.thirtytigers.com/",
    "tardigrade": "https://tardigraderecords.com/",
    "trouble in mind": "https://troubleinmindrecs.com/",
    "ourness": "https://ourness.bandcamp.com/",
    "duophonic ultra high fs": "https://www.stereolab.co.uk/",
    "suck": "https://www.carolinerose.com/",
    "fire talk": "https://www.firetalkrecs.com/",
    "dirty hit": "https://dirtyhit.co.uk/",
    "warner": "https://www.warnerrecords.com/",
    "sire records": "https://www.sirerecords.com/",
    "no more heroes": "https://www.nomoreheroes.co.uk/",
}

# Labels in sources.yml that don't match a label key on their own.
# (URL fragment -> label key)
SOURCE_URL_TO_KEY = {
    "matadorrecords": "matador", "subpop": "sub pop", "newwestrecords": "new west",
    "nonesuch": "nonesuch", "dragcity": "drag city", "merge": "merge",
    "4ad": "4ad", "jagjaguwar": "jagjaguwar", "partisanrecords": "partisan",
    "ato-records": "ato", "dominorecordco": "domino company",
    "saddle-creek": "saddle creek", "suicidesqueeze": "suicide squeeze",
    "wichita-recordings": "wichita", "younggodrecords": "young god",
    "touchandgorecords": "touch and go", "intheredrecords": "in the red",
    "warnerrecords": "warner", "sirerecords": "sire records",
    "roughtrade": "rough trade", "xlrecordings": "xl",
    "secretlycanadian": "secretly canadian", "lightintheattic": "light in the attic",
    "mute": "mute", "momandpop": "mom pop", "nomoreheroes": "no more heroes",
}

# Extra labels that fit the style clusters in TASTE_PROFILE.md but have
# few logged spins (often because spins were logged as "self" or
# "unknown"). Research checks these too.
EXTRA_LABELS = {
    "exploding in sound": "https://explodinginsound.com/",
    "julia s war": "https://juliaswar.com/",
    "perennial": "https://perennialrecords.bandcamp.com/",
    "k": "https://www.krecs.com/",
    "ba da bing": "https://badabingrecords.com/",
    "spacebomb": "https://spacebombrecords.com/",
    "mint": "https://www.mintrecs.com/",
    "stargazer": "https://stargazerrecords.com/",
    "fiction": "https://www.fictionrecords.co.uk/",
    "speedy wunderground": "https://www.speedywunderground.co.uk/",
    "kartel": "https://kartelmusicgroup.com/",
    "big scary monsters": "https://bsmrocks.com/",
    "memphis industries": "https://memphis-industries.com/",
    "bayonet": "https://www.bayonetrecords.com/",
    "numero group": "https://numerogroup.com/",
    "daptone": "https://daptonerecords.com/",
    "big crown": "https://bigcrownrecords.com/",
    "riding easy": "https://ridingeasyrecords.com/",
    "heavy psych sounds": "https://www.heavypsychsounds.com/",
    "god unknown": "https://www.godunknownrecords.co.uk/",
    "rocket recordings": "https://www.rocketrecordings.com/",
    "mexican summer": "https://mexicansummer.com/",
    "ghostly international": "https://ghostly.com/",
    "sacred bones": "https://www.sacredbonesrecords.com/",
    "sinderlyn": "https://sinderlyn.com/",
    "full time hobby": "https://fulltimehobby.co.uk/",
    "pias": "https://www.pias.com/",
    "dead oceans": "https://deadoceans.com/",
    "anti": "https://anti.com/",
    "bandcamp self release": "https://bandcamp.com/discover/rock?s=new",
}


def open_db_copy(db_path: Path) -> sqlite3.Connection:
    """SQLite can fail on the mounted folder, so work on a temp copy."""
    tmp = Path(tempfile.mkdtemp()) / "library_show.db"
    shutil.copy(db_path, tmp)
    return sqlite3.connect(tmp)


def labels_from_airplay(con: sqlite3.Connection) -> dict:
    """Return {label_key: stats} for labels you've aired enough."""
    sql = """
        SELECT label_key,
               MAX(label)                              AS label,
               COUNT(*)                                AS spins,
               COUNT(DISTINCT artist_key)              AS artists,
               MAX(date)                               AS last_spin,
               SUM(date >= ?)                          AS recent_spins,
               GROUP_CONCAT(DISTINCT artist)           AS artist_list
        FROM v_airplay
        WHERE label_key <> ''
        GROUP BY label_key
    """
    out = {}
    for key, label, spins, n_art, last, recent, artists in con.execute(sql, (RECENT_SINCE,)):
        if key in SKIP_LABEL_KEYS:
            continue
        if spins >= MIN_TOTAL_SPINS or recent >= MIN_RECENT_SPINS:
            # Top 8 artists on the label, by spin count, as a hint for research.
            top = [a for (a,) in con.execute(
                "SELECT artist FROM v_airplay WHERE label_key=? "
                "GROUP BY artist_key ORDER BY COUNT(*) DESC LIMIT 8", (key,))]
            out[key] = {
                "label": label, "spins": spins, "artists": n_art,
                "last_spin": last, "recent_spins": recent,
                "top_artists": top, "sources": ["airplay"],
            }
    return out


def labels_from_reviews(con: sqlite3.Connection) -> dict:
    """Labels of albums you reviewed for KZSU."""
    rows = con.execute(
        "SELECT label_key, MAX(label), COUNT(*) FROM kzsu_reviews "
        "WHERE label_key <> '' GROUP BY label_key").fetchall()
    return {k: {"label": l, "reviews": n} for k, l, n in rows if k not in SKIP_LABEL_KEYS}


def labels_from_sources_yml() -> set:
    """Label keys for every label URL listed in sources.yml."""
    text = SOURCES_PATH.read_text()
    keys = set()
    for url in re.findall(r"https?://\S+", text):
        for fragment, key in SOURCE_URL_TO_KEY.items():
            if fragment in url:
                keys.add(key)
    return keys


def main() -> None:
    con = open_db_copy(DB_PATH)
    labels = labels_from_airplay(con)

    # Merge in review labels (adds new labels or tags existing ones).
    for key, info in labels_from_reviews(con).items():
        entry = labels.setdefault(key, {"label": info["label"], "spins": 0, "sources": []})
        entry["reviews"] = info["reviews"]
        entry["sources"].append("reviews")

    # Merge in sources.yml labels.
    for key in labels_from_sources_yml():
        entry = labels.setdefault(key, {"label": key.title(), "spins": 0, "sources": []})
        entry["sources"].append("sources.yml")

    # Merge in style-fit extras.
    for key, url in EXTRA_LABELS.items():
        entry = labels.setdefault(key, {"label": key.title(), "spins": 0, "sources": []})
        entry["sources"].append("style fit")
        LABEL_URLS.setdefault(key, url)

    # "Sub Pop" appears twice ("sub pop" and "subpop"); fold the second in.
    if "subpop" in labels and "sub pop" in labels:
        labels["sub pop"]["spins"] += labels.pop("subpop")["spins"]
    if "domino" in labels and "domino company" in labels:
        labels["domino company"]["spins"] += labels.pop("domino")["spins"]

    # Add URLs and a priority tier.
    #   Tier 1: 50+ spins or 10+ spins since 2024  -> check every week
    #   Tier 2: everything else                     -> check every month
    for key, entry in labels.items():
        entry["url"] = LABEL_URLS.get(key, "")
        big = entry.get("spins", 0) >= 50 or entry.get("recent_spins", 0) >= 10
        entry["tier"] = 1 if big else 2

    # Artists: top N by taste score.
    profile = json.loads(PROFILE_PATH.read_text())
    artists = [
        {k: a.get(k) for k in ("artist", "key", "score", "shows", "shows_12mo",
                               "ytm_plays", "ytm_plays_90d", "last_spin")}
        for a in profile["artists"][:TOP_ARTISTS]
    ]

    watchlist = {
        "generated": date.today().isoformat(),
        "rules": {
            "min_total_spins": MIN_TOTAL_SPINS,
            "min_recent_spins": MIN_RECENT_SPINS,
            "recent_since": RECENT_SINCE,
            "top_artists": TOP_ARTISTS,
        },
        "labels": dict(sorted(labels.items(), key=lambda kv: -kv[1].get("spins", 0))),
        "artists": artists,
    }
    OUT_PATH.write_text(json.dumps(watchlist, indent=1, ensure_ascii=False))
    print(f"Wrote {OUT_PATH}: {len(labels)} labels, {len(artists)} artists")


if __name__ == "__main__":
    main()
