class AlertEngineException(Exception):
    """Base exception for gas-alert-engine."""
    pass

class AlertNotFoundException(AlertEngineException):
    """Raised when an alert is not found."""
    pass

class AlertEvaluationError(AlertEngineException):
    """Raised on condition evaluation failure."""
    pass

class InvalidConditionError(AlertEngineException):
    """Raised when a condition structure is invalid."""
    pass
