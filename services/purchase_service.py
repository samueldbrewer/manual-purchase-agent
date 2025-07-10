import logging
import json
import tempfile
import subprocess
import os
from pathlib import Path
from urllib.parse import urlparse
from models import db, Purchase, BillingProfile
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PurchaseAutomator:
    """Automated purchase system using recorded browser interactions"""
    
    def __init__(self):
        self.recording_system_path = Path(__file__).parent.parent / "recording_system"
        self.recordings_path = self.recording_system_path / "recordings"
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def get_available_recordings(self):
        """Get list of available purchase recordings"""
        try:
            recordings = []
            if self.recordings_path.exists():
                for recording_file in self.recordings_path.glob("*.json"):
                    # Skip temporary variable files
                    if recording_file.name.startswith("temp-vars"):
                        continue
                    recordings.append(recording_file.stem)
            return recordings
        except Exception as e:
            logger.error(f"Error getting available recordings: {e}")
            return []
    
    def find_recording_for_url(self, supplier_url):
        """Find appropriate recording based on supplier URL"""
        try:
            parsed_url = urlparse(supplier_url)
            domain = parsed_url.netloc.replace('www.', '').split('.')[0]
            
            # Look for exact domain match
            recording_file = self.recordings_path / f"{domain}.json"
            if recording_file.exists():
                return recording_file.name
            
            # Look for partial matches
            available_recordings = self.get_available_recordings()
            for recording in available_recordings:
                if domain.lower() in recording.lower() or recording.lower() in domain.lower():
                    return f"{recording}.json"
            
            return None
        except Exception as e:
            logger.error(f"Error finding recording for URL {supplier_url}: {e}")
            return None
    
    def purchase_part(self, part_number, supplier_url, billing_profile_id, quantity=1, recording_name=None):
        """
        Execute automated purchase using recorded browser interactions
        
        Args:
            part_number (str): The part number to purchase
            supplier_url (str): URL of the supplier's product page
            billing_profile_id (int): ID of billing profile to use
            quantity (int): Quantity to purchase
            recording_name (str): Optional specific recording to use
            
        Returns:
            dict: Purchase result with success status and details
        """
        try:
            # Check if Node.js is available for recording system
            import shutil
            if not shutil.which('node'):
                return {
                    "success": False,
                    "error": "Purchase automation not available in Railway deployment",
                    "message": "The Node.js-based recording system is only available in local development. For production purchase automation, please use a local instance.",
                    "part_number": part_number,
                    "supplier_url": supplier_url,
                    "note": "Purchase recordings require Node.js and cannot run in the Railway Python-only environment"
                }
            
            # Check if purchases are enabled
            enable_purchases = getattr(Config, 'ENABLE_REAL_PURCHASES', None)
            if not enable_purchases or enable_purchases.lower() != 'true':
                return {
                    "success": False,
                    "error": "Real purchases are disabled",
                    "message": "Set ENABLE_REAL_PURCHASES=true to enable automated purchasing",
                    "part_number": part_number,
                    "supplier_url": supplier_url
                }
            
            # Get billing profile
            billing_profile = BillingProfile.query.get(billing_profile_id)
            if not billing_profile:
                return {
                    "success": False,
                    "error": "Billing profile not found",
                    "message": f"No billing profile found with ID {billing_profile_id}"
                }
            
            # Find appropriate recording
            if not recording_name:
                recording_name = self.find_recording_for_url(supplier_url)
            
            if not recording_name:
                return {
                    "success": False,
                    "error": "No suitable recording found",
                    "message": f"No purchase recording available for {urlparse(supplier_url).netloc}",
                    "available_recordings": self.get_available_recordings()
                }
            
            # Decrypt billing profile data
            billing_data = billing_profile.get_decrypted_data()
            
            # Create temporary variables file
            variables = {
                "product_url": supplier_url,
                "quantity": str(quantity),
                "first_name": billing_data.get("first_name", "John"),
                "last_name": billing_data.get("last_name", "Doe"),
                "email": billing_data.get("email", "test@example.com"),
                "phone": billing_data.get("phone", "555-123-4567"),
                "address": billing_data.get("address", "123 Main St"),
                "city": billing_data.get("city", "City"),
                "state": billing_data.get("state", "CA"),
                "zip_code": billing_data.get("zip_code", "90210"),
                "card_number": billing_data.get("card_number", "4111111111111111"),
                "card_expiry": billing_data.get("card_expiry", "12/25"),
                "card_cvv": billing_data.get("card_cvv", "123")
            }
            
            # Create temporary variables file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, 
                                           dir=self.recording_system_path) as temp_file:
                json.dump(variables, temp_file)
                temp_vars_file = temp_file.name
            
            try:
                # Execute purchase using recording system
                cmd = [
                    'node', 'index.js', 'clone',
                    str(self.recordings_path / recording_name),
                    supplier_url,
                    '--vars-file', temp_vars_file,
                    '--headless',
                    '--conservative'  # Use conservative timing for purchases
                ]
                
                logger.info(f"Executing purchase command: {' '.join(cmd)}")
                
                # Run the command from the recording system directory
                result = subprocess.run(
                    cmd,
                    cwd=self.recording_system_path,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                # Create purchase record
                purchase = Purchase(
                    part_number=part_number,
                    supplier_url=supplier_url,
                    quantity=quantity,
                    billing_profile_id=billing_profile_id,
                    recording_used=recording_name,
                    status='completed' if result.returncode == 0 else 'failed',
                    automation_log=result.stdout + result.stderr if result.stdout or result.stderr else None
                )
                
                db.session.add(purchase)
                db.session.commit()
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "Purchase completed successfully",
                        "purchase_id": purchase.id,
                        "part_number": part_number,
                        "supplier_url": supplier_url,
                        "quantity": quantity,
                        "recording_used": recording_name,
                        "execution_log": result.stdout
                    }
                else:
                    return {
                        "success": False,
                        "error": "Purchase automation failed",
                        "message": f"Recording execution failed with return code {result.returncode}",
                        "purchase_id": purchase.id,
                        "execution_log": result.stderr,
                        "stdout": result.stdout
                    }
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_vars_file)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Purchase automation timeout",
                "message": "Purchase recording execution timed out after 5 minutes"
            }
        except Exception as e:
            logger.error(f"Error in purchase automation: {e}")
            return {
                "success": False,
                "error": "Purchase automation error",
                "message": str(e)
            }