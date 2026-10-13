# Stage 1: broaden the evidence (GPT-5.6-Sol on the Training claims)

**Status:** ✅ closed 2026-10-13
**Result in one line:** GPT-5.6-Sol gets **57 of 60 Training claims right** (rubric 0.934). The one real error, a goodwill request not escalated, scored **1.00 on the Authority rubric**, while right answers scored 0.00 on it: the reward needs fixing before anything else.

## Goal

Find where the skill and the rubrics fall short, without touching the 30 Evaluation claims. Sol got 29 of those 30 right in stage 0, so they show little to fix, and they must stay held out. The 60 Training claims are the ones refinement is allowed to use. This stage measures them, changes nothing, and produces the evidence stages 2 (rubrics) and 3 (skill) work from.

## What changed

| | Stage 0 | This stage |
| --- | --- | --- |
| Claims | 30 Evaluation claims | **60 Training claims** ([config/training-sample-ids.json](config/training-sample-ids.json)) |
| Route | Evaluation jobs | `executions run` with rubric grading (evaluation jobs stopped reaching the claim system, see below) |

Everything else is unchanged: model (GPT-5.6-Sol), skill, rubrics, strategy (`Simple`), world. Configuration: [config/](config/), identical to stage 0's.

**How the skill and rubrics were made** ([history](../../docs/04-hill-climb-method.md#6-where-the-skill-and-rubrics-came-from)):

| | Made how | From |
| --- | --- | --- |
| Skill | By hand, carried over | Stage 0 (attempt 1's business brief) |
| Rubrics | By hand, carried over | Stage 0 (the six hand-designed rubrics) |

## How the run went

| | |
| --- | --- |
| When | 2026-10-13, 15:05–17:27 IST |
| First attempt (not used) | Evaluation jobs, as in stage 0: 40 claims in 4 jobs. Sol never reached the claim system (0 calls arrived at the MCP server) and asked for evidence on almost every claim. Evaluation jobs now fail this way for every model ([P11](../../docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error)). Stopped; results kept in [raw/run/](raw/run/) as evidence |
| The run | `executions run` with rubric grading (`scripts/exec-batches.ps1`), 5 claims at a time: 60 claims in 51 minutes, 3–6 minutes each. 59 completed; 1 failed on the platform (04185) |
| Before the run | MAI-CODE-5b had been selected during the stage 4 attempts; deselected so only Sol is selected, as in stage 0 |

⚠️ **Route:** stage 0 used evaluation jobs; this stage used `executions run`. These Training claims weren't in stage 0, so nothing is compared across the change. The 30 Evaluation claims will be re-baselined on this route before stage 2.

Step-by-step commands and responses: [RUNBOOK.md](RUNBOOK.md).

## Results

| Measure | GPT-5.6-Sol, 60 Training claims |
| --- | --- |
| **Right answers** (decision + instrument + payable, hand-checked) | **57/60** |
| Wrong | 1 (C-2026-04174, authority) |
| World-data defect | 1 (C-2026-04106) |
| Platform failure | 1 (C-2026-04185) |
| Automatic scorer before the hand-check | 45/60 (12 right answers misread) |
| Rubric score (platform) | 0.934 |
| Tool calls per claim | mean 11.2, range 5–19; claim-system calls 1.9 |
| **Reward ranks right above wrong** | **83%** of pairs: the two non-right answers score 0.90 and 0.85, above 13 and 4 of the 57 right ones |

**Right answers by claim type:** abstention 6/6 · authority **2/3** · covered-simple 4/5 (04106 is the world defect) · declined-simple 3/3 · dual-limit 6/6 · exclusion 3/4 (04185 platform failure) · precedence 10/10 · repair-warranty 2/2 · serial-boundary 6/6 · stale-deck 3/3 · valuation 12/12.

**Rubric score by rubric** (mean where graded): Coverage 1.00 · Precedence 0.87 · Grounding 0.91 · Valuation 0.95 (34 claims) · Authority and action 0.92 · Gaps 0.98 (30 claims).

Detail: [results/hand-check.md](results/hand-check.md) · [results/ground-truth-check.md](results/ground-truth-check.md) (automatic) · [results/run-summary.md](results/run-summary.md) (per claim) · [results/reward-ranking.txt](results/reward-ranking.txt).

## Findings

| Issue | Evidence | Goes to |
| --- | --- | --- |
| **The Authority rubric misfires both ways** | The one wrong answer (04174: ₹742,000 goodwill not escalated, nothing recorded) scored **Authority and action 1.00**. Right answers scored **0.00** on it: 04119 (asked only "still in warranty?") and 04108 | **Stage 2.** Require a *recorded* escalation when goodwill exceeds the requester's authority (a red flag fits); make the action items not applicable when the question doesn't ask for a decision |
| **Valuation can't see supersession pricing** (stage 0, 04151) | No valuation errors in these 12 claims; the stage 0 case stands | **Stage 2.** Valuation must require *applying* the superseding part's price |
| **Sol often records no claim-system action** | 17 of 59 claims: on question-style prompts ("What's the position…", "…and advise") Sol answered as advice only. It cost 04174 its escalation; 04181 and 04182 concluded "request evidence" without recording one | **Stage 3** (skill: when to record), after stage 2 settles what the rubric expects |
| **World defect: C-2026-04106** | The only pump-replacement claim fitted with a hose set; Sol held it for the mismatch | **World fix** in the generator, or drop 04106 from training. Not a model problem |
| The scorer misreads 12 right answers | Narrow questions with no amount; negations ("no escalation is required"); an instrument named to rule it out; policy clause 6.1 as governing | **Scorer fix** before stage 2, so the automatic count can be trusted |
| Evaluation jobs no longer reach the claim system, for any model | 0 MCP calls during 4 Sol jobs; `executions run` works | Platform team ([P11](../../docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error)); runner switched |

## Conclusion

On the Training claims, Sol adjudicates almost everything correctly (57/60, one miss being a world defect), so the skill is not what limits correctness for a frontier model. **The reward is the weak point:** the rubric meant to catch an unescalated goodwill request gave it full marks, while marking down right answers that had no action to take. Since the rubric score becomes the RFT reward, this gets fixed first.

## Next

1. **Fix the scorer's misreads** (no platform cost), and decide on 04106 (fix the world or drop it from training).
2. **Re-baseline stage 0** on the `executions run` route: the 30 Evaluation claims with Sol, current rubrics.
3. **Stage 2, reward alignment (rubrics only):** Authority and action (recorded escalation; not applicable to informational questions) and Valuation (apply the superseding price). Re-grade and re-rank on the Training claims, then a new Evaluation baseline.
