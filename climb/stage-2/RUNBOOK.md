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
```text
17:56:10 60 claims, model prod-gpt-56-reasoning-sol, 5 at a time
17:56:18 04104+04105+04106+04107+04108 started
…
18:46:45   04190 Completed in 4 min: rubric 1.000 (5 graded), tools 16 (claim system 2, not completed 0)   (trimmed: 60 Completed, no failures; raw/run/run-log.txt)
```

## 5. Score · 13:16 UTC

```bash
.venv/Scripts/python.exe scripts/score_ground_truth.py climb/stage-2/raw/run/result-*.json --out climb/stage-2/results --label "Stage 2: GPT-5.6-Sol, 60 Training claims, revised Authority and Valuation rubrics"
```
First pass: **52/60**, 8 to check. Hand-check: 7 were misreads (04119, 04144 "still under warranty"; 04137 "no … goodwill escalation is needed"; 04173, 04175 decline with a goodwill escalation recorded; 04180 "cannot presently be approved or declined"; 04185 exclusion bulletin read as governing), 1 real miss (04147: all searches returned nothing). The scorer was fixed (71/71 tests) and re-run:
```text
| **Fully correct** | **59/60 (98%)** |
| Mean rubric score (platform) | 0.94 |
```
```bash
.venv/Scripts/python.exe scripts/reward-ranking.py climb/stage-2/results
```
```text
correct (with hand-check): 59 of 60
mean rubric: right 0.941 · wrong 0.875
right ranked above wrong: 51 of 59 pairs (86%); ties 3
  wrong: C-2026-04147 rubric 0.875 - outscores 5 of 59 right answers
```
The failed claim-system calls (all `request_missing_evidence`, first attempt) show `String or binary data would be truncated in table 'contoso-warranty.dbo.EvidenceRequest', column 'field_name'`: the column is `NVARCHAR(40)` in `world-builder/out/db/seed.azuresql.sql`.
