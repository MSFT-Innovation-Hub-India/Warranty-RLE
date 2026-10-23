# Contoso Industrial: warranty adjudication RLE

A Microsoft 365 **Frontier Tuning** world where an agent adjudicates warranty claims for a fictional industrial manufacturer, using a SharePoint library, Teams channels and a claim system. The repository records a **hill climb**: measure a frontier model, measure a small model, and close the gap one change at a time, up to reinforcement fine-tuning. Everything is synthetic.

**Presenting the project?** Start with the [journey and demo guide](docs/07-journey-and-demo-guide.md): the business story, measured progression, Streamlit launch command, CLI examples, multiple-skill routing and the platform's value proposition.

## Where we are

| | |
| --- | --- |
| **Status** (2026-10-13) | Attempt 2. **[Stage 0](climb/stage-0/README.md) closed: the baseline.** GPT-5.6-Sol gets 29/30 claims right (checked against the answer key), rubric score 0.956. **Climb reordered:** the skill and rubrics are refined with Sol first (stages 1–3), then the small model is measured (stage 4) and tuned (stage 5) ([method § 3](docs/04-hill-climb-method.md#3-the-stages)) |
| **Now** | [Stage 3](climb/stage-3/README.md) closed: a skill line on recording the draft cut claim questions with no draft from 11 to 6; correctness 59/60 on the Training claims. Next: stage 3b (record even when asked for advice), then the 30 Evaluation claims on the final configuration. All runs use `executions run` ([P11](docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error)) |
| **Small model** | First attempts are recorded in [stage 4](climb/stage-4/README.md): MAI-CODE-5b could not complete a claim by any route on 10-11 to 10-13 ([P10](docs/06-platform-issues.md#p10-every-call-naming-mai-code-5b-fails-with-500-er99000), [P11](docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error)); Sol completed the same claim. To raise with the platform team |
| **Blockers** | Tuning excludes the claim-system tools ([P7](docs/06-platform-issues.md#p7-tuning-excludes-the-claim-system-tools)): blocks stage 5 · Starting a tuning job may disable the skill's rubrics ([P9](docs/06-platform-issues.md#p9-rubrics-found-disabled-evaluation-refused-er07018)) · Re-enable SQL public access before each run (switched off daily) |
| **CLI** | 1.0.14 (switched from 0.3.17 on 2026-10-10; scripts updated and checked, [docs/05 § CLI version](docs/05-operations.md#cli-version)). Attempt 1's tuning job `c77feaed` cancelled 2026-10-10 |
| **IDs** | Environment `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` · skill `cf00d339-5217-4cd1-b390-cc0d911735da` · MCP `1c171d49-7f85-4997-8126-ae20829a4dbf` |

**Demo (2026-10-22), not a climb stage:** 🖥️ GPT-5.6-Sol with TreeSearch on C-2026-04101 completed in 5m49s (execution `c9fffec9-426a-4eca-93b6-2b0616acd810`). Mean scored rubric 1.000; answer-key checks passed for decision, governing instrument and payable (approve INR 69,575). Five draft writes were snapshotted, then the database was reset to `0 0 0 0`. This single-claim demo is not evidence of improvement over Simple.

**Local console (2026-10-23):** [Streamlit CLI UI](ui/README.md) for inspecting live skills/rubrics, running Simple/TreeSearch/BestOfN with explicit approval, reopening saved executions, viewing formatted responses and raw JSON, and guarded database snapshot/reset. This adds tooling, not a new climb measurement.

## What's where

| Folder | Open it to… |
| --- | --- |
| [docs/](docs/README.md) | Understand the scenario, the configuration, the claim flow, the method, how to run things, and platform issues |
| [climb/](climb/README.md) | See the stages: scoreboard, and per stage the goal, results, findings (`README.md`) and every command run (`RUNBOOK.md`) |
| [scripts/](scripts/README.md) | Run an evaluation, score it, reset the claim database |
| [ui/](ui/README.md) | Use the local Streamlit console for CLI executions, results and database controls |
| [world-builder/](world-builder/README.md) | Rebuild or redeploy the world: spec, ground-truth engine, generators, corpus, MCP server code |
| [archive/attempt-1/](archive/attempt-1/README.md) | See the first climb and why it stalled |

[AGENTS.md](AGENTS.md) holds the working rules and the link to the Frontier Tuning CLI documentation.
