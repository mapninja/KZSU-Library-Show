# One-time edit of build_landscape_final_2026-10-22.js for the Oct. 22 Air Order update.
p = 'scripts/build_landscape_final_2026-10-22.js'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)
rep("Final built Wed. Oct. 21  |  Texas punk week", "Final built Wed. Oct. 21, updated Thu. Oct. 22 for your Air Order edits  |  Texas punk week")
i = s.index('kids.push(heading("What changed since the working draft"')
j = s.index('kids.push(spacer());\nkids.push(heading("What is in this show"')
new_tbl = '''kids.push(heading("What changed: Thu. Oct. 22 update (your Air Order edits)", 24, 160));
kids.push(simpleTable([2600, 11800], ["Change", "Detail"], [
  [{ t: "Cut by you", bold: true }, "Fontaines D.C. Six Shot Morning, Mimesis and Where Is Gone? (Happy For You stays), and Pulp The Trees. All four are out of the run of show and the Zookeeper CSV. Logged as not interested for 60 days."],
  [{ t: "Added inside the list", bold: true }, `Nervebreakers My Girlfriend is a Rock, radio edit (${N("Nervebreakers", "My Girl")}), Loco Gringos Ain't No Corndogs (${N("Loco Gringos", "Ain")}) and This Is Lorelei & MJ Lenderman Dancing in the Club, radio edit (${N("This Is Lorelei & MJ Lenderman", "Dancing")}). Set 2 is now Texas punk with Dallas added.`],
  [{ t: "Your last six, placed where they fit", bold: true }, `Set 1: Westside Cowboy (${N("Westside Cowboy", "Kick")}, after Yard Act) and Royal Blood (${N("Royal Blood", "Ten")}, last, before the Texas set). Set 7: Bauhaus (${N("Bauhaus", "The Passion")}) and Consolidated (${N("Consolidated", "Friendly")}). Set 8: Stef Chura (${N("Stef Chura", "Sweet")}, closes the slow set). Set 9: Dumb (${N("Dumb", "Pull")}, with the short rockers).`],
  [{ t: "Reordered", bold: true }, "Set 1 now follows your Air Order (Lex Walton first, Dummy after Yard Act). The Air Order on YouTube Music still lists the six at the end (positions 50 to 55); it was not changed."],
  [{ t: "Metadata", bold: true }, "Labels and tags from Zookeeper where the library has the album (Loco Gringos 1089648, Bauhaus Mask 273046, Stef Chura Midnight 1135774, Consolidated 2866, Dumb 1148228). Web sources for the rest. Nervebreakers is on the library compilation Bloodstains Across Texas only (tag 487829); no tag used."],
  [{ t: "Still open", bold: true }, { t: "Triple Shot has four Damned tracks. Loco Gringos has no lyrics posted: listen first. Lorelei and Lenderman, Nervebreakers and Consolidated are radio edits on YTM: confirm the edits by ear (Lorelei original has fuck x2 in Verse 4).", color: RED }],
  [{ t: "Earlier (Oct. 21 final)", bold: true }, "No cull or replace ticks. Labels filled for seven tracks. Greatest Gift replaced Mary Had a Little Drug Problem; Nasty joined the Triple Shot; Van Wissem and Jarmusch, EODM, Lambrini Girls and QOTSA closed the Air Order."],
]));
'''
s = s[:i] + new_tbl + s[j:]
rep('Dopamine Chamber: four tracks in Set 3 (${N("Fontaines D.C.", "Six Shot")}-${N("Fontaines D.C. & ROSALIA", "Where")}). The Fujiya',
    'Dopamine Chamber: one track in Set 3 now (${N("Fontaines D.C.", "Happy")} Happy For You; you cut the other three). The Fujiya')
rep('Set 2 (${N("Big Boys", "Fun")}-${N("Viagra Boys", "Medicine")}). Held out', 'Set 2 (${N("Nervebreakers", "My Girl")}-${N("Viagra Boys", "Medicine")}), Austin, San Antonio and Dallas. Held out')
rep('The other nine Dopamine Chamber tracks screened clean on Genius Oct. 16.', 'Happy For You and the other Dopamine Chamber tracks screened clean on Genius Oct. 16.')
rep('No. 6 in the UK.", N("Pulp", "The Trees") + " The Trees"],', 'No. 6 in the UK.", "No track: The Trees was cut from the Air Order"],')
rep('`${N("Fontaines D.C.", "Six Shot")}-${N("Fontaines D.C. & ROSALIA", "Where")} (Set 3)`],', '`${N("Fontaines D.C.", "Happy")} Happy For You (Set 3)`],')
rep('  ["Queens of the Stone Age", "Perfecth', '''  ["Westside Cowboy", "It Goes On (debut album; Kick Stones (The Boys) is the lead single)", "Island", { t: "Fri. Aug. 21", bold: true }, `${N("Westside Cowboy", "Kick")} Kick Stones (The Boys)`],
  ["Royal Blood", "Dead Company (single Ten Over Ten out Aug. 12; album date: sources say Nov. 6, 12 or 13)", "Warner", { t: "Fri. Nov. 13 (verify)", bold: true }, `${N("Royal Blood", "Ten")} Ten Over Ten`],
  ["Queens of the Stone Age", "Perfecth''')
rep('  ["Fontaines D.C., Dopamine Chamber (4 tracks in set)", AMB("CLEAN, check by ear"), `${N("Fontaines D.C.", "Six")}-${N("Fontaines D.C. & ROSALIA", "Where")}`, "Genius lyrics were posted Oct. 16. Crowd-sourced: confirm by ear."],',
    '''  ["Fontaines D.C., Happy For You", AMB("CLEAN, check by ear"), N("Fontaines D.C.", "Happy"), "Genius lyrics were posted Oct. 16. Crowd-sourced: confirm by ear."],
  [{ t: "Loco Gringos, Ain't No Corndogs", bold: true }, AMB("LISTEN FIRST"), N("Loco Gringos", "Ain"), "No lyrics posted on Genius or Bandcamp. Short (2:28): cull if unsure."],
  [{ t: "This Is Lorelei & MJ Lenderman, Dancing in the Club (Radio Edit)", bold: true }, AMB("LISTEN FIRST"), N("This Is Lorelei & MJ Lenderman", "Dancing"), "Original has fuck x2 (Verse 4). YTM lists a Radio Edit: confirm both are covered."],
  ["Nervebreakers (My Girlfriend is a Rock) and Consolidated (Friendly Fascism), both Radio Edit on YTM", AMB("CLEAN, check by ear"), `${N("Nervebreakers", "My Girl")} and ${N("Consolidated", "Friendly")}`, "Genius lyrics screened clean; the edits are not verified."],''')
rep('"Zookeeper rechecked Oct. 21 for the seven changed tracks. Not in the library: Dopamine Chamber (label from the Zookeeper label table), Big Boys, Viagra Boys, Cheekface, Pretenders. Labels not in the Zookeeper label table: Damned, Warttmann Inc., Impossible Objects of Desire. Fill in at the studio if the library has them by Thursday."',
    '"Zookeeper rechecked Oct. 21 and 22 for changed tracks. Not in the library: Dopamine Chamber (label from the Zookeeper label table), Big Boys, Viagra Boys, Cheekface, Pretenders, Westside Cowboy, Royal Blood. Labels not in the Zookeeper label table: Damned, Wild Child Records, Warttmann Inc., Impossible Objects of Desire, Warner Records (library has Warner Bros. Records). Fill in at the studio if the library has them by Thursday."')
rep("13 albums reviewed in the last 10 weeks, one track each (week 2).", "13 albums reviewed in the last 10 weeks, one track each (week 2); This Is Lorelei has a second track tonight (Lenderman version). The Westside Cowboy review is a draft, not posted.")
open(p, 'w', encoding='utf-8').write(s)
print('patched')
