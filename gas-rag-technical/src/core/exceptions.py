"""Custom exceptions for gas-rag-technical."""


class RagTechnicalError(Exception):
    """Base exception for this service."""


class ProviderError(RagTechnicalError):
    """Raised when an AI provider call fails."""


class VectorStoreError(RagTechnicalError):
    """Raised when vector database operations fail."""


class MarketDataError(RagTechnicalError):
    """Raised when market data retrieval fails."""


class KnowledgeBaseError(RagTechnicalError):
    """Raised when knowledge base operations fail."""


class ConfigurationError(RagTechnicalError):
    """Raised for configuration issues."""
