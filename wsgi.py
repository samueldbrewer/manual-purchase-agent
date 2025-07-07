#!/usr/bin/env python3
"""
WSGI entry point for Railway deployment
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import create_app
    
    # Create the Flask application
    application = create_app()
    app = application  # For gunicorn
    
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 7777))
        application.run(host="0.0.0.0", port=port)
        
except Exception as e:
    print(f"Error starting application: {e}")
    import traceback
    traceback.print_exc()
    raise