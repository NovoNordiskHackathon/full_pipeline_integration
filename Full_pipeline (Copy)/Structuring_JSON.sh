#!/usr/bin/env bash
# Structuring_JSON.sh
# Usage:
#   ./Structuring_JSON.sh /path/to/protocol_extract /path/to/ecrf_extract [protocol_json_name] [ecrf_json_name]
# Defaults:
#   protocol_json_name = structuredData.json
#   ecrf_json_name     = structuredData.json

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 /path/to/protocol_extract /path/to/ecrf_extract [protocol_json_name] [ecrf_json_name]"
  exit 1
fi

PROTO_DIR="$1"
ECRF_DIR="$2"
PROTO_JSON_NAME="${3:-structuredData.json}"
ECRF_JSON_NAME="${4:-structuredData.json}"

# Resolve script directory (expects the two Python files here)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROTO_SCRIPT="$SCRIPT_DIR/json_struct_protocol.py"
ECRF_SCRIPT="$SCRIPT_DIR/json_struct_ecrf.py"

# Pick python
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python not found in PATH."
  exit 1
fi

PROTO_JSON_PATH="$PROTO_DIR/$PROTO_JSON_NAME"
ECRF_JSON_PATH="$ECRF_DIR/$ECRF_JSON_NAME"

if [ ! -f "$PROTO_SCRIPT" ]; then
  echo "Missing: $PROTO_SCRIPT"
  exit 1
fi
if [ ! -f "$ECRF_SCRIPT" ]; then
  echo "Missing: $ECRF_SCRIPT"
  exit 1
fi
if [ ! -f "$PROTO_JSON_PATH" ]; then
  echo "Protocol JSON not found at: $PROTO_JSON_PATH"
  exit 1
fi
if [ ! -f "$ECRF_JSON_PATH" ]; then
  echo "eCRF JSON not found at: $ECRF_JSON_PATH"
  exit 1
fi

echo "=== Structuring protocol JSON ==="
"$PY" "$PROTO_SCRIPT" "$PROTO_JSON_PATH"

echo "=== Structuring eCRF JSON ==="
"$PY" "$ECRF_SCRIPT" "$ECRF_JSON_PATH"

echo "Done. Outputs saved alongside inputs with '_output' suffix."
