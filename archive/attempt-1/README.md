# Attempt 1: the first climb on world v3 (2026-10-07 → 10-10)

Read-only record. Links inside these files point at their old locations (`stages/`, `docs/evidence/`) and may be broken; the files themselves are here. The full original narrative is [JOURNEY.md](JOURNEY.md); the verbatim record is [evidence/](evidence/README.md).

**Model:** MAI-CODE-5b throughout. GPT-5.6-Sol was never measured on world v3.

## The stages in brief

| Stage | Goal | What happened | Result | Conclusion |
| --- | --- | --- | --- | --- |
| [0 · Naive baseline](stages/stage-0/README.md) | Where does a small model start with a business-brief skill and platform-generated rubrics? | 30 claims ran cleanly in batches of 5 | 🖥️ rubric **0.744** · **23/30** | Real headroom. But the generated rubrics overrated: two wrong authority answers scored 0.85 and 1.0 |
| [1 · Hand-written rubrics](stages/stage-1/README.md) | Make the rubric score follow correctness, since it becomes the RFT reward | One aborted batch (a rubric scored a correct decline 0.0, fixed); 3 claims stalled on the platform | 🖥️ **0.637** · **23/30** · right ranked above wrong 93% (was 83%) | ✅ Worked: the reward now tracks correctness better. Weakest rubric: authority and action (0.46) |
| [2 · Skill refinement](stages/stage-2/README.md) | Raise correctness by improving the skill | `skills enrich`: no change. `skills refine`: copied rubric wording into the skill, rejected. Our guidance (2b: method + folder map + hand-in rules, together) measured | 🖥️ **0.526** · **17/29** vs 22/29 matched | ❌ Regression. Three changes at once, so the cause can't be isolated |
| [3 · Headroom](stages/stage-3/README.md) | `Simple` vs `BestOfN` (N=4): is there anything for RFT to learn? | 1-claim probe worked (0.900, correct). The full batch failed on the platform before any claim ran; cancelled | Not measured | ⛔ Gate not passed |
| [4 · RFT pilot](stages/stage-4/README.md) | Exploratory tuning of `mai-code-1-flash`, gate waived by the user | Job `c77feaed` submitted 2026-10-09. The training step failed 6 times with `400` (retried each time), once reaching step 1 (reward 0.358). Claim-system tools apparently missing from training rollouts 🔬 | No model | ⛔ See [P6, P7](../../docs/06-platform-issues.md) |

## Why it stalled

| Issue | What attempt 2 does differently |
| --- | --- |
| No frontier ceiling on world v3, so "MAI is weak" couldn't be told apart from "the task is unfair" | Stage 0 measures GPT-5.6-Sol first |
| Single runs per stage; a 5-claim drop couldn't be separated from noise | Stage 1 runs every claim 3 times |
| Stage 2 bundled three skill changes | One skill fix per sub-stage, kept only if it helps |
| `skills refine` (CLI 0.3.17, no `--mode`) rewrote the skill using the rubrics | Use `--mode instruction` (CLI ≥ 1.0) or hand edits; always run `check-skill.py` |
| Headroom via `BestOfN`, which hides the losing candidates and failed at scale | Headroom from our own repeated `Simple` runs, with every answer visible |
| Authority 0/2 in every stage, wrong answer still scored 0.63–0.77 | Classified as systematic: a skill or red-flag fix, not RFT |
| RFT started without headroom, and training ran without the claim-system tools | RFT only after stages 0–3, and after P7 is resolved |
| Platform stalls, timeouts and a daily SQL lockout consumed most of the time | Pre-flight checklist and platform-issue log ([docs/05](../../docs/05-operations.md), [docs/06](../../docs/06-platform-issues.md)) |

## What carries forward

| Kept | Where it is now |
| --- | --- |
| The business-brief skill and the six hand-written rubrics | [climb/stage-0/config/](../../climb/stage-0/config/) |
| The 30 Evaluation and 60 Training samples and their IDs | Same folder |
| Stage 1's per-claim answers (MAI-CODE-5b, one run) | [stages/stage-1/eval-results-samples.json](stages/stage-1/eval-results-samples.json): can count as one of stage 1's three runs in attempt 2, since the configuration is identical |
| Batches of 5 · stall handling · ground-truth scorer · DB reset | [scripts/](../../scripts/README.md) |
