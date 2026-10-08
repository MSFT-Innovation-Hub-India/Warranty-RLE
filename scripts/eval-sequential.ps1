param(
  [string]$Env,                 # environment id
  [string]$Samples,             # "label=sampleId,label=sampleId,..." run in this order
  [string]$OutDir,              # where results go
  [string]$Model = 'dev-ct-mai-code-mp',
  [int]$TimeoutMin = 40,
  [string]$WaitForJob = '',     # optional: a job that must be terminal before starting
  [int]$BatchSize = 1           # samples per evaluation job (each job pays ~9 min of platform start-up)
)
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force $OutDir | Out-Null
$terminal = 'Succeeded','Completed','Failed','Cancelled','Canceled','PartiallySucceeded','Paused'
function Status($job) { $o = frontier-tuning --output json evaluate status $job --env-id $Env 2>$null | Out-String; [regex]::Match($o,'"Status":\s*"([^"]+)"').Groups[1].Value }
function Log($m) { $line = "$(Get-Date -Format HH:mm:ss) $m"; $line; Add-Content "$OutDir\run-log.txt" $line }

if ($WaitForJob) { for ($i=0; $i -lt 30; $i++) { $s = Status $WaitForJob; Log "waiting for $WaitForJob : $s"; if ($s -in $terminal) { break }; Start-Sleep 30 } }

$pairs = @($Samples -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
for ($k = 0; $k -lt $pairs.Count; $k += $BatchSize) {
  $batch = $pairs[$k..([Math]::Min($k + $BatchSize, $pairs.Count) - 1)]
  $label = (($batch | ForEach-Object { ($_ -split '=', 2)[0] }) -join '+')
  $sidArgs = @(); foreach ($b in $batch) { $sidArgs += '--sample-id'; $sidArgs += ($b -split '=', 2)[1] }
  $o = frontier-tuning --output json evaluate start @sidArgs --base-model $Model --strategy simple --env-id $Env 2>&1 | Out-String
  $job = [regex]::Match($o,'"JobId":\s*"([0-9a-f-]{36})"').Groups[1].Value
  if (-not $job) { Log "$label START FAILED: $($o.Trim())"; continue }
  Log "$label job $job started"
  $t0 = Get-Date; $s = ''
  while ($true) {
    Start-Sleep 60; $s = Status $job
    $mins = [int]((Get-Date) - $t0).TotalMinutes
    if ($s -in $terminal) { Log "$label $s after $mins min"; break }
    if ($mins -ge $TimeoutMin) { Log "$label TIMEOUT at $mins min ($s): cancelling"; frontier-tuning evaluate cancel $job --env-id $Env 2>&1 | Out-Null; $s = 'TimedOut'; break }
  }
  $r = frontier-tuning --output json evaluate results $job --samples --env-id $Env 2>$null | Out-String
  if ($r.IndexOf('{') -ge 0) { $r.Substring($r.IndexOf('{')) | Out-File "$OutDir\results-$label.json" -Encoding utf8 }
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql 2>&1 | Out-File "$OutDir\db-after-$label.txt" -Encoding utf8
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-reset-actions.sql 2>&1 | Out-Null
  Log "$label done (job $job, $s); DB snapshot saved and reset"
}
Log "ALL DONE"
