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

# Standalone function wrappers for backwards compatibility
def search_manuals(make, model, manual_type="technical manual", year=None):
    """Standalone function wrapper for manual search."""
    finder = ManualFinder()
    result = finder.search_manuals(make, model, manual_type)
    
    # Convert to expected format for the API
    if result['success']:
        return result['manuals']
    else:
        logger.error(f"Search failed: {result['error']}")
        return []

def download_manual(url, filename=None):
    """Standalone function wrapper for manual download."""
    finder = ManualFinder()
    result = finder.download_manual(url, filename)
    
    if result['success']:
        return result['filename']
    else:
        raise Exception(result['error'])

def verify_manual_contains_model(file_path, model):
    """Verify if a manual contains references to a specific model."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        
        # Search first few pages for model references
        for page_num in range(min(5, len(doc))):
            page = doc[page_num]
            text = page.get_text().lower()
            
            if model.lower() in text:
                doc.close()
                return True
        
        doc.close()
        return False
    except Exception as e:
        logger.error(f"Error verifying model in manual: {e}")
        return True  # Default to include if can't verify

def get_pdf_page_count(file_path):
    """Get the number of pages in a PDF file."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        page_count = len(doc)
        doc.close()
        return page_count
    except Exception as e:
        logger.error(f"Error getting PDF page count: {e}")
        return None