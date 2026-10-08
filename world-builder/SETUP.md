# Setup: building the world on this tenant

The build recipe as it was run (2026-10-03, updated for world v3 on 2026-10-07). Each step reads **Why · Do · You should see · Watch out · Result**. Commands run from the repository root unless a step says otherwise.

## Steps

| Step | What | Status |
| --- | --- | --- |
| [P0](#p0--build-and-check-the-corpus) | Build and check the corpus | ✅ |
| [P2](#p2--sharepoint) | Load SharePoint | ✅ |
| [P3](#p3--teams) | Load Teams | ✅ |
| [P4](#p4--azure-sql) | Load Azure SQL | ✅ |
| [P5](#p5--deploy-the-mcp-server) | Deploy the MCP server | ✅ |
| [P6](#p6--protect-the-mcp-endpoint) | Protect the MCP endpoint | ⬜ before stage 1 |
| [P7](#p7--create-the-worlds) | Create the worlds | ✅ |
| [P8](#p8--connect-the-mcp-server-to-the-worlds) | Connect the MCP server to the worlds | ✅ |
| [P9](#p9--stage-0-skill-and-prompts) | Stage-0 skill and prompts | ✅ |
| [P10](#p10--prove-every-source-is-reachable) | Prove every source is reachable | ✅ dev · ✅ main (stage-0 probe) |

> P1 (running the generators) is folded into P0. Outputs below are
> **excerpts**, trimmed or condensed for reading. Every command and its full
> output is in the execution record.

### P0 — Build and check the corpus

**Why.** Every document, row and expected answer is generated from `spec/`. The
two checks prove the generator and the ground truth agree before anything is
generated.

```powershell
cd world-builder\build
..\..\.venv\Scripts\python.exe adjudicate.py     # 14 checks
..\..\.venv\Scripts\python.exe test_traps.py     # 31 checks
..\..\.venv\Scripts\python.exe populate.py       # then ground_truth.py and the gen_*.py scripts
```

<details><summary><strong>You should see</strong> (tail)</summary>

```text
All 14 checks passed - guide 03 section 8 reproduces.
31/31 checks passed.
```

</details>

✅ **Result:** 39 SharePoint files, 3 Teams channel files, an 11-table database
seed, and 30 eval / 60 train prompts in `out/`.

### P2 — SharePoint

**Why.** The agent reads policies, bulletins and rate cards from one library.

**Do.**
1. On the team site `https://microsoftapc.sharepoint.com/teams/ContosoFieldService`, create **one** document library, `Warranty Operations`. It was created through WorkIQ: `POST /sites/{site-id}/lists` with `{"displayName":"Warranty Operations","list":{"template":"documentLibrary"}}`.
2. Drag the seven folders from `world-builder/out/sharepoint/` (`01-Policy` … `07-Reference`) into it in the browser.
3. Check the upload: list each folder, and compare names and sizes with the local files.

<details><summary><strong>You should see</strong></summary>

```text
local=39 remote=39 missing=0      (v2; v3 has 38: the two labour workbooks are merged into one)
.docx: n=34 delta min=8890 max=8902
.pptx: n=2 delta min=8447 max=8533
.xlsx: n=3 delta min=7448 max=7462
TSB-C-0051 text, downloaded vs local: paragraphs+rows 18 18 identical: True
```

</details>

**Watch out.**
- One library with seven folders, not seven libraries.
- On this tenant, files can't be uploaded from code. WorkIQ only sends JSON, the Azure CLI token is rejected, and Graph PowerShell needs admin consent. Use the browser.
- Uploaded files are about 8 KB bigger. That's SharePoint adding its own metadata, not damage.

✅ **Result:** 39/39 files in place, and the trap-1 bulletin's text is identical.

**World v3 (2026-10-07):** `03-RateCards` now holds `Warranty-Labour-Rate-Card-FY26.xlsx` (flat-rate schedule + regional rates, two sheets) and `Parts-Price-List-FY26.xlsx`. Uploaded and the two v2 workbooks deleted with the world's own SharePoint tools (`tools invoke mcp_SharePointRemoteServer__createSmallBinaryFile` / `deleteFileOrFolder`, run without `cmd.exe`, whose ~8k command-line limit truncates the base64). Searchable at rank 1 within minutes.

### P3 — Teams

**Why.** Field escalations and announcements live in Teams. Trap 11 (verbal approval) is here.

**Do.**
1. In team `Contoso Field Service`, create three **standard** channels: `Field Escalations`, `Warranty Policy Updates`, `Partner Fabrikam`.
2. Run `.\.venv\Scripts\python.exe world-builder\build\gen_teams.py` to produce `world-builder/out/teams/*.json`.
3. Post each thread, then its replies in order. Start each message with the author and date in bold, and strip the internal trap labels. Posted through WorkIQ: `POST /teams/{team}/channels/{channel}/messages` and `.../messages/{id}/replies`.
4. Read the channels back and count.

<details><summary><strong>You should see</strong></summary>

```text
Field Escalations        threads=6 replies=14 total=20 leak=False
Warranty Policy Updates  threads=5 replies=0  total=5  leak=False
Partner Fabrikam         threads=3 replies=3  total=6  leak=False
```

</details>

**Watch out.**
- Use **standard** channels. 🔬 Shared channels may not be searched the same way.
- A deleted channel's name can't be reused for a while (🔬 about 30 days), which is why the names use spaces.
- Every post appears as *you*, posted today. Put the real author and date in the text: the agent reads them from there.

✅ **Result:** 31/31 messages, no trap labels.

### P4 — Azure SQL

**Why.** Asset facts (commissioning date, hours, parts, partners) live only in the database.

**Do.**

```powershell
az sql db create -g az-sqldb-common-rg -s az-sqldb-common -n contoso-warranty `
  --edition GeneralPurpose --compute-model Serverless --family Gen5 --capacity 1 `
  --min-capacity 0.5 --auto-pause-delay 60 --backup-storage-redundancy Local
```

Then load `world-builder/out/db/seed.azuresql.sql` with an Entra token ([H3](#h3-run-a-sql-file-with-an-entra-token)). It creates the 11 tables and inserts every row.

<details><summary><strong>You should see</strong></summary>

```text
{ "autoPause": 60, "min": 0.5, "name": "contoso-warranty", "sku": "GP_S_Gen5", "status": "Online", ... }
OK: 8 batches executed
AZ Assets=117  AssetTelemetry=2989  Claims=90  ServiceHistory=89  Parts=14  Dealers=4  GoodwillAuthority=4  TsbApplicability=4
TRAP1 TSB-C-0051 serial_to=1500     TRAP12 null commissioning=3      (identical to the local contoso.db)
```

</details>

**Watch out.**
- The server is **Entra-only**, so there are no SQL usernames or passwords. The deploy guide's `sqlcmd -U/-P` steps don't apply.
- The database pauses after 60 minutes idle, and the first call after that takes 30–60 s. Warm it before a run.

✅ **Result:** every table matches the local build, and traps 1 and 12 are in place.

### P5 — Deploy the MCP server

**Why.** The agent reaches the database only through this server.

**Do.**

```powershell
az acr build -r pcdotaiagentd10b5a -t contoso-service-mcp:<tag> --platform linux/amd64 world-builder/mcp
az containerapp create -g pcdotai-agent -n contoso-service-mcp --environment pcdotai-agent `
  --image pcdotaiagentd10b5a.azurecr.io/contoso-service-mcp:<tag> `
  --registry-server pcdotaiagentd10b5a.azurecr.io --registry-identity system --system-assigned `
  --target-port 8000 --ingress external --min-replicas 1 --max-replicas 3 --cpu 0.5 --memory 1.0Gi `
  --env-vars "AZURE_SQL_CONNECTION_STRING=<ODBC string, no password>" "AZURE_SQL_USE_MANAGED_IDENTITY=true" `
             "MCP_ALLOWED_HOSTS=<app FQDN>"
```

Then give the app's managed identity access to the database ([H4](#h4-give-the-apps-managed-identity-database-access)).

<details><summary><strong>You should see</strong></summary>

```text
GET https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz
{"status":"ok","assets":117}

tools/list -> 4 tools (world v3): get_claim_dossier, create_claim_adjudication,
request_missing_evidence, escalate_goodwill
(world v2 had 9 reads: get_asset, get_running_hours, get_service_history, find_prior_claims,
get_claim, get_dealer, lookup_part, get_tsb_index, get_goodwill_authority)
```

</details>

**Watch out.** All four of these are already handled in the code, and each produced this error before it was fixed:

| If you see | It means | Handled by |
| --- | --- | --- |
| Container crash: `No module named 'mcp.server.fastmcp'` | `mcp` 2.x was installed | `mcp>=1.2.0,<2` in `requirements.txt` |
| `Invalid Host header` on every call | The SDK only accepts `localhost` | `MCP_ALLOWED_HOSTS=<FQDN>` |
| `ER05017 Failed to connect` when registering, or the agent never calls the tools | **The server must be stateless**: with more than one replica, a session kept in memory is lost | `stateless_http=True` in `server.py` |
| Redirect error on `/mcp/` | The trailing slash redirects to plain HTTP | Always use `/mcp` |

✅ **Result:** healthy, and all tools tested directly, including the writes,
which were cleaned up afterwards. ⚠️ The endpoint has **no authentication** yet; see P6.

### P6 — Protect the MCP endpoint

⬜ **Deferred — must happen before stage 1**, when the tools are first switched on in main.
Anyone with the URL can call the three write tools and leave rows in the database.
The checklist is in [03 § 13 › MCP server](docs/03-scenario-design.md):

1. Connect `auth.py` in `server.py`.
2. Register the Entra app.
3. Set the two environment variables.
4. Check that a call with no token gets 401.
5. `tools upsert` both registrations to `AzureAD`.

### P7 — Create the worlds

**Why.** A "world" (environment) is the agent plus the content it may search.
The content URLs are **frozen at creation**, so a scratch world is created
first to prove them.

**Do.** The world definition is [env.md](env.md): a short neutral
instruction, the SharePoint library URL and the three Teams channel URLs.

```powershell
$devId = [guid]::NewGuid().ToString(); "DEV_AGENT_ID=$devId"
frontier-tuning environments init --file world-builder\env.md --agent-id $devId --name "Contoso Warranty Operations (wce-dev)" --output json
frontier-tuning knowledge list --env-id $devId -o json
# ...probe it (P10), then the same for main:
$mainId = [guid]::NewGuid().ToString(); "MAIN_AGENT_ID=$mainId"
frontier-tuning environments init --file world-builder\env.md --agent-id $mainId --name "Contoso Warranty Operations (wce-main)" --output json 2>&1
```

<details><summary><strong>You should see</strong></summary>

```text
DEV_AGENT_ID=6bec3bf9-0222-4285-8a5b-214867ac42cc
{
  "IsWorkspaceReady": true,
  "DebugContext": {
    "Logs": []
  }
}
--- knowledge (main, same as dev)
folder | Warranty Operations
teamsMessage | Field Escalations
teamsMessage | Warranty Policy Updates
teamsMessage | Partner Fabrikam
```

</details>

**Watch out.**
- `IsWorkspaceReady: true` doesn't mean the content is readable. That's what the P10 probe is for.
- Empty `sharepointIds` in `knowledge list` is normal for URL-scoped sources.
- `init` makes the new world the CLI default. Pass `--env-id` explicitly when there's more than one world.

✅ **Result:** two worlds with the same four sources. Models available
(`models list`): **GPT-5.6-Sol** (default), GPT-5.4-Mini and MAI-CODE-5b for runs;
GPT-5.4-Mini and MAI-Code-1-Flash for tuning.

### P8 — Connect the MCP server to the worlds

**Why.** `env.md` can't hold an MCP server: it only takes SharePoint, Teams,
Meetings and Graph connectors. Custom tools are added after the world exists.

```powershell
frontier-tuning tools create --env-id <world-id> --name contoso-service `
  --description "Contoso service claim system: asset registry, running-hours telemetry, service history, claims, partner master, parts, goodwill authority, and draft adjudication actions." `
  --url https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/mcp --auth-scheme NoAuth -o json
frontier-tuning tools status <server-id> --env-id <world-id>
frontier-tuning tools disable 1c171d49-7f85-4997-8126-ae20829a4dbf --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4   # main only: stage 0 runs without it
```

<details><summary><strong>You should see</strong></summary>

```text
"AuthenticationScheme": "NoAuth", "Enabled": true, ...
Tool: contoso-service
ID: 34d14238-fe93-48b5-ba70-3f3a949f6d64
Observed Callable Tools: 12
Discovery Status: observed
Tool 1c171d49-7f85-4997-8126-ae20829a4dbf disabled.
main available total: 125            (dev: 137 = 125 + our 12)
```

</details>

**Watch out.**
- The agent sees our tools as `<first 5 chars of server id>__<tool>` (e.g. `34d14__get_asset`), not `contoso-service__…`.
- `tools list` shows only the **first 50** tools by default, which hides ours. Use `tools list --limit 500` or `tools available`.
- `NoAuth` is temporary. P6 switches it to `AzureAD`.

✅ **Result:** connected in both worlds. Dev is on; main is **off**, which is stage 0's condition.

### P9 — Stage-0 skill and prompts

**Why.** Stage 0 needs one broad skill, with rubrics written by the platform
rather than by us. That's the naive baseline the climb starts from.

**Do.**
1. Write stages/stage-0/warranty-assistant.md. It describes the business job: who the agent serves, what an adjudication must establish, which sources exist, and how to write for an adjudicator. It deliberately leaves out the rules that solve the traps (which instrument wins, document over index, no install-date substitute, flat-rate cap, rate by repair date, written authority). The agent has to find those in the policy documents.
2. Create it on dev with `generateRubrics: true`, and review what the platform generates.
3. Pin the generated set in warranty-assistant.rubrics.json and apply it to main, so both worlds are scored against identical rubrics.

```powershell
frontier-tuning skills create --file stages\stage-0\warranty-assistant.md --env-id 6bec3bf9-0222-4285-8a5b-214867ac42cc -o json   # dev: generates rubrics
frontier-tuning skills create --file stages\stage-0\warranty-assistant.md --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json   # main
frontier-tuning skills update cf00d339-5217-4cd1-b390-cc0d911735da --file <main skill JSON with pinned Rubrics> --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
```

<details><summary><strong>You should see</strong> — the pinned rubrics on both worlds</summary>

```text
Requested Outcome Delivery                        (critical, user_facing,          6 items)
Claim Determination Requirements                  (critical, user_facing,          5 items)
Internal Record Use and Grounding                 (critical, trajectory_non_tool, 10 items)
Adjudicator-Ready Presentation and Traceability   (high,     user_facing,          6 items)
Claim-System Draft Execution                      (critical, trajectory_non_tool,  1 items)
identical to pinned (name, importance, type, items): True
```

</details>

How the generated rubrics map onto the rubrics we designed in 03 § 9.2:

| Designed rubric | Generated set covers it? |
| --- | --- |
| Coverage determination | ✅ |
| Evidence grounding | ✅ strongly: 10 source checks plus per-fact attribution |
| Valuation accuracy | ✅ structure and arithmetic, but not the trap rules |
| Evidence closure | ✅ unestablished facts, conflicting sources |
| Precedence discipline | ⚠️ names the instrument, but not why it beats the others |
| Authority and action | ⚠️ checks drafts are recorded, but not approval authority |

The ⚠️ gaps are intentional headroom: stage 2's hand-written rubrics close them.

**Watch out.**
- **Rubric generation isn't repeatable.** The same file gave 5 rubrics on dev, 1 rubric (14 items) on main, and a different 5 on a preview regeneration. Pin one set, or stages can't be compared.
- `skills create` updates in place by name. With `generateRubrics: true` it would silently replace the pinned rubrics, so the file is now `false`.
- `Claim-System Draft Execution` will fail at stage 0, where the MCP server is off. That's expected, and part of the diagnosable gap.
- From stage 1, the agent records drafts, so run the baseline check ([H2](#h2-baseline-check--are-the-action-tables-clean)) and clean up between runs.

✅ **Skill done:** `warranty-assistant` on main `cf00d339-5217-4cd1-b390-cc0d911735da` and dev `8e9d12a2-b0a5-4683-95f1-b225ed9ade44`, with identical pinned rubrics.
✅ **Prompts done:** 8 eval prompts in stages/stage-0/stage0.jsonl: 3 covered-simple, 2 declined-simple, and 3 precedence (04114, 04116, 04118).

### P10 — Prove every source is reachable

✅ **On dev.** One question per source, asked through the agent. Each answer was correct and cited its source.

| Source | Question | Agent did | Time |
| --- | --- | --- | --- |
| SharePoint | TSB-C-0051's serial range and coverage? | 1 search → correct (01200–01850, 36 mo / 8,000 h) | 52 s |
| Teams | What did Vikram say on C-2026-04141, and Meera's reply? | 7 Teams calls → correct, authors read from the text | 80 s |
| Database | Commissioning date and hours of CIE-4000-CH-01700? | 2 MCP calls → correct (4 Apr 2024, 4,120 h) | 53 s |

Raw records: p7 · p8.

🔬 **Not yet proven:** the other files and threads one by one, Excel content
specifically, and the same on main. The stage-0 probe on main covers the last.

---

## Helpers

### H3 Run a SQL file with an Entra token

```powershell
# load-sql.ps1
param($File, $Token)
$cn = New-Object System.Data.SqlClient.SqlConnection("Server=tcp:az-sqldb-common.database.windows.net,1433;Database=contoso-warranty;Encrypt=True;TrustServerCertificate=False;Connection Timeout=90;")
$cn.AccessToken = $Token
$cn.Open()
$text = [IO.File]::ReadAllText($File)
$batches = [regex]::Split($text, '(?im)^\s*GO\s*$') | Where-Object { $_.Trim() }
$i = 0
foreach ($b in $batches) {
  $i++
  $cmd = $cn.CreateCommand(); $cmd.CommandText = $b; $cmd.CommandTimeout = 300
  try { [void]$cmd.ExecuteNonQuery() } catch { Write-Output "FAILED batch $i : $($_.Exception.InnerException.Message)"; $cn.Close(); exit 1 }
}
Write-Output "OK: $i batches executed"
$cn.Close()
```

```powershell
$tok = az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv
powershell.exe -NoProfile -ExecutionPolicy Bypass -File load-sql.ps1 -File (Resolve-Path world-builder\out\db\seed.azuresql.sql).Path -Token $tok
```

### H4 Give the app's managed identity database access

The user is created from the identity's app ID, so the server needs no directory lookup.

```sql
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'contoso-service-mcp')
BEGIN
    DECLARE @sid varbinary(16) = CAST(CAST('7fc1bdfd-95af-4c4b-bbeb-82203b1300b1' AS uniqueidentifier) AS varbinary(16));
    DECLARE @stmt nvarchar(400) = N'CREATE USER [contoso-service-mcp] WITH SID = ' + CONVERT(varchar(34), @sid, 1) + N', TYPE = E';
    EXEC(@stmt);
END;
ALTER ROLE db_datareader ADD MEMBER [contoso-service-mcp];
ALTER ROLE db_datawriter ADD MEMBER [contoso-service-mcp];
```

App ID: `az ad sp show --id <principalId> --query appId -o tsv`.
