"""Create a clean planner workbook for Hindi Explainer Studio.

Run: python tools/build_planner.py
The app reads the Schedule sheet header row at row 3.
"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "planner.xlsx"
OUT.parent.mkdir(parents=True, exist_ok=True)

NAVY = "244F73"
PAPER = "F5F3ED"
GOLD = "D7AD55"
INK = "17212B"
WHITE = "FFFFFF"

wb = Workbook()
ws = wb.active
ws.title = "Schedule"
ws.sheet_view.showGridLines = False
ws.merge_cells("A1:H1")
ws["A1"] = "Hindi Explainer Studio — Production Planner"
ws["A1"].font = Font(name="Arial", size=18, bold=True, color=WHITE)
ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
ws.merge_cells("A2:H2")
ws["A2"] = "Plan research, writing, production, review and publishing. Use the studio dashboard as the live production view."
ws["A2"].font = Font(italic=True, color=INK)
headers = ["Post date (IST)", "Slot", "Post time (IST)", "Format", "Video type", "Working title", "Status", "Notes"]
for col, label in enumerate(headers, 1):
    c = ws.cell(3, col, label)
    c.font = Font(bold=True, color=WHITE)
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(wrap_text=True, vertical="center")
widths = [16, 10, 16, 12, 18, 48, 16, 48]
for i, width in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = width
for row in range(4, 204):
    for col in range(1, 9):
        cell = ws.cell(row, col)
        cell.fill = PatternFill("solid", fgColor=WHITE if row % 2 == 0 else PAPER)
        cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.cell(row, 1).number_format = "dd mmm yyyy"
    ws.cell(row, 3).number_format = "hh:mm"
for rng, values in [
    ("B4:B203", '"A,B,Long"'),
    ("D4:D203", '"Short,Long"'),
    ("E4:E203", '"Scenario,Myth test,Why,True story,Versus,Ranking,Timeline,Paradox,Puzzle,How it works,Superlative,How many,Map/scale,Explainer"'),
    ("G4:G203", '"Idea,Researching,Scripted,Approved,Rendered,Ready,Scheduled,Posted,Skipped"')
]:
    dv = DataValidation(type="list", formula1=values, allow_blank=True)
    ws.add_data_validation(dv); dv.add(rng)
ws.freeze_panes = "A4"
ws.auto_filter.ref = "A3:H203"

ideas = wb.create_sheet("Ideas")
ideas.append(["Working title", "Format", "Type", "Core question", "Research status", "Priority", "Notes"])
for c in ideas[1]:
    c.font = Font(bold=True, color=WHITE); c.fill = PatternFill("solid", fgColor=NAVY)
for i,w in enumerate([48,12,18,54,20,12,48],1): ideas.column_dimensions[get_column_letter(i)].width=w
ideas.freeze_panes="A2"

types = wb.create_sheet("Types")
types.append(["Format", "Editorial structure", "Visual opportunities", "Evidence requirement"])
for c in types[1]:
    c.font = Font(bold=True, color=WHITE); c.fill = PatternFill("solid", fgColor=NAVY)
type_rows = [
    ("Scenario", "Counterfactual premise → constraints → plausible consequences", "System simulation, causal chain, timeline", "State assumptions and distinguish inference from fact"),
    ("Myth test", "Claim → strongest evidence → what it gets right/wrong", "Side-by-side comparisons, labels", "Trace the original claim and disconfirming evidence"),
    ("Why", "Question → common explanation → mechanism → implications", "Causal diagrams, cutaways, timelines", "Primary evidence for key mechanisms"),
    ("True story", "Context → trigger → turning points → consequence", "Maps, archival material, timelines", "Primary records and scholarly corroboration"),
    ("Versus", "Comparable criteria → evidence by criterion → qualified verdict", "Split-screen charts and diagrams", "Comparable measures and clear caveats"),
    ("Ranking", "Define metric → explain entries → limitations", "Ranked visual scale and data cards", "Transparent dataset and ranking method"),
    ("Timeline", "Starting state → sequence → turning points → current state", "Animated timeline and maps", "Dated records and corroboration"),
    ("Paradox", "Apparent contradiction → hidden condition → resolution", "System diagrams, comparison, animation", "Verify the apparent contradiction and its limits"),
    ("Puzzle", "Question → evidence → pause → reasoned answer", "Visual clues, diagrams and reveal", "A fair solution grounded in evidence"),
    ("How it works", "Problem → components → process → failure modes", "Exploded diagrams and process animation", "Technical documentation or peer-reviewed sources"),
    ("Superlative", "Define measure → compare candidates → qualify claim", "Scale, ranked comparison, map", "A defensible definition and complete enough data"),
    ("How many", "Define quantity → calculate → show assumptions", "Counters, scale model, animated chart", "Reproducible calculation and units"),
    ("Map/scale", "Orient viewer → reveal geography or proportion → implication", "Sourced map, common scale, motion graphic", "Correct boundary/source data and transparent scale"),
    ("Explainer", "Define system → connect components → show outcome", "System diagram, flow and documentary visuals", "Reliable source coverage for every key link"),
]
for row in type_rows: types.append(row)
for i,w in enumerate([18,54,48,52],1): types.column_dimensions[get_column_letter(i)].width=w
types.freeze_panes="A2"

analytics = wb.create_sheet("Analytics")
analytics.append(["Title", "Posted (IST)", "Slot", "Video type", "Views", "Engaged %", "Avg % viewed", "Avg view duration (s)", "Likes", "Comments", "Shares", "Subscribers", "Retention notes"])
for c in analytics[1]:
    c.font = Font(bold=True, color=WHITE); c.fill = PatternFill("solid", fgColor=NAVY)
for i,w in enumerate([48,16,10,18,14,14,14,20,12,12,12,14,48],1): analytics.column_dimensions[get_column_letter(i)].width=w
analytics.freeze_panes="A2"

wb.save(OUT)
print(f"Created {OUT}")
