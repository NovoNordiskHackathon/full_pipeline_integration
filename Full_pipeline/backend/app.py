#!/usr/bin/env python3
"""
Flask backend for PTD Generator (rebuilt integration)
Mirrors the old integration while using updated backend modules in this folder.
"""

import os
import sys
import json
import tempfile
import logging
import traceback
from pathlib import Path
from typing import Optional

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Ensure project root is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

# Optional helpers (present in project root)
try:
    from doc_to_pdf import convert_doc_to_pdf  # noqa: F401
except Exception:
    convert_doc_to_pdf = None

try:
    from simpletext_extract import extract_text_from_pdf  # noqa: F401
except Exception:
    extract_text_from_pdf = None

# Import updated pipeline modules from project root
from json_struct_protocol import run_hierarchy as process_protocol  # type: ignore
from json_struct_ecrf import run_hierarchy as process_ecrf  # type: ignore

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = os.path.join(CURRENT_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(CURRENT_DIR, "output")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "json"}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage, folder: str) -> Optional[str]:
    if file_storage and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        file_path = os.path.join(folder, filename)
        file_storage.save(file_path)
        return file_path
    return None


@app.route("/")
def home():
    return jsonify(
        {
            "message": "PTD Generator API is running",
            "available_endpoints": [
                "/status",
                "/health",
                "/run_pipeline",
                "/run_ptd_generation",
                "/download/<filename>",
                "/outputs/latest",
            ],
        }
    )


@app.route("/status", methods=["GET"]) 
def get_status():
    return jsonify(
        {
            "status": "running",
            "message": "PTD Generator backend is operational",
            "version": "1.0.0",
            "endpoints": {
                "run_pipeline": "/run_pipeline",
                "status": "/status",
                "health": "/health",
            },
        }
    )


@app.route("/health", methods=["GET"]) 
def health_check():
    return jsonify({"status": "healthy", "cwd": str(Path().cwd())})


@app.route("/run_pipeline", methods=["POST"]) 
def run_pipeline():
    """
    Accepts uploaded files (protocol_file, crf_file) OR JSON payload with
    { protocol_json: {...}, ecrf_json: {...} }.
    When JSON is provided, structure it via updated hierarchy processors and return results.
    """
    try:
        # File upload path
        if "protocol_file" in request.files and "crf_file" in request.files:
            return _process_uploaded_files()

        # JSON path
        if request.is_json:
            data = request.get_json(silent=True) or {}
            if "protocol_json" in data and "ecrf_json" in data:
                return _process_json_data(data)

        return (
            jsonify(
                {
                    "success": False,
                    "error": "Either upload files (protocol_file, crf_file) or provide JSON data (protocol_json, ecrf_json)",
                }
            ),
            400,
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"Pipeline processing failed: {e}"}), 500


# Backward-compatibility alias: some clients call with a leading double slash
@app.route("//run_pipeline", methods=["POST"])  # e.g., http://127.0.0.1:5000//run_pipeline
def run_pipeline_double_slash():
    return run_pipeline()


def _process_uploaded_files():
    try:
        protocol_file = request.files.get("protocol_file")
        crf_file = request.files.get("crf_file")

        if not protocol_file or not crf_file:
            return jsonify({"success": False, "error": "Both protocol and CRF files are required"}), 400

        protocol_path = save_uploaded_file(protocol_file, UPLOAD_FOLDER)
        crf_path = save_uploaded_file(crf_file, UPLOAD_FOLDER)

        if not protocol_path or not crf_path:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid file format. Supported: PDF, DOC, DOCX, JSON",
                    }
                ),
                400,
            )

        # Conversion from PDF/DOC to JSON is not implemented in integration; keep identical behavior to old project
        return jsonify(
            {
                "success": True,
                "message": "Files uploaded successfully. Note: PDF/DOC conversion not yet implemented.",
                "files": {
                    "protocol": os.path.basename(protocol_path),
                    "crf": os.path.basename(crf_path),
                },
                "next_steps": "Upload JSON files for full processing",
            }
        )
    except Exception as e:
        logger.error(f"File processing error: {e}")
        return jsonify({"success": False, "error": f"File processing failed: {e}"}), 500


def _process_json_data(data: dict):
    try:
        protocol_json = data["protocol_json"]
        ecrf_json = data["ecrf_json"]

        with tempfile.TemporaryDirectory() as temp_dir:
            protocol_file = os.path.join(temp_dir, "protocol.json")
            ecrf_file = os.path.join(temp_dir, "ecrf.json")

            with open(protocol_file, "w", encoding="utf-8") as f:
                json.dump(protocol_json, f, indent=2)
            with open(ecrf_file, "w", encoding="utf-8") as f:
                json.dump(ecrf_json, f, indent=2)

            # Structure both JSONs using updated processors
            protocol_output = os.path.join(temp_dir, "protocol_structured.json")
            ecrf_output = os.path.join(temp_dir, "ecrf_structured.json")
            process_protocol(protocol_file, protocol_output)
            process_ecrf(ecrf_file, ecrf_output)

            with open(protocol_output, "r", encoding="utf-8") as f:
                structured_protocol = json.load(f)
            with open(ecrf_output, "r", encoding="utf-8") as f:
                structured_ecrf = json.load(f)

            return jsonify(
                {
                    "success": True,
                    "message": "Pipeline processing completed successfully",
                    "results": {
                        "structured_protocol": structured_protocol,
                        "structured_ecrf": structured_ecrf,
                        "processing_steps": [
                            "Protocol JSON structured",
                            "eCRF JSON structured",
                            "Ready for PTD generation",
                        ],
                    },
                }
            )
    except Exception as e:
        logger.error(f"JSON processing error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"JSON processing failed: {e}"}), 500


@app.route("/run_ptd_generation", methods=["POST"]) 
def run_ptd_generation():
    """
    Run the full PTD generation pipeline using the updated generator in PTD_Gen/.
    Expects structured JSON payload with keys: protocol_json, ecrf_json.
    Produces an Excel file under OUTPUT_FOLDER and returns a download URL.
    """
    try:
        data = request.get_json(silent=True) or {}
        if "protocol_json" not in data or "ecrf_json" not in data:
            return jsonify({"success": False, "error": "Protocol and eCRF JSON data are required"}), 400

        with tempfile.TemporaryDirectory() as temp_dir:
            protocol_file = os.path.join(temp_dir, "protocol_structured.json")
            ecrf_file = os.path.join(temp_dir, "ecrf_structured.json")

            with open(protocol_file, "w", encoding="utf-8") as f:
                json.dump(data["protocol_json"], f, indent=2)
            with open(ecrf_file, "w", encoding="utf-8") as f:
                json.dump(data["ecrf_json"], f, indent=2)

            # Ensure output path
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            output_file = os.path.join(OUTPUT_FOLDER, "ptd_output.xlsx")

            # Call the updated CLI in stream mode to avoid template requirement
            import subprocess
            cmd = [
                sys.executable,
                os.path.join(CURRENT_DIR, "PTD_Gen", "generate_ptd.py"),
                "--protocol",
                protocol_file,
                "--ecrf",
                ecrf_file,
                "--out",
                output_file,
                "--stream",
            ]
            logger.info("Running PTD generation: %s", " ".join(cmd))
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                logger.error("PTD generation failed: %s\n%s", proc.stderr, proc.stdout)
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"PTD generation failed: {proc.stderr or proc.stdout}",
                        }
                    ),
                    500,
                )

            if not os.path.exists(output_file):
                return (
                    jsonify({"success": False, "error": "PTD output file not created"}),
                    500,
                )

            return jsonify(
                {
                    "success": True,
                    "message": "PTD generation completed",
                    "output_file": os.path.basename(output_file),
                    "download_url": f"/download/{os.path.basename(output_file)}",
                }
            )
    except Exception as e:
        logger.error(f"PTD generation error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"PTD generation failed: {e}"}), 500


@app.route("/download/<path:filename>") 
def download_file(filename: str):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/outputs/latest", methods=["GET"]) 
def get_latest_output():
    """Return metadata and download URL for the latest .xlsx in OUTPUT_FOLDER."""
    try:
        if not os.path.isdir(OUTPUT_FOLDER):
            return jsonify({"success": False, "error": "Output folder not found"}), 404

        # Find .xlsx files and pick the most recently modified one
        xlsx_files = [
            f for f in os.listdir(OUTPUT_FOLDER)
            if os.path.isfile(os.path.join(OUTPUT_FOLDER, f)) and f.lower().endswith(".xlsx")
        ]
        if not xlsx_files:
            return jsonify({"success": False, "error": "No output files available"}), 404

        latest_file = max(
            xlsx_files,
            key=lambda f: os.path.getmtime(os.path.join(OUTPUT_FOLDER, f)),
        )
        return jsonify(
            {
                "success": True,
                "output_file": latest_file,
                "download_url": f"/download/{latest_file}",
            }
        )
    except Exception as e:
        logger.error("Failed to get latest output: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(_):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
