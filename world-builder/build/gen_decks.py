"""Render the quarterly warranty review decks.

The Q2 deck is DELIBERATELY STALE. It summarises coverage as "24 months
standard", which was true of the global policy when it was written and is wrong
for any asset a bulletin now covers, and wrong for India in the other direction.
It is the most confidently-worded source in the corpus and the least reliable —
which is exactly how review decks behave in a real company.

    .venv/Scripts/python.exe world-builder/build/gen_decks.py
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent.parent / "out" / "sharepoint" / "05-Reviews"

NAVY = RGBColor(0x1F, 0x4E, 0x79)
GREY = RGBColor(0x60, 0x60, 0x60)


def title_slide(prs: Presentation, title: str, subtitle: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = title
    slide.placeholders[1].text = subtitle
    slide.shapes.title.text_frame.paragraphs[0].runs[0].font.color.rgb = NAVY


def bullet_slide(prs: Presentation, title: str, bullets: list[tuple[str, int]]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = title
    slide.shapes.title.text_frame.paragraphs[0].runs[0].font.color.rgb = NAVY
    tf = slide.placeholders[1].text_frame
    tf.clear()
    for i, (text, level) in enumerate(bullets):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.text = text
        para.level = level
        para.font.size = Pt(18 if level == 0 else 15)
    return slide


def table_slide(prs: Presentation, title: str, headers: list[str],
                rows: list[list[str]]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title
    slide.shapes.title.text_frame.paragraphs[0].runs[0].font.color.rgb = NAVY
    shape = slide.shapes.add_table(len(rows) + 1, len(headers),
                                   Inches(0.6), Inches(1.7),
                                   Inches(9.0), Inches(0.4 * (len(rows) + 1)))
    table = shape.table
    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = h
        cell.text_frame.paragraphs[0].runs[0].font.size = Pt(12)
        cell.text_frame.paragraphs[0].runs[0].font.bold = True
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = str(val)
            cell.text_frame.paragraphs[0].runs[0].font.size = Pt(11)


def chart_slide(prs: Presentation, title: str, categories: list[str],
                series: dict[str, list[float]]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title
    slide.shapes.title.text_frame.paragraphs[0].runs[0].font.color.rgb = NAVY
    data = CategoryChartData()
    data.categories = categories
    for name, values in series.items():
        data.add_series(name, values)
    frame = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                                   Inches(0.7), Inches(1.6),
                                   Inches(8.8), Inches(4.8), data)
    chart = frame.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False


def note(slide, text: str) -> None:
    slide.notes_slide.notes_text_frame.text = text


# ---------------------------------------------------------------------------

def q2_deck() -> Path:
    """FY26 Q2 — the stale one."""
    prs = Presentation()
    title_slide(prs, "Warranty Review — FY26 Q2",
                "Contoso Industrial · Warranty Operations · published 14 October 2025")

    bullet_slide(prs, "Headlines", [
        ("Warranty cost at 2.8% of revenue, down 0.3 points on FY25 Q4", 0),
        ("Claim volume up 11% year on year, driven by the 4000-series installed base", 0),
        ("Average settlement time 8.4 working days against a 10-day target", 0),
        ("India remains the largest region by claim volume", 0),
    ])

    # THE TRAP. Accurate against the global policy when written; wrong for any
    # asset a bulletin covers, and wrong for India, which runs 18 months.
    s = bullet_slide(prs, "Coverage at a glance", [
        ("Standard coverage: 24 months from commissioning, or 6,000 running hours", 0),
        ("Applies across all product families and all regions", 1),
        ("Labour reimbursed at flat-rate allowance", 0),
        ("Parts reimbursed at territory list price", 0),
        ("Goodwill available at manager discretion for near-miss cases", 0),
    ])
    note(s, "TRAP 6. This slide is the stale summary. 'Applies across all product "
            "families and all regions' was never true of India (18 months under "
            "ADD-IN-2.1) and is wrong for any asset covered by TSB-C-0051 or "
            "TSB-P-0112. 'Goodwill at manager discretion' contradicts policy 7.1, "
            "which requires recorded authority at tier. A model that trusts this "
            "deck over the policy fails the Evidence grounding rubric.")

    chart_slide(prs, "Warranty cost by product family (INR lakh)",
                ["FY25 Q3", "FY25 Q4", "FY26 Q1", "FY26 Q2"],
                {"4000-series chiller": [182, 174, 196, 211],
                 "2200-series compressor": [96, 101, 94, 88]})

    table_slide(prs, "Top failure modes — 4000-series",
                ["Component", "Claims", "Share", "Trend"],
                [["Hydraulic circuit", "214", "38%", "Rising"],
                 ["Compressor", "147", "26%", "Stable"],
                 ["Control system", "88", "16%", "Falling"],
                 ["Structural / cooling", "61", "11%", "Stable"],
                 ["Other", "52", "9%", "Stable"]])

    bullet_slide(prs, "Actions", [
        ("Engineering to review hydraulic circuit failure rate on the 4000-series", 0),
        ("Bulletin under consideration for affected serial ranges", 1),
        ("Partner documentation quality to be raised at the Q3 partner forum", 0),
        ("Rate card review ahead of FY26 close", 0),
    ])
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "FY26-Q2-Warranty-Review.pptx"
    prs.save(path)
    return path


def q3_deck() -> Path:
    """FY26 Q3 — current, and it is the one that mentions the bulletins."""
    prs = Presentation()
    title_slide(prs, "Warranty Review — FY26 Q3",
                "Contoso Industrial · Warranty Operations · published 16 April 2026")

    bullet_slide(prs, "Headlines", [
        ("Warranty cost at 3.4% of revenue, up 0.6 points — driven by bulletin activity", 0),
        ("TSB-C-0051 extended 4000-series hydraulic and compressor coverage in January", 0),
        ("TSB-P-0112 superseded TSB-P-0107 in February, narrowing the covered range", 0),
        ("FY26 labour rates took effect 1 April 2026", 0),
    ])

    table_slide(prs, "Coverage position by instrument",
                ["Instrument", "Applies to", "Period", "Notes"],
                [["POL-WAR-4.2", "All, unless varied", "24 mo / 6,000 h", "Global baseline"],
                 ["ADD-IN-2.1", "India installations", "18 mo / 5,000 h", "Shorter than global"],
                 ["ADD-EM-1.3", "EMEA installations", "24 mo / 6,000 h", "No variation"],
                 ["TSB-C-0051", "4000-CH 01200-01850", "36 mo / 8,000 h", "Hydraulic + compressor"],
                 ["TSB-P-0112", "2200-AC 00400-00750", "30 mo / 7,000 h", "Supersedes 0107"],
                 ["TSB-C-0043", "4000-CH all serials", "No change", "Reverses 5.2 exclusion"]])

    bullet_slide(prs, "Precedence — a reminder for adjudicators", [
        ("A bulletin naming the serial range takes precedence over the regional addendum", 0),
        ("The regional addendum takes precedence over the global policy", 0),
        ("A superseded bulletin has no effect, whether or not it is still published", 0),
        ("Where the claim system index and a bulletin disagree, the bulletin governs", 0),
        ("Policy clause 1.4", 1),
    ])

    chart_slide(prs, "Claims by funding code",
                ["FY26 Q1", "FY26 Q2", "FY26 Q3"],
                {"Standard": [412, 388, 301],
                 "Bulletin": [0, 12, 168],
                 "Repair warranty": [31, 28, 34],
                 "Goodwill": [22, 19, 16]})

    bullet_slide(prs, "Watch items", [
        ("Applicability index in the claim system is lagging bulletin publication", 0),
        ("Adjudicate from the bulletin document, not the index", 1),
        ("Goodwill approvals given in channels are not being recorded against claims", 0),
        ("Authority must be recorded in the claim system — policy 7.1", 1),
        ("Commissioning records missing for a small number of assets", 0),
    ])

    path = OUT / "FY26-Q3-Warranty-Review.pptx"
    prs.save(path)
    return path


if __name__ == "__main__":
    a, b = q2_deck(), q3_deck()
    for p in (a, b):
        print(f"  {p.name:36} {len(Presentation(p).slides)} slides")
    print(f"\n2 decks written to {OUT}")
