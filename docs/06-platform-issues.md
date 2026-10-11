# Platform issues

Every platform error or unexplained behaviour, with what the platform team needs to look into it. Newest first. How to handle an error is in [AGENTS.md § When the platform errors](../AGENTS.md#when-the-platform-errors); the CLI's own guidance is in the docs' [*API error diagnostics*](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1#api-error-diagnostics) and [troubleshooting playbook](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1/agent-guidance/playbooks/troubleshooting.html).

**Fixed context for every issue below:** environment `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` · skill `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da` · MCP server `contoso-service` `1c171d49-7f85-4997-8126-ae20829a4dbf` (NoAuth) · region of MCP host: South India.

| # | Issue | Status | First seen (UTC) |
| --- | --- | --- | --- |
| [P7](#p7-tuning-excludes-the-claim-system-tools) | Tuning excludes 36 tools "that can make changes"; the claim-system tools never appear in training rollouts | 🔬 Open, **blocks a meaningful RFT** | 2026-10-10 12:41 |
| [P11](#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error) | MAI-CODE-5b runs can't call the claim system ("virtualization error"); the calls never reach the MCP server | 🔴 Open, **blocks stage 1** | 2026-10-11 07:05 |
| [P10](#p10-every-call-naming-mai-code-5b-fails-with-500-er99000) | `evaluate start --base-model dev-ct-mai-code-mp` fails with `500 ER99000` | Workaround: pass the GUID `00000000-0000-0000-8000-100000000004` | 2026-10-11 06:51 |
| [P9](#p9-rubrics-found-disabled-evaluation-refused-er07018) | All six rubrics found disabled; `evaluate start` refused with `ER07018` | Fixed by re-enabling; cause 🔬 | 2026-10-11 01:51 |
| [P8](#p8-skipped-rubrics-reported-as-00-in-cli-10) | CLI 1.0 reports a rubric skipped as not applicable as `score: 0.0` | Worked around in our scripts | 2026-10-10 |
| [P6](#p6-tuning-step-fails-repeatedly-with-400) | Tuning step fails repeatedly with `400 We hit an internal error` | Closed: job cancelled 2026-10-10 17:45 UTC | 2026-10-09 12:50 |
| [P5](#p5-bestofn-evaluation-fails-before-any-claim-runs) | BestOfN evaluation fails before any claim runs (`HttpRequestException`) | Closed by cancellation; not reproduced | 2026-10-09 04:49 |
| [P4](#p4-submissions-time-out-but-succeed) | `tune start` and `skills refine start` time out on the reply but start server-side | Workaround: reconcile with `list` | 2026-10-07 |
| [P3](#p3-evaluation-claims-never-register-as-complete) | Evaluation claims finish but never register as complete; platform resubmits up to 6× | Workaround: runner cancels after 15 min idle | 2026-10-08 |
| [P2](#p2-finish-tool-rejects-correct-hand-ins) | Finish tool rejects correct hand-ins; a stub or the echoed question is graded | Reported 2026-10-06; open | 2026-10-05 |
| [P1](#p1-execution-diagnostics-unavailable) | Execution diagnostics API returns 403/404 | Open | 2026-10-05 |

---

## P11 MAI-CODE-5b runs cannot call the claim system ("virtualization error")

| Field | Value |
| --- | --- |
| CLI | 1.0.14 |
| Command | `evaluate start --sample-id 90dfe727-082c-4c06-bca9-6321b9382be4 --base-model 00000000-0000-0000-8000-100000000004 --strategy Simple --env-id 598fd1b0-…` (via `eval-batches.ps1`) |
| Job | `bf5947ad-dd49-4812-9305-b9fc13a2ce45`, claim C-2026-04101, 2026-10-11 07:04:58–07:33:23 UTC, `Succeeded` after 28 min. At 07:53:05 UTC the platform changed it to **`Failed`**, `errorCode: Rest401`, "Job execution failed with an unknown error." (`stages: []`, score kept at 0.4375) |
| Agent's answer | "I couldn't complete the adjudication for claim C-2026-04101 because the warranty assistant could not access the required claim-system dossier tool; it failed with a **virtualization error**." Rubric 0.4375 |
| Platform counters | `evaluate diagnostics` → `toolCalls: succeeded 4, failed 5, total 9` |
| Our MCP server | Healthy throughout (`/healthz` → `{"status":"ok","assets":117}`). Console logs of all 5 replicas (revision `contoso-service-mcp--0000007`): **no `CallToolRequest` between 07:00 and 07:33 UTC**, one `ListToolsRequest` at 07:27:26. During stage 0 (GPT-5.6-Sol, 01:58–03:47 UTC), tool calls did arrive (`CallToolRequest` at 03:26–03:42 in the retained log tail) |
| Retry (08:05 UTC) | The same command, same GUID, returned `500 ER99000` (transaction `7098a052-c09d-f81a-e17d-ec8fb2fdd798`); `evaluate list` at 08:06:50 showed no new job. The GUID that was accepted at 07:04 is now refused as well (see P10) |
| Reading | A `401` points to an authorization failure. The platform failed the claim-system calls for this MAI-CODE-5b execution before forwarding them to the MCP server. MAI-CODE-5b called the same server successfully in attempt 1 (2026-10-07 to 10-09) |
| Ask | (1) What is the "virtualization error" on `contoso-service` tool calls in `dev-ct-mai-code-mp` executions? (2) Why does it affect this model and not GPT-5.6-Sol, in the same environment on the same day? (3) What does `Rest401` on the job mean: which call was unauthorized? (4) Is it related to P7 (tools excluded from tuning) or P10 (two catalogue rows for the model)? |
| Evidence | [diagnostics.json](../climb/stage-1/raw/probe-guid/diagnostics.json) · [sample-detail.json](../climb/stage-1/raw/probe-guid/sample-detail.json) · [status-after.json](../climb/stage-1/raw/probe-guid/status-after.json) (the `Rest401`) · MCP replica logs in [climb/stage-1/raw/probe-guid/](../climb/stage-1/raw/probe-guid/) · retry: [runner-output.txt](../climb/stage-1/raw/probe-guid-2/runner-output.txt) |

## P10 Every call naming MAI-CODE-5b fails with 500 ER99000

| Field | Value |
| --- | --- |
| CLI | 1.0.14 |
| Window | 2026-10-11 06:51–07:00 UTC · every attempt exit 1 |
| Model | `dev-ct-mai-code-mp` (MAI-CODE-5b), catalogue IDs `00000000-0000-0000-8000-100000000004` and `dev-ct-mai-code-mp` |

| UTC | Command (sample IDs shortened) | Error | Transaction ID |
| --- | --- | --- | --- |
| 06:51:59 | `evaluate start --sample-id ×10 --base-model dev-ct-mai-code-mp --strategy Simple` | `API error (500): ER99000: An unknown error has occurred.` | `d4a49046-54b3-f8aa-e7d3-ecbf79b75029` |
| 06:54:32 | same, resubmitted once after reconciling | same | `cd0c5f3c-815d-0354-891b-1ac14219acc7` |
| 06:57:21 | `evaluate start --sample-id 90dfe727-… --base-model dev-ct-mai-code-mp --strategy Simple` (1 claim) | same | `e7f5cfad-8a0b-7815-acd0-5182e8c48c8a` |
| 06:59:22 | `models set dev-ct-mai-code-mp --enabled` | `API error (400): ER59004: modelId 'dev-ct-mai-code-mp' is invalid; it must contain a GUID.` | `0ed7d7a7-72f0-1507-c927-c49ee5dfe154` |
| 06:59:51 | `models set 00000000-0000-0000-8000-100000000004 --enabled` | `API error (500): ER99000: An unknown error has occurred.` | `eb6d2bee-935e-d4fc-f0d3-25fc8fab500b` |
| 08:05 | `evaluate start --sample-id 90dfe727-… --base-model 00000000-0000-0000-8000-100000000004 --strategy Simple` (1 claim; the GUID accepted at 07:04) | same | `7098a052-c09d-f81a-e17d-ec8fb2fdd798` |

| | |
| --- | --- |
| Reconciled | After each `evaluate start`, `evaluate list` showed no new job (newest: GPT-5.6-Sol `2697a580…`, 03:32 UTC). Nothing was charged; the claim database was untouched |
| Same environment, same hour | GPT-5.6-Sol evaluations succeeded 01:58–03:47 UTC (7 jobs); `ping` and `auth check` OK |
| Environment model state | `models list` → `trainingModels`: `prod-gpt-56-reasoning-sol` `isEnabled: true, isSelected: true`; both MAI entries `isEnabled: false`. Same on 2026-10-10 17:58 UTC. MAI-CODE-5b evaluated successfully in this environment on 2026-10-07 to 10-09 (attempt 1); when it was disabled is unknown |
| Workaround (07:04 UTC, worked once) | `--base-model 00000000-0000-0000-8000-100000000004` (MAI-CODE-5b's GUID ID) is accepted: job `bf5947ad-dd49-4812-9305-b9fc13a2ce45`. The model list has two MAI rows (IDs `0000…0004` and `dev-ct-mai-code-mp`); the CLI submits the matched ID, and the name-style ID fails. For GPT-5.6-Sol the name-style ID is the selected row, and it works |
| Ask | (1) Why do the two catalogue rows for one model behave differently, and why a 500 rather than a clear error? (2) Why do `evaluate start` and `models set` return 500 for it rather than a clear error? (3) Must a model be enabled with `models set` before `evaluate start --base-model` can use it? |

## P9 Rubrics found disabled; evaluation refused (ER07018)

| Field | Value |
| --- | --- |
| CLI | 1.0.14 |
| Command | `frontier-tuning --output json evaluate start --sample-id 90dfe727-082c-4c06-bca9-6321b9382be4 --base-model prod-gpt-56-reasoning-sol --strategy Simple --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4` (via `eval-batches.ps1`) |
| Window | 2026-10-11 01:50:41–01:51:28 UTC · exit 1 |
| Error | `API error (400): ER07018: None of the selected samples are eligible for evaluation based on their attached skills.` |
| Transaction ID | `10611f24-b671-3788-a09b-681656a26987` |
| State found | The sample was fine (Evaluation, attached to the skill) and the skill was enabled, but **all six rubrics were `isEnabled: false`**. Skill `lastModifiedDateTime` 2026-10-09 08:43:44 UTC, 5 s before the tuning job `c77feaed` logged `FINE_TUNING_STARTED … Preparing your training examples` (08:43:49). The last successful evaluation (`44945388`) was created before that, at 03:17 UTC |
| Likely cause 🔬 | Starting the tuning job disabled the skill's rubrics. Unconfirmed |
| Fix | `rubrics update <id> --skill-id … --enable` for all six (01:54:57 UTC); content unchanged. Resubmission accepted (job `da0fd79d-8bbc-466c-9cf7-b480054bf96a`) |
| Ask | Does `tune start` disable a skill's rubrics? If so, why, and should it re-enable them afterwards? The ER07018 message could name the cause ("no enabled rubrics") |

## P8 Skipped rubrics reported as 0.0 in CLI 1.0

| Field | Value |
| --- | --- |
| CLI | 1.0.14 (0.3.17 for comparison) |
| Command | `frontier-tuning -e 598fd1b0-… -o json evaluate results 9abbbeb3-424c-4093-bdb7-91936cf8fa3d --samples` (also `-o json-legacy` and `--schema samples-v1`) |
| Reported | For C-2026-04140 (a correct decline), *Valuation accuracy* and *Gaps reported* come back as `score: 0.0`, `scoreReason: ""`. 0.3.17 returned the same rubrics as `Score: null` with a `Skip` reason ("…covered-claim valuation requirements were not triggered") |
| Impact | Anyone averaging the per-rubric scores would penalise every decline and hold. The help text says "a null score is unmeasured", but the null is not preserved |
| Our handling | Use the submission's `score` (it excludes skipped rubrics: 0.6875 = mean of the four graded) and treat `0.0` + empty reason as skipped |
| Ask | Preserve `null` and the skip reason for skipped rubrics in CLI 1.0 JSON output |

## P7 Tuning excludes the claim-system tools

| Field | Value |
| --- | --- |
| CLI | 0.3.17 |
| Command | `frontier-tuning --output json tune diagnostics c77feaed-96de-4b88-9802-e0f265601eb8 --include-metrics --env-id 598fd1b0-…` |
| Job | tuning `c77feaed-96de-4b88-9802-e0f265601eb8`, base `mai-code-1-flash` |
| Window | 2026-10-10 12:41:50 → 16:32:32 UTC |
| Reported | `Tools provided by the agent: 100` · `TOOLS_EXCLUDED_FOR_SAFETY: Tools not used because they can make changes: 36` · `Tools enabled for training: 64` |
| What we see | The step-1 tool usage lists 30+ tools (SharePoint, Teams, `m365__search_enterprise_files`, `lumina_sandbox__*`) but **none of the four `contoso-service` tools**, including the read-only `get_claim_dossier`, which every evaluation run calls first. Training reward at step 1: **0.358** |
| Likely cause 🔬 | Our MCP tools carry no MCP annotations (no `readOnlyHint`), and the registration has `AnnotatedActions: []`, so the service may treat all four as mutating. Not confirmed |
| Impact | Without the claim dossier no claim can be adjudicated, so the model is being trained on a different task from the one it is evaluated on |
| Ask | (1) Which 36 tools were excluded, and why? (2) Is `get_claim_dossier` excluded? (3) How should a remote MCP server mark read-only tools so tuning keeps them (MCP `readOnlyHint`? `AnnotatedActions`?) (4) How can draft-only write tools be allowed, or simulated, during training? |
| Evidence | [tune-diagnostics-2026-10-10.json](../archive/attempt-1/evidence/stage-4/tune-diagnostics-2026-10-10.json) |

## P6 Tuning step fails repeatedly with 400

| Field | Value |
| --- | --- |
| CLI | 0.3.17 |
| Commands | `tune status` / `tune diagnostics c77feaed-96de-4b88-9802-e0f265601eb8 --include-metrics` |
| Job | `c77feaed-96de-4b88-9802-e0f265601eb8`, submitted 2026-10-09 05:29:38 UTC |
| Reported | `Stages[ModelTraining].Errors: [{Code: "400", Message: "Job execution failed with an unknown error."}]`. Log: `StepFailed` + `400 We hit an internal error and will retry automatically.` at 10-09 12:50, 15:25, 20:46; 10-10 06:48, 10:34, 17:07. Training stage `attempts: 4, failedAttempts: 3` (as of 17:33). `MODEL_TRAINING_FAILED: Model training did not complete.` at 10-10 16:58, after model training had started at 12:53 and reported a step-1 reward |
| Status at last read | 2026-10-10 17:33 UTC: `Running`, retry scheduled in ~123 min, `readyForEvaluation: false`. Status `UpdatedAt` still shows the creation time, so it can't be used to tell progress |
| Closed | Cancelled at the user's request: `tune cancel` 17:44:39 UTC → `CancelRequested`; `tune status` 17:45:28 → `Cancelled`, `isTerminal: true` ([after-cancel status](../archive/attempt-1/evidence/stage-4/tune-status-after-cancel-2026-10-10.json)) |
| Transaction ID | None returned (the error is in the job, not a CLI response) |
| Ask | What is failing in the Training step, and is it related to P7? |
| Evidence | [tune-status-2026-10-10.json](../archive/attempt-1/evidence/stage-4/tune-status-2026-10-10.json) · [tune-diagnostics-2026-10-10.json](../archive/attempt-1/evidence/stage-4/tune-diagnostics-2026-10-10.json) |

## P5 BestOfN evaluation fails before any claim runs

| Field | Value |
| --- | --- |
| CLI | 0.3.17 |
| Command | `evaluate start --strategy BestOfN --best-of-n 4` on 5 claims (via `scripts/eval-batches.ps1`) |
| Job | `729ff2cd-5096-4f87-8026-638043f68019`, created 2026-10-09 04:40:17 UTC |
| Reported | `StandaloneEvaluation` step failed at 04:49:12; `HttpRequestException` *"We hit an internal error and will retry automatically."* (TransientIssue, retryable); `StepRetryScheduled` ~5 min. Zero claims started |
| What we did | Cancelled at the user's request; status `Cancelled` verified; database clean |
| Context | A 1-claim BestOfN probe (`44945388-1e87-41b5-adfd-32123fe29268`) completed the same morning in 68 min and reported `BestOfN, n=4`, but returned only the selected answer |
| Evidence | [diagnostics-before-cancel.json](../archive/attempt-1/evidence/stage-3/bestofn/diagnostics-before-cancel.json) · [cancel-status.json](../archive/attempt-1/evidence/stage-3/bestofn/cancel-status.json) |

## P4 Submissions time out but succeed

| Field | Value |
| --- | --- |
| Commands | `skills refine start --skill-id … --sample-id ×17` (2026-10-07 ~13:20 UTC) · `tune start --base-model mai-code-1-flash …` (2026-10-09 05:29 UTC) |
| Reported | `Error: ReadTimeout: submission outcome is unknown` |
| Reality | Both had started server-side: refinement `588f45c8-cd74-4bfc-9522-b334933d8211`, tuning `c77feaed-…` |
| What to do | Never resubmit. Reconcile with `skills refine list` / `tune list`, as the CLI message says |

## P3 Evaluation claims never register as complete

| Field | Value |
| --- | --- |
| Job | `6032038e-…` (2026-10-08); claims C-2026-04140, 04141, 04149 |
| Reported | `Resubmissions: 6`. The agent finished each attempt and wrote a draft every ~20 min, but the execution never became complete; job timed out at 60 min |
| Also | Attempt 1 stage 2: claim 04130 stalled twice; one retry batch ran 216 min |
| Workaround | `scripts/eval-batches.ps1` cancels a job with no progress for 15 min, keeps finished claims, requeues the rest |

## P2 Finish tool rejects correct hand-ins

Full report as sent: [platform-issue-finish-rejection.md](../archive/attempt-1/evidence/platform-issue-finish-rejection.md). In short: the finish tool rejects the agent's final answer (seen with GPT-5.4-Mini 22/28, MAI-CODE-5b in several runs, GPT-5.6-Sol 0/62); the graded answer becomes a stub, an inability message or the echoed question. Cost on MAI-CODE-5b: 4–6 claims per 30-claim run. Ask: the finish tool's schema and validation rules, and which answer is graded after a rejection.

## P1 Execution diagnostics unavailable

`executions diagnostics <id>` → `403 The execution diagnostics API is not enabled` (2026-10-05); for the BestOfN probe → `404` (2026-10-09). `executions get` returns not-found for evaluation execution IDs. Rejected finish attempts therefore can't be inspected.
