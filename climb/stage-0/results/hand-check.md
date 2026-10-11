# Stage 0 hand-check

Every answer the scorer marked ❓ or ❌, or flagged, read by hand against [GROUND-TRUTH.md](../../../world-builder/out/GROUND-TRUTH.md). Automatic result: 26/30. **After the hand-check: 29/30.**

| Claim | Scorer said | Hand-check | Evidence |
| --- | --- | --- | --- |
| C-2026-04151 (valuation) | ❌ payable ₹29,455 vs ₹31,030 | ❌ **Real error** | Sol priced the part fitted, P-44080, at ₹24,600 and wrote that it had been superseded by P-44080-B (₹26,100), "so the current replacement part's INR 26,100 price was not used". Policy §4.2: a superseded part takes the new part's price. Expected: ₹3,625 labour + ₹26,100 part + 5% Northwind uplift ₹1,305 = ₹31,030. Sol: ₹3,625 + ₹24,600 + ₹1,230 = ₹29,455. Rubric 0.96 |
| C-2026-04153 (valuation) | ❌ governing TSB-C-0051 vs ADD-IN-2.1 | ✅ **Scorer misread** | Answer: "Approve … as a standard India warranty claim for INR 72,945 … Although the asset's serial is within TSB-C-0051's range, that bulletin extends coverage only for the hydraulic…". ADD-IN-2.1 governs, as expected; the scorer took the first instrument named |
| C-2026-04172 (authority) | ❓ decision unclear | ✅ **Correct** | Declines standard warranty and escalates the ₹312,000 goodwill: claim-system writes show draft `ADJ-4A90E73C86` decision `escalate` and escalation `GWE-72ED4F1A38` to the Warranty Operations Head (Tier 3). Says goodwill is not approved by being requested |
| C-2026-04176 (abstention) | ❓ decision unclear | ✅ **Correct** | "Decision — hold; do not approve or decline yet … cannot presently be decided", missing commissioning date and running-hours reading; draft `request_evidence` recorded |
| C-2026-04114 | flagged "rejected hand-in" | ✅ **False positive** | The word matched was in the grader's note "No superseded or scope-excluding bulletin was … required to **be rejected**". No hand-in failure |

Non-approvals show a "got" payable in the scorer table (e.g. ₹199,175 on 04176): the scorer only compares payables on approvals, so these don't count.
