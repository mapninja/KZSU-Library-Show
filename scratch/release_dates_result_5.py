import json
R = []
def add(key, date, prec, sources, note, label="", status="released"):
    R.append(dict(key=key, date=date, precision=prec, sources=sources, status=status, note=note, label=label))

add("mitski|nothing s about to happen to me", "2026-02-27", "day",
    ["https://en.wikipedia.org/wiki/Nothing's_About_to_Happen_to_Me", "https://mitski.bandcamp.com/album/nothings-about-to-happen-to-me"],
    "Wikipedia and Bandcamp agree. A Spotify prerelease page showed Feb 26, likely a prerelease listing.")
add("hugernaut|circulator", "2026-03-02", "day",
    ["https://hugernaut.com/", "https://beat.com.au/its-all-about-the-music-for-regional-family-band-hugernaut-pumped-to-finally-launch-their-album-in-the-big-smoke/", "https://collegeradiocharts.com/march-25th-2026-weighted/"],
    "Band site lists album release 2nd March 2026; Circulator charted on Azzliff by Mar 25, 2026. Label spelled Azzliff in charts, Azziff on band site. Beat piece covers a later Melbourne launch show.")
add("other lives|sheerar sessions", "2026-05-22", "day",
    ["https://otherlivesofficial.bandcamp.com/album/sheerar-sessions", "https://frontview-magazine.be/en/article/other-lives-special-demo-album-sheerar-sessions-out-now", "https://open.spotify.com/album/3Uj4hu84SArvgd577dCpKL"],
    "Demo versions of songs from Volume V (Oct 2025). Bandcamp, Spotify and Amazon show May 22.")
add("temporary blessings|sumbisori", "2025-12-05", "day",
    ["https://temporaryblessings.bandcamp.com/album/sumbisori", "https://music.apple.com/us/album/sumbisori/1831079699", "https://www.coleminerecords.com/products/temporary-blessings-sumbisori-release-date-11-14-2025"],
    "Bandcamp, Apple Music, Amazon and label listing agree on Dec 5, 2025 (Colemine URL slug says 11-14-2025 but page shows 12/5/2025). Label copyright College Of Knowledge; Colemine also sells it.")
add("kneecap|fenian", "2026-05-01", "day",
    ["https://en.wikipedia.org/wiki/Fenian_(album)", "https://kneecap.bandcamp.com/album/fenian", "https://heavenlyrecordings.com/artist/kneecap/"],
    "Wikipedia, Bandcamp and Heavenly agree on May 1. Earlier announcement said Apr 24 (Irish Times, Jan 2026); a Spotify prerelease page showed Apr 30. Label per Wikipedia and Heavenly is Heavenly Recordings; input said [PIAS].",
    label="Heavenly Recordings")
add("miss grit|under my umbrella", "2026-04-24", "day",
    ["https://www.brooklynvegan.com/miss-grit-announces-new-lp-under-my-umbrella-shows-shares-stranger/", "https://music.apple.com/us/album/under-my-umbrella/1870707890", "https://www.music-tracker.com/release/under-my-umbrella"],
    "BrooklynVegan, Apple Music, Music Tracker agree on Apr 24. A Loudwire store listing shows Apr 23 for the vinyl.")
add("nora kelly band|so wrong for so long", "2026-05-22", "day",
    ["https://mintrecs.com/releases/so-wrong-so-long", "https://norakellyband.bandcamp.com/album/so-wrong-for-so-long", "https://exclaim.ca/music/article/nora-kelly-band-port-city-blues-song-review"],
    "Label, Bandcamp and Exclaim! agree. A retailer CD presale listing says 7/3/26 (likely ship date).")
add("tory silver|in through the front with lasers", "2026-05-29", "day",
    ["https://torysilvermusic.bandcamp.com/album/in-through-the-front-with-lasers", "https://thedailymusicreport.com/reviews/tory-silver-in-through-the-front-with-lasers-05312026/", "https://femmusic.com/2026/03/18/tory-silver-in-through-the-front-with-lasers/"],
    "Announced for May 29 on Michi Tapes; Daily Music Report review (May 31) says released May 29. Track count differs between sources (9 vs 11).")
add("dinosaur jr|there near", "2026-08-28", "day",
    ["https://www.premierguitar.com/news/dinosaur-jr-new-album-there-near", "https://spillmagazine.com/spill-news-dinosaur-jr-announce-new-album-out-august-28-via-jagjaguwar-north-american-tour/", "https://scummywatertower.com/reviews/album-reviews/dinosaur-jr-there-near-2026-album-review/"],
    "Sources agree on Aug 28, 2026 via Jagjaguwar; review dated Aug 28 says it is out.")
add("westside cowboy|it goes on", "2026-08-21", "day",
    ["https://westsidecowboy.bandcamp.com/album/it-goes-on", "https://www.islandrecords.com/products/it-goes-on-standard-cd", "https://en.wikipedia.org/wiki/It_Goes_On"],
    "Bandcamp and Island store give Aug 21. Release is on Island Records (Universal Music Operations); no source seen mentioning Slow Play.",
    label="Island Records")
add("sharp pins|electric my icebox", "2027-01-15", "day",
    ["https://stereogum.com/2512318/sharp-pins-announce-new-ep-electric-my-icebox-hear-how-can-i-explain-what-she-does-to-me/music", "https://krecs.com/products/electric-my-icebox-prnl075-klp328-lp-cd-cs", "https://jackpotrecords.com/products/sharp-pins-electric-my-icebox-12-vinyl-ep-pre-order-out-1-15-27", "https://readdork.com/news/sharp-pins-electric-my-icebox-ep-e7f0c6bd4e"],
    "Six-song EP on K/Perennial, pre-orders open, due Jan 15, 2027; date is after today so announced.", status="announced")
add("sylvan esso|hot slob", "2026-06-10", "day",
    ["https://sylvanesso.bandcamp.com/track/hot-slob-2", "https://stereogum.com/2502072/sylvan-esso-hot-slob/music", "https://shorefire.com/releases/entry/sylvan-esso-invite-you-to-their-hot-slob-partynew-single-video-out-now-on-psychic-hotline"],
    "Bandcamp and YouTube list June 10, 2026; press release says out now on Psychic Hotline.")
add("lambrini girls|cult of celebrity", "2026-03-31", "day",
    ["https://lambrinigirlsband.bandcamp.com/track/cult-of-celebrity", "https://music.apple.com/gb/album/cult-of-celebrity-single/1880086351", "https://consequence.net/2026/03/lambrini-girls-new-single-cult-of-celebrity/"],
    "Bandcamp, Apple Music and The Daily Music Report (Mar 31) agree. YouTube video credits City Slang.")
add("allah las|ultramarine", "2026-05-13", "day",
    ["https://allah-las.bandcamp.com/album/ultramarine-2", "https://shop.mexicansummer.com/release/590885-allah-las-ultramarine?lang=en_GB", "https://mexicansummer.com/allah-las-release-new-single-ultramarine/"],
    "Bandcamp and Mexican Summer shop show May 13, 2026 (7-inch ships June 26). Search snippet also mentioned a 29 May date on a Mexican Summer page; treated as ambiguous. Lead single from Sirenas (album Aug 28, 2026 per a retailer).")
add("miss grit|stranger", "2026-01-27", "day",
    ["https://bleep.com/release/555136-miss-grit-stranger", "https://stereogum.com/2486717/miss-grit-announces-new-album-under-my-umbrella-hear-stranger/music", "https://www.side-line.com/miss-grit-launches-new-album-under-my-umbrella-with-single-stranger-on-mute/"],
    "Bleep lists Jan 27, 2026 and press announced the album and single that day. Shazam shows Apr 24 (album date), likely conflation.")
add("gelli haha|klouds will carry me to sleep", "2026-03-25", "day",
    ["https://open.spotify.com/track/3IdaTGnIie33x1MIZQ5frN", "https://music.apple.com/us/album/klouds-will-carry-me-to-sleep-single/1882817247", "https://www.beatport.com/track/klouds-will-carry-me-to-sleep/26834251", "https://www.treblezine.com/hear-a-new-song-from-gelli-haha-klouds-will-carry-me-to-sleep/"],
    "Spotify, Apple Music, Beatport and Treble agree on Mar 25, 2026 via Innovative Leisure.")
add("imperial teen|all hands up", "2026-09", "month",
    ["https://rmas.mx/en/2026/09/17/imperial-teen-release-hands-all-up-new-preview-of-all-over-you/", "https://open.spotify.com/album/54JRR5bBSd8GqdLTVYRtfo", "https://silverpr.co.uk/imperial-teen-announce-new-album-all-over-you-out-9th-october-on-merge-records/"],
    "Title appears to be 'Hands All Up' (not 'All Hands Up'), single from album All Over You (Merge, Oct 9, 2026). Coverage dated about Sept 17, 2026, but exact day not confirmed.")
add("steve earle los lobos|volver a celaya city of immigrants", "2026-08-06", "day",
    ["https://steveearle.bandcamp.com/album/volver-a-celaya-city-of-immigrants", "https://www.steveearle.com/news/2026/8/6/volver-a-celaya-with-los-lobos-out-now", "https://www.loslobos.org/news/2026-08-06/los-lobos-latest-collaboration-with-steve-earle-volver-a-celaya-out-now/", "https://www.countrystandardtime.com/news/newsitem.asp?xid=16189"],
    "Digital single 'Volver A Celaya' out Aug 6, 2026 on New West. The limited 7-inch pairing it with 'City of Immigrants' (B-side, Earle with Forro in the Dark) is dated Oct 16, 2026 per Steve Earle site and Blues Magazine. Use Oct 16 if the physical 7-inch edition is meant; input current_date was 2026-10-16.")

json.dump(R, open("/sessions/awesome-gifted-dirac/mnt/KZSU-Library-Show/scratch/release_dates_result_5.json", "w"), indent=1)
print(len(R))
