# API Reference — PTD Generator

Base URL: `http://127.0.0.1:5000`

## Endpoints

### GET `/`
- Description: Service root with available endpoints.
- Response example:
```json
{
  "message": "PTD Generator API is running",
  "available_endpoints": ["/status", "/health", "/run_pipeline", "/run_ptd_generation", "/download/<filename>"]
}
```

### GET `/status`
- Description: Status and version.
- Response example:
```json
{
  "status": "running",
  "message": "PTD Generator backend is operational",
  "version": "1.0.0",
  "endpoints": {"run_pipeline": "/run_pipeline", "status": "/status", "health": "/health"}
}
```

### GET `/health`
- Description: Health probe; returns current working directory.
- Response example:
```json
{"status": "healthy", "cwd": "/path/to/repo/Full_pipeline"}
```

### POST `/run_pipeline`
- Description: Accepts EITHER multipart file upload (two files) OR JSON payload with structured inputs.
- Upload fields (multipart/form-data):
  - `protocol_file`: PDF/DOC/DOCX/JSON
  - `crf_file`: PDF/DOC/DOCX/JSON
- JSON body:
```json
{
  "protocol_json": {"elements": []},
  "ecrf_json": {"elements": []}
}
```
- Responses:
  - Upload path (current behavior):
    ```json
    {
      "success": true,
      "message": "Files uploaded successfully. Note: PDF/DOC conversion not yet implemented.",
      "files": {"protocol": "Protocol_1234.pdf", "crf": "Mock CRF.pdf"},
      "next_steps": "Upload JSON files for full processing"
    }
    ```
  - JSON path (structuring outcome):
    ```json
    {
      "success": true,
      "message": "Pipeline processing completed successfully",
      "results": {
        "structured_protocol": {"name": "Document Root", "children": [...]},
        "structured_ecrf": {"name": "Document Root", "children": [...]},
        "processing_steps": ["Protocol JSON structured","eCRF JSON structured","Ready for PTD generation"]
      }
    }
    ```
- Sample curl (JSON):
```bash
curl -s -X POST http://127.0.0.1:5000/run_pipeline \
  -H 'Content-Type: application/json' \
  -d '{"protocol_json": {"elements": []}, "ecrf_json": {"elements": []}}'
```

- Sample curl (multipart upload):
```bash
curl -s -X POST http://127.0.0.1:5000/run_pipeline \
  -F protocol_file=@"Full_pipeline (Copy)/uploads/Protocol_1234.pdf" \
  -F crf_file=@"Full_pipeline (Copy)/uploads/Mock CRF.pdf"
```

### POST `/run_ptd_generation`
- Description: Runs the full PTD generation on structured JSON and creates an Excel in `output/`.
- JSON body:
```json
{
  "protocol_json": {"elements": []},
  "ecrf_json": {"elements": []}
}
```
- Response example:
```json
{
  "success": true,
  "message": "PTD generation completed",
  "output_file": "ptd_output.xlsx",
  "download_url": "/download/ptd_output.xlsx"
}
```
- Sample curl:
```bash
curl -s -X POST http://127.0.0.1:5000/run_ptd_generation \
  -H 'Content-Type: application/json' \
  -d '{"protocol_json": {"elements": []}, "ecrf_json": {"elements": []}}'
```

### GET `/download/<filename>`
- Description: Download generated files.
- Sample:
```bash
curl -L -o ptd_output.xlsx http://127.0.0.1:5000/download/ptd_output.xlsx
```

## Backend callable functions (core)

From updated modules under `PTD_Gen/modules/`:

- `soa_parser.parse_soa(protocol_json, output_csv, config=None)`
  - Parse schedule tables from protocol JSON to CSV.
  - Example:
    ```python
    from PTD_Gen.modules.soa_parser import parse_soa
    parse_soa('protocol_structured.json', 'schedule.csv')
    ```

- `form_extractor.extract_forms(ecrf_json, output_csv, config=None)`
  - Extract form metadata from eCRF JSON to CSV.

- `common_matrix.merge_common_matrix(ecrf_csv, schedule_csv, output_csv, config=None)`
  - Merge forms and schedule to a common matrix CSV.

- `event_grouping.group_events(protocol_json, output_xlsx, config=None)`
  - Create visit groups and windows from protocol JSON to Excel.

- `schedule_layout.generate_schedule_grid(visits_xlsx, forms_csv, output_xlsx, config=None)`
  - Create final schedule grid Excel.

- `Final_study_specific_form.process_clinical_forms(json_file_path, output_csv_path, config_path)`
  - Build Study Specific Forms sheet.

If you need exact examples, see the legacy implementations:
- `Full_pipeline (Copy)/backend/generate_ptd.py` — CLI reference and sequence of calls.
- `Full_pipeline (Copy)/backend/modules/*.py` — function definitions and expected inputs/outputs.

If a field detail isn’t clear, refer to the exact file and lines:
- Endpoints: `Full_pipeline (Copy)/app.py` L55–L290 (routes and logic)
- PTD CLI: `Full_pipeline (Copy)/backend/generate_ptd.py` L619–L759 (argparse and main)
