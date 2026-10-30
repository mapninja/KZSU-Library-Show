// build_landscape_working_2026-11-05.js
// Builds the landscape, table-based WORKING Show Script for The Library (Thursday, Nov. 5, 2026).
// Reads the show plan directly: data/recon/2026-11-05/working_playlist.json
// Run from the repo root:  node scripts/build_landscape_working_2026-11-05.js "<out>.docx"
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
const plan = JSON.parse(fs.readFileSync(path.join(REPO, "data/recon/2026-11-05/working_playlist.json"), "utf8"));
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
    const extra = held ? " FCC: " + t.fcc_note : (f.t === "CLEAN, check ear" ? " " + (t.fcc_note || "Check by ear.") : (f.t === "LISTEN FIRST" ? " " + (t.fcc_note || "") : ""));
    const ytm = t.ytm_missing ? " NOT ON YOUTUBE MUSIC: play the library CD." : "";
    const notes = (held ? "HELD OUT of Zookeeper CSV. " : "") + (t.why || "") + ytm + extra;
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
kids.push(para("Thursday, Nov. 5, 2026  |  KZSU 90.1 FM  |  6-8 p.m. PT  |  Draft built Thu. Oct. 29 (Thursday-night run)  |  Punk and post-punk arc, week 4 of 4  |  Landscape table version", { size: 18, color: "555555", after: 120 }));

let num = 1, cum = 0; const built = [];
for (const set of plan.sets) { const b = setTable(set, num, cum); num = b.nextNum; cum = b.cumEnd; built.push({ set, ...b }); }
const total = cum;
const h1 = built.filter((b) => /^Hour 1/.test(b.set.set)).reduce((a, b) => a + b.setSecs, 0);

kids.push(heading("Run of show", 26));
kids.push(simpleTable([6200, 1500, 1800, 2400, 2500], ["Set", "Tracks", "Set time", "Track numbers", "Running total"],
  built.map((b) => { const first = b.nextNum - b.count, last = b.nextNum - 1; return [b.set.set, String(b.count), fmt(b.setSecs), `${first}-${last}`, fmt(b.cumEnd)]; })
    .concat([[{ t: "Total (airable)", bold: true }, { t: String(built.reduce((a, b) => a + b.count, 0)), bold: true }, { t: fmt(total), bold: true }, `Hour 1 ${fmt(h1)}, Hour 2 ${fmt(total - h1)}`, { t: "Target 2:30:00", bold: true }]])));
kids.push(note("FCC column: green CLEAN, amber means listen first or check by ear, red means hold out. Tag is the KZSU library tag; a dash means not in the library. The list runs " + fmt(Math.max(0, total - 9000)) + " over the 2:30 target. Bench tracks (back page) are not in the Air Order."));

kids.push(heading("What is in this draft", 24, 160));
kids.push(simpleTable([2600, 11800], ["Item", "Detail"], [
  [{ t: "Theme", bold: true }, "Regular show. New releases from Fri. Oct. 30, anniversaries from 1991, 1996 and 2001, Bay Area shows for Nov. 5 to 8, and the punk and post-punk arc (week 4 of 4; review Nov. 12)."],
  [{ t: "New this week", bold: true }, `Out Fri. Oct. 30: Queens of the Stone Age (${N("Queens of the Stone Age", "Run")}), Clinic (${N("Clinic", "Wild")}), Ex:Re (${N("Ex:Re", "Radio")}), Sennen (${N("Sennen", "Here")}), DIIV (${N("DIIV", "Dare")}) and Thao (Triple Shot). Twisted Teens' album is out Fri. Nov. 6 (${N("Twisted Teens", "When")}).`],
  [{ t: "Triple Shot", bold: true }, `Thao (${N("Thao & The Get Down Stay Down", "Bag")}-${N("THAO", "Sick")}). New album Show Me out Oct. 30 on Kill Rock Stars; album release show at the Independent Sun. Nov. 8. Sick of the Times has no posted lyrics: listen first. Swap on the bench: We the Common.`],
  [{ t: "Reviewed albums in rotation", bold: true }, "Week 4 for the ten albums posted Oct. 4 to 8: five play (Twisted Teens Blame the Clown, Palace, Lex Walton, Ty Segall, This Is Lorelei). Week 3 for The Fall, Sylvan Esso and Yard Act. 8 tracks. Table below."],
  [{ t: "Anniversaries", bold: true }, `Set 3 (${N("my bloody valentine", "Only")}-${N("The National", "American")}): Loveless 35, Bandwagonesque 35, Being There 30, Unchained 30 (on show day), The Natural Bridge 30, Ride the Fader 30, The National 25. Loveless is not on YouTube Music: play the library CD.`],
  [{ t: "Punk and post-punk focus", bold: true }, `Set 6 (${N("Dicks", "Hate")}-${N("TV Priest", "Decoration")}) with the Texas slot (Dicks) plus Team Dresch (${N("Team Dresch", "Hand")}) and Colleen Green (${N("Colleen Green", "Whatever")}) in the Bay Area set.`],
  [{ t: "Machines set", bold: true }, `Kraftwerk and Cabaret Voltaire (${N("Kraftwerk", "Numbers")}-${N("Cabaret Voltaire", "Nag")}), requested back Oct. 16 and unaired Oct. 15 and Oct. 22. Hot Chip joins from your Next Show playlist.`],
  [{ t: "Your Next Show adds", bold: true }, "Twisted Teens When We First Met, Palace Made My Bed, Ty Segall Play Cowboys, This Is Lorelei Hey Sarah, The Linda Lindas, Sprints, TV Priest, Hot Chip, John Lennon and Chris Cornell (newest add). Many more are on the bench."],
  [{ t: "Held out", bold: true }, { t: "Queens of the Stone Age Easy Street (fuck x1, Verse 2; also in cool-off to Dec. 8) and Greg Freeman Cahokia (fuck x1, shit x1). Clinic You and I, DIIV Trillions, Lambrini Girls Spilt and The Garden Bootleg are in cool-off (your deletes).", color: RED }],
  [{ t: "Ticket giveaway", bold: true }, "None placed. The repo has no November ticket sheet (October ends Oct. 29). Send current rows if there is a giveaway for Nov. 5 or later."],
  [{ t: "Labels and tags", bold: true }, "Zookeeper checked Oct. 29. Fill in at the studio or verify: Sprints (Nice Swan, not in the label table), Sour Widows (Julia's War), Michael Nau (Suicide Squeeze), Olivia Tremor Control (Elephant 6). Not in the library yet: the Oct. 30 albums, The National, John Lennon, Thao & The Get Down Stay Down."],
  [{ t: "Dates to verify", bold: true }, "Silver Jews (Oct. 30, 1996), Chavez (Nov. 5, 1996) and The National (Oct. 30, 2001) rest on one source (Wikipedia). Teenage Fanclub's day (Nov. 4) is one source."],
]));

kids.push(heading("Talk break: Today in music", 24, 200));
kids.push(simpleTable([2600, 3300, 6000, 2500], ["Artist or place", "Item", "Fact", "In tonight's set"], [
  ["Johnny Cash", "Unchained (Nov. 5, 1996)", "Second American Recordings album with Rick Rubin. Tom Petty and the Heartbreakers back Cash. Won the Grammy for Best Country Album. Rusty Cage is a Soundgarden cover.", N("Johnny Cash", "Rusty") + " Rusty Cage"],
  ["The Fall", "Are You Are Missing Winner (Nov. 5, 2001)", "Released on Cog Sinister. Wikipedia and Discogs agree on the date. Tonight's Fall track is from Post Script (2026).", N("The Fall", "A Caveat") + " A Caveat"],
  ["My Bloody Valentine", "Loveless (Nov. 4, 1991)", "Creation in the UK, Sire in the US. Wikipedia and Creation Records agree on the date. Not on YouTube Music.", N("my bloody valentine", "Only") + " Only Shallow"],
  ["Teenage Fanclub", "Bandwagonesque (Nov. 1991)", "Creation in the UK, Geffen in the US. Star Sign reached No. 4 on Billboard Modern Rock Tracks. Day: verify.", N("Teenage Fanclub", "What") + " What You Do To Me"],
  ["Wilco", "Being There (Oct. 29, 1996)", "Reprise. A 19-track double album sold at a single-album price. 30 years last Thursday.", N("Wilco", "Outtasite") + " Outtasite"],
]));
kids.push(note("Focus calendar: punk and post-punk arc ends with the Nov. 12 review. Nov. 5 is also Guy Fawkes Night in the UK (not in the set)."));

kids.push(heading("Talk break: new and coming up", 24, 200));
kids.push(simpleTable([2300, 3600, 2200, 2100, 4200], ["Artist", "Release", "Label", "Date", "In tonight's set"], [
  ["Queens of the Stone Age", "Perfecth (ninth album; Josh Homme and Michael Shuman produced)", "Matador", { t: "Fri. Oct. 30", bold: true }, `${N("Queens of the Stone Age", "Run")} Run Away From the Mob`],
  ["Clinic", "Wild in the Streets (tenth album, 12 songs)", "Domino", { t: "Fri. Oct. 30", bold: true }, `${N("Clinic", "Wild")} Wild In The Streets`],
  ["DIIV", "ZIRP! (fifth album; A. G. Cook produced)", "Fantasy (Concord)", { t: "Fri. Oct. 30", bold: true }, `${N("DIIV", "Dare")} Dare Me`],
  ["Ex:Re", "Save As (second album; Elena Tonra of Daughter)", "4AD", { t: "Fri. Oct. 30", bold: true }, `${N("Ex:Re", "Radio")} Radio Station`],
  ["Sennen", "New Quiet (first album since 2016)", "Sonic Cathedral", { t: "Fri. Oct. 30", bold: true }, `${N("Sennen", "Here")} Here It Comes`],
  ["Thao", "Show Me (first album in six years; Tune-Yards co-produced)", "Kill Rock Stars", { t: "Fri. Oct. 30", bold: true }, `${N("THAO", "Sick")} Sick of the Times (Triple Shot)`],
  ["Twisted Teens", "Holy Cross Tigers", "Sub Pop", { t: "Fri. Nov. 6", bold: true }, `${N("Twisted Teens", "When")} When We First Met; ${N("Twisted Teens", "Circus")} Circus Clown (reviewed album)`],
  ["Lex Walton", "Ultimate Love Forever (CD and LP)", "Sub Pop", { t: "Fri. Nov. 20", bold: true }, `${N("Lex Walton", "Adrian")} Adrian Borland Will Have His Revenge On London`],
  ["Hot Chip", "A Long Way From Kansas (ninth album)", "Domino", { t: "Fri. Jan. 8, 2027", bold: true }, `${N("Hot Chip", "Random")} Random Violence (tribute to JD Twitch)`],
]));
kids.push(spacer());

kids.push(heading("Reviewed albums in rotation (last 10 weeks)", 24, 120));
const REV = [
  ["Twisted Teens", "Blame the Clown", "Oct. 6", "Circus Clown", "4", "Circus", "Week 4"], ["Palace", "Ox", "Oct. 8", "Made My Bed", "-", "Made", "Week 4"],
  ["Lex Walton", "Ultimate Love Forever", "Oct. 8", "Adrian Borland Will Have His Revenge On London", "-", "Adrian", "Week 4"], ["Ty Segall", "Chrome", "Oct. 8", "Play Cowboys", "-", "Play", "Week 4"],
  ["This Is Lorelei", "The Singer in My Band", "Oct. 8", "Hey Sarah Is It Gonna Rain Forever", "-", "Hey", "Week 4"], ["The Fall", "Post Script", "Oct. 15", "A Caveat", "4", "A Caveat", "Week 3"],
  ["Sylvan Esso", "Ow ∞", "Oct. 15", "Concrete Glen", "4", "Concrete", "Week 3"], ["Yard Act", "You're Gonna Need A Little Music", "Oct. 15", "Over The Barrel", "-", "Over", "Week 3"],
];
kids.push(simpleTable([2300, 3300, 1200, 3700, 900, 1500, 1500], ["Artist", "Album", "Posted", "Track tonight", "Stars", "On air", "Rotation"],
  REV.map((r) => [r[0], r[1], r[2], r[3], r[4], N(r[0], r[5]), r[6]])));
kids.push(note("Stars shown only where an earlier plan recorded them; a dash means not checked this week. Resting this week: Twisted Teens Florida Water Blues, Dread Spectre Council Thetans, Little Barrie Gravity Freeze, Sluice Companion, Tricky Different When It's Silent. Your Oct. 29 cuts (Overhead, Dream On, Ultimate Love 4Ever, Hand Me A Cigarette, I Still See Me There, Billy Came Back, Retro Song, Flood Season, the Yard Act title track, Hex's Up, Black Paint) were show-length cuts; other tracks from the same albums stand in. Skipped as aired in the last 21 days: Peekaboo Hand, Denny's, For Thee I Sing, Separation, Don't You Cry in Lonesomeness, Hooves & Cloves, Raven, More Bad Miles Of Road, Beadie, Zillow, Because I Don't Know, New Beginnings, 30 Degrees."));
kids.push(spacer());
kids.push(micBreak("MIC BREAK: OPENING", mb("opening")));

// ---- Hour 1 ----
kids.push(heading("HOUR 1", 30, 0, true));
built.filter((b) => /^Hour 1/.test(b.set.set)).forEach((b) => {
  kids.push(b.table); kids.push(spacer());
  if (/Set 1/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 1 (NEW THIS WEEK)", mb("after_new"))); kids.push(spacer()); }
  if (/Set 3/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: ANNIVERSARIES AND END OF HOUR 1", mb("anniversary").concat(mb("end_hour_1")).concat(["Tease: Thursday Triple Shot opens Hour 2: Thao."]))); }
});

// ---- Hour 2 ----
kids.push(heading("HOUR 2", 30, 0, true));
built.filter((b) => !/^Hour 1/.test(b.set.set)).forEach((b) => {
  if (/Triple Shot/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: TRIPLE SHOT INTRO", mb("triple_shot_intro"))); kids.push(spacer()); }
  kids.push(b.table); kids.push(spacer());
  if (/Triple Shot/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER THE TRIPLE SHOT", mb("after_triple_shot"))); kids.push(spacer()); }
  if (/Set 5/.test(b.set.set)) {
    kids.push(heading("Talk break after Set 5: Bay Area shows, upcoming only (foopee.com, read Oct. 29; confirm before air)", 22));
    kids.push(simpleTable([2000, 4800, 3000, 4600], ["Date", "Act", "Venue", "Detail"],
      plan.bay_area_shows.map((s) => [{ t: s.date, bold: true }, s.act, s.venue, (s.detail + (s.note ? " " + s.note : "")).trim()]),
      { keepTogether: true }));
    kids.push(note("Upcoming shows only. No ticket giveaway placed (no November ticket sheet)."));
    kids.push(spacer());
    kids.push(micBreak("MIC BREAK: BAY AREA", mb("bay_area_break")));
    kids.push(spacer());
  }
  if (/Set 7/.test(b.set.set)) { kids.push(micBreak("MIC BREAK: AFTER SET 7 (MACHINES)", mb("after_machines"))); kids.push(spacer()); }
});
kids.push(micBreak("MIC BREAK: CLOSING", mb("closing")));

// ---- Back of the sheet ----
kids.push(heading("FCC watch list", 28, 0, true));
const AMB = (t) => ({ t, color: AMBER, bold: true });
kids.push(simpleTable([3600, 2400, 1500, 6900], ["Artist and track", "Status", "Where", "Action"], [
  [{ t: "Clinic, Wild In The Streets", bold: true }, AMB("LISTEN FIRST"), N("Clinic", "Wild"), "No lyrics posted (Genius and LRCLIB). 2:06 title track. Listen before air."],
  [{ t: "THAO, Sick of the Times", bold: true }, AMB("LISTEN FIRST"), N("THAO", "Sick"), "No lyrics posted (Genius and LRCLIB). Swap: We the Common (CLEAN, 283 words) on the bench."],
  ["Twisted Teens, When We First Met", AMB("CLEAN"), N("Twisted Teens", "When"), "Screened in an earlier week. 1:53."],
  [{ t: "Queens of the Stone Age, Easy Street", bold: true }, { t: "fuck x1 (Verse 2)", color: RED }, "Held out", "Run Away From the Mob (CLEAN, 235 words) stands in. Cool-off to Dec. 8 anyway."],
  [{ t: "Greg Freeman, Cahokia", bold: true }, { t: "fuck x1 (intro), shit x1 (Chorus)", color: RED }, "Held out", "In the Weekly Playlist; he plays the Independent Thu. Nov. 5."],
  ["Clinic, You and I", { t: "Cool-off to Dec. 22", color: RED }, "Dropped", "Your delete Oct. 23. Not an FCC issue."],
  ["DIIV, Trillions", { t: "Cool-off to Dec. 15", color: RED }, "Dropped", "Your delete Oct. 16. Not an FCC issue."],
  ["Lambrini Girls, Spilt; The Garden, Bootleg", { t: "Cool-off to Dec. 26", color: RED }, "Dropped", "Your deletes Oct. 27. Not an FCC issue."],
  ["Everything else in the Air Order", AMB("CLEAN"), "Sets 1-8", "Genius, LRCLIB or your reviews found no FCC or caution words. Crowd-sourced lyrics can be wrong; listen first where a track is new to you."],
]));

kids.push(heading("Bench: extra tracks not in the Air Order", 28, 240));
kids.push(note("Replacement pool if you cut tracks tonight. Many come from your Next Show playlist. Labels came from Zookeeper where the album is in the library; others marked in the plan."));
kids.push(simpleTable([2300, 3400, 3200, 2400, 1700, 1400], ["Artist", "Track", "Release", "Label", "Date", "FCC"], plan.bench.map((t) => {
  const st = t.fcc_status;
  const f = st === "CLEAN" ? { t: "CLEAN", color: GREEN, bold: true } : st === "CAUTION" ? { t: "CAUTION", color: AMBER, bold: true } : st === "FCC" ? { t: "HOLD", color: RED, bold: true } : { t: "LISTEN FIRST", color: AMBER, bold: true };
  return [t.artist, t.track, t.album || "-", (t.label || "-").replace(" (verify)", ""), String(t.released || "-"), f];
})));
kids.push(note("LISTEN FIRST means no lyrics were posted or the track was not screened."));

const doc = new Document({
  creator: "DJ Stace (Claude)",
  title: "Library Show Working Show Script 2026-11-05 (Landscape Tables)",
  styles: { default: { document: { run: { font: FONT, size: 18 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [run("The Library with DJ Stace  |  Nov. 5, 2026 (working draft)  |  Page ", { size: 14, color: "777777" }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: "777777" })] })] }) },
    children: kids,
  }],
});
const out = process.argv[2];
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out, buf.length, "bytes; total airable", fmt(total)); });
