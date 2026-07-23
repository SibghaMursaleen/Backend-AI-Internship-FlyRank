import sqlite3
from typing import List, Optional
from app.repositories.base import TaskRepository

class SQLiteTaskRepository(TaskRepository):
    def __init__(self, database_path: str):
        self.database_path = database_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn:
                # Create tasks table if it does not exist
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT 0
                    )
                """)
                
                # Insert seed tasks if table is empty
                cursor = conn.execute("SELECT COUNT(*) as count FROM tasks")
                row = cursor.fetchone()
                if row['count'] == 0:
                    conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy groceries", 0))
                    conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Read a book", 1))
                    conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Work out", 0))
        finally:
            conn.close()

    def get_all(self, done: Optional[bool] = None, search: Optional[str] = None) -> List[dict]:
        conn = self._get_connection()
        try:
            query = "SELECT id, title, done FROM tasks WHERE 1=1"
            params = []
            if done is not None:
                query += " AND done = ?"
                params.append(1 if done else 0)
            if search is not None:
                query += " AND title LIKE ?"
                params.append(f"%{search}%")
            query += " ORDER BY id ASC"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]
        finally:
            conn.close()

    def get_by_id(self, task_id: int) -> Optional[dict]:
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
            return None
        finally:
            conn.close()

    def create(self, title: str) -> dict:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (title,))
                task_id = cursor.lastrowid
            return self.get_by_id(task_id)
        finally:
            conn.close()

    def update(self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[dict]:
        conn = self._get_connection()
        try:
            # Check if task exists
            cursor = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
            if not cursor.fetchone():
                return None
            
            updates = []
            params = []
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            if done is not None:
                updates.append("done = ?")
                params.append(1 if done else 0)
            
            if updates:
                query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
                params.append(task_id)
                with conn:
                    conn.execute(query, params)
            
            return self.get_by_id(task_id)
        finally:
            conn.close()

    def delete(self, task_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
            if not cursor.fetchone():
                return False
            with conn:
                conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return True
        finally:
            conn.close()
