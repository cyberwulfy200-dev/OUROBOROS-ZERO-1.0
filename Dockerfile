# OUROBOROS-ZERO - Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Metadata
LABEL maintainer="research@ouroboros-zero.dev"
LABEL version="1.0-ZERO"
LABEL description="OUROBOROS-ZERO - The Eternal Serpent of Digital Replication"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    OUROBOROS_ENV=production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 -s /bin/bash replicator

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=replicator:replicator src/ ./src/
COPY --chown=replicator:replicator config/ ./config/
COPY --chown=replicator:replicator tests/ ./tests/

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R replicator:replicator /app/data /app/logs

# Create volume mount points
VOLUME ["/app/data", "/app/logs", "/app/config"]

# Switch to non-root user
USER replicator

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('/app/data/replicator.db') else 1)"

# Expose ports (if needed for future features)
# EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["python", "-u", "src/ouroboros_zero.py"]

# Default command
CMD []
