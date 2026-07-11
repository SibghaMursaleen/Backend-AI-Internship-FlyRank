<h1 align="center">🔷 Minimal Python Backend</h1>

<p align="center">
  A lightweight FastAPI web server with two JSON endpoints.<br/>
  Built for the FlyRank AI Internship Week 1 Assignment.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

---

## 📌 Overview

A lightweight backend implementation that establishes a simple **request-response loop** using **Python** and **FastAPI**. It provides two structured JSON endpoints for health checks and greetings.

---

## ⚙️ How It Works

| Step | Stage | Description |
|------|-------|-------------|
| 1 | **FastAPI Initialization** | Initializes the core FastAPI application inside `main.py` |
| 2 | **Routing Setup** | Configures routes for `/` and `/status` GET endpoints |
| 3 | **Server Startup** | Uses Uvicorn to run the server on `localhost:8000` |
| 4 | **Response Generation** | Listens for HTTP requests and replies with formatted JSON payloads |

---

## 📁 Project Structure

```
week 1/Minimal Python backed - Assignement 1/
│
├── main.py            # Main FastAPI server script
├── requirements.txt   # Python dependency definitions
└── README.md          # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.8+ installed.
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Steps

#### Step 1: Run the Server
Start the development server:
```bash
uvicorn main:app --reload
```

#### Step 2: Test the Endpoints
You can query the endpoints using `curl` or visit them in your browser:
- **Root**: `curl http://127.0.0.1:8000/`
- **Status**: `curl http://127.0.0.1:8000/status`

---

## 🛠️ Tech Stack

| Technology | Role |
|------------|------|
| **Python** | Primary development language |
| **FastAPI** | High-performance API web framework |
| **Uvicorn** | ASGI server for serving the application |

---

## 📄 License

This project is released under the [MIT License](LICENSE) — free to use, modify, and distribute.

---

<p align="center">
  Built with 🐍 Python &nbsp;·&nbsp; FlyRank AI Internship
</p>
