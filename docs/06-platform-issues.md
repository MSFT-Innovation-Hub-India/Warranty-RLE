# Platform issues

Every platform error or unexplained behaviour, with what the platform team needs to look into it. Newest first. How to handle an error is in [AGENTS.md § When the platform errors](../AGENTS.md#when-the-platform-errors); the CLI's own guidance is in the docs' [*API error diagnostics*](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1#api-error-diagnostics) and [troubleshooting playbook](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1/agent-guidance/playbooks/troubleshooting.html).

**Fixed context for every issue below:** environment `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` · skill `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da` · MCP server `contoso-service` `1c171d49-7f85-4997-8126-ae20829a4dbf` (NoAuth) · region of MCP host: South India.

| # | Issue | Status | First seen (UTC) |
| --- | --- | --- | --- |
| [P7](#p7-tuning-excludes-the-claim-system-tools) | Tuning excludes 36 tools "that can make changes"; the claim-system tools never appear in training rollouts | 🔬 Open, **blocks a meaningful RFT** | 2026-10-10 12:41 |
| [P6](#p6-tuning-step-fails-repeatedly-with-400) | Tuning step fails repeatedly with `400 We hit an internal error` | Open, job still retrying | 2026-10-09 12:50 |
| [P5](#p5-bestofn-evaluation-fails-before-any-claim-runs) | BestOfN evaluation fails before any claim runs (`HttpRequestException`) | Closed by cancellation; not reproduced | 2026-10-09 04:49 |
| [P4](#p4-submissions-time-out-but-succeed) | `tune start` and `skills refine start` time out on the reply but start server-side | Workaround: reconcile with `list` | 2026-10-07 |
| [P3](#p3-evaluation-claims-never-register-as-complete) | Evaluation claims finish but never register as complete; platform resubmits up to 6× | Workaround: runner cancels after 15 min idle | 2026-10-08 |
| [P2](#p2-finish-tool-rejects-correct-hand-ins) | Finish tool rejects correct hand-ins; a stub or the echoed question is graded | Reported 2026-10-06; open | 2026-10-05 |
| [P1](#p1-execution-diagnostics-unavailable) | Execution diagnostics API returns 403/404 | Open | 2026-10-05 |

---

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
