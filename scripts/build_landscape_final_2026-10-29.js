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
const fmtMin = (s) => fmt(s);
kids.push(new Paragraph({ spacing: { after: 40 }, children: [run("The Library with DJ Stace: Final Show Script", { size: 36, bold: true, color: NAVY })] }));
kids.push(para("Thursday, Oct. 29, 2026  |  KZSU 90.1 FM  |  6-8 p.m. PT  |  Rebuilt Thu. Oct. 29 after your Air Order edits (55 tracks)  |  Halloween specialty show (punk and post-punk arc, week 3 of 4)  |  Landscape table version", { size: 18, color: "555555", after: 120 }));

let num = 1, cum = 0; const built = [];
for (const set of plan.sets) { const b = setTable(set, num, cum); num = b.nextNum; cum = b.cumEnd; built.push({ set, ...b }); }
const total = cum;
const h1 = built.filter((b) => /^Hour 1/.test(b.set.set)).reduce((a, b) => a + b.setSecs, 0);
const ALL = plan.sets.flatMap((s) => s.tracks);
const newTracks = ALL.filter((t) => t.source === "your_review_halloween");
const newSecs = newTracks.reduce((a, t) => a + secs(t.duration), 0);
const numOf = (t) => "#" + NN(t.artist, t.track.slice(0, 12));
const listNew = newTracks.map((t) => `${numOf(t)} ${t.artist}, ${t.track}`).join("; ");

kids.push(heading("Run of show", 26));
kids.push(simpleTable([6200, 1500, 1800, 2400, 2500], ["Set", "Tracks", "Set time", "Track numbers", "Running total"],
  built.map((b) => { const first = b.nextNum - b.count, last = b.nextNum - 1; return [b.set.set, String(b.count), fmt(b.setSecs), `${first}-${last}`, fmt(b.cumEnd)]; })
    .concat([[{ t: "Total (airable)", bold: true }, { t: String(built.reduce((a, b) => a + b.count, 0)), bold: true }, { t: fmt(total), bold: true }, `Hour 1 ${fmt(h1)}, Hour 2 ${fmt(total - h1)}`, { t: "Target 2:30:00", bold: true }]])));
kids.push(note(`FCC column: green CLEAN, amber means listen first or check by ear, red means hold out. Tag is the KZSU library tag; a dash means not in the library. Light blue rows are new since the Oct. 28 final. The list runs ${fmt(total)}. Without the ${newTracks.length} new tracks from your reviews it runs ${fmt(total - newSecs)}. Bench tracks (back pages) are not in the Air Order.`));

kids.push(heading("What changed since the Oct. 28 final", 24, 160));
kids.push(simpleTable([2600, 11800], ["Change", "Detail"], [
  [{ t: "Air Order read", bold: true }, "Read Thu. Oct. 29: 40 tracks (52 on Oct. 28). Your cuts and adds win. The Air Order keeps your order; this script groups the same tracks into themed sets."],
  [{ t: "Culled by you (13)", bold: true, fill: RED_BG }, { t: "The Fall Retro Song; Queens of the Stone Age No One Knows; Bambara Steel Dust Ocean; Mitski Your Best American Girl; Bobby Pickett Monster Mash; and eight reviewed-rotation tracks: This Is Lorelei Billy Came Back, Sluice Overhead, Palace Dream On, Lex Walton Ultimate Love 4Ever, Sylvan Esso Flood Season, Twisted Teens Hand Me A Cigarette, Tricky I Still See Me There, Yard Act You're Gonna Need A Little Music. Out of the script, the Zookeeper CSV and the sheet.", fill: RED_BG }],
  [{ t: "Replaced", bold: true }, "None. No Replace ticks in the Notes Sheet."],
  [{ t: "Added by you", bold: true, fill: CHANGE_BG }, { t: `${N("The Sisters Of Mercy", "This")} The Sisters of Mercy, This Corrosion (9:31; library copy is the compilation A Slight Case of Overbombing, tag 127022). Added Oct. 29 after the first rebuild: ${N("Dread Spectre Council", "Hex")} Dread Spectre Council, Hex's Up; ${N("The Flaming Lips", "God")} The Flaming Lips, God Will Control The Werewolves (Third Man, not in the library); ${N("BODEGA", "Fear")} Bodega, Fear not the Fear (listen first, no lyrics posted); ${N("Lambrini Girls", "Cult")} Lambrini Girls, Cult of Celebrity (City Slang, not in the library).`, fill: CHANGE_BG }],
  [{ t: "Triple Shot options", bold: true, fill: CHANGE_BG }, { t: `You asked for the Queens options. All three are in the Air Order and the Triple Shot set: ${N("Queens of the Stone Age", "Monsters")} Monsters in the Parasol (Rated R, 2000), ${N("Queens of the Stone Age", "If I")} If I Had a Tail (...Like Clockwork, 2013), ${N("Queens of the Stone Age", "Hangin")} Hangin' Tree (Songs for the Deaf, 2002). LRCLIB shows no flagged words in any of them. Pick one for the third song and cut the other two; the totals below count all three.`, fill: CHANGE_BG }],
  [{ t: `New from your reviews (${newTracks.length})`, bold: true, fill: CHANGE_BG }, { t: `Halloween-themed tracks you already reviewed: ${listNew}. All are in the library with a tag. FCC status comes from your review. Added to the bottom of your Air Order so you can preview them.`, fill: CHANGE_BG }],
  [{ t: "Rearranged", bold: true }, "Eight themed sets: horror-punk anthems, haunted covers, black and cats and fuzz, the devil's set (closes Hour 1), the Triple Shot, ghosts and graveyards, goth and post-punk, and an industrial and long-dark closer ending on Black Sabbath."],
  [{ t: "Triple Shot", bold: true }, `${N("Queens of the Stone Age", "Where")} Where the Goth Girls At? and ${N("Queens of the Stone Age", "Burn")} Burn the Witch are set. The third song is your pick from the three options above (${N("Queens of the Stone Age", "Monsters")}, ${N("Queens of the Stone Age", "If I")}, ${N("Queens of the Stone Age", "Hangin")}).`],
  [{ t: "Length", bold: true }, `All tracks: ${fmt(total)}. Without the new review picks: ${fmt(total - newSecs)}. You cull on air; the first cuts are the new picks, then the long closers (Bauhaus 9:37, Sabbath 9:26, This Corrosion 9:31, Alien Sex Fiend 7:58).`],
  [{ t: "Kept as is", bold: true }, `Both Sonics versions of The Witch (${NN("The Sonics", "The Witch")} and the second one). Cut one on air if you want only one.`],
]));

kids.push(heading("What is in this show", 24, 200));
kids.push(simpleTable([2600, 11800], ["Item", "Detail"], [
  [{ t: "Theme", bold: true }, "Halloween specialty show. Punk and post-punk arc, week 3 of 4. The Triple Shot opens Hour 2."],
  [{ t: "Your reviews on air", bold: true }, "13 reviewed tracks: Ty Segall, Dread Spectre Council (Raven and your add Hex's Up), Twisted Teens and Little Barrie from the October rotation, plus the eight new picks. Table below."],
  [{ t: "Triple Shot", bold: true }, `Queens of the Stone Age (${N("Queens of the Stone Age", "Where")}-${N("Queens of the Stone Age", "Hangin")}). New single from Perfecth, out Fri. Oct. 30 on Matador. Third song is your pick of three options. Easy Street stays out (cool-off to Dec. 8).`],
  [{ t: "Punk and post-punk focus", bold: true }, `Fuzz and punk in Set 3 (${N("Fake Names", "Punk")} Fake Names, ${N("So Pitted", "cat")} So Pitted), goth and post-punk in Set 7 (${N("Siouxsie and the Banshees", "Spell")}-${N("Talking Heads", "Psycho")}). Killing Joke and Iceage are in cool-off.`],
  [{ t: "Dropped", bold: true }, { t: "Death Valley Girls, Basic Witch: you deleted it from Weekly Oct. 9 (60-day cool-off to Dec. 8). Ministry Burned Out (shit x1), Black Lips Bad Kids (shit x1) and Tropical Fuck Storm stay out for FCC.", color: RED }],
  [{ t: "Ticket giveaway", bold: true }, "None placed. No sheet row lists Stace with a give-by date on or after Oct. 29. Katie Pruitt (Chapel, Oct. 29, listed DJ Mr Bones) gave by 10/28. Send a current row if you want one."],
  [{ t: "Release timing", bold: true }, "Queens of the Stone Age and Ministry land Fri. Oct. 30, one day after the show. Say \"out tomorrow.\""],
]));

kids.push(heading("Talk break: Today in music", 24, 200));
kids.push(simpleTable([2600, 3300, 6000, 2500], ["Artist or place", "Item", "Fact", "In tonight's set"], [
  ["Orson Welles", "War of the Worlds (Oct. 30, 1938)", "CBS aired it at 8 p.m. ET on The Mercury Theatre on the Air, Howard Koch script. The FCC investigated and found no law was broken. A radio story for a radio show.", "After the Triple Shot"],
  ["Black Sabbath", "Reunion on Letterman (Oct. 30, 1998)", "All four original members played Paranoid on the Late Show. Confirmed by IMDb episode listing, Louder and Black Sabbath Online.", N("Black Sabbath", "Black Sabbath") + " Black Sabbath (closer)"],
  ["The Cure", "Roger O'Donnell birthday", "Born Oct. 29, 1955. Keyboards on Disintegration (1989). The library holds the Lullaby single.", N("The Cure", "Lullaby") + " Lullaby"],
  ["The Who", "My Generation (UK single, Oct. 29, 1965)", "Not in the set. Mention if you need filler.", "--"],
]));
kids.push(note("Focus calendar: goth and post-punk tonight, D.C. hardcore Nov. 5."));

kids.push(heading("Talk break: new and coming up", 24, 200));
kids.push(simpleTable([2300, 3600, 2200, 2100, 4200], ["Artist", "Release", "Label", "Date", "In tonight's set"], [
  ["Queens of the Stone Age", "Perfecth (ninth album; Josh Homme and Michael Shuman produced)", "Matador", { t: "Fri. Oct. 30", bold: true }, `${N("Queens of the Stone Age", "Where")} Where the Goth Girls At? (Triple Shot)`],
  ["Ministry", "Hate to Go (Take Out or Delivery), final album", "Cleopatra", { t: "Fri. Oct. 30", bold: true }, `${N("Ministry", "Every")} Every Day Is Halloween`],
  ["Fake Names", "Punk Ruins (third album)", "Epitaph", { t: "Fri. Oct. 23", bold: true }, `${N("Fake Names", "Punk")} Punk Ruins`],
  ["The Lemonheads with The Bevis Frond", "Roky (12-inch)", "Fire Records", { t: "Fri. Oct. 16", bold: true }, `${N("The Lemonheads", "Roky")} Roky`],
  ["Twisted Teens", "The Holy Cross Tigers", "Sub Pop", { t: "Fri. Nov. 6", bold: true }, `${N("Twisted Teens", "Circus")} Circus Clown (from Blame the Clown)`],
]));
kids.push(spacer());

kids.push(heading("Your reviews on air tonight", 24, 120));
const REVROWS = [
  ["Ty Segall", "Chrome", "Oct. 8, 2026", "Black Paint", "5", N("Ty Segall", "Black")],
  ["Dread Spectre Council", "Thetans", "Oct. 8, 2026", "Raven", "5", N("Dread Spectre Council", "Raven")],
  ["Dread Spectre Council", "Thetans", "Oct. 8, 2026", "Hex's Up (your add; two tracks from one album)", "5", N("Dread Spectre Council", "Hex")],
  ["Twisted Teens", "Blame the Clown", "Oct. 6, 2026", "Circus Clown", "4", N("Twisted Teens", "Circus")],
  ["Little Barrie", "Gravity Freeze", "Oct. 8, 2026", "It Isn't Soul", "3", N("Little Barrie", "It Isn")],
].concat(newTracks.map((t) => { const m = /^(\S+) stars? reviewed (.+)$/.exec(t.review || "") || []; return [t.artist, t.album, m[2] || "", t.track, m[1] === "unrated" ? "-" : (m[1] || "-"), numOf(t)]; }));
kids.push(simpleTable([2600, 3600, 1700, 3400, 900, 2200], ["Artist", "Album", "Reviewed", "Track tonight", "Stars", "On air"], REVROWS));
kids.push(note("Stars are your track-level stars from the review. So Pitted cat scratch has no star rating in the review. Cut from the rotation by you: Lorelei, Sluice, Palace, Lex Walton, Sylvan Esso, Twisted Teens Florida Water Blues, Tricky, Yard Act, The Fall."));
kids.push(spacer());
kids.push(micBreak("MIC BREAK: OPENING", mb("opening")));

// ---- Hour 1 ----
kids.push(heading("HOUR 1", 30, 0, true));
built.filter((b) => /^Hour 1/.test(b.set.set)).forEach((b) => {
  kids.push(b.table); kids.push(spacer());
  if (/Set 1/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 1 (HORROR-PUNK)", mb("after_set_1"))); kids.push(spacer()); }
  if (/Set 2/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 2 (COVERS)", mb("after_set_2"))); kids.push(spacer()); }
  if (/Set 3/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 3 (FUZZ)", mb("after_set_3"))); kids.push(spacer()); }
  if (/Set 4/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: END OF HOUR 1", mb("end_hour_1"))); }
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
  if (/Set 7/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 7 (GOTH AND POST-PUNK)", mb("after_goth"))); kids.push(spacer()); }
});
kids.push(micBreak("MIC BREAK: CLOSING", mb("closing")));

// ---- Back of the sheet ----
kids.push(heading("FCC watch list", 28, 0, true));
const AMB = (t) => ({ t, color: AMBER, bold: true });
kids.push(simpleTable([3200, 2400, 1500, 7300], ["Artist and track", "Status", "Where", "Action"], [
  [{ t: "Coil, Where Even the Darkness Is Something to See", bold: true }, { t: "LISTEN FIRST", color: AMBER, bold: true }, N("Coil", "Where"), "No lyrics on LRCLIB or Genius. Mostly instrumental with a sample; confirm by ear."],
  [{ t: "Fake Names, Punk Ruins", bold: true }, AMB("CLEAN, check by ear"), N("Fake Names", "Punk"), "Genius lyrics are short. Confirm by ear."],
  ["Skinny Puppy, Love", AMB("CLEAN, check by ear"), N("Skinny Puppy", "Love"), "Genius posts 40 words. Confirm by ear."],
  [{ t: "Review picks with no lyrics posted", bold: true }, AMB("Per your review"), `${N("Angélica Garcia", "Lucifer")}, ${N("The Mars Volta", "Graveyard")}, ${N("A Giant Dog", "Black")}, ${N("So Pitted", "cat")}`, "Your reviews flag FCC words by track number; none of these four tracks is flagged. Confirm by ear if you have not played them in a while."],
  ["Other new review picks (4)", AMB("CLEAN (LRCLIB)"), `${N("Adia Victoria", "Devil")}, ${N("L’epée", "Ghost")}, ${N("Black Pumas", "Black")}, ${N("Stef Chura", "Eyes")}`, "LRCLIB lyrics show no flagged words."],
  ["The Sisters of Mercy, This Corrosion", AMB("CLEAN"), N("The Sisters Of Mercy", "This"), "LRCLIB, 662 words, no hits."],
  [{ t: "Bodega, Fear not the Fear", bold: true }, { t: "LISTEN FIRST", color: AMBER, bold: true }, N("BODEGA", "Fear"), "New add. No lyrics posted. The review template flags FCC words only on the title track (fuck x2), which is not in the set. Confirm this one by ear."],
  ["Queens Triple Shot options (3)", AMB("CLEAN (LRCLIB)"), `${N("Queens of the Stone Age", "Monsters")}, ${N("Queens of the Stone Age", "If I")}, ${N("Queens of the Stone Age", "Hangin")}`, "LRCLIB: 191, 201 and 123 words, no flagged words."],
  ["Lambrini Girls, Cult of Celebrity", AMB("CLEAN (LRCLIB)"), N("Lambrini Girls", "Cult"), "LRCLIB, 224 words, no hits. Band is known for strong language; the earlier single The Basement has shit x3."],
  ["Flaming Lips, God Will Control The Werewolves", AMB("CLEAN (Genius)"), N("The Flaming Lips", "God"), "Genius, 155 words, no hits."],
  ["Your other Air Order adds", AMB("CLEAN (Genius)"), "Sets 1, 2, 3, 4, 7, 8", "Screened earlier by Genius word counts. No hits."],
  ["Lera Lynn & Shovels & Rope, Wolf Like Me", AMB("CLEAN"), N("Lera Lynn & Shovels & Rope", "Wolf"), "Genius, 396 words, no hits."],
  ["Public Image Ltd., Swan Lake (Death Disco)", AMB("CLEAN"), N("Public Image Ltd.", "Swan"), "Genius, 142 words, no hits."],
  [{ t: "Ministry, Burned Out", bold: true }, { t: "shit x1", color: RED }, "Held out", "Every Day Is Halloween stands in."],
  [{ t: "Black Lips, Bad Kids", bold: true }, { t: "shit x1", color: RED }, "Held out", "Not in set."],
  ["Tropical Fuck Storm", { t: "fuck in the band name", color: RED }, "Held out", "Do not announce the name on air."],
  ["Queens of the Stone Age, Easy Street", { t: "Cool-off to Dec. 8", color: RED }, "Held out", "Deleted from Weekly Oct. 9. Not an FCC issue."],
  ["Death Valley Girls, Basic Witch", { t: "Cool-off to Dec. 8", color: RED }, "Dropped", "Deleted from Weekly Oct. 9. Not an FCC issue."],
]));

kids.push(heading("More Halloween picks from your reviews (not in the Air Order)", 28, 240));
kids.push(note("Swap-ins if you want more. FCC comes from the flagged track numbers in your reviews; none of these tracks is flagged (the Death Song review lists no FCC line at all, so confirm Death March by ear). Dread Spectre Council tracks are the same album as Raven, so use one per show."));
kids.push(simpleTable([2300, 3000, 3000, 2300, 1100, 1700, 1000], ["Artist", "Track", "Album", "Label", "Tag", "Reviewed", "Time"], [
  ["Built to Spill", "Spiderweb", "When the Wind Forgets Your Name", "Sub Pop Records", "1148307", "Jan. 15, 2023", "5:24"],
  ["The Black Angels", "Death March", "Death Song", "Partisan Records", "1107032", "May 8, 2017", "3:25"],
  ["Dread Spectre Council", "Spiderette", "Thetans", "Handmade Records", "1156474", "Oct. 8, 2026", "4:21"],
  ["Dread Spectre Council", "Evil Incarnate", "Thetans", "Handmade Records", "1156474", "Oct. 8, 2026", "2:37"],
  ["L’epée", "La Brigade des Maléfices", "Diabolique", "A Recordings", "1139464", "Oct. 12, 2019", "-"],
  ["The Mars Volta", "Blacklight Shine", "The Mars Volta", "Clouds Hill", "1148251", "Jan. 8, 2023", "-"],
  ["Stef Chura", "Sweet Sweet Midnight", "Midnight", "Saddle Creek", "1135774", "July 5, 2019", "5:29"],
  ["Twisted Teens", "Corpse Pose", "Blame the Clown", "Chain Smoking Records", "1156418", "Oct. 6, 2026", "1:02"],
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
