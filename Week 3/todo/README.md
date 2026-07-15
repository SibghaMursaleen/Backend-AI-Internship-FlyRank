<h1 align="center">🔷 Todo CRUD API</h1>

<p align="center">
  A clean, robust FastAPI-based Todo CRUD API supporting in-memory or PostgreSQL repositories.<br/>
  Empowers developers with a structured backend to manage, filter, and track tasks.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

---

### 📌 Overview
This project is a high-performance **Todo CRUD API** built using **FastAPI** and **Python**. It provides endpoints for creating, retrieving, updating, and deleting tasks. The system features validation to prevent empty inputs and integrates a clean repository pattern supporting both in-memory storage and PostgreSQL database connectivity.

> **Key:** The API defaults to **in-memory** storage unless configured with PostgreSQL environment variables.

---

### ⚙️ How It Works

| Step | Stage | Description |
|------|-------|-------------|
| 1 | **Request Validation** | Incoming client payloads are validated using **Pydantic** models, rejecting empty titles or incorrect field types with explicit error messages. |
| 2 | **Routing & Controller** | The **FastAPI** application routes requests to their corresponding endpoint handlers in `main.py`. |
| 3 | **Repository Layer** | Handlers query/update the **TaskRepository** abstraction (in-memory or relational database storage). |
| 4 | **Response Formatting** | Successful operations return formatted JSON matching the **TaskResponse** schema, while failures yield consistent JSON error responses. |

---

### 📁 Project Structure

```
todo-CURD-API/
│
├── app/
│   ├── models/
│   │   └── task.py          # Pydantic schemas for request validation & responses
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract base class defining repo interface
│   │   └── in_memory.py     # In-memory implementation of the task repository
│   ├── __init__.py
│   └── config.py            # Environment configuration loader
│
├── main.py                  # API endpoints, FastAPI application, exception handlers
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

> **Note:** `.env` and `.venv` files are excluded from git. Refer to the **Getting Started** section to create your own configuration.

---

### 🚀 Getting Started

#### Prerequisites
- **Python 3.10** or higher installed on your system.
- Virtual environment package (`venv`).

#### Step 1: Clone and Set Up Virtual Environment
Create and activate your Python virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Step 2: Install Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

#### Step 3: Run the Server
Start the FastAPI application with Uvicorn:
```bash
uvicorn main:app --reload
```
The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000) and the Interactive Swagger Documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

### 🎨 Configuration Options

| Environment Variable | Description | Default | Status |
|----------------------|-------------|---------|--------|
| `REPOSITORY_TYPE` | Storage repository to use (`in-memory` or `postgres`) | `in-memory` | ✅ Active |
| `DATABASE_URL` | PostgreSQL connection URL string | *None* | 🔧 Optional |

---

### 🛠️ Tech Stack

| Technology | Role |
|------------|------|
| **FastAPI** | Modern, fast web framework for building APIs with Python |
| **Pydantic** | Data validation and settings management |
| **Uvicorn** | ASGI server implementation for running the application |
| **psycopg2-binary** | PostgreSQL database adapter for Python |

---

### ⚠️ Tips / Best Practices
- Always use the `/docs` interactive documentation to test and verify request schemas.
- For production usage, configure a persistent PostgreSQL database via the `DATABASE_URL` environment variable.
- Run validation-related unit tests before pushing updates.

---

### 📄 License
This project is released under the [MIT License](LICENSE) — free to use, modify, and distribute.

---

<p align="center">
  Built with 🐍 Python &nbsp;·&nbsp; Made by Sibgha Mursaleen
</p>
