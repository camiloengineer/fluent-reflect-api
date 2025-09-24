# syntax=docker/dockerfile:1
# Multi-stage build for smaller production image
FROM python:3.11-slim as base

# Set env vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# System deps (add build-essential only when needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY app ./app
# No copiamos .env para producción. Usa `gcloud run deploy --set-env-vars` o Secret Manager.

# Create non-root user
RUN useradd -u 1001 -m appuser
USER appuser

# Expose Cloud Run port (Cloud Run sets $PORT)
ENV PORT=8080
EXPOSE 8080

# Healthcheck (optional, Cloud Run has its own but helpful locally)
HEALTHCHECK CMD curl -f http://localhost:${PORT}/health || exit 1

# Start Uvicorn using the PORT env var provided by Cloud Run.
# Note: Using a shell form so that $PORT is expanded (JSON array form would pass the literal string).
CMD ["/bin/sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
