# Stage 0: baseline with GPT-5.6-Sol

**Status:** ✅ closed 2026-10-11
**Result in one line:** GPT-5.6-Sol gets **29 of 30 claims right**, checked against the answer key, with a platform rubric score of **0.956**. The one wrong answer still scored 0.96 on the rubrics.

## Goal

Establish the baseline for this use case: how well the strongest available model adjudicates the 30 evaluation claims with the current skill and rubrics. Every later stage is read against this result.

## Configuration

| | |
| --- | --- |
| Model | GPT-5.6-Sol (`prod-gpt-56-reasoning-sol`) |
| Strategy | `Simple`: one attempt per claim |
| Skill | Business brief: what to establish, which sources exist, how to write ([config/skill.md](config/skill.md)) |
| Rubrics | Six hand-written rubrics ([config/rubrics.md](config/rubrics.md)) |
| Claims | All 30 evaluation claims ([config/eval-sample-ids.json](config/eval-sample-ids.json)) |
| World | v3, environment `wce-main`, claim database freshly re-seeded |

**How the skill and rubrics were made** ([history](../../docs/04-hill-climb-method.md#6-where-the-skill-and-rubrics-came-from)):

| | Made how | From |
| --- | --- | --- |
| Skill | By hand, carried over | Attempt 1's business brief, written 2026-10-03 without the trap rules. Same text, description restored |
| Rubrics | By hand, carried over | The six designed before the skill existed (world-builder 03 § 9.2), revised against attempt 1 stage 0's answers. Identical to attempt 1 stage 1 |

### How the six rubrics came to be

| Step | What happened | Result |
| --- | --- | --- |
| 1. Generated from the skill | Attempt 1, stage 0 (2026-10-03): the skill was created with `skills create … generateRubrics: true`, so the **platform generated rubrics from the skill text** | 5 rubrics. Not repeatable: the same skill gave 5, then 1, then a different 5. They **overrated wrong answers** (0.85–1.0); the reward ranked a right answer above a wrong one only 83% of the time |
| 2. Written by hand | The six were written instead, with the **GitHub Copilot agent in VS Code, using the Claude Opus 5.5 model**, from the world's trap list (world-builder 03 § 9.2, "written before the skill exists") and revised against step 1's answers ([changes and evidence](../../archive/attempt-1/stages/stage-1/rubrics.md)). Applied in attempt 1, stage 1 (2026-10-08) | Right ranked above wrong 93% of the time |
| 3. Pinned | Written in the **platform's own rubric format**, the same structure the generator produces: `RubricName`, `Description`, `ChecklistItems`, `Importance` (critical, high), `RubricType` (`user_facing`), `RedFlags` (empty), `MeasurementMethod` (`binary_checklist`). Pinned in [config/rubrics.json](config/rubrics.json), with `generateRubrics: false` in the skill so the platform can't replace them | The six used from attempt 1 stage 1 onwards, and here |

The platform's grader still does the judging: it scores each answer against these rubrics with no judging prompt from us. Only the criteria are ours. Who drafted them comes from the user's account; the repository's own records say only "designed by hand".

For comparison, on 2026-10-13 the platform generated rubrics again from the same skill text, in `wce-dev` on a copy of the skill: 4 rubrics that check completeness and sourcing but not the traps ([stage 1, generated-rubrics](../stage-1/raw/generated-rubrics/rubrics-generated.md)).

## Two independent checks on every answer

The platform's rubric score says how well an answer **reads** against the checklists. It does not know the right answer: the grader has no answer key. So every answer was also checked for whether it is **right**:

| Check | How | Result |
| --- | --- | --- |
| **Rubric score** (platform) | The platform's grader scores each answer against the six rubrics | Mean **0.956** |
| **Ground truth, automatic** | `scripts/score_ground_truth.py` compares the **decision**, the **governing instrument** and the **payable amount** with the answer key (`world-builder/out/data/claims.json`, the source of [GROUND-TRUTH.md](../../world-builder/out/GROUND-TRUTH.md)) | 26/30 |
| **Ground truth, by hand** | Every answer the scorer marked wrong or couldn't read was read in full against the answer key ([results/hand-check.md](results/hand-check.md)) | **29/30** |

The hand-check corrected the automatic result in three places, where the scorer misread an answer that was right:

| Claim | Scorer | By hand |
| --- | --- | --- |
| C-2026-04153 | Wrong instrument | ✅ Right. The answer names TSB-C-0051 only to rule it out; ADD-IN-2.1 governs, as expected |
| C-2026-04172 | Couldn't read the decision | ✅ Right. Escalated the ₹312,000 goodwill request to the Warranty Operations Head, and the escalation was recorded |
| C-2026-04176 | Couldn't read the decision | ✅ Right. Held the claim and requested the missing commissioning record |
| C-2026-04151 | Wrong payable | ❌ **Wrong**, confirmed (below) |

### Where a good rubric score hid a wrong answer

| Claim | Rubric score | What Sol answered | The right answer |
| --- | --- | --- | --- |
| C-2026-04151 | **0.96** | Approve ₹29,455: the part fitted priced at its own list price, ₹24,600 | Approve **₹31,030**: the part has been superseded, and policy §4.2 prices a superseded part at the new part's price, ₹26,100 (plus the 5% partner uplift on that) |

Sol saw the supersession and chose not to apply it. The Valuation rubric only asks the answer to *name* any supersession, which it did, so the rubric scored it as highly as answers that were right: 0.96 is above 15 of the 29 correct answers. **For this world, the rubric score is not enough on its own to tell right from wrong.** This matters later: in fine-tuning, the rubric score is the reward.

## How the run went

| | |
| --- | --- |
| When | 2026-10-11, 07:14–09:19 IST, pre-flight to close |
| Jobs | 1 smoke-test job (1 claim) + 6 jobs (29 claims), 14 minutes each. No stalls, no retries |
| Before the run | The claim database held 19 drafts written outside the climb (a Foundry agent on 10-09), so it was fully **re-seeded**. All six rubrics were found **disabled**, probably by the cancelled tuning job, and the first submission was refused. They were re-enabled with content unchanged ([P9](../../docs/06-platform-issues.md#p9-rubrics-found-disabled-evaluation-refused-er07018)) |
| Tooling fixed | The database script couldn't load the full seed; the runner stopped when a log watcher locked its file (the platform job carried on and was taken over); the scorer misread table-style totals; the summary counted not-applicable rubrics as 0. All fixed and re-tested |

Every command and response, in order, ready to re-run: [RUNBOOK.md](RUNBOOK.md).

## Results

| Measure | GPT-5.6-Sol |
| --- | --- |
| **Right answers** (decision + instrument + payable, hand-checked) | **29/30** |
| Rubric score (platform) | 0.956 |
| Hand-in failures (echoed question, stub, "can't access") | 0 |
| Tool calls per claim | mean 13.7, range 7–27 |

**Right answers by claim type:** covered-simple 3/3 · declined-simple 2/2 · precedence 5/5 · serial-boundary 4/4 · dual-limit 3/3 · stale-deck 2/2 · authority 2/2 · abstention 3/3 · **valuation 5/6**.

**Rubric score by rubric** (mean over the claims it applies to): Coverage 1.00 · Precedence 0.90 · Grounding 0.98 · Valuation 0.92 (17 approvals) · Authority and action 0.98 · Gaps 0.90 (10 claims).

Detail: [results/ground-truth-check.md](results/ground-truth-check.md) (automatic check, per claim) · [results/hand-check.md](results/hand-check.md) (by hand) · [results/run-summary.md](results/run-summary.md) (rubric score and tool calls per claim).

## Findings

| Issue | What we did |
| --- | --- |
| The world is solvable with this skill: Sol handled every trap type, including document over stale index, dual limits, the stale deck, missing records and goodwill escalation | Baseline recorded: **29/30** |
| One real error: supersession pricing on C-2026-04151 | Kept as is. It's a fair test, and the answer shows the rule was read but misapplied |
| The rubrics scored that wrong answer 0.96 | Noted for reward alignment: the Valuation checklist should require *applying* the superseding price, not only naming it |
| The scorer misread 3 right answers | Hand-checked; teach the scorer these phrasings before the next run |
| The database had been used outside the climb | A full re-seed is now part of the pre-flight checks ([docs/05](../../docs/05-operations.md#before-every-run)) |

## Conclusion

With the current skill and rubrics, this world allows **29 of 30 claims to be adjudicated correctly**, and that is the baseline. The rubric score (0.956) agrees with correctness overall, but not claim by claim: a wrong payable can score as well as a right one. So results are always reported with the ground-truth check alongside the rubric score.

## Next

Run the same use case, same configuration, with MAI-CODE-5b.
