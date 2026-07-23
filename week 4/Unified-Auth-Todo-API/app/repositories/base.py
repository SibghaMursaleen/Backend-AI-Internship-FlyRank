from abc import ABC, abstractmethod
from typing import List, Optional

class TaskRepository(ABC):
    @abstractmethod
    def get_all(self, done: Optional[bool] = None, search: Optional[str] = None) -> List[dict]:
        """Fetch all tasks, with optional filters."""
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[dict]:
        """Fetch a single task by ID."""
        pass

    @abstractmethod
    def create(self, title: str) -> dict:
        """Create a new task."""
        pass

    @abstractmethod
    def update(self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[dict]:
        """Update an existing task."""
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete an existing task by ID."""
        pass
