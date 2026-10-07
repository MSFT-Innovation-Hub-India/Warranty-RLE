# Ground-truth check — stage-1-v2

Scored by `build/score_ground_truth.py` against `out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 8 |
| Decision correct | 7/8 (88%) |
| Governing instrument correct | 8/8 (100%) |
| Payable correct (approvals) | 4/5 (80%) |
| **Fully correct** | **7/8 (88%)** |
| Needs human review | 1 |
| Mean rubric score (platform) | 0.991 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| covered-simple | 3 | 2 | 0.976 |
| declined-simple | 2 | 2 | 1.0 |
| precedence | 3 | 3 | 1.0 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹69,575 → ₹69,575 ✅ | 1.0 | ✅ |  |
| `C-2026-04102` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹48,420 → ₹48,420 ✅ | 0.927 | ✅ |  |
| `C-2026-04103` | covered-simple | approve → request_evidence ❌ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹19,150 → ₹19,150 ❌ | 1.0 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04109` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04110` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04114` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04116` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04118` | precedence | approve → approve ✅ | TSB-P-0112 → TSB-P-0112 ✅ | ₹67,500 → ₹67,500 ✅ | 1.0 | ✅ |  |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
