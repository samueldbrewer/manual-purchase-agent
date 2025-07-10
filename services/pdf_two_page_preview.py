"""PDF two-page preview generator service."""

import logging
import tempfile
import os

logger = logging.getLogger(__name__)

class PDFTwoPagePreview:
    """Service for generating two-page PDF preview images."""
    
    def __init__(self):
        pass
    
    def generate_from_url(self, pdf_url):
        """Generate a two-page preview image from a PDF URL."""
        try:
            # For Railway deployment, we'll return None to indicate preview not available
            # This prevents blocking the API when PDF preview generation isn't possible
            logger.info(f"Two-page PDF preview generation not available in Railway environment for: {pdf_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating two-page PDF preview: {e}")
            return None
    
    def generate_from_file(self, pdf_path):
        """Generate a two-page preview image from a local PDF file."""
        try:
            # For Railway deployment, we'll return None to indicate preview not available
            logger.info(f"Two-page PDF preview generation not available in Railway environment for: {pdf_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating two-page PDF preview from file: {e}")
            return None