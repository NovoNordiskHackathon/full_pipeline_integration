# PTD Generator - Presentation Outline

## Slide 1: Title Slide
**Title**: PTD Generator
**Subtitle**: Automated Protocol Translation Document Generation
**Tagline**: Transform Protocol and CRF documents into structured PTD files using AI-powered processing

**Speaker Notes**: 
- Welcome to the PTD Generator presentation
- This system automates the creation of Protocol Translation Documents from clinical trial documents
- Combines AI-powered text extraction with structured data processing

## Slide 2: Project Overview
**Title**: What is PTD Generator?

**Bullet Points**:
- **Purpose**: Transform Protocol PDFs and eCRF documents into structured PTD files
- **Technology**: AI-powered text extraction + hierarchical document structuring
- **Output**: Standardized Excel files with Schedule Grid and Study Specific Forms
- **Target Users**: Clinical research teams, data managers, protocol developers

**Speaker Notes**:
- PTD Generator solves the manual, time-consuming process of creating Protocol Translation Documents
- Uses advanced AI to extract and structure data from complex clinical documents
- Produces standardized outputs that integrate with existing clinical data management systems

## Slide 3: High-Level Architecture
**Title**: System Architecture

**ASCII Diagram**:
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
```

**Speaker Notes**:
- Three-layer architecture: Frontend, API, and Processing Pipeline
- Flask API serves as the communication layer between web interface and processing modules
- Modular design allows for easy maintenance and feature additions

## Slide 4: Repository Layout
**Title**: Project Structure

**File Tree**:
```
Full_pipeline/
├── app.py                          # Main Flask application
├── frontend/                       # Web interface
│   ├── index.html                  # Main HTML page
│   ├── script.js                   # Frontend JavaScript
│   └── styles.css                  # CSS styling
├── PTD_Gen/                        # Core PTD generation
│   ├── generate_ptd.py             # Main orchestrator
│   ├── modules/                    # Processing modules
│   └── config/                     # Configuration files
└── docs/                           # Documentation
```

**Speaker Notes**:
- Clean, organized structure with clear separation of concerns
- Frontend handles user interaction, PTD_Gen contains core processing logic
- Comprehensive documentation for maintainability

## Slide 5: Key Modules - Form Extraction
**Title**: Form Extraction Module

**Responsibilities**:
- Extract form information from eCRF JSON files
- Classify form sources (Library, New, Reference Study)
- Identify dynamic triggers and required status
- Generate structured CSV output

**Configuration**: `config_form_extractor.json`
**Input**: eCRF JSON file
**Output**: Forms CSV with metadata

**Speaker Notes**:
- Uses pattern matching and AI to intelligently extract form information
- Automatically classifies forms based on naming conventions and context
- Handles complex eCRF structures with nested hierarchies

## Slide 6: Key Modules - Schedule Parsing
**Title**: Schedule of Activities Parser

**Responsibilities**:
- Parse schedule tables from protocol documents
- Extract visit patterns and procedures
- Create visit-procedure mapping matrix
- Handle complex table structures

**Configuration**: `config_soa_parser.json`
**Input**: Protocol JSON file
**Output**: Schedule CSV matrix

**Speaker Notes**:
- Intelligently identifies schedule tables in protocol documents
- Handles various visit naming conventions (V1, P1, S1D1, etc.)
- Robust parsing that works with different document formats

## Slide 7: Key Modules - PTD Generation
**Title**: PTD Generation Orchestrator

**Responsibilities**:
- Coordinate 5-stage processing pipeline
- Merge data from multiple sources
- Generate Excel output with two sheets
- Support multiple output modes (stream, surgery, fast)

**Features**:
- Template-based generation
- Memory-efficient processing
- Multiple output formats

**Speaker Notes**:
- Central orchestrator that coordinates all processing modules
- Supports different processing modes for various use cases
- Generates professional Excel outputs with proper formatting

## Slide 8: API Endpoints
**Title**: RESTful API Interface

**Key Endpoints**:
- `GET /status` - System status and health
- `POST /run_pipeline` - Main processing endpoint
- `POST /run_ptd_generation` - Full PTD generation
- `GET /download/<filename>` - File download

**Example cURL**:
```bash
curl -X POST http://localhost:5000/run_pipeline \
  -F "protocol_file=@protocol.pdf" \
  -F "crf_file=@crf.pdf"
```

**Speaker Notes**:
- RESTful API design for easy integration
- Supports both file upload and JSON data input
- Comprehensive error handling and status reporting

## Slide 9: Setup & Run
**Title**: Quick Setup and Running

**Setup Commands**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

**Access Points**:
- Frontend: http://localhost:5000
- API: http://localhost:5000/status

**Speaker Notes**:
- Simple setup process with minimal dependencies
- Runs on standard port 5000
- Easy to deploy and maintain

## Slide 10: Troubleshooting
**Title**: Common Issues and Solutions

**Top 5 Fixes**:
1. **ModuleNotFoundError**: Add current directory to PYTHONPATH
2. **Port Already in Use**: Kill existing process or use different port
3. **Missing Dependencies**: Reinstall requirements.txt
4. **File Not Found**: Check file paths and permissions
5. **JSON Decode Error**: Validate input JSON files

**Debug Commands**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
lsof -i :5000
python -m json.tool input.json
```

**Speaker Notes**:
- Common issues are well-documented with specific solutions
- Debug commands help identify and resolve problems quickly
- Comprehensive logging for troubleshooting

## Slide 11: Demo Flow
**Title**: Live Demo - PTD Generation

**Demo Steps**:
1. **Start Application**: `python app.py`
2. **Access Frontend**: Open http://localhost:5000
3. **Upload Files**: Drag and drop Protocol and CRF documents
4. **Process Documents**: Click "Generate PTD" button
5. **Monitor Progress**: Watch processing steps
6. **Download Result**: Get generated PTD Excel file

**Expected Output**:
- Schedule Grid sheet with visit-procedure matrix
- Study Specific Forms sheet with form details
- Professional formatting and styling

**Speaker Notes**:
- Live demonstration of the complete workflow
- Shows user-friendly interface and processing capabilities
- Demonstrates real-world usage scenarios

## Slide 12: Next Steps
**Title**: Future Enhancements

**Immediate Improvements**:
- Complete integration testing
- Enhanced error handling
- Input validation

**Short-term Goals**:
- Docker containerization
- CI/CD pipeline
- API documentation with Swagger

**Long-term Vision**:
- Microservices architecture
- Cloud deployment
- Machine learning enhancements

**Speaker Notes**:
- Clear roadmap for future development
- Focus on scalability and maintainability
- Community-driven development approach

## Slide 13: References and Resources
**Title**: Documentation and Support

**Documentation**:
- `docs/README_FULL.md` - Comprehensive documentation
- `docs/ARCHITECTURE.md` - System architecture
- `docs/API_REFERENCE.md` - API documentation
- `docs/QUICK_START.md` - Quick start guide

**Support**:
- GitHub repository with issue tracking
- Comprehensive troubleshooting guide
- Example configurations and templates

**Speaker Notes**:
- Extensive documentation for users and developers
- Multiple support channels for assistance
- Regular updates and community contributions

## Slide 14: Questions & Discussion
**Title**: Questions and Discussion

**Contact Information**:
- Repository: [GitHub Link]
- Documentation: `docs/` directory
- Issues: GitHub Issues tracker

**Discussion Topics**:
- Integration requirements
- Customization needs
- Performance considerations
- Deployment strategies

**Speaker Notes**:
- Open floor for questions and discussion
- Address specific use cases and requirements
- Gather feedback for future improvements