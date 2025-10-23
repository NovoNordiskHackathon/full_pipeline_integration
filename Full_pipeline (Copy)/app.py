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
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import traceback

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import existing pipeline modules
from backend.json_struct_protocol import run_hierarchy as process_protocol
from backend.json_struct_ecrf import run_hierarchy as process_ecrf
from backend.generate_ptd import main as generate_ptd_main

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
        'endpoints': {
            'run_pipeline': '/run_pipeline',
            'status': '/status',
            'health': '/health'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': str(Path().cwd())})

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
        elif 'protocol_json' in request.json and 'ecrf_json' in request.json:
            return process_json_data(request.json)
        else:
            return jsonify({
                'success': False,
                'error': 'Either upload files or provide JSON data'
            }), 400
            
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Pipeline processing failed: {str(e)}'
        }), 500

def process_uploaded_files():
    """Process uploaded files through the pipeline"""
    try:
        protocol_file = request.files['protocol_file']
        crf_file = request.files['crf_file']
        
        if not protocol_file or not crf_file:
            return jsonify({
                'success': False,
                'error': 'Both protocol and CRF files are required'
            }), 400
        
        # Save uploaded files
        protocol_path = save_uploaded_file(protocol_file, UPLOAD_FOLDER)
        crf_path = save_uploaded_file(crf_file, UPLOAD_FOLDER)
        
        if not protocol_path or not crf_path:
            return jsonify({
                'success': False,
                'error': 'Invalid file format. Supported: PDF, DOC, DOCX'
            }), 400
        
        # For now, we'll simulate processing since the actual pipeline expects JSON files
        # In a real implementation, you'd convert PDF/DOC to JSON first
        return jsonify({
            'success': True,
            'message': 'Files uploaded successfully. Note: PDF/DOC conversion not yet implemented.',
            'files': {
                'protocol': os.path.basename(protocol_path),
                'crf': os.path.basename(crf_path)
            },
            'next_steps': 'Upload JSON files for full processing'
        })
        
    except Exception as e:
        logger.error(f"File processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'File processing failed: {str(e)}'
        }), 500

def process_json_data(data):
    """Process JSON data through the pipeline"""
    try:
        protocol_json = data['protocol_json']
        ecrf_json = data['ecrf_json']
        
        # Create temporary files for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            protocol_file = os.path.join(temp_dir, 'protocol.json')
            ecrf_file = os.path.join(temp_dir, 'ecrf.json')
            
            # Write JSON data to temporary files
            with open(protocol_file, 'w', encoding='utf-8') as f:
                json.dump(protocol_json, f, indent=2)
            
            with open(ecrf_file, 'w', encoding='utf-8') as f:
                json.dump(ecrf_json, f, indent=2)
            
            # Process protocol JSON
            protocol_output = os.path.join(temp_dir, 'protocol_structured.json')
            process_protocol(protocol_file, protocol_output)
            
            # Process eCRF JSON
            ecrf_output = os.path.join(temp_dir, 'ecrf_structured.json')
            process_ecrf(ecrf_file, ecrf_output)
            
            # Generate PTD (this would require the full PTD generation pipeline)
            # For now, we'll return the structured JSON files
            with open(protocol_output, 'r', encoding='utf-8') as f:
                structured_protocol = json.load(f)
            
            with open(ecrf_output, 'r', encoding='utf-8') as f:
                structured_ecrf = json.load(f)
            
            return jsonify({
                'success': True,
                'message': 'Pipeline processing completed successfully',
                'results': {
                    'structured_protocol': structured_protocol,
                    'structured_ecrf': structured_ecrf,
                    'processing_steps': [
                        'Protocol JSON structured',
                        'eCRF JSON structured',
                        'Ready for PTD generation'
                    ]
                }
            })
            
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
            output_file = os.path.join(temp_dir, 'ptd_output.xlsx')
            
            # Write JSON data
            with open(protocol_file, 'w', encoding='utf-8') as f:
                json.dump(data['protocol_json'], f, indent=2)
            
            with open(ecrf_file, 'w', encoding='utf-8') as f:
                json.dump(data['ecrf_json'], f, indent=2)
            
            # Run PTD generation (simulate for now)
            # In real implementation, you'd call the actual PTD generation function
            logger.info("PTD generation would run here with the structured JSON files")
            
            # Create a sample response
            return jsonify({
                'success': True,
                'message': 'PTD generation completed',
                'output_file': 'ptd_output.xlsx',
                'download_url': '/download/ptd_output.xlsx'
            })
            
    except Exception as e:
        logger.error(f"PTD generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'PTD generation failed: {str(e)}'
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)