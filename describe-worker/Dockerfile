FROM python:3.14-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

# Copy resize-worker code
COPY describe_worker.py ./

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "python", "describe_resize-worker.py"]
