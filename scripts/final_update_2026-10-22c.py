#!/usr/bin/env python3
"""
final_update_2026-10-22c.py
Adds the "track history" fields the Final Show Script now shows instead of playlist-management notes:
  rel_main   bold release date with year (AP style)
  rel_sub    small line under it (single/album/EP, parent album date)
  info       2 to 3 sentences of track and artist history (from four research agents, checked and trimmed)
  shows      booked Bay Area shows for the artist (foopee.com, read Oct. 22, 2026; list runs to Jan. 2027)
Beginner notes: n is the track's position in tonight's list (1 to 55). The agents' raw output is in
data/recon/2026-10-22/research/output_1..4.json; we read it, apply manual fixes, and save into the plan.
"""
import json, re
from pathlib import Path

PLAN = Path("data/recon/2026-10-22/working_playlist.json")
R = Path("data/recon/2026-10-22/research")
plan = json.loads(PLAN.read_text(encoding="utf-8"))
res = {r["n"]: r for k in (1, 2, 3, 4) for r in json.loads((R / f"output_{k}.json").read_text(encoding="utf-8"))}

# bold date + small line (AP style: Jan. Feb. Aug. Sept. Oct. Nov. Dec. abbreviated; March April May June July spelled out)
REL = {
 1: ("Aug. 26, 2026", "album (digital); LP and CD Nov. 20, 2026"),
 2: ("Oct. 16, 2026", "compilation on Kill Rock Stars"),
 3: ("Feb. 13, 2026", "album"),
 4: ("July 10, 2026", "album"),
 5: ("June 23, 2026", "single; album July 17, 2026"),
 6: ("May 20, 2026 (verify)", "single; album Aug. 21, 2026"),
 7: ("Aug. 13, 2026", "single; album Oct. 16, 2026"),
 8: ("Feb. 26, 2026 (verify)", "single; album May 22, 2026"),
 9: ("Aug. 12, 2026", "single; album Nov. 6, 2026"),
 10: ("1978", "EP; reissued Feb. 5, 2021"),
 11: ("1982", "EP"),
 12: ("1984", "EP; collected 1991"),
 13: ("April 11, 1996", "radio single; album May 6, 1996"),
 14: ("March 1991", "album"),
 15: ("1992", "album; reissued 2006 and 2020"),
 16: ("Aug. 28, 2026", "album"),
 17: ("April 25, 2025", "album"),
 18: ("Oct. 16, 2026", "album"),
 19: ("Sept. 18, 2026", "album"),
 20: ("Feb. 23, 2026", "single; album March 27, 2026"),
 21: ("Sept. 11, 2026", "album"),
 22: ("March 25, 2025", "single; deluxe album April 25, 2025"),
 23: ("2025", "single; album March 2026"),
 24: ("May 19, 2026", "single; album July 17, 2026"),
 25: ("Oct. 22, 1976", "single; album Feb. 18, 1977"),
 26: ("May 1984", "single B-side"),
 27: ("Feb. 18, 1977", "single, same day as the album"),
 28: ("April 1979", "single; album Nov. 1979"),
 29: ("June 26, 2026", "single; album July 28, 2026"),
 30: ("March 11, 2022", "album"),
 31: ("1984 to 1986 (verify)", "album; collected 1993"),
 32: ("June 15, 2026", "single; album Sept. 25, 2026"),
 33: ("Oct. 9, 2015", "album"),
 34: ("Nov. 1981", "album"),
 35: ("May 11, 1981", "album; remaster Oct. 5, 2009"),
 36: ("June 1979", "single"),
 37: ("June 19, 1981", "single; album Oct. 16, 1981"),
 38: ("April 26, 1991", "album"),
 39: ("Oct. 6, 2026 (verify)", "single; album Oct. 30, 2026"),
 40: ("July 23, 2026", "single; album Oct. 16, 2026"),
 41: ("July 21, 2026 (verify)", "single; album Sept. 11, 2026"),
 42: ("Oct. 2, 2026", "album"),
 43: ("Aug. 5, 1986", "UK single; album Oct. 20, 1986"),
 44: ("June 7, 2019", "album"),
 45: ("Oct. 7, 2016", "album; 7-inch May 2016"),
 46: ("Sept. 18, 2012", "album"),
 47: ("Feb. 1, 2016", "single; album May 13, 2016"),
 48: ("May 26, 2026", "album"),
 49: ("Aug. 23, 2022", "single; album Nov. 11, 2022"),
 50: ("Feb. 26, 2026", "album"),
 51: ("March 1, 2019", "EP"),
 52: ("Sept. 9, 2026 (verify)", "single; album Nov. 6, 2026"),
 53: ("June 7, 2019", "album; cover of 1984 song"),
 54: ("March 31, 2026 (verify)", "single"),
 55: ("Aug. 25, 2026", "single; album Oct. 30, 2026"),
}

# Hand-edited info for tracks where the agent text had a flagged or unverifiable claim
INFO = {
 2: "Heavens to Betsy are an Olympia, Washington duo, Corin Tucker and Tracy Sawyer. The song comes from a February 1992 demo engineered by Molly Neuman of Bratmobile and first appeared on Throw: The Yoyo Studio Compilation (Yoyo Recordings), the library copy. Kill Rock Stars issues it Oct. 16, 2026 as track 7 of baby's gone, a 16-track set that also gathers the 1993 These Monsters Are Real and 1994 Direction recordings.",
 3: "Track 6 of 12 on Blame the Clown, the second full-length from the New Orleans duo Twisted Teens, on Chain Smoking Records. Melrose Billiard plays lead guitar on this song. Their next album, The Holy Cross Tigers, is out Nov. 6, 2026 on Sub Pop.",
 4: "Track 6 on Florida Water Blues, the New Orleans duo Twisted Teens' 2026 album, after Guided Thunder. Reviewers compare it to a barroom blues band discovering Iggy Pop.",
 8: "Lead single and opening track on Gravity Freeze, the band's sixth studio album, on Easy Eye Sound. Barrie Cadogan wrote the song on bass, and the album was co-produced by Rupert Lyddon at Rat Salad Studios in London.",
 12: "Track 2 of the 1984 self-titled EP on Rabid Cat, recorded in July 1984 at Earth and Sky Studio in Austin. Steve Anderson wrote the lyrics and David Wm. Sims the music. David Yow sang, and he later fronted The Jesus Lizard. The EP is the first eight tracks of the 1991 Touch and Go compilation The Greatest Gift.",
 13: "Lead single from Electriclarryland, the San Antonio band's seventh studio album. Radio service began April 11, 1996. It reached number one on the Billboard Modern Rock Tracks chart. The album came out May 6, 1996, reached number 31 on the Billboard 200 and went gold in August 1996.",
 14: "Track 5 on Goat, the band's second studio album, produced by Steve Albini and released on Touch and Go. Singer David Yow had fronted Scratch Acid. Goat was remastered by Albini and Bob Weston and reissued in 2009 with five bonus tracks.",
 17: "From viagr aboys, the fourth album by the Swedish band Viagra Boys, produced by Pelle Gunnerfeldt, who has worked with the band since their start. It is track 6 and came out on the band's own Shrimptech Enterprises label. It was not issued as a separate single.",
 20: "Released as a single ahead of Companion, the third album by the Durham, North Carolina, band Sluice. Justin Morris wrote the songs, and he has said a carpentry job inspired this one.",
 23: "Dread Spectre Council is the solo project of Kenneth Amundsen of Oslo, Norway. This track was released as a single in 2025 ahead of the debut album Thetans, on the Oslo label Handmade Records, out March 2026.",
 26: "Recorded Jan. 19, 1984 for the BBC comedy The Young Ones, which aired it in the episode of the same name on May 29, 1984. It was the B-side of Thanks for the Night. It is on no Damned studio album and later appeared on compilations, including Punk Generation: Best Of The Damned - Oddities & Versions.",
 27: "The Damned's second single, released by Stiff on the same day as their debut album, which is regarded as the first album by a UK punk band. Brian James wrote it and Nick Lowe produced it. The B-side has two tracks, Stab Yor Back and Singalongascabies.",
 28: "The Damned's single on Chiswick, catalog CHIS 112, with Noise Noise Noise on the B-side. It peaked at No. 20 in the UK. Captain Sensible had moved to guitar and Algy Ward joined on bass. A re-recorded version opens Machine Gun Etiquette, and that is the version on the album.",
 30: "From Broken Equipment, the Brooklyn band's 2022 album. Ben Hozie wrote it and produced the album with live sound mixer Bobby Lewis. It is track 4.",
 31: "Frightwig is an all-woman San Francisco punk band formed in the early 1980s. The song comes from their first two albums, Cat Farm Faboo (Subterranean, 1984) and Faster, Frightwig, Kill! Kill! (Caroline, 1986), and is on the compilation Wild Women Never Die (Southern, 1993), the library copy. The band released We Need to Talk in 2023.",
 34: "From Damaged, Black Flag's debut album and the first with vocalist Henry Rollins, on SST Records. Rollins joined only weeks before the album was recorded. The band on tour now is led by guitarist Greg Ginn.",
 35: "From Computer World, the Dusseldorf group's 1981 album. The song counts in several languages, including Japanese. A German version, Nummern, followed on a January 1982 maxi-single. The track on air is from the 2009 remaster.",
 38: "From Friendly Fa$cism, the 1991 album by San Francisco industrial hip-hop act Consolidated, recorded at Razors Edge in San Francisco from November 1990 to January 1991. The title comes from Bertram Gross's 1980 book on creeping fascism. The album is on Nettwerk.",
 42: "Track 4 of 9 on Post Script, released on Cog Sinister and billed as the band's final studio album. It was built from unused vocals Mark E. Smith recorded between 2001 and 2014, with new backing tracks added. Smith died in January 2018. The attribution to The Fall is disputed.",
 43: "Chrissie Hynde wrote the song and Jimmy Iovine produced it, with Bob Clearmountain mixing. It was the lead single from Get Close (UK release Oct. 20, 1986) and reached No. 10 on both the Billboard Hot 100 and the UK Singles Chart. Hynde has said she wrote it for her friend, tennis player John McEnroe.",
 44: "Will Toledo of Car Seat Headrest produced and recorded Midnight, and he sings this song as a duet with Chura and plays guitar, bass, synth and piano on it. It is on her second album, on Saddle Creek. Chura has said the chorus and guitar riff came after the unexpected death of a close friend.",
 45: "Sub Pop issued it as a 7-inch single with The Snake of Addis Ababa in May 2016, ahead of Requiem, the Swedish band's third studio album. Sub Pop released the album in North America and Rocket Recordings elsewhere.",
 53: "A cover of George Michael's Careless Whisper, which Michael wrote with Andrew Ridgeley and released in 1984. Jesse Hughes, performing as Boots Electric, recorded it for a covers album of 13 songs he wished he had written, released by UMe. This version drops the original's saxophone line.",
}
def clean(s):
    s = re.sub(r"\s*(The track|It|The song) runs (about )?[^.]*\.", "", s)
    return s.strip()

STARS = {"Lex Walton": 5, "Twisted Teens": 5, "Yard Act": 5, "Little Barrie": 5, "Ty Segall": 3, "Palace": 5, "Sluice": 5,
         "Dread Spectre Council": 5, "Tricky": 5, "Sylvan Esso": 4, "The Fall": 4, "Stef Chura": 4, "Dumb": 4}
STARS_TRACK = {("This Is Lorelei", "Don't You Cry in Lonesomeness"): 4}

# Booked Bay Area shows (foopee.com list, read Oct. 22, 2026). Format: doors/show times as listed.
SHOWS = {
 "Cheekface": ["Fri. Oct. 23, Cornerstone, Berkeley, with BODEGA ($36; doors 8 p.m., show 9 p.m.). A second listing has Waitress."],
 "BODEGA": ["Fri. Oct. 23, Cornerstone, Berkeley, with Cheekface ($36; doors 8 p.m., show 9 p.m.)."],
 "Frightwig": ["Fri. Oct. 23, Chapel, S.F., with AroMa and scary story time ($25; doors 7 p.m.).", "Sat. Nov. 21, Bottom of the Hill, S.F., with M.D.C. and Class Of '77 ($20/$23; doors 8 p.m.)."],
 "Julia Jacklin": ["Fri. Oct. 23, Castro, S.F. (sold out).", "Sat. Oct. 24, Castro, S.F. ($48.60; doors 7 p.m.)."],
 "Protomartyr": ["Fri. Oct. 23, Ritz, San Jose, with Accessory ($26/$30; doors 8 p.m.).", "Sat. Oct. 24, August Hall, S.F., with Accessory ($37.25; doors 7 p.m.)."],
 "Black Flag": ["Fri. Oct. 23, Felton Music Hall, Felton (21+).", "Sat. Oct. 24, Music Hall, Napa ($43; doors 7 p.m.).", "Sun. Oct. 25, Cornerstone, Berkeley ($45.80; doors 7 p.m.). Greg Ginn lineup."],
 "The Damned": ["Wed. Nov. 11, Fillmore, S.F., with Flamin' Groovies and Courettes (doors 7 p.m., show 8 p.m.)."],
 "feeble little horse": ["Wed. Dec. 9, Independent, S.F., with Mop ($36; doors 7:30 p.m.).", "Thu. Dec. 10, Independent, S.F. (sold out)."],
}

n = 0
for s in plan["sets"]:
    for t in s["tracks"]:
        n += 1
        r = res[n]
        assert r["artist"].lower()[:6] == t["artist"].lower()[:6], (n, r["artist"], t["artist"])
        t["rel_main"], t["rel_sub"] = REL[n]
        info = INFO.get(n) or clean(r["info"])
        st = STARS.get(t["artist"]) or STARS_TRACK.get((t["artist"], t["track"]))
        if st:
            info += f" Your review: {st} star{'s' if st != 1 else ''}."
        t["info"] = info
        t["shows"] = SHOWS.get(t["artist"], [])
        t["research_sources"] = r.get("sources", [])
        t["research_confidence"] = r.get("confidence")
        # label fixes found in research
        if n == 17:
            t["label"] = "Shrimptech Enterprises"; t["label_source"] = "wikipedia, Apple Music (band's own label; not in ZK)"
        if n == 53:
            t["label"] = "Ume"; t["label_source"] = "zookeeper label table 19395 (UMe, per the band's announcement)"
        if n == 55:
            t["released"] = "2026-08-25 (single; album Perfecth out Oct. 30)"

# Royal Blood album date: newer sources say Nov. 6, 2026
for s in plan["sets"]:
    for t in s["tracks"]:
        if t["artist"] == "Royal Blood":
            t["released"] = "2026-08-12 (single; album Dead Company out Nov. 6)"
            t["why"] = t["why"].replace("Dead Company is due Nov. 13 on Warner Records; sources list Nov. 6, 12 and 13, so verify.", "Dead Company is due Nov. 6 on Warner Records (August coverage said Nov. 13).")
plan["booked_shows_source"] = "foopee.com the-list by-date pages 0 to 11, read Oct. 22, 2026 (Bay Area only, through Jan. 2027)"
PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("tracks", n, "with shows:", sum(1 for s in plan["sets"] for t in s["tracks"] if t["shows"]))

# ---- talk breaks that mention booked shows (second pass, same run) ----
plan = json.loads(PLAN.read_text(encoding="utf-8"))
mb = plan["mic_breaks"]
mb["bay_area_break"] = [
 "Fri. Oct. 23: Cheekface with BODEGA at Cornerstone in Berkeley; Frightwig at Chapel in S.F.; Protomartyr at the Ritz in San Jose; Julia Jacklin at the Castro (sold out). Black Flag with Greg Ginn plays Felton Music Hall Oct. 23, Music Hall in Napa Oct. 24 and Cornerstone in Berkeley Oct. 25.",
 "Sat. Oct. 24: Protomartyr at August Hall in S.F. and Julia Jacklin at the Castro. Later: Slow Pulp at the Fillmore Oct. 28, The Damned at the Fillmore Nov. 11, Frightwig at Bottom of the Hill Nov. 21, feeble little horse at the Independent Dec. 9 and 10 (Dec. 10 sold out).",
]
if not any("Fillmore" in x for x in mb["triple_shot_intro"]):
    mb["triple_shot_intro"].append("The Damned play the Fillmore in San Francisco on Wed. Nov. 11, with Flamin' Groovies and Courettes.")
PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
