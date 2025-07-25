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
                "num": 10,  # Get more results for better AI analysis
                "hl": "en",
                "gl": "us"
            })
            
            results = search.get_dict()
            parts = []
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    # Gather rich context from search result
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    link = result.get('link', '')
                    
                    # Combine all available text for AI analysis
                    context_text = f"Title: {title}\nURL: {link}\nDescription: {snippet}"
                    
                    # Use AI to extract part numbers with full context
                    part_numbers = self._extract_part_numbers_from_text(context_text, make, model)
                    
                    if part_numbers:
                        # Add source URL to each part for traceability
                        for part in part_numbers:
                            part['source_url'] = link
                            part['source_title'] = title
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
            
            # Prepare comprehensive web search context
            web_context = "No web search results available."
            if web_result.get("success") and web_result.get("parts"):
                parts_text = []
                for part in web_result["parts"]:
                    source_info = f" [Source: {part.get('source_title', 'Unknown')}]" if part.get('source_title') else ""
                    context_info = f" [Context: {part.get('context', 'N/A')}]" if part.get('context') else ""
                    parts_text.append(
                        f"- {part['oem_part_number']}: {part['description']} "
                        f"(confidence: {part['confidence']}){source_info}{context_info}"
                    )
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
    
    def _extract_part_numbers_from_text(self, text, make, model):
        """Use AI to extract and validate part numbers from search result text."""
        try:
            if not self.openai_api_key:
                return []
            
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""
            Analyze this search result text to extract valid OEM part numbers for {make} {model} equipment.

            Text to analyze:
            {text}

            Your task:
            1. Identify potential part numbers in the text
            2. Assess which ones are likely genuine OEM part numbers (not manual numbers, model numbers, page numbers, etc.)
            3. Consider {make}'s typical part numbering format and conventions
            4. Exclude obvious false positives like manual pages, document numbers, phone numbers, etc.
            5. Rate confidence based on context and formatting

            Respond with a JSON array of valid part numbers:
            [
                {{
                    "oem_part_number": "XX-XXXXXX",
                    "description": "Brief description of what this part likely is",
                    "confidence": 0.85,
                    "context": "Where/how this was found in the text"
                }}
            ]

            If no valid part numbers are found, return an empty array: []
            """
            
            response = client.chat.completions.create(
                model="gpt-4.1-nano-2025-04-14",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            try:
                parsed_parts = json.loads(result)
                if isinstance(parsed_parts, list):
                    return parsed_parts
                else:
                    return []
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse part extraction response as JSON: {result}")
                return []
                
        except Exception as e:
            logger.error(f"AI part extraction failed: {e}")
            return []
    
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