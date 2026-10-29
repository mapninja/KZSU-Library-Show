// build_landscape_one_hour_2026-10-29.js
// Builds the landscape, table-based ONE-HOUR Show Script (Stanford Sports preempts half the show) for The Library (Thursday, Oct. 29, 2026).
// Reads Stace's 15 picks (grouped into sets) from data/recon/2026-10-29/one_hour_sets.json
// Run from the repo root:  node scripts/build_landscape_final_2026-10-29.js "<out>.docx"
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
const plan = JSON.parse(fs.readFileSync(path.join(REPO, "data/recon/2026-10-29/one_hour_sets.json"), "utf8"));

// ---- track numbers, counted the same way the set tables count (SKIP and CUT are skipped) ----
const NUM = [];
{ let n = 0; for (const s of plan.sets) for (const t of s.tracks) { if (t.priority === "SKIP" || t.priority === "CUT") continue; n++; NUM.push({ n, artist: t.artist, track: t.track }); } }
const NN = (artist, prefix) => { const m = NUM.find((x) => x.artist === artist && x.track.toLowerCase().startsWith(prefix.toLowerCase())); if (!m) throw new Error("No track: " + artist + " " + prefix); return m.n; };
const N = (artist, prefix) => "#" + NN(artist, prefix);
// Nth: number of the Nth match (used where an artist has two versions of the same track)
const Nth = (artist, prefix, k) => "#" + NUM.filter((x) => x.artist === artist && x.track.toLowerCase().startsWith(prefix.toLowerCase()))[k].n;

const FONT = "Arial";
const PAGE_W = 14400; // usable width in DXA (11 in minus 0.5 in margins)
const NAVY = "1F3864", BAND = "D9E2F3", ZEBRA = "F5F7FA", RED_BG = "F8D7DA", AMBER_BG = "FFF3CD", GREEN_BG = "E2F0D9", CHANGE_BG = "DDEBF7";
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
  const title = `${set.set}   |   ${airable.length} ${airable.length === 1 ? "track" : "tracks"}   |   ${fmt(setSecs)}   |   on air through ${fmt(cumEnd)}`;
  const bandRows = [new TableRow({ cantSplit: true, children: [cell(title, PAGE_W, { span: 9, fill: BAND, bold: true, size: 22, color: NAVY, keepNext: true })] })];
  if (/Triple Shot/.test(set.set)) bandRows.push(new TableRow({ cantSplit: true, children: [cell("Intro: " + plan.triple_shot.angle, PAGE_W, { span: 9, fill: BAND, size: 18, keepNext: true })] }));
  const head = new TableRow({ tableHeader: true, cantSplit: true, children: COLS.map((h, i) => cell(h, W[i], { fill: NAVY, color: "FFFFFF", bold: true, keepNext: true })) });
  let n = startNum;
  const shown = set.tracks.filter((t) => t.priority !== "CUT"); // Stace's cuts do not print
  const rows = shown.map((t, ri) => {
    const kn = ri < shown.length - 1;
    const held = t.priority === "SKIP" || t.priority === "CUT";
    const num = held ? "--" : String(n++);
    const f = fcc(t);
    const changed = !!t.final_change;
    const fill = held ? RED_BG : changed ? CHANGE_BG : ri % 2 ? ZEBRA : undefined;
    const extra = held ? " FCC: " + t.fcc_note : (f.t === "CLEAN, check ear" ? " " + (t.fcc_note || "Check by ear.") : "");
    const notes = (held ? "HELD OUT of Zookeeper CSV. " : "") + (changed ? "[" + t.final_change + "] " : "") + (t.why || "") + extra;
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
kids.push(new Paragraph({ spacing: { after: 40 }, children: [run("The Library with DJ Stace: One-Hour Show Script", { size: 36, bold: true, color: NAVY })] }));
kids.push(para("Thursday, Oct. 29, 2026  |  KZSU 90.1 FM  |  Halloween  |  One hour tonight (Stanford Sports has the other half of the slot)  |  15 tracks picked from your One-Hour Picker sheet  |  Landscape table version", { size: 18, color: "555555", after: 120 }));

let num = 1, cum = 0; const built = [];
for (const set of plan.sets) { const b = setTable(set, num, cum); num = b.nextNum; cum = b.cumEnd; built.push({ set, ...b }); }
const total = cum;
const AO = [];  // longest tracks first, for the "if you run long" table
for (const s of plan.sets) for (const t of s.tracks) AO.push({ n: NN(t.artist, t.track.slice(0, 8)), t });

kids.push(heading("Run of show", 26));
kids.push(simpleTable([6600, 1500, 1800, 2400, 2100], ["Set", "Tracks", "Set time", "Track numbers", "Running total"],
  built.map((b) => { const first = b.nextNum - b.count, last = b.nextNum - 1; return [b.set.set, String(b.count), fmt(b.setSecs), `${first}-${last}`, fmt(b.cumEnd)]; })
    .concat([[{ t: "Total music", bold: true }, { t: String(built.reduce((a, b) => a + b.count, 0)), bold: true }, { t: fmt(total), bold: true }, "", { t: "Hour: 60:00", bold: true }]])));
kids.push(note(`Your picks run ${fmt(total)}. With about 10 minutes of talk, IDs and PSAs, music should be about 50:00, so you are about ${fmt(total - 3000)} over. The table below lists the longest tracks if you need to drop some on air. FCC column: green CLEAN, amber means listen first. Tag is the KZSU library tag; a dash means not in the library.`));

kids.push(heading("If you run long: cut candidates, longest first", 24, 160));
const longest = [...AO].sort((a, b) => secs(b.t.duration) - secs(a.t.duration)).slice(0, 6);
kids.push(simpleTable([900, 3600, 4800, 1300, 3800], ["#", "Artist", "Track", "Time", "Why it is a good cut"], longest.map((x) => [
  "#" + x.n, x.t.artist, x.t.track, x.t.duration,
  x.t.artist === "Black Sabbath" ? "Closer, 9:26. Drop it and end on Alien Sex Fiend, or end with Sabbath and cut elsewhere." :
  x.t.artist === "Alien Sex Fiend" ? "7:58, the second-longest track." :
  x.t.artist === "The Black Angels" ? "5:33, core artist, easy to swap for a shorter fuzz track." :
  x.t.artist === "Dread Spectre Council" ? "4:54, five-star review. Keep if you can." : "Cut if you are still over."])));

kids.push(heading("Talk break: Today in music", 24, 200));
kids.push(simpleTable([2600, 3600, 6200, 2000], ["Artist or place", "Item", "Fact", "In tonight's set"], [
  ["Orson Welles", "War of the Worlds (Oct. 30, 1938)", "CBS aired it at 8 p.m. ET on The Mercury Theatre on the Air. The FCC investigated afterward and found no law was broken. A radio story for a radio show.", "Any break"],
  ["Black Sabbath", "Reunion on Letterman (Oct. 30, 1998)", "All four original members played Paranoid on the Late Show. Confirmed by IMDb episode listing, Louder and Black Sabbath Online.", N("Black Sabbath", "Black Sabbath") + " Black Sabbath (closer)"],
  ["Queens of the Stone Age, Ministry, Mitski", "New this Friday, Oct. 30", "QOTSA: Perfecth (Matador). Ministry: Hate to Go (Take Out or Delivery), final album (Cleopatra). Mitski: Puberty 2, 10th Anniversary Edition (Dead Oceans). Say \"out tomorrow.\"", N("Queens of the Stone Age", "Where") + " Where the Goth Girls At?"],
]));
kids.push(spacer());

kids.push(heading("Show", 24, 120));
const bk = (label, lines) => { kids.push(micBreak(label, lines)); kids.push(spacer()); };
bk("MIC BREAK: OPENING", [
  "Halloween show, one hour tonight. Punk and post-punk focus, week 3 of 4: goth and post-punk close the hour. D.C. hardcore Nov. 5.",
  "Tonight: Screamin' Jay Hawkins, a werewolf cover, fuzz, the devil, a new Queens of the Stone Age single, then goth and industrial to the end.",
]);
built.forEach((b, i) => {
  kids.push(b.table); kids.push(spacer());
  if (i === 0) bk("MIC BREAK: AFTER SET 1", [
    "Screamin' Jay Hawkins recorded I Put a Spell on You in 1956. Wolf Like Me is a TV on the Radio song; Lera Lynn and Shovels & Rope cover it.",
    "The Flaming Lips announced The Teardrop Throbs Oct. 26, due in January on Third Man (verify). It is the first Lips album without Steven Drozd. God Will Control the Werewolves is the first track out.",
  ]);
  if (i === 1) bk("MIC BREAK: AFTER SET 2", [
    "Lambrini Girls released Cult of Celebrity Mar. 31 on City Slang, their first new music since the 2025 album Who Let The Dogs Out. Dread Spectre Council's Raven is from Thetans on Handmade Records; your review gave it five stars.",
  ]);
  if (i === 2) bk("MIC BREAK: AFTER SET 3", [
    "Andy Shauf, Satan. Next: the new Queens of the Stone Age single.",
  ]);
  if (i === 3) bk("MIC BREAK: AFTER QOTSA", [
    "Queens of the Stone Age, Where the Goth Girls At? Perfecth, the band's ninth album, is out Fri. Oct. 30 on Matador. Josh Homme and Michael Shuman produced it.",
    "Ministry's final album, Hate to Go (Take Out or Delivery), is also out Fri. Oct. 30 on Cleopatra, and Mitski's Puberty 2 anniversary edition is out the same day.",
  ]);
  if (i === 4) bk("MIC BREAK: AFTER SET 5", [
    "On Oct. 30, 1938, CBS aired Orson Welles' War of the Worlds on The Mercury Theatre on the Air. The FCC investigated afterward and found no law was broken.",
  ]);
});
bk("MIC BREAK: CLOSING", [
  "Black Sabbath: the four original members reunited on Letterman Oct. 30, 1998 to play Paranoid.",
  "Next week, Nov. 5: US hardcore and Washington D.C. Fugazi, Husker Du, Bad Brains, short songs.",
]);

kids.push(heading("Bay Area shows, upcoming only (foopee.com, read Oct. 22 and 23; confirm before air)", 22, 120));
kids.push(simpleTable([2000, 4200, 3600, 4600], ["Date", "Act", "Venue", "Status"],
  plan.bay_area_shows.filter((s) => s.date !== "Source").map((s) => [{ t: s.date, bold: true }, s.what.split(". $")[0].split(" $")[0], s.venue, s.what.includes("$") ? s.what.slice(s.what.indexOf("$")) + (s.note ? " " + s.note : "") : (s.note || "")]),
  { keepTogether: true }));
kids.push(note("Not placed in a break tonight because the hour is short. Read one or two if time allows. No ticket giveaway: no sheet row lists Stace with a give-by date on or after Oct. 29."));

kids.push(heading("FCC watch list", 24, 200));
const AMB = (t) => ({ t, color: AMBER, bold: true });
kids.push(simpleTable([4000, 2400, 1500, 6500], ["Artist and track", "Status", "Where", "Action"], [
  [{ t: "Coil, Where Even the Darkness Is Something to See", bold: true }, AMB("LISTEN FIRST"), N("Coil", "Where"), "No lyrics on LRCLIB or Genius. Mostly instrumental with a sample; confirm by ear."],
  ["Lambrini Girls, Cult of Celebrity", AMB("CLEAN (LRCLIB)"), N("Lambrini Girls", "Cult"), "LRCLIB, 224 words, no hits. Band is known for strong language; the earlier single The Basement has shit x3."],
  ["All other picks", AMB("CLEAN"), "--", "Screened by LRCLIB or Genius word counts, or your review lists no FCC words for the track."],
]));

const doc = new Document({
  creator: "DJ Stace (Claude)",
  title: "Library Show One-Hour Show Script 2026-10-29 (Landscape Tables)",
  styles: { default: { document: { run: { font: FONT, size: 18 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [run("The Library with DJ Stace  |  Oct. 29, 2026 (one hour)  |  Page ", { size: 14, color: "777777" }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: "777777" })] })] }) },
    children: kids,
  }],
});
const out = process.argv[2];
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out, buf.length, "bytes; total", fmt(total)); });
