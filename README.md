# Contoso Industrial: warranty adjudication RLE

A Microsoft 365 **Frontier Tuning** world: an agent adjudicates warranty claims for a fictional industrial manufacturer, reading a SharePoint library, Teams channels and a claim system. The repository records a **hill climb** on that world, from a naive start to reinforcement fine-tuning, one change per stage. Everything is **synthetic**.

**Start here:** [docs/JOURNEY.md](docs/JOURNEY.md).

## What's where

| Folder | What it's for | When you open it |
| --- | --- | --- |
| [docs/](docs/README.md) | `JOURNEY.md`: the scenario, where the climb stands, what we've learned. `evidence/`: the verbatim record | Always: this is the story |
| [stages/](stages/README.md) | One folder per climb stage: skill, pinned rubrics, prompts, commands, result, findings | To see or replay a stage |
| [scripts/](scripts/) | Climb helpers: run evaluations in batches, summarise and score a stage, reset the claim database | When running a stage |
| [world-builder/](world-builder/README.md) | Everything that creates and deploys the world: spec, ground-truth engine, generators, generated corpus and database, MCP server, build recipe | Only to rebuild or redeploy the world |

`AGENTS.md` holds the rules the work follows.

## Running a stage, in short

```powershell
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql                     # claim database clean: 0 0 0 0
powershell -File scripts\eval-sequential.ps1 -Env <world-id> -Samples <label=sampleId,...> -OutDir docs\evidence\stage-N -BatchSize 5
python scripts\summarise-stage.py docs\evidence\stage-N stages\stage-N --consolidate
```

The exact commands for each stage are in its README.
