# Stage 1 runbook: commands and responses

Every command **exactly as run**, in order, from the repository root in PowerShell 7, each followed by its response. *(trimmed)* marks a shortened response; full output is in [raw/](raw/). To replay the stage, run the commands in order.

| | |
| --- | --- |
| Date | 2026-10-11 (UTC) |
| CLI | `frontier-tuning, version 1.0.14 (2026-10-09)` |
| Environment | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` |
| Skill | `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da` |
| Model | `dev-ct-mai-code-mp` (MAI-CODE-5b) · strategy `Simple` · batches of 10 |

---

## 0. Set up the stage folder

The configuration is copied unchanged from stage 0.

```bash
mkdir -p climb/stage-1/config climb/stage-1/results climb/stage-1/raw && cp climb/stage-0/config/* climb/stage-1/config/
diff -rq climb/stage-0/config climb/stage-1/config && echo "config identical to stage 0"
```
```text
config identical to stage 0
```

---

## 1. Pre-flight · 06:48 UTC (12:18 IST)

### 1.1 CLI and sign-in

```powershell
frontier-tuning --version
frontier-tuning auth check
```
```text
frontier-tuning, version 1.0.14 (2026-10-09)
https://aka.ms/ft-cli/start#1014
✓ Frontier Tuning authentication is ready.
```

### 1.2 MCP server and database reachable

```powershell
curl.exe -s -m 60 https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz
```
```text
{"status":"ok","assets":117}
```

### 1.3 Database state

```powershell
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql | Tee-Object climb\stage-1\raw\preflight-db-baseline.txt
.\scripts\sql-run.ps1 -File scripts\db-table-counts.sql | Tee-Object climb\stage-1\raw\preflight-db-counts.txt
```
```text
drafts evidence_requests escalations claims_not_seeded
     0                 0           0                 0

tbl                       n
Dealers                   4
Parts                    14
Assets                  117
AssetTelemetry         3007
Claims                   92
ServiceHistory           89
GoodwillAuthority         4
TsbApplicability          4
ClaimAdjudicationDraft    0
EvidenceRequest           0
GoodwillEscalation        0
```

### 1.4 Re-seed anyway · 06:49 UTC

The database was clean, but the re-seed takes 20 s and guarantees stage 1 starts from exactly the data stage 0 did.

```powershell
.\scripts\sql-run.ps1 -File world-builder\out\db\seed.azuresql.sql | Tee-Object climb\stage-1\raw\db-reseed.txt
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql
```
```text
OK: 8 batch(es) executed
drafts evidence_requests escalations claims_not_seeded
     0                 0           0                 0
```

### 1.5 Live skill, rubrics and samples match `config/`

```powershell
.\.venv\Scripts\python.exe scripts\check-live-config.py climb\stage-1\config | Tee-Object climb\stage-1\raw\preflight-config-check.txt
```
```text
instructions match config/skill.md: True
rubrics: live 6, pinned 6
  Authority and action: items ok, importance ok, enabled ok
  Coverage determination: items ok, importance ok, enabled ok
  Evidence grounding: items ok, importance ok, enabled ok
  Gaps reported, not filled: items ok, importance ok, enabled ok
  Precedence discipline: items ok, importance ok, enabled ok
  Valuation accuracy: items ok, importance ok, enabled ok
evaluation samples: 30/30 present; wrong type or skill: none
ALL MATCH
```

### 1.6 No other job active

```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
$ev = frontier-tuning -e $e evaluate list --limit 3 -o json | Out-String; ($ev.Substring($ev.IndexOf('[')) | ConvertFrom-Json) | ForEach-Object { "eval $($_.id) $($_.status)" }
$tu = frontier-tuning -e $e tune list --limit 3 -o json | Out-String; ($tu.Substring($tu.IndexOf('[')) | ConvertFrom-Json) | ForEach-Object { "tune $($_.jobId ?? $_.id) $($_.status)" }
```
```text
eval 2697a580-0671-49b5-b76f-f34041f22277 Succeeded
eval 4bae38ee-051b-4bf5-9faf-d71eb2d30b0b Succeeded
eval 11178c7e-6b40-4ce6-986f-8addb4e17da1 Succeeded
tune c77feaed-96de-4b88-9802-e0f265601eb8 Cancelled
```

✅ Pre-flight passed.

---

## 2. Run all 30 claims · 06:50 UTC (12:20 IST)

No smoke test: the pipeline was proven in stage 0, and MAI-CODE-5b ran on this environment in attempt 1. The first job serves as the check.

Batches of **10** (stage 0 used 5). In stage 0 every job took 14 min whether it held 4 or 5 claims, so claims within a job run in parallel and the time is mostly per-job overhead. Batch size doesn't change any answer: each claim is its own execution.

```powershell
$s = (Get-Content climb\stage-1\config\eval-sample-ids.json -Raw | ConvertFrom-Json | ForEach-Object { "$($_.claim.Substring(7))=$($_.id)" }) -join ','
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples $s -OutDir climb\stage-1\raw\run -Model dev-ct-mai-code-mp -BatchSize 10
```

**Response · 06:51:59 UTC: refused**, exit 1 (runner output, trimmed):
```text
Command failed (1): frontier-tuning --output json evaluate start --sample-id 90dfe727-082c-4c06-bca9-6321b9382be4 … (10 sample IDs) --base-model dev-ct-mai-code-mp --strategy Simple --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
Error: API error (500): ER99000: An unknown error has occurred.
The request outcome is unknown; it was not retried. Inspect the resource before submitting again.
Transaction ID: d4a49046-54b3-f8aa-e7d3-ecbf79b75029
Submission outcome is unknown; the operation may have started server-side. Do not retry the start or cancel automatically. Reconcile first with:
  frontier-tuning -e 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json evaluate list
```

### 2.1 Reconcile · 06:52 UTC

```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
$ev = frontier-tuning -e $e evaluate list --limit 3 -o json | Out-String; ($ev.Substring($ev.IndexOf('[')) | ConvertFrom-Json) | ForEach-Object { "eval $($_.id) $($_.status) $($_.inputModelName) $($_.createdDateTime)" }
frontier-tuning ping
```
```text
eval 2697a580-0671-49b5-b76f-f34041f22277 Succeeded prod-gpt-56-reasoning-sol 10/11/2026 09:02:35
eval 4bae38ee-051b-4bf5-9faf-d71eb2d30b0b Succeeded prod-gpt-56-reasoning-sol 10/11/2026 08:47:23
eval 11178c7e-6b40-4ce6-986f-8addb4e17da1 Succeeded prod-gpt-56-reasoning-sol 10/11/2026 08:32:14
✓ Auth:  sansri@microsoft.com
✓ https://substrate.office.com/KnowledgeGraph/api/v1.0/Environments/598fd1b0-36f1-402f-ba36-aa00c8a67cc4  3602ms
```
No job was created; the service is reachable.

### 2.2 Resubmit once · 06:53 UTC

Same command as step 2. Response: the same `500 ER99000`, transaction ID `cd0c5f3c-815d-0354-891b-1ac14219acc7`. Reconciled again: no job created.

### 2.3 One claim, to rule out batch size · 06:57 UTC

```powershell
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples '04101=90dfe727-082c-4c06-bca9-6321b9382be4' -OutDir climb\stage-1
aw\probe -Model dev-ct-mai-code-mp -BatchSize 1 -MaxAttempts 1
```
```text
Error: API error (500): ER99000: An unknown error has occurred.
Transaction ID: e7f5cfad-8a0b-7815-acd0-5182e8c48c8a
```
Not batch size. Reconciled: no job created.

### 2.4 The environment's model settings · 06:58 UTC

```powershell
$m = frontier-tuning -e $e models list -o json | Out-String; $o = $m.Substring($m.IndexOf('{')) | ConvertFrom-Json
$o.trainingModels | Where-Object { $_.name -in 'dev-ct-mai-code-mp','prod-gpt-56-reasoning-sol' } | ForEach-Object { "$($_.id) | $($_.name) | enabled=$($_.isEnabled) selected=$($_.isSelected)" }
```
```text
00000000-0000-0000-8000-100000000005 | prod-gpt-56-reasoning-sol | enabled=False selected=False
00000000-0000-0000-8000-100000000004 | dev-ct-mai-code-mp | enabled=False selected=False
dev-ct-mai-code-mp | dev-ct-mai-code-mp | enabled=False selected=False
prod-gpt-56-reasoning-sol | prod-gpt-56-reasoning-sol | enabled=True selected=True
```
Only GPT-5.6-Sol is enabled for this environment, which was already the case on 10-10 (stage 0's saved model list).

### 2.5 Try to enable MAI-CODE-5b · 06:59 UTC

```powershell
frontier-tuning -e $e models set dev-ct-mai-code-mp --enabled -o json
frontier-tuning -e $e models set 00000000-0000-0000-8000-100000000004 --enabled -o json
```
```text
Error: API error (400): ER59004: modelId 'dev-ct-mai-code-mp' is invalid; it must contain a GUID.
Transaction ID: 0ed7d7a7-72f0-1507-c927-c49ee5dfe154

Error: API error (500): ER99000: An unknown error has occurred.
The request outcome is unknown; it was not retried. Inspect the resource before submitting again.
Transaction ID: eb6d2bee-935e-d4fc-f0d3-25fc8fab500b
```
`models list` afterwards: unchanged.

⛔ **Stopped.** Every call that names MAI-CODE-5b returns `500 ER99000`, while GPT-5.6-Sol worked in this environment two hours earlier. A platform-side problem; recorded as [P10](../../docs/06-platform-issues.md#p10-every-call-naming-mai-code-5b-fails-with-500-er99000) with all transaction IDs. Nothing ran, nothing was charged, and the database is still at the seeded state.

---

## 3. Score

## 4. Close

---

## Dead ends

| What | Result |
| --- | --- |
| `evaluate start` with MAI-CODE-5b, ×3 (10 claims, 10 claims, 1 claim) | `500 ER99000` each time; no job created |
| `models set` to enable MAI-CODE-5b, by name and by GUID | `400 ER59004` (needs a GUID), then `500 ER99000` |
