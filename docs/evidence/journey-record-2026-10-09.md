# 2026-10-09: stage 2 closure on 29 claims

User decision: exclude the last claim rather than wait. Stopped attached shell `stage2b` using `stop_powershell`, then cancelled its active platform job. No excluded answer used. User subsequently re-enabled SQL public network access after the daily SFI shutdown.

## Cancellation

Exactly as run:

```powershell
frontier-tuning evaluate cancel beb6e3ac-ceb5-4283-b107-7a5368bdbd7f --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
```

Verbatim output:

```text
Evaluation job cancel requested successfully.
Job ID: beb6e3ac-ceb5-4283-b107-7a5368bdbd7f
Workspace ID: 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
```

Exactly as run:

```powershell
frontier-tuning --output json evaluate status beb6e3ac-ceb5-4283-b107-7a5368bdbd7f --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\excluded-04130-status.json; frontier-tuning --output json evaluate results beb6e3ac-ceb5-4283-b107-7a5368bdbd7f --samples --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Out-File docs\evidence\stage-2\2b\excluded-04130-results.json -Encoding utf8
```

Full outputs: [status](stage-2/2b/excluded-04130-status.json) (`Status: Cancelled`, `isTerminal: true`), [excluded results](stage-2/2b/excluded-04130-results.json). Retained only as evidence, not in the merged reported cohort.

## Merge and automatic score

Exactly as run:

```powershell
.\.venv\Scripts\python.exe scripts\summarise-stage.py docs\evidence\stage-2\2b stages\stage-2 --consolidate 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\summary-output.txt
```

Full verbatim output: [summary-output.txt](stage-2/2b/summary-output.txt). Raw merged submissions: [stage 2 results](../../stages/stage-2/eval-results-samples.json). Automatic result 14/29; manual inspection resolves three extraction errors and four review flags → **17/29**, documented without editing raw responses in [hand-check.md](../../stages/stage-2/hand-check.md).

## Paired comparison

Exactly as run:

```powershell
@'
import sys,json,statistics
from pathlib import Path
from collections import defaultdict
sys.path.insert(0,str(Path('scripts').resolve()))
import score_ground_truth as gt
sets={}
for stage in ('stage-1','stage-2'):
 p=Path('stages')/stage/'eval-results-samples.json'; rows=gt.score(gt.read_executions(p),gt.load_expected()); rows=[r for r in rows if not r['claim'].endswith('04130')]
 if stage=='stage-2':
  for r in rows:
   if r['claim'][-5:] in ('04115','04116','04151'): r['correct']=True
   if r['claim'][-5:] in ('04102','04150','04171'): r['correct']=False
 sets[stage]={r['claim']:r for r in rows}
 right=[r['rubric'] for r in rows if r['correct']]; wrong=[r['rubric'] for r in rows if not r['correct']]
 d=json.loads(p.read_text()); subs=[s for s in d['Submissions'] if 'C-2026-04130' not in s['Sample']['Prompt']]; calls=[len(s['Execution'].get('ToolExecutions') or []) for s in subs]
 per=defaultdict(list)
 for s in subs:
  for rr in s['Execution']['RubricResults']:
   if rr.get('Score') is not None: per[rr['RubricName']].append(rr['Score'])
 print(stage,'correct',len(right),'rubric',statistics.mean(r['rubric'] for r in rows),'calls mean',statistics.mean(calls),'median',statistics.median(calls),'right',statistics.mean(right),'wrong',statistics.mean(wrong),'ranking',sum((a>b)+.5*(a==b) for a in right for b in wrong)/(len(right)*len(wrong)))
 print('per rubric',{k:round(statistics.mean(v),3) for k,v in per.items()})
 print('handin flags',sum('rejected' in gt._grader_notes(s['Execution']).lower() or 'formatter' in gt._grader_notes(s['Execution']).lower() for s in subs))
 if stage=='stage-2':
  for s in subs:
   tools=s['Execution'].get('ToolExecutions') or []
   errors=[t for t in tools if any(w in json.dumps(t).lower() for w in ('deny public','connection was denied','public network access','sql exception','sqlexception'))]
   if errors: print('SQL errors',s['Sample']['Prompt'],len(errors))
for c,r in sets['stage-2'].items():
 old=sets['stage-1'][c]['correct']; new=r['correct']
 if old!=new: print('CHANGED',c,old,'->',new)
'@ | .\.venv\Scripts\python.exe - 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\paired-comparison-output.txt
```

Full verbatim output: [paired-comparison-output.txt](stage-2/2b/paired-comparison-output.txt). The narrow SQL-error string scan found no matches in retained tool records; this does not prove the overnight database was accessible or reset successfully. The keyword hand-in flag is not a count of all failed finish attempts.

## SQL cleanup

First attempt, exactly as run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\excluded-04130-db-snapshot.txt; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-reset-actions.sql 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\final-reset.txt; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-baseline.sql 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\final-baseline.txt
```

Dead end: SQL denied public access. Full outputs: [snapshot failure](stage-2/2b/excluded-04130-db-snapshot.txt), [reset failure](stage-2/2b/final-reset.txt), [baseline failure](stage-2/2b/final-baseline.txt). The outer pipeline exited zero despite these failures; do not treat that as successful cleanup.

After the user re-enabled access, exactly as run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\excluded-04130-db-snapshot-retry.txt; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-reset-actions.sql 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\final-reset-retry.txt; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-baseline.sql 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\final-baseline-retry.txt
```

Full outputs: [snapshot](stage-2/2b/excluded-04130-db-snapshot-retry.txt), [reset](stage-2/2b/final-reset-retry.txt), [baseline](stage-2/2b/final-baseline-retry.txt). Both reset and baseline explicitly show drafts, evidence requests, escalations and claims-not-seeded **0 0 0 0**.

## Closure

Recorded in [JOURNEY](../JOURNEY.md), [stage index](../../stages/README.md) and [stage 2](../../stages/stage-2/README.md). No stage 3 started, no live skill rollback, no commit/tag created. Stage 1 remains the stronger measured configuration. The [run log](stage-2/2b/run-log.txt) records a 216-minute job despite a 75-minute runner default; timeout-enforcement root cause remains unverified.

## SQL causality check

User asked whether regression toward the end must be caused by SQL's daily public-access shutdown. Checked **retained executions**, not discarded attempts. Times converted from execution UTC to IST (+05:30); pre/post groups use retained execution start time, not original sample order. They are different claim mixes, not a controlled temporal experiment.

Exactly as run:

```powershell
@'
import json,re,sys
from pathlib import Path
from datetime import datetime,timedelta
sys.path.insert(0,str(Path('scripts').resolve()))
import score_ground_truth as gt
root=Path('stages'); p=root/'stage-2'/'eval-results-samples.json'
d=json.loads(p.read_text()); rows=gt.score(gt.read_executions(p),gt.load_expected())
truth={r['claim']:r['correct'] for r in rows}
for c in ('04115','04116','04151'): truth['C-2026-'+c]=True
for c in ('04102','04150','04171'): truth['C-2026-'+c]=False
base={r['claim']:r['correct'] for r in gt.score(gt.read_executions(root/'stage-1'/'eval-results-samples.json'),gt.load_expected())}
for before in (True,False):
 ss=[s for s in d['Submissions'] if (datetime.fromisoformat(s['Execution']['StartDateTime'])+timedelta(hours=5,minutes=30)).day==(8 if before else 9)]
 cs=[re.search(r'C-2026-\d+',s['Sample']['Prompt']).group() for s in ss]
 print('Before midnight IST' if before else 'After midnight IST',len(cs),'claims; stage1',sum(base[c] for c in cs),'correct; stage2',sum(truth[c] for c in cs),'correct; newly wrong',[c[-5:] for c in cs if base[c] and not truth[c]])
for stage in ('stage-1','stage-2'):
 ss=json.loads((root/stage/'eval-results-samples.json').read_text())['Submissions']; calls=affected=0
 for s in ss:
  if 'C-2026-04130' in s['Sample']['Prompt']: continue
  failed=[t for t in s['Execution']['ToolExecutions'] if t['Status']!='Completed']; calls+=len(failed); affected+=bool(failed)
 print(stage,'failed tool calls',calls,'claims affected',affected)
reads=writes=0
for s in d['Submissions']:
 for t in s['Execution']['ToolExecutions']:
  if not t['Title'].startswith('1c171'): continue
  v=t['Output']
  while isinstance(v,str) or isinstance(v,list):
   v=json.loads(v) if isinstance(v,str) else v[0]['text']
  assert t['Status']=='Completed'
  if '__get_claim_dossier' in t['Title']: assert v['claim']['found'] is True; reads+=1
  else: assert v['created'] is True; writes+=1
print('Verified all retained SQL-backed agent calls:',reads,'successful dossier reads;',writes,'successful writes; zero failure payloads.')
'@ | .\.venv\Scripts\python.exe - 2>&1 | Tee-Object -FilePath docs\evidence\stage-2\2b\sql-regression-summary.txt
```

Verbatim output:

```text
Before midnight IST 15 claims; stage1 13 correct; stage2 9 correct; newly wrong ['04102', '04131', '04140', '04148', '04150', '04152']
After midnight IST 14 claims; stage1 9 correct; stage2 8 correct; newly wrong ['04149', '04153', '04178']
stage-1 failed tool calls 11 claims affected 5
stage-2 failed tool calls 66 claims affected 17
Verified all retained SQL-backed agent calls: 63 successful dossier reads; 31 successful writes; zero failure payloads.
```

The six pre-midnight new losses ended between 20:14 and 23:22 IST. The post-midnight losses ended at 01:31 (04149), 01:36 (04153) and 05:15 (04178); all had successful dossier payloads. The [detailed check](stage-2/2b/sql-regression-check-verified.txt) records per-claim times and failed tool names: 62 of 66 failed calls are SharePoint browsing (getSiteByPath 25, listDocumentLibrariesInSite 12, getFolderChildren 24, getDefaultDocumentLibraryInSite 1); the other four are file/storage/Teams tools, not SQL.

The [snapshot record](stage-2/2b/db-snapshots.txt) contains successful local SQL queries after jobs ending at 00:16, 01:17 and 04:54, then a public-access denial after the final five-claim job at 05:54. The run log's “saved and reset” line is misleading for that last job. These records **do not establish an actual shutdown at 00:00 IST**, nor successful resets throughout the night. They distinguish failed laptop-side cleanup from the successful retained agent-side SQL calls.

Dead end: the initial [payload scan](stage-2/2b/sql-regression-check.txt) assumed write success was `ok: true` and mixed all failed tools into an issue count. Actual writes use `created: true`; corrected and verified above. Do not use its issue count as a SQL failure count.

**Conclusion:** measured regression is not restricted to late batches and cannot be explained by a demonstrated SQL failure in these retained executions. SQL cleanup failure is confirmed; retrieval/navigation failures and non-answers are separately observed. No assertion that the skill alone caused them, and no rerun started.

## Stage 3 started

User authorised stage 3 at 08:35 IST. Configuration: restored stage 1 instructions; unchanged live rubrics and Evaluation sample IDs; MAI-CODE-5b; exclude 04130 from both full-run arms; request BestOfN N=4.

Dependency-bootstrap dead end, exactly as run:

```powershell
& 'C:\Users\sansri\.agents\skills\microsoft-foundry\scripts\check-and-setup-dependencies.ps1'
```

Output excerpt *(trimmed)*:

```text
ERROR: no compatible version of microsoft.foundry found for azd 1.25.1
Update available: 1.25.1 -> 1.35.1 (https://github.com/Azure/azure-dev/releases/tag/azure-dev-cli_1.35.1)
To update, run `winget upgrade Microsoft.Azd`
```

No azd upgrade; no Foundry API used. Continued on the existing Frontier Tuning CLI, version 0.3.16.

Restoration, exactly as run:

```powershell
New-Item -ItemType Directory -Force stages\stage-3, docs\evidence\stage-3\probe | Out-Null; Copy-Item stages\stage-1\warranty-assistant.md stages\stage-3\warranty-assistant.md; Copy-Item stages\stage-1\warranty-assistant.rubrics.json stages\stage-3\warranty-assistant.rubrics.json; Copy-Item stages\stage-1\samples.jsonl stages\stage-3\samples.jsonl; Copy-Item stages\stage-1\sample-map.json stages\stage-3\sample-map.json; Copy-Item 'C:\Users\sansri\.copilot\session-state\17bb335a-9ca3-491f-a6d8-8f61cd8edd1e\files\stage3-skill-before.json' docs\evidence\stage-3\skill-before.json; $body=((Get-Content stages\stage-3\warranty-assistant.md -Raw) -split '## Instructions',2)[1].Trim(); frontier-tuning skills update cf00d339-5217-4cd1-b390-cc0d911735da --instructions $body --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object docs\evidence\stage-3\restore-skill-output.txt; if ($LASTEXITCODE -ne 0) { throw 'Skill restoration failed' }; frontier-tuning --output json skills get cf00d339-5217-4cd1-b390-cc0d911735da --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 | Out-File docs\evidence\stage-3\skill-restored.json -Encoding utf8
```

Full outputs: [restore](stage-3/restore-skill-output.txt), [live skill before](stage-3/skill-before.json), [live skill after](stage-3/skill-restored.json).

Verification and probe submission, exactly as run:

```powershell
@'
import json
from pathlib import Path
stage=Path('stages')/'stage-3';ev=Path('docs')/'evidence'/'stage-3'
s=json.loads((ev/'skill-restored.json').read_text(encoding='utf-8-sig')); before=json.loads((ev/'skill-before.json').read_text(encoding='utf-8-sig'))
assert s['Prompt'].replace('\r\n','\n').strip()==(stage/'warranty-assistant.md').read_text(encoding='utf-8-sig').split('## Instructions',1)[1].strip()
assert s['Rubrics']==before['Rubrics']
a=json.loads((stage/'warranty-assistant.rubrics.json').read_text(encoding='utf-8-sig'))
for x,y in zip(a,s['Rubrics']):
 for k in ('RubricName','Description','ChecklistItems','ScoringScale','ScoringCriteria','RedFlags','MeasurementMethod','Importance'): assert x.get(k)==y.get(k),(x['RubricName'],k)
assert len(a)==len(s['Rubrics'])==6
print('PASS: stage 1 instructions restored (CRLF-normalised); live rubrics unchanged; all six scoring definitions match pinned stage 1. Server category/type metadata differences retained, not rewritten. Evaluation sample IDs unchanged.')
'@ | .\.venv\Scripts\python.exe - 2>&1 | Tee-Object docs\evidence\stage-3\configuration-check.txt; if ($LASTEXITCODE -ne 0) { throw 'Configuration mismatch' }; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-baseline.sql 2>&1 | Tee-Object docs\evidence\stage-3\baseline-before-probe.txt; if ($LASTEXITCODE -ne 0) { throw 'SQL baseline inaccessible' }; $sid=(Get-Content stages\stage-3\sample-map.json -Raw | ConvertFrom-Json | Where-Object {$_.claim -eq 'C-2026-04101'}).id; frontier-tuning --output json evaluate start --sample-id $sid --base-model dev-ct-mai-code-mp --strategy BestOfN --best-of-n 4 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object docs\evidence\stage-3\probe\start.json
```

Full outputs: [verification](stage-3/configuration-check.txt), [clean baseline](stage-3/baseline-before-probe.txt), [start response](stage-3/probe/start.json). Job `44945388-1e87-41b5-adfd-32123fe29268` accepted at 03:17:41 UTC (08:47:41 IST). Acceptance alone does not verify that four rollouts execute.

Dead end: initial literal verification did not normalise CRLF and compared server-assigned rubric metadata against authored JSON; corrected above without altering live rubrics.

Safeguard validation: successful output capture, nonzero child exit propagation, one-second process-tree timeout and JSON parsing all passed. Initial 10-second Windows process startup allowance timed out; success/failure tests passed using 60 seconds. A deliberate SQL `THROW 51000, 'Expected safeguard test', 1;` returned exit 1; baseline returned exit 0. No schema/data changes from that test.

Probe monitor, exactly as run (attached async shell `stage3-probe`, not detached):

```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $map=Get-Content stages\stage-3\sample-map.json -Raw | ConvertFrom-Json; $probe=($map | Where-Object {$_.claim -eq 'C-2026-04101'}).id; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\eval-batches.ps1 -Env $e -Samples '' -OutDir docs\evidence\stage-3\probe -Strategy BestOfN -BestOfN 4 -TimeoutMin 75 -MaxAttempts 1 -AdoptJob 44945388-1e87-41b5-adfd-32123fe29268 -AdoptSamples "04101=$probe"
```

The 75-minute monitor budget starts on adoption, not original submission. Per-command stdout/stderr retained under [probe](stage-3/probe/); SQL failure stops the monitor instead of claiming successful reset. Full arms remain gated on probe verification.

Startup verification, exactly as run:

```powershell
frontier-tuning --output json evaluate status 44945388-1e87-41b5-adfd-32123fe29268 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object docs\evidence\stage-3\probe\status-initial.json; Get-Content docs\evidence\stage-3\probe\run-log.txt -Tail 5; git --no-pager diff --check
```

[Full status](stage-3/probe/status-initial.json) confirms `Strategy: BestOfN`, `StrategyBody: {"N": 4}`, `Status: Running`. Monitor startup:

```text
08:52:24 adopting job 44945388-1e87-41b5-adfd-32123fe29268 for 04101
```

Whitespace check passed; unrelated existing files emitted LF→CRLF warnings. Actual candidate execution and selected result still pending.

Windows PowerShell 5.1 monitor correction: the first monitor read valid diagnostics but reported `Command failed ()` because the process object did not retain its exit handle. Stopped only the local monitor (platform job left running), cached the process handle before waiting, then tested in the actual Windows PowerShell 5.1 runtime including a real diagnostics call.

Exactly as run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'C:\Users\sansri\.copilot\session-state\17bb335a-9ca3-491f-a6d8-8f61cd8edd1e\files\test-stage3-runner.ps1' 2>&1 | Tee-Object docs\evidence\stage-3\safeguard-tests.txt; if ($LASTEXITCODE -ne 0) { throw 'Windows PowerShell safeguard tests failed' }
```

Verbatim output:

```text
PASS under Windows PowerShell 5.1: successful output, exit 7 propagation, one-second process-tree timeout, real CLI diagnostics.
```

Resumed attached monitor `stage3-probe-fixed` without resubmitting. Reduced adoption budget to 65 minutes to account for the elapsed time:

```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $map=Get-Content stages\stage-3\sample-map.json -Raw | ConvertFrom-Json; $probe=($map | Where-Object {$_.claim -eq 'C-2026-04101'}).id; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\eval-batches.ps1 -Env $e -Samples '' -OutDir docs\evidence\stage-3\probe -Strategy BestOfN -BestOfN 4 -TimeoutMin 65 -MaxAttempts 1 -AdoptJob 44945388-1e87-41b5-adfd-32123fe29268 -AdoptSamples "04101=$probe"
```

### Probe completed; full arms started

Verbatim monitor output:

```text
09:03:05 adopting job 44945388-1e87-41b5-adfd-32123fe29268 for 04101
09:55:35 04101 Succeeded after 53 min
09:56:25 04101 done (job 44945388-1e87-41b5-adfd-32123fe29268): 1/1 finished; DB snapshot saved and reset
09:56:25 ALL DONE
```

Exactly as run:

```powershell
.\.venv\Scripts\python.exe scripts\score_ground_truth.py docs\evidence\stage-3\probe\results-04101.json --out stages\stage-3\probe --label 'Stage 3 BestOfN capability probe' 2>&1 | Tee-Object docs\evidence\stage-3\probe\score-output.txt
```

Full outputs: [raw result](stage-3/probe/results-04101.json), [score](stage-3/probe/score-output.txt), [reset](stage-3/probe/db-reset-04101.txt). Correct 1/1, mean rubric 0.900. Service result records `harnessStrategyType: BestOfN`, `harnessStrategyBody: {"n": 4}`. Only one selected execution is returned; no four candidate answer set. Billing reports 2,387,451 total tokens (including cache-accounting fields separately) and 40 tool invocations; these do not independently prove a candidate count.

Dead end, exactly as run:

```powershell
$r=Get-Content docs\evidence\stage-3\probe\results-04101.json -Raw | ConvertFrom-Json; $id=$r.Submissions[0].Execution.Id; frontier-tuning --output json executions diagnostics $id --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Out-File docs\evidence\stage-3\probe\execution-diagnostics.json -Encoding utf8
```

[Verbatim error](stage-3/probe/execution-diagnostics.json): API 404 / ER99000. Do not claim independently verified rollout count or “correct in any of N”. Compare the service-labelled selected result with fresh Simple.

Full comparison launched as attached async shell `stage3-full`, exactly as run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File stages\stage-3\run.ps1
```

Pinned orchestration: [run.ps1](../../stages/stage-3/run.ps1). Simple then BestOfN; same 29 sample IDs, model and skill; batch size 5; N=4; timeout 75/180 minutes per job respectively; stall threshold 30 minutes; at most two runner attempts. Probe does not contribute to either full-arm score. Stop on SQL/reset/submission errors or exhausted claims; no silent fallback strategy. Stage remains in progress.

### Removing redundant fresh Simple

User challenged repeating the already-measured stage 1 configuration at 10:06 IST. Recommended reusing stage 1's existing matched-29 Simple baseline. The clarification tool returned user unavailable and instructed a pragmatic choice; selected the recommended time-saving approach. Historical comparison caveat retained: dates, safeguards and retry budgets differ; do not attribute all movement solely to strategy.

Stopped attached shell `stage3-full` (local orchestration), then exactly as run:

```powershell
frontier-tuning evaluate cancel 008103c3-727c-4d2e-97dc-9630a8754c67 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object docs\evidence\stage-3\simple\cancel-output.txt; if ($LASTEXITCODE -ne 0) { throw 'Cancel failed' }; frontier-tuning --output json evaluate status 008103c3-727c-4d2e-97dc-9630a8754c67 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object docs\evidence\stage-3\simple\cancel-status.json
```

Full outputs: [cancellation](stage-3/simple/cancel-output.txt), [terminal status](stage-3/simple/cancel-status.json). Job `Cancelled`, `isTerminal: true`; cancelled Simple is excluded from metrics.

Exactly as run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql 2>&1 | Tee-Object docs\evidence\stage-3\simple\cancel-db-snapshot.txt; if ($LASTEXITCODE -ne 0) { throw 'Snapshot failed' }; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-reset-actions.sql 2>&1 | Tee-Object docs\evidence\stage-3\simple\cancel-db-reset.txt; if ($LASTEXITCODE -ne 0) { throw 'Reset failed' }; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-baseline.sql 2>&1 | Tee-Object docs\evidence\stage-3\simple\cancel-db-baseline.txt; if ($LASTEXITCODE -ne 0) { throw 'Baseline failed' }; git --no-pager diff --check
```

Full outputs: [snapshot](stage-3/simple/cancel-db-snapshot.txt), [reset](stage-3/simple/cancel-db-reset.txt), [baseline](stage-3/simple/cancel-db-baseline.txt). No action rows; reset and baseline both 0 0 0 0. Whitespace check passed with existing LF→CRLF warnings.

Changed pinned [run.ps1](../../stages/stage-3/run.ps1) to BestOfN only, then launched attached async shell `stage3-bestofn`, exactly as run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File stages\stage-3\run.ps1
```

Existing stage 1 merged answers supply the Simple comparator; omit 04130 → 0.637 · 22/29. No fresh Simple measurement will be reported. No RFT started.

### BestOfN stopped at user's request

At 10:21 IST user requested cancelling if no full-batch result and proceeding toward tuning. Checked diagnostics: five claims not started, zero completed/graded; `HttpRequestException` at 10:19 IST, service retry scheduled in approximately five minutes. Earlier one-claim probe had completed; distinguished that from the full batch.

Stopped attached shell `stage3-bestofn`, then exactly as run:

```powershell
frontier-tuning --output json evaluate diagnostics 729ff2cd-5096-4f87-8026-638043f68019 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Out-File docs\evidence\stage-3\bestofn\diagnostics-before-cancel.json -Encoding utf8; frontier-tuning evaluate cancel 729ff2cd-5096-4f87-8026-638043f68019 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object docs\evidence\stage-3\bestofn\cancel-output.txt; if ($LASTEXITCODE -ne 0) { throw 'Cancellation failed' }; frontier-tuning --output json evaluate status 729ff2cd-5096-4f87-8026-638043f68019 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object docs\evidence\stage-3\bestofn\cancel-status.json
```

Full outputs: [diagnostics](stage-3/bestofn/diagnostics-before-cancel.json), [cancellation](stage-3/bestofn/cancel-output.txt), [terminal status](stage-3/bestofn/cancel-status.json). Verified `Cancelled`, `isTerminal: true`.

Exactly as run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql 2>&1 | Tee-Object docs\evidence\stage-3\bestofn\cancel-db-snapshot.txt; if ($LASTEXITCODE -ne 0) { throw 'Snapshot failed' }; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-reset-actions.sql 2>&1 | Tee-Object docs\evidence\stage-3\bestofn\cancel-db-reset.txt; if ($LASTEXITCODE -ne 0) { throw 'Reset failed' }; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-baseline.sql 2>&1 | Tee-Object docs\evidence\stage-3\bestofn\cancel-db-baseline.txt; if ($LASTEXITCODE -ne 0) { throw 'Baseline failed' }
```

Full outputs: [snapshot](stage-3/bestofn/cancel-db-snapshot.txt), [reset](stage-3/bestofn/cancel-db-reset.txt), [baseline](stage-3/bestofn/cancel-db-baseline.txt). No action rows; baseline 0 0 0 0.

Stage 3 headroom unmeasured, not near-zero and not passed. No further batches or tuning submitted. Explicit exception to the repository's headroom-before-tuning rule requested before any pilot tuning submission.

## Commit preparation: lossless capture consolidation

User approved consolidation and a commit at 10:36 IST, followed by stage 4 tuning
preflight. Git initially contained 204 untracked files and seven modified files;
nothing was staged. Consolidated only the 122 untracked
`command-<id>.stdout.txt` / `.stderr.txt` captures. Kept failed attempts, raw
results, named diagnostics, run logs and database snapshots unchanged.

Exactly as run:

```powershell
& 'C:\Users\sansri\.copilot\session-state\5a4c8306-33b0-40a6-bf84-8b4dc8a5382d\files\consolidate-captures.ps1'
```

The exact helper was subsequently moved to
[consolidate-captures.ps1](stage-3/consolidate-captures.ps1) for the audit record.
It refuses tracked captures or existing archives, verifies each ZIP entry
against the original byte length and SHA-256, then removes only the verified
loose copies. Empty stderr entries are preserved.

Verbatim output:

```text
PASS probe : 88 captures archived; every original byte verified with SHA-256
PASS simple : 14 captures archived; every original byte verified with SHA-256
PASS bestofn : 20 captures archived; every original byte verified with SHA-256
```

See [evidence index](README.md#command-captures) for extraction instructions.
No blanket ignore rule added; no measurement or configuration changed.

Validation, exactly as run:

```powershell
& .\.venv\Scripts\python.exe scripts\test_score_ground_truth.py; if ($LASTEXITCODE -ne 0) { throw 'Scorer tests failed' }; & .\.venv\Scripts\python.exe scripts\check-skill.py stages\stage-3\warranty-assistant.md stages\stage-3\warranty-assistant.rubrics.json; if ($LASTEXITCODE -ne 0) { throw 'Skill leakage check failed' }; $targets = @('scripts\eval-batches.ps1','scripts\sql-run.ps1','stages\stage-3\run.ps1'); foreach ($file in $targets) { $tokens=$null; $errors=$null; [void][System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PWD $file),[ref]$tokens,[ref]$errors); if ($errors.Count) { throw ($errors | Out-String) }; "PASS PowerShell parse: $file" }
```

Output *(trimmed: individual PASS lines omitted)*:

```text
53/53 checks passed.
OK: no rubric phrases, no claim-specific answers
PASS PowerShell parse: scripts\eval-batches.ps1
PASS PowerShell parse: scripts\sql-run.ps1
PASS PowerShell parse: stages\stage-3\run.ps1
```

Editor diagnostics: no errors in the two runner scripts, `check-skill.py` or
stage 3's `run.ps1`. VS Code test discovery returned no tests; the repository's
standalone scorer test script above passed.

Dead end: broad JSON validation encountered `stage-2/refine-start.json`, which is
a verbatim text CLI response despite its extension; preserve it as evidence,
not rewrite it into invented JSON. Configuration JSON is validated separately.

The Foundry skill's mandatory dependency bootstrap again failed to install
`microsoft.foundry` because azd 1.25.1 has no compatible extension. No upgrade
performed; Foundry workflow not used. This world uses Frontier Tuning 0.3.16.
Read-only `tune start --help` states that the service determines the sample
selection; it does not resolve the Training/Evaluation question. No tuning
submission made during commit preparation.

### Runner regression checks

Exactly as run (extracted only `InvokeBounded`; no evaluation job or SQL call):

```powershell
$ErrorActionPreference='Stop'
$tokens=$null; $errors=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PWD 'scripts\eval-batches.ps1'),[ref]$tokens,[ref]$errors)
$fn=$ast.Find({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'InvokeBounded' },$true)
Invoke-Expression $fn.Extent.Text
$OutDir=Join-Path 'C:\Users\sansri\.copilot\session-state\5a4c8306-33b0-40a6-bf84-8b4dc8a5382d\files' ('runner-check-'+[guid]::NewGuid().ToString('N'))
$null=New-Item -ItemType Directory -Path $OutDir
try {
  $result=InvokeBounded 'powershell.exe' @('-NoProfile','-Command','Write-Output runner-ok; exit 0') 60
  if ($result.Trim() -ne 'runner-ok') { throw 'Success output mismatch' }
  'PASS InvokeBounded success/output'
  $failed=$false
  try { $null=InvokeBounded 'powershell.exe' @('-NoProfile','-Command','Write-Output expected-failure; exit 7') 60 } catch { if ($_.Exception.Message -notmatch 'Command failed \(7\)' -or $_.Exception.Message -notmatch 'expected-failure') { throw }; $failed=$true }
  if (-not $failed) { throw 'Nonzero exit was ignored' }
  'PASS InvokeBounded nonzero exit/output'
  $timedOut=$false
  try { $null=InvokeBounded 'powershell.exe' @('-NoProfile','-Command','Start-Sleep 15') 1 } catch { if ($_.Exception.Message -notmatch 'Command exceeded 1s') { throw }; $timedOut=$true }
  if (-not $timedOut) { throw 'Timeout was ignored' }
  'PASS InvokeBounded timeout'
} finally {
  Get-ChildItem -LiteralPath $OutDir -File | ForEach-Object { Remove-Item -LiteralPath $_.FullName }
  Remove-Item -LiteralPath $OutDir
}
```

Verbatim output:

```text
PASS InvokeBounded success/output
PASS InvokeBounded nonzero exit/output
PASS InvokeBounded timeout
```

Additional local checks: eight stage 2/3 root configuration/result JSON files
parsed; all 122 ZIP entries reverified against manifests; `git diff --check`
passed (existing LF-to-CRLF warnings only). Local credential-pattern check
found no matches in new loose files; this narrow scan is not a security audit.

Commit gate: full staged `git diff --cached --check` flagged whitespace in
verbatim SQL/CLI captures (PowerShell table padding and terminal blank lines).
Preserved those bytes rather than "fix" evidence. Authored files passed:

```powershell
git --no-pager diff --cached --check -- scripts stages docs\JOURNEY.md docs\evidence\README.md docs\evidence\journey-record-2026-10-07.md docs\evidence\journey-record-2026-10-09.md docs\evidence\stage-3\consolidate-captures.ps1; if ($LASTEXITCODE -ne 0) { throw 'Authored file whitespace check failed' }; "Staged files: $(@(git diff --cached --name-only).Count)"; git --no-pager diff --cached --stat | Select-Object -Last 3
```

Verbatim output:

```text
Staged files: 96
 stages/stage-3/warranty-assistant.md               |   32 +
 stages/stage-3/warranty-assistant.rubrics.json     |  128 +
 96 files changed, 32147 insertions(+), 27 deletions(-)
```

Local credential-pattern check also found no matches inside any of the 122
archived captures. Existing raw results and logs are synthetic scenario
evidence, not customer data.

## Stage 4: approved exploratory pilot

User explicitly selected **"Approve exploratory tuning pilot without measured
headroom"**. Stage 3 is not passed. Read the user-provided orbit playbook: rubrics
are reward functions, tuning is whole-world, at least 11 usable training prompts
are required, and completion can take days. Those are upstream guidance, not
tenant measurements. No separate grader code was created.

User upgraded Frontier Tuning; verified `frontier-tuning --version` returns
`0.3.17 (2026-10-03)`. `tune start --help` still says the service determines sample
selection and training. Epoch override omitted (server default).

Preflight reads:

```powershell
frontier-tuning --output json models list --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
frontier-tuning --output json samples get 0187ef5c-8464-4f62-a24c-e6d286ee97e0 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
frontier-tuning --output json skills get cf00d339-5217-4cd1-b390-cc0d911735da --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-baseline.sql
```

Full CLI JSON in [stage-4/](stage-4/). Live inventory was read before upgrade:
60 Training + 30 Evaluation. Base `mai-code-1-flash` is in `FTBaseModels` after
upgrade. Live skill enabled; instructions match restored stage 1 pin after CRLF
normalization; all six live skill rubric scoring definitions match.

SQL verbatim output:

```text
drafts evidence_requests escalations claims_not_seeded
------ ----------------- ----------- -----------------
     0                 0           0                 0



OK: 1 batch(es) executed
```

Reward-check dead end: exact comparison with authored JSON failed because the
Training sample DTO omits descriptions and scoring direction. Investigated
against the **measured stage 1 sample payload**: same IDs, checklist items,
category, scale, scoring criteria, red flags, method, importance and source for
all six rubrics. The baseline also omits descriptions and has null direction.
No live/sample edit made. Only Training sample 04104 individually inspected.
Pinned input copies and live snapshots retained for replay.

### Submission and reconciliation

Exactly as run:

```powershell
$ErrorActionPreference='Stop'; frontier-tuning --output json tune start --base-model mai-code-1-flash --new-model contoso-warranty-v3-stage4-pilot-20261009 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object -FilePath docs\evidence\stage-4\tune-start.json; if ($LASTEXITCODE -ne 0) { throw 'Tuning submission failed; do not retry without inspecting evidence and reconciling jobs' }
```

Full verbatim CLI output: [tune-start.json](stage-4/tune-start.json). `ReadTimeout`,
submission outcome unknown. **Did not retry or cancel.**

Exactly as run:

```powershell
frontier-tuning --output json tune list --limit 5 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object -FilePath docs\evidence\stage-4\tune-list-after-timeout.json; if ($LASTEXITCODE -ne 0) { throw 'Tuning reconciliation read failed; submission outcome still unknown' }
```

[Full reconciliation](stage-4/tune-list-after-timeout.json) returned one matching
job, `c77feaed-96de-4b88-9802-e0f265601eb8`, created 05:29:38 UTC / 10:59:38 IST.
`JobTaskType: SampleBasedFineTuning`, `Status: Running`; snapshot one skill,
three tools, **90 prompts**, four knowledge sources. Capture counts do not
identify the backend training subset. `FinetuningType` is null; do not infer
the specific training algorithm from that payload.

Exactly as run (independent read-only calls):

```powershell
frontier-tuning --output json tune status c77feaed-96de-4b88-9802-e0f265601eb8 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object -FilePath docs\evidence\stage-4\tune-status.json; if ($LASTEXITCODE -ne 0) { throw 'Tuning status read failed' }
frontier-tuning --output json tune diagnostics c77feaed-96de-4b88-9802-e0f265601eb8 --include-metrics --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1 | Tee-Object -FilePath docs\evidence\stage-4\tune-diagnostics.json; if ($LASTEXITCODE -ne 0) { throw 'Tuning diagnostics read failed' }
```

[Status](stage-4/tune-status.json): training and deployment `NotStarted`,
`readyForEvaluation: false`, `isTerminal: false`. Diagnostics verbatim:

```json
{
  "jobId": "c77feaed-96de-4b88-9802-e0f265601eb8",
  "state": "NotAvailable",
  "status": "Running"
}
```

No background local polling process left running. No database reset during the
active tuning job. No training metrics, tuned-model readiness or gain claimed.

## Stage 4 status check after 11:14 IST

User requested current status. Exactly as run:

```powershell
frontier-tuning --output json tune status c77feaed-96de-4b88-9802-e0f265601eb8 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
```

Exit code 0. Full verbatim output: [status response](stage-4/tune-status-training-in-progress.json).
ModelTraining changed from NotStarted to InProgress; deployment remains
NotStarted, no stage errors, readyForEvaluation false. No database changes.

## Stage 4 status check after 11:36 IST

Exactly as run:

```powershell
frontier-tuning --output json tune status c77feaed-96de-4b88-9802-e0f265601eb8 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
```

Exit code 0. Full output identical to the [previous saved response](stage-4/tune-status-training-in-progress.json):
Running, ModelTraining InProgress, ModelDeployment NotStarted, no errors,
readyForEvaluation false. No progress percentage or ETA returned. No database changes.
