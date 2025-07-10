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
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            
            return {
                "success": True,
                "text": text,
                "page_count": len(doc)
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
                    model="gpt-4",
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
                    model="gpt-4",
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