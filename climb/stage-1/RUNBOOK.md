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

### 2.6 Use the model's GUID as `--base-model` · 07:04 UTC (12:34 IST)

Insight from the evaluation model list: MAI-CODE-5b appears twice, once with ID `00000000-0000-0000-8000-100000000004` and once with ID `dev-ct-mai-code-mp`. The CLI submits the *ID* it matches, and an ID beats a name, so `--base-model dev-ct-mai-code-mp` submitted the name-style row. For GPT-5.6-Sol the same rule picked the row marked selected (✓), which is why stage 0 worked. `models set` had already said a model ID "must contain a GUID".

```powershell
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples '04101=90dfe727-082c-4c06-bca9-6321b9382be4' -OutDir climb\stage-1\raw\probe-guid -Model 00000000-0000-0000-8000-100000000004 -BatchSize 1 -MaxAttempts 1
```
```text
12:35:05 04101 job bf5947ad-dd49-4812-9305-b9fc13a2ce45 started
```
```powershell
frontier-tuning -e 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 evaluate list --limit 2 -o json     # summarised
```
```text
eval bf5947ad-dd49-4812-9305-b9fc13a2ce45 Running dev-ct-mai-code-mp 10/11/2026 12:34:58
```
✅ **Accepted.** For MAI-CODE-5b, pass the GUID `00000000-0000-0000-8000-100000000004`.

### 2.7 The probe's result · 07:33 UTC (13:03 IST)

```text
13:03:23 04101 Succeeded after 28 min
13:04:11 04101 done (job bf5947ad-dd49-4812-9305-b9fc13a2ce45): 1/1 finished; DB snapshot saved and reset
13:04:11 ALL DONE
```
```powershell
$f='climb\stage-1\raw\probe-guid\results-04101.json'; $t=Get-Content $f -Raw; $o=$t.Substring($t.IndexOf('{')) | ConvertFrom-Json; $s=$o.submissions[0]
"score=$($s.score) status=$($s.status) calls=$($s.execution.billingSummary.toolInvocations)"; $s.execution.response
```
```text
score=0.4375 status=Graded calls=6
I couldn't complete the adjudication for claim **C-2026-04101** because the warranty assistant could not access the required claim-system dossier tool; it failed with a virtualization error. No claim documents were otherwise available to evaluate.
Please retry when the claim-system integration is available, or provide the claim dossier and applicable supporting documents.
```
❌ **Not a valid measurement**: the claim-system tool failed inside the platform.

### 2.8 Where the tool call failed · 07:40 UTC

```powershell
$t = frontier-tuning -e 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json evaluate diagnostics bf5947ad-dd49-4812-9305-b9fc13a2ce45 | Out-String
$t | Set-Content climb\stage-1\raw\probe-guid\diagnostics.json -Encoding utf8
($t.Substring($t.IndexOf('{')) | ConvertFrom-Json).reliability | ConvertTo-Json -Depth 4 -Compress
curl.exe -s -m 30 https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz
```
```text
{"availability":"Current", … "toolCalls":{"succeeded":4,"failed":5,"rejected":0,"cancelled":0,"pending":0,"terminal":9,"total":9,"passRate":0.444…,"averageLatencyMs":1131}, …}
{"status":"ok","assets":117}
```
MCP server logs from every replica (bash):
```bash
rev=$(az containerapp revision list -n contoso-service-mcp -g pcdotai-agent --query "[?properties.active].name" -o tsv | head -1)
for r in $(az containerapp replica list -n contoso-service-mcp -g pcdotai-agent --revision "$rev" --query "[].name" -o tsv); do
  az containerapp logs show -n contoso-service-mcp -g pcdotai-agent --revision "$rev" --replica "$r" --type console --tail 300 --format text > "climb/stage-1/raw/probe-guid/mcp-$r.txt"
  echo "$r: calls in 07h: $(grep -E '2026-10-11T07' climb/stage-1/raw/probe-guid/mcp-$r.txt | grep -c CallToolRequest)"
done
```
```text
contoso-service-mcp--0000007-6d656585bd-4krzr: calls in 07h: 0
contoso-service-mcp--0000007-6d656585bd-5vw55: calls in 07h: 0
contoso-service-mcp--0000007-6d656585bd-7cddk: calls in 07h: 0
contoso-service-mcp--0000007-6d656585bd-c5wd8: calls in 07h: 0
contoso-service-mcp--0000007-6d656585bd-pm6x5: calls in 07h: 0   (one ListToolsRequest at 07:27:26)
```
The calls never reached our server: the platform failed them first. Recorded as [P11](../../docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error).

⛔ **Stopped before the other 29 claims**: they would fail the same way, measuring the platform rather than the model. Database `0 0 0 0`.

### 2.9 Retry the single claim by GUID · 08:03 UTC (13:33 IST)

On the user's go-ahead. Pre-flight first:
```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; New-Item -ItemType Directory -Force climb\stage-1\raw\probe-guid-2 | Out-Null
.\scripts\sql-run.ps1 -File scripts\db-table-counts.sql | Tee-Object climb\stage-1\raw\probe-guid-2\preflight-db-counts.txt
.\.venv\Scripts\python.exe scripts\check-live-config.py climb\stage-1\config | Tee-Object climb\stage-1\raw\probe-guid-2\preflight-config-check.txt
$ev = frontier-tuning -e $e evaluate list --limit 3 -o json | Out-String; ($ev.Substring($ev.IndexOf('[')) | ConvertFrom-Json) | ForEach-Object { "eval $($_.id) $($_.status) $($_.inputModelName) $($_.createdDateTime)" }
curl.exe -s -m 30 https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz
```
```text
Dealers 4 · Parts 14 · Assets 117 · AssetTelemetry 3007 · Claims 92 · ServiceHistory 89 · GoodwillAuthority 4 · TsbApplicability 4 · ClaimAdjudicationDraft 0 · EvidenceRequest 0 · GoodwillEscalation 0   (trimmed to one line)
ALL MATCH
eval bf5947ad-dd49-4812-9305-b9fc13a2ce45 Failed dev-ct-mai-code-mp 10/11/2026 12:34:58
eval 2697a580-0671-49b5-b76f-f34041f22277 Succeeded prod-gpt-56-reasoning-sol 10/11/2026 09:02:35
eval 4bae38ee-051b-4bf5-9faf-d71eb2d30b0b Succeeded prod-gpt-56-reasoning-sol 10/11/2026 08:47:23
{"status":"ok","assets":117}
```
The earlier probe now reads **Failed**. Its status:
```powershell
frontier-tuning -e $e -o json evaluate status bf5947ad-dd49-4812-9305-b9fc13a2ce45 | Set-Content climb\stage-1\raw\probe-guid\status-after.json
```
```text
"status": "Failed", "errorCode": "Rest401", "errorMessage": "Job execution failed with an unknown error.",
"completedAt": "2026-10-11T07:53:05.205805+00:00", "resultMetadata": { "score": 0.4375 }, "stages": []   (excerpt)
```
(For comparison, Sol job `2697a580…`: `Succeeded`, no error code, same snapshot: 3 tools, 4 knowledge sources.)

The retry:
```powershell
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples '04101=90dfe727-082c-4c06-bca9-6321b9382be4' -OutDir climb\stage-1\raw\probe-guid-2 -Model 00000000-0000-0000-8000-100000000004 -BatchSize 1 -MaxAttempts 1
```
```text
Command failed (1): frontier-tuning --output json evaluate start --sample-id 90dfe727-082c-4c06-bca9-6321b9382be4 --base-model 00000000-0000-0000-8000-100000000004 --strategy Simple --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
Error: API error (500): ER99000: An unknown error has occurred.
The request outcome is unknown; it was not retried. Inspect the resource before submitting again.
Transaction ID: 7098a052-c09d-f81a-e17d-ec8fb2fdd798
```
Reconcile at 08:06:50 UTC (`evaluate list --limit 3`): the same three jobs as above, **no new job**. Nothing charged, database untouched.

❌ The GUID accepted at 07:04 is now refused too. Recorded under [P10](../../docs/06-platform-issues.md#p10-every-call-naming-mai-code-5b-fails-with-500-er99000) and [P11](../../docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error). Not resubmitted.

### 2.10 Another small model: GPT-5.4-Mini, one claim · 08:18 UTC (13:48 IST)

On the user's request (they asked for gpt-4.1-mini, which is not in this environment's model list; GPT-5.4-Mini is the only other small model). Its only evaluation row is `dev-ct-gpt-54-mini-mp`. Pre-flight: database `0 0 0`, ALL MATCH, no active job ([raw/probe-54mini/](raw/probe-54mini/)).
```powershell
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples '04101=90dfe727-082c-4c06-bca9-6321b9382be4' -OutDir climb\stage-1\raw\probe-54mini -Model dev-ct-gpt-54-mini-mp -BatchSize 1 -MaxAttempts 1
```
```text
Command failed (1): frontier-tuning --output json evaluate start --sample-id 90dfe727-082c-4c06-bca9-6321b9382be4 --base-model dev-ct-gpt-54-mini-mp --strategy Simple --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
Error: API error (500): ER99000: An unknown error has occurred.
Transaction ID: 87f56fcd-7553-d4d3-78ce-0dc7c0c43ecf   (excerpt)
```
Reconcile at 08:19:30 UTC (`evaluate list --limit 3`): no new job.

❌ Same failure. Only the enabled and selected model (GPT-5.6-Sol) can be evaluated in this environment now.

### 2.11 MAI over the legacy connection · 09:58 UTC (15:28 IST)

The user remembered no such errors on CLI 0.3.x. The 1.x docs describe two connections: the default (`transport = "public"`, ours) and the alternate `legacy`, the older route. Tried legacy with a separate config file, leaving the saved config unchanged ([raw/ft-legacy.toml](raw/ft-legacy.toml)):
```powershell
$c="<scratchpad>\ft-legacy.toml"
"transport = `"legacy`"`nenv_id = `"598fd1b0-36f1-402f-ba36-aa00c8a67cc4`"`n" | Set-Content $c -Encoding ascii
frontier-tuning -c $c models list
```
```text
Models for Evaluation
ID                         Name          Display Name  Fine-Tuned  Selected
prod-gpt-56-reasoning-sol  GPT-5.6-Sol   GPT-5.6-Sol       —          ✓
dev-ct-gpt-54-mini-mp      GPT-5.4-Mini  GPT-5.4-Mini      —          —
dev-ct-mai-code-mp         MAI-CODE-5b   MAI-CODE-5b       —          —
Models for Fine-tuning
gpt-54-mini       GPT-5.4-Mini …   ·   mai-code-1-flash  MAI-Code-1-Flash …   (trimmed)
```
One row per model, no GUID rows: the list as 0.3.x showed it. The single MAI claim over legacy:
```powershell
$env:FRONTIER_TUNING_CONFIG = $c
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples '04101=90dfe727-082c-4c06-bca9-6321b9382be4' -OutDir climb\stage-1\raw\probe-legacy -Model dev-ct-mai-code-mp -BatchSize 1 -MaxAttempts 1
```
```text
Command failed (1): frontier-tuning --output json evaluate start --sample-id 90dfe727-082c-4c06-bca9-6321b9382be4 --base-model dev-ct-mai-code-mp --strategy Simple --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
Error: API error (507): ER99000: An unknown error has occurred.
Transaction ID: 729fb935-5ef3-091a-49d6-60010e0f5f7f   (excerpt)
```
Reconcile at 10:00 UTC on both connections:
```text
public: eval bf5947ad-… Failed dev-ct-mai-code-mp · 2697a580-… Succeeded Sol · 4bae38ee-… Succeeded Sol
legacy: da0fd79d-… Succeeded prod-gpt-56-reasoning-sol 95% 2026-10-11T01:58 · 729ff2cd-… Cancelled dev-ct-mai-code-mp 2026-10-09T04:40 · 008103c3-… Cancelled dev-ct-mai-code-mp 2026-10-09T04:30   (trimmed)
```
No new job on either. ❌ The connection is not the cause: MAI is refused on both. The two connections show different job histories.

### 2.12 Next day: is the platform working? · 2026-10-12 01:12 UTC (06:42 IST)

Pre-flight ([raw/probe-2026-10-12/](raw/probe-2026-10-12/)): CLI 1.0.14, `transport = public`, ALL MATCH, no active job, MCP `/healthz` ok. The database first answered "Database 'contoso-warranty' … is not currently available. Please retry the connection later" (serverless resume, session tracing ID `{E3FC67CA-5741-47C3-9B13-67500B6CE9E5}`); 20 s later the counts read `… 0 0 0`. `models list` unchanged (Sol ✓ only).
```powershell
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples '04101=90dfe727-082c-4c06-bca9-6321b9382be4' -OutDir climb\stage-1\raw\probe-2026-10-12 -Model 00000000-0000-0000-8000-100000000004 -BatchSize 1 -MaxAttempts 1
```
```text
06:48:12 04101 job 171ccc7b-8fda-4a0a-a7c6-157697ffd822 started
06:50:44 04101 WARNING: Command failed (1): frontier-tuning … evaluate diagnostics … Failed to resolve 'login.microsoftonline.com'   (one local DNS blip during polling; trimmed)
07:02:03 04101 Succeeded after 14 min
07:03:03 04101 done (job 171ccc7b-8fda-4a0a-a7c6-157697ffd822): 1/1 finished; DB snapshot saved and reset
```
✅ Accepted (times are IST). The result and where the tool calls went:
```text
score=0.645833333333333 status=Graded calls=4
I couldn't adjudicate claim C-2026-04101 because the warranty assistant's claim-dossier tool is unavailable in this environment—it failed with a virtualization support error.
If you provide the claim dossier here, or have the 1c171 claim-system tool enabled, I can retry the adjudication.

evaluate diagnostics → toolCalls: succeeded 0, failed 7, total 7
MCP replica logs, polled 01:21–01:31 UTC: CallToolRequest since 01:00 UTC: 0
```
❌ **The platform is not working for MAI yet.** The job is accepted, but every claim-system call fails in the platform before reaching our server ([P11](../../docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error)). "1c171" is our MCP registration `1c171d49-…`. Not a valid measurement; database `0 0 0 0`.

(Before this was found:) every call that named MAI-CODE-5b by name returned `500 ER99000`, while GPT-5.6-Sol worked in this environment two hours earlier. A platform-side problem; recorded as [P10](../../docs/06-platform-issues.md#p10-every-call-naming-mai-code-5b-fails-with-500-er99000) with all transaction IDs. Nothing ran, nothing was charged, and the database is still at the seeded state.

---

## 3. Score

## 4. Close

---

## Dead ends

| What | Result |
| --- | --- |
| `evaluate start` with MAI-CODE-5b, ×3 (10 claims, 10 claims, 1 claim) | `500 ER99000` each time; no job created |
| `models set` to enable MAI-CODE-5b, by name and by GUID | `400 ER59004` (needs a GUID), then `500 ER99000` |
| One claim by GUID | Ran (28 min) but the claim-system calls failed inside the platform ("virtualization error"); not a valid result. Job later marked `Failed`, `Rest401` |
| Same claim by GUID again, 08:05 UTC | `500 ER99000`, no job created |
| GPT-5.4-Mini instead, 08:18 UTC | `500 ER99000`, no job created |
| MAI over the legacy connection (the 0.3.x route), 09:58 UTC | `507 ER99000`, no job created |
