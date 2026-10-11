# Ground-truth check — results

Scored by `scripts/score_ground_truth.py` against `world-builder/out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 30 |
| Decision correct | 28/30 (93%) |
| Governing instrument correct | 29/30 (97%) |
| Payable correct (approvals) | 16/17 (94%) |
| **Fully correct** | **26/30 (87%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 0 |
| Needs human review (unreadable) | 2 |
| Mean rubric score (platform) | 0.956 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| abstention | 3 | 2 | 0.978 |
| authority | 2 | 1 | 0.969 |
| covered-simple | 3 | 3 | 0.967 |
| declined-simple | 2 | 2 | 0.969 |
| dual-limit | 3 | 3 | 0.919 |
| precedence | 5 | 5 | 0.98 |
| serial-boundary | 4 | 4 | 0.98 |
| stale-deck | 2 | 2 | 0.975 |
| valuation | 6 | 4 | 0.905 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹69,575 → ₹69,575 ✅ | 0.95 | ✅ |  |
| `C-2026-04102` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹48,420 → ₹48,420 ✅ | 0.95 | ✅ |  |
| `C-2026-04103` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹19,150 → ₹19,150 ✅ | 1.0 | ✅ |  |
| `C-2026-04109` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04110` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.938 | ✅ |  |
| `C-2026-04114` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04115` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 1.0 | ✅ |  |
| `C-2026-04116` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.938 | ✅ |  |
| `C-2026-04117` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04118` | precedence | approve → approve ✅ | TSB-P-0112 → TSB-P-0112 ✅ | ₹67,500 → ₹67,500 ✅ | 0.96 | ✅ |  |
| `C-2026-04129` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04130` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 0.958 | ✅ |  |
| `C-2026-04131` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 0.96 | ✅ |  |
| `C-2026-04132` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04139` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 0.933 | ✅ |  |
| `C-2026-04140` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 0.875 | ✅ |  |
| `C-2026-04141` | dual-limit | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.95 | ✅ |  |
| `C-2026-04148` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹208,735 → ₹208,735 ✅ | 0.95 | ✅ |  |
| `C-2026-04149` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹753,880 → ₹753,880 ✅ | 0.767 | ✅ |  |
| `C-2026-04150` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.903 | ✅ |  |
| `C-2026-04151` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹31,030 → ₹29,455 ❌ | 0.96 | ❌ |  |
| `C-2026-04152` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹197,000 → ₹197,000 ✅ | 0.893 | ✅ |  |
| `C-2026-04153` | valuation | approve → approve ✅ | ADD-IN-2.1 → TSB-C-0051 ❌ | ₹72,945 → ₹72,945 ✅ | 0.96 | ❌ |  |
| `C-2026-04166` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04167` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.95 | ✅ |  |
| `C-2026-04171` | authority | escalate → escalate ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.938 | ✅ |  |
| `C-2026-04172` | authority | escalate → review ❓ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 1.0 | ❓ | decision unclear |
| `C-2026-04176` | abstention | request_evidence → review ❓ | — → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 0.933 | ❓ | decision unclear |
| `C-2026-04177` | abstention | request_evidence → request_evidence ✅ | — → POL-WAR-4.2 ✅ | — → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04178` | abstention | request_evidence → request_evidence ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 1.0 | ✅ |  |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
