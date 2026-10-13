# Stage 2: reward alignment (rubrics only)

**Status:** 🔄 running (2026-10-13)
**Result in one line:** <to come>

## Goal

Make the rubric score prefer right answers over wrong ones, whichever model wrote them. In fine-tuning the rubric score is the reward, so a rubric that gives a wrong answer full marks would teach the wrong behaviour. Stage 1 found two such gaps: the Authority rubric gave an unescalated goodwill request 1.00 while marking down right answers that had no action to take, and the Valuation rubric couldn't tell a superseded part priced wrongly (stage 0).

## What changed

| | Stage 1 | This stage |
| --- | --- | --- |
| Rubrics | The six hand-written rubrics | Same six, with **Authority and action** (items 1, 2, 4) and **Valuation accuracy** (item 3) revised ([config/rubrics.md](config/rubrics.md#stage-2-changes-2026-10-13)) |

Everything else is unchanged: model (GPT-5.6-Sol), skill, the 60 Training claims, strategy (`Simple`), route (`executions run`), world. Configuration: [config/](config/).

**How the skill and rubrics were made** ([history](../../docs/04-hill-climb-method.md#6-where-the-skill-and-rubrics-came-from)):

| | Made how | From |
| --- | --- | --- |
| Skill | By hand, carried over | Stage 1, unchanged. `check-skill.py`: no 5-word phrase shared with the new rubrics |
| Rubrics | **By hand**, edited | Stage 1's six; two edited against stage 1's misrankings and stage 0's 04151. Applied with `rubrics update --checklist-item`; the other four verified unchanged |

**Business rule assumed (option A, user's go-ahead 2026-10-13):** any question about a specific claim's outcome, however phrased, should end with the matching draft recorded in the claim system; only questions about an asset's warranty position need no action.

**Not done as planned:** red flags for the authority and supersession cases. CLI 1.x can't set red flags, so both rules are written into checklist items.

## How the run went

| | |
| --- | --- |
| When | 2026-10-13, from 17:55 IST |
| Run | `executions run`, 5 claims at a time, as stage 1 |

Step-by-step commands and responses: [RUNBOOK.md](RUNBOOK.md).

## Results

<to come>

## Findings

<to come>

## Conclusion

<to come>

## Next

<to come>
