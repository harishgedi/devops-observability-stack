# Production-ready Dockerfile for DevOps Observability Stack
# Author: Gedi Harish | github.com/harishgedi

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r observability && useradd -r -g observability observability

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY dashboards/ ./dashboards/

# Create necessary directories
RUN mkdir -p /app/dashboards /app/logs /app/data && \
    chown -R observability:observability /app

# Switch to non-root user
USER observability

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "-m", "uvicorn", "src.monitoring_service:app", "--host", "0.0.0.0", "--port", "8000"]
