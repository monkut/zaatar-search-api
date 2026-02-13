"""Entry point: uv run python -m zaatar."""

from zaatar.app import create_app
from zaatar.settings import FLASK_HOST, FLASK_PORT

app = create_app()

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
