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

### **Backend (FastAPI)**
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

### **Frontend (Angular)**
- ✔ Create post (with image upload)  
- ✔ List all posts  
- ✔ Search posts by user  
- ✔ Reusable `app-post-card` component  
- ✔ Clean Bootstrap UI  

---

# 🧱 Project Structure

```
project-root/
├─ .github/
├─ app/                        # FastAPI backend package
│  ├─ __init__.py
│  ├─ main.py                  # FastAPI app
│  └─ service.py               # DB + business logic
├─ db/
│  └─ init.sql                 # creates post table
├─ frontend/
│  └─ social-frontend/         # Angular project root
│     ├─ src/
│     ├─ angular.json
│     ├─ package.json
│     └─ ...                   # other Angular files
├─ tests/
│  ├─ conftest.py
│  ├─ test_api_posts.py
│  └─ test_service_posts.py
├─ uploads/                    # image files served via /static
│  ├─ charmander.png
│  ├─ bulbasaur.png
│  └─ squirtle.png
├─ .env.example
├─ .gitignore
├─ .python-version
├─ docker-compose.yml
├─ main.py                     # old step-1 script (DB check)
├─ openapi.yml
├─ pyproject.toml
├─ pytest.ini
├─ README.md
├─ team_log.md
└─ uv.lock

```

---

# ⚙️ Backend Setup

## 1️⃣ Install uv

**Linux / macOS**
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

**Windows PowerShell**
```powershell
iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex
```

Verify:
```bash
uv --version
```

---

## 2️⃣ Install Python 3.14

```bash
uv python install 3.14
uv python pin 3.14
```

Verify:
```bash
uv run python --version
```

---

## 3️⃣ Install backend dependencies

```bash
uv sync --locked
```

---

## 4️⃣ Start PostgreSQL

Using Docker:

```bash
docker compose up -d db
```

This loads `db/init.sql` automatically and creates the `post` table.

---

## 5️⃣ Run the backend API

Development server:

```bash
uv run uvicorn app.main:app --reload
```

Open:

- API Docs → http://localhost:8000/docs  
- Images → http://localhost:8000/static/<filename>

---

# 💻 Frontend Setup (Angular)

## 1️⃣ Install Node.js

Download from:

👉 https://nodejs.org

Verify:

```bash
node -v
npm -v
```

---

## 2️⃣ Install Angular CLI

```bash
npm install -g @angular/cli
```

---

## 3️⃣ Install frontend dependencies

```bash
cd frontend/social-frontend
npm install
```

---

## 4️⃣ Run the Angular dev server

```bash
ng serve --open
```

Frontend: http://localhost:4200  
Backend: http://localhost:8000

---

# 🧪 Running Tests

Backend tests:

```bash
uv run pytest
```

---

# 🖼 Image Handling

- Images saved to `uploads/`
- Served via `/static/<filename>`
- Angular renders via:

```html
<img [src]="'http://localhost:8000/static/' + post.image">
```

---

# 🎯 Summary

You now have:

- ✔ FastAPI backend with image uploads  
- ✔ Angular frontend with Bootstrap  
- ✔ PostgreSQL database  
- ✔ Full test suite + CI  
- ✔ Working full-stack project  
