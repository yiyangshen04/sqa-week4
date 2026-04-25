from datetime import timedelta

from src.models.priority import Priority
from tests.conftest import FIXED_NOW


# equivalence-class: sort key = priority
def test_sort_by_priority_puts_high_before_low(task_service, alice_id):
    # Arrange
    low = task_service.create_task(alice_id, title="low", priority=Priority.LOW)
    high = task_service.create_task(alice_id, title="high", priority=Priority.HIGH)
    mid = task_service.create_task(alice_id, title="mid", priority=Priority.MEDIUM)

    # Act
    result = task_service.sorted_tasks(alice_id, by="priority")

    # Assert
    assert [t.title for t in result] == ["high", "mid", "low"]


def test_sort_by_due_date_puts_earliest_first(task_service, alice_id):
    # Arrange
    later = task_service.create_task(alice_id, title="later", due_date=FIXED_NOW + timedelta(days=5))
    soon = task_service.create_task(alice_id, title="soon", due_date=FIXED_NOW + timedelta(days=1))
    undated = task_service.create_task(alice_id, title="undated")

    # Act
    result = task_service.sorted_tasks(alice_id, by="due_date")

    # Assert
    assert [t.title for t in result] == ["soon", "later", "undated"]


def test_sort_by_completed_puts_incomplete_first(task_service, alice_id):
    # Arrange
    a = task_service.create_task(alice_id, title="a")
    b = task_service.create_task(alice_id, title="b")
    task_service.mark_complete(alice_id, a.id)

    # Act
    result = task_service.sorted_tasks(alice_id, by="completed")

    # Assert
    assert [t.completed for t in result] == [False, True]


# business-logic: filter by category
def test_filter_by_category_returns_only_matching_tasks(task_service, alice_id):
    # Arrange
    task_service.create_task(alice_id, title="hw", category="school")
    task_service.create_task(alice_id, title="milk", category="home")
    task_service.create_task(alice_id, title="paper", category="school")

    # Act
    school = task_service.list_tasks(alice_id, category="school")

    # Assert
    assert sorted(t.title for t in school) == ["hw", "paper"]


# business-logic: filter by completion
def test_filter_by_completed_returns_only_completed_tasks(task_service, alice_id):
    # Arrange
    a = task_service.create_task(alice_id, title="a")
    task_service.create_task(alice_id, title="b")
    task_service.mark_complete(alice_id, a.id)

    # Act
    done_only = task_service.list_tasks(alice_id, completed=True)

    # Assert
    assert [t.title for t in done_only] == ["a"]


# business-logic: search in title and description (case-insensitive)
def test_search_matches_substring_in_title_or_description(task_service, alice_id):
    # Arrange
    task_service.create_task(alice_id, title="Pay RENT", description="landlord venmo")
    task_service.create_task(alice_id, title="call mom", description="ask about rent")
    task_service.create_task(alice_id, title="unrelated", description="nothing here")

    # Act
    hits = task_service.list_tasks(alice_id, search="rent")

    # Assert
    assert sorted(t.title for t in hits) == ["Pay RENT", "call mom"]


# business-logic: cross-user isolation on the list endpoint
def test_list_tasks_does_not_return_other_users_tasks(task_service, alice_id, bob_id):
    # Arrange
    task_service.create_task(alice_id, title="alice-1")
    task_service.create_task(bob_id, title="bob-1")
    task_service.create_task(bob_id, title="bob-2")

    # Act
    for_bob = task_service.list_tasks(bob_id)

    # Assert
    assert sorted(t.title for t in for_bob) == ["bob-1", "bob-2"]
