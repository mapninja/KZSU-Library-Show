"""Merge the Nov. 1, 2026 YouTube Music re-scrape into data/ytm/playlist_dump.json.

Why: ytmusicapi has no valid browser.json in the sandbox, so playlists were read in the
signed-in YouTube Music tab with the page's own browse API. Only playlists whose track
count changed were re-read: Next Show, To Review, Covers and FCC Edit Needed.
Everything else keeps the Oct. 25 per-artist data.

Export format: one line per playlist, "ID<TAB>Title<TAB>artist|artist^^N|..."
  - "^^N" after a name means that artist repeats N times in a row (run-length encoding)
  - "&" was exported as "+" because the browser tool blocks text with many "&"
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DUMP = ROOT / "data" / "ytm" / "playlist_dump.json"

# Text exported from the page in 950-character chunks (joined exactly as returned).
# "\t" and "\n" are written as escape sequences and fixed below.
CHUNKS = [
r"PLMduzOohHQLrQzt6w4ep6l2zAwcIzoZVF\t01 KZSU - Next Show\tTV Priest|Royal Blood|TV Priest|Ty Segall|Twisted Teens|Hamilton Leithauser + Rostam|Lex Walton|Palace^^2|Funkadelic|Sprints|Dread Spectre Council|Twisted Teens|Cut Worms|Westside Cowboy|Sampa the Great|The Fall|Sluice^^2|BODEGA|Cameron Winter|The Tallest Man On Earth|Fontaines D.C.|Twisted Teens|Fujiya + Miyagi|John Lennon|BODEGA|Soundgarden|Father John Misty|Bauhaus|TV Priest^^2|Star Moles|Hot Chip|The Linda Lindas|Dumb|Sonic Youth|matt proxy , Current Joys , never goodbye + Elijah Walker|Current Joys + YOUR ANGEL|Jesse Welles|Car Seat Headrest|J Mascis|Caroline Rose|Chris Cornell\nPLMduzOohHQLoYAPMl9uNRayfpe9uQ3NiA\tTo Review\tBill Callahan^^12|Mandy, Indiana^^10|Viagra Boys^^15|Arctic Monkeys + War Child Records|Damon Albarn, Grian Chatten, Kae Tempest + War Child Records|Black Country, New Road + War Child Records|The Last Dinner Party + War Child Records|Beth Gibbons + War Child ",
r"Records|Arooj Aftab, Beck + War Child Records|King Krule + War Child Records|Depeche Mode + War Child Records|Ezra Collective, Greentea Peng + War Child Records|Arlo Parks + War Child Records|English Teacher, Graham Coxon + War Child Records|Beabadoobee + War Child Records|Big Thief + War Child Records|Fontaines D.C. + War Child Records|Cameron Winter + War Child Records|Young Fathers + War Child Records|Pulp + War Child Records|Sampha + War Child Records|Wet Leg + War Child Records|Foals + War Child Records|Bat For Lashes + War Child Records|Anna Calvi, Nilufer Yanya, Dove Ellis + War Child Records|Olivia Rodrigo + War Child Records|Guided By Voices^^12|Sharp Pins^^11|The Fall^^9|Greg Freeman^^13|BODEGA^^12|Stef Chura^^9|Gilla Band^^10|Star Moles^^10|Jesse Welles|Death Valley Girls^^9|Fontaines D.C.|L7|Little Barrie|The Tallest Man On Earth^^11|Cameron Winter^^12|Dummy^^10|Heavens to Betsy^^16|Calibro 35^^12|Caroline Rose^^11|Fontaines",
r" D.C.^^7|Fontaines D.C. + ROSALÍA|Fontaines D.C.^^3|L'Rain|Alex Izenberg|Starcleaner Reunion|Sessa + Marina Nemésio|Colin Broster|Cate Le Bon|Orchid Salon|Andy Boay|Corridos Ketamina, Nico Malva + so02|No Joy + Morgan Greenwood|СОЮЗ|Dan English|Current Joys^^8|Sampa the Great^^16|Queens of the Stone Age^^9|Skinshape^^11|horsegiirL^^4|horsegiirL + Dylan Brady|Coil^^16|Jesse Welles^^2|Spike and the Gimme Gimmes^^11|Low Cut Connie^^10\nPLMduzOohHQLodi1DCB1DBh7maGUUoc47Z\tCovers\tTy Segall|Screaming Females|Soundgarden|Eagles Of Death Metal|Melvins|Car Seat Headrest|Lucius|CBC Music|Bedouine, Hurray For The Riff Raff + Waxahatchee|Beck|beckmangroup|Iron + Wine|SiriusXM|Sturgill Simpson|Low + Dirty Three|Wilco|Uncle Tupelo|Ty Segall|Tkay Maidza|Sunflower Bean|Car Seat Headrest|The Crystal Ark|Pavement|Wilco|Amen Dunes|Sturgill Simpson|Fruit Bats|Lera Lynn + Shovels + Rope|Marissa Nadler|Lucy Dacus|Beck|Nilüfer Yanya|Chromatics|Portugal. The Man",
r"|Kurt Vile|Sparklehorse|Nebula|Tropical Fuck Storm|St. Vincent|Eagles Of Death Metal|Juliana Hatfield|Sturgill Simpson|Bedhead|Elton John, P!nk + Logic|Florence + The Machine|Queens Of The Stone Age|Nell Smith + The Flaming Lips|Eddie Vedder|Royel Otis|Eddie Vedder|Thundercat|Andrew Bird + Lucius|The Stone Roses|Nouvelle Vague|DeVotchKa|Sneaker Pimps|Beck^^8|Fine Young Cannibals|Galaxie 500|Father John Misty|Soundgarden|Julia Jacklin|J Mascis\nPLMduzOohHQLoN-Bq1XuSpyqe1i5JffIad\tFCC Edit Needed\tPatrick Wolf|Caroline Rose|Lambrini Girls|Frog|Magnolia Electric Co. + Jason Molina|Anna Erhard|Caroline Rose|Dead Pioneers + Cheap Perfume|MC 900 Ft. Jesus|Consolidated",
]

blob = "".join(CHUNKS).replace("\\t", "\t").replace("\\n", "\n")
dump = json.loads(DUMP.read_text(encoding="utf-8"))
for line in blob.split("\n"):
    pid, title, artists = line.split("\t")
    rows = []
    for item in artists.split("|"):
        # Expand run-length encoding: "Name^^3" means three rows by Name.
        name, _, n = item.partition("^^")
        count = int(n) if n else 1
        # "+" was "&" before export; each row needs 4 slots: [title, artist, album, videoId]
        rows += [["", name.replace(" + ", " & "), "", ""]] * count
    print(f"{title}: {len(dump.get(pid, {}).get('data', []))} -> {len(rows)} rows")
    dump[pid] = {"title": title, "data": rows}
DUMP.write_text(json.dumps(dump, ensure_ascii=False), encoding="utf-8")
