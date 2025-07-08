from flask import Flask, jsonify, render_template, request, send_from_directory
from models import db
from api.manuals import manuals_bp
from api.parts import parts_bp
from api.suppliers import suppliers_bp
from api.purchases import purchases_bp
from api.profiles import profiles_bp
from api.system import system_bp
from api.enrichment import enrichment_bp
from api.screenshots import screenshots_bp
from api.recording_studio_api import recording_studio_bp
from api.generic_parts import generic_parts_bp
from web import web_bp
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
    
    # Register API blueprints
    app.register_blueprint(manuals_bp, url_prefix='/api/manuals')
    app.register_blueprint(parts_bp, url_prefix='/api/parts')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(purchases_bp, url_prefix='/api/purchases')
    app.register_blueprint(profiles_bp, url_prefix='/api/profiles')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    app.register_blueprint(enrichment_bp, url_prefix='/api/enrichment')
    app.register_blueprint(screenshots_bp, url_prefix='/api/screenshots')
    app.register_blueprint(recording_studio_bp, url_prefix='/api/recordings')
    app.register_blueprint(generic_parts_bp, url_prefix='/api/parts')
    
    # Register web UI blueprint
    app.register_blueprint(web_bp, url_prefix='/')
    
    # Root route redirects to web UI
    @app.route('/')
    def index():
        return render_template('pages/index.html')
    
    # Data Navigator route
    @app.route('/data-navigator')
    def data_navigator():
        return render_template('pages/data_navigator.html')
    
    # V3 mobile app route
    @app.route('/static/api-demo/v3/')
    def v3_app():
        try:
            response = app.send_static_file('api-demo/v3/index.html')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        except:
            return send_from_directory('static/api-demo/v3', 'index.html')
    
    # V4 mobile app route (latest)
    @app.route('/static/api-demo/v4/')
    def v4_app():
        try:
            response = app.send_static_file('api-demo/v4/index.html')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        except:
            return send_from_directory('static/api-demo/v4', 'index.html')
    
    # Serve static files for mobile apps
    @app.route('/static/api-demo/v3/<path:filename>')
    def v3_static(filename):
        return send_from_directory('static/api-demo/v3', filename)
    
    @app.route('/static/api-demo/v4/<path:filename>')
    def v4_static(filename):
        return send_from_directory('static/api-demo/v4', filename)
    
    # Debug endpoint to check file system
    @app.route('/debug/files')
    def debug_files():
        import os
        try:
            files = []
            if os.path.exists('static'):
                files.append('static directory exists')
                for root, dirs, filenames in os.walk('static'):
                    for f in filenames[:10]:  # Limit to first 10 files
                        files.append(os.path.join(root, f))
            else:
                files.append('static directory does not exist')
            
            return jsonify({
                'working_dir': os.getcwd(),
                'files': files,
                'v3_exists': os.path.exists('static/api-demo/v3/index.html'),
                'v4_exists': os.path.exists('static/api-demo/v4/index.html')
            })
        except Exception as e:
            return jsonify({'error': str(e)})
    
    # Add no-cache headers to all responses
    @app.after_request
    def add_no_cache_headers(response):
        # Only add no-cache headers to HTML, JS, and CSS files
        if response.mimetype in ['text/html', 'application/javascript', 'text/javascript', 'text/css']:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    
    # Serve screenshot images
    @app.route('/uploads/screenshots/<filename>')
    def serve_screenshot(filename):
        screenshots_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'screenshots')
        return send_from_directory(screenshots_dir, filename)
    
    # Serve supplier screenshot images
    @app.route('/uploads/screenshots/suppliers/<filename>')
    def serve_supplier_screenshot(filename):
        screenshots_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'screenshots', 'suppliers')
        return send_from_directory(screenshots_dir, filename)
    
    # Serve data files (CSV)
    @app.route('/data/<filename>')
    def serve_data_file(filename):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        return send_from_directory(data_dir, filename)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('pages/error.html', error_code=404), 404
    
    @app.errorhandler(500)
    def server_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Server error'}), 500
        return render_template('pages/error.html', error_code=500), 500
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 7777)))