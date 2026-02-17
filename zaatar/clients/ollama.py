"""Ollama LLM client for search result summarization."""

import logging

import httpx

from zaatar.settings import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

SUMMARIZE_SYSTEM_PROMPT = (
    "You are a search summarization assistant. "
    "Given a user's search query and a list of search results (title, URL, description), "
    "synthesize a concise, accurate summary that answers the query. "
    "Cite relevant URLs inline using markdown links. "
    "Do not invent information beyond what the search results provide."
)


def _is_model_available(model: str) -> bool:
    """Check if a model is already available locally in Ollama."""
    url = f"{OLLAMA_BASE_URL}/api/tags"
    with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
        response = client.get(url)
        response.raise_for_status()
        data = response.json()

    local_models: list[str] = [m.get("model", "") for m in data.get("models", [])]
    return model in local_models


def pull_model(model: str = OLLAMA_MODEL) -> None:
    """Pull (download) the configured model from Ollama if not already available."""
    if _is_model_available(model):
        logger.info(f"Ollama model '{model}' is already available.")
        return

    url = f"{OLLAMA_BASE_URL}/api/pull"
    payload = {"model": model, "stream": False}

    logger.info(f"Pulling Ollama model '{model}' from {OLLAMA_BASE_URL} ...")

    # Model pulls can download several GB; use a generous timeout
    with httpx.Client(timeout=600) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()

    logger.info(f"Ollama model '{model}' is ready.")


def summarize(query: str, results: list[dict[str, str]], model: str = OLLAMA_MODEL) -> str:
    """Summarize search results using the configured Ollama model."""
    formatted_results = "\n".join(f"- [{r['title']}]({r['url']}): {r['description']}" for r in results)

    prompt = (
        f"Search query: {query}\n\n"
        f"Search results:\n{formatted_results}\n\n"
        "Provide a concise summary answering the query based on these results."
    )

    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": SUMMARIZE_SYSTEM_PROMPT,
        "stream": False,
    }

    logger.debug(f"Requesting Ollama summarization with model '{model}'")

    with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    return data.get("response", "").strip()
