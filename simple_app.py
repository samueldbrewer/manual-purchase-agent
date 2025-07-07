#!/usr/bin/env python3
"""
Minimal Flask app for Railway deployment testing
"""
import os
from flask import Flask, jsonify

def create_simple_app():
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            "status": "success",
            "message": "Manual Purchase Agent is running!",
            "version": "v15.6",
            "port": os.environ.get("PORT", "7777")
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})
    
    @app.route('/api/system/health')
    def api_health():
        return jsonify({
            "status": "healthy",
            "service": "Manual Purchase Agent",
            "version": "v15.6"
        })
    
    return app

if __name__ == "__main__":
    app = create_simple_app()
    port = int(os.environ.get("PORT", 7777))
    app.run(host="0.0.0.0", port=port, debug=False)