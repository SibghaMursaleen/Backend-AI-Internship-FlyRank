from fastapi import FastAPI, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Optional
from app.models.task import TaskResponse, TaskCreate, TaskUpdate
from app.repositories.base import TaskRepository
from app.repositories.in_memory import InMemoryTaskRepository
from app.config import REPOSITORY_TYPE

app = FastAPI(title="Task API", version="1.0", description="Task CRUD API made by Sibgha Mursaleen")

# Custom exception handler to return 400 Bad Request with JSON error on validation failure
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = "Invalid input"
    if errors:
        for err in errors:
            loc = err.get("loc", [])
            msg = err.get("msg", "")
            field = loc[-1] if loc else ""
            if field == "title":
                error_msg = "Title is required and cannot be empty"
                break
        else:
            error_msg = f"Validation error on field '{errors[0].get('loc', [''])[0]}': {errors[0].get('msg')}"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": error_msg}
    )

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
        "made_by": "Sibgha Mursaleen",
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

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    repo: TaskRepository = Depends(get_repository)
):
    # Reject whitespace-only title
    if not task_in.title.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required and cannot be empty"}
        )
    return repo.create(title=task_in.title.strip())

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    repo: TaskRepository = Depends(get_repository)
):
    # Reject whitespace-only title if provided
    if task_in.title is not None and not task_in.title.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required and cannot be empty"}
        )
    
    # We update title (stripped if provided) and done (if provided)
    title_to_update = task_in.title.strip() if task_in.title is not None else None
    updated_task = repo.update(task_id=task_id, title=title_to_update, done=task_in.done)
    
    if not updated_task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"}
        )
    return updated_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    repo: TaskRepository = Depends(get_repository)
):
    success = repo.delete(task_id)
    if not success:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"}
        )
    return





