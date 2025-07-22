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
            'message': 'Demo API error - contact samueldbrewer@gmail.com for support'
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
            'message': 'Demo API error - contact samueldbrewer@gmail.com for support'
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
            'message': 'Demo API error - contact samueldbrewer@gmail.com for support'
        }), 500

@demo_bp.route('/manuals/process', methods=['POST'])
@require_demo_key
def demo_manual_process():
    """Demo version of manual processing - accepts PDF URL and processes directly"""
    try:
        data = request.json
        
        # Validate required fields
        pdf_url = data.get('pdf_url')
        make = data.get('make', 'Unknown')
        model = data.get('model', 'Unknown')
        
        if not pdf_url:
            return jsonify({
                'error': 'pdf_url is required',
                'message': 'Please provide a PDF URL to process'
            }), 400
        
        logger.info(f"Demo manual processing for {g.demo_key_info['company']}: {pdf_url}")
        
        # Import required services
        from services.manual_finder import download_manual as download_manual_service
        from services.manual_parser import extract_text_from_pdf, extract_information
        import os
        
        local_path = None
        
        try:
            # Download PDF directly from URL
            logger.info(f"Downloading PDF from: {pdf_url}")
            local_path = download_manual_service(pdf_url)
            logger.info(f"PDF downloaded to: {local_path}")
            
            # Check if file exists
            if not os.path.exists(local_path):
                raise Exception(f"Downloaded file not found at {local_path}")
            
            # Extract text from PDF
            logger.info("Extracting text from PDF...")
            text = extract_text_from_pdf(local_path)
            logger.info(f"Extracted {len(text)} characters of text")
            logger.info(f"Text preview (first 500 chars): {text[:500]}")
            
            # Check if we actually got meaningful text
            if len(text.strip()) < 100:
                logger.warning(f"Very little text extracted ({len(text)} chars), PDF might be image-based or corrupted")
            
            # Use AI to extract comprehensive information
            logger.info("Processing with AI...")
            extracted_info = extract_information(text)
            logger.info(f"AI extraction results: {len(extracted_info.get('error_codes', []))} error codes, {len(extracted_info.get('part_numbers', []))} part numbers")
            logger.info(f"Manual subject identified: {extracted_info.get('manual_subject', 'Unknown')}")
            
            # Build comprehensive response
            result = {
                'success': True,
                'pdf_url': pdf_url,
                'make': make,
                'model': model,
                'processing_method': 'Direct PDF URL Processing with GPT-4.1-Nano',
                'ai_model': 'gpt-4o-mini',
                'extraction_source': 'Real-time AI extraction from PDF text',
                'manual_subject': extracted_info.get('manual_subject', 'Unknown'),
                
                # Error codes with structured format
                'error_codes': extracted_info.get('error_codes', []),
                'error_codes_count': len(extracted_info.get('error_codes', [])),
                'error_codes_format': 'Error Code Number, Short Error Description',
                
                # Part numbers with structured format  
                'part_numbers': extracted_info.get('part_numbers', []),
                'part_numbers_count': len(extracted_info.get('part_numbers', [])),
                'part_numbers_format': 'OEM Part Number, Short Part Description',
                
                # Additional extracted information
                'common_problems': extracted_info.get('common_problems', []),
                'maintenance_procedures': extracted_info.get('maintenance_procedures', []),
                'safety_warnings': extracted_info.get('safety_warnings', []),
                
                'processing_timestamp': request.json.get('timestamp') or 'Not provided'
            }
            
            logger.info(f"Successfully processed PDF: {len(result['error_codes'])} error codes, {len(result['part_numbers'])} part numbers")
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}", exc_info=True)
            result = {
                'success': False,
                'error': str(e),
                'pdf_url': pdf_url,
                'make': make,
                'model': model,
                'processing_method': 'Direct PDF URL Processing with GPT-4.1-Nano',
                'message': 'Failed to process PDF - check URL accessibility'
            }
        
        finally:
            # Clean up temporary file
            if local_path and os.path.exists(local_path):
                try:
                    os.remove(local_path)
                    logger.info(f"Cleaned up temporary file: {local_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {local_path}: {e}")
        
        # Add watermark
        result = add_demo_watermark(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demo manual processing error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Demo API error - contact samueldbrewer@gmail.com for support'
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
            'message': 'Demo API error - contact samueldbrewer@gmail.com for support'
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
            'message': 'Demo API error - contact samueldbrewer@gmail.com for support'
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
            'contact_sales': 'samueldbrewer@gmail.com'
        })
    except Exception as e:
        logger.error(f"Demo status error: {e}")
        return jsonify({'error': str(e)}), 500