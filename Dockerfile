# Dockerfile for PurrCrypt API (Python-only version)
# Simple, lightweight container without Rust dependencies

FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python application files
COPY requirements.txt .
COPY app.py .
COPY api/ ./api/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt     

# Create a non-root user for security
RUN useradd -m -u 1000 purrcrypt && \
    chown -R purrcrypt:purrcrypt /app

USER purrcrypt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5000

# Expose port
EXPOSE 5000

# Health check
# Health check — uses API_PREFIX env var (defaults to /api)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f "http://localhost:${PORT:-5000}${API_PREFIX:-/api}/health" || exit 1

# Run the Flask API with Gunicorn (production WSGI server)
# 4 workers, binding to all interfaces, with access logging
CMD sh -c "gunicorn --bind ${HOST:-0.0.0.0}:${PORT:-5000} --workers 4 --access-logfile - --error-logfile - app:app"

