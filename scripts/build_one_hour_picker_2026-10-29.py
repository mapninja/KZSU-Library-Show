"""Builds the one-hour picker workbook for the Oct. 29, 2026 Halloween show.
Reads the plan, keeps the 35 tracks Stace has not cut, and writes an Excel sheet where
typing x in the Play column adds that track's runtime to a running total."""
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule

plan = json.load(open('/sessions/blissful-nifty-cori/mnt/KZSU-Library-Show/data/recon/2026-10-29/working_playlist.json'))
tracks = []
for s in plan['sets']:
    for t in s['tracks']:
        if t.get('priority') in ('CUT', 'SKIP'):
            continue
        tracks.append((s['set'], t))

def secs(d):
    m, x = d.split(':'); return int(m) * 60 + int(x)

F = 'Arial'
navy = PatternFill('solid', fgColor='1F3864'); band = PatternFill('solid', fgColor='D9E2F3')
inp = PatternFill('solid', fgColor='FFF2CC'); thin = Side(style='thin', color='B7B7B7')
box = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook(); ws = wb.active; ws.title = 'One-Hour Picker'
ws['A1'] = 'The Library with DJ Stace: one-hour picker, Thu. Oct. 29, 2026 (Halloween)'
ws['A1'].font = Font(name=F, size=14, bold=True, color='1F3864')
ws['A2'] = 'Type x in the yellow Play column to pick a track. Selected total, remaining time and the running total update on their own.'
ws['A2'].font = Font(name=F, size=10, italic=True)

# ---- summary block (rows 3-7). Yellow cells are inputs; everything else is a formula. ----
FIRST, LAST = 11, 11 + len(tracks) - 1
labels = [
 ('Show length (min)', 60, 'input'),
 ('Talk, IDs and PSAs (min)', 10, 'input'),
 ('Music target', '=TIME(0,D3-D4,0)', 'f'),
 ('Selected music', f'=SUM(J{FIRST}:J{LAST})', 'f'),
 ('Time left', f'=0', 'f'),
 ('Tracks picked', f'=COUNTIF(A{FIRST}:A{LAST},"?*")', 'f'),
]
for i, (lab, val, kind) in enumerate(labels):
    r = 3 + i
    ws.cell(r, 3, lab).font = Font(name=F, size=10, bold=True)
    c = ws.cell(r, 4, val); c.font = Font(name=F, size=10, bold=True, color='0000FF' if kind == 'input' else '000000')
    c.border = box; c.alignment = Alignment(horizontal='center')
    if kind == 'input': c.fill = inp
ws['D5'].number_format = '[m]:ss'; ws['D6'].number_format = '[m]:ss'; ws['D7'].number_format = '[m]:ss'
ws['D7'].value = '=MAX(D5-D6,0)'   # time left floors at 0:00 (Excel cannot show negative time); E7 reports an overage
ws['E7'] = '=IF(D6>D5,"OVER by "&TEXT(D6-D5,"[m]:ss"),"under target")'
ws['E7'].font = Font(name=F, size=10, bold=True)

ws['G3'] = 'How to use'; ws['G3'].font = Font(name=F, size=10, bold=True)
notes = [
 'Yellow cells are inputs: Show length, Talk allowance and the Play column.',
 'Runtime comes from the YouTube Music durations in the plan. Selected runtime is blank until you mark a track.',
 'Running total adds up only the tracks you picked, in air order, so you can see where the hour lands.',
 'Set rows are shaded by set. FCC: CLEAN unless it says LISTEN FIRST (Coil).',
]
for i, n in enumerate(notes):
    ws.cell(4 + i, 7, n).font = Font(name=F, size=9)

# ---- table ----
heads = ['Play (x)', '#', 'Set', 'Artist', 'Track', 'Album', 'Label', 'Runtime', 'Seconds', 'Selected runtime', 'Running total (picked)', 'FCC', 'Notes']
HR = 10
for j, h in enumerate(heads, 1):
    c = ws.cell(HR, j, h); c.font = Font(name=F, size=10, bold=True, color='FFFFFF'); c.fill = navy
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); c.border = box
ws.row_dimensions[HR].height = 30

def fcc(t):
    st = t.get('fcc_status', '')
    return 'LISTEN FIRST' if st == 'UNVERIFIED' else 'CLEAN'

for i, (setname, t) in enumerate(tracks):
    r = FIRST + i
    short = setname.split(': ', 1)[-1] if ': ' in setname else setname
    vals = [None, i + 1, setname, t['artist'], t['track'], t.get('album', ''), t.get('label', '').replace(' (verify)', ''),
            f'=I{r}/86400', secs(t['duration']), f'=IF(A{r}<>"",H{r},0)', f'=SUM(J${FIRST}:J{r})', fcc(t), (t.get('why') or '')[:140]]
    for j, v in enumerate(vals, 1):
        c = ws.cell(r, j, v); c.font = Font(name=F, size=10, bold=(j == 5)); c.border = box
        c.alignment = Alignment(vertical='center', wrap_text=(j in (3, 6, 7, 13)))
    ws.cell(r, 1).fill = inp; ws.cell(r, 1).alignment = Alignment(horizontal='center', vertical='center')
    ws.cell(r, 2).alignment = Alignment(horizontal='center', vertical='center')
    for col in (8, 10, 11): ws.cell(r, col).number_format = '[m]:ss'; ws.cell(r, col).alignment = Alignment(horizontal='center', vertical='center')
    ws.cell(r, 8).number_format = 'm:ss'
    ws.cell(r, 9).font = Font(name=F, size=10, color='0000FF')       # hardcoded seconds from the plan
    if fcc(t) != 'CLEAN': ws.cell(r, 12).font = Font(name=F, size=10, bold=True, color='8A6100')

# totals row
TR = LAST + 1
ws.cell(TR, 5, 'All 35 tracks').font = Font(name=F, size=10, bold=True)
ws.cell(TR, 8, f'=SUM(H{FIRST}:H{LAST})').number_format = '[m]:ss'
ws.cell(TR, 10, f'=SUM(J{FIRST}:J{LAST})').number_format = '[m]:ss'
for col in (8, 10): ws.cell(TR, col).font = Font(name=F, size=10, bold=True); ws.cell(TR, col).alignment = Alignment(horizontal='center')

# dropdown: x or blank
dv = DataValidation(type='list', formula1='"x"', allow_blank=True, showErrorMessage=False)
ws.add_data_validation(dv); dv.add(f'A{FIRST}:A{LAST}')
# picked rows turn green; running total turns red once past the music target
green = PatternFill('solid', bgColor='E2F0D9'); red = PatternFill('solid', bgColor='F8D7DA')
ws.conditional_formatting.add(f'B{FIRST}:M{LAST}', FormulaRule(formula=[f'$A{FIRST}<>""'], fill=green))
ws.conditional_formatting.add(f'K{FIRST}:K{LAST}', FormulaRule(formula=[f'AND($A{FIRST}<>"",K{FIRST}>$D$5)'], fill=red))
ws.conditional_formatting.add('E7', FormulaRule(formula=['$D$6>$D$5'], font=Font(name=F, bold=True, color='B00020')))

for col, w in zip('ABCDEFGHIJKLM', [9, 5, 34, 24, 34, 28, 22, 10, 9, 12, 14, 14, 60]): ws.column_dimensions[col].width = w
ws.freeze_panes = f'F{FIRST}'
ws.auto_filter.ref = f'A{HR}:M{LAST}'
ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.cell(TR + 2, 1, 'Source: data/recon/2026-10-29/working_playlist.json (35 tracks after your Working cull); durations are YouTube Music runtimes. Seconds column is the only hardcoded data (blue).').font = Font(name=F, size=9, italic=True)
out = '/sessions/blissful-nifty-cori/mnt/outputs/Library Show One-Hour Picker 2026-10-29.xlsx'
wb.save(out); print('saved', len(tracks))
