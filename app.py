from flask import Flask, jsonify, send_from_directory
from models import db
from api.manuals import manuals_bp
from api.parts import parts_bp
from api.suppliers import suppliers_bp
from api.purchases import purchases_bp
from api.profiles import profiles_bp
from api.system import system_bp
from api.enrichment import enrichment_bp
from api.screenshots import screenshots_bp
from api.generic_parts import generic_parts_bp
import os

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Disable caching for development
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Initialize database
    db.init_app(app)
    
    # Create tables if they don't exist (Railway PostgreSQL or local SQLite)
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database table creation failed: {e}")
            print("Will retry table creation on first request")
            # Continue anyway - tables might already exist or database might not be ready yet
    
    # Register API blueprints
    app.register_blueprint(manuals_bp, url_prefix='/api/manuals')
    app.register_blueprint(parts_bp, url_prefix='/api/parts')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(purchases_bp, url_prefix='/api/purchases')
    app.register_blueprint(profiles_bp, url_prefix='/api/profiles')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    app.register_blueprint(enrichment_bp, url_prefix='/api/enrichment')
    app.register_blueprint(screenshots_bp, url_prefix='/api/screenshots')
    app.register_blueprint(generic_parts_bp, url_prefix='/api/parts')
    
    # Root route serves the V4 interface
    @app.route('/')
    def index():
        return send_from_directory('static/api-demo/v4', 'index.html')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "version": "v15.6"})
    
    # API Test Console
    @app.route('/api-test')
    def api_test():
        return send_from_directory('static', 'api-test.html')
    
    # Static file serving for V4 interface
    @app.route('/v4/<path:filename>')
    def v4_static(filename):
        return send_from_directory('static/api-demo/v4', filename)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 7777)))