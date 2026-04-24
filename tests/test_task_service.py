from datetime import timedelta

import pytest

from src.exceptions import (
    InvalidDueDateError,
    InvalidReminderError,
    InvalidSortKeyError,
    InvalidTaskTitleError,
    TaskNotFoundError,
    UnauthorizedTaskAccessError,
)
from src.models.priority import Priority
from tests.conftest import FIXED_NOW


def test_create_task_stores_all_fields(task_service, alice_id):
    # Arrange
    due = FIXED_NOW + timedelta(days=2)

    # Act
    task = task_service.create_task(
        alice_id,
        title="Write tests",
        description="AAA pattern with explicit sections",
        priority=Priority.HIGH,
        due_date=due,
        category="school",
    )

    # Assert
    assert task.id > 0
    assert task.owner_id == alice_id
    assert task.title == "Write tests"
    assert task.description == "AAA pattern with explicit sections"
    assert task.priority == Priority.HIGH
    assert task.due_date == due
    assert task.category == "school"
    assert task.completed is False


def test_get_task_returns_the_created_task(task_service, alice_id):
    # Arrange
    created = task_service.create_task(alice_id, title="Buy milk")

    # Act
    loaded = task_service.get_task(alice_id, created.id)

    # Assert
    assert loaded.id == created.id
    assert loaded.title == "Buy milk"


def test_update_task_changes_title_and_category(task_service, alice_id):
    # Arrange
    t = task_service.create_task(alice_id, title="Old", category="old-cat")

    # Act
    updated = task_service.update_task(alice_id, t.id, title="New title", category="home")

    # Assert
    assert updated.title == "New title"
    assert updated.category == "home"


def test_delete_task_removes_it_from_the_list(task_service, alice_id):
    # Arrange
    created = task_service.create_task(alice_id, title="Transient")

    # Act
    task_service.delete_task(alice_id, created.id)

    # Assert
    assert task_service.list_tasks(alice_id) == []


def test_mark_complete_flips_the_completed_flag(task_service, alice_id):
    # Arrange
    t = task_service.create_task(alice_id, title="To do")
    # Act
    done = task_service.mark_complete(alice_id, t.id)
    # Assert
    assert done.completed is True


def test_list_tasks_returns_every_task_owned_by_the_user(task_service, alice_id):
    # Arrange
    task_service.create_task(alice_id, title="A")
    task_service.create_task(alice_id, title="B")

    # Act
    tasks = task_service.list_tasks(alice_id)

    # Assert
    assert sorted(t.title for t in tasks) == ["A", "B"]


# invalid-input
def test_create_task_with_empty_title_raises(task_service, alice_id):
    # Arrange
    empty_title = ""

    # Act / Assert
    with pytest.raises(InvalidTaskTitleError):
        task_service.create_task(alice_id, title=empty_title)


# invalid input
def test_create_task_with_whitespace_only_title_raises(task_service, alice_id):
    # Arrange
    whitespace_title = "   \t  "

    # Act / Assert
    with pytest.raises(InvalidTaskTitleError):
        task_service.create_task(alice_id, title=whitespace_title)


# invalid-input
def test_create_task_with_title_over_200_chars_raises(task_service, alice_id):
    # Arrange
    too_long = 'x' * 201

    # Act / Assert
    with pytest.raises(InvalidTaskTitleError):
        task_service.create_task(alice_id, title=too_long)


# invalid-input
def test_create_task_with_past_due_date_raises(task_service, alice_id):
    # Arrange
    yesterday = FIXED_NOW - timedelta(days=1)

    # Act / Assert
    with pytest.raises(InvalidDueDateError):
        task_service.create_task(alice_id, title="x", due_date=yesterday)


# invalid-input
def test_set_reminder_after_due_date_raises(task_service, alice_id):
    # Arrange
    due = FIXED_NOW + timedelta(days=1)
    tsk = task_service.create_task(alice_id, title="x", due_date=due)
    reminder_too_late = due + timedelta(hours=1)

    # Act / Assert
    with pytest.raises(InvalidReminderError):
        task_service.set_reminder(alice_id, tsk.id, reminder_too_late)


# boundary
def test_create_task_with_title_exactly_200_chars_is_accepted(task_service, alice_id):
    # Arrange
    title = "x" * 200

    # Act
    task = task_service.create_task(alice_id, title=title)

    # Assert
    assert len(task.title) == 200
    assert task.title == title


# boundary / edge
def test_create_task_with_due_date_equal_to_now_is_accepted(task_service, alice_id):
    # Arrange
    due = FIXED_NOW

    # Act
    task = task_service.create_task(alice_id, title="x", due_date=due)

    # Assert
    assert task.due_date == FIXED_NOW


# boundary
def test_list_tasks_for_user_with_no_tasks_returns_empty_list(task_service, alice_id):
    # Arrange

    # Act
    tasks = task_service.list_tasks(alice_id)

    # Assert
    assert len(tasks) == 0


# boundary
def test_sort_by_priority_with_a_single_task_returns_just_that_task(task_service, alice_id):
    # Arrange
    only = task_service.create_task(alice_id, title="only one", priority=Priority.MEDIUM)

    # Act
    results = task_service.sorted_tasks(alice_id, by="priority")

    # Assert
    assert results == [only]


# exception-handling
def test_get_task_with_unknown_id_raises_not_found(task_service, alice_id):
    # Arrange
    missing_id = 99999

    # Act / Assert
    with pytest.raises(TaskNotFoundError):
        task_service.get_task(alice_id, missing_id)


# exception-handling (also business logic: cross-user isolation)
def test_get_another_users_task_raises_unauthorized(task_service, alice_id, bob_id):
    # Arrange
    alice_task = task_service.create_task(alice_id, title="Alice's private task")

    # Act / Assert
    with pytest.raises(UnauthorizedTaskAccessError):
        task_service.get_task(bob_id, alice_task.id)


# exception-handling (also biz logic)
def test_delete_another_users_task_raises_unauthorized(task_service, alice_id, bob_id):
    # Arrange
    alice_task = task_service.create_task(alice_id, title="Alice's")

    # Act / Assert
    with pytest.raises(UnauthorizedTaskAccessError):
        task_service.delete_task(bob_id, alice_task.id)


# exception-handling
def test_sorted_tasks_with_unknown_sort_key_raises(task_service, alice_id):
    # Arrange
    task_service.create_task(alice_id, title="anything")

    # Act / Assert
    with pytest.raises(InvalidSortKeyError):
        task_service.sorted_tasks(alice_id, by="not-a-real-key")
