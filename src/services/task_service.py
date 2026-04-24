from datetime import datetime
from typing import Any, Literal

from src.clock import Clock
from src.exceptions import (
    InvalidDueDateError,
    InvalidReminderError,
    InvalidSortKeyError,
    InvalidTaskTitleError,
    TaskNotFoundError,
    UnauthorizedTaskAccessError,
)
from src.models.priority import Priority
from src.models.task import Task
from src.repositories.task_repository import TaskRepository
from src.services.reminder_service import ReminderService

MAX_TITLE_LENGTH = 200
SortKey = Literal["priority", "due_date", "completed"]


class TaskService:
    def __init__(
        self,
        tasks: TaskRepository,
        clock: Clock,
        reminder: ReminderService,
    ):
        self._tasks = tasks
        self._clock = clock
        self._reminder = reminder

    def create_task(
        self,
        owner_id: int,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        due_date: datetime | None = None,
        category: str | None = None,
    ) -> Task:
        self._validate_title(title)
        if due_date is not None and due_date < self._clock.now():
            raise InvalidDueDateError("due_date cannot be in the past")
        task = Task(
            id=self._tasks.next_id(),
            owner_id=owner_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category,
        )
        return self._tasks.add(task)

    def get_task(self, owner_id: int, task_id: int) -> Task:
        return self._load_owned(owner_id, task_id)

    def update_task(self, owner_id: int, task_id: int, **fields: Any) -> Task:
        task = self._load_owned(owner_id, task_id)
        if "title" in fields:
            self._validate_title(fields["title"])
            task.title = fields["title"]
        if "description" in fields:
            task.description = fields["description"]
        if "priority" in fields:
            task.priority = fields["priority"]
        if "due_date" in fields:
            new_due = fields["due_date"]
            if new_due is not None and new_due < self._clock.now():
                raise InvalidDueDateError("due_date cannot be in the past")
            task.due_date = new_due
            if task.reminder_at is not None and new_due is not None and task.reminder_at > new_due:
                task.reminder_at = None
        if "category" in fields:
            task.category = fields["category"]
        return self._tasks.update(task)

    def delete_task(self, owner_id: int, task_id: int) -> None:
        self._load_owned(owner_id, task_id)
        self._tasks.delete(task_id)

    def mark_complete(self, owner_id: int, task_id: int) -> Task:
        task = self._load_owned(owner_id, task_id)
        task.completed = True
        return self._tasks.update(task)

    def mark_incomplete(self, owner_id: int, task_id: int) -> Task:
        task = self._load_owned(owner_id, task_id)
        task.completed = False
        return self._tasks.update(task)

    def list_tasks(
        self,
        owner_id: int,
        *,
        category: str | None = None,
        completed: bool | None = None,
        search: str | None = None,
    ) -> list[Task]:
        results = self._tasks.list_for_owner(owner_id)
        if category is not None:
            results = [t for t in results if t.category == category]
        if completed is not None:
            results = [t for t in results if t.completed == completed]
        if search is not None:
            needle = search.lower()
            results = [
                t for t in results
                if needle in t.title.lower() or needle in t.description.lower()
            ]
        return results

    def sorted_tasks(self, owner_id: int, *, by: SortKey) -> list[Task]:
        items = self._tasks.list_for_owner(owner_id)
        if by == "priority":
            return sorted(items, key=lambda t: t.priority, reverse=True)
        if by == "due_date":
            return sorted(
                items,
                key=lambda t: (t.due_date is None, t.due_date or datetime.max),
            )
        if by == "completed":
            return sorted(items, key=lambda t: t.completed)
        raise InvalidSortKeyError(by)

    def set_reminder(self, owner_id: int, task_id: int, at: datetime) -> Task:
        task = self._load_owned(owner_id, task_id)
        if at < self._clock.now():
            raise InvalidReminderError("reminder cannot be in the past")
        if task.due_date is not None and at > task.due_date:
            raise InvalidReminderError("reminder cannot be after due_date")
        task.reminder_at = at
        self._tasks.update(task)
        self._reminder.schedule(task, at)
        return task

    def _load_owned(self, owner_id: int, task_id: int) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        if task.owner_id != owner_id:
            raise UnauthorizedTaskAccessError(task_id)
        return task

    @staticmethod
    def _validate_title(title: str) -> None:
        if not title or not title.strip():
            raise InvalidTaskTitleError("title cannot be empty")
        if len(title) > MAX_TITLE_LENGTH:
            raise InvalidTaskTitleError(
                f"title cannot exceed {MAX_TITLE_LENGTH} characters"
            )
