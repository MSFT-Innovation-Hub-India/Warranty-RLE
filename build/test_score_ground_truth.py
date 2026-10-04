"""Checks for score_ground_truth.py's extraction rules.

    .venv/Scripts/python.exe build/test_score_ground_truth.py
"""

from __future__ import annotations

import sys

from score_ground_truth import extract_decision, extract_governing, extract_total, load_expected

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
]

FUNCS = {"decision": extract_decision, "governing": extract_governing, "total": extract_total}


def _parts_check() -> bool:
    from score_ground_truth import _text
    return _text([{"Content": "Line one"}, {"Content": "**Total payable: ₹199,175**"}]).endswith("₹199,175**")


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
    print(f"\n{len(CASES) + 2 - failed}/{len(CASES) + 2} checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
