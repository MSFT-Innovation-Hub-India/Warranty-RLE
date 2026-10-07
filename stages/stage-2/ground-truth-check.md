# Ground-truth check — stage-2-base

Scored by `build/score_ground_truth.py` against `out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 30 |
| Decision correct | 27/30 (90%) |
| Governing instrument correct | 30/30 (100%) |
| Payable correct (approvals) | 16/17 (94%) |
| **Fully correct** | **27/30 (90%)** |
| Needs human review | 2 |
| Mean rubric score (platform) | 0.98 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| abstention | 3 | 2 | 0.989 |
| authority | 2 | 1 | 0.99 |
| covered-simple | 3 | 3 | 0.983 |
| declined-simple | 2 | 2 | 0.964 |
| dual-limit | 3 | 3 | 0.987 |
| precedence | 5 | 5 | 0.992 |
| serial-boundary | 4 | 3 | 0.98 |
| stale-deck | 2 | 2 | 0.98 |
| valuation | 6 | 6 | 0.961 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹69,575 → ₹69,575 ✅ | 1.0 | ✅ |  |
| `C-2026-04102` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹48,420 → ₹48,420 ✅ | 0.95 | ✅ |  |
| `C-2026-04103` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹19,150 → ₹19,150 ✅ | 1.0 | ✅ |  |
| `C-2026-04109` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04110` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.927 | ✅ |  |
| `C-2026-04114` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.96 | ✅ |  |
| `C-2026-04115` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 1.0 | ✅ |  |
| `C-2026-04116` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04117` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04118` | precedence | approve → approve ✅ | TSB-P-0112 → TSB-P-0112 ✅ | ₹67,500 → ₹67,500 ✅ | 1.0 | ✅ |  |
| `C-2026-04129` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04130` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 0.96 | ✅ |  |
| `C-2026-04131` | serial-boundary | approve → request_evidence ❌ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ❌ | 0.96 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04132` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04139` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04140` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04141` | dual-limit | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.96 | ✅ |  |
| `C-2026-04148` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹208,735 → ₹208,735 ✅ | 1.0 | ✅ |  |
| `C-2026-04149` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹753,880 → ₹753,880 ✅ | 1.0 | ✅ |  |
| `C-2026-04150` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 1.0 | ✅ |  |
| `C-2026-04151` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹31,030 → ₹31,030 ✅ | 1.0 | ✅ |  |
| `C-2026-04152` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹197,000 → ₹197,000 ✅ | 1.0 | ✅ |  |
| `C-2026-04153` | valuation | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹72,945 → ₹72,945 ✅ | 0.767 | ✅ |  |
| `C-2026-04166` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.96 | ✅ |  |
| `C-2026-04167` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 1.0 | ✅ |  |
| `C-2026-04171` | authority | escalate → escalate ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹67,400 ✅ | 0.98 | ✅ |  |
| `C-2026-04172` | authority | escalate → review ❓ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹312,000 ✅ | 1.0 | ❓ | decision unclear |
| `C-2026-04176` | abstention | request_evidence → request_evidence ✅ | — → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04177` | abstention | request_evidence → request_evidence ✅ | — → POL-WAR-4.2 ✅ | — → — ✅ | 0.967 | ✅ |  |
| `C-2026-04178` | abstention | request_evidence → decline ❌ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ❌ |  |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
