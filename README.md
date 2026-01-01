# 📱 Social App — Full-Stack Project  
FastAPI backend • PostgreSQL • Angular frontend • RabbitMQ resize-worker • Image uploads

This project implements a small social media application with:

- FastAPI backend (Python 3.12+, uv, SQLAlchemy, PostgreSQL)
- Angular frontend (Node.js, Angular, Bootstrap)
- Asynchronous image resizing via RabbitMQ + resize-worker
- Original + reduced image storage
- Automated tests + GitHub Actions CI

---

# 🚀 Features

## Backend (FastAPI)
- Create posts with content, image, or both
- Query all posts (`GET /posts`)
- Filter by user (`GET /posts?user=alice`)
- Limit & sorting (`limit`, `order_by`, `order_dir`)
- Search (`GET /posts/search?q=...`)
- Multipart image uploads
- Static image serving:
  - `/static/original/<filename>`
  - `/static/reduced/<filename>`
- PostgreSQL persistence (SQLAlchemy)
- OpenAPI schema (`/docs`)
- Image status tracking (`PENDING | READY | FAILED`)

## Image resize-worker
- RabbitMQ-based background processing
- Resizes images (max width 512)
- Removes transparency by compositing onto a white background (for PNGs with alpha)
- Writes reduced images to `uploads/reduced/`
- Updates `image_status` in the database

## Frontend (Angular)
- Create posts with image upload
- Default display uses the reduced image
- Click to view the full-size image (modal/lightbox)
- Post list + user filter
- Bootstrap UI

---

# 🧱 Project Structure

```text
project-root/
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py
│  │  ├─ routes.py
│  │  ├─ service.py
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  ├─ db.py
│  │  └─ queue.py
│  ├─ tests/
│  ├─ Dockerfile
│  ├─ pyproject.toml
│  └─ uv.lock
│
├─ resize-worker/
│  ├─ resize-worker.py
│  ├─ Dockerfile
│  ├─ pyproject.toml
│  └─ uv.lock
│
├─ frontend/
│  └─ social-frontend/
│     ├─ src/
│     ├─ package.json
│     └─ ...
│
├─ db/
│  └─ init.sql
│
├─ uploads/
│  ├─ original/
│  └─ reduced/
│
├─ .env.local.example
├─ .env.docker.example
├─ docker-compose.yml
├─ README.md
└─ team_log.md
```

---

# ⚙️ Environment Configuration

Two environment setups are supported:

- `.env.local` for local development (backend/frontend on host)
- `.env.docker` for docker-compose networking

Create them from the examples:

```bash
cp .env.local.example .env.local
cp .env.docker.example .env.docker
```

Example `.env.local`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social
DB_USER=admin
DB_PASSWORD=password

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE=image_resize

IMAGE_ROOT=uploads
```

Example `.env.docker`:

```env
DB_HOST=db
DB_PORT=5432
DB_NAME=social
DB_USER=admin
DB_PASSWORD=password

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE=image_resize

IMAGE_ROOT=/app/uploads
```

---

# 🔹 Local Development (backend + frontend)

This workflow is useful when you want to debug the backend and/or frontend locally, while still using Docker for infrastructure.

## 1) Start infrastructure (PostgreSQL + RabbitMQ)

```bash
docker compose --env-file .env.local up -d db rabbitmq
```

## 2) Run backend locally (uv)

```bash
cd backend
uv sync --frozen
uv run uvicorn app.main:app --reload
```

Backend:
- http://localhost:8000
- http://localhost:8000/docs

## 3) Run resize-worker (choose one)

### Option A: run resize-worker in Docker (recommended)
```bash
docker compose --env-file .env.docker up -d resize-worker
```

### Option B: run resize-worker locally (uv)
```bash
cd resize-worker
uv sync --frozen
uv run python resize-worker.py
```

## 4) Run frontend locally

```bash
cd frontend/social-frontend
npm install
ng serve --open
```

Frontend:
- http://localhost:4200

The frontend should call the backend at:
- http://localhost:8000

---

# 🔹 Full Docker Setup (all services)

```bash
docker compose --env-file .env.docker up --build
```

Services started:
- PostgreSQL
- RabbitMQ
- Backend API
- resize-worker
- Frontend (nginx)

---

# 🧪 Running Tests

Run backend tests from the backend folder (matches CI):

```bash
cd backend
uv run pytest -q
```

---

# 🖼️ Image Handling

- Originals: `uploads/original/<filename>`
- Reduced: `uploads/reduced/<filename>`
- Backend serves both under `/static/`
- Frontend displays reduced by default and opens the original in a modal on click

---

# 🎯 Summary

- FastAPI backend + SQLAlchemy + Postgres
- Angular frontend
- RabbitMQ + resize-worker for background image processing
- Tests and CI workflows
