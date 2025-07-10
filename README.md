# PartsPro - Minimal Railway Deployment

## Overview

This is a simplified version of the PartsPro application designed for Railway deployment. It includes:

1. **Complete API Suite** - All working endpoints for parts, manuals, suppliers, etc.
2. **Mobile V4 Interface** - Clean, responsive web interface
3. **Minimal Dependencies** - Removed recording system and unnecessary components

## What Was Removed

### Recording System (Complete Removal)
- `recording_system/` directory
- `recordings/` directory  
- `api/recording_studio_api.py`
- All purchase automation functionality

### Interfaces (Simplified)
- V3 interface (`static/api-demo/v3/`)
- V2 interface (`static/api-demo/v2/`)
- Old main interface files
- Templates and web UI routes

### Documentation & Backup Files
- Multiple markdown documentation files
- Archive directories and backups
- Multiple Dockerfile variants
- Deployment scripts

### Data & Test Files
- Large CSV data files
- Log files
- Screenshot directories
- Most test files

## Current Structure

```
/
├── api/                    # API endpoints
├── models/                 # Database models
├── services/              # Core services (recreated)
├── static/api-demo/v4/    # Mobile V4 interface
├── scripts/               # Utility scripts
├── utils/                 # Helper utilities
├── app.py                 # Main Flask application
├── config.py              # Configuration
├── requirements.txt       # Minimal dependencies
├── Dockerfile             # Railway deployment
└── README.md              # This file
```

## API Endpoints

The following API endpoints are available:

- `/api/manuals/*` - Manual search and processing
- `/api/parts/*` - Part resolution and management  
- `/api/suppliers/*` - Supplier search
- `/api/profiles/*` - Billing profile management
- `/api/enrichment/*` - Data enrichment
- `/api/screenshots/*` - Website screenshots
- `/api/system/*` - System health and status

## Environment Variables

Required for Railway deployment:

```env
SERPAPI_KEY=your_serpapi_key
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_encryption_key
DATABASE_URI=postgresql://user:pass@host:port/db
```

## Railway Deployment

1. **Connect Repository** to Railway
2. **Set Environment Variables** in Railway dashboard
3. **Deploy** - Railway will automatically use the Dockerfile

The application will be available at the Railway-provided URL.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Initialize database
python scripts/init_db.py

# Run application
flask run --host=0.0.0.0 --port=7777
```

## Key Features Retained

- **Real API Functionality** - All endpoints work with actual data
- **Mobile V4 Interface** - Full-featured responsive UI
- **PDF Processing** - Manual parsing with GPT-4.1-Nano
- **Part Resolution** - OEM part number resolution
- **Supplier Search** - AI-powered supplier ranking
- **Data Enrichment** - Enhanced part information

## Size Reduction

- **From**: ~40,000+ files with recording system
- **To**: ~480 files (excluding venv)
- **Size**: ~850KB core application (excluding dependencies)

## Notes

- Purchase automation functionality removed
- Recording system completely removed
- All API endpoints maintained and functional
- Mobile V4 interface cleaned and optimized
- Ready for Railway deployment with minimal footprint