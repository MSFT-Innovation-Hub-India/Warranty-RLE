# Stage 2 runbook: commands and responses

Every command **exactly as run**, in order, from the repository root, each followed by its response. *(trimmed)* marks a shortened response; full output is in [raw/](raw/).

| | |
| --- | --- |
| Date | 2026-10-13 (UTC) |
| CLI | `frontier-tuning, version 1.0.14 (2026-10-09)`, `transport = public` |
| Environment | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` |
| Skill | `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da` |
| Model | `prod-gpt-56-reasoning-sol` (GPT-5.6-Sol) · `executions run --strategy simple` · 5 at a time |

---

## 0. Set up the stage folder (bash)

```bash
mkdir -p climb/stage-2/config climb/stage-2/results climb/stage-2/raw && cp climb/stage-1/config/* climb/stage-2/config/
```
Then edit `config/rubrics.json`: Authority and action items 1, 2, 4 and Valuation accuracy item 3 (text in [config/rubrics.md](config/rubrics.md#stage-2-changes-2026-10-13)).

## 1. Check the skill against the new rubrics

```bash
.venv/Scripts/python.exe scripts/check-skill.py climb/stage-2/config/skill.md climb/stage-2/config/rubrics.json
```
```text
OK: no rubric phrases, no claim-specific answers
```

## 2. Apply the two rubric changes · 12:23 UTC (17:53 IST)

Snapshot first: `frontier-tuning -e <env> skills rubrics cf00d339-… -o json > climb/stage-2/raw/rubrics-live-before.json`.
```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $sid='cf00d339-5217-4cd1-b390-cc0d911735da'; $r = Get-Content climb\stage-2\config\rubrics.json -Raw | ConvertFrom-Json
$map = @{ 'Authority and action'='c64e109d-baeb-4377-9724-0feeb3eb95b7'; 'Valuation accuracy'='3f15471d-00d4-496e-bb87-faa37cca9fb9' }
foreach ($name in $map.Keys) { $items = ($r | ? { $_.RubricName -eq $name }).ChecklistItems; $a = @('-e',$e,'rubrics','update',$map[$name],'--skill-id',$sid,'-o','json'); foreach ($i in $items) { $a += '--checklist-item'; $a += $i }; & frontier-tuning @a }
```
```text
12:23:24 UTC update Authority and action (4 items)   → { "id": "c64e109d-…", "displayName": "Authority and action", "checklistItems": [ … ] }
12:24:10 UTC update Valuation accuracy (5 items)     → { "id": "3f15471d-…", "displayName": "Valuation accuracy", "checklistItems": [ … ] }   (trimmed: raw/rubric-update-*.json)
```

## 3. Verify: only the two rubrics changed

The CLI warns that changing a checklist "makes the service revise the skill's rubric set to stay consistent", so every rubric was compared.
```bash
.venv/Scripts/python.exe scripts/check-live-config.py climb/stage-2/config
frontier-tuning -e 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 skills rubrics cf00d339-5217-4cd1-b390-cc0d911735da -o json > climb/stage-2/raw/rubrics-live-after.json
# then compare before/after per rubric (items, importance, enabled, red flags)
```
```text
instructions match config/skill.md: True
rubrics: live 6, pinned 6   (each: items ok, importance ok, enabled ok)
evaluation samples: 30/30 present; wrong type or skill: none
ALL MATCH
same    Coverage determination · Precedence discipline · Evidence grounding · Gaps reported, not filled
CHANGED Valuation accuracy · Authority and action
```

## 4. Run the 60 Training claims · 12:25 UTC (17:55 IST)

Database `0 0 0` ([raw/preflight-db-counts.txt](raw/preflight-db-counts.txt)); no runner active.
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\exec-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -SamplesFile climb\stage-2\config\training-samples.jsonl -OutDir climb\stage-2\raw\run -Model prod-gpt-56-reasoning-sol -Parallel 5
```
