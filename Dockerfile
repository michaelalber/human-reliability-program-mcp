# HRP MCP Server Dockerfile
# Deployment container for Human Reliability Program MCP server

FROM python:3.10-slim

LABEL maintainer="HRP MCP Project"
LABEL description="Human Reliability Program (10 CFR 712) MCP Server"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HRP_MCP_TRANSPORT=stdio \
    HRP_CHROMA_PERSIST_DIR=/app/data/chroma \
    HRP_AUDIT_LOG_PATH=/app/logs/audit.jsonl

# Create app user for security
RUN groupadd -r hrp && useradd -r -g hrp hrp

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/data/chroma /app/logs && \
    chown -R hrp:hrp /app

# Switch to non-root user
USER hrp

# Expose port for HTTP transport (optional)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import hrp_mcp; print('healthy')" || exit 1

# Default command - run MCP server
ENTRYPOINT ["python", "-m", "hrp_mcp.server"]
