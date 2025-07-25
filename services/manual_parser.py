"""Manual parser service for extracting text and data from PDF manuals."""

import fitz  # PyMuPDF
import openai
import os
import logging

logger = logging.getLogger(__name__)

class ManualParser:
    """Service for parsing PDF manuals and extracting information."""
    
    def __init__(self, openai_api_key=None):
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            
            return {
                "success": True,
                "text": text,
                "page_count": page_count
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "page_count": 0
            }
    
    def extract_error_codes(self, pdf_path):
        """Extract error codes from manual using GPT-4.1-Nano."""
        try:
            # Extract text first
            text_result = self.extract_text_from_pdf(pdf_path)
            if not text_result["success"]:
                return text_result
            
            text = text_result["text"]
            
            # Use OpenAI to extract error codes
            if self.openai_api_key:
                prompt = """
                Extract all error codes from this manual text. Return them in this format:
                "Error Code Number", "Short Error Description"
                
                For example:
                "E01", "Temperature sensor failure"
                "F23", "Water pump malfunction"
                
                Text to analyze:
                """ + text[:50000]  # Limit text length
                
                response = openai.ChatCompletion.create(
                    model="gpt-4.1-mini-2025-04-14",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                
                error_codes = response.choices[0].message.content
                
                return {
                    "success": True,
                    "error_codes": error_codes,
                    "raw_text": text
                }
            else:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "error_codes": "",
                    "raw_text": text
                }
                
        except Exception as e:
            logger.error(f"Error extracting error codes: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_codes": "",
                "raw_text": ""
            }
    
    def extract_part_numbers(self, pdf_path):
        """Extract OEM part numbers from manual using GPT-4.1-Nano."""
        try:
            # Extract text first
            text_result = self.extract_text_from_pdf(pdf_path)
            if not text_result["success"]:
                return text_result
            
            text = text_result["text"]
            
            # Use OpenAI to extract part numbers
            if self.openai_api_key:
                prompt = """
                Extract all OEM part numbers from this manual text. Return them in this format:
                "OEM Part Number", "Short Part Description"
                
                For example:
                "HC21ZE038", "Compressor Motor"
                "58STA090", "Thermostat Assembly"
                
                Text to analyze:
                """ + text[:50000]  # Limit text length
                
                response = openai.ChatCompletion.create(
                    model="gpt-4.1-mini-2025-04-14",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                
                part_numbers = response.choices[0].message.content
                
                return {
                    "success": True,
                    "part_numbers": part_numbers,
                    "raw_text": text
                }
            else:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "part_numbers": "",
                    "raw_text": text
                }
                
        except Exception as e:
            logger.error(f"Error extracting part numbers: {e}")
            return {
                "success": False,
                "error": str(e),
                "part_numbers": "",
                "raw_text": ""
            }

# Standalone function wrappers for backwards compatibility
def extract_text_from_pdf(pdf_path):
    """Standalone function wrapper for text extraction."""
    parser = ManualParser()
    result = parser.extract_text_from_pdf(pdf_path)
    
    if result['success']:
        return result['text']
    else:
        raise Exception(result['error'])

def extract_information(text, manual_id=None):
    """Extract comprehensive information from manual text using GPT-4.1-Nano."""
    try:
        from openai import OpenAI
        import json
        import re
        
        # Initialize OpenAI client
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            logger.error("OpenAI API key not configured - OPENAI_API_KEY environment variable not found")
            return {
                'error_codes': [],
                'part_numbers': [],
                'manual_subject': 'Unknown',
                'common_problems': [],
                'maintenance_procedures': [],
                'safety_warnings': []
            }
        
        logger.info(f"OpenAI API key found: {openai_api_key[:12]}... (length: {len(openai_api_key)})")
        
        # Initialize OpenAI client - handle the proxies error by setting environment first
        try:
            # Set environment variable first to avoid proxies issues
            os.environ['OPENAI_API_KEY'] = openai_api_key
            client = OpenAI()
            logger.info("OpenAI client initialized successfully")
        except Exception as init_error:
            logger.error(f"OpenAI client initialization failed: {init_error}")
            return {
                'error_codes': [],
                'part_numbers': [],
                'manual_subject': 'OpenAI initialization failed',
                'common_problems': [],
                'maintenance_procedures': [],
                'safety_warnings': []
            }
        
        # Limit text to prevent token overflow
        max_text_length = 100000  # ~25K tokens for GPT-4.1-Nano
        if len(text) > max_text_length:
            text = text[:max_text_length]
            logger.info(f"Text truncated to {max_text_length} characters for processing")
        
        prompt = f"""
        Analyze this technical manual and extract the following information in JSON format:

        1. Error codes with descriptions (format: "Error Code Number", "Short Error Description")
        2. OEM part numbers with descriptions (format: "OEM Part Number", "Short Part Description")
        3. Manual subject/equipment type
        4. Common problems mentioned
        5. Maintenance procedures
        6. Safety warnings

        Return a JSON object with this structure:
        {{
            "manual_subject": "Equipment Name/Type",
            "error_codes": [
                {{"code": "E01", "description": "Temperature sensor failure"}},
                {{"code": "F23", "description": "Water pump malfunction"}}
            ],
            "part_numbers": [
                {{"code": "HC21ZE038", "description": "Compressor Motor"}},
                {{"code": "58STA090", "description": "Thermostat Assembly"}}
            ],
            "common_problems": [
                {{"issue": "Unit not cooling", "cause": "Low refrigerant", "solution": "Check for leaks"}},
                {{"issue": "Excessive noise", "cause": "Loose components", "solution": "Tighten mounting bolts"}}
            ],
            "maintenance_procedures": [
                "Clean condenser coils monthly",
                "Replace air filter every 3 months",
                "Check refrigerant levels annually"
            ],
            "safety_warnings": [
                "Disconnect power before servicing",
                "Use proper PPE when handling refrigerants",
                "Never bypass safety controls"
            ]
        }}

        Manual text to analyze:
        {text}
        """
        
        logger.info(f"Processing manual{'ID ' + str(manual_id) if manual_id else ''} with GPT-4.1-mini-2025-04-14")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini-2025-04-14",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.1
            )
            logger.info("OpenAI API call successful")
        except Exception as api_error:
            logger.error(f"OpenAI API call failed: {api_error}")
            return {
                'error_codes': [],
                'part_numbers': [],
                'manual_subject': 'Unknown',
                'common_problems': [],
                'maintenance_procedures': [],
                'safety_warnings': []
            }
        
        # Parse the JSON response
        content = response.choices[0].message.content
        
        # Extract JSON from response (handle cases where model adds extra text)
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            extracted_info = json.loads(json_str)
        else:
            # Fallback parsing
            extracted_info = json.loads(content)
        
        # Ensure all required fields exist
        extracted_info.setdefault('error_codes', [])
        extracted_info.setdefault('part_numbers', [])
        extracted_info.setdefault('manual_subject', 'Unknown')
        extracted_info.setdefault('common_problems', [])
        extracted_info.setdefault('maintenance_procedures', [])
        extracted_info.setdefault('safety_warnings', [])
        
        logger.info(f"Extracted {len(extracted_info['error_codes'])} error codes and {len(extracted_info['part_numbers'])} part numbers")
        
        return extracted_info
        
    except Exception as e:
        logger.error(f"Error extracting information: {e}")
        return {
            'error_codes': [],
            'part_numbers': [],
            'manual_subject': 'Unknown',
            'common_problems': [],
            'maintenance_procedures': [],
            'safety_warnings': []
        }

def extract_components(text, custom_prompt=None):
    """Extract structural components from manual text."""
    try:
        from openai import OpenAI
        import json
        import re
        
        # Initialize OpenAI client
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            logger.error("OpenAI API key not configured")
            return {}
        
        client = OpenAI(api_key=openai_api_key)
        
        # Use custom prompt if provided, otherwise use default
        if custom_prompt:
            prompt = f"{custom_prompt}\n\nManual text:\n{text[:50000]}"
        else:
            prompt = f"""
            Analyze this technical manual and identify key structural components with page ranges.
            
            Return a JSON object with components like:
            {{
                "table_of_contents": {{
                    "title": "Table of Contents",
                    "start_page": 1,
                    "end_page": 2,
                    "description": "Lists all sections with page numbers",
                    "key_information": ["Section names", "Page numbers", "Subsections"]
                }},
                "exploded_view": {{
                    "title": "Parts Breakdown Diagram", 
                    "start_page": 14,
                    "end_page": 18,
                    "description": "Detailed exploded view diagrams",
                    "key_information": ["Part locations", "Assembly relationships", "Part numbers"]
                }}
            }}
            
            Manual text:
            {text[:50000]}
            """
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.1
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            components = json.loads(json_str)
        else:
            components = json.loads(content)
        
        return components
        
    except Exception as e:
        logger.error(f"Error extracting components: {e}")
        return {}