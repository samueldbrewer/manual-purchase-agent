"""Supplier finder service for locating parts suppliers."""

import os
from serpapi import GoogleSearch
import logging

logger = logging.getLogger(__name__)

class SupplierFinder:
    """Service for finding suppliers for parts."""
    
    def __init__(self, serpapi_key=None):
        self.serpapi_key = serpapi_key or os.environ.get('SERPAPI_KEY')
        if not self.serpapi_key:
            raise ValueError("SERPAPI_KEY is required")
    
    def find_suppliers(self, part_number, part_description=""):
        """Find suppliers for a given part number."""
        try:
            query = f"{part_number} {part_description} buy online parts supplier"
            
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 10
            })
            
            results = search.get_dict()
            suppliers = []
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    # Filter for e-commerce sites
                    url = result.get("link", "")
                    title = result.get("title", "")
                    
                    if self._is_ecommerce_site(url, title):
                        suppliers.append({
                            "name": self._extract_domain_name(url),
                            "title": title,
                            "url": url,
                            "snippet": result.get("snippet", ""),
                            "rating": self._rate_supplier(url, title)
                        })
            
            # Sort by rating
            suppliers.sort(key=lambda x: x["rating"], reverse=True)
            
            return {
                "success": True,
                "suppliers": suppliers[:5],  # Return top 5
                "count": len(suppliers)
            }
            
        except Exception as e:
            logger.error(f"Error finding suppliers: {e}")
            return {
                "success": False,
                "error": str(e),
                "suppliers": [],
                "count": 0
            }
    
    def _is_ecommerce_site(self, url, title):
        """Check if the URL/title indicates an e-commerce site."""
        ecommerce_indicators = [
            "buy", "shop", "store", "parts", "supply", "warehouse",
            "amazon", "ebay", "grainger", "mcmaster", "partstown"
        ]
        
        text = f"{url.lower()} {title.lower()}"
        return any(indicator in text for indicator in ecommerce_indicators)
    
    def _extract_domain_name(self, url):
        """Extract clean domain name from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain.split('.')[0].title()
        except:
            return "Unknown"
    
    def _rate_supplier(self, url, title):
        """Rate supplier based on URL and title quality."""
        score = 0.5  # Base score
        
        # Preferred suppliers
        preferred = ["partstown", "grainger", "mcmaster", "amazon"]
        for pref in preferred:
            if pref in url.lower():
                score += 0.3
                break
        
        # Product page indicators
        product_indicators = ["/product/", "/item/", "/dp/", "/p/"]
        if any(indicator in url.lower() for indicator in product_indicators):
            score += 0.2
        
        # Title quality
        if "OEM" in title.upper():
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0