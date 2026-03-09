#!/usr/bin/env python3
"""
app.py - HTTP API for PurrCrypt

This module provides a REST API for encrypting and decrypting messages
into adorable cat sounds.

Endpoints (all prefixed by API_PREFIX, default /api):
    GET  /         - Basic API information
    POST /encrypt  - Encrypt text with password
    POST /decrypt  - Decrypt cat sounds with password
    GET  /health   - Health check endpoint
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
import requests

# Add the parent directory to the path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from api.cipher import CatCipher
from api import __version__ as VERSION

# Route prefix for all endpoints — override with API_PREFIX env var
API_PREFIX = os.environ.get('API_PREFIX', '/api').rstrip('/')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
cipher = CatCipher()
bp = Blueprint('purrcrypt', __name__)

# Check if debug mode is enabled
DEBUG_MODE = os.environ.get('DEBUG', 'False').lower() == 'true'

if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    logger.debug("Debug mode enabled - detailed logging active")
else:
    logger.setLevel(logging.INFO)


def log_request(endpoint, method, data=None):
    """
    Log incoming request details.

    Args:
        endpoint: Endpoint name
        method: HTTP method
        data: Request data (optional)
    """
    client_ip = request.remote_addr
    logger.info(f"[{method}] {endpoint} - Client: {client_ip}")

    if DEBUG_MODE and data:
        # Log raw request data
        logger.debug(f"  Request data: {data}")


def log_response(endpoint, status_code, response_data=None, error=None):
    """
    Log response details.

    Args:
        endpoint: Endpoint name
        status_code: HTTP status code
        response_data: Response data (optional)
        error: Error message (optional)
    """
    if error:
        logger.error(f"  {endpoint} - Status: {status_code} - Error: {error}")
    else:
        logger.info(f"  {endpoint} - Status: {status_code} - Success")

    if DEBUG_MODE and response_data:
        # Log raw response data
        logger.debug(f"  Response data: {response_data}")


@bp.route('/', methods=['GET'])
def index():
    """
    Basic API information endpoint.

    Returns:
        JSON with API information
    """
    log_request('/', 'GET')

    response = {
        'name': 'PurrCrypt API',
        'version': VERSION,
        'description': 'Encrypt messages into cat sounds!',
        'endpoints': {
            f'{API_PREFIX}/': 'GET - API information',
            f'{API_PREFIX}/encrypt': 'POST - Encrypt text (fields: text, password)',
            f'{API_PREFIX}/decrypt': 'POST - Decrypt cat sounds (fields: meow, password)',
            f'{API_PREFIX}/health': 'GET - Health check'
        },
        'github': 'https://github.com/theahadev/purrcrypt-api'
    }

    log_response('/', 200, response)
    return jsonify(response)


@bp.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    """
    Encrypt text into cat sounds.

    GET  /encrypt?text=hello&password=optional
    POST /encrypt  JSON body: {"text": "...", "password": "..."}

    Returns:
        JSON with encrypted cat sounds or error
    """
    try:
        if request.method == 'GET':
            data = request.args
        else:
            data = request.get_json() or {}
        log_request('/encrypt', request.method, data)

        text = data.get('text')
        password = data.get('password')

        if not text:
            error_msg = 'Missing required field: text'
            log_response('/encrypt', 400, error=error_msg)
            return jsonify({
                'error': error_msg
            }), 400

        # Convert empty password to None
        if password == '':
            password = None

        # Log encryption details
        text_length = len(text)
        has_password = password is not None
        if DEBUG_MODE:
            logger.debug(f"  Encrypting text (length: {text_length}, password: {'present' if has_password else 'None'})")

        # Encrypt the text
        encrypted = cipher.encrypt(text, password=password)

        if DEBUG_MODE:
            logger.debug(f"  Encryption complete (output length: {len(encrypted)})")

        response = {
            'success': True,
            'meow': encrypted,
            'encrypted': True,
            'password_protected': has_password
        }

        log_response('/encrypt', 200, response)
        return jsonify(response)

    except Exception as e:
        error_msg = f'Encryption failed: {str(e)}'
        log_response('/encrypt', 500, error=error_msg)
        return jsonify({
            'error': error_msg
        }), 500


@bp.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    """
    Decrypt cat sounds back into text.

    GET  /decrypt?meow=...&password=optional
    POST /decrypt  JSON body: {"meow": "...", "password": "..."}

    Returns:
        JSON with decrypted text or error
    """
    try:
        if request.method == 'GET':
            data = request.args
        else:
            data = request.get_json() or {}
        log_request('/decrypt', request.method, data)

        meow = data.get('meow')
        password = data.get('password')

        if not meow:
            error_msg = 'Missing required field: meow'
            log_response('/decrypt', 400, error=error_msg)
            return jsonify({
                'error': error_msg
            }), 400

        # Convert empty password to None
        if password == '':
            password = None

        # Log decryption details
        meow_length = len(meow)
        has_password = password is not None
        if DEBUG_MODE:
            logger.debug(f"  Decrypting cat sounds (length: {meow_length}, password: {'present' if has_password else 'None'})")

        # Decrypt the cat sounds
        decrypted_bytes = cipher.decrypt(meow, password=password)

        # Try to decode as UTF-8
        try:
            text = decrypted_bytes.decode('utf-8')

            # Basic validation - check if mostly printable
            printable_ratio = sum(1 for c in text if c.isprintable() or c in '\n\r\t') / len(text) if text else 0

            if printable_ratio < 0.7 and password is not None:
                error_msg = 'Decryption failed: Invalid password or corrupted data'
                logger.warning(f"  Decryption validation failed (printable ratio: {printable_ratio:.2f})")
                log_response('/decrypt', 400, error=error_msg)
                return jsonify({
                    'error': error_msg
                }), 400

            if DEBUG_MODE:
                logger.debug(f"  Decryption complete (output length: {len(text)}, printable ratio: {printable_ratio:.2f})")

            response = {
                'success': True,
                'text': text,
                'decrypted': True,
                'password_protected': has_password
            }

            log_response('/decrypt', 200, response)
            return jsonify(response)

        except UnicodeDecodeError:
            if password is not None:
                error_msg = 'Decryption failed: Invalid password or corrupted data'
                logger.warning(f"  Unicode decode error - likely wrong password")
                log_response('/decrypt', 400, error=error_msg)
                return jsonify({
                    'error': error_msg
                }), 400
            else:
                error_msg = 'Decryption failed: Corrupted data or invalid encoding'
                log_response('/decrypt', 400, error=error_msg)
                return jsonify({
                    'error': error_msg
                }), 400

    except ValueError as e:
        error_msg = f'Invalid cat sounds: {str(e)}'
        log_response('/decrypt', 400, error=error_msg)
        return jsonify({
            'error': error_msg
        }), 400

    except Exception as e:
        error_msg = f'Decryption failed: {str(e)}'
        log_response('/decrypt', 500, error=error_msg)
        return jsonify({
            'error': error_msg
        }), 500


@bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    Calls the API index to verify the service is running correctly.

    Returns:
        JSON with health status
    """
    log_request('/health', 'GET')

    try:
        port = os.environ.get('PORT', 5000)
        api_url = os.environ.get('API_URL', f'http://localhost:{port}').rstrip('/')
        check_url = f'{api_url}{API_PREFIX}/'

        if DEBUG_MODE:
            logger.debug(f"  Health check: calling {check_url}")

        # Call the index endpoint to check if API is responding
        response = requests.get(check_url, timeout=5)

        if response.status_code == 200:
            result = {
                'status': 'OK',
                'api_url': check_url,
                'api_responsive': True
            }
            log_response('/health', 200, result)
            return jsonify(result)
        else:
            error_msg = f'API returned status code {response.status_code}'
            result = {
                'status': 'ERROR',
                'error': error_msg,
                'api_url': check_url,
                'api_responsive': False
            }
            log_response('/health', 503, error=error_msg)
            return jsonify(result), 503

    except requests.exceptions.Timeout:
        error_msg = 'Request timed out'
        result = {
            'status': 'ERROR',
            'error': error_msg,
            'api_url': check_url,
            'api_responsive': False
        }
        log_response('/health', 503, error=error_msg)
        return jsonify(result), 503

    except requests.exceptions.ConnectionError as e:
        error_msg = f'Connection failed: {str(e)}'
        result = {
            'status': 'ERROR',
            'error': error_msg,
            'api_url': check_url,
            'api_responsive': False
        }
        log_response('/health', 503, error=error_msg)
        return jsonify(result), 503

    except Exception as e:
        error_msg = str(e)
        result = {
            'status': 'ERROR',
            'error': error_msg,
            'api_url': check_url,
            'api_responsive': False
        }
        log_response('/health', 503, error=error_msg)
        return jsonify(result), 503


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 Error: {request.path} not found - Client: {request.remote_addr}")
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            f'{API_PREFIX}/',
            f'{API_PREFIX}/encrypt',
            f'{API_PREFIX}/decrypt',
            f'{API_PREFIX}/health',
        ]
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    logger.warning(f"405 Error: Method {request.method} not allowed for {request.path} - Client: {request.remote_addr}")
    return jsonify({
        'error': 'Method not allowed for this endpoint'
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 Internal Server Error: {str(error)} - Client: {request.remote_addr}")
    return jsonify({
        'error': 'Internal server error'
    }), 500


app.register_blueprint(bp, url_prefix=API_PREFIX)


if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    print(f"🐱 PurrCrypt API starting on {host}:{port}")
    print(f"   API prefix: {API_PREFIX}")
    print(f"   Debug mode: {debug}")
    print(f"   Logging level: {'DEBUG' if DEBUG_MODE else 'INFO'}")

    logger.info(f"Starting PurrCrypt API server on {host}:{port} (prefix: {API_PREFIX})")
    if DEBUG_MODE:
        logger.debug("Debug logging enabled - all requests and responses will be logged")

    app.run(host=host, port=port, debug=debug)
