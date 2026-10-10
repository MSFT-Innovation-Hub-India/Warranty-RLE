# Ground-truth check — stage-1

Scored by `scripts/score_ground_truth.py` against `world-builder/out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 30 |
| Decision correct | 25/30 (83%) |
| Governing instrument correct | 24/30 (80%) |
| Payable correct (approvals) | 15/17 (88%) |
| **Fully correct** | **23/30 (77%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 0 |
| Needs human review (unreadable) | 0 |
| Mean rubric score (platform) | 0.637 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| abstention | 3 | 3 | 0.678 |
| authority | 2 | 0 | 0.409 |
| covered-simple | 3 | 3 | 0.687 |
| declined-simple | 2 | 2 | 0.875 |
| dual-limit | 3 | 2 | 0.443 |
| precedence | 5 | 4 | 0.666 |
| serial-boundary | 4 | 2 | 0.534 |
| stale-deck | 2 | 1 | 0.647 |
| valuation | 6 | 6 | 0.728 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹69,575 → ₹69,575 ✅ | 0.86 | ✅ |  |
| `C-2026-04102` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹48,420 → ₹48,420 ✅ | 0.86 | ✅ |  |
| `C-2026-04103` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹19,150 → ₹19,150 ✅ | 0.342 | ✅ |  |
| `C-2026-04109` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.875 | ✅ |  |
| `C-2026-04110` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.875 | ✅ |  |
| `C-2026-04114` | precedence | approve → approve ✅ | TSB-C-0051 → — ❌ | ₹199,175 → — ❓ | 0.37 | ❌ | no amount stated |
| `C-2026-04115` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.819 | ✅ |  |
| `C-2026-04116` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.729 | ✅ |  |
| `C-2026-04117` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.708 | ✅ |  |
| `C-2026-04118` | precedence | approve → approve ✅ | TSB-P-0112 → TSB-P-0112 ✅ | ₹67,500 → ₹67,500 ✅ | 0.703 | ✅ |  |
| `C-2026-04129` | serial-boundary | decline → review ❌ | ADD-IN-2.1 → POL-WAR-4.2 ❌ | — → — ❌ | 0.367 | ❌ | inability statement: no decision delivered |
| `C-2026-04130` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 0.65 | ✅ |  |
| `C-2026-04131` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 0.86 | ✅ |  |
| `C-2026-04132` | serial-boundary | decline → approve ❌ | ADD-IN-2.1 → TSB-C-0051 ❌ | — → ₹198,450 ✅ | 0.26 | ❌ |  |
| `C-2026-04139` | dual-limit | decline → review ❌ | TSB-C-0051 → — ❌ | — → — ❌ | 0.172 | ❌ | echoed the question: no answer delivered |
| `C-2026-04140` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → ₹199,175 ✅ | 0.688 | ✅ |  |
| `C-2026-04141` | dual-limit | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.47 | ✅ |  |
| `C-2026-04148` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹208,735 → ₹208,735 ✅ | 0.744 | ✅ |  |
| `C-2026-04149` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹753,880 → ₹753,880 ✅ | 0.492 | ✅ |  |
| `C-2026-04150` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.833 | ✅ |  |
| `C-2026-04151` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹31,030 → ₹31,030 ✅ | 0.693 | ✅ |  |
| `C-2026-04152` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹197,000 → ₹197,000 ✅ | 0.793 | ✅ |  |
| `C-2026-04153` | valuation | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹72,945 → ₹72,945 ✅ | 0.81 | ✅ |  |
| `C-2026-04166` | stale-deck | approve → approve ✅ | TSB-C-0051 → — ❌ | ₹199,175 → — ❓ | 0.667 | ❌ | no amount stated |
| `C-2026-04167` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.628 | ✅ |  |
| `C-2026-04171` | authority | escalate → review ❌ | ADD-IN-2.1 → — ❌ | — → — ❌ | 0.194 | ❌ | inability statement: no decision delivered |
| `C-2026-04172` | authority | escalate → decline ❌ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹312,000 ✅ | 0.625 | ❌ |  |
| `C-2026-04176` | abstention | request_evidence → request_evidence ✅ | — → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 0.7 | ✅ |  |
| `C-2026-04177` | abstention | request_evidence → request_evidence ✅ | — → TSB-C-0043 ✅ | — → ₹199,175 ✅ | 0.533 | ✅ |  |
| `C-2026-04178` | abstention | request_evidence → request_evidence ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 0.8 | ✅ |  |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
