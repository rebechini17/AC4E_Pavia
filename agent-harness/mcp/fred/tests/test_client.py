import httpx
import pytest

from fred_mcp_server.client import FredApiError, FredClient, load_api_key, parse_fred_value


def make_client(handler):
    return FredClient(
        api_key="test-key",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_search_series_sends_json_request_and_returns_series():
    requests = []

    def handler(request):
        requests.append(request)
        assert request.url.path == "/fred/series/search"
        assert request.url.params["api_key"] == "test-key"
        assert request.url.params["file_type"] == "json"
        assert request.url.params["search_text"] == "unemployment"
        assert request.url.params["limit"] == "2"
        return httpx.Response(
            200,
            json={
                "count": 1,
                "seriess": [
                    {
                        "id": "UNRATE",
                        "title": "Unemployment Rate",
                        "frequency": "Monthly",
                        "units": "Percent",
                    }
                ],
            },
        )

    result = make_client(handler).search_series("unemployment", limit=2)

    assert len(requests) == 1
    assert result == {
        "count": 1,
        "series": [
            {
                "id": "UNRATE",
                "title": "Unemployment Rate",
                "frequency": "Monthly",
                "units": "Percent",
            }
        ],
    }


def test_get_series_returns_first_matching_series():
    def handler(request):
        assert request.url.path == "/fred/series"
        assert request.url.params["series_id"] == "GDP"
        return httpx.Response(
            200,
            json={
                "seriess": [
                    {
                        "id": "GDP",
                        "title": "Gross Domestic Product",
                        "units": "Billions of Dollars",
                    }
                ],
            },
        )

    assert make_client(handler).get_series("GDP") == {
        "id": "GDP",
        "title": "Gross Domestic Product",
        "units": "Billions of Dollars",
    }


def test_get_observations_keeps_source_metadata_and_parses_values():
    def handler(request):
        assert request.url.path == "/fred/series/observations"
        assert request.url.params["series_id"] == "CPIAUCSL"
        assert request.url.params["observation_start"] == "2024-01-01"
        assert request.url.params["units"] == "pc1"
        return httpx.Response(
            200,
            json={
                "count": 2,
                "units": "pc1",
                "observations": [
                    {"date": "2024-01-01", "value": "3.1", "realtime_start": "2024-02-01"},
                    {"date": "2024-02-01", "value": ".", "realtime_start": "2024-03-01"},
                ],
            },
        )

    result = make_client(handler).get_observations(
        "CPIAUCSL",
        observation_start="2024-01-01",
        units="pc1",
        limit=2,
    )

    assert result["series_id"] == "CPIAUCSL"
    assert result["source"] == "FRED"
    assert result["count"] == 2
    assert result["units"] == "pc1"
    assert result["observations"] == [
        {
            "date": "2024-01-01",
            "value": 3.1,
            "value_raw": "3.1",
            "realtime_start": "2024-02-01",
        },
        {
            "date": "2024-02-01",
            "value": None,
            "value_raw": ".",
            "realtime_start": "2024-03-01",
        },
    ]


def test_parse_fred_value_handles_missing_and_numeric_values():
    assert parse_fred_value(".") is None
    assert parse_fred_value("") is None
    assert parse_fred_value("12.5") == 12.5


def test_fred_api_error_includes_fred_message():
    def handler(request):
        return httpx.Response(
            400,
            json={
                "error_code": 400,
                "error_message": "Bad Request. The value for api_key is not registered.",
            },
        )

    with pytest.raises(FredApiError, match="api_key is not registered"):
        make_client(handler).get_series("GDP")


def test_load_api_key_reads_environment_without_default_secret(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "abc123")

    assert load_api_key() == "abc123"


def test_load_api_key_rejects_missing_environment_value(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)

    with pytest.raises(ValueError, match="FRED_API_KEY"):
        load_api_key()


def test_client_rejects_empty_api_key():
    with pytest.raises(ValueError, match="FRED_API_KEY"):
        FredClient(api_key="")
