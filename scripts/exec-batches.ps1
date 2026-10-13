param(
  [string]$Env,                    # environment id
  [string]$SamplesFile,            # JSONL with one {"Prompt": "Adjudicate claim C-…"} per line (config/eval-samples.jsonl)
  [string]$Only = '',              # optional: comma-separated claim numbers to run, e.g. '04101,04102'; default all, file order
  [string]$OutDir,                 # where results go
  [string]$Model,                  # model ID from `models list`, e.g. 00000000-0000-0000-8000-100000000004
  [int]$Parallel = 5,              # claims run at the same time (one batch); the database is reset after each batch
  [int]$TimeoutMin = 60            # hard limit per claim
)
# Runs claims one execution each (`executions run --strategy simple --wait`), a batch at a
# time, instead of as evaluation jobs. `Simple` grades the answer against the skill's rubrics,
# like an evaluation. Used since 2026-10-13, when MAI-CODE-5b's claim-system calls failed
# inside evaluation jobs but worked in executions (docs/06 P11).
# Each result is saved as {label, prompt, model, startedUtc, endedUtc, execution}, which
# score_ground_truth.py and summarise-stage.py read. Nothing is ever resubmitted: a claim that
# fails or times out is reported, and a timeout stops the run before the database is reset.
$ErrorActionPreference = 'Stop'
if (-not $Env -or -not $SamplesFile -or -not $OutDir -or -not $Model) { throw 'Env, SamplesFile, OutDir and Model are required.' }
if ($Parallel -lt 1 -or $TimeoutMin -lt 1) { throw 'Parallel and TimeoutMin must be positive.' }
New-Item -ItemType Directory -Force $OutDir | Out-Null
$OutDir = [IO.Path]::GetFullPath($OutDir)
function Log($m) {
  $line = "$(Get-Date -Format HH:mm:ss) $m"; $line
  for ($i = 1; $i -le 5; $i++) {
    try { Add-Content "$OutDir\run-log.txt" $line -ErrorAction Stop; return } catch { Start-Sleep -Milliseconds (200 * $i) }
  }
  Write-Warning "could not write run-log.txt: $line"
}
function Sql([string[]]$a, [string]$outFile) {
  $o = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 @a 2>&1 | Out-String
  if ($outFile) { $o | Out-File $outFile -Encoding utf8 }
  if ($LASTEXITCODE -ne 0) { throw "SQL step failed ($($a -join ' ')): $o" }
  $o
}
function Short($s) { $s = ("$s" -replace '\s+', ' ').Trim(); if ($s.Length -gt 300) { $s.Substring(0, 300) + ' …' } else { $s } }
function CleanBaseline {
  $query = "IF EXISTS (SELECT 1 FROM ClaimAdjudicationDraft) OR EXISTS (SELECT 1 FROM EvidenceRequest) OR EXISTS (SELECT 1 FROM GoodwillEscalation) OR EXISTS (SELECT 1 FROM Claims WHERE status <> CASE WHEN claim_id LIKE 'C-2026-03%' THEN 'Paid' ELSE 'Submitted' END) THROW 51000, 'Database baseline is not clean', 1;"
  Sql @('-Query', $query) $null | Out-Null
}

# the claims, in file order
$items = @()
foreach ($line in Get-Content $SamplesFile) {
  if (-not $line.Trim()) { continue }
  $p = ($line | ConvertFrom-Json).Prompt
  $m = [regex]::Match($p, 'C-\d{4}-(\d{5})')
  if (-not $m.Success) { throw "No claim ID in prompt: $p" }
  $items += [pscustomobject]@{ Label = $m.Groups[1].Value; Prompt = $p }
}
if ($Only) {
  $want = @($Only -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
  $items = @($items | Where-Object { $want -contains $_.Label })
  if ($items.Count -ne $want.Count) { throw "Some of -Only were not found in $SamplesFile" }
}
Log "$($items.Count) claims, model $Model, $Parallel at a time"

$failed = New-Object System.Collections.ArrayList
for ($b = 0; $b -lt $items.Count; $b += $Parallel) {
  $batch = @($items[$b..([Math]::Min($b + $Parallel, $items.Count) - 1)])
  $label = ($batch.Label -join '+')
  CleanBaseline
  Log "$label started"
  $procs = @()
  foreach ($it in $batch) {
    $out = "$OutDir\cli-$($it.Label).stdout.txt"; $err = "$OutDir\cli-$($it.Label).stderr.txt"
    $cliArgs = @('-e', $Env, 'executions', 'run', '-q', $it.Prompt, '--model', $Model, '--strategy', 'simple', '--wait', '-o', 'json')
    $quoted = @('frontier-tuning') + $cliArgs | ForEach-Object { "'" + $_.Replace("'", "''") + "'" }
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes('& ' + ($quoted -join ' ') + '; exit $LASTEXITCODE'))
    $p = Start-Process powershell.exe -ArgumentList '-NoProfile', '-EncodedCommand', $encoded -PassThru -NoNewWindow -RedirectStandardOutput $out -RedirectStandardError $err
    $null = $p.Handle
    $procs += [pscustomobject]@{ Item = $it; Proc = $p; Out = $out; Err = $err; Start = (Get-Date).ToUniversalTime() }
  }
  $deadline = (Get-Date).AddMinutes($TimeoutMin)
  $timedOut = @()
  foreach ($x in $procs) {
    $ms = [Math]::Max(1000, [int]($deadline - (Get-Date)).TotalMilliseconds)
    if (-not $x.Proc.WaitForExit($ms)) {
      & taskkill.exe /PID $x.Proc.Id /T /F | Out-Null
      $timedOut += $x.Item.Label
      Log "  $($x.Item.Label) TIMEOUT after $TimeoutMin min: outcome unknown (check: frontier-tuning executions get <id>)"
      continue
    }
    $x.Proc.WaitForExit()
    $text = (Get-Content -LiteralPath $x.Out -Raw) + ''
    $i = $text.IndexOf('{')
    $ex = $null
    if ($i -ge 0) { try { $ex = $text.Substring($i) | ConvertFrom-Json } catch { } }
    # `--wait` gives up (exit 124) while the execution is still running: keep reading it by ID
    # until it ends, so the database is never reset under a running claim.
    while ($ex -and $ex.status -in 'Running', 'NotStarted', 'Pending' -and $ex.executionId) {
      if ((Get-Date) -ge $deadline) { break }
      Start-Sleep 30
      $g = & frontier-tuning -e $Env executions get $ex.executionId -o json 2>&1 | Out-String
      $j = $g.IndexOf('{')
      if ($j -ge 0) { try { $ex = $g.Substring($j) | ConvertFrom-Json } catch { } }
    }
    if ($ex -and $ex.status -in 'Running', 'NotStarted', 'Pending') {
      $timedOut += $x.Item.Label
      Log "  $($x.Item.Label) still $($ex.status) after $TimeoutMin min (execution $($ex.executionId)): outcome unknown"
      continue
    }
    if (-not $ex -or -not $ex.status) {
      [void]$failed.Add($x.Item.Label)
      Log "  $($x.Item.Label) FAILED (exit $($x.Proc.ExitCode)): $(Short ((Get-Content -LiteralPath $x.Err -Raw) + $text))"
      continue
    }
    $record = [ordered]@{ label = $x.Item.Label; prompt = $x.Item.Prompt; model = $Model; startedUtc = $x.Start.ToString('o'); endedUtc = (Get-Date).ToUniversalTime().ToString('o'); execution = $ex }
    $record | ConvertTo-Json -Depth 30 | Out-File "$OutDir\result-$($x.Item.Label).json" -Encoding utf8
    $tools = @($ex.toolExecutions)
    $claimSys = @($tools | Where-Object { $_.displayName -like '1c171__*' })
    $bad = @($tools | Where-Object { $_.status -ne 'Completed' })
    $scored = @($ex.rubricResults | Where-Object { $_.score -ne $null })
    $mean = if ($scored.Count) { '{0:N3}' -f (($scored | Measure-Object score -Average).Average) } else { 'n/a' }
    $mins = [int]((Get-Date).ToUniversalTime() - $x.Start).TotalMinutes
    Log "  $($x.Item.Label) $($ex.status) in $mins min: rubric $mean ($($scored.Count) graded), tools $($tools.Count) (claim system $($claimSys.Count), not completed $($bad.Count))"
    if ($ex.status -ne 'Completed') { [void]$failed.Add($x.Item.Label) }
  }
  if ($timedOut.Count) { throw "Stopped: $($timedOut -join ', ') timed out and may still be running; the database was NOT reset. Reconcile with executions get before going on." }
  Sql @('-File', 'scripts\db-actions-snapshot.sql') "$OutDir\db-after-$label.txt" | Out-Null
  Sql @('-File', 'scripts\db-reset-actions.sql') "$OutDir\db-reset-$label.txt" | Out-Null
  CleanBaseline
  Log "$label done: DB snapshot saved and reset"
}
if ($failed.Count) { Log "FINISHED WITH FAILURES: $($failed -join ', ') (not resubmitted)"; exit 1 }
Log "ALL DONE"
