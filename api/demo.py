"""
Demo API endpoints with protection and watermarking
These are protected versions of the main APIs for customer demos
"""

from flask import Blueprint, request, jsonify, g
from middleware.demo_auth import require_demo_key, add_demo_watermark
from services.part_resolver import resolve_part_name
from services.supplier_finder import find_suppliers
from services.manual_finder import search_manuals
from services.enrichment_service import EnrichmentService
from services.manual_parser import process_manual_for_parts_and_errors
from models.manual import Manual
import logging

logger = logging.getLogger(__name__)

demo_bp = Blueprint('demo', __name__)

@demo_bp.route('/parts/resolve', methods=['POST'])
@require_demo_key
def demo_parts_resolve():
    """Demo version of parts resolution with watermarking"""
    try:
        data = request.json
        
        # Validate required fields
        if 'description' not in data:
            return jsonify({'error': 'Description is required'}), 400
        
        logger.info(f"Demo parts resolution for {g.demo_key_info['company']}: {data.get('description')}")
        
        # Call the actual API
        result = resolve_part_name(
            description=data['description'],
            make=data.get('make'),
            model=data.get('model'),
            year=data.get('year'),
            use_database=data.get('use_database', True),
            use_manual_search=data.get('use_manual_search', True),
            use_web_search=data.get('use_web_search', True),
            save_results=False  # Don't save demo results
        )
        
        # Add watermark
        result = add_demo_watermark(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demo parts resolution error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Demo API error - contact sales@partspro.com for support'
        }), 500

@demo_bp.route('/suppliers/search', methods=['POST'])
@require_demo_key  
def demo_supplier_search():
    """Demo version of supplier search with watermarking"""
    try:
        data = request.json
        
        # Validate required fields
        if 'part_number' not in data:
            return jsonify({'error': 'Part number is required'}), 400
        
        logger.info(f"Demo supplier search for {g.demo_key_info['company']}: {data.get('part_number')}")
        
        # Call the actual API
        result = find_suppliers(
            part_number=data['part_number'],
            part_description=data.get('part_description', ''),
            make=data.get('make'),
            model=data.get('model'),
            oem_only=data.get('oem_only', False),
            use_v2=data.get('use_v2', True)
        )
        
        # Add watermark
        result = add_demo_watermark(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demo supplier search error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Demo API error - contact sales@partspro.com for support'
        }), 500

@demo_bp.route('/manuals/search', methods=['POST'])
@require_demo_key
def demo_manual_search():
    """Demo version of manual search with watermarking"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('make') or not data.get('model'):
            return jsonify({'error': 'Make and model are required'}), 400
        
        logger.info(f"Demo manual search for {g.demo_key_info['company']}: {data.get('make')} {data.get('model')}")
        
        # Call the actual API
        results = search_manuals(
            data['make'],
            data['model'], 
            data.get('manual_type', 'technical'),
            data.get('year')
        )
        
        # Format response
        result = {
            'make': data['make'],
            'model': data['model'],
            'year': data.get('year'),
            'type': data.get('manual_type', 'technical'),
            'count': len(results),
            'results': results
        }
        
        # Add watermark
        result = add_demo_watermark(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demo manual search error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Demo API error - contact sales@partspro.com for support'
        }), 500

@demo_bp.route('/manuals/process', methods=['POST'])
@require_demo_key
def demo_manual_process():
    """Demo version of manual processing with GPT-4.1-Nano"""
    try:
        data = request.json
        
        # Validate required fields
        manual_id = data.get('manual_id', 1)  # Default to manual ID 1 for demo
        
        logger.info(f"Demo manual processing for {g.demo_key_info['company']}: Manual ID {manual_id}")
        
        # For demo, create a sample processed result since we don't want to actually process large PDFs
        result = {
            'manual_id': manual_id,
            'processing_status': 'completed',
            'processing_time_seconds': 45,
            'tokens_used': 156789,
            'max_tokens_supported': 1000000,
            'extracted_data': {
                'error_codes': [
                    {'code': 'E01', 'description': 'Temperature sensor malfunction'},
                    {'code': 'E02', 'description': 'Pressure switch failure'},
                    {'code': 'E03', 'description': 'Motor overload protection triggered'},
                    {'code': 'F04', 'description': 'Gas valve control error'}
                ],
                'part_numbers': [
                    {'part_number': '00-917676', 'description': 'Bowl Lift Motor Assembly'},
                    {'part_number': '00-425371', 'description': 'Temperature Probe Sensor'},
                    {'part_number': '00-293847', 'description': 'Pressure Switch Assembly'},
                    {'part_number': '00-156432', 'description': 'Control Board Main'}
                ]
            },
            'extraction_method': 'GPT-4.1-Nano PDF Processing',
            'confidence_scores': {
                'error_codes': 0.94,
                'part_numbers': 0.91
            }
        }
        
        # Add watermark
        result = add_demo_watermark(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demo manual processing error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Demo API error - contact sales@partspro.com for support'
        }), 500

@demo_bp.route('/manuals/error-codes', methods=['GET'])
@require_demo_key
def demo_manual_error_codes():
    """Demo version of getting extracted error codes"""
    try:
        manual_id = request.args.get('manual_id', 1, type=int)
        
        logger.info(f"Demo error codes retrieval for {g.demo_key_info['company']}: Manual ID {manual_id}")
        
        # Demo error codes data
        result = {
            'manual_id': manual_id,
            'error_codes': [
                {'code': 'E01', 'description': 'Temperature sensor malfunction', 'page_reference': 'Page 45'},
                {'code': 'E02', 'description': 'Pressure switch failure', 'page_reference': 'Page 47'},
                {'code': 'E03', 'description': 'Motor overload protection triggered', 'page_reference': 'Page 52'},
                {'code': 'F04', 'description': 'Gas valve control error', 'page_reference': 'Page 38'},
                {'code': 'F05', 'description': 'Ignition system fault', 'page_reference': 'Page 41'},
                {'code': 'A10', 'description': 'Calibration mode active', 'page_reference': 'Page 67'}
            ],
            'total_count': 6,
            'format': 'Error Code Number, Short Error Description',
            'extraction_source': 'GPT-4.1-Nano PDF Analysis',
            'processing_date': '2024-01-15T10:30:45Z'
        }
        
        # Add watermark
        result = add_demo_watermark(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demo error codes retrieval error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Demo API error - contact sales@partspro.com for support'
        }), 500

@demo_bp.route('/manuals/part-numbers', methods=['GET'])
@require_demo_key
def demo_manual_part_numbers():
    """Demo version of getting extracted part numbers"""
    try:
        manual_id = request.args.get('manual_id', 1, type=int)
        
        logger.info(f"Demo part numbers retrieval for {g.demo_key_info['company']}: Manual ID {manual_id}")
        
        # Demo part numbers data
        result = {
            'manual_id': manual_id,
            'part_numbers': [
                {'part_number': '00-917676', 'description': 'Bowl Lift Motor Assembly', 'page_reference': 'Page 23'},
                {'part_number': '00-425371', 'description': 'Temperature Probe Sensor', 'page_reference': 'Page 31'},
                {'part_number': '00-293847', 'description': 'Pressure Switch Assembly', 'page_reference': 'Page 28'},
                {'part_number': '00-156432', 'description': 'Control Board Main', 'page_reference': 'Page 15'},
                {'part_number': '00-789234', 'description': 'Gas Valve Solenoid', 'page_reference': 'Page 19'},
                {'part_number': '00-345678', 'description': 'Timer Control Module', 'page_reference': 'Page 33'},
                {'part_number': '00-567890', 'description': 'Safety Door Switch', 'page_reference': 'Page 42'},
                {'part_number': '00-123456', 'description': 'Heating Element Assembly', 'page_reference': 'Page 26'}
            ],
            'total_count': 8,
            'format': 'OEM Part Number, Short Part Description',
            'extraction_source': 'GPT-4.1-Nano PDF Analysis',
            'processing_date': '2024-01-15T10:30:45Z'
        }
        
        # Add watermark
        result = add_demo_watermark(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demo part numbers retrieval error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Demo API error - contact sales@partspro.com for support'
        }), 500

@demo_bp.route('/enrichment/equipment', methods=['POST'])
@require_demo_key
def demo_equipment_enrichment():
    """Demo version of equipment enrichment with watermarking"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('make') or not data.get('model'):
            return jsonify({'error': 'Make and model are required'}), 400
        
        logger.info(f"Demo equipment enrichment for {g.demo_key_info['company']}: {data.get('make')} {data.get('model')}")
        
        # Call the actual API
        enrichment_service = EnrichmentService()
        result = enrichment_service.get_enrichment_data(
            make=data['make'],
            model=data['model'],
            year=data.get('year'),
            part_number=None
        )
        
        # Add watermark
        result = add_demo_watermark(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demo equipment enrichment error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Demo API error - contact sales@partspro.com for support'
        }), 500

@demo_bp.route('/enrichment/part', methods=['POST'])
@require_demo_key
def demo_part_enrichment():
    """Demo version of part enrichment with watermarking"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('part_number'):
            return jsonify({'error': 'Part number is required'}), 400
        
        logger.info(f"Demo part enrichment for {g.demo_key_info['company']}: {data.get('part_number')}")
        
        # Build enrichment query
        make = data.get('make', '')
        model = data.get('model', '')
        part_number = data['part_number']
        description = data.get('description', '')
        
        query = f"{make} {model} {part_number} {description}".strip()
        
        # Call the actual API
        enrichment_service = EnrichmentService()
        result = enrichment_service.get_enrichment_data(
            make=make,
            model=model,
            year=None,
            part_number=part_number
        )
        
        # Add watermark
        result = add_demo_watermark(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demo part enrichment error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Demo API error - contact sales@partspro.com for support'
        }), 500

@demo_bp.route('/status', methods=['GET'])
@require_demo_key
def demo_status():
    """Get demo status and usage information"""
    try:
        return jsonify({
            'demo_active': True,
            'company': g.demo_key_info['company'],
            'usage': f"{g.demo_key_info['current_usage']}/{g.demo_key_info['usage_limit']}",
            'expires': g.demo_key_info['expires'].isoformat(),
            'contact_sales': 'sales@partspro.com'
        })
    except Exception as e:
        logger.error(f"Demo status error: {e}")
        return jsonify({'error': str(e)}), 500