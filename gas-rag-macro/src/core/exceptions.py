"""
Custom exceptions for gas-rag-macro.
"""


class MacroServiceError(Exception):
    """Base exception for gas-rag-macro."""


class ProviderError(MacroServiceError):
    """Raised when an AI provider call fails."""


class FetcherError(MacroServiceError):
    """Raised when fetching news or calendar data fails."""


class VectorStoreError(MacroServiceError):
    """Raised when vector database operations fail."""


class CacheError(MacroServiceError):
    """Raised when Redis cache operations fail."""
