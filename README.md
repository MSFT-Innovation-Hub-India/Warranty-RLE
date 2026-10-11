# Contoso Industrial: warranty adjudication RLE

A Microsoft 365 **Frontier Tuning** world where an agent adjudicates warranty claims for a fictional industrial manufacturer, using a SharePoint library, Teams channels and a claim system. The repository records a **hill climb**: measure a frontier model, measure a small model, and close the gap one change at a time, up to reinforcement fine-tuning. Everything is synthetic.

## Where we are

| | |
| --- | --- |
| **Status** (2026-10-11) | Attempt 2. **[Stage 0](climb/stage-0/README.md) closed: the baseline.** GPT-5.6-Sol gets 29/30 claims right (checked against the answer key), rubric score 0.956. Attempt 1 is [archived](archive/attempt-1/README.md) |
| **Next** | Stage 1: the same use case and configuration with MAI-CODE-5b. **Blocked**: every call naming MAI-CODE-5b returns `500 ER99000` ([P10](docs/06-platform-issues.md#p10-every-call-naming-mai-code-5b-fails-with-500-er99000)); pre-flight done, nothing run |
| **Blockers** | Tuning excludes the claim-system tools ([P7](docs/06-platform-issues.md#p7-tuning-excludes-the-claim-system-tools)): blocks stage 4 · Starting a tuning job may disable the skill's rubrics ([P9](docs/06-platform-issues.md#p9-rubrics-found-disabled-evaluation-refused-er07018)) · Re-enable SQL public access before each run (switched off daily) |
| **CLI** | 1.0.14 (switched from 0.3.17 on 2026-10-10; scripts updated and checked, [docs/05 § CLI version](docs/05-operations.md#cli-version)). Attempt 1's tuning job `c77feaed` cancelled 2026-10-10 |
| **IDs** | Environment `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` · skill `cf00d339-5217-4cd1-b390-cc0d911735da` · MCP `1c171d49-7f85-4997-8126-ae20829a4dbf` |

## What's where

| Folder | Open it to… |
| --- | --- |
| [docs/](docs/README.md) | Understand the scenario, the configuration, the claim flow, the method, how to run things, and platform issues |
| [climb/](climb/README.md) | See the stages: scoreboard, and per stage the goal, results, findings (`README.md`) and every command run (`RUNBOOK.md`) |
| [scripts/](scripts/README.md) | Run an evaluation, score it, reset the claim database |
| [world-builder/](world-builder/README.md) | Rebuild or redeploy the world: spec, ground-truth engine, generators, corpus, MCP server code |
| [archive/attempt-1/](archive/attempt-1/README.md) | See the first climb and why it stalled |

[AGENTS.md](AGENTS.md) holds the working rules and the link to the Frontier Tuning CLI documentation.
