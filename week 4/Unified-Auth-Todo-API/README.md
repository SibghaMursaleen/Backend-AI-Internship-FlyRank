<h1 align="center">🔷 Unified Task Management API</h1>

<p align="center">
  A clean, robust FastAPI Todo CRUD API supporting In-Memory, SQLite, and PostgreSQL database storage layers.<br/>
  Orchestrated with Docker Compose and integrated with Redis caching telemetry for premium performance.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-3.0-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

---

### 📌 Overview
This project unifies multiple backend persistence patterns into a single repository using the **Repository Design Pattern**. By toggling a single environment variable, the application dynamically swaps its data layer between **In-Memory arrays**, a **SQLite** database file, or a containerized **PostgreSQL** database service (with **Redis** telemetry). Swapping storage backends requires zero changes to route endpoints or request schemas.

> **Key:** Data persistence is guaranteed locally via `tasks.db` in SQLite mode, or through Docker volumes (`pgdata`) in PostgreSQL mode.

---

### 🔐 User Authentication & Route Protection (Supabase Auth)
This project integrates **Supabase Auth** as the Identity Provider (IdP) to handle user registration, secure session sign-in, session logouts, and token verification via JSON Web Tokens (JWTs).

Some API endpoints are protected using a reusable FastAPI dependency (`get_current_user`) which intercepts incoming request headers, parses the Bearer token, and retrieves/validates the user profile remotely via the Supabase SDK. If the token is missing, expired, or invalid, the request is automatically blocked with an appropriate `401 Unauthorized` response.

Swagger UI is fully integrated with a Bearer Token padlock security scheme at the top right of `/docs` to test authorization interactively.

#### 📋 Authentication API Reference:
| Endpoint | Method | Description | Auth Required | Request Body | Status Code (Success) | Status Code (Failure) |
|---|---|---|---|---|---|---|
| `/auth/signup` | `POST` | Register a new user account | No | `{"email": "...", "password": "..."}` | `201 Created` | `400 Bad Request` |
| `/auth/login` | `POST` | Log in with credentials and receive JWT | No | `{"email": "...", "password": "..."}` | `200 OK` | `400 Bad Request` / `401 Unauthorized` |
| `/auth/logout` | `POST` | Log out the user and invalidate the session | Yes | None | `204 No Content` | `401 Unauthorized` |
| `/protected/profile` | `GET` | Retrieve the authenticated user's profile info | Yes | None | `200 OK` | `401 Unauthorized` |
| `/protected/dashboard` | `GET` | View dashboard content for authorized users | Yes | None | `200 OK` | `401 Unauthorized` |
| `/public/info` | `GET` | Access public info data | No | None | `200 OK` | - |

---


### ⚙️ How It Works

| Step | Stage | Description |
|------|-------|-------------|
| 1 | **Environment Initialization** | The application starts by loading configurations from the `.env` file to decide the storage backend (`REPOSITORY_TYPE`). |
| 2 | **Database Initialization** | The repository controller connects to the selected engine, builds the `tasks` schema if missing, and seeds it with default rows. |
| 3 | **Request Routing** | FASTAPI receives and validates client HTTP requests (via **Pydantic** validation models) and forwards them to the repository. |
| 4 | **SQL Execution** | The repository executes queries (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) on the active database engine. |
| 5 | **Caching & Telemetry** | A dedicated `/redis-ping` route queries Redis to verify connection health and latency in containerized setups. |

---

### 📁 Project Structure

```
Unified-Auth-Todo-API/
│
├── app/
│   ├── models/
│   │   └── task.py          # Pydantic validation & response schemas
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract base class defining repo interface
│   │   ├── in_memory.py     # In-memory array storage (default)
│   │   ├── sqlite.py        # SQLite storage implementation (SQL)
│   │   └── postgres.py      # PostgreSQL storage implementation (psycopg2)
│   ├── __init__.py
│   └── config.py            # Environment configuration loader
│
├── Dockerfile               # Build configuration for FastAPI container
├── docker-compose.yml       # Orchestrates FastAPI app, Postgres DB, and Redis cache
├── init.sql                 # SQL schema and seed data for Postgres initialization
├── main.py                  # API endpoints, FastAPI application, exception handlers
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

> **Note:** `.env` and `.venv` files are excluded from Git. Copy `.env.example` to create your own configuration.

---

### 🚀 Getting Started

#### Option A: Running Locally (In-Memory or SQLite)
This option requires no Docker or database installation.

1. **Activate Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   Create a `.env` file in the project root:
   ```env
   REPOSITORY_TYPE=sqlite
   SQLITE_DB_PATH=tasks.db
   ```
4. **Start the Server**:
   ```bash
   uvicorn main:app --reload
   ```
   API docs will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

#### Option B: Running via Docker Compose (PostgreSQL & Redis)
This option launches the full production-grade stack inside isolated containers.

1. **Configure Environment**:
   Create a `.env` file in the project root:
   ```env
   REPOSITORY_TYPE=postgres
   DATABASE_URL=postgresql://postgres:postgres@db:5432/todo_db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=todo_db
   REDIS_HOST=redis
   REDIS_PORT=6379
   ```
2. **Build and Run the Containers**:
   ```bash
   docker-compose up --build
   ```
   Docker Compose will build your FastAPI image, wait for Postgres and Redis container healthchecks to pass, and start the app at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

### 🎨 Configuration Options

| Environment Variable | Description | Default | Status |
|----------------------|-------------|---------|--------|
| `REPOSITORY_TYPE` | Storage repository to use (`in-memory`, `sqlite`, or `postgres`) | `in-memory` | ✅ Active |
| `SQLITE_DB_PATH` | SQLite database file location (SQLite mode) | `tasks.db` | ✅ Active |
| `DATABASE_URL` | PostgreSQL connection URL string (Postgres mode) | *None* | ✅ Active |
| `REDIS_HOST` | Hostname for Redis cache container | `redis` | ✅ Active |
| `REDIS_PORT` | Port number for Redis cache container | `6379` | ✅ Active |
| `SUPABASE_URL` | Supabase project API URL | *None* | ✅ Active |
| `SUPABASE_KEY` | Supabase anon API Key | *None* | ✅ Active |


---

### 🛠️ Tech Stack

| Technology | Role |
|------------|------|
| **FastAPI** | Modern web framework for building RESTful APIs with Python |
| **SQLite** | Local self-contained file database for lightweight persistence |
| **PostgreSQL** | Relational database management system for production persistence |
| **Redis** | High-performance caching telemetry |
| **Docker** | Orchestrates app and databases into containerized services |
| **Pydantic** | Request schemas and input data validation |

---

### ⚠️ Tips / Best Practices
- Verify database schemas and test inputs inside the interactive Swagger `/docs` page.
- Always use the `/health` and `/redis-ping` endpoints to verify service status in containerized modes.
- Avoid committing database binary files (`*.db`) to Git (ignored by default).

---

### 📄 License
This project is released under the [MIT License](LICENSE) — free to use, modify, and distribute.

---

<p align="center">
  Built with 🐍 Python &nbsp;·&nbsp; Made by Sibgha Mursaleen
</p>
