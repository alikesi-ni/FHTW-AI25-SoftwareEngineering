# 🗂 Social-App — Database Check (Step 1)

This is the first step of developing a simple social media app.  
It connects to a **PostgreSQL** database and checks whether the table **`post`** exists in the `public` schema, printing how many entries it contains.

# 🗂 Social-App — REST API + PostgreSQL (Step 2)

This project implements a simple social media backend using **FastAPI**, **PostgreSQL**, and **psycopg**.  
You can create posts, fetch posts, search posts, and retrieve the latest entry.

The API automatically exposes a full **OpenAPI specification** and documentation UI.

---

## 🚀 Features

- ✔ Create a post (`POST /posts`)
- ✔ Get post by ID (`GET /posts/{id}`)
- ✔ Get the latest post (`GET /posts/latest`)
- ✔ Search posts (`GET /posts/search?q=...`)
- ✔ Automatic OpenAPI docs (`/docs` & `/openapi.json`)
- ✔ PostgreSQL database with init script
- ✔ Image validation (image must exist inside `/uploads`)

---

## 📦 Requirements

- Python 3.12+
- `fastapi`, `uvicorn`, `psycopg`
- Docker (for PostgreSQL)

---

## 🚀 Getting Started

### 1️⃣ Install **uv**

**macOS / Linux**
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
# Restart your shell or reload your profile so `uv` is on PATH
uv --version
```

**Windows (PowerShell)**
```powershell
iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex
uv --version
```

> If `uv` isn’t found after install, restart your terminal and ensure its bin directory is on your PATH.

---

### 2️⃣ Install **Python 3.14** (managed by uv)

This project targets **Python 3.14**.

Run this once:
```bash
uv python install 3.14
uv python pin 3.14
```

Verify:
```bash
uv run python --version   # should print Python 3.14.x
```

> ⚠️ `uv sync --locked` will **not** automatically install Python 3.14 — you must install/pin it first.

---

### 3️⃣ Install Dependencies

Always use the lockfile for reproducible installs:
```bash
uv sync --locked
```

This installs exactly the same dependency versions recorded in `uv.lock`.

---

### 4️⃣ Configure the Environment & Database

Copy the example environment file and adjust the values as needed:
```bash
cp .env.example .env
```

Example `.env` contents:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social
DB_USER=admin
DB_PASSWORD=password
```

Start the PostgreSQL container:
```bash
docker compose up -d db
```

---

### 5️⃣ Run the Application

```bash
uv run python main.py
```

Example output:
```
Table 'post' exists and contains 0 entries.
```

---

## 🗂 Project Structure

```
social-app/
├─ .env.example
├─ .gitignore
├─ .python-version
├─ docker-compose.yml
├─ main.py
├─ pyproject.toml
├─ uv.lock
├─ db/
│  └─ init.sql
└─ README.md
```

---

## 💡 Notes

- Keep `uv.lock` **committed** — it guarantees everyone installs the same versions.  
- Always use `uv sync --locked`.  
- The app currently just checks whether the `post` table exists and counts rows.  
- Future steps can extend this to actually insert and fetch posts.
