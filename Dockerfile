# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV PORT=7860

# Install system dependencies needed for compiling psycopg2 and running git/pylint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for Hugging Face Spaces
RUN useradd -m -u 1000 user

WORKDIR /app

# Ensure proper permissions
RUN chown -R user:user /app

USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Copy dependencies first to leverage caching
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY --chown=user:user . .

# Expose port
EXPOSE 7860

# Run database setup & column migrations and launch production server with gunicorn
CMD ["sh", "-c", "python init_db.py && gunicorn --bind 0.0.0.0:${PORT:-7860} --timeout 180 run:app"]
