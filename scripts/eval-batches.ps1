param(
  [string]$Env,                    # environment id
  [string]$Samples,                # "label=sampleId,label=sampleId,..." run in this order
  [string]$OutDir,                 # where results go
  [string]$Model = 'dev-ct-mai-code-mp',
  [int]$BatchSize = 5,             # samples per evaluation job (each job pays ~9 min of platform start-up)
  [int]$StallMin = 15,             # no progress for this long while claims are still running = stalled
  [int]$TimeoutMin = 75,           # hard limit per job
  [int]$MaxAttempts = 3,           # a claim that stalls is requeued, up to this many attempts in all
  [ValidateSet('Simple','BestOfN')][string]$Strategy = 'Simple',
  [ValidateRange(1,16)][int]$BestOfN = 4,
  [string]$AdoptJob = '',          # optional: take over a job already running ...
  [string]$AdoptSamples = ''       # ... with these "label=sampleId" pairs
)
# Runs evaluation jobs in batches, one job at a time, and heals platform stalls:
# when a job makes no progress for -StallMin minutes, it is cancelled, the claims
# that finished are kept, and the unfinished ones go back on the queue.
$ErrorActionPreference = 'Stop'
if ($BatchSize -lt 1 -or $TimeoutMin -lt 1 -or $StallMin -lt 1 -or $MaxAttempts -lt 1) { throw 'Batch size, time limits and attempts must be positive.' }
New-Item -ItemType Directory -Force $OutDir | Out-Null
$terminal = 'Succeeded','Completed','Failed','Cancelled','Canceled','PartiallySucceeded','Paused'
function Log($m) { $line = "$(Get-Date -Format HH:mm:ss) $m"; $line; Add-Content "$OutDir\run-log.txt" $line }
function InvokeBounded([string]$Command, [string[]]$Arguments, [int]$Seconds = 120) {
  $id = [guid]::NewGuid().ToString('N')
  $stdout = Join-Path ([IO.Path]::GetFullPath($OutDir)) "command-$id.stdout.txt"
  $stderr = Join-Path ([IO.Path]::GetFullPath($OutDir)) "command-$id.stderr.txt"
  $quoted = @($Command) + $Arguments | ForEach-Object { "'" + $_.Replace("'", "''") + "'" }
  $script = '& ' + ($quoted -join ' ') + '; exit $LASTEXITCODE'
  $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
  $p = Start-Process powershell.exe -ArgumentList '-NoProfile','-EncodedCommand',$encoded -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
  $null = $p.Handle
  try {
    if (-not $p.WaitForExit($Seconds * 1000)) {
      & taskkill.exe /PID $p.Id /T /F | Out-Null
      throw "Command exceeded ${Seconds}s: $Command $($Arguments -join ' '). Submission outcome may be unknown; reconcile before retrying."
    }
    $p.WaitForExit()
    $text = (Get-Content -LiteralPath $stdout -Raw) + (Get-Content -LiteralPath $stderr -Raw)
    if ($p.ExitCode -ne 0) { throw "Command failed ($($p.ExitCode)): $Command $($Arguments -join ' ')`n$text" }
    return $text
  } finally {
    $p.Dispose()
  }
}
function JsonResult($text) {
  $start = $text.IndexOf('{')
  if ($start -lt 0) { throw "No JSON in CLI output: $text" }
  $text.Substring($start) | ConvertFrom-Json
}
function CleanBaseline {
  $query = "IF EXISTS (SELECT 1 FROM ClaimAdjudicationDraft) OR EXISTS (SELECT 1 FROM EvidenceRequest) OR EXISTS (SELECT 1 FROM GoodwillEscalation) OR EXISTS (SELECT 1 FROM Claims WHERE status <> CASE WHEN claim_id LIKE 'C-2026-03%' THEN 'Paid' ELSE 'Submitted' END) THROW 51000, 'Database baseline is not clean', 1;"
  InvokeBounded 'powershell.exe' @('-NoProfile','-ExecutionPolicy','Bypass','-File','scripts\sql-run.ps1','-Query',$query) 480 | Out-Null
}
function Pairs($s) { @($s -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }) }

$queue = New-Object System.Collections.ArrayList
foreach ($p in (Pairs $Samples)) { [void]$queue.Add($p) }
$attempts = @{}
$exhausted = New-Object System.Collections.ArrayList

function RunJob($job, $batch) {
  $label = (($batch | ForEach-Object { ($_ -split '=', 2)[0] }) -join '+')
  $t0 = Get-Date; $lastDone = -1; $lastMove = Get-Date; $why = ''; $fails = 0
  while ($true) {
    Start-Sleep 60
    $remaining = [int](($t0.AddMinutes($TimeoutMin) - (Get-Date)).TotalSeconds)
    if ($remaining -le 0) { $why = "TIMEOUT at $TimeoutMin min"; break }
    $d = $null
    try {
      $d = JsonResult (InvokeBounded 'frontier-tuning' @('--output','json','evaluate','diagnostics',$job,'--env-id',$Env) ([Math]::Min(120,$remaining)))
    } catch { Log "$label WARNING: $($_.Exception.Message)" }
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
  if ($why -notin $terminal) {
    Log "$label $why : cancelling"
    InvokeBounded 'frontier-tuning' @('evaluate','cancel',$job,'--env-id',$Env) | Out-Null
    $state = JsonResult (InvokeBounded 'frontier-tuning' @('--output','json','evaluate','status',$job,'--env-id',$Env))
    if ($state.Status -notin $terminal) { throw "Cancellation not terminal for $job; stopping before database reset." }
  }
  else { Log "$label $why after $([int]((Get-Date) - $t0).TotalMinutes) min" }
  $r = InvokeBounded 'frontier-tuning' @('--output','json','evaluate','results',$job,'--samples','--env-id',$Env)
  $res = JsonResult $r
  if ($null -eq $res.Submissions) { throw "Results for $job have no Submissions collection; stopping before reset." }
  $r.Substring($r.IndexOf('{')) | Out-File "$OutDir\results-$label.json" -Encoding utf8
  $finishedIds = @($res.Submissions | Where-Object { $_.Execution -and $_.Execution.Status -in 'Completed','Failed' } | ForEach-Object { $_.PromptId })
  InvokeBounded 'powershell.exe' @('-NoProfile','-ExecutionPolicy','Bypass','-File','scripts\sql-run.ps1','-File','scripts\db-actions-snapshot.sql') 480 | Out-File "$OutDir\db-after-$label.txt" -Encoding utf8
  InvokeBounded 'powershell.exe' @('-NoProfile','-ExecutionPolicy','Bypass','-File','scripts\sql-run.ps1','-File','scripts\db-reset-actions.sql') 480 | Out-File "$OutDir\db-reset-$label.txt" -Encoding utf8
  CleanBaseline
  $requeue = @($batch | Where-Object { $finishedIds -notcontains ($_ -split '=', 2)[1] })
  foreach ($q in $requeue) {
    $attempts[$q] = 1 + [int]$attempts[$q]
    if ($attempts[$q] -lt $MaxAttempts) { [void]$queue.Add($q); Log "  requeued $(($q -split '=',2)[0]) (attempt $($attempts[$q] + 1) of $MaxAttempts next)" }
    else { [void]$exhausted.Add($q); Log "  GAVE UP on $(($q -split '=',2)[0]) after $MaxAttempts attempts" }
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
  CleanBaseline
  $n = [Math]::Min($BatchSize, $queue.Count)
  $batch = @($queue.GetRange(0, $n)); $queue.RemoveRange(0, $n)
  foreach ($q in $batch) { if (-not $attempts.ContainsKey($q)) { $attempts[$q] = 0 } }
  $label = (($batch | ForEach-Object { ($_ -split '=', 2)[0] }) -join '+')
  $sidArgs = @(); foreach ($q in $batch) { $sidArgs += '--sample-id'; $sidArgs += ($q -split '=', 2)[1] }
  $startArgs = @('--output','json','evaluate','start') + $sidArgs + @('--base-model',$Model,'--strategy',$Strategy,'--env-id',$Env)
  if ($Strategy -eq 'BestOfN') { $startArgs += @('--best-of-n',"$BestOfN") }
  $o = InvokeBounded 'frontier-tuning' $startArgs
  $job = [regex]::Match($o, '"JobId":\s*"([0-9a-f-]{36})"').Groups[1].Value
  if (-not $job) { throw "$label START outcome unknown: $($o.Trim()); reconcile before retrying." }
  Log "$label job $job started"
  RunJob $job $batch
}
if ($exhausted.Count) { throw "Run incomplete: $($exhausted.Count) claims exhausted their attempts. See run-log.txt; do not report ALL DONE." }
Log "ALL DONE"
