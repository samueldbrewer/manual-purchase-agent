"""
Admin endpoints for managing demo keys and monitoring usage
Protected with basic auth for internal use
"""

from flask import Blueprint, request, jsonify, make_response
from middleware.demo_auth import create_demo_key, list_demo_keys, DEMO_KEYS
from functools import wraps
import base64
import os
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

def require_admin_auth(f):
    """Simple admin authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_admin_credentials(auth.username, auth.password):
            return make_response(
                jsonify({'error': 'Admin authentication required'}),
                401,
                {'WWW-Authenticate': 'Basic realm="Admin Area"'}
            )
        return f(*args, **kwargs)
    return decorated

def check_admin_credentials(username, password):
    """Check admin credentials - in production use proper auth"""
    admin_user = os.environ.get('ADMIN_USER', 'admin')
    admin_pass = os.environ.get('ADMIN_PASS', 'partspro2024!')
    return username == admin_user and password == admin_pass

@admin_bp.route('/demo-keys', methods=['GET'])
@require_admin_auth
def get_demo_keys():
    """List all demo keys and their status"""
    try:
        keys_info = list_demo_keys()
        return jsonify({
            'success': True,
            'keys': keys_info,
            'total': len(keys_info)
        })
    except Exception as e:
        logger.error(f"Error listing demo keys: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/demo-keys', methods=['POST'])
@require_admin_auth
def create_demo_key_endpoint():
    """Create a new demo key"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('company') or not data.get('contact'):
            return jsonify({'error': 'Company and contact are required'}), 400
        
        # Create the demo key
        demo_key = create_demo_key(
            company=data['company'],
            contact=data['contact'],
            days=data.get('days', 7),
            usage_limit=data.get('usage_limit', 100)
        )
        
        return jsonify({
            'success': True,
            'demo_key': demo_key,
            'company': data['company'],
            'contact': data['contact'],
            'expires_in_days': data.get('days', 7),
            'usage_limit': data.get('usage_limit', 100),
            'demo_url': f"{request.host_url}customer-demo",
            'instructions': f"Use header: X-Demo-Key: {demo_key}"
        })
        
    except Exception as e:
        logger.error(f"Error creating demo key: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/demo-keys/<demo_key>/disable', methods=['POST'])
@require_admin_auth
def disable_demo_key(demo_key):
    """Disable a demo key"""
    try:
        if demo_key in DEMO_KEYS:
            # Set usage to max to effectively disable
            DEMO_KEYS[demo_key]['current_usage'] = DEMO_KEYS[demo_key]['usage_limit']
            
            return jsonify({
                'success': True,
                'message': f'Demo key disabled: {demo_key[:8]}...',
                'company': DEMO_KEYS[demo_key]['company']
            })
        else:
            return jsonify({'error': 'Demo key not found'}), 404
            
    except Exception as e:
        logger.error(f"Error disabling demo key: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/demo-usage', methods=['GET'])
@require_admin_auth
def get_demo_usage():
    """Get demo usage statistics"""
    try:
        # Read usage log
        usage_stats = []
        try:
            with open('logs/demo_usage.log', 'r') as f:
                lines = f.readlines()[-100:]  # Last 100 entries
                for line in lines:
                    try:
                        import json
                        usage_stats.append(json.loads(line.strip()))
                    except:
                        continue
        except FileNotFoundError:
            pass
        
        # Calculate summary
        total_requests = len(usage_stats)
        companies = set(stat.get('company', 'Unknown') for stat in usage_stats)
        endpoints = {}
        
        for stat in usage_stats:
            endpoint = stat.get('endpoint', 'unknown')
            endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
        
        return jsonify({
            'success': True,
            'total_requests': total_requests,
            'unique_companies': len(companies),
            'companies': list(companies),
            'endpoint_usage': endpoints,
            'recent_usage': usage_stats[-20:] if usage_stats else []  # Last 20 entries
        })
        
    except Exception as e:
        logger.error(f"Error getting demo usage: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/demo-summary', methods=['GET'])
@require_admin_auth
def demo_summary():
    """Get overall demo system summary"""
    try:
        keys_info = list_demo_keys()
        active_keys = [k for k in keys_info if not k['expired']]
        
        return jsonify({
            'success': True,
            'total_keys': len(keys_info),
            'active_keys': len(active_keys),
            'expired_keys': len(keys_info) - len(active_keys),
            'demo_url': f"{request.host_url}customer-demo",
            'admin_instructions': {
                'create_key': 'POST /api/admin/demo-keys with {"company": "...", "contact": "..."}',
                'list_keys': 'GET /api/admin/demo-keys',
                'usage_stats': 'GET /api/admin/demo-usage',
                'disable_key': 'POST /api/admin/demo-keys/{key}/disable'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting demo summary: {e}")
        return jsonify({'error': str(e)}), 500