# One-time edit of build_landscape_final_2026-10-22.js (Oct. 22, "track history" revision):
# new Released column, history column instead of playlist notes, yellow LIVE highlights for booked shows.
p = 'scripts/build_landscape_final_2026-10-22.js'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)

# 1. run(): allow a highlight color
rep('italics: o.italics }); }', 'italics: o.italics, highlight: o.hl }); }')

# 2. wider table: new Released column, Info column
rep('const W = [450, 1800, 2600, 2100, 1600, 900, 650, 1300, 3000];', 'const W = [420, 1500, 2150, 1650, 1500, 1250, 720, 560, 1000, 3650];')
rep('const COLS = ["#", "Artist", "Track", "Album", "Label", "Tag", "Time", "FCC", "Notes"];', 'const COLS = ["#", "Artist", "Track", "Album", "Released", "Label", "Tag", "Time", "FCC", "Track history"];')
s = s.replace('span: 9', 'span: 10')

# 3. rich cell helper (several lines, each with its own style)
rep('function heading(', '''function rich(lines, w, o = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA }, borders, verticalAlign: VerticalAlign.CENTER,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: lines.map((l) => new Paragraph({ spacing: { before: l.before || 0, after: l.after || 0 }, keepNext: o.keepNext,
      children: [run(l.t, { size: l.size || 16, bold: l.bold, color: l.color, italics: l.italics, hl: l.hl })] })),
  });
}
function heading(''')

# 4. rows of the set table
i = s.index('    const extra = held')
j = s.index('  return { table: new Table({ width: { size: PAGE_W')
new_rows = '''    const rel = t.rel_main ? [{ t: t.rel_main, size: 22, bold: true, color: NAVY }, { t: t.rel_sub || "", size: 14, color: "555555", before: 20 }] : [{ t: String(t.released || "-"), size: 18, bold: true }];
    const live = (t.shows || []).map((x) => ({ t: "LIVE: " + x, size: 15, bold: true, color: "5A3E00", hl: "yellow", before: 30 }));
    const hist = [{ t: (held ? "HELD OUT of the Zookeeper CSV. " : "") + (t.info || t.why || ""), size: 16 }].concat(live);
    const artistLines = [{ t: t.artist, size: 18, bold: true }].concat((t.shows || []).length ? [{ t: "LIVE SOON", size: 13, bold: true, color: "5A3E00", hl: "yellow", before: 20 }] : []);
    return new TableRow({ cantSplit: true, children: [
      cell(num, W[0], { fill, bold: true, keepNext: kn }), rich(artistLines, W[1], { fill, keepNext: kn }),
      cell(t.track, W[2], { fill, bold: true, size: 20, keepNext: kn }), cell(t.album || "-", W[3], { fill, keepNext: kn }),
      rich(rel, W[4], { fill, keepNext: kn }),
      cell(t.label || "-", W[5], { fill, keepNext: kn }), cell(t.tag || "-", W[6], { fill, keepNext: kn }),
      cell(held ? "--" : t.duration, W[7], { fill, keepNext: kn }),
      cell(f.t, W[8], { fill: f.fill || fill, color: f.color, bold: f.bold, keepNext: kn, size: 16 }),
      rich(hist, W[9], { fill, keepNext: kn }) ] });
  });
'''
s = s[:i] + new_rows + s[j:]

# 5. Royal Blood album date
rep('"Dead Company (single Ten Over Ten out Aug. 12; album date: sources say Nov. 6, 12 or 13)", "Warner", { t: "Fri. Nov. 13 (verify)", bold: true }', '"Dead Company (single Ten Over Ten out Aug. 12, 2026)", "Warner", { t: "Fri. Nov. 6, 2026", bold: true }')

# 6. Booked-shows table replaces the old Set 6 table
a = s.index('    kids.push(heading("Talk break after Set 6: Bay Area shows')
b = s.index('    kids.push(micBreak("MIC BREAK: BAY AREA"')
booked = '''    kids.push(heading("Booked Bay Area shows for artists in tonight's set (foopee.com, read Oct. 22; confirm bills and doors before air)", 22));
    const SH = [];
    for (const st of plan.sets) for (const t of st.tracks) if ((t.shows || []).length) { let e = SH.find((x) => x.artist === t.artist); if (!e) { e = { artist: t.artist, shows: t.shows, tracks: [] }; SH.push(e); } e.tracks.push(N(t.artist, t.track.slice(0, 6)) + " " + t.track); }
    const MON = { Oct: 10, Nov: 11, Dec: 12 };
    const rows = []; for (const e of SH) for (const sh of e.shows) { const m = /^(\\w+)\\. (\\w+)\\. (\\d+), (.*)$/.exec(sh); rows.push({ key: MON[m[2]] * 100 + +m[3], day: `${m[1]}. ${m[2]}. ${m[3]}`, artist: e.artist, rest: m[4], tracks: e.tracks.join("; ") }); }
    rows.sort((x, y) => x.key - y.key);
    kids.push(simpleTable([1700, 2600, 6000, 4100], ["Date", "Artist", "Venue, bill, price", "Track tonight"],
      rows.map((r) => [{ t: r.day, bold: true, fill: "FFF2A8" }, { t: r.artist, bold: true, fill: "FFF2A8" }, { t: r.rest, fill: r.rest.includes("sold out") ? RED_BG : "FFF2A8" }, { t: r.tracks, fill: "FFF2A8" }]).concat([["Wed. Oct. 28", "Slow Pulp (ticket sheet; DJ Cleo)", "Fillmore, S.F.", "Not in set"]]), { keepTogether: true }));
    kids.push(note("Dates run through Jan. 2027 on foopee. Shows before tonight (Dinosaur Jr., Hovvdy, Heavens to Betsy at Bottom of the Hill, Stef Chura) are not listed. Yellow rows are booked shows; red means sold out."));
    kids.push(spacer());
'''
s = s[:a] + booked + s[b:]

# 7. Change table: add this revision at the top
rep('kids.push(heading("What changed: Thu. Oct. 22 update (your Air Order edits)", 24, 160));\nkids.push(simpleTable([2600, 11800], ["Change", "Detail"], [',
    'kids.push(heading("What changed: Thu. Oct. 22 update (your Air Order edits)", 24, 160));\nkids.push(simpleTable([2600, 11800], ["Change", "Detail"], [\n  [{ t: "Script format (latest)", bold: true }, "Playlist-management notes are gone from the right column. It is now Track history: release, credits, covers, chart and label facts. Release dates sit in their own bold column with the year; the small line gives single, album or EP and the parent album date. Booked Bay Area shows are marked LIVE in yellow on each row and listed by date after Set 6. Dates marked (verify) rest on one source."],')
open(p, 'w', encoding='utf-8').write(s)
print('patched')
