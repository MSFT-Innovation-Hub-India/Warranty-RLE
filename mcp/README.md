# Contoso service claim system — MCP server

The agent's connection to the structured half of the world. Nine read tools and
three draft-only action tools over MCP streamable HTTP, built to deploy to Azure
Container Apps and register with `frontier-tuning tools create`.

Everything it serves is synthetic.

---

## Why this exists

The warranty rules live in documents. The *facts a claim turns on* do not:

| Fact | Where it has to live | Why not a document |
| --- | --- | --- |
| When a machine was commissioned | `Assets` | Master data, one row per machine, changes on commissioning |
| How many hours it has run | `AssetTelemetry` | A time series — 3,000 rows and growing |
| What was actually fitted last time | `ServiceHistory` | Transactional, and it contradicts the claim often enough to matter |
| Whether a partner gets a handling uplift | `Dealers` | Operational master data, mirrors the contract |
| Who can approve what | `GoodwillAuthority` | Config that changes without reissuing policy |

An agent that never calls this server cannot produce a correct payable amount.
That is the point: the join is not optional, so it becomes gradeable.

---

## Layout

```text
scenario/mcp/
├── contoso_service_mcp/
│   ├── db.py       SQLite locally, Azure SQL in Azure - one portable surface
│   ├── tools.py    the twelve tools as pure functions - no MCP, no network
│   ├── auth.py     Entra ID bearer validation, off when unconfigured
│   └── server.py   FastMCP wiring + /healthz, the only MCP-aware file
├── tests/test_tools.py    37 checks - tools against the seeded DB, plus T-SQL translation
├── Dockerfile             python:3.12-slim + ODBC Driver 18, non-root, healthcheck
├── requirements.txt
└── deploy/azure.md        end-to-end Container Apps + Azure SQL deployment
```

`tools.py` deliberately has no MCP dependency. The behaviour can be tested
without an MCP client, which is why the test suite runs in the repo's existing
`.venv`.

---

## The tools

### Read

| Tool | Returns | Carries |
| --- | --- | --- |
| `get_asset` | Registry record, incl. commissioning date | Flags a missing commissioning record and cites policy 2.3 |
| `get_running_hours` | Latest reading at or before a date | Reports absence rather than returning zero |
| `get_service_history` | Jobs, most recent first | `part_fitted` — the part actually installed |
| `find_prior_claims` | Earlier repairs, optionally by component | The 90-day repair-warranty rule |
| `get_claim` | The claim as submitted | What the partner asked for, which is not the answer |
| `get_dealer` | Partner master | `uplift_pct` — 0% for most, 5% for Northwind |
| `lookup_part` | Part with supersession chain resolved | `current_part_no` and its price |
| `get_tsb_index` | ⚠️ Bulletin index — **deliberately stale** | Its own warning that it is not authoritative |
| `get_goodwill_authority` | Tier and approving role for an amount | That a channel approval is not authority |

### Action — all draft-only

| Tool | Effect |
| --- | --- |
| `create_claim_adjudication` | Writes a draft. Returns "No payment has been made." |
| `request_missing_evidence` | Records the request, sets the claim to **Held** — not declined |
| `escalate_goodwill` | Records a request for authority. Does not grant it |

Nothing in this server pays, sends or notifies. The worst outcome of a wrong
answer is a draft row a human rejects.

---

## The one table that is wrong on purpose

`TsbApplicability` records `TSB-C-0051` as ending at serial **1500**. The
bulletin document says **1850**. Policy clause 1.4 makes the document govern and
the index informational.

`get_tsb_index` says so in its own description and returns an
`authority_warning` on every call. **The trap is not whether the agent can find
out — it is whether it acts on what it was told**, when a structured tool
returns a clean, confident, wrong answer and the correct one is in a Word file.

That is the single most realistic thing in this world. Every enterprise has a
reporting table that lags the source of truth.

---

## Two dialects, one schema

`scenario/build/gen_db.py` emits both from a single templated DDL:

| File | For |
| --- | --- |
| `schema.sqlite.sql` / `seed.sqlite.sql` | Local development and the test suite |
| `schema.azuresql.sql` / `seed.azuresql.sql` | Azure SQL, T-SQL, with `GO` batches for `sqlcmd` |
| `contoso.db` | Prebuilt SQLite file the tests run against |

Three differences that would otherwise bite, all handled inside `db.py`:

| | SQLite | Azure SQL |
| --- | --- | --- |
| Row limiting | `LIMIT n` | `TOP (n)` — so tool SQL carries **neither**, and the adapter adds the right one |
| Column types | `TEXT` everywhere — SQLite has no date type at all | `NVARCHAR(n)`, **real `DATE`**, `DATETIMEOFFSET(0)`, `DECIMAL` — `TEXT` is deprecated in T-SQL and cannot be indexed |
| Values returned | strings and floats | `datetime.date` and `Decimal` — normalised back to ISO strings and floats |

The third one is the quiet danger: without normalisation, a date comparison that
works locally starts comparing a `date` object against a string in Azure, and
money arrives as `Decimal`, which is not JSON-serialisable. Eight checks in the
test suite cover the translation without needing a SQL Server.

### On dates specifically

The Azure SQL schema uses **real `DATE` columns**, not strings. The ISO strings
you see in `out/data/*.json` are an intermediate artefact — JSON has no date
type — and SQLite stores them as `TEXT` because SQLite has no date type either.
Neither is a modelling choice; both are what the format allows.

Two details that matter in T-SQL:

- Dates are seeded as ISO-8601 literals (`'2026-06-18'`). For `DATE`,
  `DATETIME2` and `DATETIMEOFFSET` that form is **language-neutral** — it is
  read identically whatever `SET DATEFORMAT` or `SET LANGUAGE` is in force. The
  legacy `DATETIME` type carries no such guarantee, which is one reason it is
  not used here.
- Audit stamps on the three action tables are `DATETIMEOFFSET(0)`, not
  `DATETIME2`. The tools stamp rows in UTC, and a `DATETIME2` column would have
  silently dropped the `+00:00` — leaving an audit trail that does not record
  which zone it was written in.

## Running locally

```powershell
cd scenario\mcp
..\.venv\Scripts\python.exe tests\test_tools.py     # 37 checks, no network needed
```

To run the server itself you need the `mcp` package, which is not in the repo
`.venv`:

```powershell
python -m venv .venv-mcp
.venv-mcp\Scripts\pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///../out/db/contoso.db"
.venv-mcp\Scripts\python -m contoso_service_mcp.server
# MCP at http://localhost:8000/mcp, health at /healthz
```

## Deploying

See [deploy/azure.md](deploy/azure.md). In outline: build and push to ACR,
create a Container App with external ingress, point
`AZURE_SQL_CONNECTION_STRING` at Azure SQL Database, register an Entra app for
the audience, then
`frontier-tuning tools create --url https://<app>/mcp --auth-scheme AzureAD
--aud api://<app-id>`.

⚠️ The frontier-tuning runtime calls this endpoint **from the cloud**. It must be
publicly reachable — a private endpoint or VNet-only ingress will not work.
