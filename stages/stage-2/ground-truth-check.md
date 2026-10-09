# Ground-truth check — stage-2

Scored by `scripts/score_ground_truth.py` against `world-builder/out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 29 |
| Decision correct | 17/29 (59%) |
| Governing instrument correct | 17/29 (59%) |
| Payable correct (approvals) | 9/16 (56%) |
| **Fully correct** | **14/29 (48%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 1 |
| Needs human review (unreadable) | 4 |
| Mean rubric score (platform) | 0.526 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| abstention | 3 | 2 | 0.522 |
| authority | 2 | 0 | 0.477 |
| covered-simple | 3 | 2 | 0.672 |
| declined-simple | 2 | 2 | 0.719 |
| dual-limit | 3 | 2 | 0.482 |
| precedence | 5 | 3 | 0.74 |
| serial-boundary | 3 | 1 | 0.253 |
| stale-deck | 2 | 2 | 0.683 |
| valuation | 6 | 0 | 0.333 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹69,575 → ₹69,575 ✅ | 0.85 | ✅ |  |
| `C-2026-04102` | covered-simple | approve → review ❓ | ADD-IN-2.1 → — ❌ | ₹48,420 → — ❓ | 0.317 | ❓ | decision unclear; no amount stated |
| `C-2026-04103` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹19,150 → ₹19,150 ✅ | 0.85 | ✅ |  |
| `C-2026-04109` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.688 | ✅ |  |
| `C-2026-04110` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹14,800 ✅ | 0.75 | ✅ |  |
| `C-2026-04114` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.66 | ✅ |  |
| `C-2026-04115` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹13,050 ❌ | 0.743 | ❌ |  |
| `C-2026-04116` | precedence | decline → decline ✅ | ADD-IN-2.1 → TSB-C-0051 ❌ | — → — ✅ | 0.688 | ❌ |  |
| `C-2026-04117` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.875 | ✅ |  |
| `C-2026-04118` | precedence | approve → approve ✅ | TSB-P-0112 → TSB-P-0112 ✅ | ₹67,500 → ₹67,500 ✅ | 0.733 | ✅ |  |
| `C-2026-04129` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.646 | ✅ |  |
| `C-2026-04131` | serial-boundary | approve → review ❌ | TSB-C-0051 → — ❌ | ₹198,450 → — ❌ | 0.05 | ❌ | echoed the question: no answer delivered; no amount stated |
| `C-2026-04132` | serial-boundary | decline → review ❌ | ADD-IN-2.1 → — ❌ | — → — ❌ | 0.062 | ❌ | echoed the question: no answer delivered |
| `C-2026-04139` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 0.729 | ✅ |  |
| `C-2026-04140` | dual-limit | decline → review ❌ | TSB-C-0051 → TSB-C-0043 ❌ | — → — ❌ | 0.3 | ❌ | inability statement: no decision delivered |
| `C-2026-04141` | dual-limit | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.418 | ✅ |  |
| `C-2026-04148` | valuation | approve → review ❌ | TSB-C-0051 → — ❌ | ₹208,735 → — ❌ | 0.194 | ❌ | echoed the question: no answer delivered; no amount stated |
| `C-2026-04149` | valuation | approve → review ❌ | TSB-C-0051 → — ❌ | ₹753,880 → — ❌ | 0.264 | ❌ | inability statement: no decision delivered; no amount stated |
| `C-2026-04150` | valuation | approve → review ❓ | TSB-C-0051 → — ❌ | ₹755,050 → ₹755,050 ✅ | 0.433 | ❓ | decision unclear |
| `C-2026-04151` | valuation | approve → review ❓ | TSB-C-0051 → TSB-C-0051 ✅ | ₹31,030 → ₹31,030 ✅ | 0.661 | ❓ | decision unclear |
| `C-2026-04152` | valuation | approve → review ❌ | TSB-C-0051 → — ❌ | ₹197,000 → — ❌ | 0.264 | ❌ | inability statement: no decision delivered; no amount stated |
| `C-2026-04153` | valuation | approve → review ❌ | ADD-IN-2.1 → — ❌ | ₹72,945 → — ❌ | 0.183 | ❌ | inability statement: no decision delivered; no amount stated |
| `C-2026-04166` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.623 | ✅ |  |
| `C-2026-04167` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.743 | ✅ |  |
| `C-2026-04171` | authority | escalate → review ❌ | ADD-IN-2.1 → — ❌ | — → — ❌ | 0.183 | ❓ | NOT VERIFIABLE: grader says the delivered answer differs from the stored one (finish rejected); echoed the question: no answer delivered |
| `C-2026-04172` | authority | escalate → decline ❌ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.771 | ❌ |  |
| `C-2026-04176` | abstention | request_evidence → request_evidence ✅ | — → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04177` | abstention | request_evidence → request_evidence ✅ | — → — ✅ | — → — ✅ | 0.317 | ✅ |  |
| `C-2026-04178` | abstention | request_evidence → request_evidence ✅ | ADD-IN-2.1 → TSB-C-0051 ❌ | — → ₹191,200 ✅ | 0.25 | ❌ |  |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
