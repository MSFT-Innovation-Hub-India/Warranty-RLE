# Stage 4: the small model (first attempts, blocked)

**Status:** ⛔ blocked (2026-10-11 to 10-13): MAI-CODE-5b could not complete a claim on this platform
**Result in one line:** no valid measurement. Not one MAI-CODE-5b answer was usable, by either route; GPT-5.6-Sol completed the same claim at the same time.

## Goal

Measure a small model on the configuration the Sol stages produce, with grader scores and correctness side by side, to find the headroom for skill fixes and fine-tuning. These first attempts used the stage 0 configuration, when this was still stage 1; the climb was reordered on 2026-10-13 to refine the skill and rubrics with Sol first.

## How the attempts went

| Date (UTC) | Route | What happened | Platform issue |
| --- | --- | --- | --- |
| 10-11 06:51–07:00 | Evaluation job, MAI by name | `500 ER99000`; no job created | [P10](../../docs/06-platform-issues.md#p10-every-call-naming-mai-code-5b-fails-with-500-er99000) |
| 10-11 07:04 | Evaluation job, MAI by GUID | Accepted, but every claim-system call failed ("virtualization error"); job later marked `Failed` (`Rest401`) | [P11](../../docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error) |
| 10-11 08:05–09:58 | Evaluation job: MAI by GUID again, GPT-5.4-Mini, and MAI over the legacy connection | `500` / `507 ER99000`; no job created | P10 |
| 10-12 to 10-13 | Evaluation jobs, MAI by GUID (one with MAI selected via `models set`) | Accepted; 0 claim-system calls reached the MCP server; 14–69 min per claim | P11 |
| 10-13 03:03 | Direct execution (`executions run`), read-only question | ✅ MAI and Sol both fetched the claim record correctly | — |
| 10-13 07:38 | `executions run`, 5 claims at once | Claim-system calls worked, but every claim was cut off at ~15 min ("The result of this call was not received before the turn was interrupted") or ran 53 min with no answer | — |
| 10-13 08:33 | `executions run`, 1 claim alone | MAI produced nothing for 11 min; interrupted | — |
| 10-13 09:09 | Same claim with Sol, same route | ✅ Correct, 4 min, rubric 0.95 | — |

Every command and response: [RUNBOOK.md](RUNBOOK.md) (evaluation-job attempts). Executions-route files: [raw/run/](raw/run/), [raw/run-single/](raw/run-single/).

## Findings

| Issue | What we did |
| --- | --- |
| MAI-CODE-5b fails or stalls by every route; Sol does not | Stopped spending on MAI; to raise with the platform team (dev-capacity endpoints `dev-ct-…`; ~15-minute turn limit) |
| Evaluation jobs block MAI's claim-system calls; direct executions don't | `scripts/exec-batches.ps1` runs claims through `executions run`, with rubric grading (`--strategy simple`) |
| `models set` to select MAI failed on 10-11 and worked on 10-13 | MAI left enabled alongside Sol until the Sol stages, then disabled to keep stage 0's settings |

## Next

Resume after the Sol stages (1–3) settle the skill and rubrics, and once MAI-CODE-5b answers a single claim within a few minutes. Start with one claim, then the 30 evaluation claims with repeats.
