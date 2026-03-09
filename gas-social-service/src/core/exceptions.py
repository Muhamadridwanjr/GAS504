from fastapi import HTTPException


class SelfFollowError(HTTPException):
    """Raised when a user tries to follow themselves."""
    def __init__(self):
        super().__init__(status_code=400, detail="You cannot follow yourself.")


class AlreadyFollowingError(HTTPException):
    """Raised when the follow relationship already exists."""
    def __init__(self):
        super().__init__(status_code=409, detail="You are already following this user.")


class NotFollowingError(HTTPException):
    """Raised when trying to unfollow a user not followed."""
    def __init__(self):
        super().__init__(status_code=404, detail="You are not following this user.")


class SignalServiceError(HTTPException):
    """Raised when the signal service call fails."""
    def __init__(self, detail: str = "Signal service unavailable."):
        super().__init__(status_code=502, detail=detail)


class NotificationServiceError(Exception):
    """Raised when the notification service call fails (non-critical)."""
    pass
