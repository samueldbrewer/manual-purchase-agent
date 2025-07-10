"""Manual finder service for searching and downloading technical manuals."""

import os
import requests
from serpapi import GoogleSearch
import tempfile
import logging

logger = logging.getLogger(__name__)

class ManualFinder:
    """Service for finding technical manuals using SerpAPI."""
    
    def __init__(self, serpapi_key=None):
        self.serpapi_key = serpapi_key or os.environ.get('SERPAPI_KEY')
        if not self.serpapi_key:
            raise ValueError("SERPAPI_KEY is required")
    
    def search_manuals(self, make, model, manual_type="technical manual"):
        """Search for manuals using SerpAPI."""
        try:
            query = f"{make} {model} {manual_type} filetype:pdf"
            
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 10
            })
            
            results = search.get_dict()
            manuals = []
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    if result.get("link", "").endswith(".pdf"):
                        manuals.append({
                            "title": result.get("title", ""),
                            "url": result.get("link", ""),
                            "snippet": result.get("snippet", "")
                        })
            
            return {
                "success": True,
                "manuals": manuals,
                "count": len(manuals)
            }
            
        except Exception as e:
            logger.error(f"Error searching manuals: {e}")
            return {
                "success": False,
                "error": str(e),
                "manuals": [],
                "count": 0
            }
    
    def download_manual(self, url, filename=None):
        """Download a manual from URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if not filename:
                filename = tempfile.mktemp(suffix=".pdf")
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return {
                "success": True,
                "filename": filename,
                "size": len(response.content)
            }
            
        except Exception as e:
            logger.error(f"Error downloading manual: {e}")
            return {
                "success": False,
                "error": str(e)
            }