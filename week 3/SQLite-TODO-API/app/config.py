import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REPOSITORY_TYPE = os.getenv("REPOSITORY_TYPE", "sqlite")  # Default to sqlite
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "tasks.db")
