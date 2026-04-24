from datetime import datetime
from typing import Protocol

from src.models.task import Task


class ReminderService(Protocol):
    def schedule(self, task: Task, at: datetime) -> None:
        ...


class NoOpReminderService:
    def schedule(self, task: Task, at: datetime) -> None:
        return None
