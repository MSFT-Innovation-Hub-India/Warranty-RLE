# Ground-truth check — stage-0

Scored by `build/score_ground_truth.py` against `out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 8 |
| Decision correct | 1/8 (12%) |
| Governing instrument correct | 3/8 (38%) |
| Payable correct (approvals) | 0/5 (0%) |
| **Fully correct** | **1/8 (12%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 0 |
| Needs human review | 5 |
| Mean rubric score (platform) | 0.63 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| covered-simple | 3 | 0 | 0.636 |
| declined-simple | 2 | 1 | 0.667 |
| precedence | 3 | 0 | 0.6 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → request_evidence ❌ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹69,575 → ₹69,575 ❌ | 0.747 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04102` | covered-simple | approve → request_evidence ❌ | ADD-IN-2.1 → POL-WAR-4.2 ❌ | ₹48,420 → ₹1,450 ❌ | 0.533 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04103` | covered-simple | approve → request_evidence ❌ | ADD-IN-2.1 → POL-WAR-4.2 ❌ | ₹19,150 → — ❌ | 0.627 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04109` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.744 | ✅ |  |
| `C-2026-04110` | declined-simple | decline → request_evidence ❌ | ADD-IN-2.1 → POL-WAR-4.2 ❌ | — → — ✅ | 0.59 | ❌ |  |
| `C-2026-04114` | precedence | approve → request_evidence ❌ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ❌ | 0.7 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04116` | precedence | decline → request_evidence ❌ | ADD-IN-2.1 → POL-WAR-4.2 ❌ | — → — ✅ | 0.5 | ❌ |  |
| `C-2026-04118` | precedence | approve → request_evidence ❌ | TSB-P-0112 → POL-WAR-4.2 ❌ | ₹67,500 → — ❌ | 0.6 | ❌ | request evidence given, so payable not assessed |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
