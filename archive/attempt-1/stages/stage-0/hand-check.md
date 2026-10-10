# Stage 0: hand check of the scorer's flags (2026-10-08)

`scripts/score_ground_truth.py` gave 16/30 fully correct with 7 ❓. Every ❓ and ❌ was read by hand against GROUND-TRUTH.md.

| Claim | Scorer | Delivered answer | Verdict |
| --- | --- | --- | --- |
| 04101 | ❌ governing, payable | "approve… INR 69,575… under the India addendum and the global policy" | ✅ scorer read a labour sub-line (₹2,175) and a TSB mention |
| 04103 | ❓ | "approve / covered… INR 19,150… India addendum (ADD-IN-2.1)"; next action lost in a rejected hand-in | ✅ |
| 04116 | ❌ governing | Decline; "TSB-C-0051 also does not apply because this serial (01950) is outside the named serial range" | ✅ scorer missed the negation |
| 04131 | ❌ payable | "Approve… INR 198,450… TSB-C-0051" | ✅ scorer read a labour sub-line |
| 04152 | ❓ | "Decision: Covered… INR 197,000 under TSB-C-0051"; breakdown lost in a rejected hand-in | ✅ |
| 04153 | ❌ governing, payable | "approve… INR 72,945… Global Warranty Policy and India Regional Addendum" | ✅ |
| 04178 | ❌ governing | Held for the missing running-hours reading; "India addendum ADD-IN-2.1 applies" | ✅ |
| 04115, 04140, 04167, 04176 | ❓ | **The user's question handed in as the answer** (grader: "passing the user's query verbatim to `finish`") | ❌ echoed hand-in |
| 04141 | ❓ | "unable to complete… rate-card evidence is not available"; draft approve, payable 0 | ❌ |
| 04171, 04172 | ❌ decision | Declined; goodwill was requested beyond the requester's authority, so the key says escalate | ❌ authority trap |
| 04139 | ✅ | First invocation echoed the question (rubrics 0.0); the platform re-ran the skill, which declined correctly (1.0) | ✅ (one echo) |

**Result: 23/30 fully correct.** Scorer misreads: 7 (sub-line amounts, a negated instrument, bold "Covered"). Fix before stage 1.
