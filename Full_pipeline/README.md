# Full Pipeline - Integrated Backend-Frontend

This project provides a complete integration between a Flask backend and a modern frontend for PTD (Protocol Trial Design) generation.

## Project Structure

```
Full_pipeline/
├── app.py                    # Flask backend server (main entry point)
├── frontend/                 # Static frontend files
│   ├── index.html           # Main UI
│   ├── script.js            # Frontend JavaScript with backend integration
│   └── styles.css           # Styling
├── backend/                  # Backend processing modules
│   ├── json_struct_protocol.py    # Protocol JSON structuring
│   ├── json_struct_ecrf.py        # eCRF JSON structuring
│   ├── doc_to_pdf.py              # Document conversion utilities
│   ├── simpletext_extract.py      # Text extraction utilities
│   └── PTD_Gen/                   # PTD generation modules
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Start the Backend

```bash
# From the Full_pipeline directory
python app.py
```

The Flask server will start at `http://127.0.0.1:5000`

### 3. Open the Frontend

Open `frontend/index.html` in your web browser, or serve it through a local web server.

## API Endpoints

- `GET /` - API information and available endpoints
- `GET /status` - Server status and health check
- `GET /health` - Basic health check
- `POST /run_pipeline` - Process uploaded files or JSON data
- `POST /run_ptd_generation` - Generate PTD from structured JSON
- `GET /download/<filename>` - Download generated files

## Usage

1. **Upload Files**: Use the frontend to upload Protocol and CRF documents
2. **Process**: The system will process the files through the backend pipeline
3. **Generate**: Create PTD output files
4. **Download**: Download the generated results

## Backend Processing Pipeline

1. **File Upload**: Accepts PDF, DOC, DOCX, and JSON files
2. **JSON Structuring**: Processes protocol and eCRF JSON data
3. **PTD Generation**: Creates Excel output using the PTD_Gen modules
4. **File Download**: Provides download links for generated files

## Configuration

### Environment Variables (Optional)

For PDF Services integration:
```bash
export PDF_SERVICES_CLIENT_ID=your_client_id
export PDF_SERVICES_CLIENT_SECRET=your_client_secret
```

### File Locations

- **Uploads**: `uploads/` directory (created automatically)
- **Outputs**: `output/` directory (created automatically)
- **Logs**: Console output and Flask logging

## Development

### Backend Development

The Flask app (`app.py`) integrates with existing backend modules:
- Imports from `backend/` directory
- Uses existing JSON structuring functions
- Calls PTD generation CLI tools
- Handles file uploads and downloads

### Frontend Development

The frontend (`frontend/script.js`) provides:
- File upload with drag-and-drop
- Real-time progress indicators
- Backend API integration via fetch()
- Modern UI with toast notifications

## Troubleshooting

1. **Port Already in Use**: Change the port in `app.py` (line: `app.run(debug=True, host="0.0.0.0", port=5000)`)
2. **CORS Issues**: The app includes `flask-cors` for cross-origin requests
3. **File Upload Errors**: Check file permissions and disk space
4. **Module Import Errors**: Ensure all dependencies are installed and paths are correct

## Notes

- The integration maintains the same functionality as the original pipeline
- PDF/DOC conversion is not yet implemented in the web interface
- For full file processing, use the command-line scripts in the project
- The frontend communicates with the backend via HTTP API calls