from dataclasses import dataclass
from datetime import datetime

from src.models.priority import Priority


@dataclass
class Task:
    id: int
    owner_id: int
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    due_date: datetime | None = None
    category: str | None = None
    completed: bool = False
    reminder_at: datetime | None = None
