#!/usr/bin/env bash
# run_all.sh
# Usage: ./run_all.sh /path/to/ecrf.doc /path/to/protocol.pdf [optional_output_dir]

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 /path/to/ecrf.doc /path/to/protocol.pdf [optional_output_dir]"
  exit 1
fi

ECRF_DOC="$1"
PROTOCOL_PDF="$2"
OUT_DIR="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONVERT_SH="$SCRIPT_DIR/conversion_run.sh"
EXTRACT_SH="$SCRIPT_DIR/run_extraction.sh"

if [ ! -f "$CONVERT_SH" ]; then
  echo "Missing conversion script at: $CONVERT_SH"
  exit 1
fi
if [ ! -f "$EXTRACT_SH" ]; then
  echo "Missing extraction script at: $EXTRACT_SH"
  exit 1
fi

ECRF_BASENAME="$(basename "$ECRF_DOC")"
ECRF_STEM="${ECRF_BASENAME%.*}"

if [ -n "$OUT_DIR" ]; then
  mkdir -p "$OUT_DIR"
  ECRF_PDF="$OUT_DIR/${ECRF_STEM}.pdf"
  PROTOCOL_DIR="$OUT_DIR/protocol_extract"
  ECRF_DIR="$OUT_DIR/ecrf_extract"
else
  ECRF_PDF="$(dirname "$ECRF_DOC")/${ECRF_STEM}.pdf"
  PROTOCOL_DIR="$(dirname "$PROTOCOL_PDF")/protocol_extract"
  ECRF_DIR="$(dirname "$ECRF_PDF")/ecrf_extract"
fi

PROTOCOL_ZIP="${PROTOCOL_DIR}.zip"
ECRF_ZIP="${ECRF_DIR}.zip"

echo "=== Step 1: Converting eCRF to PDF ==="
bash "$CONVERT_SH" "$ECRF_DOC" "$ECRF_PDF"

echo "=== Step 2a: Extracting text from PROTOCOL PDF ==="
bash "$EXTRACT_SH" "$PROTOCOL_PDF" "$PROTOCOL_ZIP"

echo "=== Step 2b: Extracting text from eCRF PDF ==="
bash "$EXTRACT_SH" "$ECRF_PDF" "$ECRF_ZIP"

echo "All steps completed."
echo "eCRF PDF: $ECRF_PDF"
echo "Protocol JSON directory: $PROTOCOL_DIR"
echo "eCRF JSON directory: $ECRF_DIR"
