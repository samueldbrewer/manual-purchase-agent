# Full PartsPro Dockerfile for Railway
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p uploads/screenshots instance

# Initialize database
RUN python scripts/init_db.py || echo "Database initialization skipped"

# Use Railway's PORT environment variable
EXPOSE $PORT

# Run with gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --access-logfile - --error-logfile - 'app:create_app()'