# Ground-truth check — stage-1

Scored by `build/score_ground_truth.py` against `out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 8 |
| Decision correct | 3/8 (38%) |
| Governing instrument correct | 5/8 (62%) |
| Payable correct (approvals) | 1/5 (20%) |
| **Fully correct** | **3/8 (38%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 0 |
| Needs human review | 4 |
| Mean rubric score (platform) | 0.913 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| covered-simple | 3 | 1 | 0.989 |
| declined-simple | 2 | 2 | 1.0 |
| precedence | 3 | 0 | 0.778 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹69,575 → ₹69,575 ✅ | 1.0 | ✅ |  |
| `C-2026-04102` | covered-simple | approve → request_evidence ❌ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹48,420 → ₹48,420 ❌ | 1.0 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04103` | covered-simple | approve → request_evidence ❌ | ADD-IN-2.1 → POL-WAR-4.2 ❌ | ₹19,150 → ₹19,150 ❌ | 0.967 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04109` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04110` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04114` | precedence | approve → request_evidence ❌ | TSB-C-0051 → POL-WAR-4.2 ❌ | ₹199,175 → ₹199,175 ❌ | 0.747 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04116` | precedence | decline → request_evidence ❌ | ADD-IN-2.1 → POL-WAR-4.2 ❌ | — → ₹191,200 ✅ | 0.627 | ❌ |  |
| `C-2026-04118` | precedence | approve → request_evidence ❌ | TSB-P-0112 → TSB-P-0112 ✅ | ₹67,500 → ₹67,500 ❌ | 0.96 | ❌ | request evidence given, so payable not assessed |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
