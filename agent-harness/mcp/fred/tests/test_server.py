import pytest

from fred_mcp_server.client import FredApiError
from fred_mcp_server.server import register_fred_tools


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(function):
            self.tools[function.__name__] = function
            return function

        return decorator


class StubClient:
    def search_series(self, search_text, limit):
        return {"series": [{"id": "UNRATE", "title": search_text}], "limit": limit}

    def get_series(self, series_id):
        return {"id": series_id, "title": "Gross Domestic Product"}

    def get_observations(
        self,
        series_id,
        observation_start=None,
        observation_end=None,
        units="lin",
        limit=100000,
        sort_order="asc",
    ):
        return {
            "series_id": series_id,
            "observation_start": observation_start,
            "observation_end": observation_end,
            "units": units,
            "limit": limit,
            "sort_order": sort_order,
            "observations": [{"date": "2024-01-01", "value": 1.2}],
        }


def test_register_fred_tools_exposes_expected_mcp_tool_names():
    fake_mcp = FakeMCP()

    register_fred_tools(fake_mcp, client_factory=StubClient)

    assert set(fake_mcp.tools) == {
        "fred_search_series",
        "fred_get_series",
        "fred_get_observations",
    }


def test_registered_tools_call_fred_client():
    fake_mcp = FakeMCP()
    register_fred_tools(fake_mcp, client_factory=StubClient)

    assert fake_mcp.tools["fred_search_series"]("unemployment", limit=3) == {
        "series": [{"id": "UNRATE", "title": "unemployment"}],
        "limit": 3,
    }
    assert fake_mcp.tools["fred_get_series"]("GDP")["id"] == "GDP"
    observations = fake_mcp.tools["fred_get_observations"](
        "CPIAUCSL",
        observation_start="2024-01-01",
        units="pc1",
        limit=12,
        sort_order="desc",
    )
    assert observations["series_id"] == "CPIAUCSL"
    assert observations["observation_start"] == "2024-01-01"
    assert observations["units"] == "pc1"
    assert observations["limit"] == 12
    assert observations["sort_order"] == "desc"


def test_registered_tools_convert_fred_errors_to_tool_errors():
    class FailingClient:
        def search_series(self, search_text, limit):
            raise FredApiError("FRED rejected the request")

    fake_mcp = FakeMCP()
    register_fred_tools(fake_mcp, client_factory=FailingClient)

    with pytest.raises(Exception, match="FRED rejected the request"):
        fake_mcp.tools["fred_search_series"]("bad")
