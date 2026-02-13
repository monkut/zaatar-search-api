"""URL fetch + readability extraction + html2text conversion."""

import logging
from urllib.parse import urlparse

import html2text
import httpx
from readability import Document

from zaatar.definitions import ALLOWED_SCHEMES
from zaatar.models import FetchQuery, FetchResponse
from zaatar.settings import FETCH_MAX_CHARS, FETCH_TIMEOUT

logger = logging.getLogger(__name__)


class FetchError(Exception):
    """Raised when URL fetching or extraction fails."""


def _validate_url(url: str) -> None:
    """Validate that the URL uses an allowed scheme."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        msg = f"URL scheme '{parsed.scheme}' not allowed. Use http or https."
        raise FetchError(msg)


def _extract_content(html: str, extract_mode: str) -> str:
    """Extract readable content from HTML."""
    doc = Document(html)
    readable_html = doc.summary()

    converter = html2text.HTML2Text()
    if extract_mode == "text":
        converter.ignore_links = True
        converter.ignore_images = True
        converter.ignore_emphasis = True

    return converter.handle(readable_html).strip()


def fetch(query: FetchQuery) -> FetchResponse:
    """Fetch a URL, extract readable content, and return the response."""
    _validate_url(query.url)

    max_chars = query.maxChars if query.maxChars is not None else FETCH_MAX_CHARS

    logger.debug(f"Fetching URL: {query.url} mode={query.extractMode} max_chars={max_chars}")

    with httpx.Client(timeout=FETCH_TIMEOUT, follow_redirects=True) as client:
        response = client.get(query.url)
        response.raise_for_status()

    content = _extract_content(response.text, query.extractMode)

    if max_chars > 0:
        content = content[:max_chars]

    return FetchResponse(
        url=query.url,
        content=content,
        extract_mode=query.extractMode,
        content_length=len(content),
    )
