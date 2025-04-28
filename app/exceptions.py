class WineAppError(Exception):
    """Base class for wine app errors"""
    pass

class GoogleSearchApiError(WineAppError):
    """Raised when Google Search API fails"""
    pass

class GeminiApiError(WineAppError):
    """Raised when Gemini API fails"""
    pass