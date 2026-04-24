from datetime import timedelta
from unittest.mock import Mock

import pytest

from src.exceptions import InvalidReminderError
from src.models.priority import Priority
from src.services.task_service import TaskService
from tests.conftest import FIXED_NOW


class RecordingReminderService:
    """Spy: hand-rolled recorder. Every schedule() call is appended
    to self.calls so the test can inspect the interaction history."""

    def __init__(self):
        self.calls = []

    def schedule(self, task, at):
        self.calls.append((task.id, at))


# business-logic — uses a Mock to verify the outgoing call
def test_set_reminder_calls_the_reminder_service_with_task_and_time(task_repo, clock, alice_id):
    # Arrange
    reminder_mock = Mock()
    svc = TaskService(task_repo, clock, reminder_mock)
    due = FIXED_NOW + timedelta(days=2)
    t = svc.create_task(alice_id, title="ping me", due_date=due)
    when = FIXED_NOW + timedelta(hours=5)

    # Act
    svc.set_reminder(alice_id, t.id, when)

    # Assert
    reminder_mock.schedule.assert_called_once()
    called_task, called_when = reminder_mock.schedule.call_args.args
    assert called_task.id == t.id
    assert called_when == when


# business-logic — uses a Spy to inspect the history of calls
def test_set_reminder_is_recorded_on_the_spy(task_repo, clock, alice_id):
    # Arrange
    spy = RecordingReminderService()
    svc = TaskService(task_repo, clock, spy)
    due = FIXED_NOW + timedelta(days=3)
    t = svc.create_task(alice_id, title="A", due_date=due)
    when = FIXED_NOW + timedelta(hours=1)

    # Act
    svc.set_reminder(alice_id, t.id, when)

    # Assert
    assert spy.calls == [(t.id, when)]


# exception-handling
def test_set_reminder_in_the_past_raises(task_service, alice_id):
    # Arrange
    t = task_service.create_task(alice_id, title="x")
    past = FIXED_NOW - timedelta(hours=1)

    # Act / Assert
    with pytest.raises(InvalidReminderError):
        task_service.set_reminder(alice_id, t.id, past)


# equivalence-class / demonstrates Dummy
def test_sorted_tasks_works_with_a_dummy_reminder_service(task_repo, clock, alice_id):
    # Arrange
    dummy_reminder = object()   # placeholder — sorted_tasks never touches reminder
    svc = TaskService(task_repo, clock, dummy_reminder)
    svc.create_task(alice_id, title="low one", priority=Priority.LOW)
    svc.create_task(alice_id, title="big one", priority=Priority.HIGH)

    # Act
    result = svc.sorted_tasks(alice_id, by="priority")

    # Assert
    assert [t.title for t in result] == ["big one", "low one"]
