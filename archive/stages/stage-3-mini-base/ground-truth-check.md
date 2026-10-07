# Ground-truth check — stage-3-mini-base

Scored by `build/score_ground_truth.py` against `out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 28 |
| Decision correct | 14/28 (50%) |
| Governing instrument correct | 12/28 (43%) |
| Payable correct (approvals) | 5/16 (31%) |
| **Fully correct** | **1/28 (4%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 19 |
| Needs human review | 26 |
| Mean rubric score (platform) | 0.416 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| abstention | 3 | 1 | 0.428 |
| authority | 2 | 0 | 0.367 |
| covered-simple | 3 | 0 | 0.285 |
| declined-simple | 1 | 0 | 0.663 |
| dual-limit | 3 | 0 | 0.386 |
| precedence | 4 | 0 | 0.412 |
| serial-boundary | 4 | 0 | 0.431 |
| stale-deck | 2 | 0 | 0.621 |
| valuation | 6 | 0 | 0.39 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → request_evidence ❌ | ADD-IN-2.1 → — ❌ | ₹69,575 → — ❌ | 0.292 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected); request evidence given, so payable not assessed |
| `C-2026-04102` | covered-simple | approve → request_evidence ❌ | ADD-IN-2.1 → — ❌ | ₹48,420 → — ❌ | 0.502 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected); request evidence given, so payable not assessed |
| `C-2026-04103` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹19,150 → ₹19,150 ✅ | 0.062 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04109` | declined-simple | decline → request_evidence ❌ | ADD-IN-2.1 → — ❌ | — → — ✅ | 0.663 | ❌ |  |
| `C-2026-04114` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.193 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04115` | precedence | approve → request_evidence ❌ | TSB-C-0051 → — ❌ | ₹755,050 → — ❌ | 0.517 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04116` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.29 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04117` | precedence | decline → review ❓ | ADD-IN-2.1 → — ❌ | — → — ✅ | 0.65 | ❓ | decision unclear |
| `C-2026-04129` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → — ❌ | — → ₹191,200 ✅ | 0.465 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04130` | serial-boundary | approve → request_evidence ❌ | TSB-C-0051 → — ❌ | ₹198,450 → ₹191,200 ❌ | 0.69 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04131` | serial-boundary | approve → request_evidence ❌ | TSB-C-0051 → — ❌ | ₹198,450 → — ❌ | 0.098 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected); request evidence given, so payable not assessed |
| `C-2026-04132` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → TSB-C-0051 ❌ | — → — ✅ | 0.472 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04139` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 0.257 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04140` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 0.45 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04141` | dual-limit | approve → request_evidence ❌ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → — ❌ | 0.45 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected); request evidence given, so payable not assessed |
| `C-2026-04148` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹208,735 → ₹208,735 ✅ | 0.393 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04149` | valuation | approve → request_evidence ❌ | TSB-C-0051 → POL-WAR-1.4 ❌ | ₹753,880 → — ❌ | 0.557 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04150` | valuation | approve → approve ✅ | TSB-C-0051 → — ❌ | ₹755,050 → ₹742,000 ❌ | 0.357 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04151` | valuation | approve → review ❓ | TSB-C-0051 → — ❌ | ₹31,030 → — ❓ | 0.452 | ❓ | decision unclear; no amount stated |
| `C-2026-04152` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹197,000 → ₹197,000 ✅ | 0.415 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04153` | valuation | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹72,945 → ₹72,945 ✅ | 0.163 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04166` | stale-deck | approve → request_evidence ❌ | TSB-C-0051 → POL-WAR-1.4 ❌ | ₹199,175 → — ❌ | 0.625 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04167` | stale-deck | approve → review ❓ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹742,000 ❌ | 0.617 | ❓ | decision unclear |
| `C-2026-04171` | authority | escalate → approve ❌ | ADD-IN-2.1 → — ❌ | — → ₹67,400 ✅ | 0.428 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04172` | authority | escalate → review ❓ | ADD-IN-2.1 → — ❌ | — → ₹312,000 ✅ | 0.306 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected); decision unclear |
| `C-2026-04176` | abstention | request_evidence → request_evidence ✅ | — → — ✅ | — → — ✅ | 0.526 | ✅ |  |
| `C-2026-04177` | abstention | request_evidence → request_evidence ✅ | — → POL-WAR-4.2 ✅ | — → — ✅ | 0.347 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |
| `C-2026-04178` | abstention | request_evidence → request_evidence ✅ | ADD-IN-2.1 → — ❌ | — → — ✅ | 0.41 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected) |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
