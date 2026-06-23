# FRED MCP Server

This MCP server exposes the Federal Reserve Bank of St. Louis FRED API through
three tools:

- `fred_search_series`: search for FRED series metadata by text.
- `fred_get_series`: fetch metadata for one FRED series id.
- `fred_get_observations`: fetch observations for one FRED series id.

Observation values are returned as floats. FRED missing-value markers (`"."`)
are returned as `None`, with the original value preserved as `value_raw`.
Results include FRED source metadata, units, observation date strings, and the
sample restrictions passed to the tool.

## Setup

Install dependencies from the repository root:

```bash
python3 -m pip install -r requirements.txt
```

Provide your FRED API key through an environment variable. Do not commit the key
to the repository.

```bash
export FRED_API_KEY="your-local-key"
```

Run the server directly from the repository root:

```bash
PYTHONPATH=agent-harness/mcp/fred/src python3 -m fred_mcp_server
```

## Codex MCP Config

This machine is configured globally in `~/.codex/config.toml` with:

```toml
[mcp_servers.fred]
command = "/Users/antoniomele/Dropbox/github/AC4E_Pavia/.venv/bin/python"
args = ["-m", "fred_mcp_server"]
env_vars = ["FRED_API_KEY"]

[mcp_servers.fred.env]
PYTHONPATH = "/Users/antoniomele/Dropbox/github/AC4E_Pavia/agent-harness/mcp/fred/src"
```

Codex launches this as a local stdio MCP server. MCP stdio uses JSON-RPC
messages over standard input and output. The `env_vars` setting allows Codex to
forward `FRED_API_KEY` from the launching environment without storing the secret
in the config file.

To inspect the registration:

```bash
codex mcp get fred
```

## Data Notes

The server requests JSON from FRED's public web service endpoints:

- `/fred/series/search`
- `/fred/series`
- `/fred/series/observations`

It does not modify raw data files in this repository. The only transformation is
parsing FRED observation values from strings to floats and converting missing
markers to `None`.
