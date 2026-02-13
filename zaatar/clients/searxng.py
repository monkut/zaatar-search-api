"""SearXNG HTTP client with parameter mapping."""

import logging
from typing import Any

import httpx

from zaatar.definitions import FRESHNESS_TO_TIME_RANGE
from zaatar.models import SearchQuery, SearchResponse, SearchResult, SearchResultsWeb
from zaatar.settings import FETCH_TIMEOUT, SEARXNG_BASE_URL, SEARXNG_ENGINES, SEARXNG_SAFESEARCH

logger = logging.getLogger(__name__)


def _build_searxng_params(query: SearchQuery) -> dict[str, Any]:
    """Build SearXNG query parameters from a SearchQuery model."""
    params: dict[str, Any] = {
        "q": query.query,
        "format": "json",
        "safesearch": SEARXNG_SAFESEARCH,
    }

    if SEARXNG_ENGINES:
        params["engines"] = SEARXNG_ENGINES

    if query.search_lang:
        params["language"] = query.search_lang

    if query.freshness:
        time_range = FRESHNESS_TO_TIME_RANGE.get(query.freshness)
        if time_range:
            params["time_range"] = time_range

    return params


def search(query: SearchQuery) -> SearchResponse:
    """Execute a search against SearXNG and return normalized results."""
    params = _build_searxng_params(query)
    url = f"{SEARXNG_BASE_URL}/search"

    logger.debug(f"SearXNG request: {url} params={params}")

    with httpx.Client(timeout=FETCH_TIMEOUT) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    raw_results: list[dict[str, Any]] = data.get("results", [])
    results = [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            description=r.get("content", ""),
        )
        for r in raw_results[: query.count]
    ]

    return SearchResponse(web=SearchResultsWeb(results=results))
