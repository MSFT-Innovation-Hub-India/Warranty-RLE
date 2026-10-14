# Stage 3: skill, record the draft

**Status:** ✅ closed 2026-10-14
**Result in one line:** The skill line roughly halved the claim questions with no draft recorded (11 → 6) and correctness held at 59/60. The 6 left are prompts Sol reads as asking for advice ("advise", "work up", "where do we land"), where it deliberately records nothing.

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
| When | 2026-10-14, 11:18–12:11 IST |
| Run | `executions run`, 5 claims at a time: 60 claims in 52 minutes (median 3.3 min each), all completed |

Step-by-step commands and responses: [RUNBOOK.md](RUNBOOK.md).

## Results

| Measure | Stage 1 | Stage 2 | **Stage 3** |
| --- | --- | --- | --- |
| **Claim questions with no draft recorded** | 15 | 11 | **6** |
| **Right answers** (automatic, matches the hand-check) | 57/60 | 59/60 | **59/60** |
| Not right | 04174 · 04106 · 04185 | 04147 (search outage) | **04104**: superseded part priced at its own price |
| Rubric score (platform) | 0.934 | 0.940 | 0.942 |
| Reward ranks right above wrong | 83% | 86% | 85% |
| Tool calls per claim | 11.2 | 11.9 | 10.9 |

**Right answers by claim type:** abstention 6/6 · authority 3/3 · covered-simple 4/5 (04104) · declined-simple 3/3 · dual-limit 6/6 · exclusion 4/4 · precedence 10/10 · repair-warranty 2/2 · serial-boundary 6/6 · stale-deck 3/3 · valuation 12/12.

**Rubric score by rubric** (mean where graded): Coverage 1.00 · Precedence 0.89 · Grounding 0.93 · Valuation 0.98 · Authority and action 0.90 · Gaps 1.00.

Detail: [results/ground-truth-check.md](results/ground-truth-check.md) · [results/run-summary.md](results/run-summary.md) (writes recorded per claim) · [results/reward-ranking.txt](results/reward-ranking.txt).

## Findings

| Issue | Evidence | What we did / next |
| --- | --- | --- |
| **The skill line works, partly** | Claim questions with no draft: 11 → 6. Correctness unchanged | ✅ Keep |
| **Sol still treats some requests as advice only** | The 6 misses, each saying so: 04121 and 04158 "…and advise" ("I have provided advice only"); 04125 "work up … coverage position and payable amount" ("No claim-system action was taken"); 04133 "I need a decision … before the partner call"; 04147 "Where do we land?" ("this is decision support only"); 04159 "Customer is asking … what's the coverage position?" | **Stage 3b (skill):** say that recording a draft doesn't decide the claim, so it applies even when the request is for advice. The skill opens with "An adjudicator decides each claim, and you prepare that decision for them", which Sol may read as "don't act" |
| **The supersession mistake recurred, and the revised rubric caught it** | 04104: P-44080 fitted, superseded by P-44080-B; priced at ₹24,600 instead of ₹26,100 (₹28,225 vs ₹29,725). Sol reasoned the agreement "requires reimbursement of the part actually fitted". **Valuation 0.60**; overall 0.89, below the right-answer mean 0.94 (outscores 9 of 59) | The reward works as stage 2 intended. Sol's reasoning is a skill question (stage 3c candidate): the policy's supersession clause isn't being applied |
| The scorer misread 3 answers, and one stage 2b probe | "remain held — not approved or declined"; "**controlling** coverage instrument"; a concessive "Although …, ADD-IN-2.1 …" read as ruling the addendum out; "would ordinarily govern" read as governing | ✅ Fixed: 4 rules, 4 tests (75/75). Every stage's automatic count now matches its hand-check; attempt 1 unchanged |

## Conclusion

One sentence in the skill moved behaviour in the intended direction without costing correctness: Sol now records the draft on most claim questions. The remaining misses are a single, clear pattern, requests Sol reads as asking for advice, which a second, narrower skill line can address. Separately, the reward now does what stage 2 designed it to do on a mistake Sol made naturally (supersession pricing).

## Next

1. **Stage 3b (skill):** recording a draft doesn't decide a claim, so it applies to requests for advice too. Measure on the 60 Training claims.
2. **Then the Evaluation claims:** the 30 held-out claims with the final skill and rubrics, for the configuration a small model would be measured on (stage 4).
