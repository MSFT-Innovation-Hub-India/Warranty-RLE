# Stage 0 runbook: commands and responses

Every command **exactly as run**, in order, from the repository root in PowerShell 7, each followed by its response. *(trimmed)* marks a shortened response; the full output is in [raw/](raw/). To replay the stage, run the commands in order.

| | |
| --- | --- |
| Date | 2026-10-11 (UTC) |
| CLI | `frontier-tuning, version 1.0.14 (2026-10-09)` |
| Environment | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` |
| Skill | `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da` |
| Model | `prod-gpt-56-reasoning-sol` (GPT-5.6-Sol) · strategy `Simple` |

---

## 1. Pre-flight

### 1.1 CLI and sign-in · 01:44 UTC

```powershell
frontier-tuning --version
frontier-tuning auth check
```
```text
frontier-tuning, version 1.0.14 (2026-10-09)
https://aka.ms/ft-cli/start#1014
✓ Frontier Tuning authentication is ready.
```

### 1.2 MCP server and database reachable · 01:44 UTC

```powershell
curl.exe -s -m 60 https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz
```
```text
{"status":"ok","assets":117}
```

### 1.3 Database baseline · 01:44 UTC

```powershell
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql
```
```text
drafts evidence_requests escalations claims_not_seeded
------ ----------------- ----------- -----------------
    19                 0           0                 0
OK: 1 batch(es) executed
```

⚠️ **Not clean: 19 drafts.** Expected `0 0 0 0`.

### 1.4 What was written · 01:45 UTC

```powershell
.\scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql | Tee-Object climb\stage-0\raw\db-before-reseed-actions.txt
```
*(trimmed: full rows in [raw/db-before-reseed-actions.txt](raw/db-before-reseed-actions.txt))*
```text
kind  id             claim_id     detail                                              created_at
draft ADJ-0D7D8967F9 C-2026-04101 approve | payable=69575.00 INR | refs=[…]          10/9/2026 12:49:56 PM +00:00
draft ADJ-143E911875 C-2026-04102 approve | payable=48420.00 INR | refs=[…]          10/9/2026 12:50:35 PM +00:00
…  (19 drafts, claims 04101–04149, written 2026-10-09 11:55–13:00 UTC)
draft ADJ-A7470F6CC9 C-2026-04149 approve | payable=753880.00 INR | refs=[…]         10/9/2026 1:00:18 PM +00:00
(no rows)
```

The drafts came from outside this climb: no recorded job ran at that time. The user had run a Foundry agent on the same claims.

### 1.5 Row counts before the reset · 01:45 UTC

```powershell
.\scripts\sql-run.ps1 -File scripts\db-table-counts.sql | Tee-Object climb\stage-0\raw\db-before-reseed-counts.txt
```
```text
tbl                       n
Dealers                   4
Parts                    14
Assets                  117
AssetTelemetry         3007
Claims                   92
ServiceHistory           89
GoodwillAuthority         4
TsbApplicability          4
ClaimAdjudicationDraft   19
EvidenceRequest           0
GoodwillEscalation        0
```

Counts can't show edited values, so the whole database is re-seeded rather than just the action tables reset.

### 1.6 Full re-seed · 01:46 UTC

```powershell
.\scripts\sql-run.ps1 -File world-builder\out\db\seed.azuresql.sql | Tee-Object climb\stage-0\raw\db-reseed.txt
```
```text
OK: 8 batch(es) executed
```

Drops and recreates all 11 tables from the generated seed (20 s). The MCP server's access is by database role (`db_datareader`, `db_datawriter`), so it survives the drop.

*Dead end first:* the same command failed twice with `Program 'powershell.exe' failed to run: StandardOutputEncoding is only supported when standard output is redirected`. Cause: `sql-run.ps1` passed the SQL as a base64 command-line argument, and the 432 KB seed exceeds Windows' ~32K limit. Fixed by passing it through a temp file; no SQL had run.

### 1.7 After the re-seed · 01:46 UTC

```powershell
.\scripts\sql-run.ps1 -File scripts\db-table-counts.sql | Tee-Object climb\stage-0\raw\db-after-reseed-counts.txt
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql | Tee-Object climb\stage-0\raw\db-after-reseed-baseline.txt
curl.exe -s -m 60 https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz
```
```text
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

drafts evidence_requests escalations claims_not_seeded
     0                 0           0                 0

{"status":"ok","assets":117}
```

✅ Clean.

### 1.8 Live skill, rubrics and samples match `config/` · 01:47 UTC

```powershell
.\.venv\Scripts\python.exe scripts\check-live-config.py climb\stage-0\config | Tee-Object climb\stage-0\raw\preflight-config-check.txt
```
```text
instructions match config/skill.md: True
rubrics: live 6, pinned 6
  Authority and action: items ok, importance ok, enabled DIFFERS
  Coverage determination: items ok, importance ok, enabled DIFFERS
  Evidence grounding: items ok, importance ok, enabled DIFFERS
  Gaps reported, not filled: items ok, importance ok, enabled DIFFERS
  Precedence discipline: items ok, importance ok, enabled DIFFERS
  Valuation accuracy: items ok, importance ok, enabled DIFFERS
evaluation samples: 30/30 present; wrong type or skill: none
MISMATCH
```

Instructions, checklist items, importance and the 30 sample IDs match. All six rubrics show **not enabled**:

```powershell
frontier-tuning -e 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 rubrics list --skill-id cf00d339-5217-4cd1-b390-cc0d911735da
```
*(trimmed)*
```text
Rubric ID: 0fdf9e95-3602-4505-9514-287a4bf6cfdc
Name: Coverage determination
Importance: Critical
Enabled: ✗
Checklist Items: 4
…  (same for all six)
```

🔬 CLI 0.3.x never showed an enabled flag. Attempt 1's evaluations were graded on these rubrics in this same state, and the tuning job reported "Scoring criteria configured: 6". **Left unchanged** to keep the conditions identical to attempt 1. The smoke test (step 2) shows whether all six are still graded.

### 1.9 No other job active · 01:49 UTC

```powershell
frontier-tuning -e 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 evaluate list --limit 10 -o json
frontier-tuning -e 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 tune list --limit 5 -o json
```
*(summarised: id, status, created)*
```text
eval 729ff2cd-5096-4f87-8026-638043f68019 Cancelled 10/09/2026 10:10:17
eval 008103c3-727c-4d2e-97dc-9630a8754c67 Cancelled 10/09/2026 10:00:22
eval 44945388-1e87-41b5-adfd-32123fe29268 Succeeded 10/09/2026 08:47:41
eval beb6e3ac-ceb5-4283-b107-7a5368bdbd7f Cancelled 10/09/2026 05:55:19
eval b27edc85-14e0-43e0-95ca-56480e2ff4b3 Succeeded 10/09/2026 04:55:27
tune c77feaed-96de-4b88-9802-e0f265601eb8 Cancelled
```

✅ Nothing running.

### 1.10 Re-enable the rubrics (added after step 2's first attempt failed) · 01:54 UTC

The first smoke submission (step 2a) was refused because all six rubrics were disabled ([P9](../../docs/06-platform-issues.md#p9-rubrics-found-disabled-evaluation-refused-er07018)). Restores the state attempt 1 was graded under; content unchanged.

```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $sk='cf00d339-5217-4cd1-b390-cc0d911735da'
& { foreach ($r in '0fdf9e95-3602-4505-9514-287a4bf6cfdc','cd65bcb6-f40f-4de2-9ad9-23158b2dc492','9bab192e-af3e-42e3-903a-598b6b829737','3f15471d-00d4-496e-bb87-faa37cca9fb9','c64e109d-baeb-4377-9724-0feeb3eb95b7','d09918c5-f072-4db5-8b40-647ff046d4b3') { $out = frontier-tuning -e $e rubrics update $r --skill-id $sk --enable 2>&1 | Out-String; "$r -> exit $LASTEXITCODE : $(($out -split "`n" | Where-Object { $_.Trim() } | Select-Object -First 2) -join ' / ')" } } | Tee-Object climb\stage-0
aw
ubrics-enable.txt
.\.venv\Scripts\python.exe scripts\check-live-config.py climb\stage-0\config | Tee-Object climb\stage-0
aw\preflight-config-check-2.txt
```
```text
0fdf9e95-3602-4505-9514-287a4bf6cfdc -> exit 0 : Rubric updated. / Rubric: Coverage determination
cd65bcb6-f40f-4de2-9ad9-23158b2dc492 -> exit 0 : Rubric updated. / Rubric: Precedence discipline
9bab192e-af3e-42e3-903a-598b6b829737 -> exit 0 : Rubric updated. / Rubric: Evidence grounding
3f15471d-00d4-496e-bb87-faa37cca9fb9 -> exit 0 : Rubric updated. / Rubric: Valuation accuracy
c64e109d-baeb-4377-9724-0feeb3eb95b7 -> exit 0 : Rubric updated. / Rubric: Authority and action
d09918c5-f072-4db5-8b40-647ff046d4b3 -> exit 0 : Rubric updated. / Rubric: Gaps reported, not filled
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

✅ On a replay, run this before step 2 if 1.8 shows `enabled DIFFERS`.

---

## 2. Smoke test: one claim (C-2026-04101)

### 2a First attempt · 01:50 UTC: refused

```powershell
$s = (Get-Content climb\stage-0\config\eval-sample-ids.json -Raw | ConvertFrom-Json | Where-Object { $_.claim -eq 'C-2026-04101' } | ForEach-Object { "$($_.claim.Substring(7))=$($_.id)" }) -join ','
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples $s -OutDir climb\stage-0
aw\smoke -Model prod-gpt-56-reasoning-sol -BatchSize 5 -MaxAttempts 1
```
```text
exit 1
```
The runner's start call (`evaluate start`) wrote to stderr:
```text
Error: API error (400): ER07018: None of the selected samples are eligible for evaluation based on their attached skills.
Transaction ID: 10611f24-b671-3788-a09b-681656a26987
```
No job created (checked with `evaluate list --limit 3`: newest job still `729ff2cd…`, 2026-10-09). Diagnosed and fixed in 1.10.

### 2b Second attempt · 01:58 UTC

Same command as 2a.

```text
07:28:19 04101 job da0fd79d-8bbc-466c-9cf7-b480054bf96a started
```

At 07:39 IST a status poll failed on a local network blip (`Failed to resolve 'login.microsoftonline.com'`). The runner tolerates that, but its log write then failed (`The process cannot access the file …run-log.txt because it is being used by another process`) because a `tail -f` watching the log held it open. The runner exited (02:09 UTC). **The platform job kept running** (`Running`, phase `Executing`, 1 claim running at 02:10 UTC).

Fix: the runner's `Log` now retries and never stops the run on a log-write failure. Don't watch `run-log.txt` with `tail -f` on Windows; read it.

### 2c Adopt the running job · 02:10 UTC

No new submission: the runner takes over the existing job, then collects results, snapshots and resets the database as usual.

```powershell
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples '' -OutDir climb\stage-0\raw\smoke -Model prod-gpt-56-reasoning-sol -MaxAttempts 1 -AdoptJob da0fd79d-8bbc-466c-9cf7-b480054bf96a -AdoptSamples '04101=90dfe727-082c-4c06-bca9-6321b9382be4'
```

```text
07:40:32 adopting job da0fd79d-8bbc-466c-9cf7-b480054bf96a for 04101
07:41:47 04101 Succeeded after 1 min
07:42:33 04101 done (job da0fd79d-8bbc-466c-9cf7-b480054bf96a): 1/1 finished; DB snapshot saved and reset
07:42:33 ALL DONE
exit 0
```
(The first two lines also printed `WARNING: could not write run-log.txt`: the orphaned `tail` was still holding the file. Stopped with `Stop-Process -Id 3340,40084`.)

### 2d Smoke result · 02:12 UTC

```powershell
$f='climb\stage-0\raw\smoke\results-04101.json'; $t=Get-Content $f -Raw; $o=$t.Substring($t.IndexOf('{')) | ConvertFrom-Json; $s=$o.submissions[0]
"score=$($s.score) status=$($s.status) toolInvocations=$($s.execution.billingSummary.toolInvocations) tokens=$($s.execution.billingSummary.totalTokens)"
$s.execution.rubricResults | ForEach-Object { "  {0,-28} {1,5}" -f $_.displayName, $_.score }
Get-Content climb\stage-0\raw\smoke\db-after-04101.txt
```
*(trimmed)*
```text
score=0.95 status=Graded toolInvocations=10 tokens=298294
  Coverage determination           1
  Precedence discipline         0.75
  Evidence grounding               1
  Valuation accuracy               1
  Authority and action             1
  Gaps reported, not filled        0      <- skipped as not applicable (empty reason); 0.95 = mean of the other five
draft ADJ-92B40546B5 C-2026-04101 approve | payable=69575.00 INR | refs=["POL-WAR-4.2 clauses 1.4, 2.1 and 4.1", "ADD-IN-2.1 scope and clause A1", …]
```
Answer opens `# Decision — APPROVE INR 69,575`: approve, ADD-IN-2.1, ₹69,575, all as the ground truth. Database reset after the job: `0 0 0 0`.

```powershell
.\.venv\Scripts\python.exe scripts\score_ground_truth.py climb\stage-0\raw\smoke\results-04101.json --out climb\stage-0\raw\smoke\check
```
First run: `₹69,575 → ₹2,175 ❌`. The scorer read the first figure of Sol's table row `| **Total** | INR 2,175 + INR 67,400 + INR 0 | **INR 69,575** |`. **Fixed:** in a table row it now reads the last cell; new test added (54/54), archived stages 0–2 rescore with 0 differences. After the fix:
```text
| `C-2026-04101` | covered-simple | approve → approve ✅ | ADD-IN-2.1 → ADD-IN-2.1 ✅ | ₹69,575 → ₹69,575 ✅ | 0.95 | ✅ |
```

✅ Smoke passed: the model ID is accepted, the claim runs, all six rubrics are applied, the answer is scored, and the database is snapshotted and reset. The result for 04101 counts as part of the 30, so step 3 runs the other 29.

---

## 3. The remaining 29 claims

### 3.1 Start · 02:15 UTC

```powershell
$s = (Get-Content climb\stage-0\config\eval-sample-ids.json -Raw | ConvertFrom-Json | Where-Object { $_.claim -ne 'C-2026-04101' } | ForEach-Object { "$($_.claim.Substring(7))=$($_.id)" }) -join ','
powershell -File scripts\eval-batches.ps1 -Env 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -Samples $s -OutDir climb\stage-0\raw\run -Model prod-gpt-56-reasoning-sol -BatchSize 5
```

### 3.2 Run log · 02:14–03:47 UTC (07:44–09:17 IST)

Runner console output, verbatim:
```text
UTC 2026-10-11T02:14:25
07:44:58 04102+04103+04109+04110+04114 job d02eb5da-f21a-4661-9b79-bbf4a2f02cac started
07:59:26 04102+04103+04109+04110+04114 Succeeded after 14 min
08:00:13 04102+04103+04109+04110+04114 done (job d02eb5da-f21a-4661-9b79-bbf4a2f02cac): 5/5 finished; DB snapshot saved and reset
08:00:39 04115+04116+04117+04118+04129 job 12b806d8-b8a5-42a1-92c0-11bdf2f98ef1 started
08:15:01 04115+04116+04117+04118+04129 Succeeded after 14 min
08:15:47 04115+04116+04117+04118+04129 done (job 12b806d8-b8a5-42a1-92c0-11bdf2f98ef1): 5/5 finished; DB snapshot saved and reset
08:16:28 04130+04131+04132+04139+04140 job 5343fa35-607d-48bd-9cfb-380bf9c69876 started
08:30:49 04130+04131+04132+04139+04140 Succeeded after 14 min
08:31:40 04130+04131+04132+04139+04140 done (job 5343fa35-607d-48bd-9cfb-380bf9c69876): 5/5 finished; DB snapshot saved and reset
08:32:18 04141+04148+04149+04150+04151 job 11178c7e-6b40-4ce6-986f-8addb4e17da1 started
08:46:13 04141+04148+04149+04150+04151 Succeeded after 14 min
08:46:52 04141+04148+04149+04150+04151 done (job 11178c7e-6b40-4ce6-986f-8addb4e17da1): 5/5 finished; DB snapshot saved and reset
08:47:28 04152+04153+04166+04167+04171 job 4bae38ee-051b-4bf5-9faf-d71eb2d30b0b started
09:01:25 04152+04153+04166+04167+04171 Succeeded after 14 min
09:02:07 04152+04153+04166+04167+04171 done (job 4bae38ee-051b-4bf5-9faf-d71eb2d30b0b): 5/5 finished; DB snapshot saved and reset
09:02:38 04172+04176+04177+04178 job 2697a580-0671-49b5-b76f-f34041f22277 started
09:16:43 04172+04176+04177+04178 Succeeded after 14 min
09:17:26 04172+04176+04177+04178 done (job 2697a580-0671-49b5-b76f-f34041f22277): 4/4 finished; DB snapshot saved and reset
09:17:26 ALL DONE
exit 0
UTC 2026-10-11T03:47:26
```
6 jobs, 14 min each, no stalls, no retries. What the agent wrote to the claim system per job: [raw/run/db-snapshots.txt](raw/run/db-snapshots.txt).

---

## 4. Score · 03:47 UTC

### 4.1 Merge the smoke claim with the 29, summarise and score

```powershell
Copy-Item climb\stage-0\raw\smoke\results-04101.json climb\stage-0\raw\run\
Copy-Item climb\stage-0\raw\smoke\db-after-04101.txt climb\stage-0\raw\run\
.\.venv\Scripts\python.exe scripts\summarise-stage.py climb\stage-0\raw\run climb\stage-0\results --consolidate
```
*(trimmed: full tables in [results/ground-truth-check.md](results/ground-truth-check.md) and [results/run-summary.md](results/run-summary.md))*
```text
30 answers from 1 file(s); decisions read: {'approve': 17, 'decline': 8, 'escalate': 1, 'review': 2, 'request_evidence': 2}
| Decision correct | 28/30 (93%) |
| Governing instrument correct | 29/30 (97%) |
| Payable correct (approvals) | 16/17 (94%) |
| **Fully correct** | **26/30 (87%)** |
| Needs human review (unreadable) | 2 |
| Mean rubric score (platform) | 0.956 |
…
Claims: 30 · mean rubric 0.956 · mean calls 13.7 · mean tool output n/a · overflows 0 · rejected hand-ins 1
Per rubric (mean over graded, skipped excluded): … Valuation accuracy 0.52 · … Gaps reported, not filled 0.3
consolidated: 7 snapshots -> db-snapshots.txt; per-job results removed
```

The per-rubric means for Valuation and Gaps were wrong: in v1's raw JSON a skipped rubric has **no** `scoreReason` key, and the skip rule required the key. Fixed in `summarise-stage.py` and the scorer's fallback (54/54 tests; archived stages 0–2 still rescore with 0 differences). Per-claim rubric scores were unaffected (they are the platform's `score`). Summary regenerated from the merged file:

```powershell
$tmp="$env:TEMP\claude\s0-resum"; New-Item -ItemType Directory -Force $tmp | Out-Null
Copy-Item climb\stage-0\results\eval-results-samples.json "$tmp\results-all.json"
.\.venv\Scripts\python.exe scripts\summarise-stage.py $tmp climb\stage-0\results
```
```text
Claims: 30 · mean rubric 0.956 · mean calls 13.7 · mean tool output n/a · overflows 0 · rejected hand-ins 1
Per rubric (mean over graded, skipped excluded): Coverage determination 1.0 · Precedence discipline 0.897 · Evidence grounding 0.975 · Valuation accuracy 0.918 · Authority and action 0.983 · Gaps reported, not filled 0.9
```
(On a replay with the fixed scripts, 4.1 alone gives these numbers.)

### 4.2 Hand-check

Every ❓, ❌ and flag read by hand: [results/hand-check.md](results/hand-check.md). Result: **29/30**. 04153, 04172 and 04176 are correct (scorer misread or unreadable); 04114's "rejected hand-in" flag is a false positive; **04151 is a real error** (supersession price not applied).

### 4.3 Reward ranking

```powershell
.\.venv\Scripts\python.exe scripts\reward-ranking.py climb\stage-0\results --set C-2026-04153=correct --set C-2026-04172=correct --set C-2026-04176=correct
```
```text
correct (with hand-check): 29 of 30
mean rubric: right 0.955 · wrong 0.960
right ranked above wrong: 11 of 29 pairs (38%); ties 3
  wrong: C-2026-04151 rubric 0.96 - outscores 15 of 29 right answers
```

---

## 5. Close · 03:49 UTC

```powershell
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql | Tee-Object climb\stage-0\raw\db-final-baseline.txt
```
```text
drafts evidence_requests escalations claims_not_seeded
     0                 0           0                 0
```

The runner's per-command stdout/stderr captures (216 in `raw/run`, 36 in `raw/smoke`) were zipped to `command-captures.zip` in each folder; entry counts were verified before the loose files were removed.

---

## Dead ends

| What | Result |
| --- | --- |
| Re-seed with the original `sql-run.ps1` | Failed to launch (SQL passed as a command-line argument, over the length limit). Script fixed; nothing had run |
| Smoke 2a | Refused, `ER07018`: rubrics disabled. Fixed in 1.10 |
| Smoke 2b runner | Exited when a `tail -f` locked its log during a network blip; job unaffected and adopted in 2c |
