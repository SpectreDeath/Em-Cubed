# Em-Cubed container base image for skill execution
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install wasmtime for WASM surface
RUN curl https://wasmtime.dev/install.sh -sSf | bash

# Copy application
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[dev]" 2>/dev/null || pip install --no-cache-dir -e .

# Copy skills directory
COPY skills/ ./skills/

# Install pygls for LSP
RUN pip install pygls pyyaml

# Create entrypoint
ENTRYPOINT ["python", "-m", "em_cubed.container_executor"]