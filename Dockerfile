# Dockerfile
FROM python:3.14-slim

# System deps for psycopg, etc.
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Copy dependency metadata
COPY pyproject.toml uv.lock ./

# Copy source code and db scripts
COPY app ./app
COPY db ./db

# Create uploads dir inside container
RUN mkdir -p /app/uploads

# Install dependencies using uv + lockfile
RUN uv sync --locked --no-dev

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI app
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
