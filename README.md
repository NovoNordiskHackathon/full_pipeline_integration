# PTD Generator - Frontend/Backend Integration

This repository wires a lightweight Flask backend to the existing PTD pipeline and a static frontend UI.

## Project layout

full_pipeline_integration/
- backend/
  - app.py
  - (reuses existing pipeline under `Full_pipeline (Copy)/PTD_Gen`)
- frontend/
  - index.html
  - script.js
  - styles.css
- requirements.txt

## Backend

Start the API (Flask):

```bash
cd backend
python app.py
```

- Status: GET http://localhost:5000/status
- Run pipeline: POST http://localhost:5000/run_pipeline
  - multipart/form-data fields:
    - protocol_json: file (JSON for protocol)
    - ecrf_json: file (JSON for eCRF)
    - template_xlsx: file (optional) Excel template
    - mode: default | stream | surgery (optional)
    - fast: true | false (optional)
- Download result: GET http://localhost:5000/download?job_id=<id>

Notes
- If no `template_xlsx` is provided, the backend returns the Schedule Grid workbook only.
- JSONs with an `elements` array are auto-structured via existing `json_struct_*` scripts.

## Frontend

Open the static page directly in a browser:

```bash
open frontend/index.html
```

The UI allows selecting two files (protocol JSON and eCRF JSON) and sends them to the backend using `fetch()`.

## Requirements

Install Python dependencies from the repo root:

```bash
pip install -r requirements.txt
```

This includes Flask, flask-cors, and pipeline dependencies (pandas, openpyxl, xlsxwriter, pdfservices-sdk).

## Development tips

- Backend logs and temp artifacts are written under `runs/`.
- Existing pipeline logic is reused; no code changes were made to the algorithmic modules.
