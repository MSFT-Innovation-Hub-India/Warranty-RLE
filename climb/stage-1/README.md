# Stage 1: broaden the evidence (GPT-5.6-Sol on the Training claims)

**Status:** 🔄 running (2026-10-13)
**Result in one line:** <to come>

## Goal

Find where the skill and the rubrics fall short, without touching the 30 Evaluation claims. Sol got 29 of those 30 right in stage 0, so they show little to fix, and they must stay held out. The 60 Training claims are the ones refinement is allowed to use. This stage measures them, changes nothing, and produces the evidence stages 2 (rubrics) and 3 (skill) work from.

## What changed

| | Stage 0 | This stage |
| --- | --- | --- |
| Claims | 30 Evaluation claims | **60 Training claims** ([config/training-sample-ids.json](config/training-sample-ids.json)) |

Everything else is unchanged: model (GPT-5.6-Sol), skill, rubrics, strategy (`Simple`), world, route (evaluation jobs). Configuration: [config/](config/), identical to stage 0's.

**How the skill and rubrics were made** ([history](../../docs/04-hill-climb-method.md#6-where-the-skill-and-rubrics-came-from)):

| | Made how | From |
| --- | --- | --- |
| Skill | By hand, carried over | Stage 0 (attempt 1's business brief) |
| Rubrics | By hand, carried over | Stage 0 (the six hand-designed rubrics) |

## How the run went

| | |
| --- | --- |
| When | 2026-10-13, from 15:05 IST |
| Jobs | 6 evaluation jobs of 10 claims |
| Before the run | MAI-CODE-5b had been selected during the stage 4 attempts; deselected so only Sol is selected, as in stage 0 |

Step-by-step commands and responses: [RUNBOOK.md](RUNBOOK.md).

## Results

<to come>

## Findings

<to come>

## Conclusion

<to come>

## Next

<to come>
