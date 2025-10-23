# Full_pipeline - Backend Organization

This folder contains the frontend and a backend located under `backend/`.

## Layout
- `frontend/`: Static UI (HTML/JS/CSS)
- `backend/`: Flask API and processing modules
  - `app.py`: Flask server entrypoint
  - `json_struct_protocol.py`, `json_struct_ecrf.py`: JSON structuring
  - `doc_to_pdf.py`, `simpletext_extract.py`: conversion/extraction utilities
  - `PTD_Gen/`: PTD generation CLI and modules

## Quick start (API)
1. Python 3.10+
2. Install dependencies (first time):
   ```bash
   cd Full_pipeline
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```
   The API will run at `http://localhost:5000`.

### Endpoints
- `GET /status` – server status
- `POST /run_pipeline` –
  - Accepts FormData with `protocol_file` and `crf_file` (PDF/DOC/DOCX/JSON) and returns processing message
  - OR accepts JSON body `{protocol_json, ecrf_json}` and returns structured results
- `POST /run_ptd_generation` – generate PTD from structured JSONs
- `GET /download/<filename>` – download generated file

## End-to-end scripts
Run from `Full_pipeline/`.

- Convert eCRF Doc to PDF:
  ```bash
  ./conversion_run.sh /path/to/ecrf.docx /optional/out.pdf
  ```

- Extract JSON from PDFs (protocol or eCRF):
  ```bash
  ./run_extraction.sh /path/to/input.pdf /optional/out.zip
  ```

- Structure the extracted JSONs:
  ```bash
  ./Structuring_JSON.sh /path/to/protocol_extract /path/to/ecrf_extract
  ```

- Full pipeline (convert, extract, structure, generate PTD):
  ```bash
  ./Full_Pipeline.sh /path/to/ecrf.docx /path/to/protocol.pdf /optional/output_dir
  ```

## Requirements
Install once:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you need PDF Services:
```bash
export PDF_SERVICES_CLIENT_ID=your_client_id
export PDF_SERVICES_CLIENT_SECRET=your_client_secret
```

## Frontend
Open the static UI directly in your browser:
```bash
open frontend/index.html   # macOS
xdg-open frontend/index.html  # Linux
```

If your backend is not running on `http://localhost:5000`, set a different base URL before the script tag in `frontend/index.html`:
```html
<script>
  window.API_BASE = 'http://127.0.0.1:5000';
  // or your remote server URL
  // window.API_BASE = 'https://your-domain.example.com';
<\/script>
<script src="script.js"><\/script>
```

## Notes
- Uploads and outputs for the API live under `backend/uploads` and `backend/output`.
- `Full_Pipeline.sh` uses `backend/PTD_Gen` generator.
- Frontend in `frontend/` now calls the backend endpoints directly via `fetch`.
