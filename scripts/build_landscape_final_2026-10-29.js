// build_landscape_final_2026-10-29.js
// Builds the landscape, table-based FINAL Show Script (Wednesday-night build) for The Library (Thursday, Oct. 29, 2026).
// Reads the show plan directly: data/recon/2026-10-29/working_playlist.json
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
const plan = JSON.parse(fs.readFileSync(path.join(REPO, "data/recon/2026-10-29/working_playlist.json"), "utf8"));
const MB = plan.mic_breaks;
const mb = (k) => MB[k].slice();

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
    const changed = !!t.final_change;
    const fill = held ? RED_BG : changed ? CHANGE_BG : ri % 2 ? ZEBRA : undefined;
    const extra = held ? " FCC: " + t.fcc_note : (f.t === "CLEAN, check ear" ? " " + (t.fcc_note || "Check by ear.") : "");
    const notes = (held ? "HELD OUT of Zookeeper CSV. " : "") + (changed ? "NEW (" + t.final_change + "). " : "") + (t.why || "") + extra;
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
kids.push(new Paragraph({ spacing: { after: 40 }, children: [run("The Library with DJ Stace: Final Show Script", { size: 36, bold: true, color: NAVY })] }));
kids.push(para("Thursday, Oct. 29, 2026  |  KZSU 90.1 FM  |  6-8 p.m. PT  |  Final built Wed. Oct. 28, 8 p.m.  |  Halloween specialty show (punk and post-punk arc, week 3 of 4)  |  Landscape table version  |  Request changes Thursday before air", { size: 18, color: "555555", after: 120 }));

let num = 1, cum = 0; const built = [];
for (const set of plan.sets) { const b = setTable(set, num, cum); num = b.nextNum; cum = b.cumEnd; built.push({ set, ...b }); }
const total = cum;
const h1 = built.filter((b) => /^Hour 1/.test(b.set.set)).reduce((a, b) => a + b.setSecs, 0);

kids.push(heading("Run of show", 26));
kids.push(simpleTable([6200, 1500, 1800, 2400, 2500], ["Set", "Tracks", "Set time", "Track numbers", "Running total"],
  built.map((b) => { const first = b.nextNum - b.count, last = b.nextNum - 1; return [b.set.set, String(b.count), fmt(b.setSecs), `${first}-${last}`, fmt(b.cumEnd)]; })
    .concat([[{ t: "Total (airable)", bold: true }, { t: String(built.reduce((a, b) => a + b.count, 0)), bold: true }, { t: fmt(total), bold: true }, `Hour 1 ${fmt(h1)}, Hour 2 ${fmt(total - h1)}`, { t: "Target 2:30:00", bold: true }]])));
kids.push(note("FCC column: green CLEAN, amber means listen first or check by ear, red means hold out. Tag is the KZSU library tag; a dash means not in the library. The list runs " + fmt(Math.max(0, total - 9000)) + " over the 2:30 target. Bench tracks (back page) are not in the Air Order."));

kids.push(heading("What changed since the Oct. 27 draft", 24, 160));
kids.push(simpleTable([2600, 11800], ["Change", "Detail"], [
  [{ t: "Culled", bold: true }, "None. No Cull ticks in the Notes Sheet."],
  [{ t: "Replaced", bold: true }, "None. No Replace ticks in the Notes Sheet."],
  [{ t: "Added", bold: true, fill: CHANGE_BG }, { t: `${N("Coil", "Where")} Coil, Where Even the Darkness Is Something to See (3:05), added to your Air Order (#45) after the Oct. 27 sync. Placed in Set 5 after Skinny Puppy. FCC: no lyrics posted, so LISTEN FIRST.`, fill: CHANGE_BG }],
  [{ t: "Placed", bold: true }, `Your ten tracks at the bottom of the Air Order (#43-52) sit in the sets that fit: Set 1 (${Nth("The Sonics", "The Witch", 1)} Sonics, ${N("The Kills", "I Put")} Kills), Set 3 (${N("Bauhaus", "Bela")} to ${N("Talking Heads", "Psycho")}), Set 5 (${N("Nick Cave and The Bad Seeds", "Up")} to ${N("Andy Shauf", "Satan")}). Reorder on the Air Order if you want a different run; your order wins.`],
  [{ t: "Kept as is", bold: true }, `Both Sonics versions of The Witch stay in (${Nth("The Sonics", "The Witch", 0)} at 2:41 and ${Nth("The Sonics", "The Witch", 1)} at 2:48). Cut one on air if you want only one.`],
  [{ t: "Labels and tags", bold: true }, "Filled from Zookeeper Oct. 28 for all ten added tracks. Library tags: Talking Heads 77, Rolling Stones Beggars Banquet (the library copy of the original LP), Sonics The Witch single, Coil Love's Secret Domain (!K7 issue). Not in the library: Kills, Nick Cave Tender Prey, Skinny Puppy Bites, Andy Shauf, Lera Lynn. Alien Sex Fiend label (Anagram Records) is not in the Zookeeper label table."],
  [{ t: "Facts fixed", bold: true }, "Black Sabbath on Letterman Oct. 30, 1998 is confirmed (IMDb episode listing, Louder, Black Sabbath Online). Fake Names mic line now says Punk Ruins came out Oct. 23, not today."],
]));

kids.push(heading("What is in this show", 24, 200));
kids.push(simpleTable([2600, 11800], ["Item", "Detail"], [
  [{ t: "Theme", bold: true }, "Halloween specialty show. Punk and post-punk arc, week 3 of 4. The Triple Shot opens Hour 2."],
  [{ t: "Length", bold: true }, `The list runs ${fmt(total)}, ${fmt(Math.max(0, total - 9000))} over the 2:30 target. You cull on Thursday. Bench tracks (back page) are the replacement pool.`],
  [{ t: "Reviewed albums in rotation", bold: true }, "13 albums, one track each. Ten albums are in week 3 (posted Oct. 4 to 8); The Fall, Sylvan Esso and Yard Act are in week 2. Next show (Nov. 5) is week 4 for the first ten: about half. Table below."],
  [{ t: "Triple Shot", bold: true }, `Queens of the Stone Age (${N("Queens of the Stone Age", "Where")}-${N("Queens of the Stone Age", "Burn")}). New single from Perfecth, out Fri. Oct. 30 on Matador. Easy Street stays out (cool-off to Dec. 8).`],
  [{ t: "Punk and post-punk focus", bold: true }, `Set 3 (${N("Siouxsie and the Banshees", "Spell")}-${N("Talking Heads", "Psycho")}) plus Fake Names, Punk Ruins (${N("Fake Names", "Punk")}), out Oct. 23 on Epitaph. Killing Joke and Iceage are in cool-off.`],
  [{ t: "Dropped", bold: true }, { t: "Death Valley Girls, Basic Witch: you deleted it from Weekly Oct. 9 (60-day cool-off to Dec. 8). Ministry Burned Out (shit x1), Black Lips Bad Kids (shit x1) and Tropical Fuck Storm stay out for FCC.", color: RED }],
  [{ t: "Ticket giveaway", bold: true }, "None placed. No sheet row lists Stace with a give-by date on or after Oct. 29. Katie Pruitt (Chapel, Oct. 29, listed DJ Mr Bones) gave by 10/28. Send a current row if you want one."],
  [{ t: "Release timing", bold: true }, "Queens of the Stone Age, Ministry and Mitski (anniversary edition) all land Fri. Oct. 30, one day after the show. Say \"out tomorrow.\""],
]));

kids.push(heading("Talk break: Today in music", 24, 200));
kids.push(simpleTable([2600, 3300, 6000, 2500], ["Artist or place", "Item", "Fact", "In tonight's set"], [
  ["Orson Welles", "War of the Worlds (Oct. 30, 1938)", "CBS aired it at 8 p.m. ET on The Mercury Theatre on the Air, Howard Koch script. The FCC investigated and found no law was broken. A radio story for a radio show.", "Intro for Set 5"],
  ["Black Sabbath", "Reunion on Letterman (Oct. 30, 1998)", "All four original members played Paranoid on the Late Show. Confirmed by IMDb episode listing, Louder and Black Sabbath Online.", N("Black Sabbath", "Black Sabbath") + " Black Sabbath"],
  ["The Cure", "Roger O'Donnell birthday", "Born Oct. 29, 1955. Keyboards on Disintegration (1989). The library holds the Lullaby single.", N("The Cure", "Lullaby") + " Lullaby"],
  ["The Who", "My Generation (UK single, Oct. 29, 1965)", "Not in the set. Mention if you need filler.", "--"],
  ["Mitski", "Puberty 2 turns 10", "10th Anniversary Edition out Fri. Oct. 30 on Dead Oceans.", N("Mitski", "Your") + " Your Best American Girl"],
]));
kids.push(note("Focus calendar: goth and post-punk tonight, D.C. hardcore Nov. 5."));

kids.push(heading("Talk break: new and coming up", 24, 200));
kids.push(simpleTable([2300, 3600, 2200, 2100, 4200], ["Artist", "Release", "Label", "Date", "In tonight's set"], [
  ["Queens of the Stone Age", "Perfecth (ninth album; Josh Homme and Michael Shuman produced)", "Matador", { t: "Fri. Oct. 30", bold: true }, `${N("Queens of the Stone Age", "Where")} Where the Goth Girls At? (Triple Shot)`],
  ["Ministry", "Hate to Go (Take Out or Delivery), final album", "Cleopatra", { t: "Fri. Oct. 30", bold: true }, `${N("Ministry", "Every")} Every Day Is Halloween`],
  ["Mitski", "Puberty 2 10th Anniversary Edition", "Dead Oceans", { t: "Fri. Oct. 30", bold: true }, `${N("Mitski", "Your")} Your Best American Girl`],
  ["Fake Names", "Punk Ruins (third album)", "Epitaph", { t: "Fri. Oct. 23", bold: true }, `${N("Fake Names", "Punk")} Punk Ruins`],
  ["The Lemonheads with The Bevis Frond", "Roky (12-inch)", "Fire Records", { t: "Fri. Oct. 16", bold: true }, `${N("The Lemonheads", "Roky")} Roky`],
  ["Twisted Teens", "The Holy Cross Tigers", "Sub Pop", { t: "Fri. Nov. 6", bold: true }, `${N("Twisted Teens", "Circus")} and ${N("Twisted Teens", "Hand")} (reviewed albums)`],
  ["Lex Walton", "Ultimate Love Forever (CD and LP)", "Sub Pop", { t: "Fri. Nov. 20", bold: true }, `${N("Lex Walton", "Ultimate")} Ultimate Love 4Ever`],
]));
kids.push(spacer());

kids.push(heading("Reviewed albums in rotation (last 10 weeks)", 24, 120));
const REV = [
  ["Ty Segall", "Chrome", "Oct. 8", "Black Paint", "5", "Black"], ["Dread Spectre Council", "Thetans", "Oct. 8", "Raven", "5", "Raven"],
  ["Twisted Teens", "Blame the Clown", "Oct. 6", "Circus Clown", "4", "Circus"], ["Little Barrie", "Gravity Freeze", "Oct. 8", "It Isn't Soul", "3", "It Isn"],
  ["The Fall", "Post Script", "Oct. 15", "Retro Song", "4", "Retro"], ["This Is Lorelei", "The Singer in My Band", "Oct. 8", "Billy Came Back", "4", "Billy"],
  ["Sluice", "Companion", "Oct. 8", "Overhead", "5", "Overhead"], ["Palace", "Ox", "Oct. 8", "Dream On", "4", "Dream"],
  ["Lex Walton", "Ultimate Love Forever", "Oct. 8", "Ultimate Love 4Ever", "5", "Ultimate"], ["Sylvan Esso", "Ow ∞", "Oct. 15", "Flood Season", "4", "Flood"],
  ["Twisted Teens", "Florida Water Blues", "Oct. 8", "Hand Me A Cigarette", "5", "Hand"], ["Tricky", "Different When It's Silent", "Oct. 8", "I Still See Me There", "4", "I Still"],
  ["Yard Act", "You're Gonna Need A Little Music", "Oct. 15", "You're Gonna Need A Little Music", "5", "You're"],
];
kids.push(simpleTable([2600, 3600, 1500, 3700, 1000, 2000], ["Artist", "Album", "Posted", "Track tonight", "Stars", "On air"],
  REV.map((r) => [r[0], r[1], r[2], r[3], r[4], N(r[0], r[5])])));
kids.push(note("Posted = date the review went into Zookeeper. Tracks aired in October were skipped: Play Cowboys, Separation, Hex's Up, Hooves & Cloves, More Bad Miles Of Road, Luggin' Hurt, Peekaboo Hand, Top Of The World Hwy No. 2, Oh No Now My, Hey Sarah, Don't You Cry in Lonesomeness, Beadie, Zillow, Made My Bed, Denny's, For Thee I Sing, Adrian Borland, Because I Don't Know, Concrete Glen, New Beginnings, Over The Barrel, 30 Degrees, A Caveat."));
kids.push(spacer());
kids.push(micBreak("MIC BREAK: OPENING", mb("opening")));

// ---- Hour 1 ----
kids.push(heading("HOUR 1", 30, 0, true));
built.filter((b) => /^Hour 1/.test(b.set.set)).forEach((b) => {
  kids.push(b.table); kids.push(spacer());
  if (/Set 1/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 1 (HORROR-PUNK)", mb("after_set_1"))); kids.push(spacer()); }
  if (/Set 3/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: END OF HOUR 1", mb("end_hour_1").concat(["Tease: Thursday Triple Shot opens Hour 2: Queens of the Stone Age."]))); }
});

// ---- Hour 2 ----
kids.push(heading("HOUR 2", 30, 0, true));
built.filter((b) => !/^Hour 1/.test(b.set.set)).forEach((b) => {
  if (/Triple Shot/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: TRIPLE SHOT INTRO", mb("triple_shot_intro"))); kids.push(spacer()); }
  kids.push(b.table); kids.push(spacer());
  if (/Triple Shot/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER THE TRIPLE SHOT", mb("after_triple_shot"))); kids.push(spacer()); }
  if (/Set 6/.test(b.set.set)) {
    kids.push(heading("Talk break after Set 6: Bay Area shows, upcoming only (foopee.com, read Oct. 22 and 23; confirm before air)", 22));
    kids.push(simpleTable([2000, 4200, 3600, 4600], ["Date", "Act", "Venue", "Status"],
      plan.bay_area_shows.filter((s) => s.date !== "Source").map((s) => [{ t: s.date, bold: true }, s.what.split(". $")[0].split(" $")[0], s.venue, s.what.includes("$") ? s.what.slice(s.what.indexOf("$")) + (s.note ? " " + s.note : "") : (s.note || "")]),
      { keepTogether: true }));
    kids.push(note("Upcoming shows only. No ticket giveaway this week."));
    kids.push(spacer());
    kids.push(micBreak("MIC BREAK: BAY AREA", mb("bay_area_break")));
    kids.push(spacer());
  }
  if (/Set 7/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 7 (NEW, ANNIVERSARY AND NOVELTY)", mb("anniversary"))); kids.push(spacer()); }
});
kids.push(micBreak("MIC BREAK: CLOSING", mb("closing")));

// ---- Back of the sheet ----
kids.push(heading("FCC watch list", 28, 0, true));
const AMB = (t) => ({ t, color: AMBER, bold: true });
kids.push(simpleTable([3200, 2400, 1500, 7300], ["Artist and track", "Status", "Where", "Action"], [
  [{ t: "Fake Names, Punk Ruins", bold: true }, AMB("CLEAN, check by ear"), N("Fake Names", "Punk"), "Genius lyrics are short. Confirm by ear."],
  [{ t: "Coil, Where Even the Darkness Is Something to See", bold: true }, { t: "LISTEN FIRST", color: AMBER, bold: true }, N("Coil", "Where"), "New add. No lyrics on LRCLIB or Genius. Mostly instrumental with a sample; confirm by ear."],
  [{ t: "Misfits, Halloween", bold: true }, AMB("CLEAN"), N("Misfits", "Halloween"), "Screened Oct. 15 (LRCLIB). 1:53."],
  ["Your Air Order adds (10 tracks)", AMB("CLEAN (Genius)"), "Sets 1, 3, 5, 7", "Screened earlier by Genius word counts. No hits. Skinny Puppy Love is 40 words: confirm by ear."],
  ["Reviewed-album tracks (13)", AMB("Per your review"), "Sets 2, 3, 6", "Your Zookeeper reviews list FCC words per track; none of these 13 has a flag."],
  ["Lera Lynn & Shovels & Rope, Wolf Like Me", AMB("CLEAN"), N("Lera Lynn & Shovels & Rope", "Wolf"), "Genius, 396 words, no hits."],
  ["Public Image Ltd., Swan Lake (Death Disco)", AMB("CLEAN"), N("Public Image Ltd.", "Swan"), "Genius, 142 words, no hits."],
  [{ t: "Ministry, Burned Out", bold: true }, { t: "shit x1", color: RED }, "Held out", "Every Day Is Halloween stands in."],
  [{ t: "Black Lips, Bad Kids", bold: true }, { t: "shit x1", color: RED }, "Held out", "Not in set."],
  ["Tropical Fuck Storm", { t: "fuck in the band name", color: RED }, "Held out", "Do not announce the name on air."],
  ["Queens of the Stone Age, Easy Street", { t: "Cool-off to Dec. 8", color: RED }, "Held out", "Deleted from Weekly Oct. 9. Not an FCC issue."],
  ["Death Valley Girls, Basic Witch", { t: "Cool-off to Dec. 8", color: RED }, "Dropped", "Deleted from Weekly Oct. 9. Not an FCC issue."],
]));

kids.push(heading("Bench: extra tracks not in the Air Order", 28, 240));
kids.push(note("Replacement pool if you cut tracks tonight. Labels came from Zookeeper where the album is in the library; others marked in the plan."));
kids.push(simpleTable([2300, 3400, 3200, 2400, 1700, 1400], ["Artist", "Track", "Release", "Label", "Date", "FCC"], plan.bench.map((t) => {
  const st = t.fcc_status;
  const f = st === "CLEAN" ? { t: "CLEAN", color: GREEN, bold: true } : st === "CAUTION" ? { t: "CAUTION", color: AMBER, bold: true } : st === "FCC" ? { t: "HOLD", color: RED, bold: true } : { t: "LISTEN FIRST", color: AMBER, bold: true };
  return [t.artist, t.track, t.album || "-", (t.label || "-").replace(" (verify)", ""), String(t.released || "-"), f];
})));
kids.push(note("LISTEN FIRST means no lyrics were posted or the track was not screened."));

const doc = new Document({
  creator: "DJ Stace (Claude)",
  title: "Library Show Final Show Script 2026-10-29 (Landscape Tables)",
  styles: { default: { document: { run: { font: FONT, size: 18 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [run("The Library with DJ Stace  |  Oct. 29, 2026 (final)  |  Page ", { size: 14, color: "777777" }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: "777777" })] })] }) },
    children: kids,
  }],
});
const out = process.argv[2];
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out, buf.length, "bytes; total airable", fmt(total)); });
