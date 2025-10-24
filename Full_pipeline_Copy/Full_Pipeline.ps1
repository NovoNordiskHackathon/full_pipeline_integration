# run_full_pipeline.ps1
# Usage:
#   .\run_full_pipeline.ps1 -EcrfDoc "C:\path\ecrf.doc" -ProtocolPdf "C:\path\protocol.pdf" [-OutDir "C:\out"]
# Notes:
#   - Expects API_Call.sh and Structuring_JSON.sh next to this script
#   - Uses WSL/bash if available; otherwise relies on bash in PATH (e.g., Git Bash)

param(
  [Parameter(Mandatory=$true)] [string] $EcrfDoc,
  [Parameter(Mandatory=$true)] [string] $ProtocolPdf,
  [string] $OutDir
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ApiCall = Join-Path $ScriptDir "API_Call.sh"
$Structuring = Join-Path $ScriptDir "Structuring_JSON.sh"

if (!(Test-Path $ApiCall)) { throw "Missing: $ApiCall" }
if (!(Test-Path $Structuring)) { throw "Missing: $Structuring" }

# Prefer WSL if available
$UseWSL = ($null -ne (Get-Command wsl.exe -ErrorAction SilentlyContinue))

Write-Host "=== Running API_Call.sh ==="
if ($UseWSL) {
  if ($OutDir) {
    wsl bash -lc "`"$ApiCall`" `"$EcrfDoc`" `"$ProtocolPdf`" `"$OutDir`""
  } else {
    wsl bash -lc "`"$ApiCall`" `"$EcrfDoc`" `"$ProtocolPdf`""
  }
} else {
  if ($OutDir) {
    bash "$ApiCall" "$EcrfDoc" "$ProtocolPdf" "$OutDir"
  } else {
    bash "$ApiCall" "$EcrfDoc" "$ProtocolPdf"
  }
}

# Derive extract dirs (mirror API_Call.sh logic)
$EcrfStem = [System.IO.Path]::GetFileNameWithoutExtension($EcrfDoc)
if ($OutDir) {
  $ProtocolDir = Join-Path $OutDir "protocol_extract"
  $EcrfDir     = Join-Path $OutDir "ecrf_extract"
  $EcrfPdfOut  = Join-Path $OutDir "$EcrfStem.pdf"
} else {
  $EcrfPdfOut  = Join-Path ([System.IO.Path]::GetDirectoryName($EcrfDoc)) "$EcrfStem.pdf"
  $ProtocolDir = Join-Path ([System.IO.Path]::GetDirectoryName($ProtocolPdf)) "protocol_extract"
  $EcrfDir     = Join-Path ([System.IO.Path]::GetDirectoryName($EcrfPdfOut)) "ecrf_extract"
}

Write-Host "=== Running Structuring_JSON.sh ==="
if ($UseWSL) {
  wsl bash -lc "`"$Structuring`" `"$ProtocolDir`" `"$EcrfDir`""
} else {
  bash "$Structuring" "$ProtocolDir" "$EcrfDir"
}

# Structured outputs (defaults)
$StructuredProtocolJson = Join-Path $ProtocolDir "structuredData_output.json"
$StructuredEcrfJson     = Join-Path $EcrfDir "structuredData_output.json"
if (!(Test-Path $StructuredProtocolJson)) { throw "Missing: $StructuredProtocolJson" }
if (!(Test-Path $StructuredEcrfJson))     { throw "Missing: $StructuredEcrfJson" }

Write-Host "=== Generating PTD ==="
$TemplatePath = "PTD_Gen/PTD Template v.2_Draft (1).xlsx"

# Pick python (Windows)
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $python) { throw "Python not found in PATH." }
$PY = $python.Source

& $PY "PTD_Gen/generate_ptd.py" `
  --ecrf "$StructuredEcrfJson" `
  --protocol "$StructuredProtocolJson" `
  --template "$TemplatePath" `
  --inplace

Write-Host "All done."
Write-Host "Protocol JSON dir: $ProtocolDir"
Write-Host "eCRF JSON dir: $EcrfDir"
Write-Host "Structured protocol JSON: $StructuredProtocolJson"
Write-Host "Structured eCRF JSON: $StructuredEcrfJson"
Write-Host "PTD output written inside PTD_Gen (in-place on template)."
