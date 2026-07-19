# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV PORT=5000

# Install system dependencies needed for compiling psycopg2 and running git/pylint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies first to leverage caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port
EXPOSE 5000

# Run database setup and launch production server with gunicorn
CMD python -c "from app import create_app, db; app = create_app(); ctx = app.app_context(); ctx.push(); db.create_all()" && \
    gunicorn --bind 0.0.0.0:5000 --timeout 120 "run:app"
