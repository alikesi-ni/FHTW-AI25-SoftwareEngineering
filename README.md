# 📱 Social App — Full-Stack Project  
FastAPI backend • PostgreSQL • Angular frontend • Image uploads

This project implements a small social media application with:

- A **FastAPI backend** (Python 3.14, uv, PostgreSQL)
- An **Angular frontend** (Node.js, npm, Bootstrap)
- Image upload support  
- Search & filter API  
- Automated tests + GitHub Actions CI

---

# 🚀 Features

## **Backend (FastAPI)**
- ✔ Create posts with **comment**, **image**, or both  
- ✔ Query all posts (`GET /posts`)
- ✔ Filter by user (`GET /posts?user=alice`)
- ✔ Limit & sorting (`limit`, `order_by`, `order_dir`)
- ✔ Search (`GET /posts/search?q=...`)
- ✔ Image uploads stored in `/uploads`
- ✔ Static image serving (`/static/<filename>`)
- ✔ PostgreSQL storage
- ✔ Clear service-layer logic
- ✔ Full OpenAPI schema automatically generated

## **Frontend (Angular)**
- ✔ Create post (with image upload)  
- ✔ List all posts  
- ✔ Search posts by user  
- ✔ Reusable `app-post-card` component  
- ✔ Clean Bootstrap UI  

---

# 🧱 Project Structure

```text
project-root/
├─ .github/
├─ app/                        # FastAPI backend package
│  ├─ __init__.py
│  ├─ main.py
│  └─ service.py
├─ db/
│  └─ init.sql
├─ frontend/
│  └─ social-frontend/
│     ├─ src/
│     ├─ angular.json
│     ├─ package.json
│     └─ ...
├─ tests/
│  ├─ conftest.py
│  ├─ test_api_posts.py
│  └─ test_service_posts.py
├─ uploads/
│  ├─ charmander.png
│  ├─ bulbasaur.png
│  └─ squirtle.png
├─ .env.local.example
├─ .env.docker.example
├─ .gitignore
├─ .python-version
├─ docker-compose.yml
├─ main.py
├─ openapi.yml
├─ pyproject.toml
├─ pytest.ini
├─ README.md
├─ team_log.md
└─ uv.lock
```

---

# ⚙️ Backend Setup

You can run the backend in two ways:

- **Option A:** Local development using uv  
- **Option B:** Fully containerized using Docker / docker-compose

---

# 0️⃣ Prepare environment files

Two example environment files are provided:

- `.env.local.example` → for local development  
- `.env.docker.example` → for docker-compose

Create real env files:

```bash
cp .env.local.example .env.local
cp .env.docker.example .env.docker
```

### Example `.env.local`
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social
DB_USER=admin
DB_PASSWORD=password
IMAGE_ROOT=uploads
```

### Example `.env.docker`
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=social
DB_USER=admin
DB_PASSWORD=password
IMAGE_ROOT=/app/uploads
```

---

# 🔹 Option A — Local Development (uv + local PostgreSQL)

## 1️⃣ Install uv

Linux / macOS:
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:
```powershell
iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex
```

Verify:
```bash
uv --version
```

## 2️⃣ Install Python 3.14

```bash
uv python install 3.14
uv python pin 3.14
```

Verify:
```bash
uv run python --version
```

## 3️⃣ Install backend dependencies

```bash
uv sync --locked
```

## 4️⃣ Start PostgreSQL (using docker-compose)

```bash
docker compose --env-file .env.local up -d db
```

## 5️⃣ Run the backend API locally

Make sure `.env.local` is loaded, then:

```bash
uv run uvicorn app.main:app --reload
```

Open:  
- **API Docs:** http://localhost:8000/docs  
- **Images:** http://localhost:8000/static/<filename>

---

# 🔹 Option B — Backend in Docker (Production‑style)

## 1️⃣ Build the backend image
```bash
docker build -t social-backend .
```

## 2️⃣ Start backend + DB
```bash
docker compose --env-file .env.docker up -d
```

## 3️⃣ Access the backend
- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  
- Images: http://localhost:8000/static/<filename>

---

# 💻 Frontend Setup (Angular)

## 1️⃣ Install Node.js

https://nodejs.org/

Verify:
```bash
node -v
npm -v
```

## 2️⃣ Install Angular CLI
```bash
npm install -g @angular/cli
```

## 3️⃣ Install dependencies
```bash
cd frontend/social-frontend
npm install
```

## 4️⃣ Run dev server
```bash
ng serve --open
```

Frontend: http://localhost:4200  
Backend: http://localhost:8000  

---

# 🧪 Running Tests

```bash
uv run pytest
```

---

# 🖼️ Image Handling

- Images saved to `uploads/`
- Served via `/static/<filename>`
- Angular usage:

```html
<img [src]="'http://localhost:8000/static/' + post.image">
```

---

# 🎯 Summary

You now have:

✔ FastAPI backend with image uploads  
✔ Angular frontend  
✔ PostgreSQL database  
✔ Environment-specific configuration  
✔ Full test suite + CI  
✔ Optional Dockerized backend
