"""Pydantic model validation tests."""

import pytest
from pydantic import ValidationError

from zaatar.models import FetchQuery, FetchResponse, SearchQuery, SearchResponse, SearchResult, SearchResultsWeb


class TestSearchQuery:
    def test_minimal_query(self):
        q = SearchQuery(query="python")
        assert q.query == "python"
        assert q.count == 5
        assert q.country is None

    def test_full_query(self):
        q = SearchQuery(
            query="flask api",
            count=3,
            country="US",
            search_lang="en",
            ui_lang="en",
            freshness="pw",
        )
        assert q.count == 3
        assert q.country == "US"
        assert q.freshness == "pw"

    def test_count_bounds(self):
        with pytest.raises(ValidationError):
            SearchQuery(query="test", count=0)

        with pytest.raises(ValidationError):
            SearchQuery(query="test", count=11)

    def test_query_required(self):
        with pytest.raises(ValidationError):
            SearchQuery()


class TestSearchResponse:
    def test_response_structure(self):
        resp = SearchResponse(
            web=SearchResultsWeb(
                results=[
                    SearchResult(title="Test", url="https://example.com", description="A test result"),
                ]
            )
        )
        assert len(resp.web.results) == 1
        assert resp.web.results[0].title == "Test"

    def test_empty_results(self):
        resp = SearchResponse(web=SearchResultsWeb(results=[]))
        assert resp.web.results == []


class TestFetchQuery:
    def test_defaults(self):
        q = FetchQuery(url="https://example.com")
        assert q.extractMode == "markdown"
        assert q.maxChars is None

    def test_custom_values(self):
        q = FetchQuery(url="https://example.com", extractMode="text", maxChars=1000)
        assert q.extractMode == "text"
        assert q.maxChars == 1000


class TestFetchResponse:
    def test_response(self):
        resp = FetchResponse(
            url="https://example.com",
            content="Hello world",
            extract_mode="markdown",
            content_length=11,
        )
        assert resp.content_length == 11
