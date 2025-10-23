#!/bin/bash
# run_extraction.sh
# Extract text JSON from a PDF using local Python entrypoint, then unzip
# Usage: ./run_extraction.sh /path/to/input.pdf [optional_output.zip]

set -euo pipefail

# -------- CHECK ARGUMENTS --------
if [ -z "${1:-}" ]; then
    echo "Usage: $0 /path/to/input.pdf [optional_output.zip]"
    exit 1
fi

INPUT_PDF="$1"
OUTPUT_ZIP="${2:-extractTextInfoFromPDF.zip}"
OUTPUT_DIR="${OUTPUT_ZIP%.zip}"

# -------- RESOLVE SCRIPT DIR --------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -------- PICK PYTHON --------
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python not found in PATH."
  exit 1
fi

# -------- OPTIONAL VENV (LOCAL .venv) --------
if [ -z "${VIRTUAL_ENV:-}" ] && [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.venv/bin/activate"
fi

# -------- EMBEDDED CREDENTIALS (as requested) --------
# WARNING: Storing secrets in source is insecure. Prefer env vars in production.
export PDF_SERVICES_CLIENT_ID="fac56459a2be4f3794621e0beef349c6"
export PDF_SERVICES_CLIENT_SECRET="p8e-J-2GTpkl34Gl-huJqqh6Qwp77WKJ-Hs1"

# -------- CHECK CREDENTIALS --------
if [ -z "${PDF_SERVICES_CLIENT_ID:-}" ] || [ -z "${PDF_SERVICES_CLIENT_SECRET:-}" ]; then
  echo "Missing Adobe PDF Services credentials: set PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET"
  exit 1
fi

# -------- RUN THE PYTHON SCRIPT --------
echo "Running PDF extraction..."
"$PY" "$SCRIPT_DIR/simpletext_extract.py" "$INPUT_PDF" -o "$OUTPUT_ZIP"

# -------- UNZIP THE RESULT --------
echo "Unzipping the result..."
mkdir -p "$OUTPUT_DIR"
unzip -o "$OUTPUT_ZIP" -d "$OUTPUT_DIR"

echo "Extraction and unzip complete. JSON available in $OUTPUT_DIR"

