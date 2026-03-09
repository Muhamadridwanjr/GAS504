class JournalServiceError(Exception):
    pass

class TradeNotFoundError(JournalServiceError):
    pass

class AnalysisNotFoundError(JournalServiceError):
    pass

class UnauthorizedError(JournalServiceError):
    pass
