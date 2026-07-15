import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REPOSITORY_TYPE = os.getenv("REPOSITORY_TYPE", "in-memory")  # Default to in-memory
