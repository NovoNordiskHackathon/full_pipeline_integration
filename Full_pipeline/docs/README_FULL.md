# PTD Generator — Full Repository Documentation

This documentation targets maintainers and new developers. It explains the purpose, architecture, repo layout, backend/ frontend modules, APIs, setup, troubleshooting, and migration notes from the old working project.

---

## 1) Project overview

- The PTD (Protocol Translation Document) Generator transforms Protocol and eCRF sources into structured JSON, then produces a combined Excel workbook summarizing visits, forms, and study-specific items.
- The system exposes a small Flask API for pipeline orchestration and a simple frontend to upload files and trigger processing.
- In the old working project (`Full_pipeline (Copy)`), the backend/ frontend integration is complete and is the canonical reference for endpoints and run commands. The current folder (`Full_pipeline`) contains updated logic and a compatible Flask app.

---

## 2) Repository layout

```
Full_pipeline/
  app.py                      # Flask app (rebuilt integration; mirrors old endpoints)
  frontend/                   # Frontend: index.html, script.js, styles.css
  PTD_Gen/                    # Updated PTD generation modules
    config/                   # JSON configurations for each stage
    modules/                  # Core pipeline modules (SoA parser, forms, schedule)
    generate_ptd.py           # CLI orchestrator for full PTD generation
    Final_study_specific_form.py
  requirements.txt            # Root runtime dependencies
  ... (scripts)               # start_backend.sh, run_extraction.sh, etc.

Full_pipeline (Copy)/          # Old working project (reference)
  app.py                       # Flask API with working frontend integration
  backend/                     # Legacy pipeline folder + modules
    config/                    # Legacy JSON configs
    modules/                   # Legacy modules (form_extractor, soa_parser, ...)
    generate_ptd.py            # Older PTD orchestration
  frontend/                    # Legacy frontend
  requirements.txt             # Legacy deps
```

Short descriptions (top-level):
- `app.py`: Flask app serving the API and orchestrating JSON structuring and PTD generation.
- `frontend/`: Modern, single‑page UI for uploading files and calling `/run_pipeline`.
- `PTD_Gen/`: Updated pipeline. Mirrors legacy `backend/` but with clearer structure and configs.
- `requirements.txt`: Project dependencies (Flask, CORS, pandas, openpyxl, xlsxwriter, etc.).
- Scripts (`start_backend.sh`, `run_extraction.sh`, `conversion_run.sh`): helpers to run parts of the pipeline.

---

## 3) Architecture diagram and flow

ASCII diagram

```
+-----------------+         +-------------------------+          +--------------------+
|  Frontend (UI)  |  --->   | Flask API (app.py)      |   --->   |  Pipeline Modules  |
| index.html/js   |  POST   | /run_pipeline, /health  |          |  (PTD_Gen/modules) |
| styles.css      |         | /run_ptd_generation     |          |                    |
+--------+--------+         +-----------+-------------+          +----------+---------+
                                  |                                       |
                                  | writes temp JSON files                |
                                  v                                       v
                             +----------------+                   +---------------------+
                             | JSON Structing |  process_*()      |  PTD Generation     |
                             | (protocol,eCRF)| -----------------> | generate_ptd.py     |
                             +----------------+                    |  (stream/template)  |
                                      |                            +----------+----------+
                                      |                                         |
                                      v                                         v
                                 Structured JSON                         PTD Excel (.xlsx)
```

Textual flow
- Frontend uploads files or sends JSON → Flask `/run_pipeline`.
- If JSON: `app.py` writes temp files and calls the structuring functions:
  - Protocol: `json_struct_protocol.run_hierarchy(...)`
  - eCRF: `json_struct_ecrf.run_hierarchy(...)`
- Optional: `/run_ptd_generation` calls `PTD_Gen/generate_ptd.py` to produce the Excel, using stream mode (no template file required).

Key calling relationships
- `app.py` → `json_struct_protocol.run_hierarchy` and `json_struct_ecrf.run_hierarchy`
- `app.py` → `PTD_Gen/generate_ptd.py --stream` (subprocess)
- `generate_ptd.py` → `modules.form_extractor`, `modules.soa_parser`, `modules.common_matrix`, `modules.event_grouping`, `modules.schedule_layout`, `Final_study_specific_form`.

---

## 4) Detailed module descriptions (legacy reference + updated modules)

This section documents the modules from the old working project (`Full_pipeline (Copy)/backend/…`) and the updated equivalents in `Full_pipeline/PTD_Gen/modules`. File names are the same or very similar; configs moved from `backend/config` → `PTD_Gen/config` in the updated layout.

- `backend/json_struct_protocol.py` and `backend/json_struct_ecrf.py`
  - Purpose: Convert flat JSON extracted from PDFs into a hierarchical structure rooted at `"Document Root"`, fixing table placement and header nesting.
  - Main functions:
    - `run_hierarchy(input_file, output_file=None)`
  - Inputs/Outputs:
    - Input: path to JSON file with `elements: [{ path, text, ...}]`
    - Output: hierarchical JSON written to `output_file` (or `{input}_output.json`)
  - Config: N/A
  - Example:
    ```bash
    python backend/json_struct_protocol.py path/to/protocol.json
    ```

- `backend/generate_ptd.py`
  - Purpose: Build combined PTD workbook (Schedule Grid + Study Specific Forms) using the five-stage pipeline and template/stream modes.
  - Main functions:
    - `run_schedule_grid_pipeline(protocol_json, ecrf_json, final_output_xlsx, config_dir, for_stream=False)`
    - `generate_study_specific_forms_xlsx(ecrf_json)`
    - `replace_sheets_in_template(...)`, `finalize_formatting(...)`, `main()`
  - Inputs/Outputs:
    - Inputs: structured protocol and eCRF JSON paths; optional template path
    - Outputs: `.xlsx` file either in-place or at `--out`
  - Config: `backend/config/*.json` (see mapping below)
  - Example:
    ```bash
    python backend/generate_ptd.py \
      --protocol protocol_structured.json \
      --ecrf ecrf_structured.json \
      --template PTD_Template.xlsx \
      --out ptd_output.xlsx
    ```

- `backend/Final_study_specific_form.py`
  - Purpose: Extract study-specific items into a multi-row grouped Excel layout with CTDM-style headers.
  - Main functions:
    - `process_clinical_forms(json_file_path, output_csv_path, config_path)`
    - Helpers to derive data types, lengths, precision, and ranges from codelist content.
  - Inputs/Outputs: takes structured eCRF JSON, produces Excel sheet.
  - Config: `config_study_specific_forms.json`

- `backend/modules/form_extractor.py`
  - Purpose: Extract high-level forms from eCRF JSON (labels, names, triggers, required flags, visits), deduplicating and validating.
  - Key functions: `extract_forms()`, `extract_forms_with_corrections()`, helpers for trigger/visit detection.
  - Inputs/Outputs: eCRF JSON → CSV of forms.
  - Config: `config_form_extractor.json`

- `backend/modules/soa_parser.py`
  - Purpose: Parse protocol SoA tables, detect visit headers, map procedures per visit, and produce a schedule CSV.
  - Key functions: `parse_soa()`, `parse_protocol_schedule()`, `save_schedule_to_csv()`
  - Inputs/Outputs: protocol JSON → schedule CSV with visits as columns.
  - Config: `config_soa_parser.json`

- `backend/modules/common_matrix.py`
  - Purpose: Merge forms CSV and schedule CSV to construct a common per-visit matrix with ordering via fuzzy matching.
  - Key functions: `merge_common_matrix()` (internally `generate_ordered_soa_matrix()`)
  - Inputs/Outputs: forms CSV + schedule CSV → matrix CSV.
  - Config: `config_common_matrix.json`

- `backend/modules/event_grouping.py`
  - Purpose: Group visits into event categories (e.g., Screening, Randomisation), derive offset types/ windows.
  - Key functions: `group_events()` (internally `generate_visits_with_groups()`)
  - Inputs/Outputs: protocol JSON → visits-with-groups Excel.
  - Config: `config_event_grouping.json`

- `backend/modules/schedule_layout.py`
  - Purpose: Build final schedule grid Excel using visits-with-groups and the common matrix.
  - Key functions: `generate_schedule_grid()`, `build_schedule_layout()`, plus a streaming writer variant.
  - Inputs/Outputs: visits-with-groups Excel + matrix CSV → formatted Excel grid.
  - Config: `config_schedule_layout.json`

Configuration files used (updated location under `PTD_Gen/config/`):
- `config_form_extractor.json`
- `config_soa_parser.json`
- `config_common_matrix.json`
- `config_event_grouping.json`
- `config_schedule_layout.json`
- `config_study_specific_forms.json`

---

## 5) Frontend files

- `frontend/index.html`: Landing page with upload area, progress indicator, and result section.
- `frontend/script.js`: Handles drag‑and‑drop, file selection, UI state, and calls the backend. Old repo calls `http://127.0.0.1:5000//run_pipeline` (double slash tolerated). New app also registers `//run_pipeline` for compatibility.
- `frontend/styles.css`: Styles for modern UI and animations.

Frontend → Backend interaction
- Upload path: POST to `/run_pipeline` with `FormData` containing `protocol_file` and `crf_file`.
- JSON path: POST to `/run_pipeline` with JSON body `{ protocol_json, ecrf_json }`.
- The current implementation uploads files but simulates conversion; full processing runs on JSON inputs.

---

## 6) API endpoints (from old working repo)

Exact routes and methods are defined in `Full_pipeline (Copy)/app.py`:
- `GET /` — returns service message and available endpoints
- `GET /status` — returns status, version, and endpoint map
- `GET /health` — returns `{"status": "healthy"}` and current working directory
- `POST /run_pipeline` — accepts either multipart file upload (`protocol_file`, `crf_file`) or JSON payload `{ protocol_json, ecrf_json }`; returns structured JSON or next steps
- `POST /run_ptd_generation` — accepts structured JSON, triggers PTD generation (simulated in the legacy app)
- `GET /download/<filename>` — download generated files in `output/`

Examples
```bash
# Health
curl -s http://127.0.0.1:5000/health | jq

# Pipeline (JSON):
curl -s -X POST http://127.0.0.1:5000/run_pipeline \
  -H 'Content-Type: application/json' \
  -d '{
        "protocol_json": {"elements": [{"path": "//Document/Title", "text": "Test Protocol"}]},
        "ecrf_json":     {"elements": [{"path": "//Document/Title", "text": "Test eCRF"}]}
      }' | jq

# PTD generation (JSON):
curl -s -X POST http://127.0.0.1:5000/run_ptd_generation \
  -H 'Content-Type: application/json' \
  -d '{
        "protocol_json": {"elements": []},
        "ecrf_json":     {"elements": []}
      }' | jq
```

---

## 7) Setup & installation

Create and activate a virtual environment
```bash
# from repo root
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

Install dependencies
```bash
# Updated repo
pip install -r Full_pipeline/requirements.txt
pip install -r Full_pipeline/PTD_Gen/requirements.txt

# (Optional) Legacy reference
pip install -r "Full_pipeline (Copy)/requirements.txt"
pip install -r "Full_pipeline (Copy)/backend/requirements.txt"
```

Environment variables
- None required. Default port: `5000`.

Run the backend locally
```bash
# Old working project (reference):
cd "Full_pipeline (Copy)"
python app.py

# Updated project:
cd Full_pipeline
python app.py
```

Helper scripts
- `start_backend.sh`: start the Flask app (may wrap the above Python call).
- `conversion_run.sh`, `run_extraction.sh`: legacy helpers for parts of the pipeline.
- `Full_Pipeline.sh`, `Structuring_JSON.sh`: higher‑level wrappers for structuring and generation steps.

sys.path/import notes
- The old app uses `sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))` and `sys.path.append(os.path.dirname(os.path.abspath(__file__)))` to import legacy modules.
- If you see `ModuleNotFoundError: No module named 'modules'`, run from the project root or add the relevant directory to `PYTHONPATH`.

---

## 8) How to run tests

There is a simple smoke test in the old repo: `Full_pipeline (Copy)/test_backend.py`.
```bash
# With the old backend running on :5000
python "Full_pipeline (Copy)/test_backend.py"
```
If you need tests in the updated repo, add a basic pytest suite that:
- Asserts `GET /health` returns 200.
- Posts minimal JSON to `/run_pipeline` and verifies the structured response.
- Mocks the PTD generation subprocess.

---

## 9) Troubleshooting / common errors

- ModuleNotFoundError: No module named 'modules'
  - Cause: running from the wrong working directory.
  - Fixes:
    - Run from the project root: `cd Full_pipeline && python app.py`
    - Or add to `PYTHONPATH`: `export PYTHONPATH=$(pwd)`
    - Or mirror old behavior with `sys.path.append(...)` in a local harness.

- Port already in use
  - Fix: change port via `app.run(..., port=5001)` for a local run, or stop the other process.

- PTD output file not created
  - Check the subprocess logs from `PTD_Gen/generate_ptd.py` and ensure dependencies (`openpyxl`, `xlsxwriter`, `pandas`) are installed.

- PDF/DOC conversion not implemented
  - Current pipeline expects JSON input. Use `/run_pipeline` with JSON body during development.

---

## 10) Migration notes: `Full_pipeline (Copy)` → `Full_pipeline`

- Imports:
  - Legacy: `app.py` appends `backend/` to `sys.path` and imports modules from `backend/`.
  - Updated: modules live under `PTD_Gen/modules`, configs under `PTD_Gen/config`.
- Endpoints:
  - Kept the same. The updated app also tolerates the legacy double-slash `//run_pipeline` path.
- PTD generation:
  - Legacy: `run_ptd_generation` simulated; template-based replacement optional.
  - Updated: invokes `PTD_Gen/generate_ptd.py --stream` to generate a workbook without a template.
- Frontend:
  - Legacy calls `http://127.0.0.1:5000//run_pipeline`. Updated backend registers both `/run_pipeline` and `//run_pipeline` for compatibility.

Integration items to recreate if you add a fresh `app.py` to `Full_pipeline`:
- Register endpoints: `/`, `/health`, `/status`, `/run_pipeline` (JSON or files), `/run_ptd_generation`, `/download/<filename>`.
- Ensure `PTD_Gen` is importable; call structuring functions for JSON and the CLI for generation (`--stream`).
- Create `uploads/` and `output/` folders under the app directory.

---

## 11) Useful commands & quick reference

```bash
# Create & activate venv
python -m venv .venv && source .venv/bin/activate

# Install deps (updated repo)
pip install -r Full_pipeline/requirements.txt -r Full_pipeline/PTD_Gen/requirements.txt

# Run backend (updated repo)
python Full_pipeline/app.py

# Health check
curl -s http://127.0.0.1:5000/health | jq

# Run pipeline (JSON)
curl -s -X POST http://127.0.0.1:5000/run_pipeline \
  -H 'Content-Type: application/json' \
  -d '{"protocol_json": {"elements": []}, "ecrf_json": {"elements": []}}'
```

---

## 12) Changelog

- 2025-01-01 — Placeholder — Author
  - Migrated pipeline modules under `PTD_Gen/` and kept endpoints compatible.
  - Added streaming PTD generation mode to avoid template dependency.

---

## 13) Suggested next steps / improvements

- CI: Add GitHub Actions for lint, type check, and test.
- Packaging: Publish `PTD_Gen` as an internal package; add an entry-point CLI.
- Containerization: Add Dockerfile for the API and a docker-compose service for local runs.
- Tests: Introduce unit tests for each module and API contract tests.
- Docs hosting: Publish these docs to a static site (e.g., GitHub Pages or MkDocs).

---

## 14) License

This project currently has no explicit license. Suggested default: MIT.

Steps:
1) Copy `LICENSE` (MIT) into the repo root.
2) Update owner, year, and project name.
3) Add a `License` section to README with the chosen license.

---

## 15) Verification checklist

- [ ] `python Full_pipeline/app.py` starts on port 5000
- [ ] `GET /health` returns `{ "status": "healthy" }`
- [ ] `POST /run_pipeline` with JSON returns structured `protocol` and `ecrf`
- [ ] `POST /run_ptd_generation` returns a download URL and creates `output/ptd_output.xlsx`
- [ ] Frontend page loads and calls the backend successfully
