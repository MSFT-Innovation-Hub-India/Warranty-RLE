# Stage 0: frontier reference (GPT-5.6-Sol)

**Status:** ✅ closed 2026-10-11
**Result in one line:** GPT-5.6-Sol gets **29/30** claims fully right (rubric **0.956**), so the world is fair and solvable with the current skill. The one miss also shows the rubrics can't see a wrong payable.

## Goal

Find out what this world allows with the current skill and rubrics, using the strongest model available. That gives the climb its **ceiling**: the small model is measured against what is achievable, not against 30/30. It also flags claims that even the frontier model gets wrong, which would point to a problem in the world, the answer key or the skill.

Why first: attempt 1 never measured GPT-5.6-Sol on world v3, so its stalls couldn't be told apart from an unfair task ([archive](../../archive/attempt-1/README.md)).

## What changed

| | Attempt 1, stage 1 (best measured configuration) | This stage |
| --- | --- | --- |
| Model | MAI-CODE-5b `dev-ct-mai-code-mp` | **GPT-5.6-Sol `prod-gpt-56-reasoning-sol`** |

Unchanged: the business-brief skill ([config/skill.md](config/skill.md)), the six hand-written rubrics ([config/rubrics.md](config/rubrics.md)), the 30 evaluation prompts and their sample IDs ([config/eval-sample-ids.json](config/eval-sample-ids.json)), strategy `Simple`, world v3. All 30 claims were run, including C-2026-04130.

## How the run went

| | |
| --- | --- |
| When | 2026-10-11, 07:14–09:19 IST (pre-flight to close) |
| Jobs | 1 smoke job (1 claim) + 6 jobs (29 claims). Every job finished in 14 min: no stalls, no retries |
| Before the run | The claim database held 19 drafts written outside the climb (a Foundry agent on 10-09), so it was fully **re-seeded**. All six rubrics were found **disabled** (likely by the cancelled tuning job) and the first submission was refused. Re-enabled, content unchanged ([P9](../../docs/06-platform-issues.md#p9-rubrics-found-disabled-evaluation-refused-er07018)) |
| Tooling fixed on the way | `sql-run.ps1` couldn't pass the 432 KB seed; the runner stopped when a log watcher locked its file (the job carried on and was adopted); the scorer misread Sol's table-row totals; the summariser counted not-applicable rubrics as 0. All fixed and re-tested; attempt 1's results rescore unchanged |

Every command and response, in order: [RUNBOOK.md](RUNBOOK.md).

## Results

| Measure | MAI-CODE-5b (attempt 1, stage 1) | **GPT-5.6-Sol (this stage)** |
| --- | --- | --- |
| Rubric score | 0.637 | **0.956** |
| Correct: decision + instrument + payable | 23/30 | **29/30** (hand-checked; scorer alone 26/30) |
| Hand-in failures | 5 (1 echo, 2 stubs, 2 "can't access") | **0** |
| Calls per claim | median 14 (matched 29 claims) | mean 13.7 (range 7–27) |
| Authority (escalate goodwill) | 0/2 | **2/2** |

**By claim type (correct):** covered-simple 3/3 · declined-simple 2/2 · precedence 5/5 · serial-boundary 4/4 · dual-limit 3/3 · stale-deck 2/2 · authority 2/2 · abstention 3/3 · **valuation 5/6**.

**By rubric (mean where it applies):** Coverage 1.00 · Precedence 0.90 · Grounding 0.98 · Valuation 0.92 (17 approvals) · Authority and action 0.98 · Gaps 0.90 (10 claims).

**Reward check:** the one wrong answer scored **0.96**, higher than 15 of the 29 right answers.

Detail: [results/ground-truth-check.md](results/ground-truth-check.md) (scorer) · [results/hand-check.md](results/hand-check.md) (every ❓/❌ read by hand) · [results/run-summary.md](results/run-summary.md) (per claim).

## Findings

| Issue | What we did |
| --- | --- |
| **The world is solvable with this skill.** Sol handled every trap type except one: precedence, document over stale index, dual limits, stale deck, missing records, and goodwill escalation | Gate passed (≥ 26/30). The ceiling for MAI is 29/30 |
| **Authority is a small-model problem, not a skill problem.** MAI declined both goodwill claims in every attempt-1 stage. Sol escalated both, to the right tier, and recorded the escalation | For stage 1: if MAI never escalates across 3 runs, this is a "never right" behaviour, so the lever is the skill, not RFT |
| **One real error, C-2026-04151: supersession.** Sol priced the fitted part at its own list price (₹24,600) and explicitly chose not to use the superseding part's price (₹26,100), against policy §4.2. ₹29,455 instead of ₹31,030 | Recorded as the world's hardest valuation trap. Kept as is: it's a fair test, and Sol's reasoning shows it read the rule and misapplied it |
| **The reward can't see a wrong payable.** 04151 scored 0.96: the Valuation checklist asks the answer to *name* any supersession, which Sol did, not to *apply* it | Candidate fix for stage 2 (reward alignment): a checklist item or red flag on pricing the superseding part. During RFT, today's rubric would reward this mistake |
| Scorer misread 3 correct answers (04153 names a bulletin in order to rule it out; 04172 and 04176 phrase the decision in ways the patterns don't read) | Hand-checked. To improve before stage 1, since MAI will run 90 claims |
| Database touched outside the climb (19 drafts from a Foundry agent) | Full re-seed added to the pre-flight; new `db-table-counts.sql` and `check-live-config.py` make it a two-command check |

## Conclusion

The question is answered: **with the current skill and rubrics, the world allows 29/30, and the rubric mean at that level is 0.956.** MAI-CODE-5b's attempt-1 result (23/30, 0.637) leaves a gap of 6 claims and 0.32 rubric points to close. Authority, MAI's most consistent failure, is achievable with today's skill. The rubrics are good enough to measure, but not yet to be the RFT reward: a wrong valuation scored as well as the right ones.

## Next

[Stage 1](../README.md): MAI-CODE-5b on exactly this configuration, each claim run 3 times (attempt 1's stage 1 run counts as one), to measure floor, reach and variance per claim. Before it starts: make the scorer read the three phrasings it missed here, so the 90 answers need less hand-checking.
