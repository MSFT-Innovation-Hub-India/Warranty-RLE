# Ground-truth check — stage-0

Scored by `scripts/score_ground_truth.py` against `world-builder/out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 30 |
| Decision correct | 23/30 (77%) |
| Governing instrument correct | 24/30 (80%) |
| Payable correct (approvals) | 14/17 (82%) |
| **Fully correct** | **23/30 (77%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 0 |
| Needs human review (unreadable) | 0 |
| Mean rubric score (platform) | 0.744 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| abstention | 3 | 2 | 0.726 |
| authority | 2 | 0 | 0.924 |
| covered-simple | 3 | 3 | 0.899 |
| declined-simple | 2 | 2 | 0.892 |
| dual-limit | 3 | 1 | 0.262 |
| precedence | 5 | 4 | 0.768 |
| serial-boundary | 4 | 4 | 0.948 |
| stale-deck | 2 | 1 | 0.555 |
| valuation | 6 | 6 | 0.715 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹69,575 → ₹69,575 ✅ | 1.0 | ✅ |  |
| `C-2026-04102` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹48,420 → ₹48,420 ✅ | 0.83 | ✅ |  |
| `C-2026-04103` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹19,150 → ₹19,150 ✅ | 0.868 | ✅ |  |
| `C-2026-04109` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.967 | ✅ |  |
| `C-2026-04110` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.817 | ✅ |  |
| `C-2026-04114` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.887 | ✅ |  |
| `C-2026-04115` | precedence | approve → review ❌ | TSB-C-0051 → — ❌ | ₹755,050 → — ❌ | 0.156 | ❌ | echoed the question: no answer delivered; no amount stated |
| `C-2026-04116` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04117` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.967 | ✅ |  |
| `C-2026-04118` | precedence | approve → approve ✅ | TSB-P-0112 → TSB-P-0112 ✅ | ₹67,500 → ₹67,500 ✅ | 0.831 | ✅ |  |
| `C-2026-04129` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04130` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 0.88 | ✅ |  |
| `C-2026-04131` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 0.944 | ✅ |  |
| `C-2026-04132` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.967 | ✅ |  |
| `C-2026-04139` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 0.514 | ✅ |  |
| `C-2026-04140` | dual-limit | decline → review ❌ | TSB-C-0051 → — ❌ | — → — ❌ | 0.062 | ❌ | echoed the question: no answer delivered |
| `C-2026-04141` | dual-limit | approve → review ❌ | TSB-C-0051 → — ❌ | ₹199,175 → — ❌ | 0.21 | ❌ | inability statement: no decision delivered; no amount stated |
| `C-2026-04148` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹208,735 → ₹208,735 ✅ | 0.798 | ✅ |  |
| `C-2026-04149` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹753,880 → ₹753,880 ✅ | 0.519 | ✅ |  |
| `C-2026-04150` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.92 | ✅ |  |
| `C-2026-04151` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹31,030 → ₹31,030 ✅ | 0.53 | ✅ |  |
| `C-2026-04152` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹197,000 → ₹197,000 ✅ | 0.598 | ✅ |  |
| `C-2026-04153` | valuation | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹72,945 → ₹72,945 ✅ | 0.927 | ✅ |  |
| `C-2026-04166` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04167` | stale-deck | approve → review ❌ | TSB-C-0051 → — ❌ | ₹755,050 → — ❌ | 0.111 | ❌ | echoed the question: no answer delivered; no amount stated |
| `C-2026-04171` | authority | escalate → decline ❌ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.849 | ❌ |  |
| `C-2026-04172` | authority | escalate → decline ❌ | ADD-IN-2.1 → TSB-C-0051 ❌ | — → — ✅ | 1.0 | ❌ |  |
| `C-2026-04176` | abstention | request_evidence → review ❌ | — → — ❌ | — → — ❌ | 0.178 | ❌ | echoed the question: no answer delivered |
| `C-2026-04177` | abstention | request_evidence → request_evidence ✅ | — → POL-WAR-4.2 ✅ | — → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04178` | abstention | request_evidence → request_evidence ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 1.0 | ✅ |  |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
