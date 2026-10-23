# Frontier Tuning console

Local Streamlit UI for the installed stable 1.x CLI. It uses your existing CLI
and Azure CLI identities; there are no API keys, direct service API calls, or
credential-entry fields. Do not expose this app to a network: anyone with access
can act using the server process's signed-in identity.

## Start

From the repository root, in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r ui\requirements.txt
.\.venv\Scripts\python.exe -m streamlit run ui\app.py --server.address 127.0.0.1
```

Open the localhost URL printed by Streamlit. Sign in with `frontier-tuning auth
login` and `az login` in a terminal beforehand. The CLI must be on PATH. SQL
connectivity/firewall prerequisites remain those in [operations](../docs/05-operations.md).

## What it does

| Surface | Behaviour |
| --- | --- |
| Live skill & rubrics | Reads the CLI-configured environment, enabled skills, instructions, attached rubric checklists and selected model. Cached for 60 seconds; refresh explicitly after changing configuration. |
| Execute | Simple, TreeSearch or BestOfN; query and model controls; optional explicit cutoff/N; exact command preview and paid-action approval. |
| Saved runs & results | Submit once, refresh by execution ID, reopen existing executions, render Markdown answers, scores, usage and tool records; collapsible JSON in a fixed-height scroll pane with exact stdout download. |
| Accuracy | Runs the existing local ground-truth scorer on a completed Contoso claim. A rubric score is never labelled factual accuracy; an unchecked run says so. |
| Claim database | Read baseline, save an action snapshot, or explicitly snapshot/reset and verify `0 0 0 0`. No automatic reset, re-seed or networking changes. |

Only the Contoso warranty environment can submit or operate the database:
`598fd1b0-36f1-402f-ba36-aa00c8a67cc4`. Other environment IDs can be inspected
and existing executions read, but the SQL scripts are not generic.

The inspected skill is **not** forcibly selected for execution. The service
routes the query. Historical returned skill metadata and rubric snapshots are
shown separately from the current live configuration. Local stage directories
are not platform selections.

Execution output uses `-o json-legacy` to retain historical skill/rubric snapshots
that the simplified JSON formatter can omit. It is still JSON. The response
within that envelope is rendered as Markdown. Missing effective defaults, branch
scores, stop reasons and timings remain missing; the UI does not invent them.
TreeSearch defaults to an **explicit 0.95** cutoff in the form, and BestOfN to
**explicit N=4**; uncheck the respective option to omit it and use an unknown
service default. These are UI defaults, not measured optimal settings.

## Safety and saved evidence

- All CLI arguments are passed as an argument list with `shell=False`, not
  interpolated into a shell command.
- Submission checks local unresolved attempts, all returned executions,
  evaluation jobs and tuning jobs, then the actual SQL baseline. Unknown job
  statuses block operations. Large/truncated job lists fail closed.
- A submission intent is saved **before** invoking the CLI. No submission,
  cancellation or reset is retried automatically. A timeout may leave a job
  running; use history to attach its recovered ID or explicitly record evidence
  that no execution was created.
- History, original commands, pre-run configuration, exact CLI output, SQL
  snapshots and scorer reports live under `.local/frontier-console/`, already
  excluded by the repository's `.gitignore`. Keep all prompts/data synthetic.
- Reset saves its snapshot first, checks jobs again, resets using the existing
  script, then verifies the baseline. A local exclusive lock coordinates UI
  sessions/processes sharing this history folder. It cannot lock out external
  CLI users: arrange exclusive use of the shared environment/database.
- An uncertain reset blocks further writes until you inspect the database,
  confirm no SQL action remains active, and record reconciliation evidence.
- If the process crashes with `operation.lock` left behind, first reconcile
  service activity; only then remove that specific lock file manually.
- UI trials are not climb stages. For a controlled comparison, follow the stage
  documentation, held-out sample and one-variable rules in [AGENTS.md](../AGENTS.md).
  Platform errors still need recording in [platform issues](../docs/06-platform-issues.md).

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest ui.test_console
```

Tests mock all service writes and database operations. Streamlit AppTest covers
the strategy controls, execution approval gate, formatted response and raw JSON.
