# Stage 3 runbook: commands and responses

Every command **exactly as run**, in order, from the repository root. *(trimmed)* marks a shortened response; full output is in [raw/](raw/).

| | |
| --- | --- |
| Date | 2026-10-14 (UTC) |
| CLI | `frontier-tuning, version 1.0.14 (2026-10-09)`, `transport = public` |
| Environment / skill | `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` / `cf00d339-5217-4cd1-b390-cc0d911735da` |
| Model | `prod-gpt-56-reasoning-sol` · `executions run --strategy simple` · 5 at a time |

## 1. The skill edit (bash)

```bash
mkdir -p climb/stage-3/config climb/stage-3/results climb/stage-3/raw && cp climb/stage-2b/config/* climb/stage-3/config/ && rm climb/stage-3/config/probe-prompts.jsonl
# edit climb/stage-3/config/skill.md: one line (see README)
diff climb/stage-2b/config/skill.md climb/stage-3/config/skill.md
.venv/Scripts/python.exe scripts/check-skill.py climb/stage-3/config/skill.md climb/stage-3/config/rubrics.json
```
```text
30c30
< - where the outcome calls for an action in the claim system, record it there as a draft and say what you recorded
---
> - whenever you are asked about a specific claim, however the question is put, finish by recording the matching draft in the claim system (an adjudication, an evidence request or a goodwill escalation) and say what you recorded; a question only about an asset's warranty position needs no draft
OK: no rubric phrases, no claim-specific answers
```

## 2. Apply and verify · 05:47 UTC (11:17 IST)

```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $sid='cf00d339-5217-4cd1-b390-cc0d911735da'
frontier-tuning -e $e skills get $sid -o json | Set-Content climb\stage-3\raw\skill-live-before.json
$md = Get-Content climb\stage-3\config\skill.md -Raw; $instr = $md.Substring($md.IndexOf('## Instructions') + '## Instructions'.Length).Trim()
frontier-tuning -e $e skills update $sid --prompt $instr -o json | Set-Content climb\stage-3\raw\skill-update.json
.\.venv\Scripts\python.exe scripts\check-live-config.py climb\stage-3\config
.\scripts\sql-run.ps1 -File scripts\db-table-counts.sql
```
```text
instructions match config/skill.md: True
rubrics: live 6, pinned 6   (each: items ok, importance ok, enabled ok)
ALL MATCH
ClaimAdjudicationDraft 0 | EvidenceRequest 0 | GoodwillEscalation 0   (trimmed)
```

## 3. Run the 60 Training claims · 05:48 UTC (11:18 IST)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\exec-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -SamplesFile climb\stage-3\config\training-samples.jsonl -OutDir climb\stage-3\raw\run -Model prod-gpt-56-reasoning-sol -Parallel 5
```
