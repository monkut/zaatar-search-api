"""Flask app factory and OpenAPI YAML route."""

import logging

import yaml
from flask import Response
from flask_openapi3 import Info, OpenAPI

from zaatar import __version__
from zaatar.routes.fetch import fetch_bp
from zaatar.routes.search import search_bp

logger = logging.getLogger(__name__)


def create_app() -> OpenAPI:
    """Create and configure the Flask OpenAPI application."""
    info = Info(
        title="Zaatar Search API",
        version=__version__,
        description="OpenClaw-compatible web search and fetch API backed by SearXNG",
    )
    app = OpenAPI(
        __name__,
        info=info,
        doc_prefix="/openapi",
    )

    app.register_api(search_bp)
    app.register_api(fetch_bp)

    @app.get("/openapi/yaml", doc_ui=False)
    def openapi_yaml() -> Response:
        """Return the OpenAPI spec as YAML."""
        spec = app.api_doc
        yaml_content = yaml.dump(spec, default_flow_style=False, sort_keys=False)
        return Response(yaml_content, mimetype="text/yaml")

    return app
