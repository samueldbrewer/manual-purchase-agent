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
from api.demo import demo_bp
from api.admin import admin_bp
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
    
    # Debug database configuration
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
    print(f"Database URI: {db_uri[:50]}..." if len(db_uri) > 50 else f"Database URI: {db_uri}")
    print(f"DATABASE_URL env var: {'Set' if os.environ.get('DATABASE_URL') else 'Not set'}")
    print(f"Working directory: {os.getcwd()}")
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            # For Railway, skip table creation if database isn't ready
            if 'sqlite' not in db_uri.lower():
                print("Detected PostgreSQL database - attempting table creation")
            else:
                print("Detected SQLite database - creating instance directory")
                os.makedirs('instance', exist_ok=True)
            
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database table creation failed: {e}")
            print("Application will continue - tables may be created on first request")
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
    app.register_blueprint(demo_bp, url_prefix='/api/demo')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Root route serves the V4 interface - protected
    @app.route('/')
    def index():
        from middleware.demo_auth import require_demo_key
        @require_demo_key
        def protected_index():
            return send_from_directory('static/api-demo/v4', 'index.html')
        return protected_index()
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "version": "v15.6"})
    
    # API Test Console - protected
    @app.route('/api-test')
    def api_test():
        from middleware.demo_auth import require_demo_key
        @require_demo_key
        def protected_api_test():
            return send_from_directory('static', 'api-test.html')
        return protected_api_test()
    
    # Customer Demo
    @app.route('/customer-demo')
    def customer_demo():
        return send_from_directory('static/customer-demo', 'index.html')
    
    # Customer Demo Assets
    @app.route('/customer-demo/<path:filename>')
    def customer_demo_assets(filename):
        response = send_from_directory('static/customer-demo', filename)
        if filename.endswith('.css'):
            response.headers['Content-Type'] = 'text/css'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    # Static file serving for V4 interface - protected
    @app.route('/v4/<path:filename>')
    def v4_static(filename):
        from middleware.demo_auth import require_demo_key
        @require_demo_key
        def protected_v4_static():
            return send_from_directory('static/api-demo/v4', filename)
        return protected_v4_static()
    
    # CSS file routing for main page - protected
    @app.route('/styles.css')
    def styles_css():
        from middleware.demo_auth import require_demo_key
        @require_demo_key
        def protected_styles():
            return send_from_directory('static/api-demo/v4', 'styles.css')
        return protected_styles()
    
    # JS file routing for main page - protected
    @app.route('/app.js')
    def app_js():
        from middleware.demo_auth import require_demo_key
        @require_demo_key
        def protected_js():
            return send_from_directory('static/api-demo/v4', 'app.js')
        return protected_js()
    
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