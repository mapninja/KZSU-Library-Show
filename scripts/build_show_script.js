// build_show_script.js
// ONE builder for every Library Show script (draft, final, specialty, short shows).
// Replaces the dated one-off builders (build_landscape_final_2026-10-29.js and friends).
//
// WHAT IT MAKES
//   A landscape Word file with the TRACKLIST FIRST, so the on-air page is the first page you open.
//   One table, columns: #, Artist, Track, Album, Orig. release, FCC, ZK tag, Time, Notes.
//   Thin "MIC BREAK" rows sit between sets. All general show info (talk breaks, today in
//   music, new releases, Bay Area shows, giveaway, FCC watch list, bench) comes AFTER the tracklist.
//
// HOW TO RUN (from the repo root)
//   node scripts/build_show_script.js 2026-11-05 draft  outputs/recon/2026-11-05
//   node scripts/build_show_script.js 2026-11-05 final  outputs/recon/2026-11-05
//   Then make the PDF: scripts/build_show_script.sh 2026-11-05 final   (runs this file, then LibreOffice)
//
// INPUT  data/recon/<date>/working_playlist.json   (the plan; tracks with priority SKIP or CUT never print)
//   Per track fields used: artist, track, album, released, fcc_status, fcc_note, tag, duration,
//   why (curatorial note), credits (producer, studio, year), related (related bands), notes (free text).
//   Notes cell = notes || why, then "Prod:" credits and "Related:" bands when present.
//
// Beginner notes
//   * "docx" is an npm library that writes Word files. A Table is rows; a row is cells; a cell holds paragraphs.
//   * Times are "m:ss" strings. secs() turns them into seconds so we can add them up.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, AlignmentType, PageOrientation, Footer, PageNumber, VerticalAlign,
} = require("docx");

const [showDate, stage = "final", outDir = "."] = process.argv.slice(2);
if (!showDate) { console.error("usage: node build_show_script.js <YYYY-MM-DD> <draft|final> [outDir]"); process.exit(1); }
const REPO = path.resolve(__dirname, "..");
const plan = JSON.parse(fs.readFileSync(path.join(REPO, "data/recon", showDate, "working_playlist.json"), "utf8"));
const STAGE = stage.toUpperCase();
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const nice = (iso) => { const [y, m, d] = iso.split("-").map(Number); const wd = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
  return `${["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][wd]}, ${MONTHS[m - 1]}. ${d}, ${y}`; };

// ---- look and feel ----
const FONT = "Arial", PAGE_W = 14400; // 11 in minus 0.5 in margins, in DXA (1/20 pt)
const NAVY = "1F3864", BAND = "D9E2F3", ZEBRA = "F5F7FA", RED_BG = "F8D7DA", AMBER_BG = "FFF3CD", GREEN_BG = "E2F0D9";
const GREEN = "1B7F3B", RED = "B00020", AMBER = "8A6100";
const line = { style: BorderStyle.SINGLE, size: 4, color: "B7B7B7" };
const borders = { top: line, bottom: line, left: line, right: line };
const run = (text, o = {}) => new TextRun({ text: String(text), font: FONT, size: o.size || 18, bold: o.bold, color: o.color, italics: o.italics });
const para = (text, o = {}) => new Paragraph({ spacing: { before: o.before || 0, after: o.after || 0 }, alignment: o.align, keepNext: o.keepNext, children: [run(text, o)] });
function cell(text, w, o = {}) {
  const lines = Array.isArray(text) ? text : [text];
  return new TableCell({ width: { size: w, type: WidthType.DXA }, borders, columnSpan: o.span, verticalAlign: VerticalAlign.CENTER,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 40, bottom: 40, left: 80, right: 80 }, children: lines.map((l) => para(l, o)) });
}
const heading = (text, size = 26, before = 0, pageBreak = false) => new Paragraph({ pageBreakBefore: pageBreak, spacing: { before, after: 80 }, keepNext: true, children: [run(text, { size, bold: true, color: NAVY })] });
const note = (text) => new Paragraph({ spacing: { before: 60, after: 60 }, children: [run(text, { size: 16, italics: true, color: "555555" })] });
const spacer = () => new Paragraph({ spacing: { after: 120 }, children: [] });
function simpleTable(widths, header, rows, o = {}) {
  const head = new TableRow({ tableHeader: true, cantSplit: true, children: header.map((h, i) => cell(h, widths[i], { fill: NAVY, color: "FFFFFF", bold: true, size: 18 })) });
  const body = rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => { const v = typeof c === "object" && c !== null ? c : { t: c };
    return cell(v.t, widths[i], { size: o.size || 18, fill: v.fill || (ri % 2 ? ZEBRA : undefined), color: v.color, bold: v.bold }); }) }));
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows: [head, ...body] });
}

// ---- helpers for time and FCC ----
const secs = (d) => { const m = /^(\d+):(\d+)$/.exec(d || ""); return m ? +m[1] * 60 + +m[2] : 0; };
const fmt = (s) => { const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60; return h ? `${h}:${String(m).padStart(2, "0")}:${String(x).padStart(2, "0")}` : `${m}:${String(x).padStart(2, "0")}`; };
function fcc(t) {
  const n = (t.fcc_note || "").toLowerCase();
  if (t.fcc_status === "FCC") return { t: "HOLD", color: RED, bold: true, fill: RED_BG };
  if (t.fcc_status === "UNVERIFIED") return { t: "LISTEN FIRST", color: AMBER, bold: true, fill: AMBER_BG };
  if (n.includes("check by ear") || n.includes("partial")) return { t: "CLEAN, check ear", color: AMBER, bold: true, fill: AMBER_BG };
  return { t: "CLEAN", color: GREEN, bold: true };
}
const notesText = (t) => { const parts = [t.notes || t.why || ""]; if (t.credits) parts.push("Prod: " + t.credits); if (t.related) parts.push("Related: " + t.related); return parts.filter(Boolean).join(" ").replace(/\s+/g, " ").trim(); };

// ---- collect airable tracks by set (CUT and SKIP never print) ----
const sets = plan.sets.map((s) => ({ name: s.set, tracks: s.tracks.filter((t) => t.priority !== "CUT" && t.priority !== "SKIP") })).filter((s) => s.tracks.length);
const all = sets.flatMap((s) => s.tracks);
const total = all.reduce((a, t) => a + secs(t.duration), 0);

// ---- which talk-break text belongs after which set (plan.mic_breaks keys differ by show) ----
const MB = plan.mic_breaks || {};
function breakKeysAfter(set, idx) {
  const keys = [], num = (/Set (\d+)/.exec(set.name) || [])[1];
  if (num) keys.push("after_set_" + num);
  keys.push("after_set_" + (idx + 1));
  if (/Triple Shot/i.test(set.name)) keys.push("after_triple_shot");
  if (idx === sets.length - 1) keys.push("closing");
  if (/Set 4/.test(set.name)) keys.push("end_hour_1");
  if (/Set 6/.test(set.name)) keys.push("bay_area_break");
  if (/Set 7/.test(set.name)) keys.push("after_goth");
  return keys.filter((k) => MB[k]);
}

// ---- the tracklist table (first thing in the file) ----
const W = [450, 1850, 2600, 2000, 1150, 1100, 900, 650, 3700];
const COLS = ["#", "Artist", "Track", "Album", "Orig. release", "FCC", "ZK tag", "Time", "Notes"];
function tracklist() {
  const head = new TableRow({ tableHeader: true, cantSplit: true, children: COLS.map((h, i) => cell(h, W[i], { fill: NAVY, color: "FFFFFF", bold: true, keepNext: true })) });
  const rows = [head]; let n = 0, cum = 0, hour2Seen = false;
  const band = (text, fill, o = {}) => new TableRow({ cantSplit: true, children: [cell(text, PAGE_W, { span: 9, fill, bold: true, size: o.size || 18, color: o.color || NAVY, keepNext: o.keepNext })] });
  const clip = (s, n) => { const x = Array.isArray(s) ? s[0] : String(s); return x.length > n ? x.slice(0, n).replace(/\s+\S*$/, "") + "..." : x; };
  if (MB.opening) rows.push(band("MIC BREAK: opening  |  " + clip(MB.opening, 150) + "  (full text at the back)", GREEN_BG, { color: "000000" }));
  sets.forEach((s, si) => {
    if (/^Hour 2/.test(s.name) && !hour2Seen) { hour2Seen = true; rows.push(band(`HOUR 2  |  on air from ${fmt(cum)}`, NAVY, { color: "FFFFFF", size: 22 })); }
    const secsSet = s.tracks.reduce((a, t) => a + secs(t.duration), 0);
    rows.push(band(`${s.name}  |  ${s.tracks.length} ${s.tracks.length === 1 ? "track" : "tracks"}  |  ${fmt(secsSet)}  |  through ${fmt(cum + secsSet)}`, BAND, { size: 20, keepNext: true }));
    s.tracks.forEach((t, ri) => {
      n++; const f = fcc(t); const fill = ri % 2 ? ZEBRA : undefined; const kn = ri < s.tracks.length - 1;
      rows.push(new TableRow({ cantSplit: true, children: [
        cell(String(n), W[0], { fill, bold: true, keepNext: kn }), cell(t.artist, W[1], { fill, bold: true, keepNext: kn }),
        cell(t.track, W[2], { fill, bold: true, size: 21, keepNext: kn }), cell(t.album || "-", W[3], { fill, keepNext: kn }),
        cell(String(t.released || "-"), W[4], { fill, keepNext: kn }), cell(f.t, W[5], { fill: f.fill || fill, color: f.color, bold: f.bold, keepNext: kn }),
        cell(t.tag || "-", W[6], { fill, keepNext: kn }), cell(t.duration || "-", W[7], { fill, keepNext: kn }),
        cell(notesText(t), W[8], { fill, size: 16, keepNext: kn }) ] }));
    });
    cum += secsSet;
    const ks = breakKeysAfter(s, si);
    if (ks.length) rows.push(band("MIC BREAK  |  " + clip(MB[ks[0]], 160) + "  (full text at the back)", GREEN_BG, { color: "000000" }));
  });
  return new Table({ width: { size: PAGE_W, type: WidthType.DXA }, columnWidths: W, rows });
}

// ---- body ----
const kids = [];
const label = plan.theme ? ` | ${plan.theme} show` : "";
kids.push(new Paragraph({ spacing: { after: 30 }, children: [run(`The Library with DJ Stace: ${STAGE} Show Script`, { size: 32, bold: true, color: NAVY })] }));
kids.push(para(`${nice(showDate)}  |  KZSU 90.1 FM  |  Tracklist first; general show info starts after the last track  |  ${all.length} tracks, ${fmt(total)}${label}`, { size: 16, color: "555555", after: 80 }));
kids.push(tracklist());
kids.push(note("FCC column: green CLEAN, amber means listen first or check by ear, red means hold out. ZK tag is the KZSU library tag; a dash means not in the library. Orig. release is the original release date or year."));

// ===== general info (after the tracklist) =====
kids.push(heading("Run of show", 26, 0, true));
let cum = 0, n = 1;
kids.push(simpleTable([7000, 1500, 1800, 2400, 1700], ["Set", "Tracks", "Set time", "Track numbers", "Running total"],
  sets.map((s) => { const ss = s.tracks.reduce((a, t) => a + secs(t.duration), 0); const first = n; n += s.tracks.length; cum += ss; return [s.name, String(s.tracks.length), fmt(ss), `${first}-${n - 1}`, fmt(cum)]; })
    .concat([[{ t: "Total", bold: true }, { t: String(all.length), bold: true }, { t: fmt(total), bold: true }, "", { t: "Target 2:30:00 for a full show", bold: true }]])));

if (plan.mic_breaks) {
  kids.push(heading("Talk breaks (full text)", 24, 200));
  const order = Object.keys(MB);
  kids.push(simpleTable([2800, 11600], ["Break", "Say"], order.map((k) => [{ t: k.replace(/_/g, " "), bold: true, fill: GREEN_BG }, { t: MB[k], fill: GREEN_BG }])));
}
if (plan.today_in_music) {
  kids.push(heading("Today in music", 24, 200));
  const rows = [];
  for (const k of Object.keys(plan.today_in_music)) { const v = plan.today_in_music[k]; if (Array.isArray(v)) v.forEach((x) => rows.push([k.replace(/_/g, " "), x])); }
  if (rows.length) kids.push(simpleTable([2000, 12400], ["Date", "Item"], rows));
}
if (plan.new_releases && plan.new_releases.length) {
  kids.push(heading("New and coming up", 24, 200));
  kids.push(simpleTable([14400], ["Release"], plan.new_releases.map((r) => [typeof r === "string" ? r : JSON.stringify(r)])));
}
// Bay Area shows: upcoming only (on or after the show date)
const showD = new Date(showDate + "T00:00:00Z");
const upcoming = (plan.bay_area_shows || []).filter((s) => { const m = /([A-Z][a-z]{2})\.? (\d{1,2})/.exec(s.date || ""); if (!m) return false; const mi = MONTHS.indexOf(m[1]); if (mi < 0) return false;
  const d = new Date(Date.UTC(showD.getUTCFullYear(), mi, +m[2])); return d >= showD; });
if (upcoming.length) {
  kids.push(heading("Bay Area shows (upcoming only; confirm before air)", 24, 200));
  kids.push(simpleTable([2000, 4800, 3600, 4000], ["Date", "Act", "Venue", "Status"], upcoming.map((s) => {
    // Newer plans store act and detail separately; older plans only have one "what" string.
    const act = s.act || s.what.split(". $")[0].split(" $")[0];
    const detail = s.detail || (s.what.includes("$") ? s.what.slice(s.what.indexOf("$")) : "");
    return [{ t: s.date, bold: true }, act, s.venue, detail + (s.note ? " " + s.note : "")]; })));
}
if (plan.ticket_giveaway) {
  kids.push(heading("Ticket giveaway", 24, 200));
  const g = plan.ticket_giveaway;
  kids.push(simpleTable([2800, 11600], ["Item", "Detail"], [["Proposed", g.proposed || "None"], ["Rule result", g.default_rule_result || ""], ["Flag", g.flag || "Confirm rules, call-in number and show time before air."]]));
}
// FCC watch list: everything not plain CLEAN, plus tracks held out of the plan
const watch = all.filter((t) => fcc(t).t !== "CLEAN");
const held = (plan.excluded_fcc || []);
if (watch.length || held.length) {
  kids.push(heading("FCC watch list", 24, 200));
  kids.push(simpleTable([4200, 2200, 8000], ["Artist and track", "Status", "Detail"],
    watch.map((t) => [`${t.artist}, ${t.track}`, fcc(t), t.fcc_note || ""]).concat(held.map((x) => [`${x.artist}, ${x.track}`, { t: "HELD OUT", color: RED, bold: true }, `${x.fcc}. ${x.action || ""}`]))));
}
if (plan.bench && plan.bench.length) {
  kids.push(heading("Bench: replacements if you cut tracks", 24, 200));
  kids.push(simpleTable([2600, 3600, 3200, 2400, 1200, 1400], ["Artist", "Track", "Album", "Label", "Released", "FCC"], plan.bench.map((t) => [t.artist, t.track, t.album || "-", (t.label || "-").replace(" (verify)", ""), String(t.released || "-"), fcc(t)])));
}
if (plan.cut && plan.cut.length) {
  kids.push(heading("Cut from the plan", 24, 200));
  kids.push(note(plan.cut.map((c) => `${c.artist}, ${c.track}`).join("; ")));
}

const doc = new Document({
  creator: "DJ Stace (Claude)", title: `Library Show Script ${showDate} (${STAGE})`,
  styles: { default: { document: { run: { font: FONT, size: 18 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE }, margin: { top: 600, bottom: 600, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [run(`The Library with DJ Stace  |  ${showDate} (${stage})  |  Page `, { size: 14, color: "777777" }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: "777777" })] })] }) },
    children: kids,
  }],
});
const out = path.join(outDir, `Library Show Script ${showDate} (${STAGE}).docx`);
fs.mkdirSync(outDir, { recursive: true });
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out, "|", all.length, "tracks |", fmt(total)); });
