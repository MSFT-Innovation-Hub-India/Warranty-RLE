# Frontier Tuning CLI — Command Reference

Command surface of **CLI 0.3.11**, captured from `--help` on the installed
binary. Companion to guides/01-contract-renewal.md.

> Installed help takes precedence over upstream docs — they disagree in places.
> Verify with `--help` before copying a command from anywhere, including here.
> Note 0.3.12 was advertised as available during this run but was not installed.

---

## Contents

- [Mental model](#mental-model)
- [Global options](#global-options)
- [Top-level commands](#top-level-commands)
- [Auth and connectivity](#auth-and-connectivity)
- [`environments`](#environments)
- [`knowledge`](#knowledge)
- [`skills`](#skills)
- [`rubrics`](#rubrics)
- [`samples`](#samples)
- [`run` / `chat`](#run--chat)
- [`executions`](#executions)
- [`models`](#models)
- [`evaluate`](#evaluate)
- [`tune`](#tune)
- [`rle-quality`](#rle-quality)
- [`health`](#health)
- [`tools`](#tools)
- [Other commands](#other-commands)
- [File formats](#file-formats)
- [Known traps](#known-traps)

---

## Mental model

Objects nest like this:

```
Environment (world / workspace)          ← addressed by GUID, --env-id
├── Capabilities   OneDriveAndSharePoint, TeamsMessages, Meetings, GraphConnectors
│                  (frozen at init — no update command)
├── Knowledge      resolved source references derived from capabilities
├── Tools          MCP servers / connectors (built-in + custom)
├── Skills         task definitions
│   └── Rubrics    grading criteria, snapshotted into samples at upload
├── Samples        prompts, typed Evaluation / Training / untyped
├── Executions     one record per agent run
├── Evaluations    scored jobs over samples
└── Tuning jobs    whole-workspace fine-tuning
```

Everything lives server-side. The CLI is a thin HTTP client.

---

## Global options

Accepted at any command level; deeper levels override shallower ones.

| Option | Meaning |
| --- | --- |
| `-e, --env-id TEXT` | Environment/workspace ID. Required by most commands. Also `FRONTIER_TUNING_ENV_ID` |
| `-o, --output [json\|table]` | Output format. Default `table`. **Use `json` for anything you need to parse** |
| `-v, --verbose` | Verbose/debug logging |
| `-c, --config-file PATH` | Config file path. Also `FRONTIER_TUNING_CONFIG`. A non-existent path is treated as empty config and created on first write — handy for seeding a per-tenant/CI config |
| `-p, --profile TEXT` | Activate a config profile, overriding `active_profile` |
| `--mock` | Run against the local mock server (no Azure creds). Start it with `frontier-tuning-mock`. Unrelated to `tools mocks` |
| `--local` | Hit a locally-running KServing instance (default `http://localhost:8080/api/v1.0`). Requires a server-side flight |
| `-H, --header NAME:VALUE` | Extra HTTP header on every request, repeatable, curl-style |
| `--version` / `--help` | — |

**Precedence:** command flag → `FRONTIER_TUNING_*` env var → active profile → config file → built-in default.

Built-in defaults when nothing is configured:

```text
base_url: https://substrate.office.com/KnowledgeGraph/api/v1.0
scopes:   https://substrate.office.com/knowledgegraph/.default
```

---

## Top-level commands

| Command | Purpose |
| --- | --- |
| `chat` | Alias for `run` |
| `check` | Is the current token valid |
| `completion` | Shell completion setup |
| `config` | Manage CLI configuration and profiles |
| `environments` | Manage environments |
| `evaluate` | Start and monitor evaluation jobs |
| `health` | Workspace health metrics and LLM insights |
| `knowledge` | Manage grounding sources |
| `login` | Interactive MSAL sign-in; also initializes the configured environment |
| `logout` | Clear cached tokens |
| `models` | List base models for this workspace |
| `pad` | Import a Power Automate Desktop recording |
| `ping` | Connectivity, auth status, API latency |
| `publish` | Publish the world to a channel (e.g. M365 agent) |
| `refresh` | Silent MSAL token refresh |
| `rle-quality` | Score environment quality and check readiness |
| `rubrics` | Manage a skill's rubrics |
| `run` | Send a query; the agent resolves and invokes a skill |
| `samples` | Manage samples |
| `serve` | Expose the agent as a local MCP server for coding agents |
| `skills` | Manage skills |
| `tools` | Manage MCP servers / connectors |
| `tune` | Start and monitor fine-tuning jobs |
| `update` | Upgrade the CLI |
| `versions` | List, inspect and roll back versioned skills |
| `whoami` | Identity decoded from the current token |

`executions` is not listed in `--help` but works — see [`executions`](#executions).

---

## Auth and connectivity

```powershell
frontier-tuning login
frontier-tuning whoami
frontier-tuning check
frontier-tuning --env-id <env-id> ping --count 1
```

| Command | Returns | Proves |
| --- | --- | --- |
| `login` | `Signed in successfully as <upn>` | Interactive sign-in succeeded. **Also initializes the configured environment** — not purely an auth operation |
| `whoami` | `UPN`, `OID`, `Tenant`, `Expires` | Which identity and when the token dies. **Check `Expires` first when things break** |
| `check` | Token validity + remaining minutes | Token only. Without an env ID: `No env_id set - skipping connectivity probe` |
| `ping` | `✓ Auth`, workspace `McpServers` URL, latency ms | Workspace reachable and MCP servers registered. **Does not prove retrieval works** |

Tokens last roughly an hour. `refresh` attempts a silent renewal without prompting.

---

## `environments`

| Command | Purpose |
| --- | --- |
| `init-md` | Generate a Markdown template for `init --file` |
| `init` | Provision an environment (POST) |
| `get` | Summary: ID, tools, skills |
| `list` | Environments for the current tenant |
| `export` | Export all assets (tools + skills) to JSON |
| `import` | Import tools and skills from a JSON export |
| `access` | Share with people as owners or contributors |
| `mapping` | Manage the ID a workspace/agent ID resolves to |

```powershell
frontier-tuning environments init-md --out-file sample-env.md
frontier-tuning environments init --file env.local.md --agent-id <your-guid> --output json
frontier-tuning environments get --env-id <env-id> --output json
```

**`init` inputs:** `--file` (the `env.md`), optional `--agent-id` (supply your own
GUID so you have the ID saved *before* the call returns).

**`init` output:**

```json
{ "IsWorkspaceReady": true, "DebugContext": { "Logs": [] } }
```

`IsWorkspaceReady` = provisioned and accepting requests. It does **not** mean your
capability URLs resolved or your content is retrievable.

**`get` output** includes a `Tools` array of built-in MCP slots:

```json
{ "Type": "OneDrive", "Name": "OneDrive", "Url": "https://office.com", "Enabled": true }
```

`Url` here is service metadata, not a connectable endpoint. Typical enabled set:
`Me`, `SharePoint`, `OneDrive`, `Teams`. Typical disabled: `Email`, `Word`,
`M365Chat`, `Calendar`, `fabriciq`. **No capability name turns `Email` on** —
there is no email capability.

> **Capability URLs are frozen at `init`.** No `environments update` exists.
> Re-running `init` on an existing agent ID fails with
> `API error (400): {"code":"ER99000"}`. Wrong URL ⇒ provision a new world.

`access` manages environment **membership** (owners/contributors). It does not
grant the runtime access to documents.

---

## `knowledge`

Grounding sources attached to an environment.

| Command | Purpose |
| --- | --- |
| `list` | Sources attached to the environment |
| `get` | One source by ID |
| `add` | Add a source |
| `remove` | Remove a source |
| `set-label` | Set grounding / training / rules labels on a source |
| `remove-label` | Remove all labels from a source |

```powershell
frontier-tuning knowledge list --env-id <env-id> -o json
```

**Output fields:**

| Field | Meaning |
| --- | --- |
| `id`, `url`, `folderUrl` | The registered URL, echoed back |
| `displayName` | The **resolved** name. Matching your real folder is a good sign |
| `type` | `folder`, `file`, `library`, `site`, `subsite`, `teamsMessage` |
| `isAllItemsIncluded` | `false` = scoped to this folder only |
| `webUrl`, `chatType` | Teams sources |
| `sharepointIds.*` | `siteId`, `webId`, `listId`, `uniqueId`, `siteUrl`. **Empty strings suggest the source did not resolve** |
| `createdBy` / `lastModifiedBy` | Registering identity |

> **Registration ≠ retrievability.** A source can be listed here and still return
> nothing, either because it never resolved or because indexing has not caught up.
>
> `add` / `remove` suggest sources may be adjustable after provisioning, despite
> capability URLs being frozen. **Untested here.**

---

## `skills`

| Command | Purpose |
| --- | --- |
| `init-md` | Generate a skill Markdown template |
| `create` | Create a skill (idempotent by name) |
| `get` | Get a skill by ID |
| `list` | All skills in the world |
| `update` | Partial update — omitted flags unchanged |
| `delete` / `delete-all` | Delete skills — **cascades to their samples** |
| `enable` / `disable` | Include/exclude from query routing |
| `enrich` | AI-improve `Name` and `Description` only |
| `generate-rubrics` | Generate rubrics from instructions |
| `rubrics` | List a skill's rubrics |
| `refine` | Start/review skill refinement runs |
| `suggest` | Suggest skills from usage patterns |

```powershell
frontier-tuning skills create --file skills/renewal-notice-check.md --env-id <env-id> --output json
frontier-tuning skills get <skill-id> --env-id <env-id> --show-rubrics --output json
frontier-tuning skills generate-rubrics <skill-id>          # preview only without --apply
```

**Key output fields:**

| Field | Meaning |
| --- | --- |
| `Id` | Skill ID — needed by nearly everything downstream |
| `Prompt` | Your `## Instructions`, verbatim |
| `Rubrics[]` | `Name`, `ChecklistItems`, `MeasurementMethod` (e.g. `binary_checklist`), `Importance`, `Source` (`user_authored` / generated), `RubricType` |
| `Enabled` | Participates in routing |
| `Version` | Increments on update |
| `updatedInPlace` | `true` = overwrote an existing same-name skill |
| `Tools[]` | Skill-scoped tools, e.g. `read_from_storage` |
| `Knowledge[]` | Skill-level knowledge references |
| `BaseSkillDefinition` | e.g. `base` |

> **Do not set `generateRubrics: true` on a file that has hand-written rubrics.**
> Successful generation **replaces** your `## Rubrics`. Hand-written ones survive
> only if generation fails. The `skills init-md` template sets it `true` *and*
> ships example rubrics — following it literally discards your work.
>
> **Duplicate skill names silently break grading** → `OverallScore: null` with no
> per-sample results. `create` is idempotent by name; `--allow-duplicate-name`
> exists only for deliberate duplicates.
>
> **A disabled skill is not an error.** The world falls back to general behaviour
> and answers *worse*. That is what a routing failure looks like from outside.

---

## `rubrics`

| Command | Purpose |
| --- | --- |
| `refine start --skill-id <id>` | Start an async rubric refinement run |
| `refine status <ref-id>` | Poll |
| `refine detail <ref-id>` | Preview the refined set |
| `refine cancel <ref-id>` | Request cancellation |
| `refine apply <ref-id> --skill-id <id>` | **Replace** the skill's rubrics |

---

## `samples`

| Command | Purpose |
| --- | --- |
| `upload` | Bulk upload from JSONL/JSON |
| `create` | Single sample |
| `list` | All samples (shows Type) |
| `get` / `update` / `delete` | Per sample |
| `delete-by-skill` | All samples for a skill |
| `generate` | Start a synthetic prompt generation job |
| `status` / `generation-jobs` / `download` | Manage generation jobs |
| `suggest` | Suggest samples from your M365 work |

```powershell
frontier-tuning samples upload samples/renewal-notice-check.eval.jsonl `
  --skill-id <skill-id> --type Evaluation --env-id <env-id>
```

**`upload` options:**

| Option | Meaning |
| --- | --- |
| `FILE` (positional) | JSONL — each line an object with at least a `Prompt` field. JSON — an array, or `{"Samples":[…]}` |
| `-s, --skill-id` | **Required.** Applied to all samples in the file |
| `-t, --type [evaluation\|training]` | Applied atomically at creation. **Omit and samples are untyped — usable for both** |

Expected output: `Uploaded: N | Failed: 0`.

> **Samples are not deduplicated.** Re-uploading a file adds a second copy of every
> prompt. To add prompts later, upload a file containing only the new lines.
>
> **Samples snapshot the skill's rubrics at upload time.** Edit a rubric afterwards
> and scores will not move — the single most common false alarm. Re-upload.
>
> **Type matters twice.** `evaluate start` considers only `Evaluation`-typed
> samples unless `--include-training-samples`. `tune start` needs ≥ 11 prompts
> usable for training.
>
> `samples create` returns **HTTP 201 with no body** — `None` is not a failure.
> Check the exit code.

---

## `run` / `chat`

```powershell
frontier-tuning chat --query "Which agreements have a notice deadline between 1 October 2026 and 31 December 2026?" `
  --skill-id <skill-id> --conversation-id <guid> `
  --model prod-gpt-54-reasoning --strategy simple --env-id <env-id>
```

| Option | Meaning |
| --- | --- |
| `-q, --query TEXT` | **Required.** The natural-language query |
| `-s, --skill-id TEXT` | Route directly to this skill. Omit to let routing choose |
| `--conversation-id TEXT` | For multi-turn; auto-generated if omitted |
| `-w, --wait` | Poll until the execution completes and show the result |
| `--model TEXT` | Model for this execution. **Repeatable** for a true multi-model run |
| `--strategy [simple\|bestofn\|treesearch]` | Orchestrator strategy. Omit for the service default |
| `--best-of-n INTEGER` | Rollouts for BestOfN. Requires `--strategy BestOfN`, must be > 0 |

**Output without `--wait`:**

```text
Execution ID:    5266c6b5-18ee-48f9-ae4c-9f81eac671f4
Conversation ID: 8a9b0e7e-a06e-4482-ae40-d1f53a721e2e
Status:          Running
```

**Save the Execution ID immediately.** The run continues server-side. Slowness is
never a reason to resubmit — poll the same execution.

This is also the **only reliable check** that capability scoping and indexing
worked. `environments get` and `export` under-report; this probe does not.

---

## `executions`

Not in the top-level `--help` listing, but functional.

| Command | Purpose |
| --- | --- |
| `executions list` | Recent executions |
| `executions get <id>` | Full trajectory |
| `diag execution <id>` | Diagnose an execution |

```powershell
frontier-tuning executions get <execution-id> --env-id <env-id> --output json
```

**Key fields:**

| Field | Meaning |
| --- | --- |
| `Id`, `ConversationId`, `UserQuery` | Identity of the run |
| `Status` | `Running` / `Completed` / … — **`Completed` ≠ correct** |
| `ErrorResponse` | Usually `null` even on failed runs |
| `Skills[]` | Which skill fired, and its status |
| `ToolExecutions[]` | One entry per tool call: `Title`, `Status`, `Inputs[]`, `Output` |
| `Response[]` | Final answer: `Content`, `Link` |
| `LatestChainOfThought` | Reasoning trace; `null` when nothing gradeable was produced |
| `BillingSummary` | Token counts — not surfaced by the CLI's table output |
| `TaskSnapshot` | The task as captured at submission |

**Diagnostic signals:**

| Signal | Meaning |
| --- | --- |
| `"FileRetrievalDetails": []` | Nothing retrieved by that call, even if it reports `Completed` |
| `parentFolderId: root` | Root browsing — the agent is guessing |
| Tool inputs naming unregistered sites | Scoping failed; the agent is inventing paths |
| `"success_count": 0, "failure_count": N` | Per-file failures inside `results`, with no top-level HTTP status |
| `Status: Completed`, `RubricResults: []`, `LatestChainOfThought: null` | No gradeable answer was produced — read the response text first |
| `Sorry — a transient error interrupted that request.` with `Status: Completed` | The run failed but reports success. Check `ToolExecutions` for a non-`Completed` entry |

> **Decode twice.** Tool `Output` is an array of text parts; the useful JSON sits
> inside a part's `text` string. A regex over the raw blob misses it.
>
> **Match on decoded `StatusCode`**, not raw text — a successful response can
> contain `403` inside a GUID.

---

## `models`

```powershell
frontier-tuning models list --env-id <env-id> --output json
```

Returns **two different, non-overlapping lists**:

| Field | Used by | Contained here |
| --- | --- | --- |
| `TrainingModels` | `evaluate start`, `chat --model` | `prod-gpt-54-reasoning` |
| `FTBaseModels` | `tune start` | `gpt-5-2025-08-07`, `gpt-54-mini`, `mai-code-1-flash` |

> Despite the name, **`TrainingModels` is the execution/evaluation list.** Passing a
> tunable base to `evaluate start` fails with `Unknown base model`.
>
> **You cannot baseline the model you are going to tune.** Membership in one list
> does not imply membership in the other.

---

## `evaluate`

| Command | Purpose |
| --- | --- |
| `start` | Start an evaluation job |
| `status <job-id>` | Job status |
| `results <job-id>` | Results of a completed job |
| `list` | Jobs for this workspace |
| `compare` | Two or more jobs side by side |
| `diagnostics <job-id>` | Operational diagnostics |
| `cancel <job-id>` | Cancel |

```powershell
frontier-tuning evaluate start --skill-id <skill-id> --limit 1 `
  --base-model prod-gpt-54-reasoning --strategy simple --env-id <env-id>
```

**`start` options:**

| Option | Meaning |
| --- | --- |
| `-b, --base-model TEXT` | Model to evaluate. **Repeatable** or comma-separated. Omit ⇒ interactive prompt (**will hang a script**) |
| `--sample-id TEXT` | Scope to specific sample IDs. Repeatable |
| `--skill-id TEXT` | Scope to one skill's samples |
| `--limit INTEGER` | Cap sample count, applied *after* the above filters. Must be > 0 |
| `--include-training-samples` | Also evaluate Training-typed samples. Ignored with `--sample-id` |
| `--strategy [simple\|bestofn\|treesearch]` | Harness strategy |
| `--best-of-n INTEGER` | Rollouts for BestOfN |
| `--per-model` | **One job per model** instead of one job with all models as candidates |

**Two multi-model shapes:**

| Shape | Behaviour |
| --- | --- |
| default | ONE job; all models offered to each sample as candidates; the strategy picks per sample. Produces a **single blended score**, not per-model scores |
| `--per-model` | ONE JOB PER MODEL, same samples and scope. Produces **directly comparable** per-model scores and token costs. Feed the job IDs to `evaluate compare` |

> **By default an evaluation is WHOLE-WORKSPACE** — every sample prompt regardless
> of skill. Use `--skill-id` / `--sample-id` / `--limit` to scope. A scope matching
> no samples is rejected server-side.

**Reading results — three traps:**

1. **`results --samples` prints `Score: —` for every row**, even when all scores are
   present. It reads `Execution.RubricResults` (always empty) instead of
   `Execution.Skills[*].RubricResults`. Use the asset's `eval-report.ps1`.
2. **`ConvertFrom-Json` without `-AsHashtable` throws** on the payload — it carries
   both `id` and `Id`.
3. **Check submitted vs graded.** A prompt that fires no skill produces no rubric
   rows, is dropped from the average rather than scored zero, and leaves
   `FailureRate: 0.0`. The tell in the built-in table is `Skill: —` on that row.

```text
Submitted: 6   Graded: 5

WARNING: 1 sample(s) completed but were graded on nothing.
```

> `OverallScore: null` means **broken grading, not a bad answer** — usually
> duplicate skill names or a grader failure.
>
> Timing: six samples took **~55 minutes**, with ~15 minutes in `NotStarted` first.
> Each sample is a full agent run.

---

## `tune`

| Command | Purpose |
| --- | --- |
| `start` | Start a sample-based fine-tuning job |
| `status <job-id>` | Status and readiness for evaluation |
| `list` | Jobs for this workspace |
| `diagnostics <job-id>` | Job diagnostics |
| `cancel <job-id>` | Cancel |
| `delete-deployment` | Delete the deployed model a job produced |

```powershell
frontier-tuning tune start --base-model gpt-54-mini --new-model my-agent-v2 --env-id <env-id>
```

| Option | Meaning |
| --- | --- |
| `-m, --new-model TEXT` | Name for the fine-tuned model; auto-generated if omitted |
| `-b, --base-model TEXT` | Base model ID; skips the interactive prompt. Validated against `FTBaseModels` |
| `-e, --epochs INTEGER` | 1–10. Server default if omitted |

> **`-e` is ambiguous.** It means both `--epochs` and `--env-id`; 0.3.11 warns
> *"The parameter -e is used more than once."* **Always use long options here.**
>
> **No `--skill-id`, no sample filter.** The job snapshots the **entire workspace**
> — every skill, every tool, both sample types. Clean up first. Returned
> `WorkspaceSnapshotMetadata.SamplePromptsCount` reports the full count, evaluation
> samples included. To tune one skill in a multi-skill world, **disable the others**
> — disabled skills are excluded from inference and training.
>
> **≥ 11 usable training prompts required:**
> `API error (400): {"code":"ER07010","message":"The workspace has 8 sample prompt(s) usable for training, but this job requires at least 11."}`
>
> Training can take **days** on fungible capacity. Do not resubmit because it is slow.
> Check `status` for `readyForEvaluation` — training completion alone does not mean
> the model is evaluable.

---

## `rle-quality`

| Command | Purpose |
| --- | --- |
| `check` | Score the environment and print the quality report |
| `start` | Start a quality evaluation without waiting |
| `status <run-id>` | Progress |
| `result <run-id>` | Scored result |

**Not exercised in this run.** Given the description — "score environment quality
and check readiness" — it is the most promising candidate for a programmatic
readiness signal, but what it actually measures is undocumented here. Worth
investigating before relying on the `chat` probe alone.

---

## `health`

| Command | Purpose |
| --- | --- |
| `get` | Aggregated workspace health metrics |
| `compute` | Trigger async health compute (non-blocking) |
| `insights` | Latest stored insight |
| `generate-insights` | Fresh synchronous LLM insight |
| `token-usage` | Workspace token consumption |

`token-usage` is useful for cost tracking. Tokens are not currency without pricing.

---

## `tools`

MCP servers and connectors registered in the environment.

```powershell
frontier-tuning tools create --name erp-connector --description "Purchase orders and inventory" `
  --url <url> --auth-scheme AzureAD --aud <resource-url>
frontier-tuning tools enable <tool-id>
frontier-tuning tools sources
```

> `tools list` shows **callable actions**; `tools sources` shows the **stable server
> ID** accepted by `enable`, `disable`, `delete`, `get`, `status`.

The contract-renewal world needs **no custom tool** — it grounds on first-party
capabilities, which is why it onboards quickly. A custom connector is the natural
next step and is what moves an engagement from ~4–5 weeks per skill toward 12–14.

---

## Other commands

| Command | Notes |
| --- | --- |
| `config show/set/init/profile` | Manage persisted config. `config show` confirms which world you are pointed at |
| `versions` | List, inspect and roll back versioned skills |
| `serve` | Expose the agent as a local MCP server for coding agents |
| `publish --channel m365agent` | Publish the world. Needs Node 18+, `atk` CLI, M365 sign-in. Use `--dry-run` first |
| `pad` | Import a Power Automate Desktop recording |
| `update` / `update --check` / `update --yes` | Upgrade in place. **Windows: close all other terminals using the CLI first** — it replaces the running `.exe` |

---

## File formats

### `env.md`

```markdown
---
name: Vendor Contract Renewal Review
description: Prepares evidence for vendor agreement renewal decisions.
# agentId: <uuid>   # optional — auto-generated if omitted
---

## Instructions

<agent instructions>

## Conversation Starters

- title: Agreements that auto-renew
  text: List every agreement that renews automatically and the notice period each requires.

## Capabilities

- name: OneDriveAndSharePoint
  items_by_url:
    - url: https://contoso.sharepoint.com/sites/VendorManagement/Shared Documents/Contracts
- name: TeamsMessages
  urls:
    - url: https://teams.microsoft.com/l/channel/19%3A…%40thread.skype/vendor-operations
```

Only four capabilities can be grounded against: `OneDriveAndSharePoint`,
`TeamsMessages`, `Meetings`, `GraphConnectors`. Word/Excel/PowerPoint are **files
reached through** `OneDriveAndSharePoint`, not capabilities. URLs with spaces work
raw or percent-encoded.

### `skill.md`

```markdown
---
name: renewal-notice-check
description: <drives routing — which queries select this skill>
generateRubrics: false
---

## Instructions

<becomes the agent's Prompt — do not use '#' characters here, they parse as comments>

## Rubrics

### Deadline coverage
- All in-window agreements listed
- Inclusive boundaries respected

## Knowledge

# - id: SPO_xxxx
#   name: policy.docx
#   type: file
```

`## Instructions` → `Description` / `Prompt` on the wire. `## Rubrics` H3 headings
→ rubric names; bullets → checklist items. Supported knowledge source types:
`file`, `folder`, `library`, `subsite`, `site` for OneDrive and SharePoint.
**Teams messages, calendar and email are not supported knowledge source types.**

### Sample JSONL

One JSON object per line, at least a `Prompt` field:

```json
{"Prompt": "Which agreements have a notice deadline between 1 October 2026 and 31 December 2026?"}
```

---

## Known traps

Consolidated, in rough order of how much time they cost.

| # | Trap |
| --- | --- |
| 1 | **`Status: Completed` does not mean success.** Empty retrieval, hallucinated answers and transient failures all report `Completed` with `ErrorResponse: null` |
| 2 | **Capability URLs are frozen at `init`.** No update command. Wrong URL ⇒ new world |
| 3 | **Registration ≠ retrievability.** `knowledge list` showing your folder proves nothing about whether the agent can read it |
| 4 | **`-e` means both `--epochs` and `--env-id`** on `tune start`. Use long options |
| 5 | **`tune start` snapshots the whole workspace** — no skill or sample filter |
| 6 | **Samples snapshot rubrics at upload time.** Rubric edits need a re-upload |
| 7 | **Samples are not deduplicated.** Re-uploading duplicates every prompt |
| 8 | **`evaluate start` defaults to whole-workspace** and to Evaluation-typed samples only |
| 9 | **Submitted ≠ graded.** Ungraded samples vanish from the mean while `FailureRate` stays `0.0` |
| 10 | **`results --samples` shows `Score: —` for everything.** Per-sample scores live elsewhere |
| 11 | **Duplicate skill names silently break grading** → `OverallScore: null` |
| 12 | **`generateRubrics: true` destroys hand-written rubrics** on successful generation |
| 13 | **Three commands report three different tool counts.** `environments get` says `Tools (0)`; `export` lists 8; the tune snapshot says 2. Read `Enabled` per slot from `export` |
| 14 | **`environments export` reports `Samples: []` and `Evaluations: []`** on a world that has both. Use `samples list` / `evaluate list` |
| 15 | **Windows silently reuses the device account.** `login --interactive` to choose another, then verify with `whoami` |
| 16 | **Windows cannot `update` while the CLI is running** in another terminal |
| 17 | **Tokens expire in ~1 hour.** Check `whoami` before diagnosing a "service problem" |
| 18 | **`skills delete` cascades to samples.** Export first if you need them |
| 19 | **The service can require a newer CLI.** Run `update` rather than retrying |
| 20 | **Omitting `--base-model` triggers an interactive prompt** that hangs scripts |
