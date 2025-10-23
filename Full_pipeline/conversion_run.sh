
#!/bin/bash
# conversion_run.sh
# Convert a document to PDF using local Python entrypoint
# Usage: ./conversion_run.sh /path/to/input_document [optional_output.pdf]

set -euo pipefail

# -------- CHECK ARGUMENTS --------
if [ -z "${1:-}" ]; then
    echo "Usage: $0 /path/to/input_document [optional_output.pdf]"
    exit 1
fi

INPUT_DOC="$1"
# Default: replace extension with .pdf
INPUT_DIRNAME="$(dirname "$INPUT_DOC")"
INPUT_BASENAME="$(basename "$INPUT_DOC")"
INPUT_STEM="${INPUT_BASENAME%.*}"
OUTPUT_PDF="${2:-$INPUT_DIRNAME/$INPUT_STEM.pdf}"

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
export PDF_SERVICES_CLIENT_ID="cfe6d92ffc8a4021bc01ca26b3917849"
export PDF_SERVICES_CLIENT_SECRET="p8e-nbSa5xqfkJsuvtloz1nzrhX_DRFqzHr6"

# -------- CHECK CREDENTIALS --------
if [ -z "${PDF_SERVICES_CLIENT_ID:-}" ] || [ -z "${PDF_SERVICES_CLIENT_SECRET:-}" ]; then
  echo "Missing Adobe PDF Services credentials: set PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET"
  exit 1
fi

# -------- RUN THE PYTHON SCRIPT --------
echo "Converting document to PDF..."
"$PY" "$SCRIPT_DIR/doc_to_pdf.py" "$INPUT_DOC" "$OUTPUT_PDF"

if [[ -f "$OUTPUT_PDF" ]]; then
    echo "Conversion successful: $OUTPUT_PDF"
else
    echo "Conversion failed."
    exit 1
fi

