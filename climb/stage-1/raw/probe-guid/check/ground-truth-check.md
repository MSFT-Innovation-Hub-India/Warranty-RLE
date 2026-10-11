# Ground-truth check — check

Scored by `scripts/score_ground_truth.py` against `world-builder/out/data/claims.json` (the source of GROUND-TRUTH.md).

| Measure | Result |
| --- | --- |
| Answers scored | 1 |
| Decision correct | 0/1 (0%) |
| Governing instrument correct | 0/1 (0%) |
| Payable correct (approvals) | 0/1 (0%) |
| **Fully correct** | **0/1 (0%)** |
| Delivered ≠ stored (not verifiable; finish rejected) | 0 |
| Needs human review (unreadable) | 1 |
| Mean rubric score (platform) | 0.438 |

## By slice

| Slice | Answers | Fully correct | Mean rubric score |
| --- | --- | --- | --- |
| covered-simple | 1 | 0 | 0.438 |

## Per answer

| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `C-2026-04101` | covered-simple | approve → review ❓ | ADD-IN-2.1 → — ❌ | ₹69,575 → — ❓ | 0.438 | ❓ | decision unclear; no amount stated |

❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.
