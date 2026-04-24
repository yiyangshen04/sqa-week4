class TodoError(Exception):
    """Base class for all domain errors raised by the to-do backend."""


class InvalidTaskTitleError(TodoError):
    pass


class InvalidDueDateError(TodoError):
    pass


class InvalidReminderError(TodoError):
    pass


class TaskNotFoundError(TodoError):
    pass


class UnauthorizedTaskAccessError(TodoError):
    pass


class UserAlreadyExistsError(TodoError):
    pass


class InvalidCredentialsError(TodoError):
    pass


class InvalidSortKeyError(TodoError):
    pass
