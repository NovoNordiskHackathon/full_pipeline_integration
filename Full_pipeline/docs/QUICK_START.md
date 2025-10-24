# PTD Generator - Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## 1. Setup Environment

### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

## 2. Run the Application

### Start Backend Server
```bash
# From project root directory
python app.py
```

### Access the Application
- **Frontend**: http://localhost:5000
- **API**: http://localhost:5000/status

## 3. Test the API

### Check Status
```bash
curl -X GET http://localhost:5000/status
```

### Upload Files (if you have test files)
```bash
curl -X POST http://localhost:5000/run_pipeline \
  -F "protocol_file=@protocol.pdf" \
  -F "crf_file=@crf.pdf"
```

## 4. Generate PTD (Command Line)

### Using JSON Files
```bash
python PTD_Gen/generate_ptd.py \
  --ecrf ecrf.json \
  --protocol protocol.json \
  --out ptd_output.xlsx
```

### Using Template
```bash
python PTD_Gen/generate_ptd.py \
  --ecrf ecrf.json \
  --protocol protocol.json \
  --template template.xlsx \
  --out ptd_output.xlsx
```

## 5. Troubleshooting

### Common Issues

#### Module Not Found Error
```bash
# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Port Already in Use
```bash
# Find and kill process using port 5000
lsof -i :5000
kill -9 <PID>
```

#### Missing Dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 6. Next Steps

1. **Read Full Documentation**: See `docs/README_FULL.md`
2. **Understand Architecture**: See `docs/ARCHITECTURE.md`
3. **API Reference**: See `docs/API_REFERENCE.md`
4. **Configure Settings**: Edit JSON files in `PTD_Gen/config/`

## Quick Commands Reference

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Run
python app.py

# Test
curl -X GET http://localhost:5000/status

# Generate PTD
python PTD_Gen/generate_ptd.py --ecrf ecrf.json --protocol protocol.json --out output.xlsx
```

---

**Need Help?** Check the full documentation in `docs/README_FULL.md`