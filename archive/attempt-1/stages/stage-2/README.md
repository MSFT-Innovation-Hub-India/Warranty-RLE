# Stage 2: skill refinement (world v3, MAI-CODE-5b)

**Status:** ✅ measured and closed on **29 claims** (2026-10-09), at the user's request. **The skill regressed:** rubric **0.526**, hand-checked correctness **17/29**, against stage 1's **0.637 · 22/29 on the same claims**. What this stage does is explained in [JOURNEY § What we do next: stage 2](../../docs/JOURNEY.md#what-we-do-next-stage-2).

## The change (against stage 1)
Only the skill. Rubrics ([warranty-assistant.rubrics.json](warranty-assistant.rubrics.json), stage 1's hand-written set), model (MAI-CODE-5b) and the 30 evaluation prompts ([samples.jsonl](samples.jsonl)) are unchanged. Two measured steps:

| Step | Skill | How it was produced |
| --- | --- | --- |
| **2a** | *nothing applied* | The platform's tools on stage 1's skill ([warranty-assistant.stage-1.md](warranty-assistant.stage-1.md)): `skills enrich` (no change) and `skills refine` on 17 Training claims ([refine-sample-set.json](refine-sample-set.json)). The refined skill ([refined-by-platform.md](refined-by-platform.md)) restates the rubrics, so it was **rejected**; see Findings |
| **2b** | [warranty-assistant.2b.md](warranty-assistant.2b.md) | Stage 1's skill plus our guidance ([guidance-2b.md](guidance-2b.md)): method, the library folder map, how to hand in |

The applied 2b skill passes `python scripts\check-skill.py <skill> warranty-assistant.rubrics.json`: no 5-word phrase shared with the rubrics, and no claim numbers, serials, amounts or bulletin codes. The platform's rejected version does not.

**Training samples.** The 60 Training prompts ([training-samples.jsonl](training-samples.jsonl), IDs in [training-sample-map.json](training-sample-map.json)) were uploaded for `skills refine`, which uses Training samples only. They are distinct claims from the 30 evaluation prompts and are intended for RFT; which sample type the tuning service actually consumes remains unverified.

## Apply and run
```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $sk='cf00d339-5217-4cd1-b390-cc0d911735da'
frontier-tuning samples upload stages\stage-2\training-samples.jsonl --skill-id $sk --type Training --env-id $e
frontier-tuning skills enrich $sk --env-id $e
frontier-tuning skills refine start --skill-id $sk --sample-id <id> ... --env-id $e        # the 17 in refine-sample-set.json
frontier-tuning skills refine status <refinement-id> --env-id $e
frontier-tuning skills refine detail <refinement-id> --env-id $e -o json                  # review; then check-skill.py
python scripts\check-skill.py stages\stage-2\refined-by-platform.md stages\stage-2\warranty-assistant.rubrics.json   # FAIL: rubric wording -> not applied
# 2b: stage 1's skill + guidance
$f = Get-Content stages\stage-2\warranty-assistant.2b.md -Raw; $body = ($f -split '## Instructions',2)[1].Trim()
frontier-tuning skills update $sk --instructions $body --env-id $e
$s = (Get-Content stages\stage-2\sample-map.json -Raw | ConvertFrom-Json | Where-Object { $_.claim -ne 'C-2026-04130' } | ForEach-Object { "$($_.claim.Substring(7))=$($_.id)" }) -join ','
powershell -File scripts\eval-batches.ps1 -Env $e -Samples $s -OutDir docs\evidence\stage-2\2b -BatchSize 5
python scripts\summarise-stage.py docs\evidence\stage-2\2b stages\stage-2 --consolidate
```

## Result
🖥️ **Matched comparison: the same 29 claims, excluding C-2026-04130 from both stages.** The original stage 1 result remains 23/30; 04130 was correct there, so its matched baseline is 22/29. The exclusion was chosen to stop waiting, not because of an observed answer. This is a partial-cohort, retry-conditioned result, not a clean full-30 comparison.

| Measure | Stage 1, matched 29 | Stage 2b, matched 29 |
| --- | --- | --- |
| Fully correct | **22/29 (76%)** | **17/29 (59%)**, down 5 claims |
| Mean rubric score | **0.637** | **0.526** |
| Mean / median tool calls | 15.4 / 14 | 20.3 / 17 |
| Authority claims correct | 0/2 | 0/2 |
| Echoed questions | 1/29 | 4/29 |
| Inability answers | 2/29 | 5/29 |
| Incomplete substantive answers | 2/29 | 1/29 |
| Rejection keyword flag in final grader notes | 0/29 | 0/29; does **not** establish that no finish attempts failed |

**Per rubric, matched 29**:

| Rubric | Stage 1 | Stage 2b |
| --- | --- | --- |
| Coverage | 0.784 | 0.683 |
| Precedence | 0.543 | 0.500 |
| Grounding | 0.549 | 0.422 |
| Valuation | 0.657 | 0.588 |
| Authority and action | 0.464 | 0.285 |
| Gaps | 0.722 | 0.821 |

**What moved:** 4 claims recovered (04114, 04129, 04139, 04166), but 9 previously correct claims became wrong (04102, 04131, 04140, 04148, 04149, 04150, 04152, 04153, 04178). Right answers still outscore wrong ones about 92% of the time (stage 1: 93%), but wrong authority answer 04172 scores **0.771**.

The automatic scorer reports **14/29** with 4 review flags; the [hand check](hand-check.md) resolves those flags and three extraction errors to **17/29**. Raw answers remain untouched in [eval-results-samples.json](eval-results-samples.json). Detail: [automatic check](ground-truth-check.md), [per-claim run table](run-summary.md), [paired measurement output](../../docs/evidence/stage-2/2b/paired-comparison-output.txt).

## Findings
| Issue | What we did |
| --- | --- |
| `skills enrich` returned `enriched: false, reason: already-optimal` and changed nothing | Recorded; the platform's description rewrite had nothing to add to stage 1's skill |
| `skills refine start` timed out on the reply (`ReadTimeout: submission outcome is unknown`) although the run had started | Reconciled with `skills refine list` before doing anything else; never resubmit blindly |
| **`skills refine` wrote the rubrics into the skill.** Its output (run `588f45c8`, 2.5 h on 17 Training claims) has a "Verify before finish" list that paraphrases the rubric checklist: 2 verbatim 5-word phrases, and on average **47%** of each rubric item's content words reappear (up to 71%). It also put the whole 5k text in the skill's *description* (routing) field, with no instructions. Its failure analysis and validation scores came back empty (0 → 0) | **Rejected** (AGENTS.md: never put a rubric's wording into the skill). A skill that recites the grader's checklist raises the rubric score without making the agent more correct, and in RFT that trains to the test. Kept as [refined-by-platform.md](refined-by-platform.md). Its one useful observation, *"claim work often ended with retrieval commentary instead of adjudication"*, matches stage 1's giving-up cases and is covered by 2b's guidance |
| Guidance did not improve the measured run: more calls, more non-answers, and authority still 0/2 | Closed as a regression, not a successful hill climb; do not promote 2b as the best skill |
| 04130 stalled twice and was running its third attempt | User excluded it on 2026-10-09; stopped the runner, cancelled job `beb6e3ac-ceb5-4283-b107-7a5368bdbd7f`, verified `Cancelled`, and excluded it from both sides of the comparison; original 30 prompts retained |
| One retry batch took 216 minutes despite the runner's 75-minute default | Recorded a timeout-enforcement failure; the cause is not established, and the runner must be hardened before another unattended run |
| Final SQL snapshot/reset failed because public access was denied; user re-enabled access | Retried successfully: snapshot retained, reset and baseline both **0 0 0 0**. Earlier automatic reset messages are not proof of success; overnight database isolation is not established |
| Suspected that late regression came from the midnight SQL shutdown | Checked retained execution times and payloads: **6/9 newly wrong claims finished before midnight**, all **63 dossier reads and 31 writes succeeded**, and local snapshots succeeded at 00:16, 01:17 and 04:54; first denied snapshot is 05:54. SQL cleanup failure is confirmed, but does not explain the retained answer regression ([evidence](../../docs/evidence/journey-record-2026-10-09.md#sql-causality-check)) |
| Failed tool calls increased from 11 on 5 claims to 66 on 17 claims (matched 29); 62 of stage 2's failures are SharePoint browsing tools | Recorded retrieval/navigation failures as a separate contributor worth investigating; counts are not proof that guidance caused them |
| Gap-reporting score rose while correctness fell; 04172 still earns 0.771 for declining rather than escalating | Do not interpret the higher gaps score as an improvement; audit reward alignment before RFT |

## Next
Stage 1 remains the stronger measured skill. Restore it before any headroom experiment, after addressing runner timeouts and verifying SQL access/reset checks. **No stage 3 or tuning run started.** The live skill is still 2b; this closure does not silently change it.
