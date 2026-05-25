# Base image for secure skill execution
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY pyproject.toml .
COPY README.md .

# Install dependencies
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/
COPY skills/ ./skills/
COPY tests/ ./tests/

# Create non-root user directories
RUN mkdir -p /app/logs /app/cache && \
    chown -R appuser:appuser /app/logs /app/cache /app/skills /app/src

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONPATH=/app/src
ENV EM_CUBED_SKILLS_DIR=/app/skills
ENV EM_CUBED_LOG_DIR=/app/logs
ENV EM_CUBED_CACHE_DIR=/app/cache

# Default command
CMD ["python", "-m", "em_cubed"]