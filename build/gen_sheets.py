"""Render the rate cards and parts price list from catalog.json.

    .venv/Scripts/python.exe build/gen_sheets.py
"""

from __future__ import annotations

import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from adjudicate import CATALOG, ENTITIES

OUT = Path(__file__).resolve().parent.parent / "out" / "sharepoint" / "03-RateCards"
FAMILY_NAME = {f["code"]: f["name"] for f in ENTITIES["families"]}

HEAD_FILL = PatternFill("solid", fgColor="1F4E79")
HEAD_FONT = Font(color="FFFFFF", bold=True, size=11)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def style_sheet(ws, widths: list[int], title: str, subtitle: str) -> None:
    ws.insert_rows(1, 2)
    ws["A1"] = title
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = subtitle
    ws["A2"].font = Font(italic=True, size=9, color="606060")
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for cell in ws[3]:
        if cell.value is not None:
            cell.fill = HEAD_FILL
            cell.font = HEAD_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=3):
        for cell in row:
            if cell.value is not None:
                cell.border = BORDER
    ws.freeze_panes = "A4"


def flat_rate_labour() -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Flat Rate Labour"
    ws.append(["Operation code", "Description", "Product family", "Component",
               "Flat-rate hours"])
    for op in CATALOG["operations"]:
        ws.append([op["op_code"], op["description"],
                   FAMILY_NAME.get(op["family"], op["family"]),
                   op["component"].replace("_", " "), op["flat_hours"]])
    style_sheet(ws, [18, 42, 32, 16, 16],
                "Flat Rate Labour Schedule — FY26",
                "Contoso Industrial · Warranty Operations · effective 1 April 2026 · "
                "hours payable per operation, per policy clause 4.1")

    notes = wb.create_sheet("Notes")
    for r, line in enumerate([
        "Flat Rate Labour Schedule — FY26",
        "",
        "Labour is payable at the flat-rate allowance for the operation code, or at the",
        "hours actually claimed, whichever is the lesser (Global Warranty Policy, 4.1).",
        "",
        "Hours above the flat-rate allowance are not payable and are reported to the",
        "partner as a variance on the adjudication.",
        "",
        "The rate applied to these hours is the regional labour rate in force on the",
        "date of repair. See Labour-Rates-By-Region-FY26.xlsx.",
    ], start=1):
        notes.cell(row=r, column=1, value=line)
    notes.column_dimensions["A"].width = 80
    notes["A1"].font = Font(bold=True, size=12)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "Flat-Rate-Labour-FY26.xlsx"
    wb.save(path)
    return path


def labour_rates() -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Labour Rates"
    ws.append(["Region", "Currency", "Rate per hour", "Effective from", "Effective to"])
    for row in CATALOG["labour_rates"]:
        ws.append([row["region"], row["currency"], row["rate"],
                   row["effective_from"], row["effective_to"]])
    style_sheet(ws, [14, 12, 16, 16, 16],
                "Regional Labour Rates — FY25 and FY26",
                "Contoso Industrial · Warranty Operations · the rate applied is the one in "
                "force on the DATE OF REPAIR, per policy clause 4.1")

    notes = wb.create_sheet("Notes")
    for r, line in enumerate([
        "Regional Labour Rates",
        "",
        "IMPORTANT: the rate applied to a claim is the rate in force on the date of",
        "repair — not the date of submission, and not the current date.",
        "",
        "The FY26 rates take effect on 1 April 2026. A repair carried out on or before",
        "31 March 2026 is reimbursed at the FY25 rate even if the claim is submitted",
        "later.",
        "",
        "Rates are quoted in the settlement currency of the partner's territory.",
    ], start=1):
        notes.cell(row=r, column=1, value=line)
    notes.column_dimensions["A"].width = 80
    notes["A1"].font = Font(bold=True, size=12)

    path = OUT / "Labour-Rates-By-Region-FY26.xlsx"
    wb.save(path)
    return path


def parts_price_list() -> Path:
    """Load-bearing parts, padded with family-consistent noise so a lookup is real work."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Parts Price List"
    ws.append(["Part number", "Description", "Product family", "Supersedes",
               "Superseded by", "Price INR", "Price EUR", "Price SGD"])

    rows = []
    for p in CATALOG["parts"]:
        rows.append([p["part_no"], p["description"],
                     FAMILY_NAME.get(p["family"], p["family"]),
                     p.get("supersedes") or "", p.get("superseded_by") or "",
                     p["price"]["INR"], p["price"]["EUR"], p["price"]["SGD"]])

    rng = random.Random(4000)
    noise = [
        ("Pressure switch", "4000-CH"), ("Expansion valve", "4000-CH"),
        ("Sight glass assembly", "4000-CH"), ("Suction strainer", "4000-CH"),
        ("Oil separator element", "4000-CH"), ("Contactor, 40 A", "4000-CH"),
        ("Temperature sensor, PT100", "4000-CH"), ("Display panel", "4000-CH"),
        ("Isolation valve", "4000-CH"), ("Anti-vibration mount set", "4000-CH"),
        ("Intercooler core", "2200-AC"), ("Unloader valve", "2200-AC"),
        ("Air intake filter", "2200-AC"), ("Belt set", "2200-AC"),
        ("Crankcase heater", "2200-AC"), ("Pressure relief valve", "2200-AC"),
        ("Moisture separator", "2200-AC"), ("Control relay", "2200-AC"),
        ("Cooling fan blade", "2200-AC"), ("Gasket set", "2200-AC"),
    ]
    used = {p["part_no"] for p in CATALOG["parts"]}
    for i, (desc, fam) in enumerate(noise):
        for j in range(2):
            base = 44000 if fam == "4000-CH" else 22000
            num = f"P-{base + 700 + i * 7 + j}"
            if num in used:
                continue
            used.add(num)
            inr = rng.randrange(3, 160) * 1000 + rng.randrange(0, 20) * 50
            rows.append([num, desc, FAMILY_NAME[fam], "", "",
                         inr, round(inr / 90.5, 0), round(inr / 62.5, 0)])

    rows.sort(key=lambda r: r[0])
    for r in rows:
        ws.append(r)

    style_sheet(ws, [16, 34, 32, 16, 16, 14, 12, 12],
                "Parts Price List — FY26",
                "Contoso Industrial · list prices by territory · price the part ACTUALLY "
                "FITTED; where superseded, the superseding part's price applies (policy 4.2)")
    for row in ws.iter_rows(min_row=4, min_col=6, max_col=8):
        for cell in row:
            cell.number_format = "#,##0"

    path = OUT / "Parts-Price-List-FY26.xlsx"
    wb.save(path)
    return len(rows), path


if __name__ == "__main__":
    a = flat_rate_labour()
    b = labour_rates()
    n, c = parts_price_list()
    print(f"  {a.name:36} {len(CATALOG['operations'])} operations")
    print(f"  {b.name:36} {len(CATALOG['labour_rates'])} rate rows")
    print(f"  {c.name:36} {n} parts")
    print(f"\n3 workbooks written to {OUT}")
