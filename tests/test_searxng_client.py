"""SearXNG client unit tests."""

from unittest.mock import patch

import httpx

from zaatar.clients.searxng import _build_searxng_params, search
from zaatar.models import SearchQuery


class TestBuildSearxngParams:
    def test_minimal_params(self):
        query = SearchQuery(query="python")
        params = _build_searxng_params(query)
        assert params["q"] == "python"
        assert params["format"] == "json"
        assert "language" not in params
        assert "time_range" not in params

    def test_with_language(self):
        query = SearchQuery(query="test", search_lang="en")
        params = _build_searxng_params(query)
        assert params["language"] == "en"

    def test_with_freshness(self):
        query = SearchQuery(query="test", freshness="pd")
        params = _build_searxng_params(query)
        assert params["time_range"] == "day"

    def test_unknown_freshness_ignored(self):
        query = SearchQuery(query="test", freshness="unknown")
        params = _build_searxng_params(query)
        assert "time_range" not in params

    @patch("zaatar.clients.searxng.SEARXNG_ENGINES", "google,duckduckgo")
    def test_with_engines(self):
        query = SearchQuery(query="test")
        params = _build_searxng_params(query)
        assert params["engines"] == "google,duckduckgo"


class TestSearch:
    @patch("zaatar.clients.searxng.httpx.Client")
    def test_search_success(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={
                "results": [
                    {"title": "Python", "url": "https://python.org", "content": "Python programming language"},
                    {"title": "Flask", "url": "https://flask.palletsprojects.com", "content": "Flask framework"},
                ]
            },
            request=httpx.Request("GET", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        query = SearchQuery(query="python", count=2)
        result = search(query)

        assert len(result.web.results) == 2
        assert result.web.results[0].title == "Python"
        assert result.web.results[0].description == "Python programming language"

    @patch("zaatar.clients.searxng.httpx.Client")
    def test_search_limits_count(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={
                "results": [
                    {"title": f"Result {i}", "url": f"https://example.com/{i}", "content": f"Content {i}"}
                    for i in range(10)
                ]
            },
            request=httpx.Request("GET", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        query = SearchQuery(query="test", count=3)
        result = search(query)

        assert len(result.web.results) == 3

    @patch("zaatar.clients.searxng.httpx.Client")
    def test_search_empty_results(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={"results": []},
            request=httpx.Request("GET", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        query = SearchQuery(query="nonexistent")
        result = search(query)

        assert result.web.results == []
