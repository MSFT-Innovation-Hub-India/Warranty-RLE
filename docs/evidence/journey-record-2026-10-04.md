# Execution record — 2026-10-04 (verbatim)

> Every command run on 2026-10-04, with its output, including dead ends.
> **For the readable walkthrough, see [JOURNEY.md](../JOURNEY.md).** The previous session is in [journey-record-2026-10-03.md](journey-record-2026-10-03.md).

---

## Stage 0 — preparation and run

### S0.1 Select the 8 prompts

```powershell
$keep = 'C-2026-04101','C-2026-04102','C-2026-04103','C-2026-04109','C-2026-04110','C-2026-04114','C-2026-04116','C-2026-04118'
$lines = Get-Content out\samples\warranty-adjudication.eval.jsonl | Where-Object { $l = $_; $keep | Where-Object { $l -match [regex]::Escape($_) + '\b' } }
[IO.File]::WriteAllLines((Resolve-Path stages\stage-0).Path + '\stage0.jsonl', [string[]]$lines, (New-Object System.Text.UTF8Encoding $false))
```

```text
1: {"Prompt": "Adjudicate claim C-2026-04101."}
2: {"Prompt": "Fabrikam Service Partners have submitted C-2026-04102. Is it covered, and what do we pay?"}
3: {"Prompt": "Can you work up C-2026-04103 for me — coverage position and payable amount?"}
4: {"Prompt": "What's the position on C-2026-04109?"}
5: {"Prompt": "Review C-2026-04110 and tell me the decision, the instrument it turns on, and the amount."}
6: {"Prompt": "C-2026-04114 came in from Fabrikam Service Partners this morning. Where do we land?"}
7: {"Prompt": "Please assess C-2026-04116 on serial CIE-4000-CH-01950 and give me the payable figure."}
8: {"Prompt": "C-2026-04118: covered or not? If covered, what's payable and under what?"}
```

The first expected-answer listing failed with `KeyError: 'total_payable'`: declined claims have no total. Re-run with `.get()`:

```text
C-2026-04101 covered-simple approve ADD-IN-2.1 69575.0
C-2026-04102 covered-simple approve ADD-IN-2.1 48420.0
C-2026-04103 covered-simple approve ADD-IN-2.1 19150.0
C-2026-04109 declined-simple decline ADD-IN-2.1 None
C-2026-04110 declined-simple decline ADD-IN-2.1 None
C-2026-04114 precedence approve TSB-C-0051 199175.0
C-2026-04116 precedence decline ADD-IN-2.1 None
C-2026-04118 precedence approve TSB-P-0112 67500.0
```

### S0.2 Pre-flight on main

```powershell
New-Item -ItemType Directory -Force -Path docs\evidence\stage-0 | Out-Null
$m = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
"== tool sources (main)"; frontier-tuning tools sources --env-id $m -o json 2>&1 | ConvertFrom-Json | ForEach-Object { if ($_.value) { $_.value } else { $_ } } | ForEach-Object { "  {0,-16} enabled={1}" -f $_.Name, $_.Enabled }
"== skills (main)"; frontier-tuning skills list --env-id $m -o json 2>&1 | ConvertFrom-Json | ForEach-Object { if ($_.value) { $_.value } else { $_ } } | ForEach-Object { "  {0} | {1} | enabled={2} | rubrics={3}" -f $_.Id, $_.Name, $_.Enabled, @($_.Rubrics).Count }
"== samples (main)"; frontier-tuning samples list --env-id $m -o json 2>&1 | Out-String | ForEach-Object { $_.Trim().Substring(0, [Math]::Min(300, $_.Trim().Length)) }
"== baseline (H2)"; $tok = az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv; powershell.exe -NoProfile -ExecutionPolicy Bypass -File '<session folder>\baseline-check.ps1' -Token $tok
"== CLI"; frontier-tuning --version 2>&1 | Select-Object -First 1; frontier-tuning whoami 2>&1 | Select-String 'Expires'
```

```text
== tool sources (main)
  contoso-service  enabled=False
  fabriciq         enabled=False
  Word             enabled=False
  M365Chat         enabled=False
  SharePoint       enabled=True
  OneDrive         enabled=True
  Teams            enabled=True
  Calendar         enabled=False
  Email            enabled=False
== skills (main)
  cf00d339-5217-4cd1-b390-cc0d911735da | warranty-assistant | enabled=True | rubrics=5
== samples (main)
[]
== baseline (H2)
drafts=0 evidence=0 escalations=0 non_submitted=0
== CLI
frontier-tuning, version 0.3.16 (2026-09-29)

  Expires    2026-10-04 08:43 UTC
```

```powershell
frontier-tuning refresh 2>&1 | Select-Object -Last 3; frontier-tuning whoami 2>&1 | Select-String 'Expires'
```

```text
✓ Token refreshed successfully.
  Signed in as: sansri@microsoft.com

  Expires    2026-10-04 08:43 UTC
```

### S0.3 Hand probe — `--skill-id` fails (dead end)

```powershell
frontier-tuning chat --env-id $m --skill-id cf00d339-5217-4cd1-b390-cc0d911735da -q "Adjudicate claim C-2026-04114." --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content docs\evidence\stage-0\stage0-probe.json -Encoding utf8
```

```text
Error: API error (500): submission was not retried because its outcome is unknown
Transaction ID: 212b958e-7f7d-259f-a1a9-fd36b5131a8e
```

Retried, with the same result: `Transaction ID: bb87ad8c-a4cb-52de-99f2-96ff23c04ccc`.

### S0.4 Isolating the cause

```powershell
$m = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $d = '6bec3bf9-0222-4285-8a5b-214867ac42cc'
"== ping main"; frontier-tuning --env-id $m ping --count 1 2>&1 | Select-Object -First 6
"== whoami"; frontier-tuning whoami 2>&1 | Select-String 'Expires'
"== A: main, no skill-id"; frontier-tuning chat --env-id $m -q "What serial range does bulletin TSB-C-0051 cover?" --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content docs\evidence\stage-0\diag-a-main-noskill.json -Encoding utf8; "exit=$LASTEXITCODE"; (Get-Content docs\evidence\stage-0\diag-a-main-noskill.json -Raw).Substring(0, 200)
```

```text
== ping main
✓ Auth:  sansri@microsoft.com
✓
https://substrate.office.com/KnowledgeGraph/api/v1.0/Workspaces/598fd1b0-36f1-4
02f-ba36-aa00c8a67cc4/McpServers  6607ms
== whoami

  Expires    2026-10-04 08:43 UTC
== A: main, no skill-id
exit=0
{"executionId": "09218d06-cc83-4050-8027-e7443ce87e6c", "conversationId": "5cce66ae-988e-4119-aad1-acc5e61581f6", "status": "Completed", "startDateTime": "2026-10-04T08:34:31.1677274+00:00", "endDateT
```

```powershell
$d = '6bec3bf9-0222-4285-8a5b-214867ac42cc'
frontier-tuning chat --env-id $d --skill-id 8e9d12a2-b0a5-4683-95f1-b225ed9ade44 -q "Adjudicate claim C-2026-04114." --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content docs\evidence\stage-0\diag-b-dev-skill.json -Encoding utf8; "exit=$LASTEXITCODE"; $r = Get-Content docs\evidence\stage-0\diag-b-dev-skill.json -Raw; $r.Substring(0, [Math]::Min(220, $r.Length))
```

```text
exit=1
Error: API error (500): submission was not retried because its outcome is unknown
Transaction ID: 7e409da0-8450-d79b-c2b5-66912b8a7191
```

Run A routed to the skill on its own and was graded on the pinned rubrics:

```text
status=Completed exec=09218d06-cc83-4050-8027-e7443ce87e6c
rubricResults: [{"Score":1.0,"Reasoning":"This was a narrow bulletin question, and the response directly supplied the requested inclusive serial range plus concise applicability qualifications. Claim outcome, governing-instrument selection, coverage-position analysis, payable amount, and claim next steps were not requested.","Skip":null,"ExtraOutputs":null,"Id":"03ff334c-8fe1-4cc6-a230-1bf0c1d7744d","RubricName"…
tools: m365__search_enterprise_files
executions get -> Skills: warranty-assistant  | RubricResults count: 5
```

**Conclusion:** `chat --skill-id` returns a 500 in both worlds. Normal routing works and selects the skill.

### S0.5 Hand probe via routing — the stage-0 gate

```powershell
frontier-tuning chat --env-id $m -q "Adjudicate claim C-2026-04114." --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content docs\evidence\stage-0\stage0-probe.json -Encoding utf8
# + the summary one-liner (tool title/status/latency/FileRetrievalDetails, rubric scores, response), as in JOURNEY H1
```

Raw: [stage-0/stage0-probe.json](stage-0/stage0-probe.json)

```text
exit=0 size=595598
status=Completed exec=4796e7dc-c2ee-4ad3-9235-44511c6976e0 10/04/2026 14:07:15 -> 10/04/2026 14:10:13 error=
  m365__search_enterprise_files | Completed | 5183 ms | FRD non-empty | searchQuery="C-2026-04114"; from=0; size=25
  teams__SearchTeamsMessages | Completed | 3032 ms |  | message=C-2026-04114; conversationId=; top=25; nextLink=
  m365__call_copilot | Completed | 3244 ms |  | query=Find and summarize all organisation records relevant to warranty claim C-2026-04114. …
  m365__search_enterprise_files | Completed | 5094 ms | FRD non-empty | searchQuery="CIE-4000-CH-01700"; from=0; size=25
  m365__search_enterprise_files | Completed | 5427 ms | FRD non-empty | searchQuery="TSB-C-0051"; from=0; size=25
  m365__search_enterprise_files | Completed | 5150 ms | FRD non-empty | searchQuery="POL-WAR-4.2"; from=0; size=25
  … 24 tool calls in total (SharePoint search, Teams search, 2× m365__call_copilot); no contoso-service tools
rubric scores: Requested Outcome Delivery=1 | Claim Determination Requirements=1 | Internal Record Use and Grounding=0.9 | Adjudicator-Ready Presentation and Traceability=0.666666666666667 | Claim-System Draft Execution=…
response:
# Claim C-2026-04114 — adjudication prepared
## Decision: **Cannot yet be finally decided — hold pending commissioning evidence**
…
## Governing warranty instrument
**Primary instrument: TSB-C-0051, read with POL-WAR-4.2.**
```

*(trimmed: the full trace and answer are in the raw file)*

### S0.6 Upload the samples

```powershell
frontier-tuning samples upload stages\stage-0\stage0.jsonl --skill-id cf00d339-5217-4cd1-b390-cc0d911735da --type Evaluation --env-id $m 2>&1 | Tee-Object -FilePath docs\evidence\stage-0\samples-upload.txt
```

```text
Uploading ---------------------------------------- 8/8 0:00:21

Uploaded: 8 | Failed: 0
samples in main: 8   (all Evaluation)
```

### S0.7 Start the evaluation

```powershell
frontier-tuning evaluate start --skill-id cf00d339-5217-4cd1-b390-cc0d911735da --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $m -o json 2>&1 | Tee-Object -FilePath docs\evidence\stage-0\evaluate-start.json
```

Raw: [stage-0/evaluate-start.json](stage-0/evaluate-start.json)

```text
"JobId": "555d5dd2-f9c3-4008-8846-02e9ceca44d3", "JobType": "Evaluation", "Status": "Running",
"BaseModelName": "prod-gpt-56-reasoning-sol", "CreatedAt": "2026-10-04T08:42:34.8459396+00:00",
"WorkspaceSnapshotMetadata": { "SkillsCount": 1, "ToolsCount": 3, "SamplePromptsCount": 8, "KnowledgeSourcesCount": 4 }
```

### S0.8 Poll until done

```powershell
$m = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $job = '555d5dd2-f9c3-4008-8846-02e9ceca44d3'; $log = 'docs\evidence\stage-0\evaluate-status-poll.txt'
for ($i = 0; $i -lt 30; $i++) { $raw = frontier-tuning evaluate status $job --env-id $m -o json 2>&1 | Out-String; $st = if ($raw -match '"Status"\s*:\s*"([^"]+)"') { $Matches[1] } else { 'unknown' }; "$(Get-Date -Format 'HH:mm:ss') status=$st"; if ($st -notin 'Running','NotStarted','Queued','Pending','InProgress','unknown') { break }; Start-Sleep 300 }
```

```text
14:13:07 status=NotStarted
14:18:34 status=InProgress
14:23:49 status=InProgress
14:29:03 status=InProgress
14:34:24 status=Succeeded
```

### S0.9 Results — summary first, then per answer

```powershell
frontier-tuning evaluate results $job --env-id $m -o json 2>&1 | Set-Content stages\stage-0\eval-results.json -Encoding utf8
```

```text
exit=0 size=3122
"OverallScore": 0.6301388740539551 · "StatusMessage": "Evaluation completed (overall=0.630): 8 graded." · "Strategy": "Simple"
Requested Outcome Delivery 1.0 · Claim Determination Requirements 0.65 · Internal Record Use and Grounding 0.7548611111111111 ·
Adjudicator-Ready Presentation and Traceability 0.7458333333333333 · Claim-System Draft Execution 0.0   (SampleCount 8 each)
submissions: None        ← summary only; --samples is needed for answers
```

```powershell
frontier-tuning evaluate results $job --samples --env-id $m -o json 2>&1 | Set-Content stages\stage-0\eval-results-samples.json -Encoding utf8
frontier-tuning evaluate diagnostics $job --env-id $m 2>&1 | Set-Content stages\stage-0\eval-diagnostics.txt -Encoding utf8
```

```text
exit=0 size=3627566
Progress  (8 samples)
  Execution:  completed 8, running 0, pending 0, failed 0  (100%)
  Grading:    graded 8, excluded 0, awaiting 0  (100%)
Results so far
  Score: 0.630   Graded samples: 8   Scored rubrics: 40
submissions: 8
execution keys: [..., 'UserQuery', 'Response', ...]
Response[:200]: [{'Content': '# Claim C-2026-04118 — adjudication status\n\n## Decision: **HOLD — cannot yet be decided**...
```

`Response` is a list of parts, so the scorer's `_text()` now joins `Content` parts (+1 test, 19/19 passing).

### S0.10 Ground-truth check

```powershell
.\.venv\Scripts\python.exe build\score_ground_truth.py stages\stage-0\eval-results-samples.json --out stages\stage-0 --label "Stage 0 — job 555d5dd2"
```

The first run showed `payable` figures on held answers, e.g. 04102 `₹1,450`, an hourly rate. I changed the scorer so that an approve-expected answer given a non-approve decision is marked *"payable not assessed"*. Final output: [stages/stage-0/ground-truth-check.md](../../stages/stage-0/ground-truth-check.md).

```text
| Decision correct | 1/8 (12%) |
| Governing instrument correct | 3/8 (38%) |
| Payable correct (approvals) | 0/5 (0%) |
| **Fully correct** | **1/8 (12%)** |
| Mean rubric score (platform) | 0.63 |
decisions read: {'request_evidence': 7, 'decline': 1}
```

A hand spot-check of 04101, 04102, 04110 and 04116 confirmed the scorer's reading. Every one of them says "cannot yet be decided / hold", citing missing claim-system facts and POL-WAR-4.2 clause 2.3.

---

## Stage 1 — switch on the claim system

### S1.1 Decisions (user, 14:47–14:48 IST)

The user corrected "stage 2" to **stage 1**, and deferred endpoint auth (P6) as not core to the climb. I kept the MCP tool descriptions as designed (03 § 13) and deferred the runbook text fixes (P11). All recorded in `stages/stage-1/README.md`.

### S1.2 Reusable database scripts

Created `scripts/sql-run.ps1`, `scripts/db-baseline.sql`, `scripts/db-actions-snapshot.sql` and `scripts/db-reset-actions.sql`. Column names checked against `out/db/schema.azuresql.sql` first. Test:

```powershell
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql; "-----"; .\scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql
```

```text
drafts evidence_requests escalations claims_not_submitted
------ ----------------- ----------- --------------------
     0                 0           0                    0
OK: 1 batch(es) executed
-----
(no rows)
(no rows)
OK: 1 batch(es) executed
```

### S1.3 Stage folder

```powershell
New-Item -ItemType Directory -Force -Path stages\stage-1 | Out-Null
Copy-Item stages\stage-0\warranty-assistant.md, stages\stage-0\warranty-assistant.rubrics.json stages\stage-1\
Copy-Item stages\stage-0\stage0.jsonl stages\stage-1\samples.jsonl
```

```text
warranty-assistant.md: identical=True
warranty-assistant.rubrics.json: identical=True
samples identical to stage0.jsonl: True
```

### S1.4 The one change

```powershell
$m = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
"== warm"; $sw = [Diagnostics.Stopwatch]::StartNew(); try { $r = Invoke-WebRequest https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz -UseBasicParsing -TimeoutSec 120; "healthz $($r.StatusCode) $($r.Content) in $($sw.ElapsedMilliseconds) ms" } catch { "healthz FAIL $($_.Exception.Message)" }
"== enable"; frontier-tuning tools enable 1c171d49-7f85-4997-8126-ae20829a4dbf --env-id $m 2>&1
"== sources"; frontier-tuning tools sources --env-id $m -o json 2>&1 | ConvertFrom-Json | ForEach-Object { if ($_.value) { $_.value } else { $_ } } | ForEach-Object { "  {0,-16} enabled={1}" -f $_.Name, $_.Enabled }
"== available"; $raw = frontier-tuning tools available --env-id $m -o json 2>&1 | Out-String; $names = [regex]::Matches($raw, '"Name":\s*"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }
"main available total: $($names.Count)"; $names | Where-Object { $_ -like '1c171__*' }
"== status"; frontier-tuning tools status 1c171d49-7f85-4997-8126-ae20829a4dbf --env-id $m 2>&1
```

```text
== warm
healthz 200 {"status":"ok","assets":117} in 6675 ms
== enable
Tool 1c171d49-7f85-4997-8126-ae20829a4dbf enabled.
== sources
  contoso-service  enabled=True
  fabriciq         enabled=False
  Word             enabled=False
  M365Chat         enabled=False
  SharePoint       enabled=True
  OneDrive         enabled=True
  Teams            enabled=True
  Calendar         enabled=False
  Email            enabled=False
== available
main available total: 88
1c171__get_asset
1c171__get_running_hours
1c171__get_service_history
1c171__find_prior_claims
1c171__get_claim
1c171__get_dealer
1c171__lookup_part
1c171__get_tsb_index
1c171__get_goodwill_authority
1c171__create_claim_adjudication
1c171__request_missing_evidence
1c171__escalate_goodwill
== status
Tool: contoso-service
ID: 1c171d49-7f85-4997-8126-ae20829a4dbf
Observed Callable Tools: 12
Discovery Status: observed
```

The total of 88 looked wrong, so I re-read it:

```powershell
foreach ($e in @(@('main',$m), @('dev',$d))) { $raw = frontier-tuning tools available --env-id $e[1] -o json 2>&1 | Out-String; $names = [regex]::Matches($raw, '"Name":\s*"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }; "{0}: {1} tools: {2}" -f $e[0], $names.Count, (($names | ForEach-Object { ($_ -split '__')[0] } | Group-Object | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join '  ') }
```

```text
main: 137 tools: 1c171=12  lumina_sandbox=9  m365=5  mcp_OneDriveRemoteServer=18  mcp_SharePointRemoteServer=31  polymer_atomic=17  teams=43  workspace_health=2
dev: 137 tools: 34d14=12  lumina_sandbox=9  m365=5  mcp_OneDriveRemoteServer=18  mcp_SharePointRemoteServer=31  polymer_atomic=17  teams=43  workspace_health=2
```

**Conclusion:** the 88 was a transient partial read right after enabling.

### S1.5 Hand probe on main

```powershell
New-Item -ItemType Directory -Force -Path docs\evidence\stage-1 | Out-Null
frontier-tuning chat --env-id $m -q "Adjudicate claim C-2026-04114." --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content docs\evidence\stage-1\stage1-probe.json -Encoding utf8
# + the summary one-liner (as H1)
```

Raw: [stage-1/stage1-probe.json](stage-1/stage1-probe.json)

```text
exit=0 size=197542
status=Completed exec=8ce435fa-b582-4e30-aa50-cd9ce4617d05 10/04/2026 14:53:29 -> 10/04/2026 14:56:28 error=
  1c171__get_claim | Completed | 3536 ms | claim_id=C-2026-04114
  1c171__get_asset | Completed | 5120 ms | serial=CIE-4000-CH-01700
  1c171__get_running_hours | Completed | 6179 ms | serial=CIE-4000-CH-01700; as_of=2026-06-18
  1c171__get_service_history | Completed | 6175 ms | serial=CIE-4000-CH-01700; months=36
  1c171__find_prior_claims | Completed | 3513 ms | serial=CIE-4000-CH-01700; component=null
  1c171__get_dealer | Completed | 5114 ms | dealer_id=D-IN-01
  1c171__lookup_part | Completed | 5114 ms | part_no=P-44120-A
  1c171__get_tsb_index | Completed | 3391 ms | family=4000-CH; serial=CIE-4000-CH-01700
  m365__search_enterprise_files ×6 · teams__SearchTeamMessagesQueryParameters ×2
  1c171__create_claim_adjudication | Completed | 7604 ms | claim_id=C-2026-04114; decision=approve; instrument_refs=["TSB-C-0051","POL-WAR-4.2 clauses 1.4, 4.1, 4.2, 4.3 …
rubric scores: Requested Outcome Delivery=1 | Claim Determination Requirements=0.8 | Internal Record Use and Grounding=1 | Adjudicator-Ready Presentation and Traceability=1 | Claim-System Draft Execution=1
# Claim C-2026-04114 — draft adjudication
## Decision: **APPROVE — INR 199,175**
… A draft approval has been recorded in the claim system as **ADJ-41014A943B**, payable **INR 199,175** …
```

*(trimmed: the six search queries and the response body are in the raw file)*

### S1.6 Snapshot and reset what the probe wrote

```powershell
.\scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql 2>&1 | Tee-Object -FilePath docs\evidence\stage-1\db-after-probe.txt
.\scripts\sql-run.ps1 -File scripts\db-reset-actions.sql 2>&1 | Tee-Object -FilePath docs\evidence\stage-1\db-reset-before-eval.txt
```

```text
draft ADJ-41014A943B C-2026-04114 approve | payable=199175.00 INR | refs=["TSB-C-0051", "POL-WAR-4.2 clauses 1.4, 4.1, 4.2, 4.3", "ADD-IN-2.1", "Flat-Rate-Labour-FY26", "Labour-Rates-By-Region-FY26", "SPA-2023-FAB-IN"]
(no rows)
drafts=0 evidence_requests=0 escalations=0 claims_not_submitted=0
```

The table output wrapped the last column, so `sql-run.ps1` now uses `Out-String -Width 4096`.

### S1.7 Start the evaluation

```powershell
frontier-tuning evaluate start --skill-id cf00d339-5217-4cd1-b390-cc0d911735da --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $m -o json 2>&1 | Tee-Object -FilePath docs\evidence\stage-1\evaluate-start.json
```

```text
samples in main: 8
"JobId": "cf102eae-e5a6-489a-bd21-c1e1bd50a79b", "Status": "Running", "CreatedAt": "2026-10-04T09:27:48.5722823+00:00",
"WorkspaceSnapshotMetadata": { "SkillsCount": 1, "ToolsCount": 4, "SamplePromptsCount": 8, "KnowledgeSourcesCount": 4 }
```

### S1.8 Poll

```text
14:58:40 status=NotStarted
15:03:53 status=InProgress
15:09:06 status=InProgress
15:14:17 status=InProgress
15:19:29 status=Succeeded
```

### S1.9 Results, ground truth, agent writes

```powershell
$m = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $job = 'cf102eae-e5a6-489a-bd21-c1e1bd50a79b'
frontier-tuning evaluate results $job --env-id $m -o json 2>&1 | Set-Content stages\stage-1\eval-results.json -Encoding utf8
frontier-tuning evaluate results $job --samples --env-id $m -o json 2>&1 | Set-Content stages\stage-1\eval-results-samples.json -Encoding utf8
frontier-tuning evaluate diagnostics $job --env-id $m 2>&1 | Set-Content stages\stage-1\eval-diagnostics.txt -Encoding utf8
.\.venv\Scripts\python.exe build\score_ground_truth.py stages\stage-1\eval-results-samples.json --out stages\stage-1 --label "Stage 1 — job cf102eae"
.\scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql 2>&1 | Tee-Object -FilePath stages\stage-1\db-actions-after-eval.txt
```

```text
sizes: summary=3110 samples=3876839
Overall: 0.9053571224212646 | Evaluation completed (overall=0.905): 8 graded. | Strategy: Simple
  Requested Outcome Delivery: 1.0 (n=8)
  Claim Determination Requirements: 0.9 (n=8)
  Internal Record Use and Grounding: 0.975 (n=8)
  Adjudicator-Ready Presentation and Traceability: 0.9375 (n=8)
  Claim-System Draft Execution: 0.7142857142857143 (n=7)
  Execution:  completed 8, running 0, pending 0, failed 0  (100%)
  Grading:    graded 8, excluded 0, awaiting 0  (100%)
| Decision correct | 3/8 (38%) |   | **Fully correct** | **3/8 (38%)** |   | Mean rubric score (platform) | 0.913 |
draft    ADJ-4AC1CB7AD9 C-2026-04101 approve | payable=69575.00 INR | …
draft    ADJ-D7577A487B C-2026-04102 request_evidence | payable=- INR | …
evidence EVR-9CE1A69F53 C-2026-04102 field=running_hours_at_repair
evidence EVR-E0C1F52796 C-2026-04102 field=inspection_report
evidence EVR-4C51A24CF8 C-2026-04103 field=inspection_report
evidence EVR-4E56BDE0F3 C-2026-04103 field=running_hours_at_repair
draft    ADJ-3D2BEBB5EE C-2026-04110 decline | payable=0.00 INR | …
draft    ADJ-D7ECDCFE3A C-2026-04118 request_evidence | payable=- INR | …
evidence EVR-41EC6DB4A6 C-2026-04118 field=inspection_report
claim_id C-2026-04102 Held · C-2026-04103 Held · C-2026-04118 Held
```

*(trimmed: the full snapshot is in `stages/stage-1/db-actions-after-eval.txt`)*

**Scorer bug found:** 04102 was first read as `decline`. The answer opens *"cannot yet be finally decided — hold for evidence … Do **not** decline the claim"*. I added hold phrasings and negation handling for decline/approve, plus 5 tests: **23/23 pass**. Stage 1 was re-scored (04102 → `request_evidence`; totals unchanged at 3/8). Stage 0, re-scored to a temp folder, came out identical, so its closed folder is untouched.

### S1.10 Hand reading of the disputed answers, and the corpus

```text
04102: "cannot yet be finally decided — hold for evidence … lacks … the inspection report and a running-hours reading at the 18 February 2026 repair date … provisional payable amount is INR 48,420"
04103: "Coverage cannot yet be decided … the required repair-date running-hours reading is missing. The inspection report is also missing"
04118: "hold for evidence; not declined … prima facie covered under TSB-P-0112 … provisional payable amount is INR 67,500"
04114: "HOLD / CANNOT YET DECIDE … cannot approve or decline the claim until the asset's commissioning date is established"   (26 tool calls, 0 MCP)
04116: "CANNOT YET BE DECIDED … The service-claim record for C-2026-04116 / CIE-4000-CH-01950 could not be retrieved"   (32 tool calls, 0 MCP)
```

Corpus (build/gen_docs.py): TSB-G-0029: *"Partners are reminded that a claim must carry the inspection report, the running-hours reading at the date of repair, and the part number actually fitted. This bulletin is advisory…"*. SPA clause 2: *"A claim is submitted within … days of the date of repair, carrying the inspection report, the running-hours reading at the date of repair, and the part number actually fitted."* Ground truth (`build/adjudicate.py`): no inspection-report requirement; uses a reading *"at or before the date of repair"*. Inspection reports in the library: 04101 ✅, 04109 ✅, 04114 ✅; 04102, 04103, 04110, 04116, 04118 ❌.

### S1.11 Why two runs had no MCP

```text
Replicas: --0000004-…-fq4bh created 09:37:17Z · …-xb2r2 03 Oct 21:21:14Z · …-zpm44 09:24:41Z
Run starts: 04118 09:36:43 (mcp=10) · 04116 09:36:47 (mcp=0) · 04114 09:36:50 (mcp=0) · 04110 09:36:52 (mcp=9) · 04109 09:36:55 (mcp=8) · 04103 09:36:58 (mcp=11) · 04102 09:37:01 (mcp=11) · 04101 09:42:13 (mcp=9)
Server logs: no errors, no non-200 responses (one replica's stream)
```

### S1.12 Reset

```powershell
.\scripts\sql-run.ps1 -File scripts\db-reset-actions.sql 2>&1 | Tee-Object -FilePath docs\evidence\stage-1\db-reset-after-eval.txt
```

```text
drafts=0 evidence_requests=0 escalations=0 claims_not_submitted=0
```

---

## World v2 — fixing the inspection-report inconsistency

### W2.1 Decision

The user was unavailable for the choice of fix, so I took the recommended one: correct the wording, leave the ground truth alone. The user then offered to replace the files by hand (15:26 IST). Corrected rule: *the claim is adjudicated from the claim-system record; running hours come from the latest reading at or before the repair date; an inspection report is attached where one was raised and matters where an exclusion depends on it; a missing report doesn't by itself hold a claim.*

### W2.2 Generator edits

- `build/gen_docs.py`, TSB-G-0029 body: *"…must give the part number actually fitted, and should attach the inspection report where one was raised. Claims are adjudicated from the claim-system record: running hours are taken from the latest reading held at or before the date of repair. An inspection report matters where an exclusion depends on it; a missing report does not of itself hold a claim. This bulletin is advisory…"*
- `build/gen_docs.py`, partner agreement clause 2: *"…giving the part number actually fitted and attaching the inspection report where one was raised. Contoso Industrial adjudicates the claim from the claim-system record, taking running hours from the latest reading held at or before the date of repair. An inspection report matters where an exclusion depends on it; a missing report does not of itself hold a claim."*
- `build/gen_teams.py`, Partner Fabrikam "Weekly claim status", Meera's reply: OLD *"Thanks. The three without reports are held, not declined."* → NEW *"Thanks. Send them when you have them. We adjudicate from the claim-system record, so they only hold things up where an exclusion turns on the report."*

### W2.3 Gates and regeneration

```powershell
Push-Location build
..\.venv\Scripts\python.exe adjudicate.py 2>&1 | Select-Object -Last 1
..\.venv\Scripts\python.exe test_traps.py 2>&1 | Select-Object -Last 1
..\.venv\Scripts\python.exe gen_docs.py 2>&1 | Select-Object -Last 3
..\.venv\Scripts\python.exe gen_teams.py 2>&1 | Select-Object -Last 2
Pop-Location
```

```text
All 14 checks passed - guide 03 section 8 reproduces.
31/31 checks passed.
34 Word documents written to C:\Users\sansri\contoso-warranty-rle\out\sharepoint
31 messages across 3 channels written to C:\Users\sansri\contoso-warranty-rle\out\teams
```

A text-level diff of every docx against git HEAD (python-docx: paragraphs and table cells):

```text
TEXT CHANGED: out/sharepoint/02-Bulletins/TSB-G-0029 Claim documentation requirements - reminder.docx
TEXT CHANGED: out/sharepoint/04-PartnerAgreements/SPA-2022-TWD-EM Tailwind Equipment Services.docx
TEXT CHANGED: out/sharepoint/04-PartnerAgreements/SPA-2023-FAB-IN Fabrikam Service Partners.docx
TEXT CHANGED: out/sharepoint/04-PartnerAgreements/SPA-2024-NWD-IN Northwind Field Services.docx
4 document(s) with text changes out of 34
TEAMS Partner Fabrikam / Weekly claim status:
   OLD: Thanks. The three without reports are held, not declined.
   NEW: Thanks. Send them when you have them. We adjudicate from the claim-system record, so they only hold things up where an exclusion turns on the report.
```

The other 30 docx differed only in timestamps, so I restored them with `git restore`. `git status` now shows only the 4 docx and `out/teams/Partner-Fabrikam.json`.

### W2.4 Upload and live check (15:29–15:41 IST)

The user replaced the 4 docx in SharePoint by hand and edited Meera's reply in Teams. Checked through WorkIQ:

| Item | Live state |
| --- | --- |
| TSB-G-0029 (item `01DRFRACUX3AXIZYPTHFAK3LJIYLQAG4CM`) | version 2, modified 2026-10-04T09:59:37Z. Live text (python-docx paragraphs) **identical** to the local file |
| SPA-2022-TWD-EM / SPA-2023-FAB-IN / SPA-2024-NWD-IN | version 2, modified 10:00:09Z / 10:00:17Z / 10:00:24Z |
| Teams reply `1791005234486` (Partner Fabrikam, "Weekly claim status") | `lastEditedDateTime` 2026-10-04T10:10:29Z; body = bold header (unchanged, *22 Jun 2026, 09:40*) + new text |

Gotcha: `/drives/{id}/search(q=…)` still returned the old `lastModifiedDateTime` after the upload; a GET by item id returned the new one. The search index lags.

**Index probe.** Before spending 52 minutes on an evaluation: does the agent's own search already serve the new text? Execution `fc64ba2a-7354-4dcc-9fb5-c2335b000518` on main (MCP off), prompt *"Quote verbatim what bulletin TSB-G-0029 and the Fabrikam partner agreement (SPA-2023-FAB-IN) clause 2 say about inspection reports and running-hours readings. Quote only; do not adjudicate anything."* The answer quoted **both new paragraphs word for word**. New wording present: True; old wording ("must carry the inspection report") present: False. About 10 minutes from upload to being searchable.

## Stage 0 v2 — re-run on the corrected world

### S0v2.1 Setup

```powershell
frontier-tuning tools disable 1c171d49-7f85-4997-8126-ae20829a4dbf --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
# Tool 1c171d49-7f85-4997-8126-ae20829a4dbf disabled.
# tools available: 125 · MCP (1c171__): 0
```

`stages/stage-0-v2/` and `stage-1-v2/` were created as copies. SHA-256 (first 12 characters): skill `358B61B409E6`, rubrics `A3BB46F8945D`, prompts `FFB8F1D4510B`, all identical to v1. The rubrics on the platform skill `cf00d339` equal the pinned file (5 rubrics). The 8 Evaluation samples from v1 were reused, not re-uploaded.

### S0v2.2 Evaluate

```powershell
frontier-tuning evaluate start --skill-id cf00d339-5217-4cd1-b390-cc0d911735da --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json
```

```text
"JobId": "53495f74-fcd5-47ef-8b33-43893a49eb04", "Status": "Running", "CreatedAt": "2026-10-04T10:13:23Z"
"WorkspaceSnapshotMetadata": { "SkillsCount": 1, "ToolsCount": 3, "SamplePromptsCount": 8, "KnowledgeSourcesCount": 4 }
```

The snapshot matches v1 stage 0 (ToolsCount 3 = MCP off).

### S1v2.0 Pre-warm the MCP replicas (defect 2), done during the stage 0 v2 run

Before: `minReplicas 1, maxReplicas 3`, default HTTP scale rule, revision `--0000004`.

```powershell
az containerapp update -n contoso-service-mcp -g pcdotai-agent --min-replicas 3 --max-replicas 3
```

```text
{ "max": 3, "min": 3, "rev": "contoso-service-mcp--0000005", "state": "Succeeded" }
contoso-service-mcp--0000005-56d89cf494-5j99j  Running  2026-10-04T10:14:14Z
contoso-service-mcp--0000005-56d89cf494-h2tsj  Running  2026-10-04T10:14:14Z
contoso-service-mcp--0000005-56d89cf494-qtngf  Running  2026-10-04T10:14:14Z
/healthz → {"status":"ok","assets":117}
```

This costs 3 always-on replicas. Revert with `--min-replicas 1` once the stage 1 v2 evaluation finishes, if cost matters.

### S0v2.3 Results

`evaluate status` → `"Status": "Succeeded"`, `"StatusMessage": "Evaluation completed (overall=0.535): 8 graded."`, completed 2026-10-04T10:39:01Z (26 min after start; v1 took 52 min).

| Rubric | AvgScore | n |
| --- | --- | --- |
| Requested Outcome Delivery | 0.84375 | 8 |
| Claim Determination Requirements | 0.43125 | 8 |
| Internal Record Use and Grounding | 0.725 | 8 |
| Adjudicator-Ready Presentation and Traceability | 0.675 | 8 |
| Claim-System Draft Execution | 0.0 | 5 |

Ground-truth scorer: decisions read `{'request_evidence': 5, 'review': 2, 'decline': 1}`; fully correct **0/8**. The ❓ answers (04103, 04116) were read by hand: both say *"unable to complete adjudication"* / *"could not be completed"*, i.e. holds, so they're wrong. 04109 is *"provisional decline"*, citing TSB-C-0038, not ADD-IN-2.1.

Evidence the v2 text was used, 04110: *"That absence does not by itself justify declining or holding the claim: the organisation's documentation bulletin says an inspection report matters where an exclusion depends on it, and a missing inspection report does not itself hold a claim."*

Also from the answers: the agent tried the claim tools anyway and reports `ToolNotFound` (04116, 04103, 04110).

💭 v1 → v2 rubric 0.630 → 0.535, with only document wording changed, and the agent couldn't use that wording without claim facts. Treat about ±0.1 on 8 samples as run-to-run noise.

## Stage 1 v2

### S1v2.1 Setup and start

```text
/healthz → {"status":"ok","assets":117}
db-baseline.sql → 0 0 0 0
tools enable → Tool 1c171d49-7f85-4997-8126-ae20829a4dbf enabled.
tools available, read 1: 137 · MCP 12; read 2: 137 · MCP 12
```

No hand probe this time: the MCP path was already proven by the v1 probe (`8ce435fa-…`), and replicas were warm and healthy.

```text
"JobId": "95f7d234-df64-4e71-aa82-2d3db8d51b11", "Status": "Running", "CreatedAt": "2026-10-04T10:44:30Z"
SkillsCount 1 · ToolsCount 4 · SamplePromptsCount 8 · KnowledgeSourcesCount 4
```

### S1v2.2 Results

Poll: `16:36 TERMINAL "StatusMessage": "Evaluation completed (overall=0.991): 8 graded."` (completed about 11:06 UTC, 22 min).

| Rubric | AvgScore | n |
| --- | --- | --- |
| Requested Outcome Delivery | 1.0 | 8 |
| Claim Determination Requirements | 0.975 | 8 |
| Internal Record Use and Grounding | 1.0 | 8 |
| Adjudicator-Ready Presentation and Traceability | 0.9791666666666666 | 8 |
| Claim-System Draft Execution | 1.0 | 6 |

MCP tool use per run (distinct `1c171__*` tools in the trace): 04101 9 · 04102 9 · 04103 10 (+`request_missing_evidence`) · 04109 8 · 04110 9 · 04114 9 · 04116 9 · 04118 9. **8/8 runs used the tools.**

First scorer pass: 6/8. 04109 was read as `escalate`, but the answer says *"Claim C-2026-04109 should be declined for warranty payment. Current claim-system status is "Submitted"; no draft adjudication, evidence request, or escalation was created or modified."* That's a scorer bug: "no" is 51 characters before "escalation", outside the 25-character negation window. Fix: `LIST_NEGATION_RE` (a negated list ending "…, or <match>"). 2 tests added (one guarding "Not covered under warranty, so escalate…"). `test_score_ground_truth.py`: **25/25**. Re-scored all four stage folders: the stage-0, stage-1 and stage-0-v2 CSVs were unchanged; stage-1-v2 → **7/8**.

04103 answer (excerpt): *"Decision: Hold / request evidence — not yet approvable or declinable. The asset meets the applicable time and running-hours coverage tests, but the claim is for a seal kit. Global Warranty Policy clause 5.4 excludes seals when fitted as routine maintenance. No claim-specific inspection report or failure diagnosis was located…"* Ground truth: approve ₹19,150 (`exclusion_flags: []`). The `get_claim` docstring and `spec/catalog.json` give only "Seal kit - replace". The failure narrative ("Shaft seal weeping at the drive end") exists only in inspection-report text (`gen_docs.py`), and 04103 has no report. Rubric for this answer: 1.0.

DB writes (`db-actions-after-eval.txt`): drafts ADJ-8E1088E707 (04101 approve 69575) · ADJ-E40E29E578 (04102 approve 48420) · ADJ-B5F41EE4C6 (04103 request_evidence) · ADJ-944250B564 (04110 decline) · ADJ-52BBD071CD (04114 approve 199175) · ADJ-96937208C5 (04118 approve 67500); evidence EVR-CAA13AFF92 (04103); 04103 status Held. Then `db-reset-actions.sql` → baseline `0 0 0 0`.

ACA left at min = max = 3 replicas (revision `--0000005`).

---

## World v2.1 — clause 5.4 made unambiguous (19:45 IST)

User decision: *"if in real life you would manually correct that in a way for the right interpretation, then let's update the policy so that there is no ambiguity."* I chose option (b), a policy wording change.

`spec/instruments.json`, POL-WAR-4.2 clause 5.4 "Exclusion - consumables":
- OLD: *"Filters, fluids, belts, seals fitted as routine maintenance, and other consumables are excluded."*
- NEW: *"Filters, fluids, belts, seals and other consumables are excluded when replaced as scheduled maintenance. Scheduled maintenance is not claimable under warranty and has no warranty operation code, so a consumable claimed under a warranty repair operation code is treated as a corrective repair and is covered, unless an inspection report records the replacement as routine."*

Why the ground truth can't move: the engine applies only exclusion 5.2 (`adjudicate.py` line ~409, `exclusion_flags`). 5.4 is never applied. Only 2 claims are seal kits: 04103 (eval, approve) and 04110 (eval, decline on time and hours).

```text
adjudicate.py   → All 14 checks passed - guide 03 section 8 reproduces.
test_traps.py   → 31/31 checks passed.
populate.py     → Design conformance: OK
ground_truth.py → wrote out/GROUND-TRUTH.md (993 lines); diff = the "Produced <date>" line only
gen_docs.py     → 34 Word documents; text changed vs HEAD 52fcc0f: POL-WAR-4.2 only
gen_teams.py    → 31 messages; no content change
```

Timestamp-only docx and Teams files were restored. To upload: `01-Policy/POL-WAR-4.2 Contoso Industrial Global Warranty Policy v4.2.docx`.

Stages 0 v2 and 1 v2 were measured on v2, before this. Not re-run: the change affects one claim (04103), and stage 2 moves to a new prompt set.

### V2.1 upload check

POL-WAR-4.2 item `01DRFRACQDMPIPW4LWQ5E37EZ4PCKCCLWD`: version 2, `lastModifiedDateTime` 2026-10-04T14:16:39Z (19:46 IST). Live text == local text: True; "corrective repair" present: True.

## Stage 2-base — stage 1's setup on all 30 eval prompts (20:00 IST)

User: *"for stage 2, yes we could use the difficult scenarios"*, then *"lets proceed now with stage 2 base"*. Also: *"when you reach stage 2b and determine that the skill needs to be improved, i think it is important i understand how we make the changes, and not let the skill echo what is in the rubric at the same time."* Recorded as a 2b commitment in JOURNEY.

### S2b.1 Samples 8 → 30

```text
frontier-tuning samples delete-by-skill --skill-id cf00d339-…   → Error: No such option '--skill-id'.
frontier-tuning samples upload stages\stage-2-base\samples.jsonl --skill-id cf00d339-… --type Evaluation
  → Uploaded: 30 | Failed: 0          (now 38 Evaluation; the delete had failed)
frontier-tuning samples delete <id> --yes   × 8 old ids (from samples-before-delete.json) → 8 × "deleted successfully"
samples list → 30 samples; every prompt matched to a title (titles are cut at ~50 chars)
```

Files: `docs/evidence/stage-2-base/samples-before-delete.json`, `samples-upload.txt`, `samples-after.json`.

### S2b.2 Capacity and pre-flight

ACA: 0.5 vCPU / 1 GiB per replica. SQL `GP_S_Gen5_1` (serverless, min 0.5, auto-pause 60 min).

```text
az containerapp update … --min-replicas 5 --max-replicas 5 → rev contoso-service-mcp--0000006, 5 replicas Running
healthz → {"status":"ok","assets":117}
db-baseline → 0 0 0 0
tools available → 88 (first read) · then 137 ×4: 1c171=12 lumina_sandbox=9 m365=5 mcp_OneDriveRemoteServer=18
                  mcp_SharePointRemoteServer=31 polymer_atomic=17 teams=43 workspace_health=2
platform rubrics == pinned: True
```

### S2b.3 Evaluate

```text
"JobId": "9f4ad313-9629-4571-8f58-13a7bba63c97", "Status": "Running", "CreatedAt": "2026-10-04T14:36:56Z"
SkillsCount 1 · ToolsCount 4 · SamplePromptsCount 30 · KnowledgeSourcesCount 4
```

### S2b.4 Results

Poll: `20:50 TERMINAL "StatusMessage": "Evaluation completed (overall=0.978): 30 graded."` (43 min).

Rubrics: Requested Outcome Delivery 0.994 (30) · Claim Determination Requirements 0.960 (30) · Internal Record Use and Grounding 0.997 (30) · Adjudicator-Ready Presentation and Traceability 0.982 (30) · Claim-System Draft Execution 0.958 (24).

First scorer pass: 24/30 correct, 1 ❓. All 6 were read by hand:

| Claim | Evidence | Verdict |
| --- | --- | --- |
| 04140 | *"Decision: decline under warranty. … No draft adjudication, evidence request, goodwill escalation, or other claim-system change was made."* | scorer misread |
| 04150 | *"The repair is covered by **TSB-C-0051**"*; first cue sentence hit was "Under … POL-WAR-4.2 clause 1.4" | scorer misread |
| 04153 | *"**TSB-C-0051 does not govern this repair.** … Because TSB-C-0051 does not cover controls, **ADD-IN-2.1 A1** … governs"* | scorer misread |
| 04131 | *"the claim system contains a second apparently identical submitted claim, C-2026-04136"*; `claims.json`: 04131 (eval) == 04136 (train) in every field except id. Identical pairs: 04129/04133, 04130/04134, 04131/04136, 04132/04137 | world defect |
| 04178 | Key: *"Coverage cannot be determined: ADD-IN-2.1 sets a limit of 5000 running hours and the asset registry holds no telemetry reading…"* with `expiry_date 2026-04-01`, repair 2026-06-18. Agent: *"DECLINE … expired on the time limb on 1 April 2026"*. `adjudicate.py` lines 340–354 test the missing reading before the time limit | answer-key defect |
| 04172 | *"Recommended claim action: … either (a) decline the warranty element, or (b) … route the INR 312,000 request to the Warranty Operations Head"*; *"No adjudication, evidence request, or goodwill escalation has been recorded"*. Called `get_goodwill_authority(312000, India)` | genuine miss; rubric 1.0 |

Scorer changes: `LIST_ITEM_NEGATION_RE`; a ", but/so/then/and" clause break cancels a negation; `_instrument_negated()` (does not / is not / cannot … after; "not under / rather than" before; "clause 1.4" after); cue adds "covered by". A first attempt with tiered cues ("govern" first) regressed 04114 and 04166, so it was reverted to a single pass in sentence order. Tests 29/29. Re-score vs the previous CSVs: stage-0 none · stage-1 none · stage-0-v2 04116 governing POL→TSB (held answer, correctness unchanged) · stage-1-v2 04103 governing POL→ADD-IN-2.1 (unchanged) · stage-2-base 04140, 04150, 04153 → correct. **27/30.**

DB: 23 drafts · 4 evidence (04131 duplicate_claim_resolution; 04177 ×2; 04178 running_hours_at_repair) · 1 escalation (GWE-1CC95816E4, 04171, ₹67,400 → Regional Service Manager). Reset → 0 0 0 0.

---

## World v2.2 — two defects found by stage 2-base (21:15 IST)

The user was asked to choose the direction (frontier headroom gone) and was unavailable. Fixing these two defects is needed under every option, so they were fixed. The direction is still open.

| Defect | Fix |
| --- | --- |
| Answer key tested the missing hours reading before the time limit (04178) | `adjudicate.py`: the missing-reading branch runs only if `repair <= expiry_date`; otherwise it falls through to decline ("whichever occurs first") |
| …which would have left eval abstention at 2, not 3 | `populate.py`: the no-reading assets (2110–2112) are commissioned **2025-10-01** (was 2024-10-01), so the time limit hasn't run out and the missing reading really decides |
| 4 eval claims had identical training twins (serial-boundary) | `populate.py`: training serials `[1198, 1201, 1848, 1849, 1852, 1853]` (were `[1199, 1200, 1849, 1850, 1851, 1852]`, which reused the eval serials and therefore the eval assets) |
| Guard | `populate.py` now fails on any two claims identical apart from id/submitted date, and on an abstention claim that doesn't decide `request_evidence` |

```text
adjudicate.py → All 14 checks passed · test_traps.py → 31/31 · populate.py → Design conformance: OK
claims 90 (eval 30 / train 60) · decisions approve 52, decline 24, escalate 5, request_evidence 9
answer-key diff vs before: only 6 TRAIN claims changed serial (04133–04138); no expected decision, instrument or payable changed
04178 now: request_evidence, expiry 2027-04-01, commissioning 2025-10-01
engine on the OLD asset (commissioned 2024-10-01) → decline   (the engine fix alone)
```

Regenerated: ground truth, DB seeds, decks, docs, samples, sheets, Teams. A content diff vs HEAD (docx text, xlsx cells, pptx text) showed only POL-WAR-4.2 changed (the v2.1 clause 5.4, already uploaded). The other 38 rewrites were timestamp-only and were restored. **No SharePoint or Teams upload needed.** `out/samples/warranty-adjudication.train.jsonl` changed (serials in training prompts); the eval prompts are unchanged.

Azure SQL reload with `load-sql.ps1` (Entra token): `OK: 8 batches executed`. Assets 117 (local 120; the 3 registry-unknown abstention assets aren't loaded, as before) · claims 90 · telemetry 3007. Spot checks: 04136 → CIE-4000-CH-01849; 02110 commissioned 2025-10-01 with 0 readings. healthz ok; baseline 0 0 0 0.

Not re-run: stage 2-base (job `9f4ad313`) stays the record on v2.1. 04178 and 04131 are documented as defects there.

## Stage 3-mini-base — the small model, same setup (21:12 IST)

User: *"do we now not create the need for better rubrics by using the SLM first and then go about improving it? Would we not be assuming the mini model would fail with the same rubrics before indeed finding them to be so? I am trying to progress the hill climb with the realization at every step for the next."* Agreed: the evidence that the rubrics don't follow correctness is n=1 (04172), so measure first.

Before this, the rubric for right vs wrong answers (scorer CSVs):

```text
stage-1:      right n=3  mean 1.000 | wrong: 04118 0.96, 04116 0.627, 04114 0.747, 04103 0.967, 04102 1.0
stage-1-v2:   right n=7  mean 0.990 min 0.93 | wrong: 04103 1.0
stage-2-base: right n=27 mean 0.979 min 0.77 | wrong: 04178 1.0, 04172 1.0, 04131 0.96   (04178, 04131 = world defects)
```

Models: `models list` → `dev-ct-gpt-54-mini-mp` (GPT-5.4-Mini, IsSelected False), `prod-gpt-56-reasoning-sol` (IsSelected True). `evaluate start --base-model <id>` accepts it without `models set`.

Hand probe, execution `bb32816e-189d-4819-9889-05d84e2ceb95`, `chat -q "Adjudicate claim C-2026-04114." --model dev-ct-gpt-54-mini-mp --strategy simple`: Completed, 19 tool calls, **all `1c171__*`** (get_claim ×4, get_asset ×2, get_service_history ×2, get_tsb_index ×2, lookup_part ×2, get_dealer ×2, get_running_hours, find_prior_claims, create_claim_adjudication ×2). Answer: *"Decision: Request evidence — claim cannot yet be finally adjudicated"*. Billing: 474,720 input tokens, 5,513 output. DB: ADJ-071822BABB and ADJ-6DEE6A7E4B (both request_evidence, 04114) → reset → 0 0 0 0.

⚠️ Pre-flight `tools available` → **106** (= 137 − 31 SharePoint). I started the evaluation without re-reading; that was a slip. Re-reads at 21:21–21:22 → 137 ×4 with all sources. The probe's `diagnostics` is null, so the tools offered to it are unknown. 🔬

```text
"JobId": "73fa5456-45f6-411c-92e1-b553931acab8", "BaseModelName": "dev-ct-gpt-54-mini-mp", "CreatedAt": "2026-10-04T15:50:40Z"
SkillsCount 1 · ToolsCount 4 · SamplePromptsCount 30 · KnowledgeSourcesCount 4
```

### S3m.2 Stuck, then cancelled

```text
22:43 diagnostics: Phase Submitting · completed 28, running 1 · Last Progress 16:49:39Z · Retried 5 · Resubmissions 7 · Reliability Partial
partial results: 04118 Status Running (0 tools) · 04110 Pending · every submission RetryCount 1
MCP: healthz ok; ACA log POST /mcp 200 at 17:16Z (still serving)
```

User: *"cancel"* (22:52). `evaluate cancel` has no `--yes` → `{"status": "CancelRequested"}` → poll 22:53 TERMINAL, Status `Cancelled`, OverallScore null. Diagnostics: score 0.415, 28 graded, 165 rubric scores, resubmissions 8.

### S3m.3 Reading the 28: a measurement artefact

The first scorer pass gave correct 10 (mean rubric 0.310) vs wrong 14 (mean rubric 0.466), which looked like the rubrics rewarding wrong answers. Hand check:

- 04103 grader, Outcome 0.0: *"The only successfully delivered finish message states that the agent was "not able to complete a final...adjudication"… Earlier detailed finish…"*. The exported `Response` is a single part: *"Recommended position: APPROVE under standard India warranty coverage. Total payable: INR 19,150.00."* A search of the whole execution object finds "not able to complete" **only in `RubricResults[].Reasoning`**.
- The same pattern in grader reasoning ("successfully delivered finish" / "failed finish" / "earlier finish attempt"): **12/28** runs, covering most of the scorer's "correct" ones (04103, 04116, 04139, 04140, 04152, 04153; 04114's reasoning says "unable to finalize").
- Document use: **11/28** runs called `m365__search_enterprise_files`, SharePoint or Teams tools (up to 10 calls). The other 17 used only `1c171__*`. So the 106-tools read didn't block documents.

Per rubric (computed from the samples): Outcome 0.537 · Determination 0.119 · Grounding 0.300 · Presentation 0.393 · Draft Execution 0.724. DB: 36 drafts, 6 evidence requests → reset → 0 0 0 0.
