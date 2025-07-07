#!/bin/bash
# Railway startup script

# Set default port if not provided
export PORT=${PORT:-7777}

# Set Python path
export PYTHONPATH=$PWD

# Initialize database if needed
python scripts/init_db.py || echo "Database initialization skipped"

# Start the application
exec gunicorn --bind 0.0.0.0:$PORT app:create_app()