from typing import Protocol

from src.models.task import Task


class TaskRepository(Protocol):
    def add(self, task: Task) -> Task:
        ...

    def get(self, task_id: int) -> Task | None:
        ...

    def list_for_owner(self, owner_id: int) -> list[Task]:
        ...

    def update(self, task: Task) -> Task:
        ...

    def delete(self, task_id: int) -> None:
        ...

    def next_id(self) -> int:
        ...


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def next_id(self) -> int:
        value = self._next_id
        self._next_id += 1
        return value

    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def list_for_owner(self, owner_id: int) -> list[Task]:
        return [t for t in self._tasks.values() if t.owner_id == owner_id]

    def update(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> None:
        self._tasks.pop(task_id, None)
