import pytest

from src.exceptions import InvalidCredentialsError, UserAlreadyExistsError


def test_login_with_correct_password_returns_the_registered_user(auth_service):
    # Arrange
    registered = auth_service.register("alice", "pw")

    # Act
    logged_in = auth_service.login("alice", "pw")

    # Assert
    assert logged_in.id == registered.id
    assert logged_in.username == "alice"


# exception-handling
def test_registering_the_same_username_twice_raises(auth_service):
    # Arrange
    auth_service.register("alice", "pw")

    # Act / Assert
    with pytest.raises(UserAlreadyExistsError):
        auth_service.register("alice", "another-pw")


# invalid-input
def test_login_with_wrong_password_raises(auth_service):
    # Arrange
    auth_service.register("alice", "correct")

    # Act / Assert
    with pytest.raises(InvalidCredentialsError):
        auth_service.login("alice", "wrong")


# exception-handling
def test_login_with_unknown_username_raises(auth_service):
    # Act / Assert
    with pytest.raises(InvalidCredentialsError):
        auth_service.login("ghost", "anything")
