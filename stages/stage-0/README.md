# Stage 0 v2 — The naive baseline, on the corrected world

**Status:** ✅ done 2026-10-04. Job `53495f74-fcd5-47ef-8b33-43893a49eb04`: **rubric 0.535 · fully correct 0/8**. Gate passed.

**Why a v2.** Stage 1 found that the world contradicted its own answer key
([stage-1 defect 1](../stage-1/README.md#results--2026-10-04--job-cf102eae-e5a6-489a-bd21-c1e1bd50a79b)):
the partner agreements and TSB-G-0029 demanded an inspection report and a reading at
the repair date, while the ground truth requires neither. The world was corrected
("world v2"), so stage 0 is measured again. The [v1 folder](../stage-0/) stays as it was.

## What differs from stage 0 (v1)

Only the world. Skill, rubrics, prompts, model, strategy and tool switches are identical.

| | v1 | **v2** |
| --- | --- | --- |
| TSB-G-0029 and SPA clause 2 (3 agreements) | a claim *must carry* the inspection report and the reading at the date of repair | adjudicated from the claim-system record, using the latest reading at or before the repair date; a missing report *does not of itself hold a claim* |
| Teams: Partner Fabrikam, "Weekly claim status", Meera's reply | *"The three without reports are held, not declined."* | *"…We adjudicate from the claim-system record, so they only hold things up where an exclusion turns on the report."* |
| Ground truth (`out/data/claims.json`) | — | unchanged; the world now agrees with it |

Source edits: `build/gen_docs.py`, `build/gen_teams.py`. Gates 14/14 and 31/31. Only these 4 docx and 1 message changed in content. Details and the live check are in [the evidence record](../../docs/evidence/journey-record-2026-10-04.md#world-v2--fixing-the-inspection-report-inconsistency).

## World state for this stage

| | |
| --- | --- |
| World | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` |
| Model · strategy | `prod-gpt-56-reasoning-sol` · `simple` |
| MCP server | `1c171d49-7f85-4997-8126-ae20829a4dbf`: **disabled** (125 tools available, 0 MCP) |
| Skill · rubrics | `cf00d339-5217-4cd1-b390-cc0d911735da` · the same pinned 5 rubrics ([warranty-assistant.md](warranty-assistant.md), [warranty-assistant.rubrics.json](warranty-assistant.rubrics.json); hashes equal v1) |
| Samples | the same 8 uploaded Evaluation samples ([stage0.jsonl](stage0.jsonl)) |
| Platform snapshot | SkillsCount 1 · ToolsCount 3 · SamplePromptsCount 8 · KnowledgeSourcesCount 4, the same as v1 |

## Apply and run

As [stage 0](../stage-0/README.md#apply-to-a-fresh-world), after regenerating and uploading the world-v2 corpus. One extra check before evaluating, so that search isn't serving the old text:

```powershell
frontier-tuning chat --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json -q "Quote verbatim what bulletin TSB-G-0029 and the Fabrikam partner agreement (SPA-2023-FAB-IN) clause 2 say about inspection reports and running-hours readings. Quote only; do not adjudicate anything."
```

On 2026-10-04 (execution `fc64ba2a-7354-4dcc-9fb5-c2335b000518`), the agent quoted both new paragraphs word for word, about 10 minutes after upload.

## Results — 2026-10-04 · job `53495f74-fcd5-47ef-8b33-43893a49eb04`

| | Stage 0 (v1) | **Stage 0 v2** |
| --- | --- | --- |
| **Rubric score (platform)** | 0.630 | **0.535** |
| **Fully correct vs ground truth** | 1/8 | **0/8** |
| Submitted · graded | 8 · 8 | 8 · 8 |
| Wall time | 52 min | **26 min** (10:13 → 10:39 UTC) |

Detail: [ground-truth-check.md](ground-truth-check.md) · [eval-results.json](eval-results.json) · `eval-results-samples.json` (4.0 MB)

**Per rubric (platform)**

| Rubric | v1 | v2 |
| --- | --- | --- |
| Requested Outcome Delivery | 1.00 | 0.84 |
| Claim Determination Requirements | 0.65 | 0.43 |
| Internal Record Use and Grounding | 0.75 | 0.73 |
| Adjudicator-Ready Presentation and Traceability | 0.75 | 0.68 |
| Claim-System Draft Execution | 0.00 | 0.00 (n=5) |

**What happened.** The same behaviour as v1: with the claim system off, the agent
can't get the claim facts, so it holds the claim or asks for evidence (7 of 8).
04109 was again a decline, but given as *"provisional decline / do not approve yet"*.
The scorer reads the decision correctly, but the governing instrument cited
(TSB-C-0038) isn't the expected one, so it doesn't count as fully correct. 04103 and
04116 were marked ❓ by the scorer. I read both by hand: both say *"unable to complete"*,
which is a hold, so both are wrong.

**The world fix reached the agent.** On 04110 the agent checked `06-ClaimEvidence`, found
no report, and wrote: *"That absence does **not by itself justify declining or holding the
claim**: … a missing inspection report does not itself hold a claim."* That is the v2 wording
of TSB-G-0029. In v1, a missing report was a reason to hold.

**The agent also tried to call the claim tools.** It reports `ToolNotFound` "on repeated
attempts". The skill names the service claim system as a source, so the agent looks
for it, finds nothing, and says so honestly.

**Reading the numbers**
- 💭 **Treat a move of about 0.1 as noise at 8 samples.** Between v1 and v2 the only change
  was document wording, which the agent can barely use without claim facts. Yet the rubric
  score moved 0.630 → 0.535, and *Requested Outcome Delivery* fell from 1.00 to 0.84 for
  answers of the same kind. Most of that movement is run-to-run variance, not the world.
  Deltas smaller than about 0.1 on 8 samples shouldn't be read as real.
- The ground-truth number is stable: 1/8 → 0/8, and the one difference is a citation
  change on a decline that was right both times.
- Stage 0's purpose holds: without the claim system, the agent can't adjudicate.

**Gate.** ✅ Proceed to stage 1 v2. Documents retrieved in every answer, 8 = 8 graded, and the corrected wording is in use.
