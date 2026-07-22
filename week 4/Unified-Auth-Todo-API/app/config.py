import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REPOSITORY_TYPE = os.getenv("REPOSITORY_TYPE", "in-memory")  # Default to in-memory
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "tasks.db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


