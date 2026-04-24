from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, plain: str) -> str:
        ...

    def verify(self, plain: str, hashed: str) -> bool:
        ...


class PlainTextPasswordHasher:
    """Lightweight stub: the assignment allows non-cryptographic password handling."""

    _PREFIX = "plain:"

    def hash(self, plain: str) -> str:
        return f"{self._PREFIX}{plain}"

    def verify(self, plain: str, hashed: str) -> bool:
        return hashed == f"{self._PREFIX}{plain}"
