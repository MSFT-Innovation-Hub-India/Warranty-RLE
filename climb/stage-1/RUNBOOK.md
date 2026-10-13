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
```
