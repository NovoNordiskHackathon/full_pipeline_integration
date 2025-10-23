# run_all.ps1
# Usage: .\run_all.ps1 -EcrfDoc "C:\path\ecrf.doc" -ProtocolPdf "C:\path\protocol.pdf" [-OutDir "C:\output"]

param(
  [Parameter(Mandatory=$true)] [string] $EcrfDoc,
  [Parameter(Mandatory=$true)] [string] $ProtocolPdf,
  [string] $OutDir
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConvertSh = Join-Path $ScriptDir "conversion_run.sh"
$ExtractSh = Join-Path $ScriptDir "run_extraction.sh"

if (!(Test-Path $ConvertSh)) { throw "Missing conversion script at: $ConvertSh" }
if (!(Test-Path $ExtractSh)) { throw "Missing extraction script at: $ExtractSh" }

$EcrfStem = [System.IO.Path]::GetFileNameWithoutExtension($EcrfDoc)

if ($OutDir) {
  New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
  $EcrfPdf     = Join-Path $OutDir "$EcrfStem.pdf"
  $ProtocolDir = Join-Path $OutDir "protocol_extract"
  $EcrfDir     = Join-Path $OutDir "ecrf_extract"
} else {
  $EcrfPdf     = Join-Path ([System.IO.Path]::GetDirectoryName($EcrfDoc)) "$EcrfStem.pdf"
  $ProtocolDir = Join-Path ([System.IO.Path]::GetDirectoryName($ProtocolPdf)) "protocol_extract"
  $EcrfDir     = Join-Path ([System.IO.Path]::GetDirectoryName($EcrfPdf)) "ecrf_extract"
}

$ProtocolZip = "$ProtocolDir.zip"
$EcrfZip     = "$EcrfDir.zip"

Write-Host "=== Step 1: Converting eCRF to PDF ==="
if (Get-Command wsl.exe -ErrorAction SilentlyContinue) {
  wsl bash -lc "`"$ConvertSh`" `"$EcrfDoc`" `"$EcrfPdf`""
} else {
  bash "$ConvertSh" "$EcrfDoc" "$EcrfPdf"
}

Write-Host "=== Step 2a: Extracting text from PROTOCOL PDF ==="
if (Get-Command wsl.exe -ErrorAction SilentlyContinue) {
  wsl bash -lc "`"$ExtractSh`" `"$ProtocolPdf`" `"$ProtocolZip`""
} else {
  bash "$ExtractSh" "$ProtocolPdf" "$ProtocolZip"
}

Write-Host "=== Step 2b: Extracting text from eCRF PDF ==="
if (Get-Command wsl.exe -ErrorAction SilentlyContinue) {
  wsl bash -lc "`"$ExtractSh`" `"$EcrfPdf`" `"$EcrfZip`""
} else {
  bash "$ExtractSh" "$EcrfPdf" "$EcrfZip"
}

Write-Host "All steps completed."
Write-Host "eCRF PDF: $EcrfPdf"
Write-Host "Protocol JSON directory: $ProtocolDir"
Write-Host "eCRF JSON directory: $EcrfDir"
