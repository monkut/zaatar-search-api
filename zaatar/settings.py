import os

# SearXNG
SEARXNG_BASE_URL: str = os.getenv("SEARXNG_BASE_URL", "http://localhost:8080")
SEARXNG_ENGINES: str = os.getenv("SEARXNG_ENGINES", "")
SEARXNG_SAFESEARCH: int = int(os.getenv("SEARXNG_SAFESEARCH", "0"))

# Search defaults
DEFAULT_SEARCH_COUNT: int = int(os.getenv("DEFAULT_SEARCH_COUNT", "5"))
MAX_SEARCH_COUNT: int = int(os.getenv("MAX_SEARCH_COUNT", "10"))

# Fetch
FETCH_TIMEOUT: int = int(os.getenv("FETCH_TIMEOUT", "30"))
FETCH_MAX_CHARS: int = int(os.getenv("FETCH_MAX_CHARS", "50000"))

# Flask
FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")  # noqa: S104
FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
