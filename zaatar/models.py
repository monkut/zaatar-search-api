"""Pydantic models for request validation and response serialization."""

from typing import Literal

from pydantic import BaseModel, Field

from zaatar.settings import DEFAULT_SEARCH_COUNT, FETCH_MAX_CHARS, MAX_SEARCH_COUNT

# --- Search Models ---


class SearchQuery(BaseModel):
    """Query parameters for web_search endpoint."""

    query: str = Field(..., description="Search terms")
    count: int = Field(
        default=DEFAULT_SEARCH_COUNT,
        ge=1,
        le=MAX_SEARCH_COUNT,
        description="Number of results to return",
    )
    country: str | None = Field(default=None, description="2-letter country code")
    search_lang: str | None = Field(default=None, description="ISO language code for search results")
    ui_lang: str | None = Field(default=None, description="ISO language code for UI")
    freshness: str | None = Field(
        default=None,
        description='Freshness filter: "pd" (past day), "pw" (past week), "pm" (past month), "py" (past year)',
    )


class SearchResult(BaseModel):
    """A single search result."""

    title: str
    url: str
    description: str


class SearchResultsWeb(BaseModel):
    """Container for web search results."""

    results: list[SearchResult]


class SearchResponse(BaseModel):
    """Top-level search response matching Brave API structure."""

    web: SearchResultsWeb


# --- Fetch Models ---


class FetchQuery(BaseModel):
    """Query parameters for web_fetch endpoint."""

    url: str = Field(..., description="URL to fetch (http or https)")
    extractMode: Literal["markdown", "text"] = Field(  # noqa: N815
        default="markdown",
        description='Extraction mode: "markdown" or "text"',
    )
    maxChars: int | None = Field(  # noqa: N815
        default=None,
        description=f"Maximum characters to return (default: {FETCH_MAX_CHARS})",
    )


class FetchResponse(BaseModel):
    """Response from web_fetch endpoint."""

    url: str
    content: str
    extract_mode: str
    content_length: int
