# PTD Generator - Full Pipeline Integration

A full-stack web application that integrates Python backend processing with a modern frontend UI for generating Protocol Translation Documents (PTD).

## Project Structure

```
full_pipeline_integration/
├── backend/
│   ├── app.py                    # Flask backend server
│   ├── json_struct_protocol.py  # Protocol JSON processing
│   ├── json_struct_ecrf.py      # eCRF JSON processing
│   ├── generate_ptd.py          # PTD generation script
│   ├── modules/                 # PTD generation modules
│   └── config/                  # Configuration files
├── frontend/
│   ├── index.html               # Main web interface
│   ├── script.js                # Frontend JavaScript
│   └── styles.css               # Styling
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Features

- **Modern Web UI**: Clean, responsive interface with drag-and-drop file upload
- **REST API Backend**: Flask-based API with CORS support
- **Document Processing**: JSON structuring and PTD generation
- **Real-time Progress**: Visual progress indicators during processing
- **File Management**: Secure file upload and download handling

## Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation

1. **Clone or download the repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the environment**:
   ```bash
   # Create necessary directories
   mkdir -p uploads output
   ```

## Running the Application

### Backend (Flask Server)

1. **Start the Flask backend**:
   ```bash
   python app.py
   ```
   
   The backend will start on `http://localhost:5000`

2. **Verify the backend is running**:
   ```bash
   curl http://localhost:5000/status
   ```

### Frontend (Web Interface)

1. **Open the web interface**:
   - Navigate to `frontend/index.html` in your web browser
   - Or serve it using a local web server:
     ```bash
     # Using Python's built-in server
     cd frontend
     python -m http.server 8000
     # Then open http://localhost:8000
     ```

## API Endpoints

### GET /status
Returns the current system status and available endpoints.

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

### POST /run_pipeline
Processes uploaded files or JSON data through the pipeline.

**Request** (file upload):
- `protocol_file`: Protocol document file
- `crf_file`: CRF document file

**Request** (JSON data):
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
  "message": "Pipeline processing completed successfully",
  "results": {
    "structured_protocol": { /* processed protocol data */ },
    "structured_ecrf": { /* processed eCRF data */ },
    "processing_steps": ["Step 1", "Step 2", "Step 3"]
  }
}
```

### GET /health
Health check endpoint for monitoring.

## Usage

1. **Upload Documents**:
   - Drag and drop files onto the upload area
   - Or click to browse and select files
   - Supported formats: PDF, DOC, DOCX, JSON

2. **Generate PTD**:
   - Click the "Generate PTD" button
   - Watch the progress indicator
   - Download the generated PTD file

3. **Reset and Try Again**:
   - Use the "Generate Another" button to start over

## Development

### Backend Development

The Flask app (`app.py`) handles:
- File uploads and validation
- JSON data processing
- Integration with existing Python scripts
- CORS configuration for frontend communication

### Frontend Development

The frontend (`frontend/script.js`) provides:
- File upload interface with drag-and-drop
- Progress visualization
- API communication with the backend
- Error handling and user feedback

### Adding New Features

1. **Backend**: Add new routes in `app.py`
2. **Frontend**: Update `script.js` to call new endpoints
3. **Processing**: Add new Python scripts in the `backend/` directory

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure the Flask backend is running
   - Check that CORS is properly configured

2. **File Upload Issues**:
   - Verify file formats are supported
   - Check file size limits

3. **Processing Errors**:
   - Check the Flask logs for detailed error messages
   - Ensure all dependencies are installed

### Logs

Backend logs are available in the console where Flask is running. For production, consider using a proper logging configuration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue in the repository