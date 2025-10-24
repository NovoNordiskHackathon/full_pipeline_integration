# PTD Generator - Full Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Repository Layout](#repository-layout)
3. [Architecture](#architecture)
4. [Module Descriptions](#module-descriptions)
5. [API Endpoints](#api-endpoints)
6. [Setup & Installation](#setup--installation)
7. [Running the Application](#running-the-application)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Migration Notes](#migration-notes)
11. [Quick Reference](#quick-reference)
12. [Changelog](#changelog)
13. [Next Steps](#next-steps)
14. [License](#license)

## Project Overview

The **PTD Generator** is a comprehensive document processing pipeline that transforms Protocol and Case Report Form (CRF) documents into structured Protocol Translation Documents (PTD). The system combines AI-powered text extraction, hierarchical document structuring, and automated Excel generation to create standardized PTD files for clinical research.

### Purpose
- **Input**: Protocol PDFs and eCRF documents
- **Processing**: AI-powered text extraction, document structuring, and data analysis
- **Output**: Structured Excel files with Schedule Grid and Study Specific Forms

### High-Level Description
The system processes clinical trial documents through a multi-stage pipeline:
1. **Document Conversion**: PDF/DOC to structured JSON
2. **Hierarchical Structuring**: Organize content into logical hierarchies
3. **Data Extraction**: Extract forms, schedules, and metadata
4. **PTD Generation**: Create standardized Excel outputs
5. **Web Interface**: User-friendly frontend for document upload and processing

## Repository Layout

```
Full_pipeline/
├── app.py                          # Main Flask application (backend API)
├── requirements.txt                # Python dependencies
├── frontend/                       # Web interface
│   ├── index.html                  # Main HTML page
│   ├── script.js                   # Frontend JavaScript logic
│   └── styles.css                  # CSS styling
├── PTD_Gen/                        # Core PTD generation modules
│   ├── generate_ptd.py             # Main PTD generation orchestrator
│   ├── Final_study_specific_form.py # Study-specific forms generator
│   ├── modules/                    # Processing modules
│   │   ├── form_extractor.py       # Extract forms from eCRF
│   │   ├── soa_parser.py          # Parse schedule of activities
│   │   ├── common_matrix.py       # Merge common data matrix
│   │   ├── event_grouping.py      # Group events by visits
│   │   └── schedule_layout.py     # Generate schedule grid layout
│   └── config/                     # Configuration files
│       ├── config_form_extractor.json
│       ├── config_soa_parser.json
│       ├── config_common_matrix.json
│       ├── config_event_grouping.json
│       ├── config_schedule_layout.json
│       └── config_study_specific_forms.json
├── json_struct_protocol.py         # Protocol document structuring
├── json_struct_ecrf.py             # eCRF document structuring
├── doc_to_pdf.py                   # Document conversion utilities
├── simpletext_extract.py           # Text extraction from PDFs
├── run_extraction.sh               # Extraction pipeline script
├── start_backend.sh                # Backend startup script
├── conversion_run.sh               # Document conversion script
└── docs/                           # Documentation (this directory)
    ├── README_FULL.md              # This file
    ├── ARCHITECTURE.md             # Architecture documentation
    ├── API_REFERENCE.md            # API endpoint reference
    └── QUICK_START.md              # Quick start guide
```

## Architecture

### System Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   PTD Pipeline  │
│   (HTML/JS)     │◄──►│   (app.py)      │◄──►│   (PTD_Gen/)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   Modules       │
         │                       │              │   - form_extractor
         │                       │              │   - soa_parser
         │                       │              │   - common_matrix
         │                       │              │   - event_grouping
         │                       │              │   - schedule_layout
         │                       │              └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   Config Files  │
         │                       │              │   (JSON)        │
         │                       │              └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   File Upload   │    │   JSON Output   │
│   (PDF/DOC)     │    │   (Structured)  │
└─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Upload**: User uploads Protocol PDF and eCRF documents via web interface
2. **Conversion**: Documents are converted to structured JSON format
3. **Structuring**: JSON files are processed through hierarchical structuring
4. **Extraction**: Forms and schedules are extracted using specialized modules
5. **Processing**: Data is merged, grouped, and formatted
6. **Generation**: Final PTD Excel file is generated with two sheets:
   - Schedule Grid (from protocol + eCRF)
   - Study Specific Forms (from eCRF)
7. **Download**: User downloads the generated PTD file

## Module Descriptions

### Backend Modules (`PTD_Gen/modules/`)

#### `form_extractor.py`
**Purpose**: Extract form information from eCRF JSON files
**Main Functions**:
- `extract_forms(ecrf_json, output_csv, config)`: Main extraction function
- `extract_forms_with_corrections(data, config)`: Enhanced extraction with corrections
- `determine_form_source(form_name, form_text, context_text, document_context, config)`: Classify form sources
- `is_valid_form_name(text, config)`: Validate form names using patterns

**Inputs**: eCRF JSON file, configuration dictionary
**Outputs**: CSV file with form details (Form Label, Form Name, Source, Visits, Dynamic Trigger, Required status)
**Configuration**: `config_form_extractor.json`

#### `soa_parser.py`
**Purpose**: Parse schedule of activities from protocol JSON files
**Main Functions**:
- `parse_soa(protocol_json, output_csv, config)`: Main parsing function
- `parse_protocol_schedule(protocol_data, config)`: Extract visit-procedure mappings
- `find_all_schedule_tables(root, config)`: Locate schedule tables in document
- `detect_visit_header_row(all_rows, config)`: Identify visit header rows

**Inputs**: Protocol JSON file, configuration dictionary
**Outputs**: CSV file with schedule matrix (procedures × visits)
**Configuration**: `config_soa_parser.json`

#### `common_matrix.py`
**Purpose**: Merge common data matrix from forms and schedule
**Main Functions**:
- `merge_common_matrix(ecrf_csv, schedule_csv, output_csv, config)`: Merge data sources
**Inputs**: Forms CSV, Schedule CSV, configuration
**Outputs**: Merged matrix CSV
**Configuration**: `config_common_matrix.json`

#### `event_grouping.py`
**Purpose**: Group events by visits and create visit structure
**Main Functions**:
- `group_events(protocol_json, output_xlsx, config)`: Group events by visits
**Inputs**: Protocol JSON, configuration
**Outputs**: Visits Excel file
**Configuration**: `config_event_grouping.json`

#### `schedule_layout.py`
**Purpose**: Generate final schedule grid layout
**Main Functions**:
- `generate_schedule_grid(visits_xlsx, forms_csv, output_xlsx, config)`: Create schedule grid
- `generate_schedule_grid_stream(visits_xlsx, forms_csv, workbook, sheet_name, config)`: Stream-based generation
**Inputs**: Visits Excel, Forms CSV, configuration
**Outputs**: Schedule Grid Excel file
**Configuration**: `config_schedule_layout.json`

### Core Processing Files

#### `generate_ptd.py`
**Purpose**: Main PTD generation orchestrator
**Main Functions**:
- `main()`: CLI entry point with argument parsing
- `run_schedule_grid_pipeline()`: Execute 5-stage pipeline
- `generate_study_specific_forms_xlsx()`: Generate study-specific forms
- `replace_sheets_in_template()`: Replace sheets in template workbook

**Key Features**:
- Multiple output modes: `--stream`, `--surgery`, `--fast`
- Template-based generation with sheet replacement
- Memory-efficient processing for large documents

#### `Final_study_specific_form.py`
**Purpose**: Generate study-specific forms Excel sheet
**Main Functions**:
- `process_clinical_forms(ecrf_json, output_csv_path, config_path)`: Process forms
- `prepare_study_specific_forms_rows(json_file_path, config_path)`: Prepare data rows
- `write_study_specific_forms_stream(rows, workbook, sheet_name)`: Stream to workbook

### Frontend Files

#### `index.html`
**Purpose**: Main web interface
**Features**:
- Drag-and-drop file upload
- Progress tracking with animated steps
- Download interface for generated files
- Responsive design with modern UI

#### `script.js`
**Purpose**: Frontend JavaScript logic
**Main Classes**:
- `PTDGenerator`: Main application class
**Key Functions**:
- `generatePTD()`: Initiate PTD generation
- `callBackendAPI()`: Communicate with Flask backend
- `setupDragAndDrop()`: Handle file uploads
- `showProgressSection()`: Display processing progress

#### `styles.css`
**Purpose**: CSS styling and theming
**Features**:
- Modern blue/purple color scheme
- Responsive design
- Animation effects
- Professional UI components

## API Endpoints

### Base URL
```
http://localhost:5000
```

### Endpoints

#### `GET /`
**Purpose**: Home page with API information
**Response**:
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

#### `GET /status`
**Purpose**: Get current system status
**Response**:
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

#### `GET /health`
**Purpose**: Health check endpoint
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "/workspace/Full_pipeline"
}
```

#### `POST /run_pipeline`
**Purpose**: Main pipeline endpoint for file processing
**Request Types**:
1. **File Upload** (multipart/form-data):
   - `protocol_file`: Protocol document (PDF/DOC/DOCX)
   - `crf_file`: CRF document (PDF/DOC/DOCX)

2. **JSON Data** (application/json):
   ```json
   {
     "protocol_json": { /* structured protocol data */ },
     "ecrf_json": { /* structured eCRF data */ }
   }
   ```

**Response (File Upload)**:
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

**Response (JSON Processing)**:
```json
{
  "success": true,
  "message": "Pipeline processing completed successfully",
  "results": {
    "structured_protocol": { /* processed protocol data */ },
    "structured_ecrf": { /* processed eCRF data */ },
    "processing_steps": [
      "Protocol JSON structured",
      "eCRF JSON structured",
      "Ready for PTD generation"
    ]
  }
}
```

#### `POST /run_ptd_generation`
**Purpose**: Run full PTD generation pipeline
**Request**:
```json
{
  "protocol_json": { /* structured protocol data */ },
  "ecrf_json": { /* structured eCRF data */ }
}
```

**Response**:
```json
{
  "success": true,
  "message": "PTD generation completed",
  "output_file": "ptd_output.xlsx",
  "download_url": "/download/ptd_output.xlsx"
}
```

#### `GET /download/<filename>`
**Purpose**: Download generated files
**Response**: File download or 404 error

### Example cURL Commands

#### Check API Status
```bash
curl -X GET http://localhost:5000/status
```

#### Upload Files
```bash
curl -X POST http://localhost:5000/run_pipeline \
  -F "protocol_file=@protocol.pdf" \
  -F "crf_file=@crf.pdf"
```

#### Process JSON Data
```bash
curl -X POST http://localhost:5000/run_pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_json": { "elements": [...] },
    "ecrf_json": { "elements": [...] }
  }'
```

#### Generate PTD
```bash
curl -X POST http://localhost:5000/run_ptd_generation \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_json": { "elements": [...] },
    "ecrf_json": { "elements": [...] }
  }'
```

## Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Virtual Environment Setup

#### Using venv (recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### Using conda (alternative)
```bash
# Create conda environment
conda create -n ptd-generator python=3.9

# Activate environment
conda activate ptd-generator
```

### Install Dependencies

#### Root Dependencies
```bash
pip install -r requirements.txt
```

#### Backend Dependencies (if separate)
```bash
pip install -r PTD_Gen/requirements.txt
```

### Dependencies List
From `requirements.txt`:
```
pandas>=2.0.0
openpyxl>=3.1.2
xlsxwriter>=3.2.0
pdfservices-sdk
flask>=2.3.0
flask-cors>=4.0.0
werkzeug>=2.3.0
```

From `PTD_Gen/requirements.txt`:
```
openpyxl>=3.1.2
xlsxwriter>=3.2.0
pandas>=2.0.0
```

### Environment Variables
Create a `.env` file in the project root:
```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True

# Server Configuration
HOST=0.0.0.0
PORT=5000

# File Upload Configuration
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=output
MAX_CONTENT_LENGTH=16777216  # 16MB

# Logging
LOG_LEVEL=INFO
LOG_FILE=ptd_generation.log
```

### Default Ports
- **Backend API**: 5000
- **Frontend**: Served by Flask (static files)

## Running the Application

### Development Mode

#### Start Backend Server
```bash
# From project root
python app.py
```

#### Using Shell Scripts
```bash
# Start backend
./start_backend.sh

# Run extraction pipeline
./run_extraction.sh

# Run document conversion
./conversion_run.sh
```

#### Manual Module Execution
```bash
# Run protocol structuring
python json_struct_protocol.py input_protocol.json

# Run eCRF structuring  
python json_struct_ecrf.py input_ecrf.json

# Run PTD generation
python PTD_Gen/generate_ptd.py --ecrf ecrf.json --protocol protocol.json --out ptd_output.xlsx
```

### Production Mode

#### Using Gunicorn (recommended)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Using uWSGI
```bash
pip install uwsgi
uwsgi --http :5000 --wsgi-file app.py --callable app
```

### Accessing the Application
1. **Backend API**: http://localhost:5000
2. **Frontend Interface**: http://localhost:5000 (served by Flask)
3. **API Documentation**: http://localhost:5000/ (shows available endpoints)

## Testing

### Basic Smoke Tests

#### Test Backend API
```bash
# Test status endpoint
curl -X GET http://localhost:5000/status

# Test health endpoint
curl -X GET http://localhost:5000/health
```

#### Test File Upload
```bash
# Test file upload (replace with actual files)
curl -X POST http://localhost:5000/run_pipeline \
  -F "protocol_file=@test_protocol.pdf" \
  -F "crf_file=@test_crf.pdf"
```

#### Test JSON Processing
```bash
# Test JSON processing
curl -X POST http://localhost:5000/run_pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_json": {"elements": []},
    "ecrf_json": {"elements": []}
  }'
```

### Adding Unit Tests

Create `tests/` directory and add test files:

#### `tests/test_api.py`
```python
import unittest
import json
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_status_endpoint(self):
        response = self.app.get('/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'running')

    def test_health_endpoint(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

if __name__ == '__main__':
    unittest.main()
```

#### Run Tests
```bash
python -m pytest tests/
# or
python tests/test_api.py
```

## Troubleshooting

### Common Errors and Fixes

#### 1. ModuleNotFoundError: No module named 'modules'
**Error**: `ModuleNotFoundError: No module named 'modules'`
**Cause**: Python path not configured correctly
**Fix**:
```bash
# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run as module
python -m PTD_Gen.generate_ptd --ecrf ecrf.json --protocol protocol.json --out output.xlsx
```

#### 2. ImportError: No module named 'flask'
**Error**: `ImportError: No module named 'flask'`
**Cause**: Flask not installed or virtual environment not activated
**Fix**:
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. PermissionError: [Errno 13] Permission denied
**Error**: `PermissionError: [Errno 13] Permission denied`
**Cause**: Insufficient permissions for file operations
**Fix**:
```bash
# Make scripts executable
chmod +x *.sh

# Check file permissions
ls -la uploads/ output/
```

#### 4. FileNotFoundError: [Errno 2] No such file or directory
**Error**: `FileNotFoundError: [Errno 2] No such file or directory`
**Cause**: Missing input files or incorrect paths
**Fix**:
```bash
# Check if files exist
ls -la uploads/
ls -la output/

# Create missing directories
mkdir -p uploads output
```

#### 5. JSONDecodeError: Expecting value
**Error**: `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`
**Cause**: Invalid JSON file or empty file
**Fix**:
```bash
# Validate JSON files
python -m json.tool input_file.json

# Check file content
head -5 input_file.json
```

#### 6. CORS Error in Browser
**Error**: `Access to fetch at 'http://localhost:5000' from origin 'http://localhost:3000' has been blocked by CORS policy`
**Cause**: CORS not configured properly
**Fix**: CORS is already configured in `app.py` with `CORS(app)`

#### 7. Port Already in Use
**Error**: `OSError: [Errno 48] Address already in use`
**Cause**: Port 5000 already occupied
**Fix**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use different port
python app.py --port 5001
```

### Debug Mode
Enable debug mode for detailed error information:
```bash
export FLASK_DEBUG=1
python app.py
```

### Log Files
Check log files for detailed error information:
```bash
# Main log file
tail -f ptd_generation.log

# Flask logs (if using gunicorn)
tail -f gunicorn.log
```

## Migration Notes

### Differences Between `Full_pipeline (Copy)` and `Full_pipeline`

#### Integration Points to Recreate

1. **Backend Integration**:
   - `Full_pipeline (Copy)` has complete Flask integration in `app.py`
   - `Full_pipeline` has updated `app.py` but may need additional endpoints
   - **Action**: Copy missing endpoints from `Full_pipeline (Copy)/app.py`

2. **Module Structure**:
   - `Full_pipeline (Copy)` has modules in `backend/modules/`
   - `Full_pipeline` has modules in `PTD_Gen/modules/`
   - **Action**: Update import paths in `app.py`

3. **Configuration Files**:
   - `Full_pipeline (Copy)` has configs in `backend/config/`
   - `Full_pipeline` has configs in `PTD_Gen/config/`
   - **Action**: Update config paths in module calls

4. **Frontend Integration**:
   - Both have similar frontend files
   - **Action**: Verify API endpoint URLs in `script.js`

#### Required Changes for Full Integration

1. **Update Import Paths in `app.py`**:
```python
# Change from:
from backend.json_struct_protocol import run_hierarchy as process_protocol
from backend.json_struct_ecrf import run_hierarchy as process_ecrf
from backend.generate_ptd import main as generate_ptd_main

# To:
from json_struct_protocol import run_hierarchy as process_protocol
from json_struct_ecrf import run_hierarchy as process_ecrf
from PTD_Gen.generate_ptd import main as generate_ptd_main
```

2. **Update Config Paths**:
```python
# Change config directory path
config_dir = os.path.join(os.path.dirname(__file__), "PTD_Gen", "config")
```

3. **Update Frontend API URLs**:
```javascript
// In script.js, update API endpoint
const uploadResponse = await fetch('http://localhost:5000/run_pipeline', {
```

## Quick Reference

### Essential Commands

#### Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

#### Running
```bash
# Start backend
python app.py

# Run PTD generation
python PTD_Gen/generate_ptd.py --ecrf ecrf.json --protocol protocol.json --out output.xlsx

# Run extraction pipeline
./run_extraction.sh
```

#### Testing
```bash
# Test API
curl -X GET http://localhost:5000/status

# Test file upload
curl -X POST http://localhost:5000/run_pipeline -F "protocol_file=@protocol.pdf" -F "crf_file=@crf.pdf"
```

#### Debugging
```bash
# Check logs
tail -f ptd_generation.log

# Validate JSON
python -m json.tool input.json

# Check Python path
python -c "import sys; print(sys.path)"
```

### File Locations
- **Main App**: `app.py`
- **Frontend**: `frontend/`
- **PTD Modules**: `PTD_Gen/`
- **Configs**: `PTD_Gen/config/`
- **Logs**: `ptd_generation.log`
- **Uploads**: `uploads/`
- **Outputs**: `output/`

### Key Configuration Files
- `PTD_Gen/config/config_form_extractor.json`: Form extraction rules
- `PTD_Gen/config/config_soa_parser.json`: Schedule parsing rules
- `PTD_Gen/config/config_common_matrix.json`: Matrix merging rules
- `PTD_Gen/config/config_event_grouping.json`: Event grouping rules
- `PTD_Gen/config/config_schedule_layout.json`: Schedule layout rules
- `PTD_Gen/config/config_study_specific_forms.json`: Forms generation rules

## Changelog

### Version 1.0.0 (Current)
- **Date**: 2025-01-27
- **Author**: Development Team
- **Changes**:
  - Initial release of PTD Generator
  - Complete Flask backend integration
  - Modern web frontend interface
  - 5-stage PTD generation pipeline
  - Comprehensive configuration system
  - Document conversion utilities
  - Excel generation with template support

### Version 0.9.0 (Pre-release)
- **Date**: 2025-01-20
- **Author**: Development Team
- **Changes**:
  - Core PTD generation modules
  - Basic document structuring
  - Initial API endpoints
  - Configuration file system

### Planned Updates
- **Version 1.1.0**: Enhanced PDF processing, Docker support
- **Version 1.2.0**: User authentication, batch processing
- **Version 1.3.0**: Advanced analytics, reporting features

## Next Steps

### Immediate Improvements
1. **Complete Integration**: Ensure all endpoints from `Full_pipeline (Copy)` are working
2. **Error Handling**: Add comprehensive error handling and user feedback
3. **Validation**: Add input validation for uploaded files
4. **Testing**: Implement comprehensive test suite

### Short-term Goals (1-3 months)
1. **Docker Support**: Create Dockerfile and docker-compose.yml
2. **CI/CD Pipeline**: Set up GitHub Actions for automated testing
3. **Documentation**: Add API documentation with Swagger/OpenAPI
4. **Performance**: Optimize for large document processing

### Medium-term Goals (3-6 months)
1. **User Authentication**: Add user management and session handling
2. **Batch Processing**: Support multiple document processing
3. **Cloud Deployment**: Deploy to AWS/Azure/GCP
4. **Monitoring**: Add application monitoring and logging

### Long-term Goals (6+ months)
1. **Microservices**: Split into microservices architecture
2. **Machine Learning**: Add ML-based document analysis
3. **API Gateway**: Implement API gateway for scalability
4. **Multi-tenancy**: Support multiple organizations

### Technical Debt
1. **Code Refactoring**: Improve code organization and modularity
2. **Error Recovery**: Add robust error recovery mechanisms
3. **Memory Management**: Optimize memory usage for large files
4. **Security**: Implement security best practices

## License

### Current Status
This project currently does not have a formal license. 

### Recommended License
We recommend using the **MIT License** for this project:

```
MIT License

Copyright (c) 2025 PTD Generator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### License Customization
To customize the license:
1. Copy the MIT License text above
2. Replace "PTD Generator" with your organization name
3. Update the copyright year as needed
4. Save as `LICENSE` file in the project root
5. Update this documentation with the actual license information

---

**Last Updated**: 2025-01-27  
**Document Version**: 1.0.0  
**Maintainer**: Development Team