from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from app.models.task import TaskResponse
from app.repositories.base import TaskRepository
from app.repositories.in_memory import InMemoryTaskRepository
from app.config import REPOSITORY_TYPE

app = FastAPI(title="Task API", version="1.0")

# Instantiate repository as a singleton to persist in-memory state
repository_instance: TaskRepository

if REPOSITORY_TYPE == "postgres":
    # Postgres setup will be imported here in Stage 6
    # For now fallback to in-memory for safety
    repository_instance = InMemoryTaskRepository()
else:
    repository_instance = InMemoryTaskRepository()

def get_repository() -> TaskRepository:
    return repository_instance

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def read_health():
    return {
        "status": "ok"
    }

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None,
    repo: TaskRepository = Depends(get_repository)
):
    return repo.get_all(done=done, search=search)

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    repo: TaskRepository = Depends(get_repository)
):
    task = repo.get_by_id(task_id)
    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"}
        )
    return task


