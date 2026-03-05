"""Custom exceptions for gas-screener-service."""


class ScreenerError(Exception):
    pass


class EngineUnavailableError(ScreenerError):
    pass


class ValidationError(ScreenerError):
    pass
