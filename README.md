# Zaatar Search API

A self-hosted, OpenClaw-compatible web search and content fetch API backed by [SearXNG](https://docs.searxng.org/).

Zaatar provides `web_search` and `web_fetch` endpoints with parameter schemas matching the Brave/Perplexity tools that OpenClaw uses natively, allowing it to serve as a privacy-respecting, API-key-free alternative.

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/guides/install-python/) for dependency management
- Docker & Docker Compose (for SearXNG)
- System packages for lxml (Ubuntu 24.04):

```bash
sudo apt install libxml2-dev libxslt-dev
```

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Start SearXNG
docker compose up -d searxng

# 3. Start the API
uv run poe serve
```

The API is now running at `http://localhost:5000`.

## API Endpoints

### `GET /web_search`

Search the web via SearXNG.

| Parameter     | Type   | Required | Default | Description                                           |
|---------------|--------|----------|---------|-------------------------------------------------------|
| `query`       | string | yes      |         | Search terms                                          |
| `count`       | int    | no       | 5       | Number of results (1-10)                              |
| `country`     | string | no       |         | 2-letter country code                                 |
| `search_lang` | string | no       |         | ISO language code for results                         |
| `ui_lang`     | string | no       |         | ISO language code for UI                              |
| `freshness`   | string | no       |         | `pd` (day), `pw` (week), `pm` (month), `py` (year)   |

```bash
curl "http://localhost:5000/web_search?query=python&count=3"
```

Response:

```json
{
  "web": {
    "results": [
      {
        "title": "Welcome to Python.org",
        "url": "https://www.python.org/",
        "description": "The official home of the Python Programming Language."
      }
    ]
  }
}
```

### `GET /web_fetch`

Fetch a URL and extract readable content.

| Parameter     | Type   | Required | Default    | Description                     |
|---------------|--------|----------|------------|---------------------------------|
| `url`         | string | yes      |            | Target URL (http/https only)    |
| `extractMode` | string | no       | `markdown` | `markdown` or `text`            |
| `maxChars`    | int    | no       | 50000      | Truncation limit                |

```bash
curl "http://localhost:5000/web_fetch?url=https://example.com"
```

Response:

```json
{
  "url": "https://example.com",
  "content": "# Example Domain\n\nThis domain is for use in illustrative examples...",
  "extract_mode": "markdown",
  "content_length": 135
}
```

### `GET /openapi/openapi.json`

Auto-generated OpenAPI 3.1 spec as JSON.

### `GET /openapi/yaml`

Auto-generated OpenAPI 3.1 spec as YAML (`Content-Type: text/yaml`).

### `GET /openapi/`

Interactive Swagger UI documentation.

## OpenClaw Integration

OpenClaw's built-in `web_search` tool supports Brave and Perplexity. Since it does not natively support custom search providers, zaatar operates as a standalone API that you connect via an **OpenClaw plugin**.

### 1. Start zaatar

Run zaatar on the same machine as OpenClaw (or a reachable host):

```bash
# Start SearXNG + API
docker compose up -d searxng
FLASK_HOST=127.0.0.1 FLASK_PORT=5000 uv run poe serve
```

### 2. Create an OpenClaw plugin

Create a plugin directory and register `web_search` / `web_fetch` as custom agent tools that proxy to zaatar:

```
~/openclaw-plugins/zaatar-search/
  index.js
  package.json
```

`index.js`:

```js
export default function (api) {
  api.registerTool("web_search", {
    description: "Search the web using Zaatar (SearXNG)",
    parameters: {
      query: { type: "string", required: true },
      count: { type: "number", default: 5 },
      country: { type: "string" },
      search_lang: { type: "string" },
      freshness: { type: "string" },
    },
    async execute({ query, count, country, search_lang, freshness }) {
      const params = new URLSearchParams({ query });
      if (count) params.set("count", count);
      if (country) params.set("country", country);
      if (search_lang) params.set("search_lang", search_lang);
      if (freshness) params.set("freshness", freshness);

      const res = await fetch(
        `http://127.0.0.1:5000/web_search?${params}`
      );
      return await res.json();
    },
  });

  api.registerTool("web_fetch", {
    description: "Fetch and extract content from a URL using Zaatar",
    parameters: {
      url: { type: "string", required: true },
      extractMode: { type: "string", default: "markdown" },
      maxChars: { type: "number" },
    },
    async execute({ url, extractMode, maxChars }) {
      const params = new URLSearchParams({ url });
      if (extractMode) params.set("extractMode", extractMode);
      if (maxChars) params.set("maxChars", maxChars);

      const res = await fetch(
        `http://127.0.0.1:5000/web_fetch?${params}`
      );
      return await res.json();
    },
  });
}
```

### 3. Install and enable the plugin

```bash
openclaw plugins install -l ~/openclaw-plugins/zaatar-search
```

Add to `~/.openclaw/openclaw.json`:

```json5
{
  plugins: {
    enabled: true,
    allow: ["zaatar-search"],
    entries: {
      "zaatar-search": { enabled: true }
    }
  },
  // Disable built-in search to avoid conflicts
  tools: {
    web: {
      search: { enabled: false },
      fetch: { enabled: false }
    }
  }
}
```

## Environment Variables

| Variable              | Default                | Description                          |
|-----------------------|------------------------|--------------------------------------|
| `SEARXNG_BASE_URL`    | `http://localhost:8080` | SearXNG instance URL                |
| `SEARXNG_ENGINES`     | `""` (all)             | Comma-separated engine filter        |
| `SEARXNG_SAFESEARCH`  | `0`                    | SafeSearch level (0/1/2)             |
| `DEFAULT_SEARCH_COUNT`| `5`                    | Default result count                 |
| `MAX_SEARCH_COUNT`    | `10`                   | Maximum results cap                  |
| `FETCH_TIMEOUT`       | `30`                   | HTTP fetch timeout (seconds)         |
| `FETCH_MAX_CHARS`     | `50000`                | Default max content chars            |
| `FLASK_HOST`          | `0.0.0.0`              | API bind host                        |
| `FLASK_PORT`          | `5000`                 | API bind port                        |
| `LOG_LEVEL`           | `DEBUG`                | Logging level                        |

## Development

### Install dependencies

```bash
pre-commit install
uv sync
```

### Run checks

```bash
uv run poe check       # ruff linter
uv run poe format      # ruff formatter
uv run poe typecheck   # pyright
uv run poe test        # pytest
```

### Project structure

```
zaatar/
    __init__.py
    __main__.py          # Entry point
    app.py               # Flask app factory
    definitions.py       # Constants and mappings
    functions.py         # Utility functions
    models.py            # Pydantic request/response models
    settings.py          # Environment variable configuration
    clients/
        searxng.py       # SearXNG HTTP client
        fetcher.py       # URL fetch + readability extraction
    routes/
        search.py        # GET /web_search
        fetch.py         # GET /web_fetch
tests/
docker-compose.yml
data/searxng/settings.yml
```

## License

MIT
