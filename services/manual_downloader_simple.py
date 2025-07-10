import os
import logging
import requests
from urllib.parse import urlparse
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManualDownloader:
    """Simplified manual downloader using requests instead of playwright"""
    
    def __init__(self, upload_folder=None, use_temp_storage=True, debug_screenshots=False):
        """Initialize the manual downloader"""
        self.use_temp_storage = use_temp_storage
        self.debug_screenshots = debug_screenshots
        self.upload_folder = upload_folder or Config.UPLOAD_FOLDER
        
        if not self.use_temp_storage:
            os.makedirs(self.upload_folder, exist_ok=True)
    
    def download_manual(self, url, filename=None):
        """Download a manual from a URL using requests
        
        Args:
            url (str): URL of the manual to download
            filename (str): Optional filename to save as
            
        Returns:
            str: Path to the downloaded file or None if failed
        """
        try:
            logger.info(f"Downloading manual from: {url}")
            
            # Send GET request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Generate filename if not provided
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path) or 'manual.pdf'
            
            # Save the file
            if self.use_temp_storage:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    file_path = tmp_file.name
            else:
                file_path = os.path.join(self.upload_folder, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            
            logger.info(f"Successfully downloaded manual to: {file_path}")
            return file_path
            
        except requests.RequestException as e:
            logger.error(f"Failed to download manual from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading manual: {e}")
            return None