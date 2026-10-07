# Stages: the climb

One folder per stage, holding **the latest configuration of that stage**: skills, pinned rubrics, prompts, the commands to apply and run it, the result, and a short **Findings** table (issue → what we did). Superseded runs and experiments are kept in [archive/](../archive/README.md).

| Stage | The change | Model | Rubric | Correct | Status |
| --- | --- | --- | --- | --- | --- |
| [0 · Baseline](stage-0/README.md) | Starting point: one skill, generated rubrics, claim system **off**, 8 easy prompts | GPT-5.6-Sol | 0.535 | 0/8 | ✅ |
| [1 · Claim system](stage-1/README.md) | MCP server **on** | GPT-5.6-Sol | 0.991 | 7/8 | ✅ ⚠️ saturated |
| [2 · All 30 prompts](stage-2/README.md) | 8 → 30 evaluation prompts (every trap slice) | GPT-5.6-Sol | 0.978 | 27/30 | ✅ ⚠️ no frontier headroom |
| [3 · Small model, split skill](stage-3/README.md) | Model → MAI-CODE-5b; research split into its own skill; folder-scoped search | MAI-CODE-5b | – | – | ⬜ ready to run |
| 4 · Hand-written rubrics | Rubrics v2 ([draft](rubrics-v2-draft.md)) for both skills | MAI-CODE-5b | | | ⬜ |
| 5 · Headroom | `Simple` vs `BestOfN` on the same model: is there anything for tuning to capture? | MAI-CODE-5b | | | ⬜ |
| 6 · RFT | Tune `mai-code-1-flash`; compare before and after, and against GPT-5.6-Sol | MAI | | | ⬜ |

**World versions** (the corpus and claim system; ground truth from `build/adjudicate.py`):

| Version | Change |
| --- | --- |
| v2 | Inspection reports no longer required (documents now agree with the answer key) |
| v2.1 | Policy 5.4: a consumable under a warranty repair code is a corrective repair |
| v2.2 | Answer key tests the time limit before missing hours; no eval/train twin claims |
| v2.3 | Repair-warranty prior claims seeded as `Paid`; no dangling claim references |

## Rules
1. **Change one thing per stage**, or say plainly when two must move together (stage 3).
2. **A stage folder holds its latest configuration.** If a stage is re-run after a fix, the folder is updated and the superseded run moves to `archive/`. The fix goes in the stage's Findings as one line.
3. **Rubrics are pinned files**, never left to regenerate.
4. **Report two numbers, every stage**: the platform's rubric score and ground-truth correctness (`build/score_ground_truth.py`). From stage 3, also the hand-in rejection rate.
5. **Record the platform IDs** (skills, evaluation jobs), so `evaluate compare` can re-read any two stages.
6. **Tag a closed stage in git**: `stage-0`, `stage-1`, …

## Replaying the climb
Build the world once ([JOURNEY § 2](../docs/JOURNEY.md#2-setting-up-the-world)), then apply each stage's **Apply and run** block in order and compare with its **Result**.
