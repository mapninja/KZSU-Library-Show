// build_landscape.js
// Builds a landscape, table-based version of the Final Show Script for The Library (Oct. 15, 2026).
// Reads the show plan (plan_for_docx.json) and writes a Word file that opens in Google Docs.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, AlignmentType, PageOrientation, Footer, PageNumber, PageBreak, VerticalAlign,
} = require("docx");

// Input folder: pass it as the 2nd argument (node build.js out.docx <inputDir>). It holds
// plan_for_docx.json, mic_breaks.json and bench.json.
const IN = process.argv[3] || __dirname;
const plan = JSON.parse(fs.readFileSync(IN + "/plan_for_docx.json", "utf8"));

// Track numbers on air, counted the same way the set tables count them (SKIP and CUT tracks are skipped).
// N("Dinosaur Jr.", "Start Choppin") returns "#30". Talk-break tables use it so numbers never go stale.
const NUM = [];
{ let n = 0; for (const s of plan.sets) for (const t of s.tracks) { if (t.priority === "SKIP" || t.priority === "CUT") continue; n++; NUM.push({ n, artist: t.artist, track: t.track }); } }
const NN = (artist, prefix) => { const m = NUM.find((x) => x.artist === artist && x.track.toLowerCase().startsWith(prefix.toLowerCase())); if (!m) throw new Error("No track: " + artist + " " + prefix); return m.n; };
const N = (artist, prefix) => "#" + NN(artist, prefix);
const FONT = "Arial";
const PAGE_W = 14400; // usable width in DXA: 15840 (11 in) minus 0.5 in margins on each side

// ---- colors ----
const NAVY = "1F3864", BAND = "D9E2F3", ZEBRA = "F5F7FA", RED_BG = "F8D7DA", AMBER_BG = "FFF3CD";
const GREEN = "1B7F3B", RED = "B00020", AMBER = "8A6100";

// ---- small helpers ----
const border = { style: BorderStyle.SINGLE, size: 4, color: "B7B7B7" };
const borders = { top: border, bottom: border, left: border, right: border };

function run(text, o = {}) {
  return new TextRun({ text: String(text), font: FONT, size: o.size || 18, bold: o.bold, color: o.color, italics: o.italics });
}
function para(text, o = {}) {
  return new Paragraph({
    spacing: { before: o.before || 0, after: o.after || 0 },
    alignment: o.align,
    keepNext: o.keepNext,
    children: [run(text, o)],
  });
}
function cell(text, w, o = {}) {
  const lines = Array.isArray(text) ? text : [text];
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    borders,
    columnSpan: o.span,
    verticalAlign: VerticalAlign.CENTER,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: lines.map((l) => para(l, o)),
  });
}
function heading(text, size = 28, before = 0, pageBreak = false) {
  return new Paragraph({ pageBreakBefore: pageBreak, spacing: { before, after: 80 }, keepNext: true, children: [run(text, { size, bold: true, color: NAVY })] });
}
function note(text) {
  return new Paragraph({ spacing: { before: 60, after: 60 }, children: [run(text, { size: 16, italics: true, color: "555555" })] });
}
function spacer() { return new Paragraph({ spacing: { after: 120 }, children: [] }); }

// generic table: widths array, header array, rows array of arrays (strings or {t, fill, color, bold})
function simpleTable(widths, header, rows, o = {}) {
  const head = new TableRow({
    tableHeader: true, cantSplit: true,
    children: header.map((h, i) => cell(h, widths[i], { fill: NAVY, color: "FFFFFF", bold: true, size: 18, keepNext: o.keepTogether })),
  });
  const body = rows.map((r, ri) => new TableRow({
    cantSplit: true,
    children: r.map((c, i) => {
      const v = typeof c === "object" ? c : { t: c };
      return cell(v.t, widths[i], { size: o.size || 18, fill: v.fill || (ri % 2 ? ZEBRA : undefined), color: v.color, bold: v.bold, keepNext: o.keepTogether && ri < rows.length - 1 });
    }),
  }));
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows: [head, ...body] });
}

// ---- time helpers ----
const secs = (d) => { const m = /^(\d+):(\d+)$/.exec(d || ""); return m ? +m[1] * 60 + +m[2] : 0; };
const fmt = (s) => { const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
  return h ? `${h}:${String(m).padStart(2, "0")}:${String(x).padStart(2, "0")}` : `${m}:${String(x).padStart(2, "0")}`; };

// ---- FCC short label ----
function fcc(t) {
  const note = (t.fcc_note || "").toLowerCase();
  if (t.priority === "SKIP" || t.fcc_status === "FCC") return { t: "HOLD", color: RED, bold: true, fill: RED_BG };
  if (t.fcc_status === "UNVERIFIED") return { t: "LISTEN FIRST", color: AMBER, bold: true, fill: AMBER_BG };
  if (note.includes("check by ear")) return { t: "CLEAN, check ear", color: AMBER, bold: true, fill: AMBER_BG };
  return { t: "CLEAN", color: GREEN, bold: true };
}

// ---- main set tables (columns: #, Artist, Track, Album, Label, Tag, Time, FCC, Notes) ----
const W = [450, 1800, 2600, 2100, 1600, 900, 650, 1300, 3000]; // sums to 14400
const COLS = ["#", "Artist", "Track", "Album", "Label", "Tag", "Time", "FCC", "Notes"];

function setTable(set, startNum, cumStart) {
  const airable = set.tracks.filter((t) => t.priority !== "SKIP" && t.priority !== "CUT");
  const setSecs = airable.reduce((a, t) => a + secs(t.duration), 0);
  const cumEnd = cumStart + setSecs;
  let title = `${set.set}   |   ${airable.length} tracks   |   ${fmt(setSecs)}   |   on air through ${fmt(cumEnd)}`;
  const bandRows = [new TableRow({ cantSplit: true, tableHeader: false, children: [cell(title, PAGE_W, { span: 9, fill: BAND, bold: true, size: 22, color: NAVY, keepNext: true })] })];
  if (/Triple Shot/.test(set.set)) {
    bandRows.push(new TableRow({ cantSplit: true, children: [cell("Intro: " + plan.triple, PAGE_W, { span: 9, fill: BAND, size: 18, keepNext: true })] }));
  }
  const head = new TableRow({ tableHeader: true, cantSplit: true, children: COLS.map((h, i) => cell(h, W[i], { fill: NAVY, color: "FFFFFF", bold: true, keepNext: true })) });
  let n = startNum;
  const rows = set.tracks.map((t, ri) => {
    const kn = ri < set.tracks.length - 1;
    const held = t.priority === "SKIP" || t.priority === "CUT";
    const num = held ? "--" : String(n++);
    const f = fcc(t);
    const fill = held ? RED_BG : ri % 2 ? ZEBRA : undefined;
    const extra = held ? " FCC: " + t.fcc_note : (f.t === "CLEAN, check ear" ? " " + (t.fcc_note || "Check by ear.") : "");
    const notes = (held ? "HELD OUT of Zookeeper CSV. " : "") + (t.why || "") + extra;
    return new TableRow({ cantSplit: true, children: [
      cell(num, W[0], { fill, bold: true, keepNext: kn }),
      cell(t.artist, W[1], { fill, bold: true, keepNext: kn }),
      cell(t.track, W[2], { fill, bold: true, size: 20, keepNext: kn }),
      cell(t.album || "-", W[3], { fill, keepNext: kn }),
      cell(t.label || "-", W[4], { fill, keepNext: kn }),
      cell(t.tag || "-", W[5], { fill, keepNext: kn }),
      cell(held ? "--" : t.duration, W[6], { fill, keepNext: kn }),
      cell(f.t, W[7], { fill: f.fill || fill, color: f.color, bold: f.bold, keepNext: kn }),
      cell(notes, W[8], { fill, size: 16, keepNext: kn }),
    ] });
  });
  return { table: new Table({ width: { size: PAGE_W, type: WidthType.DXA }, columnWidths: W, rows: [...bandRows, head, ...rows] }),
    nextNum: n, cumEnd, count: airable.length, setSecs };
}


// ---- ticket giveaway (data/tickets/ticket_giveaways_2026-10.csv) ----
// No row lists Stace with a give-by date on or after Oct. 15 (Brit Floyd gave by 10/13), so the
// plan proposes the Dinosaur Jr. row (listed DJ: Suzi). Alternate: Hovvdy (Francis). Confirm before air.
const GIVE = { act: "Dinosaur Jr.", what: `indie rock (Set 5, ${N("Dinosaur Jr.", "Start Choppin")} Start Choppin')`, venue: "Guild Theatre, Menlo Park", date: "Mon. Oct. 19, 2026",
  giveBy: "Sun. Oct. 18", tix: "2", showTime: "Not on the sheet. Confirm before air.",
  djNote: "The ticket sheet lists Suzi, not Stace, for this show. No row lists Stace with a give-by date on or after tonight. Confirm with Suzi before air. Alternate row: Hovvdy, Chapel, S.F., Mon. Oct. 19, 2 tix, listed DJ Francis (" + N("Hovvdy", "Try Try Try") + " Try Try Try)." };
const GREEN_BG = "E2F0D9";
function micBreak(label, lines, fill = GREEN_BG) {
  return new Table({ width: { size: PAGE_W, type: WidthType.DXA }, columnWidths: [2600, 11800], rows: lines.map((l, i) => new TableRow({ cantSplit: true, children: [
    cell(i === 0 ? label : "", 2600, { fill, bold: true, size: 18, keepNext: i < lines.length - 1 }),
    cell(l, 11800, { fill, size: 20, keepNext: i < lines.length - 1 }),
  ] })) });
}
const TEASER1 = "Promo 1 (opening break): \"We have 2 tickets to give away to Dinosaur Jr. at the Guild Theatre in Menlo Park on Monday, Oct. 19. That giveaway is in the second hour.\" (Confirm the row with Suzi first.)";
const TEASER2 = "Promo 2 (end of Hour 1): \"Second hour is next, with the Thursday Triple Shot. Later in the hour, 2 tickets to Dinosaur Jr. at the Guild Theatre in Menlo Park, Monday, Oct. 19.\"";
const TEASER3 = "Promo 3 (after the Triple Shot): \"Next up, a set of Bay Area shows and new music, and in it we give away 2 tickets to see Dinosaur Jr. at the Guild Theatre in Menlo Park, Monday, Oct. 19.\"";
const MB = JSON.parse(fs.readFileSync(IN + "/mic_breaks.json", "utf8"));
const mb = (k) => MB[k].map((x) => x);

// ---- build body ----
const kids = [];
kids.push(new Paragraph({ spacing: { after: 40 }, children: [run("The Library with DJ Stace: Final Show Script", { size: 36, bold: true, color: NAVY })] }));
kids.push(para("Thursday, Oct. 15, 2026  |  KZSU 90.1 FM  |  6-8 p.m. PT  |  Final build Wed. Oct. 14, updated Thu. Oct. 15 (Air Order edits)  |  Punk and post-punk focus starts tonight  |  Landscape table version", { size: 18, color: "555555", after: 120 }));

let num = 1, cum = 0;
const built = [];
for (const set of plan.sets) { const b = setTable(set, num, cum); num = b.nextNum; cum = b.cumEnd; built.push({ set, ...b }); }
const total = cum;
const h1 = built.filter((b) => /^Hour 1/.test(b.set.set)).reduce((a, b) => a + b.setSecs, 0);

kids.push(heading("Run of show", 26));
kids.push(simpleTable([6200, 1500, 1800, 2400, 2500], ["Set", "Tracks", "Set time", "Track numbers", "Running total"],
  built.map((b) => { const first = b.nextNum - b.count, last = b.nextNum - 1; return [b.set.set, String(b.count), fmt(b.setSecs), `${first}-${last}`, fmt(b.cumEnd)]; })
    .concat([[{ t: "Total (airable)", bold: true }, { t: String(built.reduce((a, b) => a + b.count, 0)), bold: true }, { t: fmt(total), bold: true }, `Hour 1 ${fmt(h1)}, Hour 2 ${fmt(total - h1)}`, { t: "Target 2:30:00", bold: true }]])
));
kids.push(note("FCC column: green CLEAN, amber means listen first or check by ear, red means hold out. Tag is the KZSU library tag; a dash means not in the library. Cull to taste: the list runs " + fmt(total - 9000) + " over the 2:30 target."));

kids.push(heading("What changed since the Oct. 14 final", 24, 160));
kids.push(simpleTable([2600, 11800], ["Change", "Detail"], [
  [{ t: "Source", bold: true }, "Stace's Air Order edits on Oct. 15 (49 tracks). Her order for the first 40 tracks is kept. Her 9 tail tracks are placed in sets below. Air Order is read only, so its tail still sits at the end; this script and the Working playlist follow the show order."],
  ["Swapped by Stace", `IDLES "Colossus" for "The Beachland Ballroom" (${N("IDLES", "The Beachland")}). Bad Brains "Banned in D.C." for "I Against I" (${N("Bad Brains", "I Against")}). Triple Shot: Fontaines D.C. "Big" and "Jackie Down the Line" for "The Cuckoo Is A-Callin'" (${N("Fontaines D.C.", "The Cuckoo")}) and "Chequeless Reckless (Darklands Version)" (${N("Fontaines D.C.", "Chequeless")}). "Marianne" stays (${N("Fontaines D.C.", "Marianne")}).`],
  ["Cut by Stace", "Blondshell, \"Heart Has To Work So Hard\"; Brigitte Calls Me Baby, \"Altitude\"; Michael Kiwanuka, \"Summer Clothes\"; Beth Orton, \"Waiting\". Logged as not interested now (60-day cool-off to Dec. 14)."],
  ["Moved by Stace", `Stef Chura, "The Concrete" (${N("Stef Chura", "The Concrete")}) now follows Heavens to Betsy in the Bay Area set.`],
  [{ t: "Placed from her tail", bold: true }, `Set 1: Twisted Teens "Stalks" (${N("Twisted Teens", "Stalks")}). Set 4: BODEGA "Fear not the Fear" (${N("BODEGA", "Fear not")}), Sampa the Great "Location" (${N("Sampa the Great", "Location")}). Set 6: Sluice "Beadie" (${N("Sluice", "Beadie")}), MJ Lenderman "She's Leaving You" (${N("MJ Lenderman", "She's")}), Cameron Winter live (${N("Cameron Winter", "Love Takes")}), SAULT "Wildfires" (${N("SAULT", "Wildfires")}). Set 8: Firewater "Another Perfect Catastrophe" (${N("Firewater", "Another")}).`],
  [{ t: "New Set 7 (her request)", bold: true }, `Machines and motorik: Kraftwerk "Numbers" (${N("Kraftwerk", "Numbers")}), Cabaret Voltaire "Nag, Nag, Nag" (${N("Cabaret Voltaire", "Nag")}), then Fujiya & Miyagi "No Green Light" (${N("Fujiya & Miyagi", "No Green")}). Fujiya & Miyagi moved here from the new-music set.`],
  ["FCC update", { t: `Fujiya & Miyagi (${N("Fujiya & Miyagi", "No Green")}): no posted lyrics, LISTEN FIRST. Cameron Winter live (${N("Cameron Winter", "Love Takes")}) and Chequeless Reckless (${N("Fontaines D.C.", "Chequeless")}) were screened on other versions of the lyrics: check by ear. The Fall (${N("The Fall", "30 Degrees")}) and R.M.F.C. "Mirror" (${N("R.M.F.C.", "Mirror")}) still have no posted lyrics. All other new tracks screened CLEAN.`, color: AMBER, bold: true }],
  ["Labels to fill in", "Kraftwerk \"Numbers,\" Fontaines D.C. \"Chequeless Reckless,\" R.M.F.C. \"The Clue\" and \"Mirror.\" Labels marked (verify) came from the web. Zookeeper was blocked by its browser check, so tags were not re-checked."],
  [{ t: "Ticket giveaway", bold: true }, { t: "Dinosaur Jr., Guild Theatre, Menlo Park, Mon. Oct. 19, 2 tix. No row lists Stace this week, so the sheet's listed DJ (Suzi) must confirm. Promo teasers at the opening break, the end of Hour 1 and after the Triple Shot.", bold: true }],
]));

kids.push(heading("Talk break: Today in music", 24, 200));
kids.push(simpleTable([2600, 3300, 6000, 2500], ["Artist or place", "Item", "Fact", "In tonight's set"], [
  ["CBGB, New York", "Final night", "Closed Oct. 15, 2006 (20 years today). Patti Smith played the last show, a three-hour set that ran past 1 a.m.", N("Patti Smith", "Gloria") + " Gloria"],
  ["Bad Brains", "CBGB closing week", "Played a three-night residency in the club's final week, starting Oct. 9, 2006. Tonight: I Against I (1986).", N("Bad Brains", "I Against") + " I Against I"],
  ["The Jon Spencer Blues Explosion", "Now I Got Worry", "Released Oct. 15, 1996 on Matador (30 years today).", N("The Jon Spencer Blues Explosion", "2Kindsa") + " 2Kindsa Love"],
  ["Death Cab for Cutie", "The Photo Album", "Released Oct. 9, 2001 (25 years).", N("Death Cab for Cutie", "Coney") + " Coney Island"],
  ["Sex Pistols", "EMI signing", "Signed to EMI Oct. 8, 1976 (50 years). The reunion lineup played the Warfield last night, Oct. 14.", N("Sex Pistols", "Pretty") + " Pretty Vacant"],
  ["Stiff Little Fingers", "Alternative Ulster", "Released Oct. 17, 1978, two days from now.", N("Stiff Little Fingers", "Alternative") + " Alternative Ulster"],
]));
kids.push(note("Next week: The Damned, New Rose turns 50 on Oct. 22 (held out of tonight's show). Focus calendar: Texas punk Oct. 22, Halloween post-punk Oct. 29, D.C. hardcore Nov. 5."));

kids.push(heading("Talk break: new and coming up", 24, 200));
kids.push(simpleTable([2300, 3600, 2200, 2100, 4200], ["Artist", "Release", "Label", "Date", "In tonight's set"], [
  ["Fontaines D.C.", "Dopamine Chamber", "XL", { t: "Fri. Oct. 16", bold: true }, `${N("Fontaines D.C.", "Marianne")} Marianne (Triple Shot closer)`],
  ["Heavens to Betsy", "baby's gone (first release since 1994)", "Kill Rock Stars", { t: "Fri. Oct. 16", bold: true }, `${N("Heavens to Betsy", "ain")} ain't never goin' back`],
  ["Dummy", "Full Spectrum Dominance (album)", "Polyvinyl", { t: "Fri. Oct. 16", bold: true }, `${N("Dummy", "Full")} Full Spectrum Dominance`],
  ["Sampa the Great", "Nu Zamrock (Location is the third single)", "Loma Vista", { t: "Fri. Oct. 30", bold: true }, `${N("Sampa the Great", "Location")} Location`],
  ["Fujiya & Miyagi", "New Shiny Object (verify)", "Impossible Objects of Desire (verify)", { t: "Fri. Oct. 30", bold: true }, `${N("Fujiya & Miyagi", "No Green")} No Green Light`],
  ["Twisted Teens", "The Holy Cross Tigers", "Sub Pop", { t: "Fri. Nov. 6", bold: true }, `${N("Twisted Teens", "Stalks")} Stalks`],
  ["Cameron Winter", "Live at Carnegie Hall (December 2025 show)", "Partisan", "Fri. Oct. 9", `${N("Cameron Winter", "Love Takes")} Love Takes Miles`],
  ["The Tallest Man on Earth", "Deliver Me From Trying", "Anti-", "Fri. Oct. 9", `${N("The Tallest Man on Earth", "Deliver")} Deliver Me From Trying`],
  ["Stef Chura", "Dancing Alone on the Concrete", "Saddle Creek", "Fri. Oct. 2", `${N("Stef Chura", "The Concrete")} The Concrete`],
  ["Julia Jacklin", "The Gem", "4AD", "Fri. Sept. 25", `${N("Julia Jacklin", "Get Away")} Get Away From Me`],
  ["Queens of the Stone Age", "Perfecth", "Matador", "Oct. 30", { t: "Easy Street is FCC (fuck x1). Not in set.", color: RED }],
]));
kids.push(spacer());
kids.push(micBreak("MIC BREAK: OPENING", mb("opening").concat([TEASER1])));

// ---- Hour 1 ----
kids.push(heading("HOUR 1", 30, 0, true));
built.filter((b) => /^Hour 1/.test(b.set.set)).forEach((b) => {
  kids.push(b.table); kids.push(spacer());
  if (/Set 2/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 2 (UK 1977)", mb("after_uk_set"))); kids.push(spacer()); }
  if (/Set 3/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 3 (CBGB)", mb("after_cbgb_set"))); kids.push(spacer()); }
  if (/Set 4/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: END OF HOUR 1", mb("end_hour_1").concat([TEASER2]))); }
});

// ---- Hour 2 ----
kids.push(heading("HOUR 2", 30, 0, true));
built.filter((b) => !/^Hour 1/.test(b.set.set)).forEach((b) => {
  kids.push(b.table); kids.push(spacer());
  if (/Triple Shot/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER THE TRIPLE SHOT", mb("after_triple_shot").concat([TEASER3]))); kids.push(spacer()); }
  if (/Set 6/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 6 (SONGWRITERS)", mb("after_songwriters_set"))); kids.push(spacer()); }
  if (/Set 7/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 7 (MACHINES)", mb("after_machines_set"))); kids.push(spacer()); }
  if (/Set 5/.test(b.set.set)) {
    kids.push(heading("Talk break after Set 5: Bay Area shows (foopee.com, checked Oct. 8; confirm before air)", 22));
    kids.push(simpleTable([2300, 3500, 4300, 1500, 2800], ["Date", "Act", "Venue", "Status", "Track tonight"], [
      ["Wed. Oct. 14", "Dummy (with Golomb, Figure Eight, Sachi's Mirror)", "Chapel, S.F.", "Last night", N("Dummy", "Full") + " Full Spectrum Dominance"],
      [{ t: "Thu. Oct. 15", bold: true }, "Boy Harsher (with True Blue, Kassie Krut)", "Fox Theater, Oakland", { t: "Tonight, 7 p.m.", bold: true }, N("Boy Harsher", "Pain") + " Pain"],
      [{ t: "Thu. Oct. 15", bold: true }, "Imperial Teen (with Kids On A Crime Spree, Crows)", "Bottom of the Hill, S.F.", { t: "Sold out", color: RED }, "Not in set"],
      ["Sat. Oct. 17", "Heavens To Betsy (with Street Eaters, Lilies)", "Bottom of the Hill, S.F.", { t: "Sold out", color: RED }, N("Heavens to Betsy", "ain") + " ain't never goin' back"],
      ["Sun. Oct. 18", "Heavens To Betsy (with For Horses, Cut-Rate Druggist)", "Bottom of the Hill, S.F.", "$35. Check availability", N("Heavens to Betsy", "ain") + " ain't never goin' back"],
      ["Sun. Oct. 18", "Dinosaur Jr. with Stef Chura", "Castro, S.F.", { t: "Sold out", color: RED }, N("Dinosaur Jr.", "Start") + " Start Choppin', " + N("Stef Chura", "The Concrete") + " The Concrete"],
      [{ t: "Mon. Oct. 19", bold: true }, "Dinosaur Jr. (KZSU giveaway)", "Guild Theatre, Menlo Park", { t: "Tickets tonight", bold: true }, N("Dinosaur Jr.", "Start") + " Start Choppin'"],
      ["Mon. Oct. 19", "Hovvdy (alternate giveaway row)", "Chapel, S.F.", "", N("Hovvdy", "Try") + " Try Try Try"],
    ], { keepTogether: true }));
    kids.push(spacer());
    kids.push(micBreak("MIC BREAK: BAY AREA", mb("bay_area_break")));
    kids.push(spacer());
    kids.push(heading("TICKET GIVEAWAY (after Set 5)", 22));
    kids.push(simpleTable([2300, 3000, 2800, 2000, 1000, 3300], ["Act", "Type", "Venue", "Date", "Tickets", "Give by"], [
      [{ t: GIVE.act, bold: true }, GIVE.what, GIVE.venue, { t: GIVE.date, bold: true }, GIVE.tix, { t: GIVE.giveBy + " (winner picked by then)", bold: true }],
    ], { keepTogether: true }));
    kids.push(micBreak("MIC BREAK: GIVEAWAY", [
      "Read: \"That was Stef Chura and Dinosaur Jr. earlier in this set. Dinosaur Jr. plays the Guild Theatre in Menlo Park on Monday, Oct. 19. We have 2 tickets to give away.\"",
      GIVE.djNote,
      "Contest method and call-in number: use the KZSU contest procedure (not on the ticket sheet). Confirm before air.",
      "Show time: " + GIVE.showTime,
      "After the winner: follow the usual KZSU steps for logging the giveaway and ticket pickup.",
    ]));
    kids.push(spacer());
  }
});

// ---- Back of the sheet ----
kids.push(heading("FCC watch list", 28, 0, true));
const AMB = (t) => ({ t, color: AMBER, bold: true });
kids.push(simpleTable([2800, 3200, 1900, 6500], ["Artist and track", "Status", "Where", "Action"], [
  [{ t: "Fujiya & Miyagi, No Green Light", bold: true }, AMB("LISTEN FIRST"), N("Fujiya & Miyagi", "No Green"), "No lyrics posted on Genius or LRCLIB. Checked Oct. 15. Long (5:51): cull candidate if unsure."],
  [{ t: "The Fall, 30 Degrees", bold: true }, AMB("LISTEN FIRST"), N("The Fall", "30 Degrees"), "No lyrics posted on Genius (unreleased) or LRCLIB. Checked Oct. 14."],
  [{ t: "R.M.F.C., Mirror", bold: true }, AMB("LISTEN FIRST"), N("R.M.F.C.", "Mirror"), "No lyrics posted. Short song (2:23). Cull if unsure."],
  ["Cameron Winter, Love Takes Miles (Live)", AMB("CLEAN, check by ear"), N("Cameron Winter", "Love Takes"), "Screened on the studio version's lyrics (LRCLIB, 214 words). Live version may add talk."],
  ["Fontaines D.C., Chequeless Reckless (Darklands)", AMB("CLEAN, check by ear"), N("Fontaines D.C.", "Chequeless"), "Screened on a live version's lyrics (LRCLIB, 205 words)."],
  ["R.M.F.C., The Clue", AMB("CLEAN, check by ear"), N("R.M.F.C.", "The Clue"), "LRCLIB 76 words, no flagged words. Short transcription."],
  ["Death Cab for Cutie, Coney Island", AMB("CLEAN, check by ear"), N("Death Cab for Cutie", "Coney"), "Genius 70 words; may be a partial transcription."],
  ["Goat, I Sing in Silence", AMB("CLEAN, check by ear"), N("Goat", "I Sing"), "Genius 82 words; may be partial."],
  ["Dead Meadow, Everything's Goin On", AMB("CLEAN, check by ear"), N("Dead Meadow", "Everything"), "Genius 76 words; may be partial."],
  ["Perfume Genius, Queen", AMB("CLEAN, check by ear"), N("Perfume Genius", "Queen"), "Genius 85 words; short transcription."],
  ["Sex Pistols, Anarchy in the U.K.", { t: "piss x1", color: RED }, "Held out", `Pretty Vacant (${N("Sex Pistols", "Pretty")}) stands in.`],
  ["Stiff Little Fingers, Suspect Device", { t: "fuck x1", color: RED }, "Held out", `Alternative Ulster (${N("Stiff Little Fingers", "Alternative")}) stands in.`],
  ["Dinosaur Jr., Freak Scene", { t: "fuck x2 (Bridge, Outro)", color: RED }, "Held out", `Start Choppin' (${N("Dinosaur Jr.", "Start")}) stands in.`],
  ["Fontaines D.C., Tongue", { t: "shit x10 (Refrain)", color: RED }, "FCC Edit Needed", "Not airable as is. The Triple Shot is Cuckoo, Chequeless Reckless and Marianne."],
  ["Fontaines D.C., Starburster and I Love You", { t: "Held (see plan)", color: RED }, "Held out", "Not in the Triple Shot."],
  ["Wishy, Lovesick; Jesse Welles, The Nerd Reich; BODEGA, All Inside Aquarium", { t: "Held (see plan)", color: RED }, "Held out", "Not in set. BODEGA's Fear not the Fear is clean and in Set 4."],
]));

kids.push(heading("Bench: Weekly Playlist picks not in the Air Order", 28, 240));
kids.push(note("Fridays and Tuesdays sweeps through Oct. 13. Labels marked (verify) are from the web, not Zookeeper. Replacement pool if you cut tracks tonight."));
const SCR = "Screened";
const bench = JSON.parse(fs.readFileSync(IN + "/bench.json", "utf8"));
kids.push(simpleTable([2300, 3400, 3200, 2400, 1700, 1400], ["Artist", "Track", "Release", "Label", "Date", "FCC"], bench.map((t) => {
  const st = t.fcc_status;
  const f = st === "CLEAN" ? { t: "CLEAN", color: GREEN, bold: true } : st === "CAUTION" ? { t: "CAUTION", color: AMBER, bold: true } : st === "FCC" ? { t: "HOLD", color: RED, bold: true } : { t: "LISTEN FIRST", color: AMBER, bold: true };
  const hold = /HOLD/.test(t.why || "") ? " (hold for Oct. 22)" : "";
  return [t.artist, t.track + hold, t.album || "-", (t.label || "-").replace(" (verify)", ""), String(t.released || "-"), f];
})));
kids.push(note("CAUTION means a station-policy word (goddamn or bitch), not an FCC word. LISTEN FIRST means no lyrics were posted or the track was not screened."));

const doc = new Document({
  creator: "DJ Stace (Claude)",
  title: "Library Show Final Show Script 2026-10-15 (Landscape Tables)",
  styles: { default: { document: { run: { font: FONT, size: 18 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE },
      margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [run("The Library with DJ Stace  |  Oct. 15, 2026  |  Page ", { size: 14, color: "777777" }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: "777777" })] })] }) },
    children: kids,
  }],
});

const out = process.argv[2];
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out, buf.length, "bytes; total airable", fmt(total)); });
