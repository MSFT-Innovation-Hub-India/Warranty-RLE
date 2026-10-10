$ErrorActionPreference = 'Stop'
$e = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
$map = Get-Content stages\stage-3\sample-map.json -Raw | ConvertFrom-Json
$pairs = ($map | Where-Object { $_.claim -ne 'C-2026-04130' } | ForEach-Object { "$($_.claim.Substring(7))=$($_.id)" }) -join ','
if (@($map | Where-Object { $_.claim -ne 'C-2026-04130' }).Count -ne 29) { throw 'Expected exactly 29 claims' }
foreach ($strategy in @('BestOfN')) {
  $dir = "docs\evidence\stage-3\$($strategy.ToLower())"
  $budget = if ($strategy -eq 'Simple') { 75 } else { 180 }
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\eval-batches.ps1 -Env $e -Samples $pairs -OutDir $dir -Strategy $strategy -BestOfN 4 -BatchSize 5 -TimeoutMin $budget -StallMin 30 -MaxAttempts 2
  if ($LASTEXITCODE -ne 0) { throw "$strategy run incomplete; stopping the experiment. Reconcile jobs before resuming." }
  & .\.venv\Scripts\python.exe scripts\summarise-stage.py $dir "stages\stage-3\$($strategy.ToLower())"
  if ($LASTEXITCODE -ne 0) { throw "$strategy summarisation failed" }
}
