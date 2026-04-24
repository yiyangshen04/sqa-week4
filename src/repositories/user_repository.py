from typing import Protocol

from src.models.user import User


class UserRepository(Protocol):
    def add(self, user: User) -> User:
        ...

    def get_by_username(self, username: str) -> User | None:
        ...

    def next_id(self) -> int:
        ...


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._by_username: dict[str, User] = {}
        self._next_id = 1

    def next_id(self) -> int:
        value = self._next_id
        self._next_id += 1
        return value

    def add(self, user: User) -> User:
        self._by_username[user.username] = user
        return user

    def get_by_username(self, username: str) -> User | None:
        return self._by_username.get(username)
