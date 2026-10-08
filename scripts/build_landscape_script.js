// build_landscape.js
// Builds a landscape, table-based version of the Final Show Script for The Library (Oct. 8, 2026).
// Reads the show plan (plan_for_docx.json) and writes a Word file that opens in Google Docs.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, AlignmentType, PageOrientation, Footer, PageNumber, PageBreak, VerticalAlign,
} = require("docx");

const plan = JSON.parse(fs.readFileSync(__dirname + "/plan_for_docx.json", "utf8"));
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
  if (t.priority === "SKIP" || t.fcc_status === "FCC") return { t: "HOLD: piss x1", color: RED, bold: true, fill: RED_BG };
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
    const extra = held ? " FCC: " + t.fcc_note : (f.t === "CLEAN, check ear" ? " LRCLIB album match was odd; check by ear." : "");
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


// ---- ticket giveaway (from data/tickets/*.csv: the row where Stace is listed as a giving DJ) ----
const GIVE = { act: "Hovvdy", what: "indie rock (in tonight's Set 5, #24 Try Try Try)", venue: "Chapel, S.F.", date: "Mon. Oct. 19, 2026",
  giveBy: "Sun. Oct. 18", tix: "2", showTime: "Not on the sheet. Confirm before air.",
  djNote: "The ticket sheet lists Francis, not Stace, for this show. Confirm with Francis before air." };
const GREEN_BG = "E2F0D9";
// A one-row call-out table for a mic break line (promo teaser or giveaway)
function micBreak(label, lines, fill = GREEN_BG) {
  return new Table({ width: { size: PAGE_W, type: WidthType.DXA }, columnWidths: [2600, 11800], rows: lines.map((l, i) => new TableRow({ cantSplit: true, children: [
    cell(i === 0 ? label : "", 2600, { fill, bold: true, size: 18, keepNext: i < lines.length - 1 }),
    cell(l, 11800, { fill, size: 20, keepNext: i < lines.length - 1 }),
  ] })) });
}
const TEASER1 = "Promo 1 (opening break): \"We have 2 tickets to give away to Hovvdy at the Chapel in San Francisco on Monday, Oct. 19. That giveaway is in the second hour.\"";
const TEASER2 = "Promo 2 (end of Hour 1): \"Second hour is next, with the Thursday Triple Shot. Later in the hour, 2 tickets to Hovvdy at the Chapel in San Francisco, Monday, Oct. 19.\"";
const TEASER3 = "Promo 3 (after the Triple Shot): \"Hovvdy is in the songwriters set coming up, and after that set we give away 2 tickets to see them at the Chapel in San Francisco, Monday, Oct. 19.\"";

// ---- build body ----
const kids = [];
kids.push(new Paragraph({ spacing: { after: 40 }, children: [run("The Library with DJ Stace: Final Show Script", { size: 36, bold: true, color: NAVY })] }));
kids.push(para("Thursday, Oct. 8, 2026  |  KZSU 90.1 FM  |  6-8 p.m. PT  |  Final build Wed. Oct. 7  |  Landscape table version", { size: 18, color: "555555", after: 120 }));

// Run-of-show summary (computed)
const sets = plan.sets.map((s) => ({ s }));
let num = 1, cum = 0;
const built = [];
for (const set of plan.sets) { const b = setTable(set, num, cum); num = b.nextNum; cum = b.cumEnd; built.push({ set, ...b }); }
const total = cum;

kids.push(heading("Run of show", 26));
kids.push(simpleTable([6200, 1500, 1800, 2400, 2500], ["Set", "Tracks", "Set time", "Track numbers", "Running total"],
  built.map((b, i) => {
    const first = b.nextNum - b.count, last = b.nextNum - 1;
    return [b.set.set, String(b.count), fmt(b.setSecs), `${first}-${last}`, fmt(b.cumEnd)];
  }).concat([[{ t: "Total (airable)", bold: true }, { t: String(built.reduce((a, b) => a + b.count, 0)), bold: true }, { t: fmt(total), bold: true }, "", { t: "Target 2:30:00", bold: true }]])
));
kids.push(note("Zebra rows alternate for easy tracking. FCC column: green CLEAN, amber means listen first or check by ear, red means hold out. Tag is the KZSU library tag; a dash means not in the library."));

// What changed (short table)
kids.push(heading("What changed since the Working script", 24, 160));
kids.push(simpleTable([2600, 11800], ["Change", "Detail"], [
  ["Culled", "None. No ticks in the Cull column."],
  ["Replace requests", "None. No ticks in the Replace column."],
  ["Added (Air Order)", "Swans, \"Can't Find My Way Home\" (4:49), track 42. Tag 738020, The Burning World, Uni Distribution Corp. FCC clean on LRCLIB."],
  ["Held out", { t: "Sex Pistols, \"Anarchy in the U.K.\": FCC \"piss\" x1 (Outro). In the Air Order, not in the CSV. Needs a radio edit or a swap.", color: RED, bold: true }],
  ["Metadata fix", "Dinosaur Jr. \"Feel the Pain\" is on Without a Sound (tag 187859)."],
  [{ t: "Ticket giveaway (new)", bold: true }, { t: "Hovvdy, Chapel, S.F., Mon. Oct. 19. 2 tickets. Giveaway after Set 5 in Hour 2. Promo teasers at the opening break, the end of Hour 1 and after the Triple Shot. Sheet lists Francis as the giving DJ: confirm.", bold: true }],
]));

// Opening talk-break tables
kids.push(heading("Talk break: Oct. 8 in music", 24, 200));
kids.push(simpleTable([2600, 3300, 6000, 2500], ["Artist", "Album", "Fact", "In tonight's set"], [
  ["Talking Heads", "Remain in Light", "Released Oct. 8, 1980 (46 years). Sire.", "#8 Once in a Lifetime"],
  ["Soundgarden", "Badmotorfinger", "Released Oct. 8, 1991 on A&M, two weeks after Nevermind (35 years).", "#6 Slaves & Bulldozers"],
  ["Radiohead", "Kid A", "Debuted at No. 1 on the Billboard 200 the week of Oct. 8, 2000.", "#7 The National Anthem"],
]));

kids.push(heading("Talk break: new and coming up", 24, 200));
kids.push(simpleTable([2300, 3600, 2200, 2100, 4200], ["Artist", "Release", "Label", "Date", "In tonight's set"], [
  ["Teenage Fanclub", "Do Not Dare to Dream", "Merge", { t: "Fri. Oct. 9", bold: true }, "#14 Day in the Sun (Triple Shot closer)"],
  ["Imperial Teen", "All Over You", "Merge", { t: "Fri. Oct. 9", bold: true }, "#18 Overdrive"],
  ["Death Valley Girls", "Welcome to Earth", "Suicide Squeeze", { t: "Fri. Oct. 9", bold: true }, "Not in set"],
  ["Bodega", "All Inside Aquarium", "Chrysalis", { t: "Fri. Oct. 9", bold: true }, { t: "Not airable: fuck x2 (FCC Edit Needed)", color: RED }],
  ["Caroline Rose", "Gentling the Horse at the Walt Whitman Mall", "SUCK Records", "Oct. 23", "#4 Chow Mein"],
  ["Queens of the Stone Age", "Perfecth", "-", "Oct. 30", { t: "Easy Street: fuck x1 (FCC Edit Needed)", color: RED }],
  ["Ministry", "Final album", "-", "Oct. 30", "Not in set"],
  ["Twisted Teens", "The Holy Cross Tigers", "Sub Pop", "Nov. 6", "#1 When We First Met"],
  ["Morphine", "Cocoon (new album)", "Partisan", "Dec. 4", "#35 Cocoon (1993 original). Full mic break after Set 6."],
]));
kids.push(note("Next week: Thursday, Oct. 15 is Imperial Teen at Bottom of the Hill."));
kids.push(spacer());
kids.push(micBreak("MIC BREAK: PROMO", [TEASER1]));

// ---- Hour 1 ----
kids.push(heading("HOUR 1", 30, 0, true));
built.filter((b) => /^Hour 1/.test(b.set.set)).forEach((b) => {
  kids.push(b.table); kids.push(spacer());
  if (/Set 3/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: END OF HOUR 1", [TEASER2])); }
});

// ---- Hour 2 ----
kids.push(heading("HOUR 2", 30, 0, true));
built.filter((b) => !/^Hour 1/.test(b.set.set)).forEach((b) => {
  kids.push(b.table); kids.push(spacer());
  if (/Triple Shot/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: PROMO", [TEASER3])); kids.push(spacer()); }
  if (/Set 4/.test(b.set.set)) {
    kids.push(heading("Talk break after Set 4: Bay Area shows (foopee.com, Oct. 4; confirm before air)", 22));
    kids.push(simpleTable([2300, 3500, 4300, 1500, 2800], ["Date", "Act", "Venue", "Status", "Track tonight"], [
      ["Oct. 6, 7, 9, 10, 11", "My Morning Jacket", "Fillmore, S.F.", "", "#15 Wordless Chorus"],
      [{ t: "Thu. Oct. 15", bold: true }, "Imperial Teen", "Bottom of the Hill, S.F.", "", "#17 Yoo Hoo, #18 Overdrive"],
      ["Oct. 16", "Iron & Wine", "Castro, S.F.", { t: "Sold out", color: RED }, "Not in set"],
      ["Oct. 18", "Dinosaur Jr. with Stef Chura", "S.F. (verify venue)", "", "#16 Feel the Pain"],
      ["Oct. 19", "Dinosaur Jr. with Stef Chura", "Guild Theater, Menlo Park (verify)", "", "#16 Feel the Pain"],
      [{ t: "Mon. Oct. 19", bold: true }, "Hovvdy", "Chapel, S.F.", { t: "Tickets tonight", bold: true }, "#24 Try Try Try"],
      ["Oct. 19 and 20", "Geese", "Fox Theater, Oakland", { t: "Sold out", color: RED }, "#19 Cobra"],
      ["Fri. Oct. 23", "Cheekface and Bodega", "Cornerstone, Berkeley", "", "Not in set"],
    ], { keepTogether: true }));
    kids.push(spacer());
  }
  if (/Set 6/.test(b.set.set)) {
    kids.push(heading("MIC BREAK after #35: Morphine, new album Cocoon (out Dec. 4, Partisan)", 22));
    kids.push(micBreak("READ (about 60 sec)", [
      "\"That was Morphine, Cocoon, from Cure for Pain in 1993. Morphine has a new album, also called Cocoon, out Dec. 4 on Partisan. It is their first full-length since The Night in 2000, which came out after singer Mark Sandman died of a heart attack on stage in Italy. The new record is built from sessions the band started and abandoned in 1998. Sandman's partner, Sabine Hrechdakian, worked with producer Paul Q. Kolderie to go through the old tapes. Kolderie, who made Morphine records with Sean Slade and also produced Pablo Honey and Live Through This, remixed them. Dana Colley added new baritone sax on three songs. There is piano and guitar, and more than one drummer. Hrechdakian says the title is about coming home, and she pictures the cocoon as a spaceship for two. The title track is out now, with an archival video.\"",
    ]));
    kids.push(spacer());
    kids.push(simpleTable([2300, 9400, 2700], ["Ad-lib topic", "Background", "Source"], [
      [{ t: "The story", bold: true }, "Surviving members reunited to finish an eight-song LP started and abandoned in 1998, a year before Sandman died on stage. It is the first full-length since The Night, released after his death on DreamWorks in 2000. Morphine disbanded in 1999 right after his death. Decades in the making.", "Pitchfork, Line of Best Fit"],
      [{ t: "Producers", bold: true }, "Paul Q. Kolderie and Sean Slade, Morphine's longtime production duo, ran the 1998 sessions. They also produced Radiohead's Pablo Honey and Hole's Live Through This.", "Pitchfork"],
      [{ t: "Why it was shelved", bold: true }, "SPIN reports pressure from DreamWorks and friction with Kolderie, and that Sandman set the material aside and self-produced The Night. Only SPIN gives this reason, so say \"reportedly.\" Sessions were at Sandman's home studio in Cambridge, Mass. (SPIN; SPIN dates some work into 1999).", "SPIN"],
      [{ t: "The tapes", bold: true }, "Untouched for more than two decades. In 2023, Hrechdakian (Sandman's partner and the Morphine estate manager) and Kolderie digitized and assessed them, then picked the songs and mixes. Kolderie newly mixed the album. He said he was astounded by the sound and felt right \"bringing them back from the crypt.\"", "Pitchfork, Rolling Stone"],
      [{ t: "The sound", bold: true }, "Not the usual minimal trio. The recordings add piano, guitar and contributions from more than one drummer. The Night was the first Morphine LP recorded as a quartet, with drums from returning cofounder Jerome Deupree and his replacement Billy Conway.", "Pitchfork"],
      [{ t: "Dana Colley", bold: true }, "Morphine's baritone sax player. Reluctant at first, then recorded new sax parts for three songs in early 2026, playing along to the 1998 recordings. He describes it as one foot in the past and one in the present, with the sax bridging the gap.", "Pitchfork, Rolling Stone"],
      [{ t: "The title", bold: true }, "Hrechdakian says Sandman loved touring but also loved coming home to cocoon. The house was also his studio, with tape running and friends dropping by. Lyrics cover missing loved ones on tour and coming home. A space travel thread runs through the album; she pictures the cocoon as a spaceship for two.", "Pitchfork"],
      [{ t: "The songs", bold: true }, "Tomorrow, Wig, Patience, Spaceman Charm, Justine, Moons of Jupiter, Cocoon, Pretty Face. Spaceman Charm has never been heard before. Some of the others circulated as alternate versions on unofficial releases and the 2004 compilation Sandbox. Title track is out now with an archival video.", "Partisan, Line of Best Fit, Pitchfork"],
      [{ t: "Art and notes", bold: true }, "Cover is a photo Sandman took of Hrechdakian's reflection in a train window. Liner notes by poet and essayist Hanif Abdurraqib, who writes about finding Morphine after Sandman's death.", "Bandcamp, Stereogum"],
      [{ t: "Sandman", bold: true }, "Singer and two-string slide bassist. Died of a heart attack at the Nel Nome del Rock festival in Palestrina, Italy, in 1999. July 3 and age 46 are from background knowledge, not the coverage above: verify before quoting.", "Pitchfork, Hot Press"],
      [{ t: "Tonight's track", bold: true }, "We played the 1993 song from Cure for Pain (Rykodisc), #35. The new album's title track is a newly mixed 1998 recording; the coverage does not say how it differs from the 1993 version. Do not call it a re-recording.", "Verify"],
      [{ t: "Release details", bold: true }, "Out Dec. 4 on Partisan; LP (black vinyl, gatefold) and CD (digisleeve with lyric booklet). Pre-orders are open. One outlet printed Dec. 8; the label and most coverage say Dec. 4.", "Bandcamp, Partisan"],
    ], { keepTogether: true }));
    kids.push(note("Sources: Pitchfork (Jazz Monroe), The Line of Best Fit, Rolling Stone, SPIN, Stereogum, Hot Press, Partisan Records and the band's Bandcamp page, all coverage of the album announcement."));
    kids.push(spacer());
  }
  if (/Set 5/.test(b.set.set)) {
    kids.push(heading("TICKET GIVEAWAY (after Set 5)", 22));
    kids.push(simpleTable([2300, 3000, 2800, 2000, 1000, 3300], ["Act", "Type", "Venue", "Date", "Tickets", "Give by"], [
      [{ t: GIVE.act, bold: true }, GIVE.what, GIVE.venue, { t: GIVE.date, bold: true }, GIVE.tix, { t: GIVE.giveBy + " (winner picked by then)", bold: true }],
    ], { keepTogether: true }));
    kids.push(micBreak("MIC BREAK: GIVEAWAY", [
      "Read: \"That was Hovvdy earlier in this set, Try Try Try. They play the Chapel in San Francisco on Monday, Oct. 19. We have 2 tickets to give away.\"",
      GIVE.djNote,
      "Contest method and call-in number: use the KZSU contest procedure (not on the ticket sheet).",
      "Show time: " + GIVE.showTime,
      "After the winner: follow the usual KZSU steps for logging the giveaway and ticket pickup.",
    ]));
    kids.push(spacer());
  }
});

// ---- Back of the sheet ----
kids.push(heading("FCC watch list", 28, 0, true));
kids.push(simpleTable([2800, 3200, 1900, 6500], ["Artist and track", "Status", "Where", "Action"], [
  [{ t: "Sex Pistols, Anarchy in the U.K.", bold: true }, { t: "HOLD: piss x1 (\"pissed,\" Outro)", color: RED, bold: true }, "Air Order, held out of CSV", "Radio edit or swap."],
  ["Dread Spectre Council, Hex's Up", { t: "LISTEN FIRST", color: AMBER, bold: true }, "#5", "No lyrics online."],
  ["Mandrake Handshake, The Tether / Modulo 5", { t: "LISTEN FIRST", color: AMBER, bold: true }, "#33", "No lyrics online. Likely instrumental."],
  ["Courtney Barnett, One Thing At A Time", { t: "CLEAN, check by ear", color: AMBER, bold: true }, "#28", "LRCLIB match came from an odd album entry."],
  ["Imperial Teen, Overdrive", "Clean (Oct. 4 shelf check)", "#18", "Genius has no match."],
  ["Bodega, All Inside Aquarium", { t: "fuck x2", color: RED }, "FCC Edit Needed", "Not airable as is."],
  ["Queens of the Stone Age, Easy Street", { t: "fuck x1", color: RED }, "FCC Edit Needed", "Not airable as is."],
  ["Greg Freeman, Cahokia", { t: "FCC", color: RED }, "FCC Edit Needed", "Added Oct. 4. Not airable as is."],
  ["Fontaines D.C., Tongue", { t: "shit x10 (Refrain)", color: RED }, "FCC Edit Needed", "Not airable as is."],
  ["DIIV, Trillions", { t: "fucking x1", color: RED }, "FCC Edit Needed", "Not airable as is."],
  ["Spanish Love Songs, Doom Tripping", { t: "shit x1 (Verse 3)", color: RED }, "FCC Edit Needed", "Not airable as is."],
]));

kids.push(heading("Bench: new on Stace's Weekly Playlist", 28, 240));
kids.push(note("Tuesday sweeps, Oct. 4 and Oct. 6. None are in the Air Order. Labels from press unless noted."));
const SCR = "Screened";
kids.push(simpleTable([2300, 3400, 3300, 2000, 1500, 1900], ["Artist", "Track", "Release", "Label", "Date", "FCC"], [
  ["Fontaines D.C.", "Tongue", "Dopamine Chamber", "XL", "Oct. 16", { t: "HOLD", color: RED, bold: true }],
  ["Fontaines D.C.", "Marianne", "Dopamine Chamber", "XL", "Oct. 16", SCR],
  ["L7", "Loma Linda", "The Last Hurrah tour single", "-", "Oct. 6", { t: "LISTEN FIRST", color: AMBER, bold: true }],
  ["DIIV", "Trillions", "ZIRP!", "Fantasy", "Oct. 30", { t: "HOLD", color: RED, bold: true }],
  ["Clinic", "You and I (2:27)", "Wild in the Streets", "Domino", "Oct. 30", { t: "LISTEN FIRST", color: AMBER, bold: true }],
  ["Cursive", "Wounded Animal (5:49)", "Who's Watching soundtrack", "15 Passenger", "Oct. 30", { t: "LISTEN FIRST", color: AMBER, bold: true }],
  ["Dazy", "Ugly (2:54)", "MAXIMUMBLASTSUPERLOUD Vol. 2", "Lame-O", "Oct. 23", { t: "LISTEN FIRST", color: AMBER, bold: true }],
  ["Brigitte Calls Me Baby", "Altitude", "Single", "ATO", "Oct. 2", { t: "CLEAN", color: GREEN, bold: true }],
  ["Spanish Love Songs", "Doom Tripping", "Future Nausea", "Pure Noise", "Nov. 6", { t: "HOLD", color: RED, bold: true }],
  ["Kings of Leon", "Cold Blue Dawn", "O My Beloved", "Love Tap/Virgin", "Nov. 6", { t: "LISTEN FIRST", color: AMBER, bold: true }],
  ["Teens in Trouble", "I Do (3:00)", "Single", "Lauren/Sneak Dog", "-", { t: "CLEAN", color: GREEN, bold: true }],
  ["Michael Kiwanuka", "Summer Clothes", "Fudge", "Polydor", "Oct. 23", { t: "CLEAN", color: GREEN, bold: true }],
  ["Stef Chura", "Danny", "Dancing Alone on the Concrete", "Saddle Creek", "Oct. 2", SCR],
  ["Protomartyr", "Sounds We Cannot Hear", "Hotel Usona", "Domino", "Sept. 25", SCR],
  ["Greg Freeman", "Cahokia", "All Set The Bone", "Transgressive", "Oct. 2", { t: "HOLD", color: RED, bold: true }],
  ["Johnny Marr", "Spin", "The Age of Everything", "BMG", "Oct. 2", SCR],
  ["Wishy", "Lovesick", "Nature's Pill", "Winspear", "Oct. 2", SCR],
  ["Julia Jacklin", "Get Away From Me (I Think I'll Love You Soon)", "The Gem", "4AD", "Sept. 25", SCR],
  ["Blondshell", "Heart Has To Work So Hard", "Violins", "Partisan", "Sept. 25", SCR],
  ["Renny Conti", "Mona Lisa", "Split Second", "Mom + Pop", "Sept. 25", SCR],
  ["Jess Williamson", "Goodbye to All That", "A Mile South of Heaven", "New West", "Oct. 9", SCR],
  ["Death Valley Girls", "Message From the Venus Flower", "Welcome to Earth", "Suicide Squeeze", "Oct. 9", SCR],
  ["Teenage Fanclub", "There Was You", "Do Not Dare To Dream", "Merge", "Oct. 9", SCR],
  ["Phoebe Bridgers", "On Video", "Lost Weekend", "Dead Oceans", "Date to verify", SCR],
  ["mercury", "Roar Of The Heliac Goat", "Single", "-", "Sept. 30", SCR],
  ["Emma Ogier", "Hands Tied", "Fly 1111", "Lost Highway", "Nov. 11", SCR],
]));
kids.push(note("\"Screened\" means the Oct. 4 or Oct. 6 FCC screen found no flagged words or was not flagged in the notes. Check the Working script if in doubt."));

const doc = new Document({
  creator: "DJ Stace (Claude)",
  title: "Library Show Final Show Script 2026-10-08 (Landscape Tables)",
  styles: { default: { document: { run: { font: FONT, size: 18 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE },
      margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [run("The Library with DJ Stace  |  Oct. 8, 2026  |  Page ", { size: 14, color: "777777" }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: "777777" })] })] }) },
    children: kids,
  }],
});

const out = process.argv[2];
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out, buf.length, "bytes; total airable", fmt(total)); });
