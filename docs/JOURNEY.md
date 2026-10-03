# The Contoso warranty RLE — journey

How this world is built, what has been done, and what comes next. Read it top
to bottom the first time; after that, **Where we are** is all you need.

| Part | What it gives you |
| --- | --- |
| [1. The scenario](#1-the-scenario-in-two-minutes) | What the agent does, where its facts live, why it's hard |
| [2. Setting up the world](#2-setting-up-the-world) | A step-by-step recipe, with what you should see at each step |
| [3. The climb](#3-the-climb) | The five stages, what each must prove, how to tell |
| [4. What we've learned](#4-what-weve-learned) | Findings so far, in one table |
| [5. Side experiments](#5-side-experiments) | Runs outside the climb |
| [Appendix](#appendix--helper-snippets) | The small scripts the steps use |

Legend: ✅ done · ⏳ in progress · ⬜ not started · 🖥️ measured here ·
📄 upstream guidance · 🔬 unverified · 💭 reasoning

The full verbatim command record, including every dead end, is in
[evidence/journey-record-2026-10-03.md](evidence/journey-record-2026-10-03.md).

---

## Where we are

| | |
| --- | --- |
| **Status** | World built and wired up. **No stage run yet** |
| **Next** | **P9**: write the stage-0 skill and its 8 prompts, then run stage 0 |
| **Before stage 1** | **P6**: put Entra auth on the MCP endpoint (now open to anyone with the URL) |
| **Worlds** | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4`: the climb, CLI default · `wce-dev` `6bec3bf9-0222-4285-8a5b-214867ac42cc`: scratch |
| **MCP server** | main `1c171d49-7f85-4997-8126-ae20829a4dbf` (**off** for stage 0) · dev `34d14238-fe93-48b5-ba70-3f3a949f6d64` (on) |
| **Before every run** | Check that the 4 baseline counts are 0 ([H2](#h2-baseline-check--are-the-action-tables-clean)) |

---

## 1. The scenario in two minutes

**The job.** Contoso Industrial makes chillers and compressors. Service partners
send in warranty claims. The agent must answer what an adjudicator would:
**is it covered, under which rule, how much is payable, and what happens next?**
Every answer is a decision plus a number, and can be checked against
[GROUND-TRUTH.md](../out/GROUND-TRUTH.md).

**Where the facts live.** The world is set up so no single source is enough.

| Source | What's in it | How the agent reaches it |
| --- | --- | --- |
| SharePoint library `Warranty Operations` | Policy, regional addenda, 12 bulletins, rate cards (Excel), partner agreements, review decks (PowerPoint), inspection reports | Built-in SharePoint search |
| 3 Teams channels | Field escalations, policy announcements, partner chatter | Built-in Teams tools |
| Azure SQL, via our MCP server | Assets, running hours, service history, claims, partners, parts, goodwill authority | 9 read + 3 write tools |

**Why it's hard.** Twelve deliberate traps. A few examples:

| # | Trap | The wrong answer it invites |
| --- | --- | --- |
| 1 | The DB says bulletin TSB-C-0051 stops at serial 1500; the bulletin itself says 1850 | Trusting the database over the document |
| 2 | Bulletin ▸ India addendum ▸ global policy, and the addendum is *shorter* | Picking the most generous or the first rule found |
| 6 | An old review deck says "24 months standard" | Quoting a confident but stale slide |
| 11 | A manager says "go ahead and cover it" in Teams | Treating a chat message as approval |
| 12 | Some assets have no commissioning date | Guessing a date instead of asking for the record |

All 12 are in [03 § 7](03-scenario-design.md).

**The point of the exercise.** Start with an honestly weak agent and improve it
in stages, **changing one thing at a time**, so each gain can be attributed.
The frontier model (GPT-5.6-Sol) stays the same through stages 0–3. Stage 4
then asks whether a small, tuned model can match it.

---

## 2. Setting up the world

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
| [P9](#p9--stage-0-skill-and-prompts) | Stage-0 skill and prompts | ⬜ **next** |
| [P10](#p10--prove-every-source-is-reachable) | Prove every source is reachable | ✅ on dev |
| [P11](#p11--update-the-runbook) | Update the runbook | ⬜ before stage 1 |

> P1 (running the generators) is folded into P0. Outputs below are
> **excerpts**, trimmed or condensed for reading. Every command and its full
> output is in the [execution record](evidence/journey-record-2026-10-03.md).

### P0 — Build and check the corpus

**Why.** Every document, row and expected answer is generated from `spec/`. The
two checks prove the generator and the ground truth agree before anything is
generated.

```powershell
cd build
..\.venv\Scripts\python.exe adjudicate.py     # 14 checks
..\.venv\Scripts\python.exe test_traps.py     # 31 checks
..\.venv\Scripts\python.exe populate.py       # then ground_truth.py and the gen_*.py scripts
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
2. Drag the seven folders from `out/sharepoint/` (`01-Policy` … `07-Reference`) into it in the browser.
3. Check the upload: list each folder, and compare names and sizes with the local files.

<details><summary><strong>You should see</strong></summary>

```text
local=39 remote=39 missing=0
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

### P3 — Teams

**Why.** Field escalations and announcements live in Teams. Trap 11 (verbal approval) is here.

**Do.**
1. In team `Contoso Field Service`, create three **standard** channels: `Field Escalations`, `Warranty Policy Updates`, `Partner Fabrikam`.
2. Run `.\.venv\Scripts\python.exe build\gen_teams.py` to produce `out/teams/*.json`.
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

Then load `out/db/seed.azuresql.sql` with an Entra token ([H3](#h3-run-a-sql-file-with-an-entra-token)). It creates the 11 tables and inserts every row.

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
az acr build -r pcdotaiagentd10b5a -t contoso-service-mcp:<tag> --platform linux/amd64 mcp
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

tools/list -> 12 tools: get_asset, get_running_hours, get_service_history, find_prior_claims, get_claim,
get_dealer, lookup_part, get_tsb_index, get_goodwill_authority, create_claim_adjudication,
request_missing_evidence, escalate_goodwill
```

</details>

**Watch out.** All four of these are already handled in the code, and each produced this error before it was fixed:

| If you see | It means | Handled by |
| --- | --- | --- |
| Container crash: `No module named 'mcp.server.fastmcp'` | `mcp` 2.x was installed | `mcp>=1.2.0,<2` in `requirements.txt` |
| `Invalid Host header` on every call | The SDK only accepts `localhost` | `MCP_ALLOWED_HOSTS=<FQDN>` |
| `ER05017 Failed to connect` when registering, or the agent never calls the tools | **The server must be stateless**: with more than one replica, a session kept in memory is lost | `stateless_http=True` in `server.py` |
| Redirect error on `/mcp/` | The trailing slash redirects to plain HTTP | Always use `/mcp` |

✅ **Result:** healthy, and all 12 tools tested directly, including the writes,
which were cleaned up afterwards. ⚠️ The endpoint has **no authentication** yet; see P6.

### P6 — Protect the MCP endpoint

⬜ **Deferred — must happen before stage 1**, when the tools are first switched on in main.
Anyone with the URL can call the three write tools and leave rows in the database.
The checklist is in [03 § 13 › MCP server](03-scenario-design.md):

1. Connect `auth.py` in `server.py`.
2. Register the Entra app.
3. Set the two environment variables.
4. Check that a call with no token gets 401.
5. `tools upsert` both registrations to `AzureAD`.

### P7 — Create the worlds

**Why.** A "world" (environment) is the agent plus the content it may search.
The content URLs are **frozen at creation**, so a scratch world is created
first to prove them.

**Do.** The world definition is [world/env.md](../world/env.md): a short neutral
instruction, the SharePoint library URL and the three Teams channel URLs.

```powershell
$devId = [guid]::NewGuid().ToString(); "DEV_AGENT_ID=$devId"
frontier-tuning environments init --file world\env.md --agent-id $devId --name "Contoso Warranty Operations (wce-dev)" --output json
frontier-tuning knowledge list --env-id $devId -o json
# ...probe it (P10), then the same for main:
$mainId = [guid]::NewGuid().ToString(); "MAIN_AGENT_ID=$mainId"
frontier-tuning environments init --file world\env.md --agent-id $mainId --name "Contoso Warranty Operations (wce-main)" --output json 2>&1
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
- `tools list` doesn't show custom tools. Use `tools available`.
- `NoAuth` is temporary. P6 switches it to `AzureAD`.

✅ **Result:** connected in both worlds. Dev is on; main is **off**, which is stage 0's condition.

### P9 — Stage-0 skill and prompts

⬜ **Next.** Write `skills/warranty-assistant.md`: one broad skill with
`generateRubrics: true`, so the platform writes the rubrics. That's deliberately
naive. Pick the **8 easiest** eval prompts (covered-simple, declined-simple,
precedence) into `stage0.jsonl`. See the runbook's
[Stage 0](05-hill-climb-runbook.md#stage-0--the-naive-build).

### P10 — Prove every source is reachable

✅ **On dev.** One question per source, asked through the agent. Each answer was correct and cited its source.

| Source | Question | Agent did | Time |
| --- | --- | --- | --- |
| SharePoint | TSB-C-0051's serial range and coverage? | 1 search → correct (01200–01850, 36 mo / 8,000 h) | 52 s |
| Teams | What did Vikram say on C-2026-04141, and Meera's reply? | 7 Teams calls → correct, authors read from the text | 80 s |
| Database | Commissioning date and hours of CIE-4000-CH-01700? | 2 MCP calls → correct (4 Apr 2024, 4,120 h) | 53 s |

Raw records: [p7](evidence/p7/) · [p8](evidence/p8/).

🔬 **Not yet proven:** the other files and threads one by one, Excel content
specifically, and the same on main. The stage-0 probe on main covers the last.

### P11 — Update the runbook

⬜ **Before stage 1.** Two gaps in [runbook 05](05-hill-climb-runbook.md):
- Add AGENTS goals 3 (use the platform's own tools) and 4 (Simple vs BestOfN headroom).
- Correct the tool names to the `<id prefix>__<tool>` form.

---

## 3. The climb

📄 Plan from [runbook 05](05-hill-climb-runbook.md). Scores are 💭 predictions until measured.

| Stage | The one change | Expect | It proves… | Pass if |
| --- | --- | --- | --- | --- |
| **0** | Nothing — one broad skill, platform-written rubrics, MCP off, 8 easy prompts | 0.45–0.55 | The documents are reachable; the weakness is missing facts | Retrieval shows up in the trace · score 0.40–0.60 (< 0.30 means retrieval is broken, stop) |
| **1** | MCP server switched on | 0.62–0.70 | How much was just plumbing | Score up ≥ 0.10 **and** DB tools in the trace |
| **2** | Hand-written rubrics first, then 3 thin skills | 0.76–0.84 | Rubric and skill design is the biggest lever | The 3 skills score differently per rubric |
| **3** | All 30 honest prompts | 0.72–0.80 (may drop) | Where the agent is truly weak | 0.60–0.75 · Simple vs BestOfN gap measured |
| **4** | Swap to a small model, then tune it | 0.50–0.60 → 0.76–0.82 | A tuned small model can match the frontier | Within 0.05 of frontier, still abstains correctly |

**Skills vs rubrics.** Stage 0 lets the platform write the rubrics on purpose:
that's the naive baseline. From stage 2, rubrics are written by hand
**before** the skills ([drafts in 03 § 9.2](03-scenario-design.md#92-rubrics-for-the-flagship-skill--written-before-the-skill-exists)),
and the platform tools are measured against them.

*No stage has run yet.*

---

## 4. What we've learned

| Date | Finding | |
| --- | --- | --- |
| 10-03 | Uploaded content became searchable in **under 5.5 h**, not the day we budgeted | 🖥️ |
| 10-03 | Agent calls take **50–90 s** when the right tools are available, about 4 min when the agent has to hunt. Each tool call costs 3–11 s through the platform | 🖥️ |
| 10-03 | The run response **doesn't name the model** that served it, and its tool-call count in `billingSummary` doesn't always match the trace | 🖥️ |
| 10-03 | The GPT-5.4-Mini pair (run vs tune) share a base-model name; the MAI pair don't. That matters for a clean before/after in stage 4 | 🔬 |
| 10-03 | `--strategy simple` is accepted. Whether strategies actually change behaviour is still untested (stage 3) | 🔬 |

---

## 5. Side experiments

### GPT-5.6 vs MAI on one question · 10-03

Same question on dev for both models: *"Is the hydraulic pump repair on claim
C-2026-04114 covered under warranty? State the governing instrument and when
that coverage expires. Do not record or change anything in the claim system."*
Expected: covered, TSB-C-0051, expires 4 Apr 2027 or 8,000 h. Trap 1 is in play.

| | GPT-5.6 (`prod-gpt-56-reasoning-sol`) | MAI (`dev-ct-mai-code-mp`) |
| --- | --- | --- |
| Answer | ✅ Correct, trap 1 handled | ✅ Correct, trap 1 handled |
| Time | 62 s | 86 s |
| Tool calls | 6 DB + 2 documents | 6 DB + 3 documents |
| Tokens in / out | 143,361 / 1,238 | 115,928 / 435 |

💭 This is the first run to use documents and database together, and both
models handled it. One easy question says nothing about the gap between them;
stage 4 measures that properly. Raw records: [evidence/adhoc-model-compare/](evidence/adhoc-model-compare/).

---

## Appendix — helper snippets

H3 and H4 are exactly as run. H1 is a simplified, single-file form of the
summary one-liners in the record. H2 is as run, except its script path is
changed to `$env:TEMP`. Windows PowerShell 5.1 is used for SQL because it
ships with `System.Data.SqlClient`, so nothing needs installing.

### H1 Summarise an agent run

```powershell
$j = Get-Content <run>.json -Raw | ConvertFrom-Json
"status=$($j.status) exec=$($j.executionId) $($j.startDateTime) -> $($j.endDateTime)"
$j.toolExecutions | ForEach-Object { "  {0} | {1} | {2} ms | inputs: {3}" -f $_.Title, $_.Status, $_.LatencyMs, (($_.Inputs | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join '; ') }
($j.response | Out-String).Trim()
```

### H2 Baseline check — are the action tables clean?

```powershell
$s = @'
param($Token)
$cn = New-Object System.Data.SqlClient.SqlConnection("Server=tcp:az-sqldb-common.database.windows.net,1433;Database=contoso-warranty;Encrypt=True;Connection Timeout=90;")
$cn.AccessToken = $Token; $cn.Open(); $c = $cn.CreateCommand()
$c.CommandText = "SELECT (SELECT COUNT(*) FROM ClaimAdjudicationDraft) drafts, (SELECT COUNT(*) FROM EvidenceRequest) evidence, (SELECT COUNT(*) FROM GoodwillEscalation) escalations, (SELECT COUNT(*) FROM Claims WHERE status <> 'Submitted') non_submitted"
$r = $c.ExecuteReader(); $r.Read() | Out-Null; "drafts={0} evidence={1} escalations={2} non_submitted={3}" -f $r[0], $r[1], $r[2], $r[3]; $cn.Close()
'@
$p = "$env:TEMP\baseline-check.ps1"; Set-Content $p $s -Encoding UTF8
$tok = az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $p -Token $tok
# expect: drafts=0 evidence=0 escalations=0 non_submitted=0
```

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
powershell.exe -NoProfile -ExecutionPolicy Bypass -File load-sql.ps1 -File (Resolve-Path out\db\seed.azuresql.sql).Path -Token $tok
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
