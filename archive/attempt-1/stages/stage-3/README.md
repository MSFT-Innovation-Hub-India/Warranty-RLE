# Stage 3: headroom (world v3, MAI-CODE-5b)

**Status:** stopped at the user's request, 2026-10-09. BestOfN probe completed: **0.900 · correct 1/1**. Full BestOfN batch failed before claim execution and was cancelled with **zero completed/graded claims**. **Headroom is unmeasured; stage 3 gate not passed.** No tuning started.

## The one change

Compare **Simple versus BestOfN, N = 4**, on MAI-CODE-5b (`dev-ct-mai-code-mp`), with the same skill, rubric snapshots and **29 claims** (04130 excluded, as agreed).

Stage 2b regressed, so both arms use the stronger **stage 1 skill**, pinned in [warranty-assistant.md](warranty-assistant.md). This is a return to the stronger measured configuration, not an improvement credited to stage 3. [Rubrics](warranty-assistant.rubrics.json), [original 30 prompts](samples.jsonl) and [sample IDs](sample-map.json) are retained from stage 1; the runner filters 04130. Neither Training samples nor the model change.

🖥️ Live instructions verified against the pin after CRLF normalisation. All six rubric scoring definitions match; server category/type metadata differs from the original authored JSON but was unchanged by restoration. Existing Evaluation sample IDs (and their rubric snapshots) are reused. [Verification](../../docs/evidence/stage-3/configuration-check.txt).

## Before the full run

1. Restore stage 1 instructions; verify rubrics unchanged.
2. Verify SQL baseline **0 0 0 0**.
3. Run a one-claim BestOfN probe (04101, N = 4), verifying server strategy and evidence of multiple rollouts, not merely CLI acceptance.
4. Inspect the result shape before committing to a full BestOfN run. If candidate answers are unavailable, label “right in any of N” unavailable rather than infer it from the selected answer.

Probe job: `44945388-1e87-41b5-adfd-32123fe29268`. 🖥️ Completed at **09:55 IST**, about **68 minutes** after submission: **0.900 · correct 1/1**, payable INR 69,575. Result metadata confirms **BestOfN, n=4**. Returned data contains only the selected execution, not four candidate answers; actual candidate count and “correct in any of N” are **not independently verifiable**. Execution diagnostics returned 404. Evidence: [probe](../../docs/evidence/stage-3/probe/), [ground-truth check](probe/ground-truth-check.md).

## Commands

```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
$map = Get-Content stages\stage-3\sample-map.json -Raw | ConvertFrom-Json
$probe = ($map | Where-Object { $_.claim -eq 'C-2026-04101' }).id
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\eval-batches.ps1 -Env $e -Samples '' -OutDir docs\evidence\stage-3\probe -Strategy BestOfN -BestOfN 4 -TimeoutMin 75 -MaxAttempts 1 -AdoptJob 44945388-1e87-41b5-adfd-32123fe29268 -AdoptSamples "04101=$probe"
# BestOfN comparison against the existing stage 1 Simple baseline:
$pairs = ($map | Where-Object { $_.claim -ne 'C-2026-04130' } | ForEach-Object { "$($_.claim.Substring(7))=$($_.id)" }) -join ','
powershell.exe -NoProfile -ExecutionPolicy Bypass -File stages\stage-3\run.ps1
```

[run.ps1](run.ps1) runs only BestOfN, batches of 5, two attempts maximum per claim, 30-minute no-completion stall threshold, hard job budget 180 minutes. This budget reflects the 68-minute probe, not an expected finish time. Any SQL error, unknown submission or exhausted claim stops the experiment. Raw per-job results are retained. The probe and cancelled fresh Simple job are excluded from full-arm metrics.

The probe is a capability check, not a full-cohort headroom result. Compare BestOfN with stage 1's existing Simple results, excluding 04130 from both. **This is a historical comparison:** model, skill, scoring definitions and claims match, but run dates, runner safeguards, stall thresholds and retry budgets differ. It does not isolate strategy from all operational/run-to-run variation.

## Measures and gate

| Measure | Why |
| --- | --- |
| Mean rubric and fully correct selected answers | Reward headroom versus real correctness |
| Correct in any candidate, if accessible | Distinguish model capacity from grader selection |
| Failed/non-answers, tokens, time and tool calls | Expose operational recovery and extra cost |
| Sample coverage and retries | Do not hide exclusions or compare different retained cohorts |

No meaningful correctness/reward gap → do not tune. Reward rises without correctness → investigate reward alignment before RFT. A positive gap is evidence of headroom, not a guarantee of tuning gains.

## Findings

| Issue | What we did |
| --- | --- |
| Stage 2b was weaker than stage 1 | Restored stage 1 instructions for both stage 3 arms, preserving rubrics and samples |
| Runner could block inside a CLI call and silently ignore SQL failure | Added bounded child-process calls, remaining-deadline poll limits, nonzero SQL exit propagation, pre-run/post-reset clean-baseline guards, explicit cancellation reconciliation, and incomplete-run failure |
| Foundry skill dependency bootstrap tried installing an extension incompatible with azd 1.25.1 | Recorded failure; no azd upgrade or Foundry workflow used. This scenario uses the existing Frontier Tuning CLI 0.3.16 |
| A 10-second Windows process-startup test timed out | Repeated success/failure tests with 60-second allowance; separate one-second timeout test passed. SQL deliberate failure exits 1; clean baseline exits 0 |
| First Windows PowerShell 5.1 monitor lost the child exit code despite valid diagnostics | Cached process handle, tested success/nonzero/timeout and real diagnostics in 5.1; resumed same platform job with a 65-minute remaining monitor budget, no duplicate submission |
| BestOfN probe completed but exposes only the selected execution; execution diagnostics returned 404 | Proceed with service-labelled BestOfN comparison; do not claim visibility into all four candidates or report an oracle “correct in any” ceiling |
| Fresh Simple repeated the already-measured stage 1 configuration without advancing the hill climb | Stopped local orchestration, cancelled job `008103c3-727c-4d2e-97dc-9630a8754c67`, verified terminal cancellation, and reused matched stage 1 baseline; keep cancelled-run evidence separate |
| Full BestOfN batch hit `HttpRequestException` at 10:19 IST before any of five claims started; service scheduled a five-minute retry | User requested cancellation rather than more waiting; stopped orchestration, cancelled job `729ff2cd-5096-4f87-8026-638043f68019`, verified terminal cancellation, snapshot/reset/baseline passed 0 0 0 0 |
| Per-command stdout/stderr captures inflated the pending commit | Consolidated 122 captures into three ZIP archives with filename/length/SHA-256 manifests; verified every original byte before removing loose copies. Named results, diagnostics and database evidence remain readable |

## Result

**No cohort headroom result.** The one-claim probe establishes a service-labelled BestOfN result, not a meaningful tuning target. Moving directly to RFT requires explicit acknowledgement of skipping the repository's headroom prerequisite and labelling any run an unverified pilot, not a gate-passed hill climb. No RFT started.
