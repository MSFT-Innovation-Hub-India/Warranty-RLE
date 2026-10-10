# Stage 2: hand check of the 29-claim result

🖥️ Source: the stored responses and grader notes in [eval-results-samples.json](eval-results-samples.json), checked against the generated ground truth by the assistant on 2026-10-09. Raw outputs and the [automatic report](ground-truth-check.md) are unchanged.

**Automatic: 14/29. Hand-checked: 17/29.** C-2026-04130 is excluded, not counted wrong. Four review flags are resolved below.

| Claim | Automatic result | Hand check | Evidence |
| --- | --- | --- | --- |
| 04102 | Review | Wrong | Asks for library access; supplies no decision, governing instrument or payable |
| 04115 | Wrong payable | Correct | Opening and explicit total both say INR 755,050; scorer selected INR 13,050 from the labour working line containing “Amount payable” |
| 04116 | Wrong governing instrument | Correct | Declines under the India 18-month/5,000-hour window and explicitly says TSB-C-0051 does not apply; scorer's fallback selected the negated bulletin instead of the addendum named in words |
| 04150 | Review | Wrong | Gives the correct INR 755,050 breakdown, but no coverage decision or governing instrument; a correct amount alone is not fully correct |
| 04151 | Review | Correct | “is in warranty”, TSB-C-0051 and INR 31,030 are explicit; scorer does not recognise “in warranty” as approval |
| 04171 | Review, delivery mismatch | Wrong | Stored response echoes the question; grader explicitly describes the delivered response as that same echo. Its mention of an earlier failed finish is not a mismatch in the final answer |

All other automatic outcomes retained. 04178 requests evidence but does not establish the expected ADD-IN-2.1 as governing; its bulletin mention explicitly says the bulletin does not apply.

## Matched baseline

Stage 1's original **23/30** includes correct claim 04130. Removing only that claim yields **22/29**, rubric **0.637**. Stage 2b on the same 29 is **17/29**, rubric **0.526**. Per-claim rubric scores are averaged across the cohort; no incomplete or excluded execution contributes.

Reproduce: run [score_ground_truth.py](../../scripts/score_ground_truth.py) on each stage's merged result, omit 04130, then apply the six documented hand-check decisions above to stage 2 only. The [paired measurement output](../../docs/evidence/stage-2/2b/paired-comparison-output.txt) records the resulting metrics and all changed outcomes.
