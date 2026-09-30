#!/usr/bin/env python3
"""
build_music_db.py
=================

Builds ONE consolidated SQLite database of DJ Stace's music activity:

    data/library_show.db

It combines four sources:

1. KZSU Zookeeper playlists  (what you actually played on air)
2. KZSU Zookeeper reviews    (albums you reviewed for the station library)
3. Google Takeout YouTube activity (data/MyActivity.html: what you listen to)
4. (optional) any older CSV exports in notebooks/outputs/

It also writes a compact JSON file used by the HTML dashboard:

    outputs/dashboard/dashboard_data.json

HOW TO RUN (from the repository root):

    python scripts/build_music_db.py            # use saved raw files
    python scripts/build_music_db.py --refresh  # re-download from the KZSU API first

Beginner notes
--------------
* "Raw" files are saved exactly as the API returned them. We never edit them.
  That way we can always rebuild the database from scratch.
* SQLite is a database stored in a single file. Python ships with the
  `sqlite3` module, so no server or install is required.
* A "key" (for example `artist_key`) is a simplified version of a name that
  lets us match "The Walkmen" with "Walkmen, The" or "walkmen".
"""

# ---------------------------------------------------------------------------
# Imports: every library used below. All ship with Python except `requests`,
# which is only needed when you pass --refresh.
# ---------------------------------------------------------------------------
import argparse          # reads command-line flags such as --refresh
import csv               # reads and writes CSV files
import html              # turns "&amp;" back into "&"
import json              # reads and writes JSON files
import os                # reads environment variables
import re                # "regular expressions" for pattern matching in text
import sqlite3           # the built-in database engine
import time              # lets us pause between API calls (polite to servers)
import unicodedata       # strips accents: "Gutiérrez" -> "Gutierrez"
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path  # safer, cross-platform file paths

# ---------------------------------------------------------------------------
# Paths. ROOT is the repository folder (one level above scripts/).
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW_KZSU = ROOT / "data" / "raw" / "kzsu"
PROCESSED = ROOT / "data" / "processed"
DB_PATH = ROOT / "data" / "library_show.db"
TAKEOUT_HTML = ROOT / "data" / "MyActivity.html"
DASH_DIR = ROOT / "outputs" / "dashboard"

# ---------------------------------------------------------------------------
# KZSU API settings. The key is read from an environment variable first.
# Tip: put `export KZSU_LIBRARY_API_KEY=...` in a .env file that git ignores.
# ---------------------------------------------------------------------------
KZSU_API_KEY = os.getenv("KZSU_LIBRARY_API_KEY", "")
KZSU_V1 = "https://zookeeper.stanford.edu/api/v1/"
DJ_ID = "1428"          # DJ Stace's airname id in Zookeeper
DJ_NAME = "DJ Stace"


# ===========================================================================
# 1. Helper functions
# ===========================================================================
def artist_key(name: str) -> str:
    """Return a simplified matching key for an artist name.

    Examples:
        "Walkmen, The"            -> "walkmen"
        "The Walkmen"             -> "walkmen"
        "Segall, Ty"              -> "ty segall"
        "Hermanos Gutiérrez"      -> "hermanos gutierrez"
        "Father John Misty - Topic" -> "father john misty"
    """
    if not name:
        return ""
    s = name.strip()
    # YouTube auto-generated channels end with " - Topic"; official ones may say VEVO.
    s = re.sub(r"\s*-\s*Topic$", "", s)
    s = re.sub(r"VEVO$", "", s)
    # Library style "Last, First" -> "First Last" (only when there is exactly one comma
    # and the part after the comma is short, e.g. "Segall, Ty" or "Walkmen, The").
    if s.count(",") == 1:
        last, first = [p.strip() for p in s.split(",")]
        if 0 < len(first.split()) <= 3 and "&" not in first:
            s = f"{first} {last}"
    # Remove accents, lowercase, unify "and"/"&".
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().replace("&", " and ")
    s = re.sub(r"^the\s+", "", s)            # drop a leading "the"
    s = re.sub(r"[^a-z0-9 ]+", " ", s)       # punctuation -> space
    return re.sub(r"\s+", " ", s).strip()    # collapse repeated spaces


def primary_artist(name: str) -> str:
    """For 'A, B' or 'A feat. B' credits, keep the first artist (A)."""
    if not name:
        return ""
    s = re.split(r"\s+(?:feat\.?|ft\.?|featuring|with|x)\s+", name, flags=re.I)[0]
    # A comma list like "Hamilton Leithauser, Rostam" -> "Hamilton Leithauser".
    # Library-style "Segall, Ty" is handled by artist_key, so only split when
    # both sides have 2+ words or the right side is a known multi-artist marker.
    parts = [p.strip() for p in s.split(",")]
    if len(parts) > 1 and len(parts[0].split()) >= 2:
        return parts[0]
    return s.strip()


def label_key(name: str) -> str:
    """Simplify label names so 'Sub Pop Records' and 'Sub Pop' match."""
    if not name:
        return ""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(records?|recordings?|recording company|music|ltd|inc|llc|co)\b\.?", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def looks_like_duration(text: str) -> bool:
    """True for strings like '3:37'. Used to catch labels that are really durations."""
    return bool(re.fullmatch(r"\d{1,2}:\d{2}", (text or "").strip()))


# ===========================================================================
# 2. Download raw data from the KZSU API (only with --refresh)
# ===========================================================================
def fetch_paged(endpoint: str, params: dict) -> tuple[list, list]:
    """Download every page of a Zookeeper JSON:API list endpoint.

    Returns (data_items, included_items). Zookeeper uses "offset" paging:
    we ask for 100 items, then the next 100, until no `next` link remains.
    """
    import requests  # imported here so the script runs without it when not refreshing

    headers = {"X-APIKEY": KZSU_API_KEY, "Accept": "application/vnd.api+json"}
    data, included, offset = [], [], 0
    while True:
        page_params = dict(params, **{"page[size]": 100, "page[offset]": offset})
        resp = requests.get(KZSU_V1 + endpoint, headers=headers, params=page_params, timeout=90)
        resp.raise_for_status()                 # stop with an error on HTTP 4xx/5xx
        payload = resp.json()
        items = payload.get("data", [])
        if isinstance(items, dict):             # a single result comes back as a dict
            items = [items]
        data.extend(items)
        included.extend(payload.get("included", []))
        if not payload.get("links", {}).get("next") or not items:
            break
        offset += len(items)
        time.sleep(0.5)                         # be polite to the station server
    return data, included


def refresh_raw_kzsu() -> None:
    """Save fresh copies of playlists and reviews to data/raw/kzsu/."""
    if not KZSU_API_KEY:
        raise SystemExit("Set KZSU_LIBRARY_API_KEY before using --refresh.")
    RAW_KZSU.mkdir(parents=True, exist_ok=True)
    playlists, _ = fetch_paged("playlist", {"filter[airname.id]": DJ_ID})
    (RAW_KZSU / "playlists_dj1428_raw.json").write_text(json.dumps(playlists))
    albums, included = fetch_paged("album", {"filter[reviews.airname.id]": DJ_ID, "include": "reviews"})
    (RAW_KZSU / "reviews_dj1428_raw.json").write_text(json.dumps({"albums": albums, "included": included}))
    print(f"Refreshed: {len(playlists)} playlists, {len(albums)} reviewed albums")


# ===========================================================================
# 3. Parse each source into plain Python lists of dictionaries ("rows")
# ===========================================================================
def parse_kzsu_playlists() -> tuple[list, list]:
    """Turn raw playlist JSON into `shows` rows and `spins` rows."""
    raw = json.loads((RAW_KZSU / "playlists_dj1428_raw.json").read_text())
    shows, spins = [], []
    for pl in raw:
        a = pl["attributes"]
        events = a.get("events") or []
        is_rebroadcast = bool(a.get("rebroadcast")) or "rebroadcast" in (a.get("name") or "").lower()
        shows.append({
            "playlist_id": int(pl["id"]),
            "date": a.get("date"),
            "time": a.get("time"),
            "name": a.get("name"),
            "rebroadcast": int(is_rebroadcast),
            "n_spins": sum(1 for e in events if e.get("type") == "spin"),
            "n_breaks": sum(1 for e in events if e.get("type") == "break"),
            "n_comments": sum(1 for e in events if e.get("type") == "comment"),
            "zookeeper_url": f"https://zookeeper.stanford.edu/?action=viewListById&playlist={pl['id']}",
        })
        seq = 0
        for e in events:
            if e.get("type") != "spin":
                continue                        # skip breaks, comments, legal IDs
            seq += 1
            label = e.get("label") or ""
            label_bad = looks_like_duration(label)  # the 2026-09-24 import bug
            spins.append({
                "playlist_id": int(pl["id"]),
                "date": a.get("date"),
                "seq": seq,
                "created": e.get("created"),
                "artist": e.get("artist") or "",
                "track": e.get("track") or "",
                "album": e.get("album") or "",
                "label": "" if label_bad else label,
                "label_error": label if label_bad else "",
                "rebroadcast": int(is_rebroadcast),
            })
    return shows, spins


def parse_star_rating(text: str):
    """Pull a 1-5 rating out of phrases like 'Rated with *****' or '4.5/5'."""
    m = re.search(r"Rated with\s*(\*+)", text)
    if m:
        return len(m.group(1))
    m = re.search(r"(\d(?:\.\d)?)\s*/\s*5", text)
    return float(m.group(1)) if m else None


def parse_kzsu_reviews() -> list:
    """Turn raw review JSON into `reviews` rows with parsed fields."""
    raw = json.loads((RAW_KZSU / "reviews_dj1428_raw.json").read_text())
    by_id = {r["id"]: r for r in raw["included"] if r["type"] == "review"}
    rows = []
    for alb in raw["albums"]:
        at = alb["attributes"]
        rel = alb.get("relationships", {})
        label = rel.get("label", {}).get("meta", {}).get("name", "")
        for ref in rel.get("reviews", {}).get("data", []):
            rv = by_id.get(ref["id"])
            if not rv or rv["attributes"].get("airname") != DJ_NAME:
                continue                        # albums can have reviews by other DJs
            text = rv["attributes"].get("review") or ""
            fcc = re.search(r"FCCs?\s*:?\s*([^\r\n]*)", text)
            riyl = re.search(r"RIYL\s*:?\s*([^\r\n]*)", text)
            rows.append({
                "review_id": int(rv["id"]),
                "album_tag": int(alb["id"]),
                "artist": at.get("artist", ""),
                "album": at.get("album", ""),
                "label": label,
                "category": at.get("category", ""),
                "review_date": rv["attributes"].get("date"),
                "fcc_note": fcc.group(1).strip() if fcc else "",
                "riyl": riyl.group(1).strip() if riyl else "",
                "rating": parse_star_rating(text),
                "review_text": text,
                "zookeeper_url": f"https://zookeeper.stanford.edu/?s=byAlbumKey&n={alb['id']}&action=search",
            })
    return rows


def parse_takeout() -> list:
    """Parse Google Takeout MyActivity.html (YouTube + YouTube Music).

    The file is one giant HTML page where each activity looks like:
        <p class="mdl-typography--title">YouTube Music<br></p> ...
        Watched <a href="...watch?v=ID">Title</a><br><a href="...">Artist - Topic</a><br>
        Sep 22, 2026, 2:54:48 PM PDT<br>
    We cache the parsed result as CSV because the HTML is ~80 MB.
    """
    cache = PROCESSED / "youtube_takeout_activity.csv"
    if cache.exists() and cache.stat().st_mtime > TAKEOUT_HTML.stat().st_mtime:
        with cache.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    text = TAKEOUT_HTML.read_text(encoding="utf-8")
    cell_pat = re.compile(r'<p class="mdl-typography--title">(.*?)<br></p>.*?mdl-typography--body-1">(.*?)</div>', re.S)
    rows = []
    for cell in text.split('<div class="outer-cell')[1:]:
        m = cell_pat.search(cell)
        if not m:
            continue
        product, body = m.group(1), m.group(2)
        parts = body.split("<br>")
        am = re.match(r"\s*(\w[\w ]*?)\s*<a href=\"([^\"]+)\">(.*?)</a>", parts[0])
        action, url, title = (am.group(1), am.group(2), html.unescape(am.group(3))) if am else (re.sub("<.*?>", "", parts[0]).strip(), "", "")
        channel, ts = "", ""
        for p in parts[1:]:
            cm = re.match(r'<a href="([^"]+)">(.*?)</a>', p)
            if cm and not channel:
                channel = html.unescape(cm.group(2))
            elif re.match(r"[A-Z][a-z]{2} \d", p.strip()):
                ts = p.strip()
        vid = re.search(r"v=([\w-]{11})", url)
        try:
            clean = re.sub(r" [A-Z]{2,4}$", "", ts.replace(" ", " "))
            played = datetime.strptime(clean, "%b %d, %Y, %I:%M:%S %p").isoformat()
        except ValueError:
            played = ""
        rows.append({"product": product, "action": action, "title": title, "url": url,
                     "video_id": vid.group(1) if vid else "", "channel": channel,
                     "channel_url": "", "timestamp_raw": ts, "played_at": played})
    PROCESSED.mkdir(parents=True, exist_ok=True)
    with cache.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows


# ===========================================================================
# 4. Write everything into SQLite
# ===========================================================================
SCHEMA = """
DROP TABLE IF EXISTS kzsu_shows;
DROP TABLE IF EXISTS kzsu_spins;
DROP TABLE IF EXISTS kzsu_reviews;
DROP TABLE IF EXISTS yt_activity;

-- One row per KZSU playlist (show).
CREATE TABLE kzsu_shows (
    playlist_id INTEGER PRIMARY KEY, date TEXT, time TEXT, name TEXT,
    rebroadcast INTEGER, n_spins INTEGER, n_breaks INTEGER, n_comments INTEGER,
    zookeeper_url TEXT
);

-- One row per track played on air.
CREATE TABLE kzsu_spins (
    playlist_id INTEGER, date TEXT, seq INTEGER, created TEXT,
    artist TEXT, track TEXT, album TEXT, label TEXT, label_error TEXT,
    rebroadcast INTEGER, artist_key TEXT, label_key TEXT
);

-- One row per album review written by DJ Stace.
CREATE TABLE kzsu_reviews (
    review_id INTEGER PRIMARY KEY, album_tag INTEGER, artist TEXT, album TEXT,
    label TEXT, category TEXT, review_date TEXT, fcc_note TEXT, riyl TEXT,
    rating REAL, review_text TEXT, zookeeper_url TEXT, artist_key TEXT, label_key TEXT
);

-- One row per YouTube / YouTube Music action (watch, search, like...).
CREATE TABLE yt_activity (
    product TEXT, action TEXT, title TEXT, url TEXT, video_id TEXT,
    channel TEXT, artist TEXT, artist_key TEXT, played_at TEXT
);
"""

# Views are saved queries. They make the dashboard and notebooks simpler.
VIEWS = """
DROP VIEW IF EXISTS v_airplay;
CREATE VIEW v_airplay AS                      -- original broadcasts only
    SELECT * FROM kzsu_spins WHERE rebroadcast = 0;

DROP VIEW IF EXISTS v_ytm_plays;
CREATE VIEW v_ytm_plays AS                    -- songs played in YouTube Music
    SELECT * FROM yt_activity WHERE product = 'YouTube Music' AND action = 'Watched';

DROP VIEW IF EXISTS v_artist_summary;
CREATE VIEW v_artist_summary AS               -- one row per artist across all sources
    WITH air AS (
        SELECT artist_key, COUNT(*) AS spins, COUNT(DISTINCT playlist_id) AS shows,
               MIN(date) AS first_spin, MAX(date) AS last_spin, MAX(artist) AS artist
        FROM v_airplay GROUP BY artist_key),
    ytm AS (
        SELECT artist_key, COUNT(*) AS ytm_plays, MAX(played_at) AS last_ytm, MAX(artist) AS artist
        FROM v_ytm_plays WHERE artist_key <> '' GROUP BY artist_key),
    rev AS (
        SELECT artist_key, COUNT(*) AS reviews FROM kzsu_reviews GROUP BY artist_key),
    keys AS (SELECT artist_key FROM air UNION SELECT artist_key FROM ytm UNION SELECT artist_key FROM rev)
    SELECT k.artist_key, COALESCE(air.artist, ytm.artist) AS artist,
           COALESCE(air.spins, 0) AS spins, COALESCE(air.shows, 0) AS shows,
           air.first_spin, air.last_spin,
           COALESCE(ytm.ytm_plays, 0) AS ytm_plays, ytm.last_ytm,
           COALESCE(rev.reviews, 0) AS reviews
    FROM keys k LEFT JOIN air USING (artist_key) LEFT JOIN ytm USING (artist_key)
    LEFT JOIN rev USING (artist_key);
"""


def ytm_artist_from_channel(channel: str) -> str:
    """'Palace - Topic' -> 'Palace'; 'SpoonVEVO' -> 'Spoon'. Other channels kept as-is."""
    s = re.sub(r"\s*-\s*Topic$", "", channel or "").strip()
    return re.sub(r"\s*(VEVO|Official)$", "", s).strip()


def build_database(shows, spins, reviews, yt_rows) -> None:
    # We build the database in a temporary folder, then copy it into data/.
    # This avoids "disk I/O error" on synced or network folders (iCloud, Dropbox,
    # mounted drives) where SQLite's lock files can misbehave.
    import shutil, tempfile
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_db = Path(tempfile.mkdtemp()) / "library_show.db"
    con = sqlite3.connect(tmp_db)
    con.executescript(SCHEMA)

    con.executemany("INSERT INTO kzsu_shows VALUES (:playlist_id,:date,:time,:name,:rebroadcast,:n_spins,:n_breaks,:n_comments,:zookeeper_url)", shows)

    for s in spins:
        s["artist_key"] = artist_key(primary_artist(s["artist"]))
        s["label_key"] = label_key(s["label"])
    con.executemany("INSERT INTO kzsu_spins VALUES (:playlist_id,:date,:seq,:created,:artist,:track,:album,:label,:label_error,:rebroadcast,:artist_key,:label_key)", spins)

    for r in reviews:
        r["artist_key"] = artist_key(r["artist"])
        r["label_key"] = label_key(r["label"])
    con.executemany("INSERT INTO kzsu_reviews VALUES (:review_id,:album_tag,:artist,:album,:label,:category,:review_date,:fcc_note,:riyl,:rating,:review_text,:zookeeper_url,:artist_key,:label_key)", reviews)

    yt = []
    for r in yt_rows:
        art = ytm_artist_from_channel(r["channel"]) if r["product"] == "YouTube Music" else r["channel"]
        yt.append((r["product"], r["action"], r["title"], r["url"], r["video_id"], r["channel"],
                   art, artist_key(primary_artist(art)), r["played_at"]))
    con.executemany("INSERT INTO yt_activity VALUES (?,?,?,?,?,?,?,?,?)", yt)

    con.executescript(VIEWS)
    # Indexes make lookups by artist or date fast.
    con.executescript("""
        CREATE INDEX IF NOT EXISTS ix_spins_artist ON kzsu_spins(artist_key);
        CREATE INDEX IF NOT EXISTS ix_spins_date ON kzsu_spins(date);
        CREATE INDEX IF NOT EXISTS ix_yt_artist ON yt_activity(artist_key);
    """)
    con.commit()
    con.close()
    shutil.copyfile(tmp_db, DB_PATH)          # move the finished file into place


# ===========================================================================
# 5. Export a compact JSON for the dashboard
# ===========================================================================
def export_dashboard_json() -> None:
    # Open read-only ("mode=ro") so no lock files are written next to the DB.
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro&immutable=1", uri=True)
    con.row_factory = sqlite3.Row
    q = lambda sql: [dict(r) for r in con.execute(sql)]

    data = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "shows": q("SELECT playlist_id,date,time,name,rebroadcast,n_spins,zookeeper_url FROM kzsu_shows ORDER BY date"),
        # Compact spin list: [playlist_id, date, artist, track, album, label]
        "spins": [list(r.values()) for r in q("SELECT playlist_id,date,artist,track,album,label,artist_key FROM v_airplay ORDER BY date,seq")],
        "reviews": q("SELECT review_id,artist,album,label,review_date,fcc_note,riyl,rating,review_text,zookeeper_url FROM kzsu_reviews ORDER BY review_date DESC"),
        "artists": q("SELECT * FROM v_artist_summary WHERE spins+ytm_plays+reviews >= 3 ORDER BY spins*10+ytm_plays DESC LIMIT 1500"),
        "labels": q("""SELECT MAX(label) AS label, label_key, COUNT(*) AS spins, COUNT(DISTINCT artist_key) AS artists,
                       MIN(date) AS first, MAX(date) AS last FROM v_airplay WHERE label_key <> ''
                       GROUP BY label_key ORDER BY spins DESC LIMIT 300"""),
        "spins_by_year": q("SELECT substr(date,1,4) AS year, COUNT(*) AS spins, COUNT(DISTINCT playlist_id) AS shows FROM v_airplay GROUP BY year"),
        "ytm_by_month": q("SELECT substr(played_at,1,7) AS month, COUNT(*) AS plays FROM v_ytm_plays WHERE played_at >= '2020' GROUP BY month"),
        "ytm_by_hour": q("SELECT CAST(substr(played_at,12,2) AS INT) AS hour, COUNT(*) AS plays FROM v_ytm_plays GROUP BY hour"),
        "ytm_top_tracks": q("""SELECT artist, title, COUNT(*) AS plays, MAX(video_id) AS video_id, MAX(played_at) AS last
                              FROM v_ytm_plays WHERE artist <> '' GROUP BY artist_key, title ORDER BY plays DESC LIMIT 500"""),
        "ytm_recent_artists": q("""SELECT artist, COUNT(*) AS plays FROM v_ytm_plays
                                  WHERE played_at >= date('now','-90 day') AND artist <> ''
                                  GROUP BY artist_key ORDER BY plays DESC LIMIT 60"""),
        "yt_searches": q("""SELECT title AS query, COUNT(*) AS n, MAX(played_at) AS last FROM yt_activity
                           WHERE action = 'Searched for' GROUP BY lower(title) ORDER BY last DESC LIMIT 400"""),
    }
    con.close()
    DASH_DIR.mkdir(parents=True, exist_ok=True)
    (DASH_DIR / "dashboard_data.json").write_text(json.dumps(data, separators=(",", ":")))
    print(f"Dashboard data: {DASH_DIR / 'dashboard_data.json'}")


# ===========================================================================
# 6. Main program
# ===========================================================================
def main() -> None:
    parser = argparse.ArgumentParser(description="Build the DJ Stace music database")
    parser.add_argument("--refresh", action="store_true", help="re-download KZSU playlists and reviews")
    args = parser.parse_args()

    if args.refresh:
        refresh_raw_kzsu()

    shows, spins = parse_kzsu_playlists()
    reviews = parse_kzsu_reviews()
    yt_rows = parse_takeout()
    build_database(shows, spins, reviews, yt_rows)
    export_dashboard_json()

    # Print a short summary so you know it worked.
    bad_labels = sum(1 for s in spins if s["label_error"])
    print(f"Shows: {len(shows)}  Spins: {len(spins)}  Reviews: {len(reviews)}  YouTube rows: {len(yt_rows)}")
    if bad_labels:
        print(f"Warning: {bad_labels} spins have a duration in the label field (CSV column mismatch).")
    print(f"Database written to {DB_PATH}")


if __name__ == "__main__":
    main()
