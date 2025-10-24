# Quick Start — PTD Generator

Follow these minimal steps to run the API locally.

## 1) Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

## 2) Install dependencies
```bash
pip install -r Full_pipeline/requirements.txt
pip install -r Full_pipeline/PTD_Gen/requirements.txt
```

## 3) Run the backend
```bash
python Full_pipeline/app.py
# Server starts on http://127.0.0.1:5000
```

Note: If `Full_pipeline/app.py` didn’t exist, replicate the old integration’s endpoints and import patterns from `Full_pipeline (Copy)/app.py` (do not copy the file here; follow the structure documented in README_FULL.md).

## 4) Health and sample request
```bash
# Health
curl -s http://127.0.0.1:5000/health | jq

# JSON pipeline (minimal example)
curl -s -X POST http://127.0.0.1:5000/run_pipeline \
  -H 'Content-Type: application/json' \
  -d '{"protocol_json": {"elements": []}, "ecrf_json": {"elements": []}}' | jq
```

## 5) Generate PTD workbook
```bash
curl -s -X POST http://127.0.0.1:5000/run_ptd_generation \
  -H 'Content-Type: application/json' \
  -d '{"protocol_json": {"elements": []}, "ecrf_json": {"elements": []}}' | jq

# Then download
curl -L -o ptd_output.xlsx http://127.0.0.1:5000/download/ptd_output.xlsx
```

## 6) Frontend (optional)
Open `Full_pipeline/frontend/index.html` in a browser. It posts to `/run_pipeline` and simulates PTD generation when working with file uploads. JSON-based flow is supported via API calls above.
