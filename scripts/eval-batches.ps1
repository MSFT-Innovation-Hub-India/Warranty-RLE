param(
  [string]$Env,                    # environment id
  [string]$Samples,                # "label=sampleId,label=sampleId,..." run in this order
  [string]$OutDir,                 # where results go
  [string]$Model = 'dev-ct-mai-code-mp',
  [int]$BatchSize = 5,             # samples per evaluation job (each job pays ~9 min of platform start-up)
  [int]$StallMin = 15,             # no progress for this long while claims are still running = stalled
  [int]$TimeoutMin = 75,           # hard limit per job
  [int]$MaxAttempts = 3,           # a claim that stalls is requeued, up to this many attempts in all
  [string]$AdoptJob = '',          # optional: take over a job already running ...
  [string]$AdoptSamples = ''       # ... with these "label=sampleId" pairs
)
# Runs evaluation jobs in batches, one job at a time, and heals platform stalls:
# when a job makes no progress for -StallMin minutes, it is cancelled, the claims
# that finished are kept, and the unfinished ones go back on the queue.
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force $OutDir | Out-Null
$terminal = 'Succeeded','Completed','Failed','Cancelled','Canceled','PartiallySucceeded','Paused'
function Log($m) { $line = "$(Get-Date -Format HH:mm:ss) $m"; $line; Add-Content "$OutDir\run-log.txt" $line }
function Diag($job) {
  $o = frontier-tuning --output json evaluate diagnostics $job --env-id $Env 2>$null | Out-String
  try { $o.Substring($o.IndexOf('{')) | ConvertFrom-Json } catch { $null }
}
function Pairs($s) { @($s -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }) }

$queue = New-Object System.Collections.ArrayList
foreach ($p in (Pairs $Samples)) { [void]$queue.Add($p) }
$attempts = @{}

function RunJob($job, $batch) {
  $label = (($batch | ForEach-Object { ($_ -split '=', 2)[0] }) -join '+')
  $t0 = Get-Date; $lastDone = -1; $lastMove = Get-Date; $why = ''; $fails = 0
  while ($true) {
    Start-Sleep 60
    $d = Diag $job
    $mins = [int]((Get-Date) - $t0).TotalMinutes
    if (-not $d) {
      # the CLI failed (network, sign-in, a broken install): don't wait silently
      $fails = 1 + [int]$fails
      if ($fails -in 5, 15, 30) { Log "$label WARNING: cannot read job status ($fails polls in a row); check: frontier-tuning --version" }
      if ($mins -ge $TimeoutMin) { $why = "TIMEOUT at $mins min (status unreadable)"; break }
      continue
    }
    $fails = 0
    $done = [int]$d.progress.execution.completed + [int]$d.progress.execution.failed
    if ($done -ne $lastDone) { $lastDone = $done; $lastMove = Get-Date }
    $mins = [int]((Get-Date) - $t0).TotalMinutes
    $still = [int]$d.progress.execution.running + [int]$d.progress.execution.pending
    if ($d.status -in $terminal) { $why = $d.status; break }
    $idle = [int]((Get-Date) - $lastMove).TotalMinutes
    if ($done -gt 0 -and $still -gt 0 -and $idle -ge $StallMin) { $why = "STALLED ($still running, no progress for $idle min)"; break }
    if ($mins -ge $TimeoutMin) { $why = "TIMEOUT at $mins min"; break }
  }
  if ($why -notin $terminal) { Log "$label $why : cancelling"; frontier-tuning evaluate cancel $job --env-id $Env 2>&1 | Out-Null }
  else { Log "$label $why after $([int]((Get-Date) - $t0).TotalMinutes) min" }
  $r = frontier-tuning --output json evaluate results $job --samples --env-id $Env 2>$null | Out-String
  $finishedIds = @()
  if ($r.IndexOf('{') -ge 0) {
    $json = $r.Substring($r.IndexOf('{')); $json | Out-File "$OutDir\results-$label.json" -Encoding utf8
    $res = $json | ConvertFrom-Json
    $finishedIds = @($res.Submissions | Where-Object { $_.Execution -and $_.Execution.Status -in 'Completed','Failed' } | ForEach-Object { $_.PromptId })
  }
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql 2>&1 | Out-File "$OutDir\db-after-$label.txt" -Encoding utf8
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-reset-actions.sql 2>&1 | Out-Null
  $requeue = @($batch | Where-Object { $finishedIds -notcontains ($_ -split '=', 2)[1] })
  foreach ($q in $requeue) {
    $attempts[$q] = 1 + [int]$attempts[$q]
    if ($attempts[$q] -lt $MaxAttempts) { [void]$queue.Add($q); Log "  requeued $(($q -split '=',2)[0]) (attempt $($attempts[$q] + 1) of $MaxAttempts next)" }
    else { Log "  GAVE UP on $(($q -split '=',2)[0]) after $MaxAttempts attempts" }
  }
  Log "$label done (job $job): $($batch.Count - $requeue.Count)/$($batch.Count) finished; DB snapshot saved and reset"
}

if ($AdoptJob) {
  $b = Pairs $AdoptSamples
  foreach ($q in $b) { $attempts[$q] = 0 }
  Log "adopting job $AdoptJob for $((($b | ForEach-Object { ($_ -split '=',2)[0] }) -join '+'))"
  RunJob $AdoptJob $b
}

while ($queue.Count -gt 0) {
  $n = [Math]::Min($BatchSize, $queue.Count)
  $batch = @($queue.GetRange(0, $n)); $queue.RemoveRange(0, $n)
  foreach ($q in $batch) { if (-not $attempts.ContainsKey($q)) { $attempts[$q] = 0 } }
  $label = (($batch | ForEach-Object { ($_ -split '=', 2)[0] }) -join '+')
  $sidArgs = @(); foreach ($q in $batch) { $sidArgs += '--sample-id'; $sidArgs += ($q -split '=', 2)[1] }
  $o = frontier-tuning --output json evaluate start @sidArgs --base-model $Model --strategy simple --env-id $Env 2>&1 | Out-String
  $job = [regex]::Match($o, '"JobId":\s*"([0-9a-f-]{36})"').Groups[1].Value
  if (-not $job) { Log "$label START FAILED: $($o.Trim())"; continue }
  Log "$label job $job started"
  RunJob $job $batch
}
Log "ALL DONE"
