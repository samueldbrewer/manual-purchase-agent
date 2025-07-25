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
        """Resolve a part description to OEM part number using integrated web search and AI analysis."""
        try:
            # Step 1: Perform web search to gather data
            web_result = self._search_web_for_part(description, make, model)
            
            # Step 2: Use AI to analyze web search results and provide intelligent resolution
            ai_result = self._ai_analyze_web_results(description, make, model, web_result)
            
            # Step 3: Select best result using improved logic
            best_result = self._select_best_result_v2(web_result, ai_result, description, make, model)
            
            return {
                "success": True,
                "recommended_result": best_result,
                "results": {
                    "web_search": web_result,
                    "ai_analysis": ai_result
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
    
    def _ai_analyze_web_results(self, description, make, model, web_result):
        """Use AI to analyze web search results and provide intelligent part resolution."""
        try:
            if not self.openai_api_key:
                return {"error": "OpenAI API key not configured", "success": False}
            
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            # Prepare web search context
            web_context = "No web search results available."
            if web_result.get("success") and web_result.get("parts"):
                parts_text = []
                for part in web_result["parts"]:
                    parts_text.append(f"- {part['oem_part_number']}: {part['description']} (confidence: {part['confidence']})")
                web_context = f"Web search found these potential part numbers:\n" + "\n".join(parts_text)
            
            prompt = f"""
            You are an expert in {make} equipment parts. Analyze the following information to find the correct OEM part number.

            Equipment: {make} {model}
            Part needed: {description}

            {web_context}

            Your task:
            1. Analyze the web search results for relevance to the specific part needed
            2. Identify which part number is most likely correct for this specific equipment and part description
            3. Consider the manufacturer's part numbering conventions
            4. Assess the reliability of each source

            Respond in JSON format:
            {{
                "oem_part_number": "XX-XXXXXX",
                "description": "Detailed part description",
                "confidence": 0.95,
                "reasoning": "Explanation of why this is the correct part",
                "validated_against_web": true
            }}

            If no reliable part number can be determined, respond with:
            {{
                "oem_part_number": "NOT_FOUND",
                "description": "Unable to determine OEM part number",
                "confidence": 0.0,
                "reasoning": "Insufficient or unreliable information",
                "validated_against_web": false
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4.1-nano-2025-04-14",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            try:
                parsed_result = json.loads(result)
                return {
                    "success": True,
                    "oem_part_number": parsed_result.get("oem_part_number"),
                    "description": parsed_result.get("description", description),
                    "confidence": parsed_result.get("confidence", 0.0),
                    "reasoning": parsed_result.get("reasoning", ""),
                    "validated_against_web": parsed_result.get("validated_against_web", False)
                }
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {result}")
                return {
                    "success": False,
                    "error": "Failed to parse AI response",
                    "confidence": 0.0
                }
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"error": str(e), "success": False, "confidence": 0.0}
    
    def _extract_part_numbers_from_text(self, text):
        """Extract real OEM part numbers from text using improved patterns."""
        import re
        
        # Exclude common false positives
        blacklist = {
            'MANUAL', 'MANUALS', 'PARTS', 'SERVICE', 'REPAIR', 'GUIDE', 'BOOK',
            'TECHNICAL', 'OPERATION', 'INSTRUCTION', 'DOCUMENT', 'CATALOG',
            'HOBART', 'HENNY', 'PENNY', 'CARRIER', 'TRANE', 'AMERICAN', 'STANDARD'
        }
        
        part_numbers = []
        
        # Pattern 1: Hobart style (00-917676, 00-123456)
        hobart_pattern = r'\b\d{2}-\d{6}\b'
        matches = re.findall(hobart_pattern, text)
        for match in matches:
            part_numbers.append({
                "oem_part_number": match,
                "description": "Hobart OEM part number",
                "confidence": 0.9
            })
        
        # Pattern 2: Henny Penny style (HP-14-026, 67589, 140402)
        hp_patterns = [
            r'\bHP-\d{2}-\d{3}\b',  # HP-14-026
            r'\b\d{5,6}\b'          # 67589, 140402
        ]
        for pattern in hp_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match.upper() not in blacklist and not match.isalpha():
                    part_numbers.append({
                        "oem_part_number": match,
                        "description": "Henny Penny OEM part number", 
                        "confidence": 0.85
                    })
        
        # Pattern 3: General OEM patterns (avoid generic words)
        general_patterns = [
            r'\b[A-Z]{2,3}\d{4,8}\b',    # AB1234567
            r'\b\d{2,4}-[A-Z]{1,3}-\d{2,6}\b',  # 12-AB-34567
            r'\b[A-Z]\d{2}-\d{6}\b'      # A12-123456
        ]
        
        for pattern in general_patterns:
            matches = re.findall(pattern, text.upper())
            for match in matches:
                # Skip if in blacklist or looks like a common word
                if (match.upper() not in blacklist and 
                    not match.replace('-', '').isalpha() and
                    len(match) >= 5):
                    part_numbers.append({
                        "oem_part_number": match,
                        "description": "OEM part number from search",
                        "confidence": 0.7
                    })
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique_parts = []
        for part in sorted(part_numbers, key=lambda x: x['confidence'], reverse=True):
            if part['oem_part_number'] not in seen:
                seen.add(part['oem_part_number'])
                unique_parts.append(part)
        
        return unique_parts[:3]  # Return top 3 matches
    
    def _select_best_result_v2(self, web_result, ai_result, description, make, model):
        """Select the best result using improved logic that considers AI analysis of web data."""
        # Priority 1: AI analysis that validated against web results
        if (ai_result.get("success") and 
            ai_result.get("validated_against_web") and 
            ai_result.get("confidence", 0.0) > 0.7):
            return {
                "oem_part_number": ai_result["oem_part_number"],
                "description": ai_result["description"],
                "confidence": ai_result["confidence"],
                "selection_metadata": {
                    "selected_from": "ai_analysis_validated",
                    "composite_score": ai_result["confidence"],
                    "reasoning": ai_result.get("reasoning", "AI validated against web search")
                }
            }
        
        # Priority 2: High-confidence web result with AI analysis
        if (web_result.get("success") and web_result.get("parts") and
            ai_result.get("success") and ai_result.get("confidence", 0.0) > 0.6):
            best_web_part = web_result["parts"][0]
            return {
                "oem_part_number": ai_result["oem_part_number"],
                "description": ai_result["description"],
                "confidence": min(ai_result["confidence"], 0.9),  # Cap at 0.9 for mixed results
                "selection_metadata": {
                    "selected_from": "ai_analysis_with_web",
                    "composite_score": (ai_result["confidence"] + best_web_part["confidence"]) / 2,
                    "reasoning": ai_result.get("reasoning", "AI analysis based on web search")
                }
            }
        
        # Priority 3: Best web result if AI failed
        if web_result.get("success") and web_result.get("parts"):
            best_web_part = web_result["parts"][0]
            return {
                "oem_part_number": best_web_part["oem_part_number"],
                "description": best_web_part["description"],
                "confidence": best_web_part["confidence"],
                "selection_metadata": {
                    "selected_from": "web_search_only",
                    "composite_score": best_web_part["confidence"],
                    "reasoning": "Web search result without AI validation"
                }
            }
        
        # Fallback: No reliable results found
        return {
            "oem_part_number": "NOT_FOUND",
            "description": f"Unable to resolve OEM part number for {description}",
            "confidence": 0.0,
            "selection_metadata": {
                "selected_from": "fallback",
                "composite_score": 0.0,
                "reasoning": "No reliable results found from web search or AI analysis"
            }
        }

# Standalone function wrapper for backwards compatibility
def resolve_part_name(description, make=None, model=None, year=None, use_database=True, use_manual_search=True, use_web_search=True, save_results=True, bypass_cache=False):
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