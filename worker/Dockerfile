FROM python:3.14-slim

WORKDIR /worker

# Copy uv binary from Astral's image (fast + simple)
COPY --from=ghcr.io/astral-sh/uv:debian /usr/local/bin/uv /usr/local/bin/uv

# Copy dependency files first (better caching)
COPY pyproject.toml uv.lock ./

# Install exactly what's in uv.lock (reproducible)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy the worker code
COPY worker.py .

ENV IMAGE_ROOT=/app/uploads

CMD ["uv", "run", "python", "-u", "worker.py"]
