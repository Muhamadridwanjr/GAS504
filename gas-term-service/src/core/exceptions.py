class TerminalError(Exception):
    pass

class QuotaExceededError(TerminalError):
    pass

class RiskValidationError(TerminalError):
    pass
