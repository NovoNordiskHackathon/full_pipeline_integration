# run_structuring.ps1
# Usage:
#   .\run_structuring.ps1 -ProtocolDir "C:\path\protocol_extract" -EcrfDir "C:\path\ecrf_extract" [-ProtocolJsonName "structuredData.json"] [-EcrfJsonName "structuredData.json"]

param(
  [Parameter(Mandatory=$true)] [string] $ProtocolDir,
  [Parameter(Mandatory=$true)] [string] $EcrfDir,
  [string] $ProtocolJsonName = "structuredData.json",
  [string] $EcrfJsonName     = "structuredData.json"
)

$ErrorActionPreference = "Stop"

$ScriptDir      = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProtocolScript = Join-Path $ScriptDir "json_struct_protocol.py"
$EcrfScript     = Join-Path $ScriptDir "json_struct_ecrf.py"

# Prefer python, then python3 on Windows if present
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $python) { throw "Python not found in PATH." }
$PY = $python.Source

$ProtocolJsonPath = Join-Path $ProtocolDir $ProtocolJsonName
$EcrfJsonPath     = Join-Path $EcrfDir $EcrfJsonName

if (!(Test-Path $ProtocolScript)) { throw "Missing: $ProtocolScript" }
if (!(Test-Path $EcrfScript))     { throw "Missing: $EcrfScript" }
if (!(Test-Path $ProtocolJsonPath)) { throw "Protocol JSON not found at: $ProtocolJsonPath" }
if (!(Test-Path $EcrfJsonPath))     { throw "eCRF JSON not found at: $EcrfJsonPath" }

Write-Host "=== Structuring protocol JSON ==="
& $PY $ProtocolScript $ProtocolJsonPath

Write-Host "=== Structuring eCRF JSON ==="
& $PY $EcrfScript $EcrfJsonPath

Write-Host "Done. Outputs saved alongside inputs with '_output' suffix."
