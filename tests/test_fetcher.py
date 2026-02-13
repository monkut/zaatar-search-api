"""Fetcher client unit tests."""

from unittest.mock import patch

import httpx
import pytest

from zaatar.clients.fetcher import FetchError, _extract_content, _validate_url, fetch
from zaatar.models import FetchQuery

SAMPLE_HTML = """
<html>
<head><title>Test Page</title></head>
<body>
<article>
<h1>Hello World</h1>
<p>This is a test paragraph with <a href="https://example.com">a link</a>.</p>
</article>
</body>
</html>
"""


class TestValidateUrl:
    def test_http_allowed(self):
        _validate_url("http://example.com")

    def test_https_allowed(self):
        _validate_url("https://example.com")

    def test_ftp_rejected(self):
        with pytest.raises(FetchError, match="not allowed"):
            _validate_url("ftp://example.com")

    def test_file_rejected(self):
        with pytest.raises(FetchError, match="not allowed"):
            _validate_url("file:///etc/passwd")


class TestExtractContent:
    def test_markdown_mode(self):
        content = _extract_content(SAMPLE_HTML, "markdown")
        assert "Hello World" in content
        assert "test paragraph" in content

    def test_text_mode(self):
        content = _extract_content(SAMPLE_HTML, "text")
        assert "Hello World" in content
        assert "test paragraph" in content


class TestFetch:
    @patch("zaatar.clients.fetcher.httpx.Client")
    def test_fetch_success(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            text=SAMPLE_HTML,
            request=httpx.Request("GET", "https://example.com"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        query = FetchQuery(url="https://example.com")
        result = fetch(query)

        assert result.url == "https://example.com"
        assert result.extract_mode == "markdown"
        assert result.content_length > 0
        assert "Hello World" in result.content

    @patch("zaatar.clients.fetcher.httpx.Client")
    def test_fetch_text_mode(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            text=SAMPLE_HTML,
            request=httpx.Request("GET", "https://example.com"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        query = FetchQuery(url="https://example.com", extractMode="text")
        result = fetch(query)

        assert result.extract_mode == "text"

    @patch("zaatar.clients.fetcher.httpx.Client")
    def test_fetch_max_chars(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            text=SAMPLE_HTML,
            request=httpx.Request("GET", "https://example.com"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        query = FetchQuery(url="https://example.com", maxChars=10)
        result = fetch(query)

        assert result.content_length <= 10

    def test_fetch_invalid_scheme(self):
        query = FetchQuery(url="ftp://example.com")
        with pytest.raises(FetchError, match="not allowed"):
            fetch(query)
