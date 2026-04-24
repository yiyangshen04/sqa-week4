from datetime import timedelta

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
    created = task_service.create_task(alice_id, title="Old", category="old-cat")

    # Act
    updated = task_service.update_task(
        alice_id, created.id, title="New title", category="home"
    )

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
    created = task_service.create_task(alice_id, title="To do")

    # Act
    completed = task_service.mark_complete(alice_id, created.id)

    # Assert
    assert completed.completed is True


def test_list_tasks_returns_every_task_owned_by_the_user(task_service, alice_id):
    # Arrange
    task_service.create_task(alice_id, title="A")
    task_service.create_task(alice_id, title="B")

    # Act
    tasks = task_service.list_tasks(alice_id)

    # Assert
    assert sorted(t.title for t in tasks) == ["A", "B"]
