class MT5ConnectionError(Exception):
    """Raised when the connection to MT5 fails"""
    pass

class DataFetchError(Exception):
    """Raised when failing to fetch data from MT5 or Cache"""
    pass
