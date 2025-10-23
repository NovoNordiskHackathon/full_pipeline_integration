# PTD Generator - Architecture Documentation

## Overview

The PTD Generator follows a modular, pipeline-based architecture designed to process clinical trial documents through multiple stages of transformation, from raw PDFs to structured Excel outputs.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (HTML/JS/CSS)  │  API Gateway (Flask)  │  File System │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Processing Pipeline                        │
├─────────────────────────────────────────────────────────────────┤
│  Document Conversion  │  Structuring  │  Extraction  │  Generation │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Module Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  form_extractor  │  soa_parser  │  common_matrix  │  event_grouping │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Configuration Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  JSON Config Files  │  Template Files  │  Logging Configuration │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Component Architecture

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

## Data Flow Architecture

### 1. Document Input Flow

```
User Upload
    │
    ▼
┌─────────────────┐
│   File Upload   │
│   (PDF/DOC)     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Document       │
│  Conversion     │
│  (doc_to_pdf)   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Text           │
│  Extraction     │
│  (simpletext)   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Structured     │
│  JSON           │
└─────────────────┘
```

### 2. Processing Pipeline Flow

```
Structured JSON
    │
    ▼
┌─────────────────┐
│  Hierarchical   │
│  Structuring    │
│  (json_struct)  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Form           │
│  Extraction     │
│  (form_extractor)│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Schedule       │
│  Parsing        │
│  (soa_parser)   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Matrix         │
│  Merging        │
│  (common_matrix)│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Event          │
│  Grouping       │
│  (event_grouping)│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Schedule       │
│  Layout         │
│  (schedule_layout)│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  PTD            │
│  Generation     │
│  (generate_ptd) │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Excel          │
│  Output         │
│  (PTD.xlsx)     │
└─────────────────┘
```

## Module Dependencies

### Dependency Graph

```
app.py
├── json_struct_protocol.py
├── json_struct_ecrf.py
└── PTD_Gen/
    ├── generate_ptd.py
    │   ├── modules/form_extractor.py
    │   ├── modules/soa_parser.py
    │   ├── modules/common_matrix.py
    │   ├── modules/event_grouping.py
    │   ├── modules/schedule_layout.py
    │   └── Final_study_specific_form.py
    └── config/
        ├── config_form_extractor.json
        ├── config_soa_parser.json
        ├── config_common_matrix.json
        ├── config_event_grouping.json
        ├── config_schedule_layout.json
        └── config_study_specific_forms.json
```

### Module Interaction Sequence

```
1. app.py (Flask API)
   │
   ├── 2. json_struct_protocol.py
   │   └── Output: structured_protocol.json
   │
   ├── 3. json_struct_ecrf.py
   │   └── Output: structured_ecrf.json
   │
   └── 4. PTD_Gen/generate_ptd.py
       │
       ├── 5. modules/form_extractor.py
       │   ├── Input: structured_ecrf.json
       │   └── Output: extracted_forms.csv
       │
       ├── 6. modules/soa_parser.py
       │   ├── Input: structured_protocol.json
       │   └── Output: schedule.csv
       │
       ├── 7. modules/common_matrix.py
       │   ├── Input: extracted_forms.csv, schedule.csv
       │   └── Output: soa_matrix.csv
       │
       ├── 8. modules/event_grouping.py
       │   ├── Input: structured_protocol.json
       │   └── Output: visits_with_groups.xlsx
       │
       ├── 9. modules/schedule_layout.py
       │   ├── Input: visits_with_groups.xlsx, soa_matrix.csv
       │   └── Output: schedule_grid.xlsx
       │
       ├── 10. Final_study_specific_form.py
       │    ├── Input: structured_ecrf.json
       │    └── Output: study_specific_forms.xlsx
       │
       └── 11. Template Integration
            ├── Input: schedule_grid.xlsx, study_specific_forms.xlsx
            └── Output: ptd_output.xlsx
```

## Configuration Architecture

### Configuration File Mapping

| Stage | Config File | Purpose | Controls |
|-------|-------------|---------|----------|
| Form Extraction | `config_form_extractor.json` | Extract forms from eCRF | Visit patterns, form validation, source classification |
| Schedule Parsing | `config_soa_parser.json` | Parse schedule of activities | Visit patterns, cell markers, procedure filters |
| Matrix Merging | `config_common_matrix.json` | Merge common data matrix | Data merging rules, field mappings |
| Event Grouping | `config_event_grouping.json` | Group events by visits | Visit grouping rules, event classification |
| Schedule Layout | `config_schedule_layout.json` | Generate schedule grid | Layout rules, formatting, column structure |
| Study Forms | `config_study_specific_forms.json` | Generate study-specific forms | Form structure, field mappings, validation rules |

### Configuration Hierarchy

```
Configuration System
├── Default Values (hardcoded)
├── JSON Config Files
│   ├── config_form_extractor.json
│   ├── config_soa_parser.json
│   ├── config_common_matrix.json
│   ├── config_event_grouping.json
│   ├── config_schedule_layout.json
│   └── config_study_specific_forms.json
└── Runtime Overrides (command line args)
```

## API Architecture

### RESTful API Design

```
Flask Application (app.py)
├── Static Routes
│   ├── GET / (home)
│   ├── GET /status
│   └── GET /health
├── File Upload Routes
│   └── POST /run_pipeline (multipart/form-data)
├── JSON Processing Routes
│   ├── POST /run_pipeline (application/json)
│   └── POST /run_ptd_generation
└── File Download Routes
    └── GET /download/<filename>
```

### Request/Response Flow

```
Client Request
    │
    ▼
┌─────────────────┐
│  Flask Router   │
│  (app.py)       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Request        │
│  Validation     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Processing     │
│  Pipeline       │
│  (PTD_Gen/)    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Response       │
│  Generation     │
└─────────────────┘
    │
    ▼
Client Response
```

## Error Handling Architecture

### Error Propagation Flow

```
Module Error
    │
    ▼
┌─────────────────┐
│  Exception      │
│  Handling       │
│  (try/catch)    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Logging        │
│  (logging)      │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Error          │
│  Response       │
│  (JSON)         │
└─────────────────┘
    │
    ▼
Client Error Response
```

### Error Types

1. **Input Validation Errors**: Invalid file types, missing required fields
2. **Processing Errors**: Module failures, data parsing errors
3. **File System Errors**: Permission denied, file not found
4. **Configuration Errors**: Invalid JSON, missing config files
5. **System Errors**: Memory issues, timeout errors

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        Security Layers                         │
├─────────────────────────────────────────────────────────────────┤
│  Input Validation  │  File Type Checking  │  Path Sanitization │
├─────────────────────────────────────────────────────────────────┤
│  CORS Protection   │  Error Handling     │  Logging Security   │
├─────────────────────────────────────────────────────────────────┤
│  File Upload       │  Temporary File     │  Cleanup Security   │
│  Restrictions      │  Management         │                     │
└─────────────────────────────────────────────────────────────────┘
```

### Security Measures

1. **Input Validation**: File type checking, size limits
2. **Path Sanitization**: Secure filename handling
3. **CORS Protection**: Cross-origin request handling
4. **Error Handling**: Secure error messages (no sensitive data)
5. **File Management**: Temporary file cleanup
6. **Logging**: Security event logging

## Performance Architecture

### Performance Optimization Strategies

1. **Memory Management**:
   - Streaming processing for large files
   - Temporary file cleanup
   - Memory-efficient data structures

2. **Processing Optimization**:
   - Parallel processing where possible
   - Caching of configuration data
   - Lazy loading of modules

3. **File I/O Optimization**:
   - Batch file operations
   - Efficient CSV/Excel processing
   - Compressed file handling

### Scalability Considerations

1. **Horizontal Scaling**: Stateless API design
2. **Vertical Scaling**: Memory and CPU optimization
3. **Caching**: Configuration and template caching
4. **Load Balancing**: Multiple API instances

## Deployment Architecture

### Development Environment

```
Developer Machine
├── Python Virtual Environment
├── Local Flask Server (app.py)
├── File System Storage
└── Browser-based Frontend
```

### Production Environment (Recommended)

```
Production Server
├── WSGI Server (Gunicorn/uWSGI)
├── Reverse Proxy (Nginx)
├── File Storage (Local/Cloud)
├── Logging System
└── Monitoring
```

### Container Architecture (Future)

```
Docker Container
├── Python Runtime
├── Application Code
├── Dependencies
├── Configuration
└── Logging
```

## Monitoring and Logging Architecture

### Logging Levels

```
DEBUG: Detailed information for debugging
INFO: General information about program execution
WARNING: Something unexpected happened
ERROR: A serious problem occurred
CRITICAL: A very serious error occurred
```

### Log Sources

1. **Application Logs**: Main application execution
2. **Module Logs**: Individual module processing
3. **Error Logs**: Exception and error tracking
4. **Access Logs**: API request/response logging
5. **Performance Logs**: Processing time and resource usage

### Monitoring Points

1. **API Endpoints**: Response times, error rates
2. **File Processing**: Success/failure rates
3. **Resource Usage**: Memory, CPU, disk usage
4. **Error Rates**: Exception frequency and types
5. **User Activity**: Upload/download patterns

## Future Architecture Considerations

### Planned Enhancements

1. **Microservices Architecture**: Split into independent services
2. **Message Queue**: Asynchronous processing with Redis/RabbitMQ
3. **Database Integration**: Persistent storage for metadata
4. **Cloud Storage**: S3/Azure Blob for file storage
5. **API Gateway**: Centralized API management
6. **Container Orchestration**: Kubernetes deployment

### Scalability Roadmap

1. **Phase 1**: Single-instance optimization
2. **Phase 2**: Multi-instance load balancing
3. **Phase 3**: Microservices decomposition
4. **Phase 4**: Cloud-native deployment
5. **Phase 5**: Global distribution

---

**Last Updated**: 2025-01-27  
**Document Version**: 1.0.0  
**Maintainer**: Development Team