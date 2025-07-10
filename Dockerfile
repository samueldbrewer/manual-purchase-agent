# Full PartsPro Dockerfile for Railway
FROM python:3.11-slim

WORKDIR /app

# Install Node.js and system dependencies including Playwright dependencies
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get update && apt-get install -y \
    nodejs \
    build-essential \
    curl \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Install Node.js dependencies for recording system
WORKDIR /app/recording_system
RUN npm install && npx playwright install chromium
WORKDIR /app

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