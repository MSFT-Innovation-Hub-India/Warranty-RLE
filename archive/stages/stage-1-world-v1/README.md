# Stage 1 — Switch on the claim system

**Status:** ✅ measured 2026-10-04: job `cf102eae-e5a6-489a-bd21-c1e1bd50a79b`, **rubric 0.905 · correct 3/8**. ⚠️ Two defects found (a world inconsistency, and 2 runs without tools), so a re-run is recommended.

**Purpose.** Show how much of the gap was plumbing. The agent now reaches the
service claim system (the MCP server). Nothing else changes, so the difference
from stage 0 is attributable to the tools alone.

## The one change

| | Stage 0 | **Stage 1** |
| --- | --- | --- |
| MCP server `contoso-service` (`1c171d49-7f85-4997-8126-ae20829a4dbf`) | disabled | **enabled** |

```powershell
frontier-tuning tools enable 1c171d49-7f85-4997-8126-ae20829a4dbf --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
```

The platform's own snapshot agrees: `ToolsCount` 3 → **4**, while skills (1), samples (8) and knowledge sources (4) are unchanged.

## Everything else, held constant

| | |
| --- | --- |
| World | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` |
| Model · strategy | `prod-gpt-56-reasoning-sol` · `simple` |
| Skill | `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da`, [warranty-assistant.md](warranty-assistant.md), identical to stage 0 (file hash matches) |
| Rubrics | the same pinned set ([warranty-assistant.rubrics.json](warranty-assistant.rubrics.json), identical) |
| Samples | the **same 8 uploaded samples** as stage 0, not re-uploaded. [samples.jsonl](samples.jsonl) is identical to `stage-0/stage0.jsonl` |
| MCP tool descriptions | unchanged (see the decisions below) |

## Decisions taken before this stage

| Decision | Why |
| --- | --- |
| **Endpoint auth (P6) deferred** | Not part of what the climb measures. The agent's *own* writes are the real contamination risk, and those are handled by the snapshot and reset below |
| **MCP tool descriptions kept as designed** | Changing them now would mean redesigning the world. The consequence is recorded: `get_tsb_index` and `get_asset` describe trap rules (1 and 12), so those traps are easier from this stage on |
| **Runbook fixes (P11) deferred** | Docs only; no effect on measurement |

## Run

```powershell
# 0. Warm the serverless DB, check it's clean
Invoke-WebRequest https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz -UseBasicParsing
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql                       # expect 0 0 0 0
# 1. The one change, then check the tools are offered
frontier-tuning tools enable 1c171d49-7f85-4997-8126-ae20829a4dbf --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
frontier-tuning tools available --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json   # expect 137, including 12 × 1c171__*
# 2. Hand probe, then snapshot and reset what it wrote
frontier-tuning chat --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -q "Adjudicate claim C-2026-04114." --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json
.\scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql
.\scripts\sql-run.ps1 -File scripts\db-reset-actions.sql
# 3. Evaluate: same command as stage 0
frontier-tuning evaluate start --skill-id cf00d339-5217-4cd1-b390-cc0d911735da --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json
# 4. Results, the second number, then what the agent wrote, then reset
frontier-tuning evaluate results <job-id> --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json > stages\stage-1\eval-results.json
frontier-tuning evaluate results <job-id> --samples --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json > stages\stage-1\eval-results-samples.json
.\.venv\Scripts\python.exe build\score_ground_truth.py stages\stage-1\eval-results-samples.json --out stages\stage-1
.\scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql > stages\stage-1\db-actions-after-eval.txt
.\scripts\sql-run.ps1 -File scripts\db-reset-actions.sql
```

**Watch out.**
- Right after `tools enable`, `tools available` briefly returned 88 tools. A re-read gave the correct 137. Re-check before trusting the count.
- From this stage on, the agent **writes to the database**: drafts, evidence requests (which also set a claim to *Held*), and escalations. Snapshot after every run, then reset.

**Hand probe, 2026-10-04.** Execution `8ce435fa-b582-4e30-aa50-cd9ce4617d05`, the same
claim as stage 0's probe:
- 17 tool calls in 3 min: **8 MCP calls first** (claim → asset → hours → history → prior claims → dealer → part → bulletin index), then 6 document searches and 2 Teams searches, then `create_claim_adjudication`.
- Answer: ***"APPROVE — INR 199,175"* under TSB-C-0051.** That matches the ground truth exactly; stage 0 had *held* this claim.
- Draft `ADJ-41014A943B` was recorded (approve, ₹199,175), then reset.
- Rubrics: Outcome 1 · Determination 0.8 · Grounding 1 · Presentation 1 · Draft Execution 1.

## Results — 2026-10-04 · job `cf102eae-e5a6-489a-bd21-c1e1bd50a79b`

| | Stage 0 | **Stage 1** | Change |
| --- | --- | --- | --- |
| **Rubric score (platform)** | 0.630 | **0.905** | **+0.275** |
| **Fully correct vs ground truth** | 1/8 | **3/8** | +2 |
| Submitted · graded | 8 · 8 | 8 · 8 | |
| Wall time | 52 min | 52 min | |

Detail: [ground-truth-check.md](ground-truth-check.md) · [eval-results.json](eval-results.json) · `eval-results-samples.json` (3.9 MB) · [eval-diagnostics.txt](eval-diagnostics.txt) · [db-actions-after-eval.txt](db-actions-after-eval.txt) (what the agent wrote)

**Per rubric (platform)**

| Rubric | Stage 0 | Stage 1 |
| --- | --- | --- |
| Requested Outcome Delivery | 1.00 | 1.00 |
| Claim Determination Requirements | 0.65 | **0.90** |
| Internal Record Use and Grounding | 0.75 | **0.98** |
| Adjudicator-Ready Presentation and Traceability | 0.75 | **0.94** |
| Claim-System Draft Execution | 0.00 | **0.71** (7 of 8 graded on this rubric) |

**Every wrong answer has a cause outside the agent's reasoning**

| Claim | Expected | Inspection report in library? | Got MCP tools? | Answer | Cause |
| --- | --- | --- | --- | --- | --- |
| 04101 | approve | ✅ | ✅ | approve ✅ ₹69,575 | |
| 04109 | decline | ✅ | ✅ | decline ✅ | |
| 04110 | decline | ❌ | ✅ | decline ✅ | |
| 04102 | approve | ❌ | ✅ | hold (provisional ₹48,420 correct) | **World inconsistency** |
| 04103 | approve | ❌ | ✅ | hold (provisional ₹19,150 correct) | **World inconsistency** |
| 04118 | approve | ❌ | ✅ | hold (TSB-P-0112 and ₹67,500 correct) | **World inconsistency** |
| 04114 | approve | ✅ | ❌ **0 MCP calls** | hold for the commissioning date | **Environment** |
| 04116 | decline | ❌ | ❌ **0 MCP calls** | hold, claim not retrievable | **Environment** |

**Defect 1: the world contradicts itself.** The partner agreements (SPA clause 2)
and bulletin TSB-G-0029 say a claim *"must carry the inspection report, the
running-hours reading at the date of repair, and the part number actually fitted"*.
The ground-truth engine requires neither, and accepts the latest reading *at or
before* the repair date. Inspection reports exist for only 12 of 90 claims. When
an approval was expected and no report existed, the agent followed the agreement
and held the claim, which the ground truth marks wrong. This breaks the "one arbiter"
rule in `AGENTS.md`.

**Defect 2: 2 of 8 runs got no MCP tools.** All 8 runs started within 18 seconds,
and the app scaled out mid-burst (a third replica at 09:37:17). The two runs with 0 MCP
calls effectively ran as stage 0. 🔬 Likely cause: tool discovery failed during the
scale-out. The server logs show no errors.

**Reading the two numbers**
- **Plumbing was the bottleneck.** +0.275 on the rubric score, with the same skill, rubrics,
  samples and model. In the 6 runs that got the tools, the agent made **no reasoning
  errors by the world's own rules**: 3 correct, and 3 holds the partner agreement justifies,
  each with the right instrument and the correct provisional amount.
- **Rubric overrating: still inconclusive.** The holds scored 0.96–1.0. Because the
  corpus demands the report, those holds are arguably *right*, so this doesn't yet prove the
  rubrics reward wrong answers. Defect 1 must be fixed first.

**Gate (runbook):** score up ≥ 0.10 ✅ · DB tools in the trace ✅ (6 of 8).
⚠️ **The measurement isn't clean**, because of both defects. Recommended before stage 2: fix both and
**re-run stages 0 and 1** (about 2 h), keeping these results as the "world v1" record.
