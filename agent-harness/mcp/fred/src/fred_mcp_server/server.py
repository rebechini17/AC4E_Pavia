"""FastMCP server exposing FRED data tools."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from .client import FredApiError, FredClient

ClientFactory = Callable[[], FredClient]


def _default_client_factory() -> FredClient:
    return FredClient.from_environment()


def _run_fred_call(client_factory: ClientFactory, operation: Callable[[FredClient], Any]) -> Any:
    client = None
    try:
        client = client_factory()
        return operation(client)
    except (FredApiError, ValueError) as exc:
        raise ToolError(str(exc)) from exc
    finally:
        if client is not None:
            close = getattr(client, "close", None)
            if callable(close):
                close()


def register_fred_tools(
    mcp: FastMCP,
    client_factory: ClientFactory = _default_client_factory,
) -> FastMCP:
    """Register FRED tools on a FastMCP server."""

    @mcp.tool()
    def fred_search_series(search_text: str, limit: int = 10) -> dict[str, Any]:
        """Search FRED series metadata by text.

        Returns FRED series ids, titles, units, frequency, and other metadata
        supplied by the FRED series search endpoint.
        """
        return _run_fred_call(
            client_factory,
            lambda client: client.search_series(search_text=search_text, limit=limit),
        )

    @mcp.tool()
    def fred_get_series(series_id: str) -> dict[str, Any]:
        """Get metadata for one FRED series id."""
        return _run_fred_call(
            client_factory,
            lambda client: client.get_series(series_id=series_id),
        )

    @mcp.tool()
    def fred_get_observations(
        series_id: str,
        observation_start: str | None = None,
        observation_end: str | None = None,
        units: str = "lin",
        limit: int = 100000,
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """Get FRED observations for a series.

        Values are parsed from FRED strings to floats. FRED missing-value
        markers "." become None, with the original string retained as value_raw.
        Date fields, vintages, units, and sample restrictions are returned from
        FRED metadata or from the tool arguments.
        """
        return _run_fred_call(
            client_factory,
            lambda client: client.get_observations(
                series_id=series_id,
                observation_start=observation_start,
                observation_end=observation_end,
                units=units,
                limit=limit,
                sort_order=sort_order,
            ),
        )

    return mcp


def create_mcp_server(client_factory: ClientFactory = _default_client_factory) -> FastMCP:
    """Create the FRED FastMCP server."""
    mcp = FastMCP("FRED Database")
    return register_fred_tools(mcp, client_factory=client_factory)


app = create_mcp_server()


def main() -> None:
    """Run the server over MCP stdio."""
    app.run()
