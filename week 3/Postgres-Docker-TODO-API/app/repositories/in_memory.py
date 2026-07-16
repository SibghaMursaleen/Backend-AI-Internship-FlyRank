from typing import List, Optional
from app.repositories.base import TaskRepository

class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        # Pre-filled with 3 example tasks as requested in Stage 2
        self.tasks = [
            {"id": 1, "title": "Buy groceries", "done": False},
            {"id": 2, "title": "Read a book", "done": True},
            {"id": 3, "title": "Work out", "done": False}
        ]
        self._next_id = 4

    def get_all(self, done: Optional[bool] = None, search: Optional[str] = None) -> List[dict]:
        results = self.tasks
        if done is not None:
            results = [t for t in results if t["done"] == done]
        if search is not None:
            search_lower = search.lower()
            results = [t for t in results if search_lower in t["title"].lower()]
        return results

    def get_by_id(self, task_id: int) -> Optional[dict]:
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def create(self, title: str) -> dict:
        task = {
            "id": self._next_id,
            "title": title,
            "done": False
        }
        self.tasks.append(task)
        self._next_id += 1
        return task

    def update(self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[dict]:
        task = self.get_by_id(task_id)
        if not task:
            return None
        if title is not None:
            task["title"] = title
        if done is not None:
            task["done"] = done
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if not task:
            return False
        self.tasks.remove(task)
        return True
