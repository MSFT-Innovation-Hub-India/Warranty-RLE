# Stage 1 v2 — Switch on the claim system, on the corrected world

**Status:** ✅ done 2026-10-04. Job `95f7d234-df64-4e71-aa82-2d3db8d51b11`: **rubric 0.991 · fully correct 7/8**. ⚠️ Saturated.

**Why a v2.** The [v1 run](../stage-1/) found two defects that made its measurement unclean:

| Defect | Fix in v2 |
| --- | --- |
| 1. The world contradicted the answer key on inspection reports | World v2: TSB-G-0029, SPA clause 2 and one Teams reply corrected (see [stage-0-v2](../stage-0-v2/README.md#what-differs-from-stage-0-v1)) |
| 2. 2 of 8 runs got no MCP tools while the app scaled from 1 to 3 replicas mid-burst | Replicas pinned at 3 before the run (`--min-replicas 3 --max-replicas 3`, revision `--0000005`). This is environment hardening, not a change to the agent or the world |

## The one change (against stage 0 v2)

| | Stage 0 v2 | **Stage 1 v2** |
| --- | --- | --- |
| MCP server `contoso-service` (`1c171d49-7f85-4997-8126-ae20829a4dbf`) | disabled | **enabled** |

Skill, rubrics, samples, model and strategy are identical: the same files and hashes as [stage-0-v2](../stage-0-v2/).

## Run

As [stage 1](../stage-1/README.md#run): warm the DB, check the baseline (0 0 0 0), enable the MCP server, check that 137 tools are offered, evaluate, take both numbers, snapshot what the agent wrote, then reset.

## Results — 2026-10-04 · job `95f7d234-df64-4e71-aa82-2d3db8d51b11`

| | Stage 0 v2 | **Stage 1 v2** | Change | (v1 stage 1) |
| --- | --- | --- | --- | --- |
| **Rubric score (platform)** | 0.535 | **0.991** | **+0.456** | 0.905 |
| **Fully correct vs ground truth** | 0/8 | **7/8 (88%)** | +7 | 3/8 |
| Runs that used MCP tools | 0/8 | **8/8** (8–10 MCP calls each) | | 6/8 |
| Wall time | 26 min | 22 min (10:44 → 11:06 UTC) | | 52 min |

Detail: [ground-truth-check.md](ground-truth-check.md) · [eval-results.json](eval-results.json) · `eval-results-samples.json` · [db-actions-after-eval.txt](db-actions-after-eval.txt) (6 drafts, 1 evidence request; reset afterwards, baseline 0 0 0 0)

**Per rubric (platform)**

| Rubric | 0 v2 | **1 v2** |
| --- | --- | --- |
| Requested Outcome Delivery | 0.84 | 1.00 |
| Claim Determination Requirements | 0.43 | 0.975 |
| Internal Record Use and Grounding | 0.73 | 1.00 |
| Adjudicator-Ready Presentation and Traceability | 0.68 | 0.98 |
| Claim-System Draft Execution | 0.00 (n=5) | 1.00 (n=6) |

**Per claim**

| Claim | Expected | Got | Rubric | |
| --- | --- | --- | --- | --- |
| 04101 | approve ₹69,575 · ADD-IN-2.1 | the same | 1.0 | ✅ |
| 04102 | approve ₹48,420 · ADD-IN-2.1 | the same | 0.93 | ✅ (held in v1 for a missing report) |
| 04103 | approve ₹19,150 · ADD-IN-2.1 | **hold**: evidence request for the failure cause (clause 5.4) | **1.0** | ❌ world ambiguity, see below |
| 04109 | decline · ADD-IN-2.1 | the same | 1.0 | ✅ (the scorer first misread it, see below) |
| 04110 | decline · ADD-IN-2.1 | the same | 1.0 | ✅ |
| 04114 | approve ₹199,175 · TSB-C-0051 | the same | 1.0 | ✅ (no tools in v1) |
| 04116 | decline · ADD-IN-2.1 | the same | 1.0 | ✅ (no tools in v1) |
| 04118 | approve ₹67,500 · TSB-P-0112 | the same | 1.0 | ✅ (held in v1 for a missing report) |

**Both v1 defects are gone.** No claim was held for a missing inspection report, and all 8 runs got the tools.

**04103: a second world ambiguity.** Policy POL-WAR-4.2 clause 5.4 excludes *"seals fitted as
routine maintenance"*. 04103 is a seal kit (`SEAL-KIT-RR`, part P-22120). The claim record
(`get_claim`) carries only the op code, with no symptom or failure cause, and there's no inspection
report. The answer key approves, because the engine excludes only on `exclusion_flags`, which is
empty here. The agent wrote: *"the present record does not establish whether this was a covered
corrective repair or excluded routine maintenance"*, recorded draft `request_evidence` and an
evidence request, and computed the correct amount if covered (₹19,150). That is defensible from what
it could see, and consistent with the v2 wording ("an inspection report matters where an exclusion
depends on it"). Options:
(a) add a failure description to the claim record (the inspection-report texts already have one per op code);
(b) say in the policy that `*-RR` op codes are corrective repairs;
(c) leave it, and accept one ambiguous eval claim.
**Not changed: your decision.**

**Scorer fix.** 04109 says *"no draft adjudication, evidence request, or escalation was created"*. The
negation window (25 characters) didn't reach "escalation", so the scorer read it as an escalation.
Added a list-negation rule and 2 tests (25/25). Re-scoring changed no earlier stage's result.

**Reading the two numbers**
- **Plumbing was the whole gap on the easy slices.** +0.456 rubric, 0/8 → 7/8 correct, with only the MCP switch changed.
- ⚠️ **Saturated.** 0.991 is above AGENTS.md's ~0.95 line. These 8 prompts (covered-simple, declined-simple, precedence) have no headroom left for GPT-5.6-Sol with tools.
- **The rubrics don't check correctness.** The one wrong answer, 04103, scored 1.0 on every rubric. The generated rubrics reward a well-sourced, well-presented answer whether or not its decision matches the answer key. That is the case for stage 2's hand-written rubrics.

**Gate (runbook):** score up ≥ 0.10 ✅ · DB tools in the trace ✅ (8/8). **Passed, but saturated.**
Before stage 2: decide on 04103, and move to prompts with headroom (the hard slices).
