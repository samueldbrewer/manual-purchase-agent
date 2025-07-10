"""Part resolver service for finding OEM part numbers."""

import os
from serpapi import GoogleSearch
import logging

logger = logging.getLogger(__name__)

class PartResolver:
    """Service for resolving generic part descriptions to OEM part numbers."""
    
    def __init__(self, serpapi_key=None, openai_api_key=None):
        self.serpapi_key = serpapi_key or os.environ.get('SERPAPI_KEY')
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
    
    def resolve_part(self, description, make, model):
        """Resolve a part description to OEM part number."""
        try:
            # Try web search first
            web_result = self._search_web_for_part(description, make, model)
            
            # Try AI resolution
            ai_result = self._ai_resolve_part(description, make, model)
            
            # Combine results and return best match
            best_result = self._select_best_result(web_result, ai_result)
            
            return {
                "success": True,
                "recommended_result": best_result,
                "results": {
                    "web_search": web_result,
                    "ai_search": ai_result
                }
            }
            
        except Exception as e:
            logger.error(f"Error resolving part: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommended_result": None,
                "results": {}
            }
    
    def _search_web_for_part(self, description, make, model):
        """Search web for part using SerpAPI."""
        try:
            if not self.serpapi_key:
                return {"error": "SERPAPI_KEY not configured"}
            
            query = f"{make} {model} {description} OEM part number"
            
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 5
            })
            
            results = search.get_dict()
            parts = []
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    # Extract potential part numbers from title and snippet
                    text = f"{result.get('title', '')} {result.get('snippet', '')}"
                    part_numbers = self._extract_part_numbers_from_text(text)
                    
                    if part_numbers:
                        parts.extend(part_numbers)
            
            return {
                "success": True,
                "parts": parts[:5],  # Limit to top 5
                "confidence": 0.7 if parts else 0.0
            }
            
        except Exception as e:
            return {"error": str(e), "success": False, "parts": [], "confidence": 0.0}
    
    def _ai_resolve_part(self, description, make, model):
        """Use AI to resolve part description."""
        try:
            if not self.openai_api_key:
                return {"error": "OpenAI API key not configured"}
            
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""
            For a {make} {model}, find the OEM part number for: {description}
            
            Respond with just the part number and description in this format:
            "PART123", "Part Description"
            
            If you cannot determine the exact part number, respond with:
            "UNKNOWN", "Cannot determine exact OEM part number"
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            
            if "UNKNOWN" not in result:
                return {
                    "success": True,
                    "oem_part_number": result.split(',')[0].strip().strip('"'),
                    "description": result.split(',')[1].strip().strip('"') if ',' in result else description,
                    "confidence": 0.8
                }
            else:
                return {
                    "success": False,
                    "error": "Could not determine OEM part number",
                    "confidence": 0.0
                }
                
        except Exception as e:
            return {"error": str(e), "success": False, "confidence": 0.0}
    
    def _extract_part_numbers_from_text(self, text):
        """Extract potential part numbers from text."""
        import re
        
        # Common part number patterns
        patterns = [
            r'\b[A-Z0-9]{6,12}\b',  # Alphanumeric codes
            r'\b\d{2,4}[A-Z]{1,3}\d{2,6}\b',  # Number-letter-number patterns
            r'\b[A-Z]{2,4}\d{4,8}\b'  # Letter-number patterns
        ]
        
        part_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text.upper())
            for match in matches:
                if len(match) >= 6:  # Minimum length for part numbers
                    part_numbers.append({
                        "oem_part_number": match,
                        "description": "Found in search results",
                        "confidence": 0.6
                    })
        
        return part_numbers[:3]  # Return top 3 matches
    
    def _select_best_result(self, web_result, ai_result):
        """Select the best result based on confidence scores."""
        web_confidence = web_result.get("confidence", 0.0) if web_result.get("success") else 0.0
        ai_confidence = ai_result.get("confidence", 0.0) if ai_result.get("success") else 0.0
        
        if ai_confidence > web_confidence:
            return ai_result
        elif web_result.get("parts"):
            return web_result["parts"][0]  # Return best web result
        else:
            return {
                "oem_part_number": "NOT_FOUND",
                "description": "Could not resolve part number",
                "confidence": 0.0
            }

# Standalone function wrapper for backwards compatibility
def resolve_part_name(description, make=None, model=None, use_database=True, use_manual_search=True, use_web_search=True, save_results=True):
    """Standalone function wrapper for part resolution."""
    try:
        resolver = PartResolver()
        
        # If make and model are provided, use them
        if make and model:
            result = resolver.resolve_part(description, make, model)
        else:
            # Try to resolve without make/model
            result = resolver.resolve_part(description, "Generic", "Equipment")
        
        # Convert to expected API format
        if result['success'] and result.get('recommended_result'):
            recommended = result['recommended_result']
            return {
                'success': True,
                'recommended_result': {
                    'oem_part_number': recommended.get('oem_part_number', 'NOT_FOUND'),
                    'description': recommended.get('description', description),
                    'confidence': recommended.get('confidence', 0.0),
                    'selection_metadata': {
                        'selected_from': 'part_resolver',
                        'composite_score': recommended.get('confidence', 0.0)
                    }
                },
                'results': result.get('results', {})
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Part resolution failed'),
                'recommended_result': {
                    'oem_part_number': 'NOT_FOUND',
                    'description': description,
                    'confidence': 0.0
                }
            }
    
    except Exception as e:
        logger.error(f"Error in resolve_part_name: {e}")
        return {
            'success': False,
            'error': str(e),
            'recommended_result': {
                'oem_part_number': 'NOT_FOUND',
                'description': description,
                'confidence': 0.0
            }
        }