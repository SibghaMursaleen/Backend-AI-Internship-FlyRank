<h1 align="center">🔷 Postgres & Redis Docker TODO API</h1>

<p align="center">
  A clean, robust FastAPI-based Todo CRUD API integrated with PostgreSQL and Redis.<br/>
  Orchestrated with Docker Compose to provide out-of-the-box database persistence and caching telemetry.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

---

### 📌 Overview
This project is an advanced iteration of the **FastAPI Todo CRUD API**, migrated from an in-memory repository to a persistent **PostgreSQL** database and integrated with **Redis**. The entire stack (FastAPI service, Postgres DB, and Redis cache) runs inside isolated containers coordinated via **Docker Compose**. This migration proves the success of the repository design pattern, as swapping storage mechanisms was completed without altering any API endpoints or business logic.

> **Key:** Data persistence is guaranteed across container restarts by attaching a Docker volume to the PostgreSQL database container.

---

### ⚙️ How It Works

| Step | Stage | Description |
|------|-------|-------------|
| 1 | **Environment Initialization** | The application starts by loading configurations from the `.env` file to decide the repository type (`in-memory` vs `postgres`). |
| 2 | **Orchestration Healthchecks** | Docker Compose launches the stack, using healthcheck logic to delay starting the FastAPI app until the Postgres and Redis containers are healthy and accepting connections. |
| 3 | **Schema Seeding** | The first time Postgres starts, it executes `init.sql` to build the `tasks` table and seed it with initial items. |
| 4 | **API & Redis Ping Routing** | Standard routes in `main.py` handle HTTP request payloads validated via `Pydantic` models. A dedicated `/redis-ping` route verifies connection connectivity to the Redis container. |
| 5 | **Postgres Storage Layer** | Queries are processed through the `PostgresTaskRepository` implementing the abstract `TaskRepository` interface, using `psycopg2` for execution. |

---

### 📁 Project Structure

```
Postgres-Docker-TODO-API/
│
├── app/
│   ├── models/
│   │   └── task.py          # Pydantic schemas for request validation & responses
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract base class defining repo interface
│   │   ├── in_memory.py     # In-memory repository implementation (for fallback)
│   │   └── postgres.py      # NEW: PostgreSQL repository implementation
│   ├── __init__.py
│   └── config.py            # Environment configuration loader with Redis settings
│
├── main.py                  # API endpoints, exception handlers, and /redis-ping route
├── requirements.txt         # Project dependencies including psycopg2 and redis-py
├── Dockerfile               # Container build recipe for the FastAPI service
├── docker-compose.yml       # Multi-container orchestration (App, Postgres, Redis)
├── init.sql                 # SQL startup script (table creation + seeding)
├── .env.example             # Template env config
└── README.md                # Project documentation
```

> **Note:** The `.env` file contains sensitive credentials and is gitignored by default. Use `.env.example` as a starting point.

---

### 🚀 Getting Started

#### Prerequisites
* **Docker** installed and running on your system.
* **Docker Compose** v2+ installed.

#### Step 1: Set Up Local Environment Configurations
Clone or locate the directory, copy the template `.env.example` file to create your own local `.env` configuration file:
```bash
copy .env.example .env
```
Ensure `REPOSITORY_TYPE=postgres` is set in the `.env` file to enable the PostgreSQL repository.

#### Step 2: Build and Run the Compose Stack
Start the whole system using a single Docker Compose command:
```bash
docker compose up --build -d
```
Docker Compose will download the base images, build the custom FastAPI image, run health checks for PostgreSQL and Redis, and then launch the backend service.

#### Step 3: Verify the Running Services
1. Open the Interactive Swagger Documentation at [http://localhost:8000/docs](http://localhost:8000/docs) to verify API routing.
2. Call the `GET /redis-ping` endpoint. You should receive a `"redis_status": "connected"` response indicating the Redis cache is pingable.
3. Call the `GET /tasks` endpoint. You should see the three default seeded tasks (`Buy groceries`, `Read a book`, and `Work out`).

#### Step 4: Proving Persistence Across Container Restarts
To verify that tasks are stored permanently and survive system restarts:
1. Create a new task (e.g. `POST /tasks` with `{"title": "Verify docker volume persistence"}`).
2. Verify it is successfully added (it will be assigned `id: 4`).
3. Stop and remove the active containers:
   ```bash
   docker compose down
   ```
4. Start the stack back up:
   ```bash
   docker compose up -d
   ```
5. Fetch all tasks using `GET /tasks`. Note that the new task (`id: 4`) is still present. This proves that the Docker volume maps correctly and keeps your data intact!

---

### 🎨 Configuration Options

| Environment Variable | Description | Default | Status |
|----------------------|-------------|---------|--------|
| `REPOSITORY_TYPE` | Storage repository to use (`in-memory` or `postgres`) | `in-memory` | ✅ Active |
| `DATABASE_URL` | PostgreSQL connection URL string | *None* | ✅ Active |
| `POSTGRES_USER` | PostgreSQL user account name | `postgres` | ✅ Active |
| `POSTGRES_PASSWORD` | PostgreSQL user password | `postgres` | ✅ Active |
| `POSTGRES_DB` | Name of the database to create | `todo_db` | ✅ Active |
| `REDIS_HOST` | Hostname of the Redis server | `redis` | ✅ Active |
| `REDIS_PORT` | Port number of the Redis server | `6379` | ✅ Active |

---

### ⚡ Performance Optimization (Stretch Goal)

To optimize lookup queries targeting specific tasks by their name/title (e.g. searching or filtering), a B-Tree index is defined on the `title` column of the `tasks` table:
```sql
CREATE INDEX idx_tasks_title ON tasks(title);
```

#### Verification & Performance Analysis (`EXPLAIN ANALYZE`)

Below is the query plan execution analysis comparing queries run before and after the index is applied.

##### 1. Query Plan Before Creating Index (Sequential Scan)
Without the index, Postgres performs a full-table scan (Sequential Scan) to evaluate the query filter:
```sql
EXPLAIN ANALYZE SELECT * FROM tasks WHERE title = 'Work out';
```
**Output:**
```text
                                            QUERY PLAN                                            
--------------------------------------------------------------------------------------------------
 Seq Scan on tasks  (cost=0.00..11.75 rows=1 width=521) (actual time=0.052..0.053 rows=1 loops=1)
   Filter: ((title)::text = 'Work out'::text)
   Rows Removed by Filter: 2
 Planning Time: 3.378 ms
 Execution Time: 0.490 ms
```

##### 2. Query Plan After Creating Index (Index Scan)
For small tables, PostgreSQL optimizer defaults to a sequential scan because it is cheaper than index loading. By setting `SET enable_seqscan = off;` to simulate how Postgres will handle this on a larger database scale, we force index utilization:
```sql
SET enable_seqscan = off;
EXPLAIN ANALYZE SELECT * FROM tasks WHERE title = 'Work out';
```
**Output:**
```text
                                                       QUERY PLAN                                                        
-------------------------------------------------------------------------------------------------------------------------
 Index Scan using idx_tasks_title on tasks  (cost=0.13..8.15 rows=1 width=521) (actual time=0.859..0.860 rows=1 loops=1)
   Index Cond: ((title)::text = 'Work out'::text)
 Planning Time: 1.457 ms
 Execution Time: 1.103 ms
```

---

### 🛠️ Tech Stack

| Technology | Role |
|------------|------|
| **FastAPI** | Modern, fast ASGI web framework for building APIs with Python |
| **PostgreSQL** | Relational SQL database for robust, ACID-compliant storage |
| **Redis** | In-memory database used for high-speed caching and queuing |
| **Docker Compose** | Orchestration tool for defining and running multi-container applications |
| **Pydantic** | Data validation schemas for endpoints validation |
| **psycopg2-binary** | PostgreSQL database driver for Python |
| **redis-py** | Python client library for connecting to Redis |

---

### ⚠️ Tips / Best Practices
* **Database Readiness:** Always use health checks in `docker-compose.yml` to prevent the FastAPI app from starting before PostgreSQL is ready. Otherwise, the app will crash on start due to database connection refusal.
* **Volume Isolation:** Named volumes like `pgdata` are independent of container life-cycles. Do not delete the volume unless you want to wipe the database clean.
* **Service Names as Hostnames:** Inside the Docker network, containers resolve other services by their compose names (e.g., connection url points to `@db:5432` rather than `@localhost:5432`).

---

### 📄 License
This project is released under the [MIT License](LICENSE) — free to use, modify, and distribute.

---

<p align="center">
  Built with 🐳 Docker &nbsp;·&nbsp; Made by Sibgha Mursaleen
</p>
