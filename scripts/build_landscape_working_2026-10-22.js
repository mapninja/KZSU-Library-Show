// build_landscape_working_2026-10-22.js
// Builds the landscape, table-based WORKING Show Script for The Library (Thursday, Oct. 22, 2026).
// Reads the show plan directly: data/recon/2026-10-22/working_playlist.json
// Run from the repo root:  node scripts/build_landscape_working_2026-10-22.js "<out>.docx"
//
// Beginner notes:
// * "docx" is an npm library that writes Word files. A Table is rows of cells; a cell holds paragraphs.
// * N("Artist", "Track prefix") looks up a track's on-air number so talk-break tables never go stale.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, AlignmentType, PageOrientation, Footer, PageNumber, VerticalAlign,
} = require("docx");

const REPO = path.resolve(__dirname, "..");
const plan = JSON.parse(fs.readFileSync(path.join(REPO, "data/recon/2026-10-22/working_playlist.json"), "utf8"));
const MB = plan.mic_breaks;
const mb = (k) => MB[k].slice();

// ---- track numbers, counted the same way the set tables count (SKIP and CUT are skipped) ----
const NUM = [];
{ let n = 0; for (const s of plan.sets) for (const t of s.tracks) { if (t.priority === "SKIP" || t.priority === "CUT") continue; n++; NUM.push({ n, artist: t.artist, track: t.track }); } }
const NN = (artist, prefix) => { const m = NUM.find((x) => x.artist === artist && x.track.toLowerCase().startsWith(prefix.toLowerCase())); if (!m) throw new Error("No track: " + artist + " " + prefix); return m.n; };
const N = (artist, prefix) => "#" + NN(artist, prefix);

const FONT = "Arial";
const PAGE_W = 14400; // usable width in DXA (11 in minus 0.5 in margins)
const NAVY = "1F3864", BAND = "D9E2F3", ZEBRA = "F5F7FA", RED_BG = "F8D7DA", AMBER_BG = "FFF3CD", GREEN_BG = "E2F0D9";
const GREEN = "1B7F3B", RED = "B00020", AMBER = "8A6100";
const border = { style: BorderStyle.SINGLE, size: 4, color: "B7B7B7" };
const borders = { top: border, bottom: border, left: border, right: border };

function run(text, o = {}) { return new TextRun({ text: String(text), font: FONT, size: o.size || 18, bold: o.bold, color: o.color, italics: o.italics }); }
function para(text, o = {}) { return new Paragraph({ spacing: { before: o.before || 0, after: o.after || 0 }, alignment: o.align, keepNext: o.keepNext, children: [run(text, o)] }); }
function cell(text, w, o = {}) {
  const lines = Array.isArray(text) ? text : [text];
  return new TableCell({
    width: { size: w, type: WidthType.DXA }, borders, columnSpan: o.span, verticalAlign: VerticalAlign.CENTER,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: lines.map((l) => para(l, o)),
  });
}
function heading(text, size = 28, before = 0, pageBreak = false) {
  return new Paragraph({ pageBreakBefore: pageBreak, spacing: { before, after: 80 }, keepNext: true, children: [run(text, { size, bold: true, color: NAVY })] });
}
function note(text) { return new Paragraph({ spacing: { before: 60, after: 60 }, children: [run(text, { size: 16, italics: true, color: "555555" })] }); }
function spacer() { return new Paragraph({ spacing: { after: 120 }, children: [] }); }

function simpleTable(widths, header, rows, o = {}) {
  const head = new TableRow({ tableHeader: true, cantSplit: true,
    children: header.map((h, i) => cell(h, widths[i], { fill: NAVY, color: "FFFFFF", bold: true, size: 18, keepNext: o.keepTogether })) });
  const body = rows.map((r, ri) => new TableRow({ cantSplit: true,
    children: r.map((c, i) => { const v = typeof c === "object" ? c : { t: c };
      return cell(v.t, widths[i], { size: o.size || 18, fill: v.fill || (ri % 2 ? ZEBRA : undefined), color: v.color, bold: v.bold, keepNext: o.keepTogether && ri < rows.length - 1 }); }) }));
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows: [head, ...body] });
}
function micBreak(label, lines, fill = GREEN_BG) {
  return new Table({ width: { size: PAGE_W, type: WidthType.DXA }, columnWidths: [2600, 11800], rows: lines.map((l, i) => new TableRow({ cantSplit: true, children: [
    cell(i === 0 ? label : "", 2600, { fill, bold: true, size: 18, keepNext: i < lines.length - 1 }),
    cell(l, 11800, { fill, size: 20, keepNext: i < lines.length - 1 }) ] })) });
}

const secs = (d) => { const m = /^(\d+):(\d+)$/.exec(d || ""); return m ? +m[1] * 60 + +m[2] : 0; };
const fmt = (s) => { const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
  return h ? `${h}:${String(m).padStart(2, "0")}:${String(x).padStart(2, "0")}` : `${m}:${String(x).padStart(2, "0")}`; };

// FCC short label for the table
function fcc(t) {
  const note = (t.fcc_note || "").toLowerCase();
  if (t.priority === "SKIP" || t.fcc_status === "FCC") return { t: "HOLD", color: RED, bold: true, fill: RED_BG };
  if (t.fcc_status === "UNVERIFIED") return { t: "LISTEN FIRST", color: AMBER, bold: true, fill: AMBER_BG };
  if (note.includes("check by ear") || note.includes("partial")) return { t: "CLEAN, check ear", color: AMBER, bold: true, fill: AMBER_BG };
  return { t: "CLEAN", color: GREEN, bold: true };
}

const W = [450, 1800, 2600, 2100, 1600, 900, 650, 1300, 3000];
const COLS = ["#", "Artist", "Track", "Album", "Label", "Tag", "Time", "FCC", "Notes"];
function setTable(set, startNum, cumStart) {
  const airable = set.tracks.filter((t) => t.priority !== "SKIP" && t.priority !== "CUT");
  const setSecs = airable.reduce((a, t) => a + secs(t.duration), 0);
  const cumEnd = cumStart + setSecs;
  const title = `${set.set}   |   ${airable.length} tracks   |   ${fmt(setSecs)}   |   on air through ${fmt(cumEnd)}`;
  const bandRows = [new TableRow({ cantSplit: true, children: [cell(title, PAGE_W, { span: 9, fill: BAND, bold: true, size: 22, color: NAVY, keepNext: true })] })];
  if (/Triple Shot/.test(set.set)) bandRows.push(new TableRow({ cantSplit: true, children: [cell("Intro: " + plan.triple_shot.angle, PAGE_W, { span: 9, fill: BAND, size: 18, keepNext: true })] }));
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
      cell(num, W[0], { fill, bold: true, keepNext: kn }), cell(t.artist, W[1], { fill, bold: true, keepNext: kn }),
      cell(t.track, W[2], { fill, bold: true, size: 20, keepNext: kn }), cell(t.album || "-", W[3], { fill, keepNext: kn }),
      cell(t.label || "-", W[4], { fill, keepNext: kn }), cell(t.tag || "-", W[5], { fill, keepNext: kn }),
      cell(held ? "--" : t.duration, W[6], { fill, keepNext: kn }),
      cell(f.t, W[7], { fill: f.fill || fill, color: f.color, bold: f.bold, keepNext: kn }),
      cell(notes, W[8], { fill, size: 16, keepNext: kn }) ] });
  });
  return { table: new Table({ width: { size: PAGE_W, type: WidthType.DXA }, columnWidths: W, rows: [...bandRows, head, ...rows] }), nextNum: n, cumEnd, count: airable.length, setSecs };
}

// ---- build body ----
const kids = [];
kids.push(new Paragraph({ spacing: { after: 40 }, children: [run("The Library with DJ Stace: Working Show Script", { size: 36, bold: true, color: NAVY })] }));
kids.push(para("Thursday, Oct. 22, 2026  |  KZSU 90.1 FM  |  6-8 p.m. PT  |  Draft built Fri. Oct. 16 (Thursday-night run)  |  Texas punk week (punk and post-punk arc, week 2 of 4)  |  Landscape table version", { size: 18, color: "555555", after: 120 }));

let num = 1, cum = 0; const built = [];
for (const set of plan.sets) { const b = setTable(set, num, cum); num = b.nextNum; cum = b.cumEnd; built.push({ set, ...b }); }
const total = cum;
const h1 = built.filter((b) => /^Hour 1/.test(b.set.set)).reduce((a, b) => a + b.setSecs, 0);

kids.push(heading("Run of show", 26));
kids.push(simpleTable([6200, 1500, 1800, 2400, 2500], ["Set", "Tracks", "Set time", "Track numbers", "Running total"],
  built.map((b) => { const first = b.nextNum - b.count, last = b.nextNum - 1; return [b.set.set, String(b.count), fmt(b.setSecs), `${first}-${last}`, fmt(b.cumEnd)]; })
    .concat([[{ t: "Total (airable)", bold: true }, { t: String(built.reduce((a, b) => a + b.count, 0)), bold: true }, { t: fmt(total), bold: true }, `Hour 1 ${fmt(h1)}, Hour 2 ${fmt(total - h1)}`, { t: "Target 2:30:00", bold: true }]])));
kids.push(note("FCC column: green CLEAN, amber means listen first or check by ear, red means hold out. Tag is the KZSU library tag; a dash means not in the library. Cull to taste: the list runs " + fmt(total - 9000) + " over the 2:30 target. Bench tracks (back page) are not in the Air Order."));

kids.push(heading("What is in this draft", 24, 160));
kids.push(simpleTable([2600, 11800], ["Item", "Detail"], [
  [{ t: "Your requests (Oct. 16)", bold: true }, `Fontaines D.C. Dopamine Chamber: four tracks in Set 3 (${N("Fontaines D.C.", "Six Shot")}-${N("Fontaines D.C. & ROSALIA", "Where")}). The Fujiya & Miyagi, Kraftwerk, Cabaret Voltaire set is back as Set 7 (${N("Kraftwerk", "Numbers")}-${N("Fujiya & Miyagi", "No Green")}). Reviewed albums stay in tapering rotation. Bay Area highlights list upcoming shows only.`],
  [{ t: "Reviewed albums in rotation", bold: true }, "13 albums reviewed in the last 10 weeks, one track each (week 2). Table below. Taper: weeks 1 to 3 one track per album; weeks 4 to 6 about half; weeks 7 to 10 about one in four. Config: config/review_rotation.json."],
  [{ t: "Triple Shot", bold: true }, `The Damned (${N("The Damned", "New Rose")}-${N("The Damned", "Love Song")}). New Rose was released Oct. 22, 1976: 50 years on show day.`],
  [{ t: "Texas punk", bold: true }, `Set 2 (${N("Big Boys", "Fun")}-${N("Viagra Boys", "Medicine")}). Held out for FCC words: Scratch Acid Crazy Dan, Jesus Lizard Mouth Breather and Seasick.`],
  [{ t: "Fontaines D.C. FCC", bold: true }, { t: "Tongue (shit x10, Refrain) and Japan (fuck x3, shit x3, Chorus) are held out. The other nine Dopamine Chamber tracks screened clean on Genius Oct. 16.", color: RED }],
  [{ t: "Ticket giveaway", bold: true }, "None placed. No row on the ticket sheet lists Stace with a give-by date on or after Oct. 22. Rows for passed shows (Dinosaur Jr., Hovvdy) are skipped. Option: Slow Pulp, Fillmore, Oct. 28 (listed DJ Cleo): confirm with Cleo."],
  [{ t: "Carried over", bold: true }, "Tracks that did not air Oct. 15: Dummy, Heavens to Betsy, Julia Jacklin, Goat, Allah-Las, Twin Peaks, feeble little horse, Star Moles, R.M.F.C. The Clue. Fujiya & Miyagi aired as the last spin Oct. 15 but stays in your set."],
  [{ t: "Labels and tags", bold: true }, "Zookeeper checked Oct. 16. Not in the library yet: Dopamine Chamber (label from the Zookeeper label table), Big Boys, Viagra Boys, Cheekface, Pretenders. Fill in at the studio if the library has them by Thursday."],
]));

kids.push(heading("Talk break: Today in music", 24, 200));
kids.push(simpleTable([2600, 3300, 6000, 2500], ["Artist or place", "Item", "Fact", "In tonight's set"], [
  ["The Damned", "New Rose", "Released Oct. 22, 1976 on Stiff Records (50 years today). First UK punk single. Nick Lowe produced it at Pathway Studios in London, reportedly in one day. The B-side is a fast cover of the Beatles' Help!", N("The Damned", "New Rose") + " New Rose"],
  ["Pulp", "We Love Life", "Released Oct. 22, 2001 on Island (25 years today). Scott Walker produced. It reached No. 6 in the UK.", N("Pulp", "The Trees") + " The Trees"],
  ["Pretenders", "Get Close", "UK release Oct. 20, 1986 (40 years). Verify the date before air.", N("Pretenders", "Don't") + " Don't Get Me Wrong"],
  ["Scratch Acid, The Jesus Lizard", "Austin lineage", "David Yow sang for Scratch Acid, then fronted The Jesus Lizard. Goat is on Touch and Go (1991).", N("Scratch Acid", "Mary") + " and " + N("The Jesus Lizard", "Monkey")],
]));
kids.push(note("Focus calendar: Texas punk tonight, Halloween post-punk Oct. 29, D.C. hardcore Nov. 5."));

kids.push(heading("Talk break: new and coming up", 24, 200));
kids.push(simpleTable([2300, 3600, 2200, 2100, 4200], ["Artist", "Release", "Label", "Date", "In tonight's set"], [
  ["Fontaines D.C.", "Dopamine Chamber (fifth album, James Ford producing)", "XL", { t: "Fri. Oct. 16", bold: true }, `${N("Fontaines D.C.", "Six Shot")}-${N("Fontaines D.C. & ROSALIA", "Where")} (Set 3)`],
  ["Dummy", "do you love the color of the sky? (album)", "Polyvinyl", { t: "Fri. Oct. 16", bold: true }, `${N("Dummy", "Full")} Full Spectrum Dominance`],
  ["Heavens to Betsy", "baby's gone (first new release in 32 years, per Consequence)", "Kill Rock Stars", { t: "Fri. Oct. 16", bold: true }, `${N("Heavens to Betsy", "baby")} baby's gone`],
  ["The Avalanches", "No Bad Memories", "Modular", { t: "Fri. Oct. 16", bold: true }, `${N("The Avalanches", "Blue")} Blue Shadows (Karen O)`],
  ["Fujiya & Miyagi", "New Shiny Object (verify)", "Impossible Objects of Desire (verify)", { t: "Fri. Oct. 30", bold: true }, `${N("Fujiya & Miyagi", "No Green")} No Green Light`],
  ["Twisted Teens", "The Holy Cross Tigers", "Sub Pop", { t: "Fri. Nov. 6", bold: true }, `${N("Twisted Teens", "Peekaboo")} and ${N("Twisted Teens", "Top")} (reviewed albums)`],
  ["Lex Walton", "Ultimate Love Forever (CD and LP)", "Sub Pop", { t: "Fri. Nov. 20", bold: true }, `${N("Lex Walton", "For Thee")} For Thee I Sing`],
]));
kids.push(spacer());

kids.push(heading("Reviewed albums in rotation (last 10 weeks)", 24, 120));
const REV = [
  ["Twisted Teens", "Blame the Clown", "Oct. 6", "Peekaboo Hand", "5"], ["Twisted Teens", "Florida Water Blues", "Oct. 8", "Top Of The World Hwy No. 2", "5"],
  ["Lex Walton", "Ultimate Love Forever", "Oct. 8", "For Thee I Sing", "5"], ["Yard Act", "You're Gonna Need A Little Music", "Oct. 15", "New Beginnings", "5"],
  ["Little Barrie", "Gravity Freeze", "Oct. 8", "More Bad Miles Of Road", "5"], ["Palace", "Ox", "Oct. 8", "Denny's", "5"],
  ["Sluice", "Companion", "Oct. 8", "Zillow", "5"], ["This Is Lorelei", "The Singer in My Band", "Oct. 8", "Don't You Cry in Lonesomeness", "4"],
  ["Dread Spectre Council", "Thetans", "Oct. 8", "Hooves & Cloves", "5"], ["Tricky", "Different When It's Silent", "Oct. 8", "Because I Don't Know", "5"],
  ["Ty Segall", "Chrome", "Oct. 8", "Separation", "3"], ["The Fall", "Post Script", "Oct. 15", "A Caveat", "4"], ["Sylvan Esso", "Ow ∞", "Oct. 15", "Concrete Glen", "4"],
];
kids.push(simpleTable([2600, 3600, 1500, 3700, 1000, 2000], ["Artist", "Album", "Posted", "Track tonight", "Stars", "On air"],
  REV.map((r) => [r[0], r[1], r[2], r[3], r[4], N(r[0], r[3].slice(0, 6))])));
kids.push(note("Posted = date the review went into Zookeeper. Review rotation ends 10 weeks after posting (mid to late December). Tracks already aired this month were skipped: Play Cowboys, Hex's Up, Oh No Now My, Hey Sarah, Made My Bed, Luggin' Hurt, Adrian Borland, Over The Barrel, Beadie, 30 Degrees."));
kids.push(spacer());
kids.push(micBreak("MIC BREAK: OPENING", mb("opening")));

// ---- Hour 1 ----
kids.push(heading("HOUR 1", 30, 0, true));
built.filter((b) => /^Hour 1/.test(b.set.set)).forEach((b) => {
  kids.push(b.table); kids.push(spacer());
  if (/Set 2/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 2 (TEXAS PUNK)", mb("after_texas_set"))); kids.push(spacer()); }
  if (/Set 3/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 3 (FONTAINES D.C.)", mb("after_fontaines"))); kids.push(spacer()); }
  if (/Set 4/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: END OF HOUR 1", mb("end_hour_1").concat(["Tease: Thursday Triple Shot opens Hour 2: The Damned, 50 years of New Rose."]))); }
});

// ---- Hour 2 ----
kids.push(heading("HOUR 2", 30, 0, true));
built.filter((b) => !/^Hour 1/.test(b.set.set)).forEach((b) => {
  if (/Triple Shot/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: TRIPLE SHOT INTRO", mb("triple_shot_intro"))); kids.push(spacer()); }
  kids.push(b.table); kids.push(spacer());
  if (/Set 6/.test(b.set.set)) {
    kids.push(heading("Talk break after Set 6: Bay Area shows, upcoming only (foopee.com, checked Oct. 16; confirm before air)", 22));
    kids.push(simpleTable([2300, 3700, 3900, 1700, 2800], ["Date", "Act", "Venue", "Status", "Track tonight"], [
      [{ t: "Fri. Oct. 23", bold: true }, "Cheekface with BODEGA", "Cornerstone, Berkeley", { t: "$36, 8 p.m. doors. Foopee also lists Waitress as support: confirm", bold: true }, N("Cheekface", "No Fly") + " No Fly Zone, " + N("BODEGA", "Territorial") + " Territorial Call of the Female"],
      [{ t: "Fri. Oct. 23", bold: true }, "Frightwig, AroMa, scary story time", "Chapel, S.F.", "$25, 7 p.m.", N("Frightwig", "Big") + " Big Bang"],
      [{ t: "Fri. Oct. 23", bold: true }, "Julia Jacklin, Jordan Patterson", "Castro, S.F.", { t: "Sold out", color: RED }, N("Julia Jacklin", "Get") + " Get Away From Me"],
      [{ t: "Fri. Oct. 23", bold: true }, "Protomartyr, Accessory", "The Ritz, San Jose", "$26/$30, 8 p.m.", N("Protomartyr", "Feast") + " Feast of Stephen"],
      [{ t: "Fri. Oct. 23", bold: true }, "Black Flag (Greg Ginn lineup)", "Felton Music Hall, Felton", "21+", N("Black Flag", "Rise") + " Rise Above"],
      [{ t: "Sun. Oct. 25", bold: true }, "Black Flag (Greg Ginn lineup)", "Cornerstone, Berkeley", "$45.80, 7 p.m.", N("Black Flag", "Rise") + " Rise Above"],
      ["Wed. Oct. 28", "Slow Pulp (ticket sheet; DJ Cleo)", "Fillmore, S.F.", "Not in set", "--"],
    ], { keepTogether: true }));
    kids.push(note("Shows that happened before tonight (Dinosaur Jr., Hovvdy, Heavens to Betsy at Bottom of the Hill, Stef Chura) are not listed."));
    kids.push(spacer());
    kids.push(micBreak("MIC BREAK: BAY AREA", mb("bay_area_break")));
    kids.push(spacer());
  }
  if (/Set 7/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 7 (MACHINES)", mb("after_machines"))); kids.push(spacer()); }
  if (/Set 8/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 8 (ANNIVERSARY, NEW AND SLOW)", mb("anniversary"))); kids.push(spacer()); }
});
kids.push(micBreak("MIC BREAK: CLOSING", mb("closing")));

// ---- Back of the sheet ----
kids.push(heading("FCC watch list", 28, 0, true));
const AMB = (t) => ({ t, color: AMBER, bold: true });
kids.push(simpleTable([3200, 2400, 1500, 7300], ["Artist and track", "Status", "Where", "Action"], [
  [{ t: "Fujiya & Miyagi, No Green Light", bold: true }, AMB("LISTEN FIRST"), N("Fujiya & Miyagi", "No Green"), "No lyrics posted on Genius or LRCLIB. Long (5:51): cull candidate if unsure."],
  [{ t: "R.M.F.C., The Clue", bold: true }, AMB("LISTEN FIRST"), N("R.M.F.C.", "The Clue"), "No lyrics posted. Short song (1:40). Cull if unsure."],
  ["Scratch Acid, Mary Had a Little Drug Problem", AMB("CLEAN, check by ear"), N("Scratch Acid", "Mary"), "Genius 88 words: may be a partial transcription."],
  ["Fontaines D.C., Dopamine Chamber (4 tracks in set)", AMB("CLEAN, check by ear"), `${N("Fontaines D.C.", "Six")}-${N("Fontaines D.C. & ROSALIA", "Where")}`, "Genius lyrics were posted Oct. 16. Crowd-sourced: confirm by ear."],
  ["Reviewed-album tracks (13)", AMB("Per your review"), "Sets 1, 2, 4, 8", "Your Zookeeper reviews list FCC words per track; none of these tracks has a flag."],
  [{ t: "Fontaines D.C., Tongue", bold: true }, { t: "shit x10 (Refrain)", color: RED }, "FCC Edit Needed", "Not airable as is."],
  [{ t: "Fontaines D.C., Japan", bold: true }, { t: "fuck x3, shit x3 (Chorus)", color: RED }, "Held out", "Dopamine Chamber track 10. Not in set."],
  ["Scratch Acid, Crazy Dan", { t: "fuck x2, shit x1; caution bitch x2, goddamn x1", color: RED }, "Held out", "Mary Had a Little Drug Problem stands in."],
  ["The Jesus Lizard, Mouth Breather / Seasick", { t: "piss x1 / fuck x1", color: RED }, "Held out", "Monkey Trick stands in."],
  ["Black Flag, Nervous Breakdown", { t: "fuck x2 (Outro)", color: RED }, "Held out", "Rise Above stands in."],
  ["Frightwig, Crazy World", { t: "cock x1", color: RED }, "Held out", "Big Bang stands in."],
  ["Viagra Boys, Waterboy", { t: "fuck x2 (Verse 1, Verse 2)", color: RED }, "Held out", "Medicine for Horses stands in."],
  ["BODEGA, All Inside Aquarium", { t: "fuck x2", color: RED }, "FCC Edit Needed candidate", "Territorial Call of the Female stands in."],
  ["Sylvan Esso, Hot Slob", { t: "fuck x3, bitch x1 (per your review)", color: RED }, "Not in set", "You have a radio edit; not planned."],
]));

kids.push(heading("Bench: extra tracks not in the Air Order", 28, 240));
kids.push(note("Replacement pool if you cut tracks tonight. All are in Stace's Weekly Playlist except the Scratch Acid and Fontaines alternates. Labels marked (verify) came from the web, not Zookeeper."));
kids.push(simpleTable([2300, 3400, 3200, 2400, 1700, 1400], ["Artist", "Track", "Release", "Label", "Date", "FCC"], plan.bench.map((t) => {
  const st = t.fcc_status;
  const f = st === "CLEAN" ? { t: "CLEAN", color: GREEN, bold: true } : st === "CAUTION" ? { t: "CAUTION", color: AMBER, bold: true } : st === "FCC" ? { t: "HOLD", color: RED, bold: true } : { t: "LISTEN FIRST", color: AMBER, bold: true };
  return [t.artist, t.track, t.album || "-", (t.label || "-").replace(" (verify)", ""), String(t.released || "-"), f];
})));
kids.push(note("LISTEN FIRST means no lyrics were posted or the track was not screened."));

const doc = new Document({
  creator: "DJ Stace (Claude)",
  title: "Library Show Working Show Script 2026-10-22 (Landscape Tables)",
  styles: { default: { document: { run: { font: FONT, size: 18 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [run("The Library with DJ Stace  |  Oct. 22, 2026 (working draft)  |  Page ", { size: 14, color: "777777" }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: "777777" })] })] }) },
    children: kids,
  }],
});
const out = process.argv[2];
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out, buf.length, "bytes; total airable", fmt(total)); });
