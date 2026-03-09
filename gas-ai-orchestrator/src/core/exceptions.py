class OrchestratorException(Exception):
    """Base exception class for orchestrator errors."""
    pass

class ModelNotFoundError(OrchestratorException):
    """Raised when a requested model type is not found."""
    pass

class GenerationError(OrchestratorException):
    """Raised when the model fails to generate a response."""
    pass
