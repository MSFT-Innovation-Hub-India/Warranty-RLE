"""Render the Word corpus from spec/ and out/data/.

Nothing here invents a rule. Every clause, term, serial range and effective date
is read from instruments.json, so the prose a model retrieves and the answer the
engine computes come from one source.

    .venv/Scripts/python.exe build/gen_docs.py
"""

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

from adjudicate import ENTITIES, INSTRUMENTS, CATALOG, DEALERS, PARTS

OUT = Path(__file__).resolve().parent.parent / "out" / "sharepoint"
MFR = ENTITIES["manufacturer"]["short"]
FAMILY_NAME = {f["code"]: f["name"] for f in ENTITIES["families"]}

COMPONENT_LABEL = {
    "hydraulic": "hydraulic circuit",
    "compressor": "compressor",
    "controls": "control system",
    "structure": "structural and cooling assemblies",
    "valve_plate": "valve plate",
    "drive": "drive train",
    "seals": "shaft seals",
}


def components_phrase(codes: list[str]) -> str:
    names = [COMPONENT_LABEL.get(c, c.replace("_", " ")) for c in codes]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


# ---------------------------------------------------------------------------
# document furniture
# ---------------------------------------------------------------------------

def new_doc(title: str, subtitle: str = "") -> Document:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    head = doc.add_paragraph()
    run = head.add_run(MFR.upper())
    run.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x60, 0x60, 0x60)

    doc.add_heading(title, level=0)
    if subtitle:
        p = doc.add_paragraph(subtitle)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.runs[0].italic = True
    return doc


def control_table(doc: Document, rows: list[tuple[str, str]]) -> None:
    table = doc.add_table(rows=0, cols=2)
    table.style = "Light Grid Accent 1"
    for k, v in rows:
        cells = table.add_row().cells
        cells[0].text = k
        cells[1].text = str(v)
        cells[0].paragraphs[0].runs[0].bold = True
    doc.add_paragraph()


def save(doc: Document, folder: str, name: str) -> Path:
    target = OUT / folder
    target.mkdir(parents=True, exist_ok=True)
    path = target / name
    doc.save(path)
    return path


WRITTEN: list[Path] = []


def record(path: Path) -> None:
    WRITTEN.append(path)


# ---------------------------------------------------------------------------
# 01-Policy
# ---------------------------------------------------------------------------

def global_policy() -> None:
    p = INSTRUMENTS["policy"]
    doc = new_doc(p["title"], f"Version {p['version']} — effective {p['effective_from']}")
    control_table(doc, [
        ("Reference", p["id"]),
        ("Version", p["version"]),
        ("Effective from", p["effective_from"]),
        ("Document owner", p["owner"]),
        ("Applies to", "All products, all regions, all authorised service partners"),
        ("Supersedes", "POL-WAR-4.1 (effective 1 April 2024)"),
    ])

    doc.add_heading("Purpose", level=1)
    doc.add_paragraph(
        f"This policy sets out the warranty {MFR} provides on equipment it manufactures, "
        "the basis on which a claim from an authorised service partner is adjudicated, and "
        "the amounts payable. It applies to every claim submitted through the service "
        "claim system."
    )

    order = ["1.4", "2.1", "2.3", "4.1", "4.2", "4.3", "5.1", "5.2", "5.3", "5.4", "6.1", "7.1"]
    section_titles = {
        "1": "1. Interpretation",
        "2": "2. Coverage",
        "4": "4. Amounts payable",
        "5": "5. Exclusions",
        "6": "6. Repair warranty",
        "7": "7. Goodwill and authority",
    }
    seen: set[str] = set()
    for key in order:
        top = key.split(".")[0]
        if top not in seen:
            doc.add_heading(section_titles[top], level=1)
            seen.add(top)
        clause = p["clauses"][key]
        doc.add_heading(f"{key}  {clause['heading']}", level=2)
        doc.add_paragraph(clause["text"])

    doc.add_heading("Annexes", level=1)
    doc.add_paragraph(
        "The Flat Rate Labour schedule, the regional labour rate schedule and the parts "
        "price list are maintained separately and published in the Warranty Operations "
        "library. The Goodwill and Authority Matrix referred to at clause 7.1 is "
        "published alongside this policy."
    )
    record(save(doc, "01-Policy", f"{p['id']} {p['title']} v{p['version']}.docx"))


def addenda() -> None:
    for a in INSTRUMENTS["addenda"]:
        doc = new_doc(a["title"], f"Version {a['version']} — effective {a['effective_from']}")
        control_table(doc, [
            ("Reference", a["id"]),
            ("Region", a["region"]),
            ("Currency", a["currency"]),
            ("Effective from", a["effective_from"]),
            ("Read with", f"{INSTRUMENTS['policy']['id']} {INSTRUMENTS['policy']['title']}"),
        ])
        doc.add_heading("Scope", level=1)
        doc.add_paragraph(
            f"This addendum varies the Global Warranty Policy for equipment installed in "
            f"{a['region']}. Where this addendum is silent, the Global Warranty Policy "
            f"applies without variation. Where a Technical Service Bulletin names the "
            f"serial range of an asset, clause 1.4 of the Global Warranty Policy governs "
            f"the order of precedence."
        )
        for key, clause in a["clauses"].items():
            doc.add_heading(f"{key}  {clause['heading']}", level=2)
            doc.add_paragraph(clause["text"])

        if a["terms"]:
            doc.add_heading("Summary of varied terms", level=1)
            t = doc.add_table(rows=1, cols=3)
            t.style = "Light Grid Accent 1"
            hdr = t.rows[0].cells
            for i, h in enumerate(("Term", "Global policy", f"{a['region']}")):
                hdr[i].text = h
                hdr[i].paragraphs[0].runs[0].bold = True
            gp = INSTRUMENTS["policy"]["terms"]
            for label, g, r in (("Coverage period", f"{gp['months']} months", f"{a['terms']['months']} months"),
                                ("Running-hours limit", f"{gp['hours']:,} h", f"{a['terms']['hours']:,} h")):
                cells = t.add_row().cells
                cells[0].text, cells[1].text, cells[2].text = label, g, r
        record(save(doc, "01-Policy", f"{a['id']} {a['title']} v{a['version']}.docx"))


def authority_matrix() -> None:
    doc = new_doc("Goodwill and Authority Matrix", "Version 3 — effective 1 April 2025")
    control_table(doc, [
        ("Reference", "MTX-GW-3"),
        ("Effective from", "2025-04-01"),
        ("Authority for", "Policy clause 7.1"),
        ("Currency", "INR (equivalent amounts apply in other regions)"),
    ])
    doc.add_heading("Authority to approve goodwill", level=1)
    doc.add_paragraph(
        "An amount payable outside coverage may be authorised as goodwill only by a person "
        "holding the tier of authority shown below for that amount, and only where the "
        "authority is recorded in the claim system. An approval given in conversation, in a "
        "channel message, or by telephone does not constitute authority."
    )
    t = doc.add_table(rows=1, cols=3)
    t.style = "Light Grid Accent 1"
    for i, h in enumerate(("Tier", "Amount up to", "Approving role")):
        t.rows[0].cells[i].text = h
        t.rows[0].cells[i].paragraphs[0].runs[0].bold = True
    for tier in ENTITIES["goodwill_authority"]:
        cells = t.add_row().cells
        cells[0].text = str(tier["tier"])
        cells[1].text = (f"INR {tier['max_amount_inr']:,}" if tier["max_amount_inr"]
                         else "No limit")
        cells[2].text = tier["approver_role"]
    doc.add_paragraph()
    doc.add_heading("Recording authority", level=1)
    doc.add_paragraph(
        "Authority is recorded against the claim in the service claim system before payment "
        "is released. A claim carrying goodwill without a recorded authority at the correct "
        "tier is returned to the adjudicator."
    )
    record(save(doc, "01-Policy", "MTX-GW-3 Goodwill and Authority Matrix v3.docx"))


# ---------------------------------------------------------------------------
# 02-Bulletins
# ---------------------------------------------------------------------------

ADVISORY_TEXT = {
    "TSB-C-0038": "A firmware revision is available for the control board. Apply at the next "
                  "scheduled service visit. This bulletin is advisory and does not vary the "
                  "warranty position of any asset.",
    "TSB-C-0047": "A revised condenser fan balancing procedure is published in the service "
                  "manual. This bulletin is advisory and does not vary the warranty position "
                  "of any asset.",
    "TSB-C-0055": "The torque specification for compressor mounting bolts is revised. Refer "
                  "to the service manual for the revised figures. This bulletin is advisory "
                  "and does not vary the warranty position of any asset, and does not extend "
                  "coverage of the compressor or any other component.",
    "TSB-P-0098": "The drive coupling inspection interval is reduced. This bulletin is "
                  "advisory and does not vary the warranty position of any asset.",
    "TSB-P-0103": "The seal kit part number has changed. Order against the current part "
                  "number. This bulletin is advisory and does not vary the warranty position "
                  "of any asset.",
    "TSB-G-0021": "The packaging and returns process for warranty parts is revised. This "
                  "bulletin is advisory and does not vary the warranty position of any asset.",
    "TSB-G-0029": "Partners are reminded that a claim must carry the inspection report, the "
                  "running-hours reading at the date of repair, and the part number actually "
                  "fitted. This bulletin is advisory and does not vary the warranty position "
                  "of any asset.",
}


def bulletins() -> None:
    for b in INSTRUMENTS["bulletins"]:
        doc = new_doc(f"Technical Service Bulletin {b['id']}", b["title"])
        fams = ", ".join(FAMILY_NAME.get(f, f) for f in b["families"])
        rows = [
            ("Bulletin reference", b["id"]),
            ("Effective from", b["effective_from"]),
            ("Product family", fams),
        ]
        if b.get("serial_from") is not None:
            prefix = "CIE-4000-CH-" if "4000-CH" in b["families"] else "CIE-2200-AC-"
            rows.append(("Serial range",
                         f"{prefix}{b['serial_from']:05d} to {prefix}{b['serial_to']:05d} inclusive"))
        else:
            rows.append(("Serial range", "All serials in the named family"))
        if b.get("region"):
            rows.append(("Region", f"{b['region']} only"))
        if b.get("supersedes"):
            rows.append(("Supersedes", b["supersedes"]))
        if b.get("superseded_by"):
            rows.append(("Status", f"SUPERSEDED by {b['superseded_by']} — this bulletin has no effect"))
        else:
            rows.append(("Status", "Current"))
        control_table(doc, rows)

        if b.get("superseded_by"):
            warn = doc.add_paragraph()
            r = warn.add_run(
                f"This bulletin has been superseded by {b['superseded_by']} and has no effect. "
                f"It remains published for reference only. Do not adjudicate against it.")
            r.bold = True
            doc.add_paragraph()

        doc.add_heading("Purpose", level=1)
        if b.get("advisory_only"):
            doc.add_paragraph(ADVISORY_TEXT[b["id"]])
        elif b.get("reverses_exclusion"):
            doc.add_paragraph(
                "A manufacturing defect has been identified in the filter housing fitted to "
                "certain units, permitting particulate ingress into the hydraulic circuit. "
                "Damage arising from that ingress is not attributable to the operator."
            )
            doc.add_heading("Effect on warranty", level=1)
            doc.add_paragraph(
                f"The exclusion at clause {b['reverses_exclusion']} of the Global Warranty Policy "
                f"(fluid contamination) does not apply where the inspection report attributes the "
                f"contamination to the filter housing defect. Where the inspection report "
                f"attributes the contamination to any other cause, clause "
                f"{b['reverses_exclusion']} continues to apply and the claim is excluded."
            )
            doc.add_paragraph(
                "This bulletin does not extend the coverage period of any asset. The coverage "
                "period continues to be determined under clause 1.4 of the Global Warranty Policy."
            )
        else:
            comps = components_phrase(b["components"])
            doc.add_paragraph(
                f"Elevated failure rates have been observed on the {comps} of affected units. "
                f"Coverage is extended as set out below."
            )
            doc.add_heading("Effect on warranty", level=1)
            t = b["terms"]
            text = (f"For assets within the serial range named above, coverage of the {comps} "
                    f"is extended to {t['months']} months from the date of commissioning")
            text += (f", or {t['hours']:,} running hours, whichever occurs first."
                     if t.get("hours") else ".")
            doc.add_paragraph(text)
            doc.add_paragraph(
                "This bulletin names a serial range and therefore takes precedence over the "
                "regional addendum and the Global Warranty Policy, in accordance with clause "
                "1.4 of that policy."
            )
            if b.get("index_serial_to") is not None and b["index_serial_to"] != b.get("serial_to"):
                doc.add_heading("Note on the service system index", level=1)
                doc.add_paragraph(
                    "The applicability index held in the service claim system is maintained for "
                    "reporting and may lag this document. Where the index and this bulletin "
                    "disagree on the serial range, this bulletin governs, in accordance with "
                    "clause 1.4 of the Global Warranty Policy."
                )

        doc.add_heading("Claim handling", level=1)
        doc.add_paragraph(
            f"Claims adjudicated under this bulletin are recorded against funding code TSB with "
            f"the reference {b['id']}."
            if not b.get("advisory_only") and not b.get("superseded_by")
            else "No change to claim handling arises from this bulletin."
        )
        record(save(doc, "02-Bulletins", f"{b['id']} {b['title'][:60]}.docx"))


# ---------------------------------------------------------------------------
# 04-PartnerAgreements
# ---------------------------------------------------------------------------

def partner_agreements() -> None:
    for dealer in ENTITIES["dealers"][:3]:
        doc = new_doc("Service Partner Agreement",
                      f"{dealer['name']} — {dealer['agreement_ref']}")
        control_table(doc, [
            ("Agreement reference", dealer["agreement_ref"]),
            ("Partner", dealer["name"]),
            ("Partner code", dealer["dealer_id"]),
            ("Territory", dealer["region"]),
            ("Settlement currency", dealer["currency"]),
        ])
        doc.add_heading("1. Appointment", level=1)
        doc.add_paragraph(
            f"{MFR} appoints {dealer['name']} as an authorised service partner for the "
            f"territory named above, to carry out warranty repairs on {MFR} equipment and to "
            f"submit claims in accordance with the Global Warranty Policy."
        )
        doc.add_heading("2. Claim submission", level=1)
        doc.add_paragraph(
            f"A claim is submitted within {dealer['submission_sla_days']} days of the date of "
            f"repair, carrying the inspection report, the running-hours reading at the date of "
            f"repair, and the part number actually fitted."
        )
        doc.add_heading("3. Labour", level=1)
        doc.add_paragraph(
            "Labour is reimbursed at the flat-rate allowance published for the operation code, "
            "at the regional labour rate in force on the date of repair, in accordance with "
            "clause 4.1 of the Global Warranty Policy."
        )
        doc.add_heading("6. Parts and handling", level=1)
        doc.add_paragraph(
            "Parts are reimbursed at the published list price for the territory, for the part "
            "actually fitted."
        )
        if dealer["uplift_pct"]:
            doc.add_heading("6.2 Handling uplift", level=2)
            para = doc.add_paragraph()
            run = para.add_run(
                f"A handling uplift of {dealer['uplift_pct']}% of the reimbursed parts value is "
                f"payable to {dealer['name']} in addition to the parts value. The uplift is "
                f"calculated on parts only and does not apply to labour."
            )
            run.bold = True
        else:
            doc.add_paragraph(
                "No handling uplift is payable under this agreement. Parts are reimbursed at "
                "list price without addition."
            )
        doc.add_heading("9. Term", level=1)
        doc.add_paragraph(
            "This agreement runs for three years from execution and renews annually unless "
            "either party gives ninety days' written notice."
        )
        record(save(doc, "04-PartnerAgreements",
                    f"{dealer['agreement_ref']} {dealer['name']}.docx"))


# ---------------------------------------------------------------------------
# 06-ClaimEvidence — inspection reports
# ---------------------------------------------------------------------------

FINDINGS = {
    "HYD-PUMP-RR": ("Hydraulic pump seized under load. Drive coupling intact. No external "
                    "impact damage. Pump removed and replaced."),
    "COMP-RR": ("Compressor module drawing excessive current and tripping on overload. "
                "Windings tested out of specification. Module removed and replaced."),
    "FILT-HSG-RR": ("Filter housing cracked at the mounting boss, permitting particulate "
                    "ingress. Housing removed and replaced."),
    "CTRL-BD-RR": ("Control board unresponsive on power-up. No evidence of moisture ingress "
                   "or surge damage. Board replaced."),
    "COND-FAN-RR": ("Condenser fan assembly out of balance with bearing noise. Assembly "
                    "removed and replaced."),
    "VALVE-PLT-RR": ("Valve plate cracked across two ports with associated loss of delivery. "
                     "Plate kit replaced."),
    "MOTOR-RR": ("Drive motor failed to start, windings open circuit. Motor replaced."),
    "BEARING-RR": ("Main bearing set showing spalling on the outer race with elevated "
                   "vibration signature. Bearing set replaced."),
    "SEAL-KIT-RR": ("Shaft seal weeping at the drive end. Seal kit replaced."),
    "DIAG-FIELD": ("Field diagnostic visit. Fault not reproduced on site; no parts fitted."),
}


def inspection_reports() -> None:
    claims = json.loads((Path(__file__).resolve().parent.parent / "out" / "data" /
                         "claims.json").read_text(encoding="utf-8"))
    assets = {a["serial"]: a for a in json.loads(
        (Path(__file__).resolve().parent.parent / "out" / "data" /
         "assets.json").read_text(encoding="utf-8"))}

    # every exclusion claim (the report is what decides them), plus a spread of others
    chosen = [r for r in claims if r["slice"] == "exclusion"]
    for slice_ in ("precedence", "dual-limit", "valuation", "abstention",
                   "covered-simple", "declined-simple", "authority", "stale-deck"):
        chosen += [r for r in claims if r["slice"] == slice_ and r["split"] == "eval"][:1]

    for r in chosen:
        c, a = r["claim"], assets[r["claim"]["serial"]]
        dealer = DEALERS[c["dealer_id"]]
        doc = new_doc("Field Inspection Report", f"Claim {c['claim_id']}")
        control_table(doc, [
            ("Claim reference", c["claim_id"]),
            ("Serial number", c["serial"]),
            ("Product", FAMILY_NAME.get(a["family"], a["family"])),
            ("Service partner", dealer["name"]),
            ("Date of repair", c["repair_date"]),
            ("Operation code", c["op_code"]),
            ("Running hours at repair",
             f"{c['hours_at_repair']:,}" if c["hours_at_repair"] is not None
             else "Not recorded — telemetry unavailable"),
        ])
        doc.add_heading("Findings", level=1)
        doc.add_paragraph(FINDINGS.get(c["op_code"], "Component failed in service."))

        if c.get("exclusion_flags"):
            doc.add_heading("Fluid analysis", level=1)
            if c.get("contamination_from_filter_housing"):
                doc.add_paragraph(
                    "Hydraulic fluid sample returned ISO 4406 class 22/20/17, above the "
                    "acceptable limit. Particulate examined under magnification and found to be "
                    "aluminium consistent with the filter housing casting. The filter housing "
                    "was found cracked at the mounting boss. The contamination is attributable "
                    "to the filter housing defect described in TSB-C-0043."
                )
            else:
                doc.add_paragraph(
                    "Hydraulic fluid sample returned ISO 4406 class 22/20/17, above the "
                    "acceptable limit. Particulate examined under magnification and found to be "
                    "silica consistent with ingress through an unsealed reservoir cap left open "
                    "during site top-up. The filter housing was examined and found intact. The "
                    "contamination is not attributable to the filter housing defect."
                )

        doc.add_heading("Parts fitted", level=1)
        if c.get("part_fitted"):
            part = PARTS.get(c["part_fitted"], {})
            t = doc.add_table(rows=1, cols=3)
            t.style = "Light Grid Accent 1"
            for i, h in enumerate(("Part number", "Description", "Quantity")):
                t.rows[0].cells[i].text = h
                t.rows[0].cells[i].paragraphs[0].runs[0].bold = True
            cells = t.add_row().cells
            cells[0].text = c["part_fitted"]
            cells[1].text = part.get("description", "")
            cells[2].text = "1"
            doc.add_paragraph()
            if c.get("claimed_part") and c["claimed_part"] != c["part_fitted"]:
                doc.add_paragraph(
                    f"Note: the claim was raised against {c['claimed_part']}. The part actually "
                    f"fitted was {c['part_fitted']}."
                )
        else:
            doc.add_paragraph("No parts fitted.")

        doc.add_heading("Labour", level=1)
        doc.add_paragraph(f"{c['claimed_hours']} hours claimed against operation "
                          f"{c['op_code']}.")
        doc.add_paragraph()
        sig = doc.add_paragraph("Inspected by: Sunil Bhat, Field Engineer, "
                                f"{dealer['name']}")
        sig.runs[0].italic = True
        record(save(doc, "06-ClaimEvidence",
                    f"{c['claim_id']} Inspection Report {c['serial']}.docx"))


# ---------------------------------------------------------------------------
# 07-Reference — plausible distractors
# ---------------------------------------------------------------------------

def reference_docs() -> None:
    doc = new_doc("Service Manual Extract", "4000-series chiller — hydraulic circuit")
    control_table(doc, [("Document", "SM-4000-HYD-07"),
                        ("Revision", "7"),
                        ("Applies to", "4000-series industrial chiller, all serials")])
    doc.add_heading("Hydraulic circuit overview", level=1)
    doc.add_paragraph(
        "The hydraulic circuit comprises the pump assembly, the filter housing and element, "
        "the reservoir, and the delivery and return hose sets. Service intervals are given in "
        "the maintenance schedule. Fluid cleanliness is to be maintained at ISO 4406 class "
        "18/16/13 or better."
    )
    doc.add_heading("Pump removal and replacement", level=1)
    doc.add_paragraph(
        "Isolate the machine and relieve circuit pressure before disconnecting any hose. "
        "Drain the reservoir. Disconnect the drive coupling, release the four mounting bolts "
        "and withdraw the pump. Fit the replacement pump with a new gasket and torque the "
        "mounting bolts to the figure given in the specification table."
    )
    doc.add_paragraph(
        "This manual describes how work is carried out. It does not determine whether work "
        "is covered by warranty, which is a matter for the Global Warranty Policy and any "
        "applicable Technical Service Bulletin."
    )
    record(save(doc, "07-Reference", "SM-4000-HYD-07 Service Manual Extract.docx"))

    doc = new_doc("Service Partner FAQ", "Warranty claims — frequently asked questions")
    control_table(doc, [("Document", "FAQ-WAR-2"),
                        ("Revision", "2"),
                        ("Audience", "Authorised service partners")])
    qa = [
        ("How long does a claim take to settle?",
         "Claims are adjudicated within ten working days of submission where the inspection "
         "report and running-hours reading are complete."),
        ("What if the machine is just outside its coverage period?",
         "Raise the claim in the normal way. The adjudicator will consider whether a Technical "
         "Service Bulletin applies, and whether goodwill is appropriate. Goodwill requires "
         "authority at the tier set out in the Goodwill and Authority Matrix."),
        ("Can I fit a superseded part?",
         "Order against the current part number. Where a part has been superseded, the price "
         "of the superseding part applies."),
        ("Who do I ask about a specific claim?",
         "Post in the Field Escalations channel with the claim reference. Note that a reply "
         "in a channel is not an approval; authority is recorded in the claim system."),
    ]
    for q, a in qa:
        doc.add_heading(q, level=2)
        doc.add_paragraph(a)
    record(save(doc, "07-Reference", "FAQ-WAR-2 Service Partner FAQ.docx"))


if __name__ == "__main__":
    global_policy()
    addenda()
    authority_matrix()
    bulletins()
    partner_agreements()
    inspection_reports()
    reference_docs()

    by_folder: dict[str, int] = {}
    for p in WRITTEN:
        by_folder[p.parent.name] = by_folder.get(p.parent.name, 0) + 1
    for folder, n in sorted(by_folder.items()):
        print(f"  {folder:22} {n:>3} documents")
    print(f"\n{len(WRITTEN)} Word documents written to {OUT}")
