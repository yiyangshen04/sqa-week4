from src.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.password_hasher import PasswordHasher


class AuthService:
    def __init__(self, users: UserRepository, hasher: PasswordHasher):
        self._users = users
        self._hasher = hasher

    def register(self, username: str, password: str) -> User:
        if self._users.get_by_username(username) is not None:
            raise UserAlreadyExistsError(username)
        user = User(
            id=self._users.next_id(),
            username=username,
            password_hash=self._hasher.hash(password),
        )
        return self._users.add(user)

    def login(self, username: str, password: str) -> User:
        user = self._users.get_by_username(username)
        if user is None or not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError(username)
        return user
