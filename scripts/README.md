# Scripts

Everything needed to run, score and reset a stage. How they fit together: [docs/05-operations.md](../docs/05-operations.md).

| Script | Kind | What it does | Used |
| --- | --- | --- | --- |
| [eval-batches.ps1](eval-batches.ps1) | Runner | Submits evaluation jobs in batches of 5, heals stalls (cancel after 15 min idle, requeue unfinished claims), snapshots and resets the database after each job, fails closed on SQL errors | Every stage |
| [summarise-stage.py](summarise-stage.py) | Reporting | Merges a run's per-job results into one file, writes `run-summary.md`, runs the scorer | After every run |
| [score_ground_truth.py](score_ground_truth.py) | Scoring | Checks each answer's decision, governing instrument and payable against `world-builder/out/data/claims.json`. Deterministic; marks unreadable answers for review | After every run |
| [test_score_ground_truth.py](test_score_ground_truth.py) | Test | Extraction checks for the scorer | After changing the scorer |
| [check-skill.py](check-skill.py) | Guard | Fails if a skill shares a 5-word phrase with the rubrics, or contains claim numbers, serials or amounts | Before applying any skill change |
| [sql-run.ps1](sql-run.ps1) | Database | Runs a SQL file or query on the claim database with your Entra token | Wrapper for the three below |
| [db-baseline.sql](db-baseline.sql) | Database | Counts agent writes; `0 0 0 0` = clean | Before every run |
| [db-actions-snapshot.sql](db-actions-snapshot.sql) | Database | Lists what the agent wrote | After every job |
| [db-reset-actions.sql](db-reset-actions.sql) | Database | Removes agent writes, restores seeded claim statuses | After every snapshot |

Python runs from the repository's `.venv` (`.\.venv\Scripts\python.exe`). SQL runs under Windows PowerShell 5.1, which ships with `System.Data.SqlClient`.

One-off scripts from attempt 1 (`run.ps1`, `safeguard-tests.ps1`, `consolidate-captures.ps1`) stay in `archive/attempt-1/` and are not needed.
