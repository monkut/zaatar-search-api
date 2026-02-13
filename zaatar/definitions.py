"""Constants and mappings for zaatar search API."""

# Freshness parameter to SearXNG time_range mapping
FRESHNESS_TO_TIME_RANGE: dict[str, str] = {
    "pd": "day",
    "pw": "week",
    "pm": "month",
    "py": "year",
}

# Allowed URL schemes for web_fetch
ALLOWED_SCHEMES: frozenset[str] = frozenset({"http", "https"})
