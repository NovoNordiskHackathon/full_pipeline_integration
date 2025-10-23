#!/usr/bin/env python3
"""
Flask backend for PTD Generator
Integrates with existing Python pipeline scripts
"""

import os
import sys
import json
import tempfile
import shutil
import logging
import zipfile
import traceback
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Import conversion modules
from doc_to_pdf import convert_doc_to_pdf
from simpletext_extract import extract_text_and_tables_from_pdf as extract_text_from_pdf

# Import existing pipeline modules
from backend.json_struct_protocol import run_hierarchy as process_protocol
from backend.json_struct_ecrf import run_hierarchy as process_ecrf
# PTD generation will be called via subprocess

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'json'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_adobe_credentials():
    """Check if Adobe PDF Services credentials are set"""
    client_id = os.getenv('PDF_SERVICES_CLIENT_ID')
    client_secret = os.getenv('PDF_SERVICES_CLIENT_SECRET')

    if not client_id or not client_secret:
        logger.warning("⚠️  Adobe PDF Services credentials not set!")
        logger.warning("Set PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET environment variables")
        return False
    logger.info("✓ Adobe PDF Services credentials found")
    return True


@app.route('/')
def home():
    """Home page"""
    return jsonify({
        'message': 'PTD Generator API is running',
        'available_endpoints': [
            '/status',
            '/health',
            '/run_pipeline',
            '/run_ptd_generation'
        ]
    })


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, folder):
    """Save uploaded file and return the path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(folder, filename)
        file.save(file_path)
        return file_path
    return None


@app.route('/status', methods=['GET'])
def get_status():
    """Get current system status"""
    return jsonify({
        'status': 'running',
        'message': 'PTD Generator backend is operational',
        'version': '1.0.0',
        'adobe_credentials': check_adobe_credentials(),
        'endpoints': {
            'run_pipeline': '/run_pipeline',
            'status': '/status',
            'health': '/health'
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': str(Path().cwd()),
        'adobe_api': check_adobe_credentials()
    })


@app.route('/run_pipeline', methods=['POST'])
def run_pipeline():
    """
    Main pipeline endpoint
    Accepts uploaded files or JSON data and processes them
    """
    try:
        # Check if files are uploaded
        if 'protocol_file' in request.files and 'crf_file' in request.files:
            return process_uploaded_files()
        elif request.json and 'protocol_json' in request.json and 'ecrf_json' in request.json:
            return process_json_data(request.json)
        else:
            return jsonify({
                'success': False,
                'error': 'Either upload files (protocol_file, crf_file) or provide JSON data (protocol_json, ecrf_json)'
            }), 400

    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Pipeline processing failed: {str(e)}'
        }), 500


def process_uploaded_files():
    """Process uploaded files through the complete pipeline"""
    session_id = None
    try:
        protocol_file = request.files.get('protocol_file')
        crf_file = request.files.get('crf_file')

        if not protocol_file or not crf_file:
            return jsonify({
                'success': False,
                'error': 'Both protocol and CRF files are required'
            }), 400

        # Create unique session directory
        session_id = tempfile.mkdtemp(dir=UPLOAD_FOLDER)
        logger.info(f"Created session directory: {session_id}")

        # Save uploaded files
        protocol_path = save_uploaded_file(protocol_file, session_id)
        crf_path = save_uploaded_file(crf_file, session_id)

        if not protocol_path or not crf_path:
            return jsonify({
                'success': False,
                'error': 'Invalid file format. Supported: PDF, DOC, DOCX'
            }), 400

        logger.info(f"Processing files - Protocol: {protocol_path}, CRF: {crf_path}")

        # STEP 1: Convert DOC/DOCX to PDF if needed
        protocol_pdf_path = protocol_path
        crf_pdf_path = crf_path

        if protocol_path.endswith(('.doc', '.docx')):
            protocol_pdf_path = protocol_path.rsplit('.', 1)[0] + '.pdf'
            logger.info(f"Converting protocol from DOC to PDF...")
            if not convert_doc_to_pdf(protocol_path, protocol_pdf_path):
                return jsonify({
                    'success': False,
                    'error': 'Protocol DOC to PDF conversion failed'
                }), 500
            logger.info(f"✓ Protocol converted to PDF: {protocol_pdf_path}")

        if crf_path.endswith(('.doc', '.docx')):
            crf_pdf_path = crf_path.rsplit('.', 1)[0] + '.pdf'
            logger.info(f"Converting CRF from DOC to PDF...")
            if not convert_doc_to_pdf(crf_path, crf_pdf_path):
                return jsonify({
                    'success': False,
                    'error': 'CRF DOC to PDF conversion failed'
                }), 500
            logger.info(f"✓ CRF converted to PDF: {crf_pdf_path}")

        # STEP 2: Extract text from PDF to ZIP (contains structuredData.json)
        protocol_zip_path = os.path.join(session_id, 'protocol_extract.zip')
        crf_zip_path = os.path.join(session_id, 'crf_extract.zip')

        logger.info(f"Extracting text from protocol PDF...")
        extract_text_from_pdf(protocol_pdf_path, protocol_zip_path)
        logger.info(f"✓ Protocol extracted to: {protocol_zip_path}")

        logger.info(f"Extracting text from CRF PDF...")
        extract_text_from_pdf(crf_pdf_path, crf_zip_path)
        logger.info(f"✓ CRF extracted to: {crf_zip_path}")

        # STEP 3: Unzip and load structuredData.json
        protocol_extract_dir = os.path.join(session_id, 'protocol_extract')
        crf_extract_dir = os.path.join(session_id, 'crf_extract')

        os.makedirs(protocol_extract_dir, exist_ok=True)
        os.makedirs(crf_extract_dir, exist_ok=True)

        logger.info(f"Unzipping protocol extract...")
        with zipfile.ZipFile(protocol_zip_path, 'r') as zip_ref:
            zip_ref.extractall(protocol_extract_dir)

        logger.info(f"Unzipping CRF extract...")
        with zipfile.ZipFile(crf_zip_path, 'r') as zip_ref:
            zip_ref.extractall(crf_extract_dir)

        # STEP 4: Load the structuredData.json files
        protocol_json_path = os.path.join(protocol_extract_dir, 'structuredData.json')
        crf_json_path = os.path.join(crf_extract_dir, 'structuredData.json')

        if not os.path.exists(protocol_json_path):
            return jsonify({
                'success': False,
                'error': 'Protocol extraction failed - no structuredData.json found'
            }), 500

        if not os.path.exists(crf_json_path):
            return jsonify({
                'success': False,
                'error': 'CRF extraction failed - no structuredData.json found'
            }), 500

        logger.info(f"Loading protocol JSON from: {protocol_json_path}")
        with open(protocol_json_path, 'r', encoding='utf-8') as f:
            protocol_json = json.load(f)

        logger.info(f"Loading CRF JSON from: {crf_json_path}")
        with open(crf_json_path, 'r', encoding='utf-8') as f:
            crf_json = json.load(f)

        logger.info("✓ Successfully loaded extracted JSON data")

        # STEP 5: Process with your existing JSON processing pipeline
        return process_json_data({
            'protocol_json': protocol_json,
            'ecrf_json': crf_json
        })

    except Exception as e:
        logger.error(f"File processing error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'File processing failed: {str(e)}'
        }), 500
    finally:
        # Cleanup temporary files (optional - comment out for debugging)
        if session_id:
            try:
                logger.info(f"Cleaning up session directory: {session_id}")
                shutil.rmtree(session_id, ignore_errors=True)
            except Exception as cleanup_error:
                logger.warning(f"Cleanup failed: {cleanup_error}")

#
# def process_json_data(data):
#     """Process pre-extracted JSON data through the pipeline"""
#     try:
#         protocol_json = data.get('protocol_json')
#         ecrf_json = data.get('ecrf_json')
#
#         if not protocol_json or not ecrf_json:
#             return jsonify({
#                 'success': False,
#                 'error': 'Both protocol_json and ecrf_json are required'
#             }), 400
#
#         # Create temporary working directory
#         with tempfile.TemporaryDirectory() as temp_dir:
#             logger.info(f"Processing JSON data in temp directory: {temp_dir}")
#
#             # Save JSON files
#             protocol_file = os.path.join(temp_dir, 'protocol_structured.json')
#             ecrf_file = os.path.join(temp_dir, 'ecrf_structured.json')
#
#             with open(protocol_file, 'w', encoding='utf-8') as f:
#                 json.dump(protocol_json, f, indent=2)
#
#             with open(ecrf_file, 'w', encoding='utf-8') as f:
#                 json.dump(ecrf_json, f, indent=2)
#
#             # Process protocol - returns path or None
#             logger.info("Processing protocol JSON...")
#             protocol_output = process_protocol(protocol_file)
#
#             # If process_protocol doesn't return a path, construct expected path
#             if not protocol_output:
#                 protocol_output = protocol_file.replace('.json', '_output.json')
#                 logger.info(f"Using expected protocol output path: {protocol_output}")
#
#             # Process eCRF - returns path or None
#             logger.info("Processing eCRF JSON...")
#             ecrf_output = process_ecrf(ecrf_file)
#
#             # If process_ecrf doesn't return a path, construct expected path
#             if not ecrf_output:
#                 ecrf_output = ecrf_file.replace('.json', '_output.json')
#                 logger.info(f"Using expected eCRF output path: {ecrf_output}")
#
#             # Verify the output files actually exist
#             if not os.path.exists(protocol_output):
#                 return jsonify({
#                     'success': False,
#                     'error': f'Protocol processing failed - output file not found: {protocol_output}'
#                 }), 500
#
#             if not os.path.exists(ecrf_output):
#                 return jsonify({
#                     'success': False,
#                     'error': f'eCRF processing failed - output file not found: {ecrf_output}'
#                 }), 500
#
#             # Generate PTD - Call via subprocess with proper arguments
#             logger.info("Generating PTD...")
#             ptd_output_file = os.path.join(OUTPUT_FOLDER, 'ptd_output.xlsx')
#
#             # Ensure all paths are absolute
#             protocol_output_abs = os.path.abspath(protocol_output)
#             ecrf_output_abs = os.path.abspath(ecrf_output)
#             ptd_output_abs = os.path.abspath(ptd_output_file)
#
#             logger.info(f"Running PTD generation with:")
#             logger.info(f"  Protocol: {protocol_output_abs}")
#             logger.info(f"  eCRF: {ecrf_output_abs}")
#             logger.info(f"  Output: {ptd_output_abs}")
#
#             # Run generate_ptd.py as a CLI command
#             result = subprocess.run([
#                 sys.executable,  # Use same Python interpreter
#                 'backend/generate_ptd.py',
#                 '--protocol', protocol_output_abs,
#                 '--ecrf', ecrf_output_abs,
#                 '--out', ptd_output_abs
#             ], capture_output=True, text=True, check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
#
#             logger.info(f"✓ PTD generation completed")
#             logger.info(f"stdout: {result.stdout}")
#             if result.stderr:
#                 logger.warning(f"stderr: {result.stderr}")
#
#             return jsonify({
#                 'success': True,
#                 'message': 'Pipeline completed successfully',
#                 'outputs': {
#                     'protocol_processed': protocol_output_abs,
#                     'ecrf_processed': ecrf_output_abs,
#                     'ptd_file': ptd_output_abs,
#                     'download_url': f'/download/{os.path.basename(ptd_output_abs)}'
#                 }
#             })
#
#     except subprocess.CalledProcessError as e:
#         logger.error(f"PTD generation failed with exit code {e.returncode}")
#         logger.error(f"stdout: {e.stdout}")
#         logger.error(f"stderr: {e.stderr}")
#         return jsonify({
#             'success': False,
#             'error': f'PTD generation failed: {e.stderr or e.stdout}'
#         }), 500
#     except Exception as e:
#         logger.error(f"JSON processing error: {str(e)}")
#         logger.error(traceback.format_exc())
#         return jsonify({
#             'success': False,
#             'error': f'JSON processing failed: {str(e)}'
#         }), 500

def process_json_data(data):
    """Process pre-extracted JSON data through the pipeline"""
    try:
        protocol_json = data.get('protocol_json')
        ecrf_json = data.get('ecrf_json')

        if not protocol_json or not ecrf_json:
            return jsonify({
                'success': False,
                'error': 'Both protocol_json and ecrf_json are required'
            }), 400

        # Create temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Processing JSON data in temp directory: {temp_dir}")

            # Save JSON files
            protocol_file = os.path.join(temp_dir, 'protocol_structured.json')
            ecrf_file = os.path.join(temp_dir, 'ecrf_structured.json')

            with open(protocol_file, 'w', encoding='utf-8') as f:
                json.dump(protocol_json, f, indent=2)

            with open(ecrf_file, 'w', encoding='utf-8') as f:
                json.dump(ecrf_json, f, indent=2)

            # Process protocol - returns path or None
            logger.info("Processing protocol JSON...")
            protocol_output = process_protocol(protocol_file)

            # If process_protocol doesn't return a path, construct expected path
            if not protocol_output:
                protocol_output = protocol_file.replace('.json', '_output.json')
                logger.info(f"Using expected protocol output path: {protocol_output}")

            # Process eCRF - returns path or None
            logger.info("Processing eCRF JSON...")
            ecrf_output = process_ecrf(ecrf_file)

            # If process_ecrf doesn't return a path, construct expected path
            if not ecrf_output:
                ecrf_output = ecrf_file.replace('.json', '_output.json')
                logger.info(f"Using expected eCRF output path: {ecrf_output}")

            # Verify the output files actually exist
            if not os.path.exists(protocol_output):
                return jsonify({
                    'success': False,
                    'error': f'Protocol processing failed - output file not found: {protocol_output}'
                }), 500

            if not os.path.exists(ecrf_output):
                return jsonify({
                    'success': False,
                    'error': f'eCRF processing failed - output file not found: {ecrf_output}'
                }), 500

            # Generate PTD using template mode
            logger.info("Generating PTD...")
            ptd_output_file = os.path.join(OUTPUT_FOLDER, 'ptd_output.xlsx')

            # Define template file path - adjust this to your actual template location
            # Option 1: Template in backend folder
            template_file = os.path.join('backend', 'templates', 'PTD Template v.2_Draft (1).xlsx')

            # Option 2: Template in project root
            # template_file = 'ptd_template.xlsx'

            # Option 3: Template in a specific location
            # template_file = '/path/to/your/ptd_template.xlsx'

            # Ensure all paths are absolute
            protocol_output_abs = os.path.abspath(protocol_output)
            ecrf_output_abs = os.path.abspath(ecrf_output)
            ptd_output_abs = os.path.abspath(ptd_output_file)
            template_abs = os.path.abspath(template_file)

            # Check if template exists
            if not os.path.exists(template_abs):
                logger.error(f"Template file not found: {template_abs}")
                return jsonify({
                    'success': False,
                    'error': f'Template file not found: {template_abs}. Please create a template or use stream mode.'
                }), 500

            logger.info(f"Running PTD generation with:")
            logger.info(f"  Protocol: {protocol_output_abs}")
            logger.info(f"  eCRF: {ecrf_output_abs}")
            logger.info(f"  Template: {template_abs}")
            logger.info(f"  Output: {ptd_output_abs}")

            # Run generate_ptd.py with template
            result = subprocess.run([
                sys.executable,
                'backend/generate_ptd.py',
                '--protocol', protocol_output_abs,
                '--ecrf', ecrf_output_abs,
                '--template', template_abs,
                '--out', ptd_output_abs
            ], capture_output=True, text=True, check=True, cwd=os.path.dirname(os.path.abspath(__file__)))

            logger.info(f"✓ PTD generation completed successfully!")
            logger.info(f"Output: {result.stdout}")
            if result.stderr:
                logger.info(f"Additional info: {result.stderr}")

            return jsonify({
                'success': True,
                'message': 'Pipeline completed successfully! PTD file generated with template.',
                'outputs': {
                    'protocol_processed': protocol_output_abs,
                    'ecrf_processed': ecrf_output_abs,
                    'ptd_file': ptd_output_abs,
                    'template_used': template_abs,
                    'download_url': f'/download/{os.path.basename(ptd_output_abs)}'
                }
            })

    except subprocess.CalledProcessError as e:
        logger.error(f"PTD generation failed with exit code {e.returncode}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return jsonify({
            'success': False,
            'error': f'PTD generation failed: {e.stderr or e.stdout}'
        }), 500
    except Exception as e:
        logger.error(f"JSON processing error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'JSON processing failed: {str(e)}'
        }), 500


@app.route('/run_ptd_generation', methods=['POST'])
def run_ptd_generation():
    """
    Run the full PTD generation pipeline
    Requires structured JSON files as input
    """
    try:
        data = request.json
        if not data or 'protocol_json' not in data or 'ecrf_json' not in data:
            return jsonify({
                'success': False,
                'error': 'Protocol and eCRF JSON data are required'
            }), 400

        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            protocol_file = os.path.join(temp_dir, 'protocol_structured.json')
            ecrf_file = os.path.join(temp_dir, 'ecrf_structured.json')
            output_file = os.path.join(OUTPUT_FOLDER, 'ptd_output.xlsx')

            # Write JSON data
            with open(protocol_file, 'w', encoding='utf-8') as f:
                json.dump(data['protocol_json'], f, indent=2)

            with open(ecrf_file, 'w', encoding='utf-8') as f:
                json.dump(data['ecrf_json'], f, indent=2)

            # Run PTD generation via subprocess
            logger.info("Running PTD generation...")
            result = subprocess.run([
                sys.executable,
                'backend/PTD_Gen/generate_ptd.py',
                '--protocol', protocol_file,
                '--ecrf', ecrf_file,
                '--out', output_file
            ], capture_output=True, text=True, check=True, cwd=os.path.dirname(os.path.abspath(__file__)))

            return jsonify({
                'success': True,
                'message': 'PTD generation completed',
                'output_file': 'ptd_output.xlsx',
                'download_url': '/download/ptd_output.xlsx',
                'result': result
            })

    except Exception as e:
        logger.error(f"PTD generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'PTD generation failed: {str(e)}'
        }), 500


# @app.route('/download/<filename>')
# def download_file(filename):
#     """Download generated files"""
#     try:
#         file_path = os.path.join(OUTPUT_FOLDER, secure_filename(filename))
#         if os.path.exists(file_path):
#             return send_file(file_path, as_attachment=True)
#         else:
#             return jsonify({'error': 'File not found'}), 404
#     except Exception as e:
#         logger.error(f"Download error: {str(e)}")
#         return jsonify({'error': str(e)}), 500
@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        # Force download of ptd_output.xlsx regardless of what's requested
        actual_filename = 'ptd_output.xlsx'
        file_path = os.path.join(OUTPUT_FOLDER, secure_filename(actual_filename))

        logger.info(f"Download requested for: {filename}")
        logger.info(f"Serving file from: {file_path}")
        logger.info(f"File exists: {os.path.exists(file_path)}")

        if os.path.exists(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name='PTD_Output.xlsx'  # Name it properly for download
            )
        else:
            logger.error(f"File not found: {file_path}")
            return jsonify({'error': f'File not found: {file_path}'}), 404
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Starting PTD Generator Backend...")
    check_adobe_credentials()
    app.run(debug=True, host='0.0.0.0', port=5000)

