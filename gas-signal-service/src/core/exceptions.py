class SignalServiceError(Exception):
    pass

class UnauthorizedTierError(SignalServiceError):
    pass

class SignalNotFoundError(SignalServiceError):
    pass
