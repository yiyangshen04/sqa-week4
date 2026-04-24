from datetime import datetime

import pytest

from src.clock import FixedClock
from src.repositories.task_repository import InMemoryTaskRepository
from src.repositories.user_repository import InMemoryUserRepository
from src.services.auth_service import AuthService
from src.services.password_hasher import PlainTextPasswordHasher
from src.services.reminder_service import NoOpReminderService
from src.services.task_service import TaskService

FIXED_NOW = datetime(2026, 4, 23, 12, 0, 0)


@pytest.fixture
def clock():
    return FixedClock(FIXED_NOW)


@pytest.fixture
def task_repo():
    return InMemoryTaskRepository()


@pytest.fixture
def user_repo():
    return InMemoryUserRepository()


@pytest.fixture
def hasher():
    return PlainTextPasswordHasher()


@pytest.fixture
def reminder():
    return NoOpReminderService()


@pytest.fixture
def task_service(task_repo, clock, reminder):
    return TaskService(task_repo, clock, reminder)


@pytest.fixture
def auth_service(user_repo, hasher):
    return AuthService(user_repo, hasher)


@pytest.fixture
def alice_id(auth_service):
    return auth_service.register("alice", "pw").id


@pytest.fixture
def bob_id(auth_service):
    return auth_service.register("bob", "pw").id
