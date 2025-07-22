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
    """Demo version of manual processing - calls real API"""
    try:
        data = request.json
        
        # Validate required fields
        manual_id = data.get('manual_id', 1)  # Default to manual ID 1 for demo
        
        logger.info(f"Demo manual processing for {g.demo_key_info['company']}: Manual ID {manual_id}")
        
        # Call the real manual processing API
        from api.manuals import process_manual
        from flask import current_app
        
        with current_app.test_request_context(json=data):
            response = process_manual(manual_id)
            
            # Extract the response data
            if hasattr(response, 'get_json'):
                result = response.get_json()
            else:
                result = response[0].get_json() if isinstance(response, tuple) else response
        
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
    """Demo version of getting extracted error codes - uses AI processing"""
    try:
        manual_id = request.args.get('manual_id', 1, type=int)
        
        logger.info(f"Demo error codes retrieval with AI processing for {g.demo_key_info['company']}: Manual ID {manual_id}")
        
        # Get the manual from the database
        from models.manual import Manual
        from services.manual_finder import download_manual as download_manual_service
        from services.manual_parser import extract_text_from_pdf, extract_information
        import os
        
        manual = Manual.query.get(manual_id)
        if not manual:
            return jsonify({'error': f'Manual with ID {manual_id} not found'}), 404
        
        # Download the manual if not already downloaded
        if not manual.local_path or not os.path.exists(manual.local_path):
            try:
                local_path = download_manual_service(manual.url)
                manual.local_path = local_path
                from models import db
                db.session.commit()
            except Exception as e:
                logger.error(f"Failed to download manual: {e}")
                return jsonify({'error': 'Failed to download manual for processing'}), 500
        
        # Extract text and use AI to get error codes
        try:
            text = extract_text_from_pdf(manual.local_path)
            extracted_info = extract_information(text, manual_id)
            
            result = {
                'manual_id': manual_id,
                'manual_title': manual.title,
                'make': manual.make,
                'model': manual.model,
                'error_codes': extracted_info.get('error_codes', []),
                'total_count': len(extracted_info.get('error_codes', [])),
                'format': 'Error Code Number, Short Error Description',
                'extraction_source': 'GPT-4.1-Nano AI Processing',
                'processing_method': 'Real-time AI extraction from PDF text',
                'ai_model': 'gpt-4o-mini'
            }
            
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            return jsonify({'error': f'AI processing failed: {str(e)}'}), 500
        
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
    """Demo version of getting extracted part numbers - uses AI processing"""
    try:
        manual_id = request.args.get('manual_id', 1, type=int)
        
        logger.info(f"Demo part numbers retrieval with AI processing for {g.demo_key_info['company']}: Manual ID {manual_id}")
        
        # Get the manual from the database
        from models.manual import Manual
        from services.manual_finder import download_manual as download_manual_service
        from services.manual_parser import extract_text_from_pdf, extract_information
        import os
        
        manual = Manual.query.get(manual_id)
        if not manual:
            return jsonify({'error': f'Manual with ID {manual_id} not found'}), 404
        
        # Download the manual if not already downloaded
        if not manual.local_path or not os.path.exists(manual.local_path):
            try:
                local_path = download_manual_service(manual.url)
                manual.local_path = local_path
                from models import db
                db.session.commit()
            except Exception as e:
                logger.error(f"Failed to download manual: {e}")
                return jsonify({'error': 'Failed to download manual for processing'}), 500
        
        # Extract text and use AI to get part numbers
        try:
            text = extract_text_from_pdf(manual.local_path)
            extracted_info = extract_information(text, manual_id)
            
            result = {
                'manual_id': manual_id,
                'manual_title': manual.title,
                'make': manual.make,
                'model': manual.model,
                'part_numbers': extracted_info.get('part_numbers', []),
                'total_count': len(extracted_info.get('part_numbers', [])),
                'format': 'OEM Part Number, Short Part Description',
                'extraction_source': 'GPT-4.1-Nano AI Processing',
                'processing_method': 'Real-time AI extraction from PDF text',
                'ai_model': 'gpt-4o-mini'
            }
            
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            return jsonify({'error': f'AI processing failed: {str(e)}'}), 500
        
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