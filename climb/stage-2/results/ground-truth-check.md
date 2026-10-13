# Ground-truth check — Stage 2: GPT-5.6-Sol, 60 Training claims, revised Authority and Valuation rubrics

Scored by `scripts/score_ground_truth.py` against `world-builder/out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 60 |
| Decision correct | 59/60 (98%) |
| Governing instrument correct | 60/60 (100%) |
| Payable correct (approvals) | 34/35 (97%) |
| **Fully correct** | **59/60 (98%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 0 |
| Needs human review (unreadable) | 0 |
| Mean rubric score (platform) | 0.94 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| abstention | 6 | 6 | 0.965 |
| authority | 3 | 3 | 0.959 |
| covered-simple | 5 | 5 | 0.975 |
| declined-simple | 3 | 3 | 1.0 |
| dual-limit | 6 | 5 | 0.868 |
| exclusion | 4 | 4 | 0.952 |
| precedence | 10 | 10 | 0.944 |
| repair-warranty | 2 | 2 | 0.979 |
| serial-boundary | 6 | 6 | 0.979 |
| stale-deck | 3 | 3 | 0.954 |
| valuation | 12 | 12 | 0.891 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04104` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹29,725 → ₹29,725 ✅ | 1.0 | ✅ |  |
| `C-2026-04105` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹104,220 → ₹104,220 ✅ | 0.875 | ✅ |  |
| `C-2026-04106` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹26,875 → ₹26,875 ✅ | 1.0 | ✅ |  |
| `C-2026-04107` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹224,375 → ₹224,375 ✅ | 1.0 | ✅ |  |
| `C-2026-04108` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹2,900 → ₹2,900 ✅ | 1.0 | ✅ |  |
| `C-2026-04111` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04112` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹105,000 ✅ | 1.0 | ✅ |  |
| `C-2026-04113` | declined-simple | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04119` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → — ✅ | 0.75 | ✅ |  |
| `C-2026-04120` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 1.0 | ✅ |  |
| `C-2026-04121` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.875 | ✅ |  |
| `C-2026-04122` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04123` | precedence | approve → approve ✅ | TSB-P-0112 → TSB-P-0112 ✅ | ₹67,500 → ₹67,500 ✅ | 1.0 | ✅ |  |
| `C-2026-04124` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.917 | ✅ |  |
| `C-2026-04125` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.958 | ✅ |  |
| `C-2026-04126` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.938 | ✅ |  |
| `C-2026-04127` | precedence | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04128` | precedence | approve → approve ✅ | TSB-P-0112 → TSB-P-0112 ✅ | ₹67,500 → ₹67,500 ✅ | 1.0 | ✅ |  |
| `C-2026-04133` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04134` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 1.0 | ✅ |  |
| `C-2026-04135` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 1.0 | ✅ |  |
| `C-2026-04136` | serial-boundary | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹198,450 → ₹198,450 ✅ | 1.0 | ✅ |  |
| `C-2026-04137` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.875 | ✅ |  |
| `C-2026-04138` | serial-boundary | decline → decline ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04142` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04143` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04144` | dual-limit | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → — ✅ | 0.889 | ✅ |  |
| `C-2026-04145` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 0.9 | ✅ |  |
| `C-2026-04146` | dual-limit | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → ₹199,175 ✅ | 0.542 | ✅ |  |
| `C-2026-04147` | dual-limit | approve → request_evidence ❌ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹400,000 ❌ | 0.875 | ❌ | request evidence given, so payable not assessed |
| `C-2026-04154` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹208,735 → ₹208,735 ✅ | 1.0 | ✅ |  |
| `C-2026-04155` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹753,880 → ₹753,880 ✅ | 0.958 | ✅ |  |
| `C-2026-04156` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 1.0 | ✅ |  |
| `C-2026-04157` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹31,030 → ₹31,030 ✅ | 0.883 | ✅ |  |
| `C-2026-04158` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹197,000 → ₹197,000 ✅ | 1.0 | ✅ |  |
| `C-2026-04159` | valuation | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹72,945 → ₹72,945 ✅ | 0.833 | ✅ |  |
| `C-2026-04160` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹208,735 → ₹208,735 ✅ | 0.893 | ✅ |  |
| `C-2026-04161` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹753,880 → ₹753,880 ✅ | 0.9 | ✅ |  |
| `C-2026-04162` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.883 | ✅ |  |
| `C-2026-04163` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹31,030 → ₹31,030 ✅ | 0.833 | ✅ |  |
| `C-2026-04164` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹197,000 → ₹197,000 ✅ | 0.583 | ✅ |  |
| `C-2026-04165` | valuation | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹72,945 → ₹72,945 ✅ | 0.925 | ✅ |  |
| `C-2026-04168` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04169` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹755,050 → ₹755,050 ✅ | 0.944 | ✅ |  |
| `C-2026-04170` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹29,725 → — ✅ | 0.917 | ✅ |  |
| `C-2026-04173` | authority | escalate → escalate ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.938 | ✅ |  |
| `C-2026-04174` | authority | escalate → escalate ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 1.0 | ✅ |  |
| `C-2026-04175` | authority | escalate → escalate ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.938 | ✅ |  |
| `C-2026-04179` | abstention | request_evidence → request_evidence ✅ | — → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 0.95 | ✅ |  |
| `C-2026-04180` | abstention | request_evidence → request_evidence ✅ | — → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04181` | abstention | request_evidence → request_evidence ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04182` | abstention | request_evidence → request_evidence ✅ | — → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 0.958 | ✅ |  |
| `C-2026-04183` | abstention | request_evidence → request_evidence ✅ | — → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 0.883 | ✅ |  |
| `C-2026-04184` | abstention | request_evidence → request_evidence ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04185` | exclusion | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.933 | ✅ |  |
| `C-2026-04186` | exclusion | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 0.938 | ✅ |  |
| `C-2026-04187` | exclusion | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 1.0 | ✅ |  |
| `C-2026-04188` | exclusion | decline → decline ✅ | TSB-C-0051 → TSB-C-0051 ✅ | — → — ✅ | 0.938 | ✅ |  |
| `C-2026-04189` | repair-warranty | approve → approve ✅ | POL-WAR-4.2 6.1 → POL-WAR-4.2 6.1 ✅ | ₹69,575 → ₹69,575 ✅ | 0.958 | ✅ |  |
| `C-2026-04190` | repair-warranty | approve → approve ✅ | POL-WAR-4.2 6.1 → POL-WAR-4.2 6.1 ✅ | ₹69,575 → ₹69,575 ✅ | 1.0 | ✅ |  |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
