# Stage 1: switch on the claim system

**Result:** rubric **0.991** · correct **7/8** · 2026-10-04 · job `95f7d234-df64-4e71-aa82-2d3db8d51b11` · ✅ gate passed · ⚠️ saturated

## The change (against stage 0)
The MCP server `contoso-service` is **enabled** (9 read + 3 write tools on Azure SQL). Skill, rubrics, samples, model and strategy are unchanged (same files and hashes).

## Apply and run
```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $sk='cf00d339-5217-4cd1-b390-cc0d911735da'
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql                      # expect 0 0 0 0
frontier-tuning tools enable 1c171d49-7f85-4997-8126-ae20829a4dbf --env-id $e
frontier-tuning tools available --env-id $e -o json                       # re-read until the count is stable
frontier-tuning evaluate start --skill-id $sk --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $e -o json
frontier-tuning evaluate results <job> --samples --env-id $e -o json > stages\stage-1\eval-results-samples.json
.\.venv\Scripts\python.exe build\score_ground_truth.py stages\stage-1\eval-results-samples.json --out stages\stage-1
.\scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql > stages\stage-1\db-actions-after-eval.txt
.\scripts\sql-run.ps1 -File scripts\db-reset-actions.sql
```

## Result
| | Stage 0 | **Stage 1** |
| --- | --- | --- |
| Rubric score | 0.535 | **0.991** (+0.456) |
| Correct (ground truth) | 0/8 | **7/8** |
| Runs that used the claim system | 0/8 | 8/8 (8–10 MCP calls each) |

Detail: [ground-truth-check.md](ground-truth-check.md) · [eval-results.json](eval-results.json) · [db-actions-after-eval.txt](db-actions-after-eval.txt).

## Findings
| Issue | What we did |
| --- | --- |
| In the first run, 2 of 8 runs got no MCP tools while the server scaled up mid-burst | Pinned the MCP container app's replicas (3, later 5) before evaluating |
| 04103 (a seal kit) was held: policy 5.4 excluded "seals fitted as routine maintenance", and nothing said which this was. Rubrics gave the miss **1.0** | **World v2.1:** clause 5.4 now says a consumable claimed under a warranty repair code is a corrective repair |
| **The generated rubrics don't check correctness** | Hand-written rubrics drafted ([rubrics-v2-draft.md](../rubrics-v2-draft.md)); ground truth reported every stage |
| From this stage the agent writes to the database | Snapshot and reset after every run (`scripts/db-*.sql`) |
| ⚠️ 0.991 on 8 easy prompts: no headroom | Stage 2 uses all 30 eval prompts |
