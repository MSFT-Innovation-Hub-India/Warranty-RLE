# Stage 2-base — Stage 1's setup, on the honest prompt set

**Status:** ✅ measured 2026-10-04. Job `9f4ad313-9629-4571-8f58-13a7bba63c97`: **rubric 0.978 · correct 27/30** by the answer key; **29/30** by the world's rules. ⚠️ Saturated; 2 world defects found.

**Purpose.** Stage 1 v2 saturated (0.991, 7/8) on the 8 easy prompts. Before stage 2
changes the rubrics, we need a baseline on prompts that have headroom. This is that
baseline: the same agent, the same grading, the full set of 30 eval prompts. Expected:
**rubric score high, ground-truth correctness lower**, which is the gap 2a's hand-written
rubrics should expose.

This step isn't in the original runbook, which ran stage 2 on the same 8 prompts. It's
inserted here because the 8 saturated. Stage 2 is now **2-base → 2a (hand-written rubrics)
→ 2b (three thin skills)**, one change each.

## The one change (against stage 1 v2)

| | Stage 1 v2 | **Stage 2-base** |
| --- | --- | --- |
| Evaluation samples | 8 (covered-simple 3, declined-simple 2, precedence 3) | **all 30** eval prompts ([samples.jsonl](samples.jsonl), a copy of `out/samples/warranty-adjudication.eval.jsonl`) |

| Slice | Prompts | What it tests |
| --- | --- | --- |
| valuation | 6 | flat-rate hours, labour rate by region and date, part supersession, partner uplift |
| precedence | 5 | bulletin ▸ addendum ▸ policy |
| serial-boundary | 4 | a serial just inside or just outside a bulletin's range |
| covered-simple | 3 | control |
| dual-limit | 3 | months **and** hours, whichever comes first |
| abstention | 3 | missing commissioning date: hold, don't guess |
| declined-simple | 2 | control |
| stale-deck | 2 | an old review deck contradicting current policy |
| authority | 2 | goodwill beyond a manager's authority; a Teams "go ahead" isn't approval |

## Everything else, held constant

| | |
| --- | --- |
| World | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4`, corpus **v2.1** (clause 5.4 clarified; see JOURNEY) |
| Model · strategy | `prod-gpt-56-reasoning-sol` · `simple` |
| Skill · rubrics | `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da`; pinned generated rubrics. Hashes equal stage 1 v2 (`358B61B409E6`, `A3BB46F8945D`); the platform's rubrics equal the pinned file |
| MCP server | enabled; 137 tools available (12 MCP) |
| Platform snapshot | SkillsCount 1 · ToolsCount 4 · SamplePromptsCount **30** · KnowledgeSourcesCount 4 |

**Environment (not an agent variable):** MCP replicas pinned at **5** (min = max = 5,
revision `--0000006`), up from 3, because up to 30 runs may start together.

## Run

```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $sk='cf00d339-5217-4cd1-b390-cc0d911735da'
# 1. Replace the samples. `samples delete-by-skill --skill-id` does NOT exist in CLI 0.3.16;
#    list the old ones first, then delete them by id
frontier-tuning samples list --limit 500 --env-id $e -o json > samples-before.json
frontier-tuning samples upload stages\stage-2-base\samples.jsonl --skill-id $sk --type Evaluation --env-id $e
frontier-tuning samples delete <old-sample-id> --yes --env-id $e      # for each of the old 8
# 2. Capacity and pre-flight
az containerapp update -n contoso-service-mcp -g pcdotai-agent --min-replicas 5 --max-replicas 5
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql                                  # expect 0 0 0 0
frontier-tuning tools available --env-id $e -o json                                    # expect 137; re-read if not
# 3. Evaluate, then both numbers, then snapshot and reset the DB, as in stage 1
frontier-tuning evaluate start --skill-id $sk --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $e -o json
```

**Watch out.**
- The first `tools available` read returned **88**; four re-reads gave 137. Always re-read.
- Sample titles in `samples list` are cut at about 50 characters, so a claim ID may not appear. Match on the prompt text instead.

## Results — 2026-10-04 · job `9f4ad313-9629-4571-8f58-13a7bba63c97`

| | Stage 1 v2 (8 easy) | **Stage 2-base (30)** |
| --- | --- | --- |
| **Rubric score (platform)** | 0.991 | **0.978** |
| **Fully correct vs answer key** | 7/8 | **27/30 (90%)** |
| **Right by the world's own rules** (after hand check) | 8/8 | **29/30** |
| Wall time | 22 min | 43 min (14:37 → 15:20 UTC) |

Detail: [ground-truth-check.md](ground-truth-check.md) · [eval-results.json](eval-results.json) · `eval-results-samples.json` (8.7 MB) · [db-actions-after-eval.txt](db-actions-after-eval.txt) (23 drafts, 4 evidence requests, 1 escalation; reset afterwards)

**Per rubric (platform):** Outcome 0.994 · Determination 0.960 · Grounding 0.997 · Presentation 0.982 · Draft Execution 0.958 (n=24).

**Per slice (answer key, after scorer fixes):** precedence 5/5 · stale-deck 2/2 · covered-simple 3/3 · declined-simple 2/2 · valuation 6/6 · dual-limit 3/3 · serial-boundary 3/4 · abstention 2/3 · authority 1/2.

**The six answers first marked wrong, read by hand**

| Claim | Answer key | Agent | Verdict |
| --- | --- | --- | --- |
| 04140 dual-limit | decline | *"Decision: decline under warranty"* | ✅ **Scorer misread** ("no … goodwill escalation, or other change") |
| 04150 valuation | TSB-C-0051 | *"covered by **TSB-C-0051**"* | ✅ **Scorer misread** |
| 04153 valuation | ADD-IN-2.1 | *"TSB-C-0051 **does not govern** … ADD-IN-2.1 A1 … governs"* (control board isn't a TSB component) | ✅ **Scorer misread** |
| 04131 serial-boundary | approve ₹198,450 | hold: *"a second apparently identical submitted claim, C-2026-04136"* | ⚠️ **World defect.** The generator made 4 eval claims with identical training twins (04129/33, 04130/34, 04131/36, 04132/37). The agent caught a real duplicate |
| 04178 abstention | hold (no hours reading) | decline: time limit expired 1 Apr 2026, repair 18 Jun 2026 | ⚠️ **Answer-key defect.** "Whichever comes first": once time has expired, the missing hours can't matter. The engine tests missing hours *before* the time limit |
| 04172 authority | escalate (₹312,000 goodwill) | *"either (a) decline … or (b) route the ₹312,000 request to the Warranty Operations Head"*; nothing recorded | ❌ **Genuine miss.** It found the right authority tier, but hedged instead of escalating. Rubric **1.0** |

**Scorer fixes** (29/29 tests): a negated middle list item; "covered **by**"; a negated instrument ("X does not govern / apply / cover"); "POL-WAR-4.2 clause 1.4" treated as a precedence citation, not the governing instrument; "not covered, **but** escalate" no longer read as negated. Re-scoring all earlier stages changed no count.

**Reading the numbers**
- ⚠️ **Saturated again, on the hard slices too.** 0.978 rubric, and 29/30 right by the world's rules. GPT-5.6-Sol with tools gets precedence, serial boundaries, dual limits, valuation (supersession, uplift, dated labour rates), stale decks and abstention right. Per AGENTS.md goal 2, there's no frontier headroom left in this world.
- **The rubrics still don't check correctness.** The one genuine miss (04172) scored 1.0.
- **Two world defects need fixing regardless**, before any tuning:
  - 04178's answer key is wrong.
  - The 4 identical eval/train twins would **leak eval answers into RFT training** in stage 4.

**Gate.** ⚠️ Baseline measured, but there's no headroom for the frontier model. Direction needs a decision (see JOURNEY).

> **Note, 2026-10-04 21:15:** both world defects fixed after this run (world **v2.2**). The answer key now tests the time limit before a missing hours reading. The no-reading abstention assets are commissioned 2025-10-01, so the reading still decides. Training serial-boundary claims use their own serials. The 30 eval prompts and their expected answers are unchanged. This stage was not re-run. See the [evidence record](../../docs/evidence/journey-record-2026-10-04.md#world-v22--two-defects-found-by-stage-2-base-2115-ist).
