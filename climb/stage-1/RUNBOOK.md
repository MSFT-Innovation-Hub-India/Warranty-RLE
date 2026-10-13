# Stage 1 runbook: commands and responses

Every command **exactly as run**, in order, from the repository root, each followed by its response. *(trimmed)* marks a shortened response; full output is in [raw/](raw/). To replay the stage, run the commands in order.

| | |
| --- | --- |
| Date | 2026-10-13 (UTC) |
| CLI | `frontier-tuning, version 1.0.14 (2026-10-09)`, `transport = public` |
| Environment | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` |
| Skill | `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da` |
| Model | `prod-gpt-56-reasoning-sol` (GPT-5.6-Sol) · strategy `Simple` · batches of 10 |

---

## 0. Set up the stage folder (bash)

```bash
mkdir -p climb/stage-1/config climb/stage-1/results climb/stage-1/raw && cp climb/stage-0/config/* climb/stage-1/config/ && diff -rq climb/stage-0/config climb/stage-1/config && echo "config identical to stage 0"
```
```text
config identical to stage 0
```
Check the Training claims are in the answer key and don't overlap the Evaluation claims:
```text
60 training claims; 60 in answer key; overlap with eval: 0
```

## 1. Pre-flight · 09:35 UTC (15:05 IST)

### 1.1 Model selection back to stage 0's state

MAI-CODE-5b had been selected on 2026-10-13 during the [stage 4](../stage-4/README.md) attempts.
```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $d='climb\stage-1\raw'
frontier-tuning -e $e models set 00000000-0000-0000-8000-100000000004 --disabled -o json
frontier-tuning -e $e models list
```
```text
{ "isEnabled": false, "id": "00000000-0000-0000-8000-100000000004", "alias": "dev-ct-mai-code-mp", "displayName": "MAI-CODE-5b", "name": "dev-ct-mai-code-mp", "isSelected": false }
Selected: ✓ only on prod-gpt-56-reasoning-sol   (trimmed: raw/preflight-models.txt)
```

### 1.2 The 60 Training samples are live

```powershell
frontier-tuning -e $e samples list --limit 500 -o json | Set-Content "$d\preflight-samples.json"
# then: match the 60 IDs in config/training-sample-ids.json against the list (label, skill, prompt names the claim)
```
```text
training samples live: 60/60
labels: Training=60 | skill ok: 60
prompt mismatches: 0
```

### 1.3 Configuration, database, jobs, MCP server

```powershell
.\.venv\Scripts\python.exe scripts\check-live-config.py climb\stage-1\config
.\scripts\sql-run.ps1 -File scripts\db-table-counts.sql
frontier-tuning -e $e evaluate list --limit 3 -o json      # summarised
curl.exe -s -m 30 https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz
```
```text
ALL MATCH
Claims 92 | ClaimAdjudicationDraft 0 | EvidenceRequest 0 | GoodwillEscalation 0   (trimmed)
eval 918aa6d8-… Cancelled dev-ct-mai-code-mp · 97ffce1a-… Cancelled · deafd25f-… Succeeded   (no job active)
{"status":"ok","assets":117}
```

## 2. Run the 60 Training claims · 09:37 UTC (15:07 IST)

```powershell
$ids = Get-Content climb\stage-1\config\training-sample-ids.json -Raw | ConvertFrom-Json; $s = ($ids | % { "$($_.claim.Substring(7))=$($_.id)" }) -join ','
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples $s -OutDir climb\stage-1\raw\run -Model prod-gpt-56-reasoning-sol -BatchSize 10
```
```text
15:08:28 04104+04105+04106+04107+04108+04111+04112+04113+04119+04120 job f18010c9-07a9-4244-9048-88928a2fef52 started
15:29:24 04104+…+04120 Succeeded after 21 min · 15:51:02 04121+…+04134 Succeeded after 20 min · 16:12:36 04135+…+04147 Succeeded after 20 min
16:14:05 04154+04155+04156+04157+04158+04159+04160+04161+04162+04163 job 9243f112-3b92-406b-9e68-21edc1ce8fdd started   (trimmed)
```

### 2.1 ❌ The claim system never reached · 10:52 UTC

A preview score of the first 30 showed Sol asking for evidence on almost every claim:
```bash
.venv/Scripts/python.exe scripts/score_ground_truth.py climb/stage-1/raw/run/results-*.json --out <scratch> --label "stage 1 preview"
```
```text
| C-2026-04107 | covered-simple | approve → request_evidence ❌ | … | 0.875 | ❌ |
| C-2026-04111 | declined-simple | decline → request_evidence ❌ | … | 0.875 | ❌ |   (trimmed: 3 of 30 right)
```
Sol's answers said why: "the service claim system was not available through the connected tools", and (04111) "I could not submit the prompt to the requested `warranty-assistant` skill because that skill is not available in this execution environment".

The platform's own view looked normal, the same as stage 0's job `2697a580…`:
```text
f18010c9-… snapshot: skills=1 tools=3 ks=4 | trigger=cf00d339:1 | toolCalls succeeded 235, failed 1
```
The claims are in the database (`C-2026-04 90` rows, e.g. `C-2026-04107 CIE-2200-AC-00324 Submitted`). But our MCP server's logs, all replicas, 09:30–10:59 UTC:
```text
      6 ListToolsRequest      (0 CallToolRequest)
```
Evaluation jobs no longer deliver claim-system calls, for Sol as well as MAI ([P11](../../docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error)). The runner was stopped before job 5; job 4 ran to completion (11:04 UTC, `Succeeded`), its results were saved, and the database was snapshotted and reset by hand (`0 0 0`). Nothing was cancelled. The 40 results stay in [raw/run/](raw/run/) as evidence; they are **not** used.

## 3. Re-run through `executions run` · 11:05 UTC (16:35 IST)

The route that worked for Sol earlier the same day ([stage 4](../stage-4/README.md)). Same skill, rubrics, claims and model; `--strategy simple` grades against the rubrics.
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\exec-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -SamplesFile climb\stage-1\config\training-samples.jsonl -OutDir climb\stage-1\raw\run-exec -Model prod-gpt-56-reasoning-sol -Parallel 5
```
```text
16:35:47 60 claims, model prod-gpt-56-reasoning-sol, 5 at a time
16:35:54 04104+04105+04106+04107+04108 started
16:38:54   04104 Completed in 3 min: rubric 1.000 (5 graded), tools 13 (claim system 2, not completed 0)
16:38:54   04105 Completed in 3 min: rubric 1.000 (5 graded), tools 10 (claim system 2, not completed 0)
16:40:41   04106 Completed in 5 min: rubric 0.900 (5 graded), tools 16 (claim system 3, not completed 1)
16:40:41   04107 Completed in 5 min: rubric 0.950 (5 graded), tools 9 (claim system 1, not completed 0)
16:40:41   04108 Completed in 5 min: rubric 0.600 (5 graded), tools 8 (claim system 1, not completed 0)
16:41:06 04104+04105+04106+04107+04108 done: DB snapshot saved and reset
```
✅ Claim-system calls complete. Full log: [raw/run-exec/run-log.txt](raw/run-exec/run-log.txt).
