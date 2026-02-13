"""/web_fetch endpoint tests."""

from unittest.mock import patch

import httpx

from zaatar.clients.fetcher import FetchError
from zaatar.models import FetchResponse


class TestWebFetchEndpoint:
    @patch("zaatar.routes.fetch.fetch")
    def test_fetch_success(self, mock_fetch, client):
        mock_fetch.return_value = FetchResponse(
            url="https://example.com",
            content="Hello world",
            extract_mode="markdown",
            content_length=11,
        )
        response = client.get("/web_fetch?url=https://example.com")
        assert response.status_code == 200
        data = response.get_json()
        assert data["url"] == "https://example.com"
        assert data["content"] == "Hello world"
        assert data["content_length"] == 11

    def test_fetch_missing_url(self, client):
        response = client.get("/web_fetch")
        assert response.status_code == 422

    @patch("zaatar.routes.fetch.fetch", side_effect=FetchError("URL scheme 'ftp' not allowed"))
    def test_fetch_invalid_scheme(self, _mock_fetch, client):
        response = client.get("/web_fetch?url=ftp://example.com")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    @patch("zaatar.routes.fetch.fetch", side_effect=httpx.ConnectError("connection refused"))
    def test_fetch_connection_error(self, _mock_fetch, client):
        response = client.get("/web_fetch?url=https://example.com")
        assert response.status_code == 502
        data = response.get_json()
        assert "error" in data
