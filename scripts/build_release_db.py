#!/usr/bin/env python3
"""
build_release_db.py
===================

Builds the UPCOMING RELEASES database for The Library show.

Inputs
------
* data/releases/research/*.json    research files (one JSON list per file)
* data/releases/research/*.jsonl   research files (one JSON object per line)
* config/release_watchlist.json    labels + artists to watch
                                   (made by scripts/build_release_watchlist.py)
* config/taste_profile.json        artist scores (made by build_taste_profile.py)
* data/library_show.db             your KZSU airplay (made by build_music_db.py)
* data/releases/coverage.json      which labels were checked, and how

Outputs
-------
* data/library_show.db, table `upcoming_releases`   (one row per release)
* data/library_show.db, table `release_watch_labels` (the label watchlist)
* data/releases/upcoming_releases.csv               (same rows, for Excel)
* outputs/releases/upcoming_releases.md             (readable report with links)

HOW TO RUN (from the repository root), in this order:

    python scripts/build_music_db.py          # only if airplay changed
    python scripts/build_taste_profile.py     # only if airplay changed
    python scripts/build_release_watchlist.py
    python scripts/build_release_db.py

Re-run this script after build_music_db.py, because that script rebuilds the
database file from scratch and drops the release tables.

Beginner notes
--------------
* "Dedupe" means removing duplicates. Several research passes found the same
  album (for example, Bodega's record came up under the label AND the artist).
  We merge those into one row and keep every source.
* The "fit score" (0-100) estimates how likely a release is to suit the show.
  It is a starting point, not a verdict. Change the WEIGHTS below to tune it.
"""

# ---------------------------------------------------------------------------
# Imports. All ship with Python.
# ---------------------------------------------------------------------------
import csv
import json
import math
import re
import shutil
import sqlite3
import tempfile
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote_plus

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DIR = ROOT / "data" / "releases" / "research"
COVERAGE_PATH = ROOT / "data" / "releases" / "coverage.json"
WATCHLIST_PATH = ROOT / "config" / "release_watchlist.json"
PROFILE_PATH = ROOT / "config" / "taste_profile.json"
DB_PATH = ROOT / "data" / "library_show.db"
CSV_OUT = ROOT / "data" / "releases" / "upcoming_releases.csv"
MD_OUT = ROOT / "outputs" / "releases" / "upcoming_releases.md"

# ---------------------------------------------------------------------------
# Settings you can change
# ---------------------------------------------------------------------------
TODAY = date.today()
EARLIEST = TODAY - timedelta(days=11)   # keep "just out" items this far back
RECENT_AIR_DAYS = 120                   # "you're airing this artist now" window

WEIGHTS = {
    "artist": 0.55,          # multiplier on the 0-100 taste-profile artist score
    "label_max": 22,         # most points a label can add
    "label_tier1": 5,        # extra for labels you air every month
    "recent_air": 12,        # artist aired in the last RECENT_AIR_DAYS days
    "new_music": 8,          # album, EP or single of new songs
    "catalog": -4,           # reissue, live, compilation
    "soon": 5,               # out within 45 days
    "no_date": -4,           # month/year/TBA only
    "rumored": -8,
}

# Words that make the same release look different ("(CD/LP)", "Deluxe").
TITLE_NOISE = re.compile(r"\((cd/lp|physical|cd|lp|vinyl)\)|\bthe\b", re.I)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def key(text: str) -> str:
    """Simplify a name for matching: 'The Jesus Lizard' -> 'jesus lizard'."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = text.lower().replace("&", " and ")
    text = re.sub(r"\b(the|recording company|records?|recordings?|music|inc|ltd)\b", " ", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def title_key(title: str) -> str:
    """Simplify a title so '(CD/LP)' editions merge with the main record."""
    return key(TITLE_NOISE.sub(" ", title or ""))


def parse_date(text: str):
    """Return (date or None, precision). Precision: day | month | year | tba."""
    text = (text or "").strip()
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return date(*map(int, m.groups())), "day"
    m = re.fullmatch(r"(\d{4})-(\d{2})", text)
    if m:
        return date(int(m[1]), int(m[2]), 1), "month"
    m = re.match(r"(\d{4})", text)
    if m:
        return date(int(m[1]), 1, 1), "year"
    return None, "tba"


def artist_parts(artist: str) -> list:
    """Split collaborations so 'Courtney Barnett & Kurt Vile' matches both."""
    parts = re.split(r"\s*(?:&|\band\b|\bwith\b|\bx\b|/|,|feat\.?)\s*", artist, flags=re.I)
    return [key(artist)] + [key(p) for p in parts if key(p)]


# ---------------------------------------------------------------------------
# Step 1: load every research record
# ---------------------------------------------------------------------------
def load_research() -> list:
    rows = []
    for path in sorted(RESEARCH_DIR.glob("*.json*")):
        if path.suffix == ".jsonl":
            items = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        else:
            items = json.loads(path.read_text())
        for item in items:
            if "artist" not in item:          # skip the "_checked" audit objects
                continue
            item["_file"] = path.name
            rows.append(item)
    return rows


# ---------------------------------------------------------------------------
# Step 2: merge duplicates
# ---------------------------------------------------------------------------
FIELDS = ["artist", "title", "type", "label", "release_date", "status",
          "latest_single", "single_date", "preview_url", "source_url",
          "source_name", "pull_quote", "notes"]


def completeness(r: dict) -> int:
    """How much useful detail a record has. Higher wins when merging."""
    score = sum(1 for f in FIELDS if r.get(f))
    if parse_date(r.get("release_date"))[1] == "day":
        score += 3
    if "NOT RE-VERIFIED" in (r.get("notes") or "").upper():
        score -= 4
    return score


def merge_title(title: str) -> str:
    """Looser title for merging: drop '(...)' and anything after ' / '."""
    title = re.sub(r"\(.*?\)|\[.*?\]", " ", title or "")
    return title_key(title.split(" / ")[0])


def same_release(a: dict, b: dict) -> bool:
    """True when two research records describe the same release."""
    a_parts = set(artist_parts(a["artist"])) - {"various artists", "various"}
    b_parts = set(artist_parts(b["artist"])) - {"various artists", "various"}
    if a["artist"].lower().startswith("various") and b["artist"].lower().startswith("various"):
        a_parts, b_parts = {key(a["artist"])}, {key(b["artist"])}
    if not (a_parts & b_parts):
        return False
    a_single = (a.get("type") or "").lower() == "single"
    b_single = (b.get("type") or "").lower() == "single"
    if a_single != b_single:
        return False
    ta, tb = merge_title(a["title"]), merge_title(b["title"])
    if ta and tb:
        return ta == tb
    # One record has no title (e.g. "new QOTSA record in October"):
    # merge if the release month matches.
    return (a.get("release_date") or "")[:7] == (b.get("release_date") or "")[:7]


def merge(records: list) -> list:
    groups = []                      # each group is a list of matching records
    for r in records:
        for g in groups:
            if any(same_release(r, other) for other in g):
                g.append(r)
                break
        else:
            groups.append([r])

    merged = []
    for recs in groups:
        recs.sort(key=completeness, reverse=True)
        best = {f: recs[0].get(f, "") or "" for f in FIELDS}
        for other in recs[1:]:
            for f in FIELDS:
                if not best[f] and other.get(f):
                    best[f] = other[f]
        # Prefer an exact date from any record over a vaguer one.
        dated = [x for x in recs if parse_date(x.get("release_date"))[1] == "day"]
        if dated:
            best["release_date"] = dated[0]["release_date"]
        # Stace works in YouTube Music, not YouTube: rewrite any youtube.com
        # video link so it opens in music.youtube.com instead.
        for f in ("preview_url", "notes"):
            best[f] = re.sub(r"https?://(www\.)?youtube\.com/watch", "https://music.youtube.com/watch", best[f])
            best[f] = re.sub(r"https?://youtu\.be/([\w-]+)", r"https://music.youtube.com/watch?v=\1", best[f])
        best["found_via"] = "; ".join(sorted({x.get("found_via", "") for x in recs if x.get("found_via")}))
        best["sources"] = " ".join(sorted({x.get("source_url", "") for x in recs if x.get("source_url")}))
        best["n_sources"] = len({x.get("source_url") for x in recs if x.get("source_url")})
        best["verified"] = 0 if all("NOT RE-VERIFIED" in (x.get("notes") or "").upper() for x in recs) else 1
        merged.append(best)
    return merged


# ---------------------------------------------------------------------------
# Step 3: score each release against your taste
# ---------------------------------------------------------------------------
def load_context():
    profile = json.loads(PROFILE_PATH.read_text())
    artist_scores = {}
    for a in profile["artists"]:
        for k in {key(a["artist"]), key(a.get("key", ""))}:
            if k:
                artist_scores[k] = a
    watch = json.loads(WATCHLIST_PATH.read_text())
    label_info = {key(v["label"]): v for v in watch["labels"].values()}

    # Recent airplay per artist, straight from the database.
    tmp = Path(tempfile.mkdtemp()) / "db.sqlite"
    shutil.copy(DB_PATH, tmp)
    con = sqlite3.connect(tmp)
    since = (TODAY - timedelta(days=RECENT_AIR_DAYS)).isoformat()
    recent = {}
    for artist, n in con.execute(
            "SELECT artist, COUNT(*) FROM v_airplay WHERE date >= ? GROUP BY artist_key", (since,)):
        recent[key(artist)] = n
    con.close()
    return artist_scores, label_info, recent, watch


def match_label(label: str, label_info: dict):
    """A release can list several labels ('ATO / Julia's War'). Take the best."""
    best = None
    for part in re.split(r"\s*(?:/|,|;|\bx\b)\s*", label or ""):
        k = key(re.sub(r"\(.*?\)", "", part))
        info = label_info.get(k)
        if info and (best is None or info.get("spins", 0) > best.get("spins", 0)):
            best = info
    return best


def score(r: dict, artist_scores, label_info, recent) -> dict:
    why = []
    total = 0.0

    # Artist evidence. Research notes can also point at a related profile
    # artist ("found_via: artist:R.E.M." for a Michael Stipe solo record).
    candidates = artist_parts(r["artist"])
    candidates += [key(m) for m in re.findall(r"artist:([^;]+)", r.get("found_via", ""))]
    a = next((artist_scores[p] for p in candidates if p in artist_scores), None)
    if a:
        total += WEIGHTS["artist"] * a["score"]
        bits = []
        if a.get("shows"):
            bits.append(f"aired on {a['shows']} shows")
        if a.get("ytm_plays_90d"):
            bits.append(f"{a['ytm_plays_90d']} YTM plays in 90 days")
        elif a.get("ytm_plays"):
            bits.append(f"{a['ytm_plays']} YTM plays")
        why.append(f"{a['artist']}: " + ", ".join(bits) if bits else f"{a['artist']} in profile")
    n_recent = max((recent.get(p, 0) for p in artist_parts(r["artist"])), default=0)
    if n_recent:
        total += WEIGHTS["recent_air"]
        why.append(f"{n_recent} spins in last {RECENT_AIR_DAYS} days")

    # Label evidence
    lab = match_label(r.get("label", ""), label_info)
    if lab:
        pts = min(WEIGHTS["label_max"], 4 * math.log2(1 + lab.get("spins", 0)))
        if lab.get("tier") == 1:
            pts += WEIGHTS["label_tier1"]
        total += pts
        why.append(f"{lab['label']} ({lab.get('spins', 0)} spins)" if lab.get("spins") else f"{lab['label']} (watchlist)")

    # Type and timing
    rtype = (r.get("type") or "").lower()
    total += WEIGHTS["new_music"] if rtype in ("album", "ep", "single") else WEIGHTS["catalog"]
    d, precision = parse_date(r.get("release_date"))
    if precision == "day" and TODAY <= d <= TODAY + timedelta(days=45):
        total += WEIGHTS["soon"]
    if precision in ("year", "tba"):
        total += WEIGHTS["no_date"]
    if r.get("status") == "rumored":
        total += WEIGHTS["rumored"]

    r["fit_score"] = round(max(0, min(100, total)), 1)
    r["tier"] = "A" if r["fit_score"] >= 45 else "B" if r["fit_score"] >= 25 else "C"
    r["evidence"] = "; ".join(why) or "style fit (see notes)"
    r["profile_artist"] = a["artist"] if a else ""
    r["watch_label"] = lab["label"] if lab else ""
    r["recent_spins"] = n_recent
    r["date_precision"] = precision
    r["release_date_sort"] = d.isoformat() if d else "9999-12-31"

    # Preview links (search pages, so they never go stale)
    q = f"{r['artist']} {r.get('latest_single') or r['title']}"
    r["ytm_search_url"] = "https://music.youtube.com/search?q=" + quote_plus(q)
    r["bandcamp_search_url"] = "https://bandcamp.com/search?q=" + quote_plus(f"{r['artist']} {r['title']}")
    return r


# ---------------------------------------------------------------------------
# Step 4: write the database table, the CSV and the report
# ---------------------------------------------------------------------------
COLUMNS = ["release_id", "artist", "title", "type", "label", "release_date",
           "release_date_sort", "date_precision", "status", "latest_single",
           "single_date", "fit_score", "tier", "evidence", "profile_artist",
           "watch_label", "recent_spins", "notes", "pull_quote", "preview_url",
           "ytm_search_url", "bandcamp_search_url", "source_url", "source_name",
           "sources", "n_sources", "verified", "found_via", "built_on"]


def write_db(rows: list, watch: dict, coverage: dict) -> None:
    tmp = Path(tempfile.mkdtemp()) / "library_show.db"
    shutil.copy(DB_PATH, tmp)                       # work on a copy (mount quirk)
    con = sqlite3.connect(tmp)
    con.execute("DROP TABLE IF EXISTS upcoming_releases")
    con.execute(f"CREATE TABLE upcoming_releases ({', '.join(c + (' INTEGER PRIMARY KEY' if c == 'release_id' else '') for c in COLUMNS)})")
    con.executemany(
        f"INSERT INTO upcoming_releases VALUES ({', '.join('?' * len(COLUMNS))})",
        [[r.get(c, "") for c in COLUMNS] for r in rows])

    # Label watchlist with how each label was checked this round.
    status = {}
    for bucket in ("label_site_checked", "wikipedia_only", "not_checked"):
        for name in coverage.get(bucket, []):
            status[key(name)] = bucket
    con.execute("DROP TABLE IF EXISTS release_watch_labels")
    con.execute("""CREATE TABLE release_watch_labels (
        label TEXT, label_key TEXT, tier INTEGER, spins INTEGER, recent_spins INTEGER,
        last_spin TEXT, url TEXT, sources TEXT, top_artists TEXT, check_status TEXT,
        releases_found INTEGER)""")
    for k, v in watch["labels"].items():
        n_found = sum(1 for r in rows if r["watch_label"] == v["label"])
        con.execute("INSERT INTO release_watch_labels VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
            v["label"], key(v["label"]), v.get("tier"), v.get("spins", 0), v.get("recent_spins") or 0,
            v.get("last_spin", ""), v.get("url", ""), ", ".join(v.get("sources", [])),
            ", ".join(v.get("top_artists", [])), status.get(key(v["label"]), "not_checked"), n_found))
    con.execute("CREATE INDEX IF NOT EXISTS ix_upcoming_date ON upcoming_releases(release_date_sort)")
    con.commit()
    con.close()
    shutil.copy(tmp, DB_PATH)


def write_csv(rows: list) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def md_escape(text: str) -> str:
    return (text or "").replace("|", "/").replace("\n", " ")


def md_row(r: dict) -> str:
    title = f"*{md_escape(r['title'])}*" if r["type"] != "single" else f"\"{md_escape(r['title'])}\""
    single = md_escape(r.get("latest_single", ""))
    if single and single.lower() == r["title"].lower():
        single = ""
    links = f"[YTM]({r['ytm_search_url']}) · [BC]({r['bandcamp_search_url']})"
    if r.get("preview_url"):
        links = f"[Preview]({r['preview_url']}) · " + links
    if r.get("source_url"):
        links += f" · [Source]({r['source_url']})"
    note = md_escape(r.get("notes", ""))[:140]
    return (f"| {r['fit_score']:.0f} | {md_escape(r['artist'])} | {title} | {r['type']} | "
            f"{md_escape(r['label'])} | {single} | {md_escape(r['evidence'])} | {note} | {links} |")


HEADER = ("| Fit | Artist | Release | Type | Label | Latest single | Why it fits | Notes | Links |\n"
          "|---|---|---|---|---|---|---|---|---|")


def friday_of(d: date) -> date:
    """Group releases by the Friday of their release week."""
    return d + timedelta(days=(4 - d.weekday()) % 7) if d.weekday() <= 4 else d - timedelta(days=d.weekday() - 4)


def write_md(rows: list, coverage: dict, watch: dict) -> None:
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    L = []
    L.append("# Upcoming releases for The Library")
    L.append("")
    L.append(f"Built {TODAY:%b. %-d, %Y} by `scripts/build_release_db.py`. "
             f"{len(rows)} releases, sorted by date, then fit score. "
             "The full table lives in `data/library_show.db` (`upcoming_releases`) and "
             "`data/releases/upcoming_releases.csv`.")
    L.append("")
    L.append("- **Fit** is 0-100: taste-profile artist score, label airplay, recent spins, "
             "new music over catalog, and date certainty.")
    L.append("- **Tier A** (45+) are strong picks. Tier C items stay in the table so every watched label is represented.")
    L.append("- Links: **YTM** opens a YouTube Music search for the latest single; **BC** searches Bandcamp.")
    L.append("")

    # Top picks
    top = sorted([r for r in rows if r["tier"] == "A" and r["status"] != "just_out" and r["type"] != "single"],
                 key=lambda r: -r["fit_score"])
    L.append("## Top picks coming up")
    L.append("")
    L.append(HEADER)
    L += [md_row(r) for r in top[:25]]
    L.append("")

    # Singles out now
    singles = sorted([r for r in rows if r["type"] == "single"], key=lambda r: -r["fit_score"])
    L.append("## New singles out now")
    L.append("")
    L.append(HEADER)
    L += [md_row(r) for r in singles]
    L.append("")

    # Just out
    just = sorted([r for r in rows if r["status"] == "just_out"], key=lambda r: (-r["fit_score"]))
    L.append(f"## Just out ({EARLIEST:%b. %-d} to now)")
    L.append("")
    L.append(HEADER)
    L += [md_row(r) for r in just]
    L.append("")

    # By release week
    dated = [r for r in rows if r["date_precision"] == "day" and r["status"] != "just_out"
             and r["type"] != "single" and r["release_date_sort"] >= TODAY.isoformat()]
    weeks = {}
    for r in dated:
        weeks.setdefault(friday_of(date.fromisoformat(r["release_date_sort"])), []).append(r)
    L.append("## By release week")
    L.append("")
    for wk in sorted(weeks):
        L.append(f"### Week of {wk:%b. %-d, %Y}")
        L.append("")
        L.append(HEADER)
        L += [md_row(r) for r in sorted(weeks[wk], key=lambda r: -r["fit_score"])]
        L.append("")

    # Vague dates
    vague = [r for r in rows if r["date_precision"] != "day" and r["status"] != "just_out" and r["type"] != "single"]
    L.append("## Month, year or date TBA")
    L.append("")
    L.append(HEADER)
    L += [md_row(r) for r in sorted(vague, key=lambda r: (r["release_date_sort"], -r["fit_score"]))]
    L.append("")

    # Coverage
    L.append("## Label coverage")
    L.append("")
    found = {}
    for r in rows:
        if r["watch_label"]:
            found[r["watch_label"]] = found.get(r["watch_label"], 0) + 1
    status = {}
    for bucket in ("label_site_checked", "wikipedia_only", "not_checked"):
        for name in coverage.get(bucket, []):
            status[key(name)] = bucket
    label_names = {"label_site_checked": "label site", "wikipedia_only": "Wikipedia list only",
                   "not_checked": "not checked"}
    L.append("| Label | Your spins | Checked via | Releases found |")
    L.append("|---|---|---|---|")
    for v in sorted(watch["labels"].values(), key=lambda v: -v.get("spins", 0)):
        if v.get("spins", 0) < 10 and v["label"] not in found:
            continue
        L.append(f"| {v['label']} | {v.get('spins', 0)} | "
                 f"{label_names.get(status.get(key(v['label']), 'not_checked'))} | {found.get(v['label'], 0)} |")
    L.append("")
    L += [f"- {n}" for n in coverage.get("method_notes", [])]
    L.append(f"- {coverage.get('artists_note', '')}")
    L.append("")
    MD_OUT.write_text("\n".join(L))


def main() -> None:
    raw = load_research()
    rows = merge(raw)

    # Keep releases from EARLIEST onward, plus undated ones.
    kept = []
    for r in rows:
        d, precision = parse_date(r["release_date"])
        if precision == "day" and d < EARLIEST:
            continue
        if precision == "month" and d < date(EARLIEST.year, EARLIEST.month, 1):
            continue
        kept.append(r)

    artist_scores, label_info, recent, watch = load_context()
    kept = [score(r, artist_scores, label_info, recent) for r in kept]
    kept.sort(key=lambda r: (r["release_date_sort"], -r["fit_score"]))
    for i, r in enumerate(kept, 1):
        r["release_id"] = i
        r["built_on"] = TODAY.isoformat()

    coverage = json.loads(COVERAGE_PATH.read_text())
    write_db(kept, watch, coverage)
    write_csv(kept)
    write_md(kept, coverage, watch)
    tiers = {t: sum(1 for r in kept if r["tier"] == t) for t in "ABC"}
    print(f"{len(raw)} research records -> {len(rows)} unique -> {len(kept)} in window. Tiers: {tiers}")
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}, {MD_OUT.relative_to(ROOT)}, and tables in {DB_PATH.name}")


if __name__ == "__main__":
    main()
