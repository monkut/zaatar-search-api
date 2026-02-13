"""Web fetch endpoint."""

import logging

import httpx
from flask_openapi3 import APIBlueprint, Tag

from zaatar.clients.fetcher import FetchError, fetch
from zaatar.models import FetchQuery, FetchResponse

logger = logging.getLogger(__name__)

tag = Tag(name="Fetch", description="Web content fetch operations")
fetch_bp = APIBlueprint("fetch", __name__, abp_tags=[tag])


@fetch_bp.get(
    "/web_fetch",
    summary="Fetch web content",
    description="Fetch a URL and extract readable content as markdown or text",
    responses={200: FetchResponse},
)
def web_fetch(query: FetchQuery):
    """Fetch a URL, extract content, and return it."""
    try:
        result = fetch(query)
    except FetchError as exc:
        return {"error": str(exc)}, 400
    except httpx.HTTPStatusError as exc:
        logger.exception("Fetch failed")
        return {"error": f"Upstream error: {exc.response.status_code}"}, 502
    except httpx.ConnectError:
        logger.exception("Cannot connect to %s", query.url)
        return {"error": "Cannot connect to target URL"}, 502

    return result.model_dump()
