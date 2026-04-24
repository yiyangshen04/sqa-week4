def test_login_with_correct_password_returns_the_registered_user(auth_service):
    # Arrange
    registered = auth_service.register("alice", "pw")

    # Act
    logged_in = auth_service.login("alice", "pw")

    # Assert
    assert logged_in.id == registered.id
    assert logged_in.username == "alice"
