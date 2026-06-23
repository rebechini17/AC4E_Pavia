"""Small FRED API client used by the MCP tools.

The client requests JSON from the official FRED web service, preserves FRED
metadata, and converts numeric observation values to floats. Missing FRED
observation values are published as "." and are converted to None while the raw
string is retained as value_raw.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

FRED_BASE_URL = "https://api.stlouisfed.org"
FRED_SOURCE_NAME = "FRED"
DEFAULT_OBSERVATION_LIMIT = 100000


class FredApiError(RuntimeError):
    """Raised when FRED returns an error response or request execution fails."""


def load_api_key(env_var: str = "FRED_API_KEY") -> str:
    """Load the FRED API key from an environment variable."""
    api_key = os.getenv(env_var, "").strip()
    if not api_key:
        raise ValueError(f"{env_var} must be set before starting the FRED MCP server.")
    return api_key


def parse_fred_value(value: object) -> float | None:
    """Convert a FRED observation value to a float, preserving missing values as None."""
    if value is None:
        return None

    text_value = str(value).strip()
    if text_value in {"", "."}:
        return None

    return float(text_value)


def _require_text(value: str, name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} must not be empty.")
    return normalized


def _require_positive_limit(value: int, name: str, maximum: int | None = None) -> int:
    if value < 1:
        raise ValueError(f"{name} must be at least 1.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be at most {maximum}.")
    return value


def _without_none(params: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in params.items() if value is not None}


class FredClient:
    """HTTP client for the FRED API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = FRED_BASE_URL,
        timeout: float = 20.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("FRED_API_KEY must not be empty.")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = http_client or httpx.Client(timeout=timeout)
        self._owns_client = http_client is None

    @classmethod
    def from_environment(cls) -> "FredClient":
        """Create a client using FRED_API_KEY from the environment."""
        return cls(api_key=load_api_key())

    def close(self) -> None:
        """Close the underlying HTTP client if this instance created it."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "FredClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def search_series(self, search_text: str, limit: int = 10) -> dict[str, Any]:
        """Search FRED series metadata by text."""
        search_text = _require_text(search_text, "search_text")
        limit = _require_positive_limit(limit, "limit", maximum=1000)
        payload = self._get(
            "/fred/series/search",
            {
                "search_text": search_text,
                "limit": limit,
            },
        )
        series = payload.get("seriess", [])
        return {
            "count": payload.get("count", len(series)),
            "series": series,
        }

    def get_series(self, series_id: str) -> dict[str, Any]:
        """Get metadata for a single FRED series id."""
        series_id = _require_text(series_id, "series_id")
        payload = self._get("/fred/series", {"series_id": series_id})
        series = payload.get("seriess", [])
        if not series:
            raise FredApiError(f"No FRED series found for series_id={series_id}.")
        return series[0]

    def get_observations(
        self,
        series_id: str,
        observation_start: str | None = None,
        observation_end: str | None = None,
        units: str = "lin",
        limit: int = DEFAULT_OBSERVATION_LIMIT,
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """Get observations for a FRED series.

        Data transformation: FRED's string values are parsed as floats, and "."
        missing-value markers are returned as None with the original value_raw.
        """
        series_id = _require_text(series_id, "series_id")
        units = _require_text(units, "units")
        limit = _require_positive_limit(limit, "limit", maximum=DEFAULT_OBSERVATION_LIMIT)
        if sort_order not in {"asc", "desc"}:
            raise ValueError("sort_order must be 'asc' or 'desc'.")

        payload = self._get(
            "/fred/series/observations",
            _without_none(
                {
                    "series_id": series_id,
                    "observation_start": observation_start,
                    "observation_end": observation_end,
                    "units": units,
                    "limit": limit,
                    "sort_order": sort_order,
                }
            ),
        )
        observations = [self._normalize_observation(item) for item in payload.get("observations", [])]

        return {
            "series_id": series_id,
            "source": FRED_SOURCE_NAME,
            "count": payload.get("count", len(observations)),
            "units": payload.get("units", units),
            "observation_start": payload.get("observation_start", observation_start),
            "observation_end": payload.get("observation_end", observation_end),
            "sort_order": sort_order,
            "observations": observations,
        }

    def _get(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        request_params = {
            "api_key": self.api_key,
            "file_type": "json",
            **params,
        }
        try:
            response = self._client.get(
                f"{self.base_url}{endpoint}",
                params=request_params,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise FredApiError(f"FRED request failed: {exc.__class__.__name__}") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {}

        if not response.is_success:
            message = (
                payload.get("error_message")
                or payload.get("message")
                or f"HTTP {response.status_code}"
            )
            raise FredApiError(f"FRED API error {response.status_code}: {message}")

        return payload

    @staticmethod
    def _normalize_observation(observation: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(observation)
        raw_value = normalized.get("value")
        normalized["value_raw"] = raw_value
        normalized["value"] = parse_fred_value(raw_value)
        return normalized
