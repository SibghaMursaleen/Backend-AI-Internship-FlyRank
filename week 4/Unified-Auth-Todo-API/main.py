from fastapi import FastAPI, Depends, status, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from typing import List, Optional
from app.models.task import TaskResponse, TaskCreate, TaskUpdate
from app.repositories.base import TaskRepository
from app.repositories.in_memory import InMemoryTaskRepository
from app.repositories.postgres import PostgresTaskRepository
from app.repositories.sqlite import SQLiteTaskRepository
from app.config import REPOSITORY_TYPE, DATABASE_URL, SQLITE_DB_PATH, REDIS_HOST, REDIS_PORT, SUPABASE_URL, SUPABASE_KEY
import redis
from supabase import create_client, Client

supabase_client: Client = None
if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "your_supabase_url":
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

from pydantic import BaseModel

class AuthRequest(BaseModel):
    email: str
    password: str

app = FastAPI(
    title="Unified Task Management API",
    version="1.0",
    description="A unified RESTful Todo API supporting In-Memory, SQLite, and PostgreSQL database backends, complete with Redis caching. Developed by Sibgha Mursaleen during the FlyRank AI Internship."
)

@app.on_event("startup")
def startup_event():
    print("Server running and connected to Supabase")


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

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# Instantiate repository as a singleton to persist state
repository_instance: TaskRepository

if REPOSITORY_TYPE == "postgres":
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL must be set when REPOSITORY_TYPE is 'postgres'")
    repository_instance = PostgresTaskRepository(DATABASE_URL)
elif REPOSITORY_TYPE == "sqlite":
    repository_instance = SQLiteTaskRepository(database_path=SQLITE_DB_PATH)
else:
    repository_instance = InMemoryTaskRepository()

def get_repository() -> TaskRepository:
    return repository_instance

security = HTTPBearer(auto_error=False)

def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required"
        )
    
    token = credentials.credentials
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not initialized"
        )
    
    try:
        user_response = supabase_client.auth.get_user(token)
        return {
            "user": user_response.user,
            "token": token
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

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

@app.get("/redis-ping")
def ping_redis():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=2)
        if r.ping():
            return {
                "redis_status": "connected",
                "message": "PONG"
            }
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"redis_status": "disconnected", "error": "Redis ping failed"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"redis_status": "disconnected", "error": str(e)}
        )

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

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(auth_data: AuthRequest):
    if not auth_data.email or not auth_data.password:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required and cannot be empty"}
        )
    if not auth_data.email.strip() or not auth_data.password.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required and cannot be empty"}
        )
    
    if not supabase_client:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Supabase client not initialized"}
        )
    
    try:
        response = supabase_client.auth.sign_up({
            "email": auth_data.email,
            "password": auth_data.password
        })
        if not response.user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Signup failed"}
            )
        return response.user
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.post("/auth/login")
def login(auth_data: AuthRequest):
    if not auth_data.email or not auth_data.password:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required and cannot be empty"}
        )
    if not auth_data.email.strip() or not auth_data.password.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required and cannot be empty"}
        )
    
    if not supabase_client:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Supabase client not initialized"}
        )
    
    try:
        response = supabase_client.auth.sign_in_with_password({
            "email": auth_data.email,
            "password": auth_data.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": response.user
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid login credentials"}
        )

@app.get("/public/info")
def public_info():
    return { "message": "Welcome stranger! This info is public." }

@app.get("/protected/profile")
def protected_profile(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

@app.get("/protected/dashboard")
def protected_dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Welcome to the protected dashboard!",
        "user_id": current_user["user"].id
    }

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: dict = Depends(get_current_user)):
    if not supabase_client:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Supabase client not initialized"}
        )
    
    try:
        supabase_client.auth.set_session(current_user["token"], refresh_token="")
        supabase_client.auth.sign_out()
    except Exception:
        pass
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)



