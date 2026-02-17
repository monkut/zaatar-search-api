"""Entry point: uv run python -m zaatar."""

import logging

from zaatar.app import create_app
from zaatar.clients.ollama import pull_model
from zaatar.settings import FLASK_HOST, FLASK_PORT, OLLAMA_MODEL

logger = logging.getLogger(__name__)

app = create_app()

if __name__ == "__main__":
    logger.info(f"Ensuring Ollama model '{OLLAMA_MODEL}' is available ...")
    pull_model()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
