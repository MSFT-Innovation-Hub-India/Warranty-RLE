# Stages — every step of the climb, kept

Each stage of the hill climb has its own folder holding **exactly** what that
stage used: skills, pinned rubrics, sample prompts, and a README recording the
world's state, the commands, and the results. Nothing is overwritten. To see
what any stage changed, compare its folder with the one before.

| Folder | Stage | The one change | Status |
| --- | --- | --- | --- |
| [stage-0](stage-0/) | Baseline | — (one broad skill, generated rubrics, MCP off, 8 easy prompts) | ✅ **rubric 0.630 · correct 1/8** |
| [stage-1](stage-1/) | Tools | MCP server switched on | ⚠️ **rubric 0.905 · correct 3/8**, two defects found, re-run advised |
| [stage-0-v2](stage-0-v2/) | Baseline, world v2 | — (the world corrected: inspection reports no longer required) | ✅ **rubric 0.535 · correct 0/8** (v1 → v2 move ≈ run-to-run noise) |
| [stage-1-v2](stage-1-v2/) | Tools, world v2 | MCP server switched on (replicas pre-warmed) | ✅ **rubric 0.991 · correct 7/8** · ⚠️ saturated; 04103 is a world ambiguity |
| `stage-2` | Inner loop | Hand-written rubrics first, then 3 thin skills | ⬜ |
| `stage-3` | Honest set | All 30 eval prompts · Simple vs BestOfN | ⬜ |
| `stage-4a-gpt54mini` | RFT | Small model GPT-5.4-Mini: before → tune → after | ⬜ |
| `stage-4b-mai` | RFT, repeated | The same with the MAI pair | ⬜ |

## Rules

1. **Copy forward, then change one thing.** A new stage starts as a copy of the
   previous folder. Only the stage's single variable is edited.
2. **A closed stage is never edited.** Once its results are recorded, the
   folder is frozen. Corrections go into the next stage, or into a dated note
   in that stage's README.
3. **Rubrics are pinned files**, never left to regenerate. Generation isn't
   repeatable (see JOURNEY § 4).
4. **Record the platform IDs** each stage used: skill IDs, sample counts,
   evaluation job IDs. Evaluation jobs stay on the platform, so
   `evaluate compare <job-a> <job-b>` can re-read any two stages.
5. **Report two numbers, every stage:** the platform's **rubric score**, and
   **ground-truth correctness** from `build/score_ground_truth.py` (decision,
   governing instrument and payable against `out/data/claims.json`). If they
   diverge, the rubrics are rewarding the wrong thing.
6. **Tag it in git when a stage closes**: `stage-0`, `stage-1`, … so the whole
   repository can be checked out as it was at that point.

## Replaying the journey

1. Build the world once by following [JOURNEY § 2](../docs/JOURNEY.md#2-setting-up-the-world), P0–P8.
2. Apply the stages in order. Each stage README has an **Apply** block (skills,
   rubrics, samples, tool switches) and a **Run** block.
3. Compare your results with each README's **Results**.

To show someone the progression, step through the folders and their diffs:

```powershell
git diff --no-index stages/stage-1 stages/stage-2      # what stage 2 changed
```
