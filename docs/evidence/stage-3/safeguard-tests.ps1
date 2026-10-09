$ErrorActionPreference = 'Stop'
$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PWD 'scripts\eval-batches.ps1'), [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw ($errors | Out-String) }
$OutDir = Join-Path $env:TEMP ('runner-test-' + [guid]::NewGuid())
New-Item -ItemType Directory $OutDir | Out-Null
$ast.FindAll({ param($a) $a -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false) | ForEach-Object { Invoke-Expression $_.Extent.Text }
try {
  $r = InvokeBounded powershell.exe @('-NoProfile', '-Command', 'Write-Output verified; exit 0') 60
  if ($r.Trim() -ne 'verified') { throw 'Output mismatch' }
  $failed = $false
  try { InvokeBounded powershell.exe @('-NoProfile', '-Command', 'exit 7') 60 } catch { $failed = $_.Exception.Message -match 'Command failed \(7\)' }
  if (-not $failed) { throw 'Nonzero exit not surfaced' }
  $watch = [Diagnostics.Stopwatch]::StartNew()
  $failed = $false
  try { InvokeBounded powershell.exe @('-NoProfile', '-Command', 'Start-Sleep 30') 1 } catch { $failed = $_.Exception.Message -match 'exceeded 1s' }
  if (-not $failed -or $watch.Elapsed.TotalSeconds -gt 15) { throw 'Timeout not enforced' }
  $d = JsonResult (InvokeBounded frontier-tuning @('--output', 'json', 'evaluate', 'diagnostics', '44945388-1e87-41b5-adfd-32123fe29268', '--env-id', '598fd1b0-36f1-402f-ba36-aa00c8a67cc4') 120)
  if ($d.evaluationId -ne '44945388-1e87-41b5-adfd-32123fe29268') { throw 'Diagnostics parse failed' }
  'PASS under Windows PowerShell 5.1: successful output, exit 7 propagation, one-second process-tree timeout, real CLI diagnostics.'
} finally {
  Get-ChildItem -LiteralPath $OutDir -File | Remove-Item
  Remove-Item -LiteralPath $OutDir
}
