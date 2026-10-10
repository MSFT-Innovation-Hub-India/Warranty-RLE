# Operations runbook

How to run any stage: checks before a run, the run itself, scoring, and the database reset. The scripts are described one by one in [scripts/README.md](../scripts/README.md). Stage-specific commands go in each stage's `RUNBOOK.md`.

## Before every run

| # | Check | Command | Expect |
| --- | --- | --- | --- |
| 1 | CLI installed and signed in | `frontier-tuning --version` · `frontier-tuning check` (0.3.17; `auth check` in 1.0) | Version noted in the stage RUNBOOK |
| 2 | Azure CLI signed in (for SQL) | `az account show` | Your account |
| 3 | SQL reachable | Public network access on `az-sqldb-common` is switched off daily (SFI): re-enable it, and add your IP to the firewall | — |
| 4 | MCP server healthy | `curl https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz` | `"status":"ok"`. `degraded` with `Login timeout expired` means step 3 isn't done |
| 5 | Database clean | `.\scripts\sql-run.ps1 -File scripts\db-baseline.sql` | `0 0 0 0` |
| 6 | Live skill and rubrics match the stage's `config/` | `frontier-tuning skills get <skill-id> --env-id <env> -o json` (compare instructions and the six rubrics) | Identical after newline normalisation |
| 7 | No other job active in the environment | `frontier-tuning evaluate list` · `frontier-tuning tune list` | Nothing `Running` that writes to the database |

## Running an evaluation

Claims run in **batches of 5 per job**: each job pays ~9 minutes of platform start-up, so one claim per job wastes most of the time. The runner submits one job at a time, cancels a job that makes no progress for 15 minutes, keeps the finished claims, requeues the rest (up to 3 attempts), and snapshots and resets the database after every job.

```powershell
$e = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
$s = (Get-Content climb\stage-N\config\eval-sample-ids.json -Raw | ConvertFrom-Json |
      ForEach-Object { "$($_.claim.Substring(7))=$($_.id)" }) -join ','       # "04101=<id>,04102=<id>,…"
powershell -File scripts\eval-batches.ps1 -Env $e -Samples $s -OutDir climb\stage-N\raw -Model <model-id> -BatchSize 5
```

| Option | Default | Use |
| --- | --- | --- |
| `-Model` | `dev-ct-mai-code-mp` | `prod-gpt-56-reasoning-sol` for the frontier reference |
| `-Strategy` / `-BestOfN` | `Simple` / 4 | Inference-strategy comparisons |
| `-StallMin` / `-TimeoutMin` / `-MaxAttempts` | 15 / 75 / 3 | Stall handling |
| `-AdoptJob` / `-AdoptSamples` | — | Take over a job already running instead of submitting a new one |

Timing 🖥️: 5 claims take 20–27 minutes per job on MAI-CODE-5b when nothing stalls; 30 claims about 2.5–3 hours.

## Scoring a run

```powershell
python scripts\summarise-stage.py climb\stage-N\raw climb\stage-N\results --consolidate
```

This merges the per-job results into `results/eval-results-samples.json`, writes `results/run-summary.md` (per claim: rubric score, calls, minutes) and runs the ground-truth scorer, which writes `results/ground-truth-check.md` and `.csv`. Then **read every answer the scorer marks ❓ or ❌** and record the outcome in the stage README.

The scorer on its own: `python scripts\score_ground_truth.py <results.json> --out <folder>`. Its tests: `python scripts\test_score_ground_truth.py`.

## The claim database

The agent's draft writes persist in Azure SQL, so every run must start from the seeded state.

| When | Script | What it does |
| --- | --- | --- |
| Before a run | [db-baseline.sql](../scripts/db-baseline.sql) | Counts drafts, evidence requests, escalations, and claims not in their seeded status. Must be `0 0 0 0` |
| After each job | [db-actions-snapshot.sql](../scripts/db-actions-snapshot.sql) | Lists everything the agent wrote (kept with the results as evidence) |
| After the snapshot | [db-reset-actions.sql](../scripts/db-reset-actions.sql) | Empties the three action tables and puts claim statuses back to seeded |
| Full rebuild (rare) | `world-builder/out/db/seed.azuresql.sql` | Recreates and reseeds the whole database |

All are run with `.\scripts\sql-run.ps1 -File <file>`, which signs in with your Azure CLI token (Entra-only, no passwords). The runner does snapshot and reset automatically after each job.

⚠️ **Never reset while a job is running.** An evaluation or tuning job may still write. Check `evaluate list` / `tune list` first.

## Checking a long-running job

| Job | Status | Detail |
| --- | --- | --- |
| Evaluation | `evaluate status <id> -o json` | `evaluate diagnostics <id> -o json` · `evaluate results <id> --samples -o json` |
| Tuning | `tune status <id> -o json` (ready when `readyForEvaluation: true`) | `tune diagnostics <id> --include-metrics -o json` |
| Refinement | `skills refine status <id>` | `skills refine detail <id> -o json` |

A job's `UpdatedAt` may not move while it progresses; use the diagnostics' `lastProgressDateTime` and log. A timeout in our tooling never cancels the job. Errors go in [06-platform-issues.md](06-platform-issues.md).

## CLI version

Installed on 2026-10-10: **0.3.17**. The [docs](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1) describe **1.0.14**, which adds `skills refine --mode instruction|rubrics|both`, `evaluate sample-results`, and **camelCase JSON**. The runner and scorer read PascalCase fields, so after an upgrade use `-o json-legacy` or update them first. Upgrade only between stages, and record the version in the RUNBOOK.
