FROM python:3.14-slim

# Basic build tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

WORKDIR /worker

# Project metadata and lockfile
COPY pyproject.toml uv.lock ./

# Install dependencies according to the lockfile
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

# Application code
COPY sentiment_worker.py ./

# Run worker
CMD ["uv", "run", "python", "sentiment_worker.py"]
