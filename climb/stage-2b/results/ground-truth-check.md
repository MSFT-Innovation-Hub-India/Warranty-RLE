# Ground-truth check — Stage 2b probes (4 deliberately wrong)

Scored by `scripts/score_ground_truth.py` against `world-builder/out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 7 |
| Decision correct | 5/7 (71%) |
| Governing instrument correct | 7/7 (100%) |
| Payable correct (approvals) | 3/5 (60%) |
| **Fully correct** | **3/7 (43%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 0 |
| Needs human review (unreadable) | 0 |
| Mean rubric score (platform) | 0.908 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| authority | 2 | 0 | 0.933 |
| dual-limit | 1 | 1 | 0.783 |
| precedence | 1 | 1 | 1.0 |
| stale-deck | 1 | 1 | 1.0 |
| valuation | 2 | 0 | 0.853 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04119` | precedence | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → — ✅ | 1.0 | ✅ |  |
| `C-2026-04144` | dual-limit | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹199,175 → ₹199,175 ✅ | 0.783 | ✅ |  |
| `C-2026-04157` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹31,030 → ₹29,455 ❌ | 0.853 | ❌ |  |
| `C-2026-04163` | valuation | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹31,030 → ₹29,455 ❌ | 0.853 | ❌ |  |
| `C-2026-04170` | stale-deck | approve → approve ✅ | TSB-C-0051 → TSB-C-0051 ✅ | ₹29,725 → ₹29,725 ✅ | 1.0 | ✅ |  |
| `C-2026-04173` | authority | escalate → decline ❌ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → ₹18,400 ✅ | 1.0 | ❌ |  |
| `C-2026-04174` | authority | escalate → decline ❌ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | — → — ✅ | 0.867 | ❌ |  |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
