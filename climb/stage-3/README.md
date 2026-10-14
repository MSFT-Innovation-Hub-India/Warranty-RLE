# Stage 3: skill, record the draft

**Status:** 🔄 running (2026-10-14)
**Result in one line:** <to come>

## Goal

Sol records nothing in the claim system on about a quarter of claim questions (17 of 59 in stage 1, 14 of 60 in stage 2), mostly prompts like "What's the position on…" or "…and advise", which it treats as advice only. Under business rule A (user, 2026-10-13), any question about a specific claim's outcome should end with the matching draft recorded. The rubrics already enforce this (stage 2); this stage tries to teach it through the skill.

## What changed

| | Stage 2 | This stage |
| --- | --- | --- |
| Skill, one line | "where the outcome calls for an action in the claim system, record it there as a draft and say what you recorded" | "**whenever you are asked about a specific claim, however the question is put, finish by recording the matching draft in the claim system** (an adjudication, an evidence request or a goodwill escalation) and say what you recorded; **a question only about an asset's warranty position needs no draft**" |

Everything else is unchanged: model (GPT-5.6-Sol), the 60 Training claims, route (`executions run`), world. Configuration: [config/](config/).

⚠️ **Rubrics are stage 2b's**, which differ from stage 2's only in skipping Valuation on asset-only questions. That can change the rubric score of the 3 asset-only claims, not whether a draft was recorded, which is what this stage measures.

**How the skill and rubrics were made** ([history](../../docs/04-hill-climb-method.md#6-where-the-skill-and-rubrics-came-from)):

| | Made how | From |
| --- | --- | --- |
| Skill | **By hand**, one line edited | Stage 2's skill; the recording line rewritten from stage 1–2's evidence. `check-skill.py`: no rubric phrase, no claim-specific answer. Applied with `skills update --prompt` |
| Rubrics | By hand, carried over | Stage 2b |

## How the run went

| | |
| --- | --- |
| When | 2026-10-14, from 11:18 IST |
| Run | `executions run`, 5 claims at a time |

Step-by-step commands and responses: [RUNBOOK.md](RUNBOOK.md).

## Results

<to come>

## Findings

<to come>

## Conclusion

<to come>

## Next

<to come>
