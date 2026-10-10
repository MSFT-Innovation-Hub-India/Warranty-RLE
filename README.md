# Contoso Industrial: warranty adjudication RLE

A Microsoft 365 **Frontier Tuning** world where an agent adjudicates warranty claims for a fictional industrial manufacturer, using a SharePoint library, Teams channels and a claim system. The repository records a **hill climb**: measure a frontier model, measure a small model, and close the gap one change at a time, up to reinforcement fine-tuning. Everything is synthetic.

## Where we are

| | |
| --- | --- |
| **Status** (2026-10-10) | Climb restarted as **attempt 2**. Attempt 1 is [archived](archive/attempt-1/README.md): it stalled after stage 1 (best: 0.637 · 23/30 on MAI-CODE-5b). Stage 0 (GPT-5.6-Sol reference) is set up, not yet run |
| **Next** | [Stage 0](climb/stage-0/README.md): run GPT-5.6-Sol on the 30 claims |
| **Blockers** | Attempt 1's tuning job `c77feaed` is still active (training retrying after repeated `400`s), so the database must not be reset ([P6](docs/06-platform-issues.md#p6-tuning-step-fails-repeatedly-with-400)) · Tuning excludes the claim-system tools ([P7](docs/06-platform-issues.md#p7-tuning-excludes-the-claim-system-tools)): blocks stage 4 · SQL public access is off (daily); re-enable before a run |
| **CLI** | Installed 0.3.17; docs describe 1.0.14 ([docs/05 § CLI version](docs/05-operations.md#cli-version)) |
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
