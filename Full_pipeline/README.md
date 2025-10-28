# Full Pipeline - Enhanced Backend-Frontend Integration

This project provides a comprehensive integration between a Flask backend and a modern frontend for PTD (Protocol Trial Design) generation with **full document processing pipeline**.

## 🚀 Enhanced Features

- **Complete Document Processing**: DOC/DOCX → PDF → Text Extraction → JSON Structuring → PTD Generation
- **Adobe PDF Services Integration**: Professional PDF text extraction and table processing
- **Real-time Progress Tracking**: Frontend shows processing steps in real-time
- **Template-based PTD Generation**: Uses Excel templates for professional output
- **File Upload & Download**: Seamless file handling with drag-and-drop interface

## Project Structure

```
Full_pipeline/
├── app.py                    # Enhanced Flask backend with full pipeline
├── frontend/                 # Modern frontend interface
│   ├── index.html           # Main UI with drag-and-drop
│   ├── script.js            # Frontend with backend integration
│   └── styles.css           # Modern styling
├── backend/                  # Backend processing modules
│   ├── json_struct_protocol.py    # Protocol JSON structuring
│   ├── json_struct_ecrf.py        # eCRF JSON structuring
│   ├── doc_to_pdf.py              # DOC/DOCX to PDF conversion
│   ├── simpletext_extract.py      # PDF text extraction (Adobe Services)
│   └── PTD_Gen/                   # PTD generation with templates
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

### 2. Configure Adobe PDF Services (Optional but Recommended)

For full PDF processing capabilities:

```bash
export PDF_SERVICES_CLIENT_ID=your_client_id
export PDF_SERVICES_CLIENT_SECRET=your_client_secret
```

**Note**: Without Adobe credentials, the system will show warnings but still function for basic operations.

### 3. Start the Backend

```bash
# From the Full_pipeline directory
python3 app.py
```

The Flask server will start at `http://127.0.0.1:5000`

### 4. Open the Frontend

Open `frontend/index.html` in your web browser, or serve it through a local web server.

## 🔄 Complete Processing Pipeline

The enhanced integration provides a **complete end-to-end pipeline**:

### 1. **File Upload**
- Supports PDF, DOC, DOCX, and JSON files
- Drag-and-drop interface
- File validation and preview

### 2. **Document Conversion** (if needed)
- DOC/DOCX → PDF conversion using Adobe Services
- Automatic format detection and conversion

### 3. **Text Extraction**
- PDF → Structured JSON extraction
- Uses Adobe PDF Services for professional text and table extraction
- Generates `structuredData.json` files

### 4. **JSON Processing**
- Protocol JSON structuring using `json_struct_protocol.py`
- eCRF JSON structuring using `json_struct_ecrf.py`
- Data validation and formatting

### 5. **PTD Generation**
- Template-based Excel generation
- Schedule Grid creation
- Study Specific Forms generation
- Professional formatting and styling

### 6. **File Download**
- Generated PTD files available for download
- Proper file naming and formatting

## API Endpoints

- `GET /` - API information and available endpoints
- `GET /status` - Server status, Adobe credentials check, and health info
- `GET /health` - Basic health check with Adobe API status
- `POST /run_pipeline` - **Complete pipeline processing** (files → PTD)
- `POST /run_ptd_generation` - Direct PTD generation from JSON data
- `GET /download/<filename>` - Download generated files

## Usage Examples

### Complete Pipeline (Recommended)

1. **Upload Files**: Drag and drop Protocol and CRF documents
2. **Automatic Processing**: System handles conversion, extraction, and structuring
3. **PTD Generation**: Creates professional Excel output with templates
4. **Download Results**: Get the generated PTD file

### Direct JSON Processing

If you already have structured JSON data:

```bash
curl -X POST http://127.0.0.1:5000/run_ptd_generation \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_json": {...},
    "ecrf_json": {...}
  }'
```

## Configuration

### Environment Variables

```bash
# Adobe PDF Services (for full functionality)
export PDF_SERVICES_CLIENT_ID=your_client_id
export PDF_SERVICES_CLIENT_SECRET=your_client_secret
```

### File Locations

- **Uploads**: `uploads/` directory (created automatically)
- **Outputs**: `output/` directory (created automatically)
- **Templates**: `backend/templates/` (for PTD generation)
- **Logs**: Console output with detailed processing information

## Advanced Features

### Template-based PTD Generation

The system uses Excel templates for professional PTD output:
- Template location: `backend/templates/PTD Template v.2_Draft (1).xlsx`
- Preserves existing formatting and styles
- Replaces specific sheets with generated content

### Session Management

- Each processing session gets a unique temporary directory
- Automatic cleanup after processing
- Detailed logging for debugging

### Error Handling

- Comprehensive error messages
- Graceful fallbacks for missing dependencies
- Detailed logging for troubleshooting

## Troubleshooting

### Common Issues

1. **Adobe Credentials Missing**:
   ```
   WARNING: Adobe PDF Services credentials not set!
   ```
   - Set the environment variables or use JSON input mode

2. **Template Not Found**:
   ```
   ERROR: Template file not found
   ```
   - Ensure template exists in `backend/templates/`
   - Or modify template path in `app.py`

3. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path and module locations

4. **File Upload Issues**:
   - Check file permissions
   - Verify file formats are supported
   - Ensure sufficient disk space

### Debug Mode

The Flask app runs in debug mode by default, providing:
- Detailed error messages
- Automatic reloading on code changes
- Interactive debugger for errors

## Development

### Backend Development

The enhanced Flask app (`app.py`) includes:
- Complete file processing pipeline
- Adobe PDF Services integration
- Template-based PTD generation
- Comprehensive error handling
- Session management and cleanup

### Frontend Development

The frontend (`frontend/script.js`) provides:
- Modern drag-and-drop interface
- Real-time progress indicators
- Backend API integration
- Error handling and user feedback
- Professional UI/UX

## Performance Notes

- **File Processing**: Large files may take time to process
- **Memory Usage**: Processing creates temporary files that are cleaned up
- **Adobe Services**: Requires internet connection for PDF processing
- **Template Loading**: First PTD generation may be slower due to template loading

## Security Considerations

- File uploads are validated and sanitized
- Temporary files are automatically cleaned up
- No persistent storage of uploaded files
- Adobe credentials should be kept secure

---

## 🎯 **Ready to Use!**

The enhanced integration is now complete with full document processing capabilities. Simply start the backend and open the frontend to begin processing documents through the complete pipeline!