#!/usr/bin/env python3
"""
Database Initialization Script for Manual Purchase Agent.
This script creates a new, empty database with all required tables.
"""

import os
from flask import Flask
from models import db
from models.manual import Manual, ErrorCode, PartReference
from models.part import Part
from models.supplier import Supplier
from models.profile import BillingProfile
from models.purchase import Purchase
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure a Flask application for DB initialization only"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Initialize database
    db.init_app(app)
    
    return app

def init_db():
    """Initialize the database with all required tables"""
    app = create_app()
    
    # Get database URI to check if it's SQLite or PostgreSQL
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    if db_uri.startswith('sqlite'):
        # For SQLite, handle file creation
        db_path = 'instance/app.db'
        if os.path.exists(db_path):
            logger.info(f"Removing existing database at {db_path}")
            os.remove(db_path)
        
        # Ensure the instance directory exists
        os.makedirs('instance', exist_ok=True)
    else:
        # For PostgreSQL (Railway), don't try to delete anything
        logger.info("Using external database (PostgreSQL)")
    
    # Create the database tables
    with app.app_context():
        try:
            logger.info("Creating database tables")
            db.create_all()
            logger.info("Database initialization complete")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            # Don't raise the exception in Railway - tables might already exist
            if not db_uri.startswith('postgres'):
                raise

if __name__ == '__main__':
    init_db()
    print("Database has been initialized successfully.")