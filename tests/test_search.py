"""/web_search endpoint tests."""

from unittest.mock import patch

import httpx

from zaatar.models import SearchResponse, SearchResult, SearchResultsWeb


class TestWebSearchEndpoint:
    @patch("zaatar.routes.search.search")
    def test_search_success(self, mock_search, client):
        mock_search.return_value = SearchResponse(
            web=SearchResultsWeb(
                results=[
                    SearchResult(title="Test", url="https://example.com", description="A test"),
                ]
            )
        )
        response = client.get("/web_search?query=test&summarize=false")
        assert response.status_code == 200
        data = response.get_json()
        assert "web" in data
        assert len(data["web"]["results"]) == 1
        assert "summary" not in data

    def test_search_missing_query(self, client):
        response = client.get("/web_search")
        assert response.status_code == 422

    @patch("zaatar.routes.search.search")
    def test_search_with_count(self, mock_search, client):
        mock_search.return_value = SearchResponse(web=SearchResultsWeb(results=[]))
        response = client.get("/web_search?query=test&count=3")
        assert response.status_code == 200
        call_args = mock_search.call_args[0][0]
        assert call_args.count == 3

    @patch("zaatar.routes.search.search", side_effect=httpx.ConnectError("connection refused"))
    def test_search_engine_unavailable(self, _mock_search, client):
        response = client.get("/web_search?query=test")
        assert response.status_code == 502
        data = response.get_json()
        assert "error" in data


class TestWebSearchSummarization:
    @patch("zaatar.routes.search.summarize", return_value="A concise summary.")
    @patch("zaatar.routes.search.search")
    def test_search_with_summarize(self, mock_search, mock_summarize, client):
        mock_search.return_value = SearchResponse(
            web=SearchResultsWeb(
                results=[
                    SearchResult(title="Test", url="https://example.com", description="A test result"),
                ]
            )
        )
        response = client.get("/web_search?query=test&summarize=true")
        assert response.status_code == 200
        data = response.get_json()
        assert data["summary"] == "A concise summary."
        mock_summarize.assert_called_once()

    @patch("zaatar.routes.search.summarize")
    @patch("zaatar.routes.search.search")
    def test_search_without_summarize_flag(self, mock_search, mock_summarize, client):
        mock_search.return_value = SearchResponse(
            web=SearchResultsWeb(
                results=[
                    SearchResult(title="Test", url="https://example.com", description="A test"),
                ]
            )
        )
        response = client.get("/web_search?query=test&summarize=false")
        assert response.status_code == 200
        mock_summarize.assert_not_called()

    @patch("zaatar.routes.search.summarize")
    @patch("zaatar.routes.search.search")
    def test_search_summarize_skipped_for_empty_results(self, mock_search, mock_summarize, client):
        mock_search.return_value = SearchResponse(web=SearchResultsWeb(results=[]))
        response = client.get("/web_search?query=test&summarize=true")
        assert response.status_code == 200
        mock_summarize.assert_not_called()

    @patch("zaatar.routes.search.summarize", side_effect=httpx.ConnectError("connection refused"))
    @patch("zaatar.routes.search.search")
    def test_search_summarize_ollama_unavailable(self, mock_search, _mock_summarize, client):
        mock_search.return_value = SearchResponse(
            web=SearchResultsWeb(
                results=[
                    SearchResult(title="Test", url="https://example.com", description="A test"),
                ]
            )
        )
        response = client.get("/web_search?query=test&summarize=true")
        assert response.status_code == 502
        data = response.get_json()
        assert "Summarization service unavailable" in data["error"]
