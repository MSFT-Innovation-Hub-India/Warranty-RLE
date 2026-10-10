$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root = 'C:\Users\sansri\contoso-warranty-rle'
Set-Location $root
$sha = [Security.Cryptography.SHA256]::Create()
try {
  foreach ($arm in @('probe', 'simple', 'bestofn')) {
    $dir = Join-Path $root "docs\evidence\stage-3\$arm"
    $files = @(Get-ChildItem -LiteralPath $dir -File | Where-Object { $_.Name -match '^command-[0-9a-f]{32}\.(stdout|stderr)\.txt$' } | Sort-Object Name)
    if (-not $files.Count) { throw "No captures found in $dir" }
    $archive = Join-Path $dir 'command-captures.zip'
    $manifest = Join-Path $dir 'command-captures.manifest.json'
    if ((Test-Path -LiteralPath $archive) -or (Test-Path -LiteralPath $manifest)) { throw "Archive already exists in $dir" }
    $records = @()
    foreach ($file in $files) {
      $relative = $file.FullName.Substring($root.Length + 1)
      git ls-files --error-unmatch -- $relative 2>$null | Out-Null
      if ($LASTEXITCODE -eq 0) { throw "Refusing to remove tracked capture: $relative" }
      $bytes = [IO.File]::ReadAllBytes($file.FullName)
      $hash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant()
      $records += [pscustomobject]@{ name = $file.Name; bytes = $bytes.Length; sha256 = $hash }
    }
    Compress-Archive -LiteralPath $files.FullName -DestinationPath $archive -CompressionLevel Optimal
    $zip = [IO.Compression.ZipFile]::OpenRead($archive)
    try {
      if ($zip.Entries.Count -ne $files.Count) { throw "Archive entry count mismatch: $archive" }
      foreach ($record in $records) {
        $entry = $zip.GetEntry($record.name)
        if ($null -eq $entry) { throw "Missing archive entry: $($record.name)" }
        $stream = $entry.Open()
        try { $hash = [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
        finally { $stream.Dispose() }
        if ($entry.Length -ne $record.bytes -or $hash -ne $record.sha256) { throw "Archive byte mismatch: $($record.name)" }
      }
    } finally { $zip.Dispose() }
    $records | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $manifest -Encoding utf8
    foreach ($file in $files) { Remove-Item -LiteralPath $file.FullName }
    "PASS $arm : $($records.Count) captures archived; every original byte verified with SHA-256"
  }
} finally { $sha.Dispose() }
