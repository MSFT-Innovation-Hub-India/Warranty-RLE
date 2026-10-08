"""Checks for score_ground_truth.py's extraction rules.

    .venv/Scripts/python.exe scripts/test_score_ground_truth.py
"""

from __future__ import annotations

import sys

from score_ground_truth import delivery_mismatch, extract_decision, extract_governing, extract_total, load_expected

CASES = [
    ("decision", "**Yes — the repair is covered under TSB-C-0051.**", "approve"),
    ("decision", "**Approve.** Payable ₹199,175.", "approve"),
    ("decision", "The claim is **not covered**: the 18-month term expired.", "decline"),
    ("decision", "**Decline.** Coverage ended on 4 October 2025.", "decline"),
    ("decision", "The asset is out of warranty, so the claim is declined.", "decline"),
    ("decision", "Coverage **cannot yet be decided**: the commissioning date is missing.", "request_evidence"),
    ("decision", "Hold the claim and request the commissioning certificate.", "request_evidence"),
    ("decision", "This needs to be escalated to the Regional Service Manager for goodwill.", "escalate"),
    ("decision", "Not covered under warranty; escalate the goodwill request to tier 2.", "escalate"),
    ("decision", "**Approve.** Covered under TSB-C-0051; no escalation is needed.", "approve"),
    ("decision", "**Decline.** Out of warranty; there is no need to request further evidence.", "decline"),
    ("decision", "## Decision: **cannot yet be finally decided — hold for evidence**\nDo **not** decline the claim.", "request_evidence"),
    ("decision", "## Decision — **hold for evidence; not declined**\nClaim is prima facie covered.", "request_evidence"),
    ("decision", "# C-2026-04114 — **HOLD / CANNOT YET DECIDE**", "request_evidence"),
    ("decision", "We should not decline this. **Approve** — covered under ADD-IN-2.1.", "approve"),
    ("decision", "## Decision — decline as outside warranty\n**Claim C-2026-04109 should be declined. Current status is “Submitted”; no draft adjudication, evidence request, or escalation was created or modified.**", "decline"),
    ("decision", "Not covered under warranty, so escalate or decline the goodwill request.", "escalate"),
    ("decision", "**Decision: decline under warranty.** No draft adjudication, evidence request, goodwill escalation, or other claim-system change was made.", "decline"),
    ("decision", "The claim is not covered, but escalate the goodwill request to the Regional Service Manager.", "escalate"),
    ("governing", "**Approve claim C-2026-04150 for INR 755,050.00.** The repair is covered by **TSB-C-0051**. Under Global Warranty Policy **POL-WAR-4.2 clause 1.4**, a TSB takes precedence.", "TSB-C-0051"),
    ("governing", "**TSB-C-0051 does not govern this repair.** Under **POL-WAR-4.2 clause 1.4**, the order is bulletin, then addendum. Because TSB-C-0051 does not cover controls, **ADD-IN-2.1 A1**, read with the global policy, governs.", "ADD-IN-2.1"),
    ("governing", "Covered under **TSB-C-0051**, which takes precedence over ADD-IN-2.1.", "TSB-C-0051"),
    ("governing", "ADD-IN-2.1 applies to India installations; POL-WAR-4.2 is the baseline.", "ADD-IN-2.1"),
    ("total", "Labour ₹7,975\nParts ₹191,200\n**Total payable: ₹199,175**", 199175.0),
    ("total", "Total payable: ₹1,99,175 (labour ₹7,975 + parts ₹1,91,200)", 199175.0),
    ("total", "Amount payable EUR 2,341.50", 2341.50),
    ("total", "No amount is payable.", None),
    # stage 0 (world v3) misreads, 2026-10-08
    ("decision", "Decision: **Covered**. C-2026-04152 is payable at **INR 197,000** under **TSB-C-0051**.", "approve"),
    ("governing", "Decision: approve claim C-2026-04101 for INR 69,575. Under the India addendum and the global policy, the period is 18 months. TSB-C-0051 does not apply to this serial.", "ADD-IN-2.1"),
    ("governing", "Decline. TSB-C-0051 also does not apply because this serial (01950) is outside the named range. The India addendum ADD-IN-2.1 applies.", "ADD-IN-2.1"),
    ("governing", "- Global Warranty Policy POL-WAR-4.2 governs the baseline.\n- India addendum ADD-IN-2.1 applies because the asset is installed in India.", "ADD-IN-2.1"),
    ("governing", "The applicable coverage instrument is the India addendum (ADD-IN-2.1). No bulletin changes this result: TSB-P-0115 is EMEA only.", "ADD-IN-2.1"),
    ("total", "Decision: approve for INR 69,575.\n- Labour: 1.5 h at INR 1,450/hour = INR 2,175. Payable labour is the lesser.\n- Total payable: INR 69,575.", 69575.0),
    ("total", "- Labour: 1.5 h × INR 1,450 = INR 2,175, payable at the flat rate.\n- Total: INR 67,400 + INR 2,175 + INR 3,370 = INR 72,945.", 72945.0),
    ("total", "Decision: Approve claim C-2026-04131 for INR 198,450. Labour 5.0 h is payable at INR 1,450, so payable labour is INR 7,250.", 198450.0),
    # stage 1 misreads, 2026-10-08
    ("decision", "Decision: the claim is not yet decidable; I recorded a draft as request_evidence.", "request_evidence"),
    ("delivery", "The fuller attempted messages were rejected by the finish tool and were not successfully delivered.", True),
    ("delivery", "The only successfully delivered finish message states that the agent was \u201cnot able to complete\u201d.", True),
    ("delivery", "The successful finish only states that the assessment could not be completed.", True),
    ("delivery", "The remaining elements appear only in finish calls rejected by the formatter.", True),
    ("delivery", "The successful final response only says it is \u201cunable to finalize\u201d.", True),
    ("delivery", "The accepted hand-in is an inability statement; the investigation reached a covered conclusion in its attempted hand-ins.", True),
    ("delivery", "The successful hand-in is abbreviated and begins with a tool-formatting disclaimer before the result.", True),
    ("delivery", "It gives useful facts and dates, but the successful submission has no inline citations.", False),
    ("delivery", "The final hand-in begins with inability to calculate rather than directly leading with the covered decision.", True),
    ("delivery", "The successful hand-in gives a definite covered decision, identifies TSB-C-0051, and calculates INR 755,050.", False),
    ("delivery", "It omits the material inability to locate claim-specific inspection evidence from the successful final response.", False),
    ("delivery", "The response leads with \u201cDecision: Covered\u201d and the payable total, then presents dated facts.", False),
    ("delivery", "The final message documents dates and the recorded draft, and finishes with the next action.", False),
]

FUNCS = {"decision": extract_decision, "governing": extract_governing, "total": extract_total,
         "delivery": delivery_mismatch}


def _parts_check() -> bool:
    from score_ground_truth import _text
    return _text([{"Content": "Line one"}, {"Content": "**Total payable: ₹199,175**"}]).endswith("₹199,175**")


def _delivered_check() -> bool:
    from score_ground_truth import delivered_decision
    a = delivered_decision("The final successful finish definitively says the claim \u201ccannot yet be conclusively decided,\u201d and explains why.")
    b = delivered_decision("The successfully delivered finish message gives a definite approval and total, but omits the instrument.")
    c = delivered_decision("The response uses claim-system records throughout.")
    return a == "request_evidence" and b == "approve" and c is None


def _no_decision_check() -> bool:
    from score_ground_truth import _no_decision
    a = _no_decision("Adjudicate claim C-2026-04167.", "Adjudicate claim C-2026-04167.")
    b = _no_decision("Where do we land on C-2026-04141?", "I'm unable to complete the requested warranty adjudication because the rate card is missing.")
    b = b and _no_decision("Take a look at C-2026-04129.", "I can\u2019t determine the outcome of claim C-2026-04129 from the currently available records.")
    c = _no_decision("Adjudicate claim C-2026-04101.", "The asset was commissioned on 2025-03-15 and the repair falls inside the period.")
    return bool(a) and bool(b) and c is None


def main() -> int:
    failed = 0
    for kind, text, want in CASES:
        got = FUNCS[kind](text)
        ok = got == want
        failed += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {kind:9} {want!r:>22} <- {text[:70]!r}" + ("" if ok else f"   got {got!r}"))
    exp = load_expected()
    ok = len(exp) == 90 and exp["C-2026-04114"]["total"] == 199175.0
    failed += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  expected answers load: {len(exp)} claims, C-2026-04114 = ₹{exp['C-2026-04114']['total']:,.0f}")
    ok = _parts_check()
    failed += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  response given as a list of parts is joined to text")
    ok = _delivered_check()
    failed += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  delivered decision read from the grader's description")
    ok = _no_decision_check()
    failed += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  an echoed question or inability statement counts as no answer")
    print(f"\n{len(CASES) + 4 - failed}/{len(CASES) + 4} checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
