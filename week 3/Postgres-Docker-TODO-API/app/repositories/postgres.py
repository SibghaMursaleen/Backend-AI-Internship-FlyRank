import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from app.repositories.base import TaskRepository

class PostgresTaskRepository(TaskRepository):
    def __init__(self, database_url: str):
        self.database_url = database_url

    def _get_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)

    def get_all(self, done: Optional[bool] = None, search: Optional[str] = None) -> List[dict]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                query = "SELECT id, title, done FROM tasks WHERE 1=1"
                params = []
                if done is not None:
                    query += " AND done = %s"
                    params.append(done)
                if search is not None:
                    query += " AND title ILIKE %s"
                    params.append(f"%{search}%")
                query += " ORDER BY id ASC"
                cur.execute(query, params)
                rows = cur.fetchall()
                return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_by_id(self, task_id: int) -> Optional[dict]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()

    def create(self, title: str) -> dict:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
                    (title, False)
                )
                row = cur.fetchone()
                conn.commit()
                return dict(row)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update(self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[dict]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # First check if exists
                cur.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
                if not cur.fetchone():
                    return None
                
                updates = []
                params = []
                if title is not None:
                    updates.append("title = %s")
                    params.append(title)
                if done is not None:
                    updates.append("done = %s")
                    params.append(done)
                
                if not updates:
                    # Nothing to update, return the current row
                    cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
                    return dict(cur.fetchone())
                
                query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s RETURNING id, title, done"
                params.append(task_id)
                cur.execute(query, params)
                row = cur.fetchone()
                conn.commit()
                return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete(self, task_id: int) -> bool:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # First check if exists
                cur.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
                if not cur.fetchone():
                    return False
                
                cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
