# Stages — every step of the climb, kept

Each stage of the hill climb has its own folder holding **exactly** what that
stage used: skills, pinned rubrics, sample prompts, and a README recording the
world's state, the commands, and the results. Nothing is overwritten. To see
what any stage changed, compare its folder with the one before.

| Folder | Stage | The one change | Status |
| --- | --- | --- | --- |
| [stage-0](stage-0/) | Baseline | — (one broad skill, generated rubrics, MCP off, 8 easy prompts) | ⏳ prepared, not run |
| `stage-1` | Tools | MCP server switched on | ⬜ |
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
5. **Tag it in git when a stage closes**: `stage-0`, `stage-1`, … so the whole
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
