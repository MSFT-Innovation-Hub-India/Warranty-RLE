# Stage 0 — The naive baseline

**Status:** ✅ done 2026-10-04. Evaluation job `555d5dd2-f9c3-4008-8846-02e9ceca44d3`: **rubric 0.630 · fully correct 1/8**. Gate passed.

**Purpose.** Build the way most teams start, with one broad skill and
platform-generated rubrics, and measure it honestly. The MCP server is **off**,
so database facts are unreachable. Stage 1 switches it on.

## The one change

None; this is the baseline.

## World state for this stage

| | |
| --- | --- |
| World | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` |
| Model · strategy | `prod-gpt-56-reasoning-sol` (GPT-5.6-Sol) · `simple` |
| Knowledge | SharePoint `Warranty Operations` + 3 Teams channels ([world/env.md](../../world/env.md)) |
| MCP server | `contoso-service` `1c171d49-7f85-4997-8126-ae20829a4dbf`: **disabled** |
| Other tool sources | SharePoint, OneDrive, Teams on; Email, Calendar, Word, M365Chat, fabriciq off |
| Skill | `warranty-assistant`: main `cf00d339-5217-4cd1-b390-cc0d911735da` |
| Rubrics | 5 rubrics / 28 items, platform-generated on dev on 2026-10-03 and **pinned** |
| Samples | 8 eval prompts: covered-simple 04101–04103, declined-simple 04109–04110, precedence 04114 · 04116 · 04118 ([stage0.jsonl](stage0.jsonl)). 5 approve, 3 decline. 04115 and 04117 dropped as near-duplicates |

## Files

| File | What it is |
| --- | --- |
| [warranty-assistant.md](warranty-assistant.md) | The skill: the business job and sources, with no trap rules. `generateRubrics: false` (see its header comment) |
| [warranty-assistant.rubrics.json](warranty-assistant.rubrics.json) | The pinned rubric set, verbatim from the platform's generation |
| [stage0.jsonl](stage0.jsonl) | The 8 prompts, copied word for word from `out/samples/warranty-adjudication.eval.jsonl` |

## Apply (to a fresh world)

```powershell
$world = '<world-id>'
frontier-tuning skills create --file stages\stage-0\warranty-assistant.md --env-id $world -o json   # note the skill id
# apply the pinned rubrics: put the JSON array into the skill payload's "Rubrics" field
$raw  = frontier-tuning skills get <skill-id> --env-id $world -o json | Out-String
$s    = $raw.Substring($raw.IndexOf('{')) | ConvertFrom-Json
$s.Rubrics = Get-Content stages\stage-0\warranty-assistant.rubrics.json -Raw | ConvertFrom-Json
$s | ConvertTo-Json -Depth 12 | Set-Content "$env:TEMP\payload.json" -Encoding utf8
frontier-tuning skills update <skill-id> --file "$env:TEMP\payload.json" --env-id $world
frontier-tuning tools disable <mcp-server-id> --env-id $world                                        # stage 0: MCP off
```

## Run

```powershell
# 1. Hand probe (the gate): main reads the documents and routes to the skill
frontier-tuning chat --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -q "Adjudicate claim C-2026-04114." --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json
# 2. Samples
frontier-tuning samples upload stages\stage-0\stage0.jsonl --skill-id cf00d339-5217-4cd1-b390-cc0d911735da --type Evaluation --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
# 3. Evaluate
frontier-tuning evaluate start --skill-id cf00d339-5217-4cd1-b390-cc0d911735da --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json
# 4. Results, then the second number
frontier-tuning evaluate results 555d5dd2-f9c3-4008-8846-02e9ceca44d3 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json > stages\stage-0\eval-results.json                   # summary
frontier-tuning evaluate results 555d5dd2-f9c3-4008-8846-02e9ceca44d3 --samples --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json > stages\stage-0\eval-results-samples.json   # every answer
.\.venv\Scripts\python.exe build\score_ground_truth.py stages\stage-0\eval-results-samples.json --out stages\stage-0
```

**Watch out.** `chat --skill-id …` returned `API error (500)` in both worlds.
Leave it out: routing picks the skill by itself.

**Hand probe, 2026-10-04 (gate ✅).** Execution `4796e7dc-c2ee-4ad3-9235-44511c6976e0`:
routed to `warranty-assistant`, 24 tool calls (SharePoint search, Teams, `m365__call_copilot`;
no MCP), and every document search returned results. The answer: *"Cannot yet be finally
decided — hold pending commissioning evidence"*, with TSB-C-0051 correctly named as governing.
The ground truth says approve, ₹199,175. Without the claim system the agent couldn't find the
commissioning date, so it held the claim. The rubrics still scored *Claim Determination* 1.0.

## Results — 2026-10-04 · job `555d5dd2-f9c3-4008-8846-02e9ceca44d3`

| | Result |
| --- | --- |
| **Rubric score (platform)** | **0.630**: 8 submitted, 8 graded, 0 failed |
| **Fully correct vs ground truth** | **1 of 8 (12%)**: decision 1/8 · governing instrument 3/8 · payable 0/5 |
| Wall time | 52 min: about 4 min queued, about 16 min running the 8 prompts, the rest grading |
| Detail | [ground-truth-check.md](ground-truth-check.md) · [eval-results.json](eval-results.json) (summary) · `eval-results-samples.json` (every answer and trace, 3.6 MB) · [eval-diagnostics.txt](eval-diagnostics.txt) |

**Per rubric (platform)**

| Rubric | Score |
| --- | --- |
| Requested Outcome Delivery | 1.00 |
| Claim Determination Requirements | 0.65 |
| Internal Record Use and Grounding | 0.75 |
| Adjudicator-Ready Presentation and Traceability | 0.75 |
| Claim-System Draft Execution | 0.00 (expected: the MCP server is off) |

**What happened.** **7 of 8 answers held the claim** ("cannot yet be decided").
With the claim system off, the agent couldn't retrieve the claim record,
the asset or the commissioning date. It cited policy 2.3 and refused to
guess, rather than inventing facts. It still found the right rules: TSB-C-0051 for
04114, and the exact contingent amounts (₹69,575 on 04101, ₹199,175 on 04114,
"approve only if commissioning confirms…"). The one correct answer, 04109
(decline), is a claim whose inspection report is in the library.

**Reading the two numbers**
- **The gap is large: 0.63 vs 12%.** *Requested Outcome Delivery* gave **1.0 to every
  answer**: "cannot yet be decided" counts as a definite answer, so a hold scores
  full marks there.
- **But the agent behaved correctly for this stage.** Holding is the right call when the
  system of record is unreachable. The ground truth assumes full access, so it marks
  these answers wrong. Stage 0's "wrong" is mostly **missing data**, not bad reasoning.
- So stage 0 doesn't yet prove the rubrics overrate the agent. **Stage 1 is the
  cleaner test:** with the facts available, a wrong decision can no longer hide
  behind a hold.

**Gate.** ✅ **Proceed to stage 1.**
- Documents retrieved in every answer.
- Submitted = graded (8 = 8).
- The weakness is the diagnosable one: missing facts, not broken retrieval.
- 0.63 is just above the predicted 0.40–0.60 band, but below the "samples too easy" line of 0.70.

**Problems found during the run, and how they were handled**

| Problem | Handled by |
| --- | --- |
| `chat --skill-id` returned `API error (500)` in both worlds | Left it out. Normal routing chose the skill and graded on the pinned rubrics |
| `evaluate results` without `--samples` is a 3 KB summary with no answers | Use `--samples` (3.6 MB, every answer and trace) |
| In those results, `Response` is a list of parts, not text | The scorer joins the parts (+1 test, 19/19 passing) |
| The scorer showed a stray "payable" on held answers (e.g. 04102: ₹1,450, an hourly rate) | Approve-expected answers that weren't approvals are now marked *"payable not assessed"* |

**How the ground-truth check was verified.** I read four answers (04101,
04102, 04110, 04116) by hand against the scorer's output. Every one says *"cannot
yet be decided / hold"*, cites missing claim-system facts and POL-WAR-4.2 clause 2.3,
and matches what the scorer read. The "governing = POL-WAR-4.2" readings on held
answers are correct: a hold rests on clause 2.3, not on an addendum or bulletin.

**Before stage 1:**
- P6: endpoint auth.
- P11: runbook fixes.
- Decide whether the MCP tool descriptions keep their trap hints (JOURNEY § 4).
