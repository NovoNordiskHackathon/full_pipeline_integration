#!/usr/bin/env bash
# run_full_pipeline.sh
# Usage:
#   ./run_full_pipeline.sh /path/to/ecrf.doc /path/to/protocol.pdf [optional_output_dir]
# Notes:
#   - Expects API_Call.sh and Structuring_JSON.sh in the same directory as this script
#   - Structured JSONs are assumed to be named 'structuredData_output.json' (Structuring_JSON.sh default behavior)

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 /path/to/ecrf.doc /path/to/protocol.pdf [optional_output_dir]"
  exit 1
fi

ECRF_DOC="$1"
PROTOCOL_PDF="$2"
OUT_DIR="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_CALL_SH="$SCRIPT_DIR/API_Call.sh"
STRUCTURE_SH="$SCRIPT_DIR/Structuring_JSON.sh"

if [ ! -f "$API_CALL_SH" ]; then
  echo "Missing API orchestrator at: $API_CALL_SH"
  exit 1
fi
if [ ! -f "$STRUCTURE_SH" ]; then
  echo "Missing structuring orchestrator at: $STRUCTURE_SH"
  exit 1
fi

# Step 1 & 2: Run your API_Call.sh (conversion + extractions)
echo "=== Running API_Call.sh ==="
bash "$API_CALL_SH" "$ECRF_DOC" "$PROTOCOL_PDF" ${OUT_DIR:+$OUT_DIR}

# Derive extract directories as API_Call.sh does
ECRF_BASENAME="$(basename "$ECRF_DOC")"
ECRF_STEM="${ECRF_BASENAME%.*}"

if [ -n "$OUT_DIR" ]; then
  PROTOCOL_DIR="$OUT_DIR/protocol_extract"
  ECRF_DIR="$OUT_DIR/ecrf_extract"
  ECRF_PDF="$OUT_DIR/${ECRF_STEM}.pdf"
else
  ECRF_PDF="$(dirname "$ECRF_DOC")/${ECRF_STEM}.pdf"
  PROTOCOL_DIR="$(dirname "$PROTOCOL_PDF")/protocol_extract"
  ECRF_DIR="$(dirname "$ECRF_PDF")/ecrf_extract"
fi

# Step 3: Run your Structuring_JSON.sh
echo "=== Running Structuring_JSON.sh ==="
bash "$STRUCTURE_SH" "$PROTOCOL_DIR" "$ECRF_DIR"

# Structured outputs (by default)
STRUCTURED_PROTOCOL_JSON="$PROTOCOL_DIR/structuredData_output.json"
STRUCTURED_ECRF_JSON="$ECRF_DIR/structuredData_output.json"

if [ ! -f "$STRUCTURED_PROTOCOL_JSON" ]; then
  echo "Expected structured protocol JSON not found: $STRUCTURED_PROTOCOL_JSON"
  exit 1
fi
if [ ! -f "$STRUCTURED_ECRF_JSON" ]; then
  echo "Expected structured eCRF JSON not found: $STRUCTURED_ECRF_JSON"
  exit 1
fi

# Step 4: Generate PTD
echo "=== Generating PTD ==="

# Resolve paths (generator moved under backend/PTD_Gen)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEN_PTD="$SCRIPT_DIR/backend/PTD_Gen/generate_ptd.py"
TEMPLATE_PATH="$SCRIPT_DIR/backend/PTD_Gen/PTD Template v.2_Draft (1).xlsx"

if [ ! -f "$GEN_PTD" ]; then
  echo "PTD generator not found at: $GEN_PTD"
  exit 1
fi

# Pick python interpreter
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python not found in PATH."
  exit 1
fi

# If template exists, modify in place; otherwise, stream to a new file
if [ -f "$TEMPLATE_PATH" ]; then
  "$PY" "$GEN_PTD" \
    --ecrf "$STRUCTURED_ECRF_JSON" \
    --protocol "$STRUCTURED_PROTOCOL_JSON" \
    --template "$TEMPLATE_PATH" \
    --inplace
  echo "PTD output written inside PTD_Gen (in-place on template)."
else
  echo "Template not found at $TEMPLATE_PATH; using streaming mode to create a new workbook."
  OUT_XLSX="$SCRIPT_DIR/backend/PTD_Gen/PTD_Output.xlsx"
  "$PY" "$GEN_PTD" \
    --ecrf "$STRUCTURED_ECRF_JSON" \
    --protocol "$STRUCTURED_PROTOCOL_JSON" \
    --out "$OUT_XLSX" \
    --stream
  echo "PTD output written to $OUT_XLSX"
fi

echo "All done."
echo "Protocol JSON dir: $PROTOCOL_DIR"
echo "eCRF JSON dir: $ECRF_DIR"
echo "Structured protocol JSON: $STRUCTURED_PROTOCOL_JSON"
echo "Structured eCRF JSON: $STRUCTURED_ECRF_JSON"
