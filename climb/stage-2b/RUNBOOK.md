# Stage 2b runbook: commands and responses

Every command **exactly as run**, in order, from the repository root. *(trimmed)* marks a shortened response; full output is in [raw/](raw/).

| | |
| --- | --- |
| Date | 2026-10-14 (UTC) |
| CLI | `frontier-tuning, version 1.0.14 (2026-10-09)`, `transport = public` |
| Environment / skill | `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` / `cf00d339-5217-4cd1-b390-cc0d911735da` |
| Model | `prod-gpt-56-reasoning-sol` · `executions run --strategy simple` · 4 at a time |

## 1. World fix: `EvidenceRequest.field_name` · 04:50 UTC

In `world-builder/build/gen_db.py`, `field_name {ID}` → `field_name {NAME}` (`NVARCHAR(40)` → `NVARCHAR(200)`), then:
```bash
cd world-builder; ../.venv/Scripts/python.exe build/adjudicate.py; ../.venv/Scripts/python.exe build/test_traps.py; ../.venv/Scripts/python.exe build/gen_db.py
```
```text
All 14 checks passed - guide 03 section 8 reproduces.
31/31 checks passed.
  schema.sqlite.sql, seed.sqlite.sql, schema.azuresql.sql, seed.azuresql.sql, contoso.db
```
`git diff` on the generated SQL: one line, `field_name   NVARCHAR(40)` → `NVARCHAR(200)`. Live database (the first attempt hit "Database … is not currently available", the serverless resume; retried):
```powershell
.\scripts\sql-run.ps1 -Query "ALTER TABLE EvidenceRequest ALTER COLUMN field_name NVARCHAR(200) NOT NULL; SELECT c.name, t.name AS type, c.max_length/2 AS chars FROM sys.columns c JOIN sys.types t ON c.user_type_id=t.user_type_id WHERE c.object_id=OBJECT_ID('EvidenceRequest') AND c.name='field_name';"
```
```text
field_name nvarchar   200
```

## 2. Rubric: Valuation not applicable to asset-only questions · 04:54 UTC

`config/` copied from stage 2; every Valuation item's "When the claim is covered, " became "When the claim is covered and the question is about the claim rather than only an asset's warranty position, ".
```bash
.venv/Scripts/python.exe scripts/check-skill.py climb/stage-2b/config/skill.md climb/stage-2b/config/rubrics.json
```
```text
OK: no rubric phrases, no claim-specific answers
```
```powershell
$items = ((Get-Content climb\stage-2b\config\rubrics.json -Raw | ConvertFrom-Json) | ? { $_.RubricName -eq 'Valuation accuracy' }).ChecklistItems; $a=@('-e',$e,'rubrics','update','3f15471d-00d4-496e-bb87-faa37cca9fb9','--skill-id',$sid,'-o','json'); foreach ($i in $items) { $a += '--checklist-item'; $a += $i }; & frontier-tuning @a
.\.venv\Scripts\python.exe scripts\check-live-config.py climb\stage-2b\config
```
```text
ALL MATCH
```

## 3. Probes · 04:57 UTC (10:27 IST)

Database `0 0 0`. Prompts: [config/probe-prompts.jsonl](config/probe-prompts.jsonl).
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\exec-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -SamplesFile climb\stage-2b\config\probe-prompts.jsonl -OutDir climb\stage-2b\raw\run -Model prod-gpt-56-reasoning-sol -Parallel 4
```
```text
10:31:15   04174 Completed in 4 min: rubric 0.867 (5 graded), tools 16 (claim system 1, not completed 0)
10:31:15   04173 Completed in 4 min: rubric 1.000 (4 graded), tools 8 (claim system 2, not completed 0)
10:31:15   04157 Completed in 4 min: rubric 0.853 (5 graded), tools 9 (claim system 2, not completed 0)
10:31:15   04163 Completed in 4 min: rubric 0.853 (5 graded), tools 11 (claim system 2, not completed 0)
10:34:15   04119 Completed in 2 min: rubric 1.000 (3 graded), tools 5 (claim system 1, not completed 0)
10:34:41   04144 Completed in 3 min: rubric 0.783 (5 graded), tools 11 (claim system 1, not completed 0)
10:35:40   04170 Completed in 4 min: rubric 1.000 (5 graded), tools 13 (claim system 2, not completed 1)
10:36:13 ALL DONE
```
Per-rubric scores and recorded writes, compared with stage 2's normal-prompt runs of the same claims: see the README's results table.
