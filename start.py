#!/usr/bin/env python3
"""
Simple startup script for Railway deployment
"""
import os
from app import create_app

if __name__ == "__main__":
    # Get port from environment (Railway sets this)
    port = int(os.environ.get("PORT", 7777))
    
    # Create Flask app
    app = create_app()
    
    # Run with debug info
    print(f"Starting Flask app on port {port}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    # Run the app
    app.run(host="0.0.0.0", port=port, debug=False)