# PTD Generator - API Reference

## Base URL
```
http://localhost:5000
```

## Authentication
Currently, no authentication is required. All endpoints are publicly accessible.

## Content Types
- **JSON**: `application/json`
- **Multipart**: `multipart/form-data` (for file uploads)

## Error Responses

All error responses follow this format:
```json
{
  "success": false,
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (endpoint or file not found)
- `500`: Internal Server Error

## Endpoints

### 1. Home Page

#### `GET /`
Get API information and available endpoints.

**Response:**
```json
{
  "message": "PTD Generator API is running",
  "available_endpoints": [
    "/status",
    "/health", 
    "/run_pipeline",
    "/run_ptd_generation"
  ]
}
```

**Example cURL:**
```bash
curl -X GET http://localhost:5000/
```

---

### 2. System Status

#### `GET /status`
Get current system status and version information.

**Response:**
```json
{
  "status": "running",
  "message": "PTD Generator backend is operational",
  "version": "1.0.0",
  "endpoints": {
    "run_pipeline": "/run_pipeline",
    "status": "/status",
    "health": "/health"
  }
}
```

**Example cURL:**
```bash
curl -X GET http://localhost:5000/status
```

---

### 3. Health Check

#### `GET /health`
Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "/workspace/Full_pipeline"
}
```

**Example cURL:**
```bash
curl -X GET http://localhost:5000/health
```

---

### 4. Main Pipeline

#### `POST /run_pipeline`
Main pipeline endpoint for processing documents. Supports both file upload and JSON data input.

**Request Types:**

##### A. File Upload (multipart/form-data)
Upload Protocol and CRF documents for processing.

**Form Data:**
- `protocol_file` (file, required): Protocol document (PDF/DOC/DOCX)
- `crf_file` (file, required): CRF document (PDF/DOC/DOCX)

**Response (Success):**
```json
{
  "success": true,
  "message": "Files uploaded successfully. Note: PDF/DOC conversion not yet implemented.",
  "files": {
    "protocol": "protocol.pdf",
    "crf": "crf.pdf"
  },
  "next_steps": "Upload JSON files for full processing"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Both protocol and CRF files are required"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/run_pipeline \
  -F "protocol_file=@protocol.pdf" \
  -F "crf_file=@crf.pdf"
```

##### B. JSON Data (application/json)
Process structured JSON data directly.

**Request Body:**
```json
{
  "protocol_json": {
    "elements": [
      {
        "name": "Document",
        "text": "Protocol content...",
        "path": "//Document",
        "children": [...]
      }
    ]
  },
  "ecrf_json": {
    "elements": [
      {
        "name": "Document",
        "text": "eCRF content...",
        "path": "//Document",
        "children": [...]
      }
    ]
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Pipeline processing completed successfully",
  "results": {
    "structured_protocol": {
      "name": "Document Root",
      "children": [...]
    },
    "structured_ecrf": {
      "name": "Document Root",
      "children": [...]
    },
    "processing_steps": [
      "Protocol JSON structured",
      "eCRF JSON structured",
      "Ready for PTD generation"
    ]
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Either upload files or provide JSON data"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/run_pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_json": {"elements": []},
    "ecrf_json": {"elements": []}
  }'
```

---

### 5. PTD Generation

#### `POST /run_ptd_generation`
Run the full PTD generation pipeline with structured JSON data.

**Request Body:**
```json
{
  "protocol_json": {
    "elements": [
      {
        "name": "Document",
        "text": "Protocol content...",
        "path": "//Document",
        "children": [...]
      }
    ]
  },
  "ecrf_json": {
    "elements": [
      {
        "name": "Document",
        "text": "eCRF content...",
        "path": "//Document",
        "children": [...]
      }
    ]
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "PTD generation completed",
  "output_file": "ptd_output.xlsx",
  "download_url": "/download/ptd_output.xlsx"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Protocol and eCRF JSON data are required"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/run_ptd_generation \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_json": {"elements": []},
    "ecrf_json": {"elements": []}
  }'
```

---

### 6. File Download

#### `GET /download/<filename>`
Download generated files.

**Parameters:**
- `filename` (string, required): Name of the file to download

**Response (Success):**
- File download with appropriate MIME type

**Response (Error):**
```json
{
  "error": "File not found"
}
```

**Example cURL:**
```bash
curl -X GET http://localhost:5000/download/ptd_output.xlsx \
  --output ptd_output.xlsx
```

---

## Backend Module Functions

### Form Extractor Module

#### `extract_forms(ecrf_json, output_csv, config)`
Extract forms from eCRF JSON and save to CSV.

**Parameters:**
- `ecrf_json` (string): Path to eCRF JSON file
- `output_csv` (string): Path to output CSV file
- `config` (dict): Configuration dictionary

**Returns:**
- `str`: Path to output CSV file

**Example:**
```python
from PTD_Gen.modules.form_extractor import extract_forms

result = extract_forms(
    ecrf_json="ecrf.json",
    output_csv="forms.csv",
    config={"visit_patterns": ["V\\d+"]}
)
```

#### `extract_forms_with_corrections(data, config)`
Enhanced form extraction with corrections and source detection.

**Parameters:**
- `data` (dict): eCRF JSON data
- `config` (dict): Configuration dictionary

**Returns:**
- `list`: List of extracted form dictionaries

**Example:**
```python
from PTD_Gen.modules.form_extractor import extract_forms_with_corrections

forms = extract_forms_with_corrections(
    data=ecrf_data,
    config={"visit_patterns": ["V\\d+"]}
)
```

### SoA Parser Module

#### `parse_soa(protocol_json, output_csv, config)`
Parse schedule of activities from protocol JSON.

**Parameters:**
- `protocol_json` (string): Path to protocol JSON file
- `output_csv` (string): Path to output CSV file
- `config` (dict): Configuration dictionary

**Returns:**
- `str`: Path to output CSV file

**Example:**
```python
from PTD_Gen.modules.soa_parser import parse_soa

result = parse_soa(
    protocol_json="protocol.json",
    output_csv="schedule.csv",
    config={"visit_patterns": ["V\\d+"]}
)
```

#### `parse_protocol_schedule(protocol_data, config)`
Parse the protocol schedule and extract visit-procedure mappings.

**Parameters:**
- `protocol_data` (dict): Protocol JSON data
- `config` (dict): Configuration dictionary

**Returns:**
- `tuple`: (schedule_dict, visit_order, procedure_order)

**Example:**
```python
from PTD_Gen.modules.soa_parser import parse_protocol_schedule

schedule, visits, procedures = parse_protocol_schedule(
    protocol_data=protocol_data,
    config={"visit_patterns": ["V\\d+"]}
)
```

### Common Matrix Module

#### `merge_common_matrix(ecrf_csv, schedule_csv, output_csv, config)`
Merge common data matrix from forms and schedule.

**Parameters:**
- `ecrf_csv` (string): Path to eCRF CSV file
- `schedule_csv` (string): Path to schedule CSV file
- `output_csv` (string): Path to output CSV file
- `config` (dict): Configuration dictionary

**Returns:**
- `str`: Path to output CSV file

**Example:**
```python
from PTD_Gen.modules.common_matrix import merge_common_matrix

result = merge_common_matrix(
    ecrf_csv="forms.csv",
    schedule_csv="schedule.csv",
    output_csv="matrix.csv",
    config={}
)
```

### Event Grouping Module

#### `group_events(protocol_json, output_xlsx, config)`
Group events by visits and create visit structure.

**Parameters:**
- `protocol_json` (string): Path to protocol JSON file
- `output_xlsx` (string): Path to output Excel file
- `config` (dict): Configuration dictionary

**Returns:**
- `str`: Path to output Excel file

**Example:**
```python
from PTD_Gen.modules.event_grouping import group_events

result = group_events(
    protocol_json="protocol.json",
    output_xlsx="visits.xlsx",
    config={}
)
```

### Schedule Layout Module

#### `generate_schedule_grid(visits_xlsx, forms_csv, output_xlsx, config)`
Generate final schedule grid layout.

**Parameters:**
- `visits_xlsx` (string): Path to visits Excel file
- `forms_csv` (string): Path to forms CSV file
- `output_xlsx` (string): Path to output Excel file
- `config` (dict): Configuration dictionary

**Returns:**
- `str`: Path to output Excel file

**Example:**
```python
from PTD_Gen.modules.schedule_layout import generate_schedule_grid

result = generate_schedule_grid(
    visits_xlsx="visits.xlsx",
    forms_csv="forms.csv",
    output_xlsx="schedule.xlsx",
    config={}
)
```

#### `generate_schedule_grid_stream(visits_xlsx, forms_csv, workbook, sheet_name, config)`
Stream-based schedule grid generation.

**Parameters:**
- `visits_xlsx` (string): Path to visits Excel file
- `forms_csv` (string): Path to forms CSV file
- `workbook` (object): XlsxWriter workbook object
- `sheet_name` (string): Name of the sheet
- `config` (dict): Configuration dictionary

**Returns:**
- `None`

**Example:**
```python
import xlsxwriter
from PTD_Gen.modules.schedule_layout import generate_schedule_grid_stream

workbook = xlsxwriter.Workbook('output.xlsx')
generate_schedule_grid_stream(
    visits_xlsx="visits.xlsx",
    forms_csv="forms.csv",
    workbook=workbook,
    sheet_name="Schedule Grid",
    config={}
)
workbook.close()
```

### PTD Generation Module

#### `main()`
Main PTD generation CLI entry point.

**Command Line Arguments:**
- `--ecrf`: Path to eCRF JSON file (required)
- `--protocol`: Path to protocol JSON file (required)
- `--template`: Path to template Excel file (optional)
- `--out`: Output Excel file path (optional)
- `--inplace`: Modify template file in place (flag)
- `--fast`: Fast mode: values-only copy (flag)
- `--stream`: Stream directly to workbook (flag)
- `--surgery`: Low-RAM in-place surgery (flag)

**Example:**
```bash
python PTD_Gen/generate_ptd.py \
  --ecrf ecrf.json \
  --protocol protocol.json \
  --out ptd_output.xlsx \
  --template template.xlsx
```

#### `run_schedule_grid_pipeline(protocol_json, ecrf_json, final_output_xlsx, config_dir, for_stream)`
Execute the 5-stage pipeline to produce schedule grid.

**Parameters:**
- `protocol_json` (string): Path to protocol JSON file
- `ecrf_json` (string): Path to eCRF JSON file
- `final_output_xlsx` (string): Path to output Excel file
- `config_dir` (string): Path to configuration directory
- `for_stream` (bool): Whether to prepare for streaming

**Returns:**
- `str` or `dict`: Path to output file or streaming data

**Example:**
```python
from PTD_Gen.generate_ptd import run_schedule_grid_pipeline

result = run_schedule_grid_pipeline(
    protocol_json="protocol.json",
    ecrf_json="ecrf.json",
    final_output_xlsx="output.xlsx",
    config_dir="PTD_Gen/config",
    for_stream=False
)
```

### Study Specific Forms Module

#### `process_clinical_forms(ecrf_json, output_csv_path, config_path)`
Process clinical forms and generate study-specific forms.

**Parameters:**
- `ecrf_json` (string): Path to eCRF JSON file
- `output_csv_path` (string): Path to output CSV file
- `config_path` (string): Path to configuration file

**Returns:**
- `None`

**Example:**
```python
from PTD_Gen.Final_study_specific_form import process_clinical_forms

process_clinical_forms(
    ecrf_json="ecrf.json",
    output_csv_path="forms.csv",
    config_path="PTD_Gen/config/config_study_specific_forms.json"
)
```

#### `prepare_study_specific_forms_rows(json_file_path, config_path)`
Prepare data rows for study-specific forms.

**Parameters:**
- `json_file_path` (string): Path to eCRF JSON file
- `config_path` (string): Path to configuration file

**Returns:**
- `list`: List of data rows

**Example:**
```python
from PTD_Gen.Final_study_specific_form import prepare_study_specific_forms_rows

rows = prepare_study_specific_forms_rows(
    json_file_path="ecrf.json",
    config_path="PTD_Gen/config/config_study_specific_forms.json"
)
```

## Configuration Files

### Form Extractor Configuration (`config_form_extractor.json`)

```json
{
  "visit_patterns": [
    "V\\d+[A-Z]*(?:-\\d+)?",
    "P\\d+[A-Z]*(?:-\\d+)?"
  ],
  "trigger_patterns": [
    "\\bform\\s+to\\s+be\\s+(dynamically\\s+)?triggered\\b"
  ],
  "source_classification": {
    "library_indicators": [
      "\\bstandard\\s+crf\\b"
    ],
    "new_indicators": [
      "\\bstudy[- ]specific\\b"
    ]
  }
}
```

### SoA Parser Configuration (`config_soa_parser.json`)

```json
{
  "visit_patterns": [
    "\\b(?:V|P)\\d+[A-Za-z]*\\b"
  ],
  "cell_markers": [
    "\\b(?:X|YES|Y)\\b"
  ],
  "header_keywords": [
    "visit",
    "screening"
  ]
}
```

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request format and required fields |
| 404 | Not Found | Verify endpoint URL and file paths |
| 500 | Internal Server Error | Check server logs and configuration |

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## CORS

CORS is enabled for all origins. For production, configure specific allowed origins.

---

**Last Updated**: 2025-01-27  
**Document Version**: 1.0.0  
**Maintainer**: Development Team