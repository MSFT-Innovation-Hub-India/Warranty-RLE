# Stage 2: reward alignment (rubrics only)

**Status:** ✅ closed 2026-10-13
**Result in one line:** The revised rubrics behave as intended where they could be tested: asset-only questions are no longer marked down, and claims with no draft recorded now are. Correctness held (59/60; the one miss was a search outage). The two cases the changes target most, an unrecorded escalation and a mispriced superseded part, didn't recur, so those items are still untested.

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
| When | 2026-10-13, 17:53–18:47 IST |
| Run | `executions run`, 5 claims at a time, as stage 1: 60 claims in 51 minutes, all 60 completed |

Step-by-step commands and responses: [RUNBOOK.md](RUNBOOK.md).

## Results

| Measure | Stage 1 (old rubrics) | **Stage 2 (revised rubrics)** |
| --- | --- | --- |
| **Right answers** (hand-checked; the automatic scorer now agrees) | 57/60 | **59/60** |
| Not right | 04174 wrong (goodwill not escalated) · 04106 world defect · 04185 platform failure | 04147: **every** SharePoint and Teams search returned nothing, so Sol held the claim |
| Rubric score (platform) | 0.934 | 0.940 |
| **Reward ranks right above wrong** | 83% (2 non-right answers) | **86%** (1 non-right answer: 04147 at 0.875 outscores 5 of 59) |
| **Asset-only questions** ("is serial X still in warranty?") scored on Authority | 04119: **0.00** | **Not applicable**, as intended |
| **Claims with no draft recorded** scoring full marks on Authority | 12 of 17 | **2 of 11**: most now 0.5 or 0.0, as rule A intends |
| Unescalated goodwill (04174) | 1.00 with nothing recorded | Not tested: Sol recorded the escalation this time (1.00, correctly) |
| Superseded parts priced (04104, 04154, 04157, 04160, 04163) | 0.8–1.0, all priced right | 0.8–1.0, all priced right. No wrong case to test |
| Tool calls per claim | mean 11.2 | mean 11.9 (6–32) |

The skill and model didn't change, so differences in the answers themselves (04174 escalated this time, 04106 approved) are run-to-run variation, not an effect of the rubrics: the rubrics are never shown to the model.

**Right answers by claim type:** abstention 6/6 · authority 3/3 · covered-simple 5/5 · declined-simple 3/3 · dual-limit 5/6 (04147) · exclusion 4/4 · precedence 10/10 · repair-warranty 2/2 · serial-boundary 6/6 · stale-deck 3/3 · valuation 12/12.

**Rubric score by rubric** (mean where graded): Coverage 1.00 · Precedence 0.91 · Grounding 0.92 · Valuation 0.95 (34) · Authority and action 0.90 (57; was 0.92 on 59) · Gaps 1.00 (24).

Detail: [results/ground-truth-check.md](results/ground-truth-check.md) · [results/run-summary.md](results/run-summary.md) · [results/reward-ranking.txt](results/reward-ranking.txt).

## Findings

| Issue | Evidence | What we did / next |
| --- | --- | --- |
| Authority item 1 now skips asset-only questions | 04119, 04144, 04170: not graded on Authority | ✅ Keep |
| Authority item 4 now enforces "record the draft" | No-action claims scoring 1.00: 12 of 17 → 2 of 11 (04145, 04182 still 1.00: the grader isn't fully consistent) | ✅ Keep. Sol still records nothing on 14 claims: a skill gap for **stage 3** |
| **Valuation still scores asset-only questions** | 04119 (asked only "still in warranty?") scored **Valuation 0.00** | Make Valuation not applicable to asset-only questions, like Authority (**stage 2b**) |
| **Items 2 (Authority) and 3 (Valuation) untested** | Sol made neither error this run; with Sol at 59/60 there are almost no wrong answers to rank | **Stage 2b:** a few deliberate negative controls, e.g. 04174 with "advise only, don't record anything", to confirm the rubric marks them down |
| Searches can return nothing for a whole execution | 04147: 11 SharePoint/Teams searches, all empty, including "Warranty Operations" | Counted as a platform failure, not a Sol error; watch for repeats |
| **Our claim database rejects long evidence requests** | `EvidenceRequest.field_name` is `NVARCHAR(40)`: 7 first attempts failed with "String or binary data would be truncated" (stages 1–2); Sol retried shorter each time | World fix (widen the column in the generator and the live database) before the next stage, with the user's go-ahead |
| The scorer misread 7 answers | "still under warranty", "cannot presently be approved or declined", "no … hold or goodwill escalation is needed", an exclusion bulletin read as governing; declines with a recorded goodwill escalation | ✅ Fixed: 5 reading rules, 5 tests (71/71), and the scorer now uses a **recorded** goodwill escalation to settle "decline vs escalate". Automatic = hand-check in stages 1 and 2; no change on stage 0 or attempt 1 |

## Conclusion

The revised rubrics fix what stage 1 showed and could be observed here: they stop penalising right answers to asset-only questions, and they mark down claims where the outcome wasn't recorded. Correctness didn't move, as expected when only the reward changes. But Sol makes so few mistakes that the two most important new checks, an unrecorded escalation and a mispriced superseded part, weren't exercised. Before the rubrics are trusted as an RFT reward, they need wrong answers to rank, and a frontier model doesn't supply enough of them naturally.

## Next

1. **Stage 2b (rubrics):** make Valuation not applicable to asset-only questions, and run a handful of negative controls: claims prompted to skip the escalation or price a superseded part at its own price, to confirm the rubrics mark them down.
2. **World fix:** widen `EvidenceRequest.field_name` (generator and live database), with the user's go-ahead.
3. **Stage 3 (skill):** Sol records no draft on about a quarter of claim questions; teach when to record.
