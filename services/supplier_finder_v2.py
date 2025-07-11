"""Enhanced supplier finder service with AI-powered ranking and deduplication."""

import os
from serpapi import GoogleSearch
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SupplierFinderV2:
    """Enhanced service for finding suppliers with AI-powered ranking."""
    
    def __init__(self, serpapi_key=None, openai_api_key=None):
        self.serpapi_key = serpapi_key or os.environ.get('SERPAPI_KEY')
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        
        if not self.serpapi_key:
            logger.warning("SERPAPI_KEY not configured - supplier search will return empty results")
    
    def search_suppliers(self, part_number, part_description="", make=None, model=None, oem_only=False):
        """Enhanced supplier search with intelligent ranking and deduplication."""
        try:
            if not self.serpapi_key:
                return {
                    "success": False,
                    "error": "SERPAPI_KEY not configured",
                    "suppliers": [],
                    "count": 0
                }
            
            # Build comprehensive search query
            query_parts = [part_number]
            if part_description:
                query_parts.append(part_description)
            if make:
                query_parts.append(make)
            if model:
                query_parts.append(model)
            if oem_only:
                query_parts.append("OEM")
            
            query_parts.extend(["buy", "online", "parts", "supplier"])
            query = " ".join(query_parts)
            
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 15  # Get more results for better filtering
            })
            
            results = search.get_dict()
            suppliers = []
            seen_domains = set()  # For deduplication
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    url = result.get("link", "")
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    
                    # Extract domain for deduplication
                    domain = self._extract_domain(url)
                    if domain in seen_domains:
                        continue  # Skip duplicate domains
                    
                    if self._is_commercial_supplier(url, title, snippet):
                        supplier = {
                            "name": self._extract_supplier_name(url, title),
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "rating": self._calculate_supplier_rating(url, title, snippet),
                            "domain": domain,
                            "product_page": self._is_product_page(url, title)
                        }
                        suppliers.append(supplier)
                        seen_domains.add(domain)
                        
                        # Stop when we have enough good suppliers
                        if len(suppliers) >= 8:
                            break
            
            # Sort by rating (highest first)
            suppliers.sort(key=lambda x: x["rating"], reverse=True)
            
            # Apply PartsTown priority (move to top if present)
            suppliers = self._apply_partstown_priority(suppliers)
            
            return {
                "success": True,
                "suppliers": suppliers[:5],  # Return top 5
                "count": len(suppliers),
                "part_number": part_number,
                "search_query": query
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced supplier search: {e}")
            return {
                "success": False,
                "error": str(e),
                "suppliers": [],
                "count": 0
            }
    
    def _extract_domain(self, url):
        """Extract clean domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return domain.replace("www.", "")
        except:
            return url.lower()
    
    def _extract_supplier_name(self, url, title):
        """Extract clean supplier name from URL and title."""
        try:
            domain = self._extract_domain(url)
            # Get the main domain name (before first dot)
            name = domain.split('.')[0]
            
            # Special cases for known suppliers
            if "partstown" in domain:
                return "PartsTown"
            elif "grainger" in domain:
                return "Grainger"
            elif "mcmaster" in domain:
                return "McMaster-Carr"
            elif "amazon" in domain:
                return "Amazon"
            elif "ebay" in domain:
                return "eBay"
            elif "supplyhouse" in domain:
                return "SupplyHouse"
            else:
                return name.title()
        except:
            return "Unknown Supplier"
    
    def _is_commercial_supplier(self, url, title, snippet):
        """Check if this is a legitimate commercial supplier."""
        text = f"{url.lower()} {title.lower()} {snippet.lower()}"
        
        # Commercial indicators
        commercial_terms = [
            "buy", "shop", "store", "parts", "supply", "warehouse", "distributor",
            "amazon", "ebay", "grainger", "mcmaster", "partstown", "supplyhouse",
            "price", "order", "cart", "purchase", "online"
        ]
        
        # Must have at least one commercial indicator
        has_commercial = any(term in text for term in commercial_terms)
        
        # Exclude non-commercial sites
        exclude_terms = [
            "manual", "pdf", "specification", "datasheet", "forum", "wiki",
            "blog", "news", "article", "review", "youtube", "facebook"
        ]
        
        has_exclude = any(term in text for term in exclude_terms)
        
        return has_commercial and not has_exclude
    
    def _is_product_page(self, url, title):
        """Check if this appears to be a direct product page."""
        url_lower = url.lower()
        product_indicators = [
            "/product/", "/item/", "/dp/", "/p/", "/part/",
            "product-", "item-", "part-"
        ]
        
        # Check URL structure
        url_match = any(indicator in url_lower for indicator in product_indicators)
        
        # Check if URL contains part number patterns
        part_pattern = r'[A-Z0-9]{6,15}'
        has_part_number = bool(re.search(part_pattern, url, re.IGNORECASE))
        
        return url_match or has_part_number
    
    def _calculate_supplier_rating(self, url, title, snippet):
        """Calculate supplier rating based on multiple factors."""
        score = 0.5  # Base score
        
        url_lower = url.lower()
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        
        # Preferred suppliers (high trust, good service)
        if "partstown" in url_lower:
            score += 0.4  # PartsTown gets highest priority
        elif "grainger" in url_lower:
            score += 0.3
        elif "mcmaster" in url_lower:
            score += 0.3
        elif "supplyhouse" in url_lower:
            score += 0.25
        elif "amazon" in url_lower:
            score += 0.2
        
        # Product page indicators (direct product access)
        if self._is_product_page(url, title):
            score += 0.25
        
        # OEM indicators
        if "oem" in title_lower or "oem" in snippet_lower:
            score += 0.15
        
        # Availability indicators
        availability_terms = ["in stock", "available", "ships", "delivery"]
        if any(term in snippet_lower for term in availability_terms):
            score += 0.1
        
        # Price indicators
        if "$" in snippet or "price" in snippet_lower:
            score += 0.05
        
        # Title quality (specific part references)
        if len(title) > 20 and any(char.isdigit() for char in title):
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _apply_partstown_priority(self, suppliers):
        """Move PartsTown results to the top if they exist and are product pages."""
        partstown_suppliers = []
        other_suppliers = []
        
        for supplier in suppliers:
            if "partstown" in supplier["domain"] and supplier.get("product_page", False):
                partstown_suppliers.append(supplier)
            else:
                other_suppliers.append(supplier)
        
        # PartsTown suppliers first, then others
        return partstown_suppliers + other_suppliers

# Standalone function wrapper for backwards compatibility
def search_suppliers_v2(part_number, part_description="", make=None, model=None, oem_only=False):
    """Enhanced standalone function wrapper for supplier search."""
    try:
        finder = SupplierFinderV2()
        result = finder.search_suppliers(part_number, part_description, make, model, oem_only)
        return result
    
    except Exception as e:
        logger.error(f"Error in search_suppliers_v2: {e}")
        return {
            'success': False,
            'error': str(e),
            'suppliers': [],
            'count': 0,
            'part_number': part_number
        }