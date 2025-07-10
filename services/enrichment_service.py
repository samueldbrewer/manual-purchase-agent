"""Enrichment service for enhancing part data with additional information."""

import os
import openai
from serpapi import GoogleSearch
import logging

logger = logging.getLogger(__name__)

class EnrichmentService:
    """Service for enriching part data with additional information."""
    
    def __init__(self, serpapi_key=None, openai_api_key=None):
        self.serpapi_key = serpapi_key or os.environ.get('SERPAPI_KEY')
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def enrich_part_data(self, part_number, description="", make="", model=""):
        """Enrich part data with additional information."""
        try:
            result = {
                "part_number": part_number,
                "description": description,
                "make": make,
                "model": model,
                "enriched_data": {}
            }
            
            # Get specifications
            specs = self._get_part_specifications(part_number, description, make, model)
            if specs:
                result["enriched_data"]["specifications"] = specs
            
            # Get compatibility info
            compatibility = self._get_compatibility_info(part_number, make, model)
            if compatibility:
                result["enriched_data"]["compatibility"] = compatibility
            
            # Get pricing info
            pricing = self._get_pricing_info(part_number)
            if pricing:
                result["enriched_data"]["pricing"] = pricing
            
            return {
                "success": True,
                "enriched_part": result
            }
            
        except Exception as e:
            logger.error(f"Error enriching part data: {e}")
            return {
                "success": False,
                "error": str(e),
                "enriched_part": None
            }
    
    def _get_part_specifications(self, part_number, description, make, model):
        """Get part specifications using AI."""
        try:
            if not self.openai_api_key:
                return None
            
            prompt = f"""
            Provide technical specifications for this part:
            Part Number: {part_number}
            Description: {description}
            Make: {make}
            Model: {model}
            
            Return specifications in a structured format with key-value pairs.
            Focus on dimensions, materials, electrical specs, etc.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting specifications: {e}")
            return None
    
    def _get_compatibility_info(self, part_number, make, model):
        """Get compatibility information for the part."""
        try:
            if not self.serpapi_key:
                return None
            
            query = f"{part_number} compatibility {make} models"
            
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 3
            })
            
            results = search.get_dict()
            compatibility_info = []
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    compatibility_info.append({
                        "source": result.get("title", ""),
                        "url": result.get("link", ""),
                        "info": result.get("snippet", "")
                    })
            
            return compatibility_info
            
        except Exception as e:
            logger.error(f"Error getting compatibility info: {e}")
            return None
    
    def _get_pricing_info(self, part_number):
        """Get pricing information for the part."""
        try:
            if not self.serpapi_key:
                return None
            
            query = f"{part_number} price buy"
            
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 5
            })
            
            results = search.get_dict()
            pricing_info = []
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    # Look for price indicators in snippet
                    snippet = result.get("snippet", "")
                    if any(indicator in snippet.lower() for indicator in ["$", "price", "cost"]):
                        pricing_info.append({
                            "supplier": result.get("title", ""),
                            "url": result.get("link", ""),
                            "price_info": snippet
                        })
            
            return pricing_info[:3]  # Return top 3 pricing sources
            
        except Exception as e:
            logger.error(f"Error getting pricing info: {e}")
            return None