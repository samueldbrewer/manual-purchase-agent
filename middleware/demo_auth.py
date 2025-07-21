"""
Demo API key authentication middleware
Protects customer demo endpoints from unauthorized access
"""

from flask import request, jsonify, g
import logging
import os
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

# Demo API keys (in production, store in database)
DEMO_KEYS = {
    'prefix_test_key': {
        'company': 'Test/Demo Access',
        'contact': 'demo@partspro.com',
        'expires': datetime.now() + timedelta(days=365000),  # Never expires (1000 years)
        'usage_limit': 999999,  # Unlimited usage
        'current_usage': 0
    },
    'admin_full_access_2024': {
        'company': 'PartsPro Admin Access',
        'contact': 'admin@partspro.com', 
        'expires': datetime.now() + timedelta(days=365000),  # Never expires
        'usage_limit': 999999,  # Unlimited usage
        'current_usage': 0
    },
    'demo_prospect_002': {
        'company': 'Beta Industries', 
        'contact': 'jane.smith@beta.com',
        'expires': datetime.now() + timedelta(days=3),
        'usage_limit': 50,
        'current_usage': 0
    },
    # Add more as needed
}

def require_demo_key(f):
    """Decorator to require demo API key for protected endpoints"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get demo key from header
        demo_key = request.headers.get('X-Demo-Key')
        
        if not demo_key:
            logger.warning(f"Demo access attempt without key from IP: {request.remote_addr}")
            return jsonify({
                'error': 'Demo API key required',
                'message': 'Contact sales@partspro.com for demo access',
                'status': 'unauthorized'
            }), 401
        
        # Validate demo key
        key_info = DEMO_KEYS.get(demo_key)
        if not key_info:
            logger.warning(f"Invalid demo key attempted: {demo_key[:8]}... from IP: {request.remote_addr}")
            return jsonify({
                'error': 'Invalid demo API key',
                'message': 'Contact sales@partspro.com for valid demo access',
                'status': 'unauthorized'
            }), 401
        
        # Check expiration
        if datetime.now() > key_info['expires']:
            logger.info(f"Expired demo key used: {key_info['company']}")
            return jsonify({
                'error': 'Demo API key expired',
                'message': 'Your demo period has ended. Contact sales@partspro.com to continue',
                'status': 'expired'
            }), 401
        
        # Check usage limit
        if key_info['current_usage'] >= key_info['usage_limit']:
            logger.info(f"Demo usage limit exceeded: {key_info['company']}")
            return jsonify({
                'error': 'Demo usage limit exceeded',
                'message': 'You have reached your demo limit. Contact sales@partspro.com for full access',
                'status': 'limit_exceeded'
            }), 429
        
        # Log usage
        log_demo_usage(demo_key, key_info, request)
        
        # Increment usage counter
        key_info['current_usage'] += 1
        
        # Store key info in request context
        g.demo_key_info = key_info
        g.demo_key = demo_key
        
        return f(*args, **kwargs)
    
    return decorated_function

def log_demo_usage(demo_key, key_info, request):
    """Log demo API usage for tracking and follow-up"""
    try:
        usage_log = {
            'timestamp': datetime.now().isoformat(),
            'demo_key': demo_key[:8] + '...',  # Partially mask key
            'company': key_info['company'],
            'contact': key_info['contact'],
            'endpoint': request.endpoint,
            'method': request.method,
            'url': request.url,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'usage_count': key_info['current_usage'] + 1,
            'usage_limit': key_info['usage_limit']
        }
        
        # Log to file (in production, use proper logging service)
        log_file = os.path.join('logs', 'demo_usage.log')
        os.makedirs('logs', exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(usage_log) + '\n')
        
        logger.info(f"Demo usage logged: {key_info['company']} - {request.endpoint}")
        
    except Exception as e:
        logger.error(f"Failed to log demo usage: {e}")

def add_demo_watermark(response_data):
    """Add watermark to demo API responses"""
    if hasattr(g, 'demo_key_info'):
        # Add watermark information
        watermark = {
            '_demo_mode': True,
            '_demo_company': g.demo_key_info['company'],
            '_demo_usage': f"{g.demo_key_info['current_usage'] + 1}/{g.demo_key_info['usage_limit']}",
            '_contact_sales': 'Full production access: sales@partspro.com',
            '_demo_expires': g.demo_key_info['expires'].isoformat()
        }
        
        # Add watermark to response
        if isinstance(response_data, dict):
            response_data.update(watermark)
        elif hasattr(response_data, '__dict__'):
            response_data.__dict__.update(watermark)
    
    return response_data

def create_demo_key(company, contact, days=7, usage_limit=100):
    """Create a new demo API key"""
    # Generate unique key
    raw_key = f"{company}_{contact}_{datetime.now().isoformat()}"
    demo_key = f"demo_{hashlib.md5(raw_key.encode()).hexdigest()[:12]}"
    
    # Add to keys
    DEMO_KEYS[demo_key] = {
        'company': company,
        'contact': contact,
        'expires': datetime.now() + timedelta(days=days),
        'usage_limit': usage_limit,
        'current_usage': 0,
        'created': datetime.now().isoformat()
    }
    
    logger.info(f"Created demo key for {company}: {demo_key}")
    return demo_key

def list_demo_keys():
    """List all demo keys and their status"""
    keys_info = []
    for key, info in DEMO_KEYS.items():
        keys_info.append({
            'key': key[:8] + '...',
            'company': info['company'],
            'contact': info['contact'],
            'expires': info['expires'].isoformat(),
            'usage': f"{info['current_usage']}/{info['usage_limit']}",
            'expired': datetime.now() > info['expires']
        })
    return keys_info