# Stage 0: frontier reference (GPT-5.6-Sol)

**Status:** ⬜ planned, not yet run
**Result in one line:** —

## Goal

Find out what this world allows with the current skill and rubrics, using the strongest model available. That gives the climb its **ceiling**: the small model is measured against what is achievable, not against 30/30. It also flags claims that even the frontier model gets wrong. Those point to a problem in the world, the answer key or the skill, and they get fixed before the small model is measured.

Why first: attempt 1 never measured GPT-5.6-Sol on world v3, so its stalls could not be told apart from an unfair task ([archive](../../archive/attempt-1/README.md)).

## What changed

| | Attempt 1, stage 1 (the best measured configuration) | This stage |
| --- | --- | --- |
| Model | MAI-CODE-5b `dev-ct-mai-code-mp` | **GPT-5.6-Sol `prod-gpt-56-reasoning-sol`** |

Unchanged: the business-brief skill ([config/skill.md](config/skill.md)), the six hand-written rubrics ([config/rubrics.md](config/rubrics.md)), the 30 evaluation prompts and their existing sample IDs ([config/eval-sample-ids.json](config/eval-sample-ids.json)), strategy `Simple`, world v3. All 30 claims are run, including C-2026-04130 (excluded in attempt 1 only to stop waiting).

## Plan

| Step | What | Cost |
| --- | --- | --- |
| 1 | Pre-flight ([docs/05](../../docs/05-operations.md#before-every-run)): SQL on, `/healthz` ok, baseline `0 0 0 0`, live skill and rubrics match `config/`, **no other job active** | Free |
| 2 | 1-claim smoke run (C-2026-04101) to confirm the model ID is accepted and the answer is graded | 1 job |
| 3 | The 30 claims, batches of 5: `eval-batches.ps1 -Model prod-gpt-56-reasoning-sol` | 6 jobs · 💭 ~2.5–3 h |
| 4 | Score, hand-check every ❓/❌, write this README | Free |

## Gate

| Outcome | Then |
| --- | --- |
| Sol correct on **≥ 26/30** | The world is fair; go to stage 1 |
| Sol wrong on a claim | Investigate that claim (answer key, documents, skill wording) before stage 1. A claim Sol can't solve with this skill is not a test of the small model |
| Sol ≥ 0.95 rubric and 30/30 | Fine for a ceiling; the headroom question is about MAI, not Sol |
| Rubric score ranks a wrong Sol answer above a right one | Note it for stage 2 (reward alignment) |

📄 For reference, on world v2 GPT-5.6-Sol scored 0.978 and 27/30. World v3 has different tools, so that is not a prediction.

## How the run went

—

## Results

| Measure | MAI-CODE-5b (attempt 1, stage 1) | GPT-5.6-Sol (this stage) |
| --- | --- | --- |
| Rubric score | 0.637 | |
| Correct | 23/30 | /30 |
| Hand-in failures | 5 (1 echo, 2 stubs, 2 "can't access") | |
| Calls per claim (median) | 14 (matched 29 claims) | |

## Findings

| Issue | What we did |
| --- | --- |

## Conclusion

—

## Next

[Stage 1](../README.md): MAI-CODE-5b on the same configuration, each claim three times.
