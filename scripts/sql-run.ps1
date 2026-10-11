<#
.SYNOPSIS
  Run a SQL file (or a query) against the contoso-warranty Azure SQL database with your Entra sign-in.

.DESCRIPTION
  The server is Entra-only, so there are no SQL passwords. This gets an access token from the Azure CLI
  and runs the SQL through Windows PowerShell 5.1's built-in System.Data.SqlClient, so nothing needs
  installing. Files are split on GO lines. Every result set is printed.

.EXAMPLE
  .\scripts\sql-run.ps1 -File scripts\db-baseline.sql
  .\scripts\sql-run.ps1 -File scripts\db-actions-snapshot.sql
  .\scripts\sql-run.ps1 -File scripts\db-reset-actions.sql
  .\scripts\sql-run.ps1 -File world-builder\out\db\seed.azuresql.sql
#>
param(
  [string]$File,
  [string]$Query,
  [string]$Server = 'az-sqldb-common.database.windows.net',
  [string]$Database = 'contoso-warranty'
)

if (-not $File -and -not $Query) { throw 'Give -File or -Query.' }
$ErrorActionPreference = 'Stop'
$sql = if ($File) { [IO.File]::ReadAllText((Resolve-Path $File).Path) } else { $Query }
$token = az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv
if (-not $token) { throw 'No Azure CLI token. Run az login.' }

$inner = @'
param($Server, $Database, $Token, $SqlFile)
$ErrorActionPreference = 'Stop'
$sql = [IO.File]::ReadAllText($SqlFile, [Text.Encoding]::UTF8)
$cn = New-Object System.Data.SqlClient.SqlConnection("Server=tcp:$Server,1433;Database=$Database;Encrypt=True;TrustServerCertificate=False;Connection Timeout=90;")
$cn.AccessToken = $Token; $cn.Open()
$batches = [regex]::Split($sql, '(?im)^\s*GO\s*$') | Where-Object { $_.Trim() }
$i = 0
foreach ($b in $batches) {
  $i++; $cmd = $cn.CreateCommand(); $cmd.CommandText = $b; $cmd.CommandTimeout = 300
  try {
    $ds = New-Object Data.DataSet
    $da = New-Object System.Data.SqlClient.SqlDataAdapter $cmd
    [void]$da.Fill($ds)
    foreach ($t in $ds.Tables) {
      if ($t.Rows.Count -gt 0) { $t | Format-Table -AutoSize | Out-String -Width 4096 | Write-Output } else { Write-Output '(no rows)' }
    }
  } catch { Write-Output "FAILED batch $i : $($_.Exception.Message)"; $cn.Close(); exit 1 }
}
Write-Output "OK: $i batch(es) executed"
$cn.Close()
'@
$tmp = Join-Path $env:TEMP ("sql-run-" + [guid]::NewGuid() + ".ps1")
Set-Content -Path $tmp -Value $inner -Encoding UTF8
# The SQL goes through a temp file: a command-line argument is limited to ~32K characters,
# which the full seed (world-builder/out/db/seed.azuresql.sql) far exceeds.
$sqlTmp = Join-Path $env:TEMP ("sql-run-" + [guid]::NewGuid() + ".sql")
[IO.File]::WriteAllText($sqlTmp, $sql, (New-Object Text.UTF8Encoding $false))
try {
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File $tmp -Server $Server -Database $Database -Token $token -SqlFile $sqlTmp
  $code = $LASTEXITCODE
} finally {
  Remove-Item -LiteralPath $tmp, $sqlTmp
}
exit $code
