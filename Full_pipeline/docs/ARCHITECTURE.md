# Architecture — PTD Generator

## Diagram

```
User (Browser)
   |
   |  HTTP (fetch/POST)
   v
Frontend (index.html, script.js, styles.css)
   |
   |  POST /run_pipeline (files or JSON)
   |  GET /health, /status
   |  POST /run_ptd_generation (JSON)
   v
Flask API (app.py)
   |
   |  process_protocol(json)  --> json_struct_protocol.run_hierarchy
   |  process_ecrf(json)      --> json_struct_ecrf.run_hierarchy
   |  generate PTD            --> PTD_Gen/generate_ptd.py --stream
   v
PTD_Gen/modules
   |-- form_extractor.extract_forms           (eCRF → forms.csv)
   |-- soa_parser.parse_soa                   (Protocol → schedule.csv)
   |-- common_matrix.merge_common_matrix      (forms+schedule → matrix.csv)
   |-- event_grouping.group_events            (Protocol → visits.xlsx)
   |-- schedule_layout.generate_schedule_grid (visits.xlsx + matrix.csv → grid.xlsx)
   |-- Final_study_specific_form.process_clinical_forms (eCRF → forms.xlsx)
```

## Data flow

1. Frontend submits either files (currently only uploaded/saved) or JSON payloads.
2. API writes JSON to temp files and runs structuring:
   - `json_struct_protocol.run_hierarchy(input_json, output_json)`
   - `json_struct_ecrf.run_hierarchy(input_json, output_json)`
3. For PTD generation, API calls the CLI:
   - `python PTD_Gen/generate_ptd.py --protocol <structured_protocol.json> --ecrf <structured_ecrf.json> --out output/ptd_output.xlsx --stream`
4. The generator orchestrates:
   - eCRF forms extraction → CSV
   - Protocol SoA parsing → CSV
   - Merge to common matrix → CSV
   - Group visits → XLSX (visits and windowing)
   - Build final schedule grid (streamed) → Workbook with both sheets
5. API exposes `/download/<filename>` for the result.

## Sequence for main pipeline run

- `app.py` (route) → `_process_json_data(data)`
- Writes temp `protocol.json`, `ecrf.json` → calls `process_protocol`, `process_ecrf` → produces `protocol_structured.json`, `ecrf_structured.json`.
- `app.py` (route `/run_ptd_generation`) → writes structured JSON → invokes CLI with `--stream` → writes `output/ptd_output.xlsx`.

## Config file mapping

- `PTD_Gen/config/config_form_extractor.json` → tunes form label/name patterns, required keys.
- `PTD_Gen/config/config_soa_parser.json` → visit detection patterns, markers (e.g., X/Y) and header keywords.
- `PTD_Gen/config/config_common_matrix.json` → fuzzy thresholds and output column names.
- `PTD_Gen/config/config_event_grouping.json` → grouping rules, visit windows, offset types.
- `PTD_Gen/config/config_schedule_layout.json` → left columns, extra headers, stream formatting options.
- `PTD_Gen/config/config_study_specific_forms.json` → codelist detection, data type/length/precision rules.

Notes
- The old working repo keeps configs under `backend/config/` with the same names. Use those as a baseline when adjusting the updated configs.
