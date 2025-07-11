"""Website screenshot service for capturing supplier page screenshots."""

import logging
import tempfile
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class WebsiteScreenshotService:
    """Service for capturing website screenshots."""
    
    def __init__(self):
        pass
    
    def capture_screenshot(self, url, output_path=None):
        """Capture a screenshot of a website URL."""
        try:
            # For Railway deployment, screenshot capture is not available
            # This prevents blocking the API when screenshot libraries aren't available
            logger.info(f"Website screenshot capture not available in Railway environment for: {url}")
            return {
                "success": False,
                "error": "Screenshot capture not available in Railway environment",
                "url": url,
                "output_path": None
            }
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "output_path": None
            }
    
    def capture_multiple_screenshots(self, urls, output_directory=None):
        """Capture screenshots of multiple websites."""
        try:
            results = []
            for url in urls:
                result = self.capture_screenshot(url)
                results.append(result)
            
            return {
                "success": False,
                "error": "Screenshot capture not available in Railway environment",
                "results": results,
                "total_urls": len(urls),
                "successful_captures": 0
            }
            
        except Exception as e:
            logger.error(f"Error capturing multiple screenshots: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "total_urls": len(urls) if urls else 0,
                "successful_captures": 0
            }

# Standalone function wrappers for backwards compatibility
def capture_supplier_screenshots(urls):
    """Standalone function wrapper for capturing supplier screenshots."""
    try:
        service = WebsiteScreenshotService()
        
        if isinstance(urls, str):
            # Single URL
            result = service.capture_screenshot(urls)
            return {
                "success": result["success"],
                "screenshots": [result] if result["success"] else [],
                "errors": [result] if not result["success"] else [],
                "total_requested": 1,
                "total_captured": 1 if result["success"] else 0
            }
        elif isinstance(urls, list):
            # Multiple URLs
            result = service.capture_multiple_screenshots(urls)
            return {
                "success": result["success"],
                "screenshots": [r for r in result["results"] if r["success"]],
                "errors": [r for r in result["results"] if not r["success"]],
                "total_requested": result["total_urls"],
                "total_captured": result["successful_captures"]
            }
        else:
            return {
                "success": False,
                "error": "Invalid URL format - must be string or list",
                "screenshots": [],
                "errors": [],
                "total_requested": 0,
                "total_captured": 0
            }
    
    except Exception as e:
        logger.error(f"Error in capture_supplier_screenshots: {e}")
        return {
            "success": False,
            "error": str(e),
            "screenshots": [],
            "errors": [],
            "total_requested": 0,
            "total_captured": 0
        }

def capture_website_screenshot(url, output_path=None):
    """Standalone function wrapper for capturing a single website screenshot."""
    service = WebsiteScreenshotService()
    return service.capture_screenshot(url, output_path)