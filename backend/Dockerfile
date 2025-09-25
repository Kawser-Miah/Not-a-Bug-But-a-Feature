FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set working directory
WORKDIR /app

# Copy dependency manifests first (better layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (creates .venv)
RUN uv sync --locked \
    && ln -s .venv venv

# Make virtualenv available on PATH
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application source
COPY . .

# Ensure entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Expose FastAPI default port
EXPOSE 8000

# Healthcheck (simple TCP check)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c 'import socket,sys; s=socket.socket(); \
    s.connect(("127.0.0.1",8000)); s.close()' || exit 1

# Default environment (can be overridden in compose)
ENV PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:///./hackathon.db

# Run migrations then launch server
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
