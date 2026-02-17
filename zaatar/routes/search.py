"""Web search endpoint."""

import logging

import httpx
from flask_openapi3 import APIBlueprint, Tag

from zaatar.clients.ollama import summarize
from zaatar.clients.searxng import search
from zaatar.models import SearchQuery, SearchResponse

logger = logging.getLogger(__name__)

tag = Tag(name="Search", description="Web search operations")
search_bp = APIBlueprint("search", __name__, abp_tags=[tag])


@search_bp.get(
    "/web_search",
    summary="Search the web",
    description="Search the web using SearXNG metasearch engine. Optionally summarize results with a local LLM.",
    responses={200: SearchResponse},
)
def web_search(query: SearchQuery):
    """Execute a web search and return results, optionally summarized."""
    try:
        result = search(query)
    except httpx.HTTPStatusError as exc:
        logger.exception("SearXNG request failed")
        return {"error": f"Search engine error: {exc.response.status_code}"}, 502
    except httpx.ConnectError:
        logger.exception("Cannot connect to SearXNG")
        return {"error": "Search engine unavailable"}, 502

    if query.summarize and result.web.results:
        try:
            results_for_llm = [r.model_dump() for r in result.web.results]
            result.summary = summarize(query.query, results_for_llm)
        except httpx.ConnectError:
            logger.exception("Cannot connect to Ollama")
            return {"error": "Summarization service unavailable"}, 502
        except httpx.HTTPStatusError as exc:
            logger.exception("Ollama request failed")
            return {"error": f"Summarization error: {exc.response.status_code}"}, 502

    return result.model_dump(exclude_none=True)
