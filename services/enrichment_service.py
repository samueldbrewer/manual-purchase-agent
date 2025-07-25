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
                model="gpt-4.1-nano-2025-04-14",
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
    
    def get_enrichment_data(self, make, model, year=None, part_number=None):
        """Get enrichment data for equipment or parts with optimized search queries."""
        try:
            # Build base equipment identifier
            equipment = f"{make} {model}"
            if year:
                equipment = f"{make} {model} {year}"
            
            # Create search context
            if part_number:
                subject = f"{equipment} part {part_number}"
                context = {
                    "equipment": equipment,
                    "part_number": part_number,
                    "search_type": "part_specific"
                }
            else:
                subject = equipment
                context = {
                    "equipment": equipment,
                    "search_type": "equipment_general"
                }
            
            # Search for multimedia content with optimized queries
            videos = self._search_videos(context)
            articles = self._search_articles(context) 
            images = self._search_images(context)
            
            return {
                "success": True,
                "subject": subject,
                "context": context,
                "data": {
                    "videos": videos,
                    "articles": articles,
                    "images": images
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting enrichment data: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {
                    "videos": [],
                    "articles": [],
                    "images": []
                }
            }
    
    def _search_videos(self, context):
        """Search for related videos with optimized queries."""
        try:
            if not self.serpapi_key:
                return []
            
            # Build video-specific query
            if context["search_type"] == "part_specific":
                query = f"{context['equipment']} {context['part_number']} video"
            else:
                query = f"{context['equipment']} video"
            
            search = GoogleSearch({
                "q": query,
                "tbm": "vid",
                "api_key": self.serpapi_key,
                "num": 8
            })
            
            results = search.get_dict()
            videos = []
            
            for result in results.get("video_results", []):
                videos.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "thumbnail": result.get("thumbnail", ""),
                    "duration": result.get("duration", ""),
                    "source": result.get("source", ""),
                    "query_used": query
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return []
    
    def _search_articles(self, context):
        """Search for related articles and documentation with optimized queries."""
        try:
            if not self.serpapi_key:
                return []
            
            # Build documentation-specific query
            if context["search_type"] == "part_specific":
                query = f"{context['equipment']} {context['part_number']} manual documentation"
            else:
                query = f"{context['equipment']} manual documentation"
            
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 8,
                "hl": "en"
            })
            
            results = search.get_dict()
            articles = []
            
            for result in results.get("organic_results", []):
                # Prioritize official documentation sources
                url = result.get("link", "")
                title = result.get("title", "")
                
                # Check if it's likely to be official documentation
                is_official = any(domain in url.lower() for domain in [
                    'hobart.com', 'hennypenny.com', 'vulcanhart.com', 
                    'carrier.com', 'trane.com', 'manitowoc.com'
                ])
                
                articles.append({
                    "title": title,
                    "url": url,
                    "snippet": result.get("snippet", ""),
                    "source": result.get("displayed_link", ""),
                    "is_official": is_official,
                    "query_used": query
                })
            
            # Sort to prioritize official sources
            articles.sort(key=lambda x: x['is_official'], reverse=True)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []
    
    def _search_images(self, context):
        """Search for related images with optimized queries."""
        try:
            if not self.serpapi_key:
                return []
            
            # Build image-specific query
            if context["search_type"] == "part_specific":
                query = f"{context['equipment']} {context['part_number']} image"
            else:
                query = f"{context['equipment']} image"
            
            search = GoogleSearch({
                "q": query,
                "tbm": "isch",
                "api_key": self.serpapi_key,
                "num": 10,
                "safe": "active"
            })
            
            results = search.get_dict()
            images = []
            
            for result in results.get("images_results", []):
                # Filter for likely useful images (not too small, from relevant sources)
                original_url = result.get("original", "")
                thumbnail_url = result.get("thumbnail", "")
                
                # Check if source is likely to be relevant
                source_url = result.get("source", "").lower()
                is_relevant_source = any(domain in source_url for domain in [
                    'partstown', 'hobart', 'hennypenny', 'vulcanhart', 'manitowoc',
                    'repairparts', 'partsips', 'genuineparts', 'oem'
                ])
                
                images.append({
                    "title": result.get("title", ""),
                    "url": original_url,
                    "thumbnail": thumbnail_url,
                    "source": result.get("source", ""),
                    "is_relevant_source": is_relevant_source,
                    "query_used": query
                })
            
            # Sort to prioritize relevant sources
            images.sort(key=lambda x: x['is_relevant_source'], reverse=True)
            
            return images[:8]  # Return top 8 images
            
        except Exception as e:
            logger.error(f"Error searching images: {e}")
            return []