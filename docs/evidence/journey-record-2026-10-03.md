# Execution record — 2026-10-03 (verbatim)

> Full step-by-step record of everything run on 2026-10-03, every command and
> captured output, including dead ends and debugging. Kept as evidence.
> **For the readable walkthrough, see [JOURNEY.md](../JOURNEY.md).**

<!-- original title: Journey log — Contoso warranty RLE -->

Where we are, what each stage must prove, and what actually happened. The
logging rules are in [AGENTS.md § Journey log](../../AGENTS.md#journey-log--keep-it-current).

## Now

| | |
| --- | --- |
| **Position** | Prerequisites P0–P5, P7, P8 ✅ · P10 ✅ on dev · P6, P9, P11 open · no stage started |
| **Next action** | **P9**: write the stage-0 skill and the 8-prompt sample file |
| **Worlds** | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` (CLI default) · `wce-dev` `6bec3bf9-0222-4285-8a5b-214867ac42cc` (throwaway) |
| **MCP server ids** | main `1c171d49-7f85-4997-8126-ae20829a4dbf` (**disabled**, stage-0 condition) · dev `34d14238-fe93-48b5-ba70-3f3a949f6d64` (enabled) · both `NoAuth` |
| **Earliest stage 0** | As soon as P9 is done |
| **Open risk** | P6: the endpoint is unauthenticated. Run the 4-count baseline check (8.11) before every evaluation |

Legend: ✅ done · ⏳ in progress · ⬜ not started · ⛔ blocked · 🖥️ measured · 📄 upstream · 🔬 unverified · 💭 reasoning

---

## 1. Prerequisites

| # | Step | Done when | Status |
| --- | --- | --- | --- |
| P0 | Build gates | `adjudicate.py` 14/14, `test_traps.py` 31/31 | ✅ re-run 2026-10-03 |
| P1 | Generate corpus | `populate` → `ground_truth` → `gen_*` write `out/` | ✅ earlier session — output not captured |
| P2 | SharePoint loaded | 39/39 files in `Warranty Operations`, verified | ✅ 2026-10-03 |
| P3 | Teams loaded | 3 standard channels, 31 messages, read back | ✅ 2026-10-03 |
| P4 | Azure SQL loaded | Row counts = `contoso.db`, traps 1 and 12 present | ✅ 2026-10-03 |
| P5 | MCP server deployed | `/healthz` ok, 12/12 tools over `/mcp`, managed-identity DB access | ✅ 2026-10-03 |
| P6 | MCP endpoint protected | No token → 401; Entra app registered; both registrations `tools upsert` → `AzureAD` | ⬜ deferred — [03 § 16 item 6](../03-scenario-design.md#still-open) · **before stage 1** |
| P7 | Pre-flight + world init | `check` ok · `models list` re-read · `--strategy` and model-pair questions tested · `environments init` with SP + Teams URLs · `IsWorkspaceReady: true` | ✅ 2026-10-03 · model pair 🔬 hint only |
| P8 | MCP registered, switched off | `tools create` → server id from `tools sources` → `tools disable` | ✅ 2026-10-03 · `NoAuth` until P6 · main **disabled**, dev enabled |
| P9 | Stage-0 assets | `skills/warranty-assistant.md` (`generateRubrics: true`) + 8-prompt `stage0.jsonl` (covered-simple, declined-simple, precedence) | ⬜ neither file exists |
| P10 | Reachability proven | One `chat` probe per source type; `FileRetrievalDetails` non-empty | ✅ on `wce-dev` 2026-10-03 · repeat on main as the stage-0 probe |
| P11 | Runbook gap closed | AGENTS goals 3 (platform tools) and 4 (Simple vs BestOfN) written into runbook 05 · tool names corrected to `<server-id prefix>__<tool>` (P8) | ⬜ before stage 1 |

---

## 2. Stages

📄 From [runbook 05](../05-hill-climb-runbook.md). Scores are 💭 predictions until § 3 records a 🖥️ result.

| Stage | The one change | Expect | Discover | Gate — how to check | Don't miss |
| --- | --- | --- | --- | --- | --- |
| **0** | None — baseline: one broad skill, **platform-generated** rubrics, MCP off, 8 easy prompts | 0.45–0.55 | Do documents retrieve? Do generated rubrics just restate the prompt? | Probe JSON: `FileRetrievalDetails` non-empty · Submitted = Graded · score 0.40–0.60 | < 0.30 means retrieval is broken → **stop**. > 0.70 means the samples are too easy |
| **1** | MCP server enabled | 0.62–0.70 | How much of the gap is plumbing | Score up ≥ 0.10 **and** DB tools in the trace | Warm the DB first. Flat score with tools in the trace → rubric problem |
| **2** | **Rubrics hand-written first** → 3 thin skills | 0.76–0.84 | Which rubric moved; do `generate-rubrics` / `rubrics refine` beat the hand-written set? | The 3 skills diverge per rubric · rubrics landed un-regenerated | Rubric wording never goes into instructions · `samples delete-by-skill` before re-upload |
| **3** | Full 30 honest prompts | 0.72–0.80 (may drop) | Where the agent is truly weak | 0.60–0.75, or deploy the reserve · Simple vs BestOfN gap measured | Smoke run before the 4.5 h run · > 0.95 → harden the world |
| **4** | Model → small MAI, then tuned | 0.50–0.60 → 0.76–0.82 | Same weights? Does tuning close the gap? | Within 0.05 of frontier, abstention intact | Settle the model-pair question first · disable stage-0 skill · dedupe samples |

**Skills vs rubrics.** Stage 0 *deliberately* creates the skill and lets the
platform generate rubrics — that is the naive baseline. From stage 2 the rule
flips: rubrics are written first ([03 § 9.2](../03-scenario-design.md#92-rubrics-for-the-flagship-skill--written-before-the-skill-exists)),
then thin skills, then the platform tools are measured against them.

---

## 3. Execution log

Chronological. Each step: command · what it does · captured output · outcome.
Each prerequisite or stage closes with **Discovered · Inferred · Gate**.

> ⚠️ **P2–P5 were written up after the fact.** Several of their output blocks are
> condensed summaries of the real output, not verbatim captures, and some
> commands are shown in simplified form. The outcomes and gates are accurate.
> From **P7** on, every command is logged exactly as run and every output
> verbatim. Raw JSON is kept in [`evidence/`]().

### P0 — Build gates · 2026-10-03

```powershell
cd build; ..\.venv\Scripts\python.exe adjudicate.py; ..\.venv\Scripts\python.exe test_traps.py
```

Recomputes the worked example and every trap from `spec/`. Read-only.

<details><summary><strong>Captured output</strong> (tail)</summary>

```text
  PASS  1.5 h variance reported
  PASS  stale index flagged (trap-1)
  PASS  expiry 2027-04-04
  PASS  addendum and policy were considered
All 14 checks passed - guide 03 section 8 reproduces.
----
  PASS  trap-12 unknown serial -> request_evidence
  PASS  repair-warranty  covered under policy 6.1 despite an expired asset warranty
  PASS  repair-warranty  beyond 90 days it does not apply
  PASS  region  EMEA-only TSB-P-0115 does not extend an Indian asset
31/31 checks passed.
```

</details>

**Outcome:** ✅ 14/14 and 31/31. `git status` clean afterwards.

**P1** ran in an earlier session. The evidence is the [README status table](../../README.md#status):
34 docx · 3 xlsx · 2 pptx · 3 Teams JSON · 11-table seed · 30 eval / 60 train prompts.

---

### P2 — SharePoint · 2026-10-03

Target: one library, `Warranty Operations`, with seven folders — **not** seven libraries.

**2.1 Resolve the site**

```text
workiq fetch  /sites/microsoftapc.sharepoint.com:/teams/ContosoFieldService?$select=id,displayName,webUrl
```

Turns the site URL into the Graph site id that every later call needs.

<details><summary><strong>Captured output</strong></summary>

```json
{"displayName":"Contoso Field Service",
 "id":"microsoftapc.sharepoint.com,ee5fd16e-cda8-4f89-90ca-01b0d154b5b2,5fc7228e-1e45-42a3-86fe-f6b4894cd380",
 "webUrl":"https://microsoftapc.sharepoint.com/teams/ContosoFieldService"}  statusCode 200
```

</details>

**Outcome:** ✅ Site found. It is the Teams team's own site.

**2.2 Create the library**

```text
workiq create_entity  POST /sites/{site-id}/lists
{"displayName":"Warranty Operations","list":{"template":"documentLibrary"}}
```

Creates the document library. Its drive id comes from `GET /sites/{site-id}/drives`.

<details><summary><strong>Captured output</strong> (trimmed)</summary>

```json
{"displayName":"Warranty Operations","id":"278e4aaf-0de8-404d-b005-b81edf871004",
 "list":{"template":"documentLibrary"},
 "webUrl":"https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty%20Operations"}  statusCode 201
drive: b!btFf7qjNiU-QygGw0VS1so4ix19FHqNChv72tIlM04CvSo4n6A1NQLAFuB7fhxAE
```

</details>

**Outcome:** ✅ Library created.

**2.3 Upload from code — every route failed**

```text
workiq do_action   POST /drives/{d}/items/{folder}:/{name}:/createUploadSession
PUT <uploadUrl>                                  (bytes, no auth / az SharePoint token)
GET https://…/_api/web                           (az SharePoint token)
Connect-MgGraph -Scopes Sites.ReadWrite.All
```

Tries each way to push file bytes from this machine.

<details><summary><strong>Captured output</strong></summary>

```text
createUploadSession (path form) -> Access denied for POST path ...                       (WorkIQ allow-list)
PUT uploadUrl, no token         -> 401 {"code":"unauthenticated"}
PUT uploadUrl, az token         -> 401 {"innerError":{"code":"invalidAudienceUri"}}
SharePoint REST, az token       -> 401 {}
Connect-MgGraph                 -> "admin approval required"                             (reported by user)
```

</details>

**Outcome:** ⛔ WorkIQ only carries JSON. The CLI token has the wrong audience. Graph PowerShell needs admin consent. OneDrive sync was ruled out by the user.

**2.4 Upload by hand** — the user dragged the seven `out/sharepoint/` folders into the empty library.

**2.5 Verify names and sizes**

```powershell
# workiq fetch /drives/{d}/items/{folder}/children?$select=name,size  (x7), then:
$local | ... compare name + size against remote ...
```

Checks that every local file exists remotely, and how the sizes differ.

<details><summary><strong>Captured output</strong></summary>

```text
local=39 remote=39 missing=0
.docx: n=34 delta min=8890 max=8902
.pptx: n=2 delta min=8447 max=8533
.xlsx: n=3 delta min=7448 max=7462
```

</details>

**Outcome:** ✅ All 39 present. The size difference is nearly constant per type.

**2.6 Verify content of the trap-1 bulletin**

```text
workiq fetch_blob /drives/{d}/items/{TSB-C-0051 id}/content   → python-docx text diff vs local
```

Downloads the file and compares paragraph and table text with the local copy.

<details><summary><strong>Captured output</strong></summary>

```text
paragraphs+rows remote/local: 18 18 identical: True
['Serial range | CIE-4000-CH-01200 to CIE-4000-CH-01850 inclusive']
```

</details>

**Outcome:** ✅ Identical text.

| Discovered | Inferred | Gate |
| --- | --- | --- |
| WorkIQ can create libraries and folders but cannot upload bytes. Every token route is blocked on this tenant | 💭 The +7–9 KB is SharePoint writing metadata into the file on upload, not corruption — supported by 2.6 | ✅ 39/39 names match · trap-1 bulletin text identical |

---

### P3 — Teams · 2026-10-03

Target: team `Contoso Field Service`, 3 **standard** channels, 14 threads / 31 messages, with no trap labels posted.

**3.1 Inspect the channels the user created**

```text
workiq fetch /teams/1d67f268-…/channels?$select=id,displayName,membershipType
```

Lists channel types and existing content before anything is posted.

<details><summary><strong>Captured output</strong></summary>

```text
Partner-Fabrikam         shared
Field-Escalations        standard
Warranty-Policy-Updates  shared
(each channel: system event messages only)
```

</details>

**Outcome:** ⚠️ Two channels were *shared*. 🔬 Shared channels may not ground the same way as standard ones, so the user chose to replace them.

**3.2 Replace the shared channels**

```text
workiq delete_entity /teams/{t}/channels/{shared-id}          (x2)
workiq create_entity POST /teams/{t}/channels {"displayName":"Partner-Fabrikam","membershipType":"standard"}
```

Deletes the empty shared channels and recreates them as standard.

<details><summary><strong>Captured output</strong></summary>

```text
delete  -> 204, 204
create  -> 400 NameAlreadyExists "Channel name already exists, please use other name"
```

</details>

**Outcome:** ⚠️ Teams holds a deleted channel's name for a while (🔬 ~30 days). Switched to spaced names.

**3.3 Create the standard channels and rename the third**

```text
workiq create_entity POST /teams/{t}/channels {"displayName":"Partner Fabrikam","membershipType":"standard"}
workiq create_entity POST /teams/{t}/channels {"displayName":"Warranty Policy Updates","membershipType":"standard"}
workiq update_entity /teams/{t}/channels/19:pa0gYhAX… {"displayName":"Field Escalations"}
```

Creates the two channels and gives all three consistent names.

<details><summary><strong>Captured output</strong></summary>

```text
Partner Fabrikam         201  19:a8344ee1fb54414d98aef124ae27627e@thread.tacv2
Warranty Policy Updates  201  19:2b6fa5f0482b434da9bced8da3a0c1e7@thread.tacv2
Field Escalations        204  (renamed)
```

</details>

**Outcome:** ✅ Three standard channels.

**3.4 Align the generator with the new names**

```powershell
.\.venv\Scripts\python.exe build\gen_teams.py
```

Regenerates `out/teams/` with spaced channel names. The filenames keep their hyphens.

<details><summary><strong>Captured output</strong></summary>

```text
  Field Escalations           6 threads  20 messages  (6 carry a designed trap)
  Warranty Policy Updates     5 threads   5 messages  (5 carry a designed trap)
  Partner Fabrikam            3 threads   6 messages  (1 carry a designed trap)
31 messages across 3 channels written to ...\out\teams
```

</details>

**Outcome:** ✅ The diff is one `channel` line per JSON file.

**3.5 Build the posting plan**

```powershell
# python: out/teams/*.json -> teams-post-plan.json; oldest thread first;
# author + date rendered in bold; assert "carries"/"trap" absent from every payload
```

Produces the exact message bodies and fails if a trap label would leak.

<details><summary><strong>Captured output</strong> (trimmed)</summary>

```text
14 threads, 31 messages
 0 Field Escalations   replies=3  4000-series hydraulic failures — anyone else seeing this?
 4 Field Escalations   replies=4  C-2026-04141 — Litware Pune, hydraulic pump, labour over flat rate
 6 Partner Fabrikam    replies=1  Parts supersession — P-44120
 9 Warranty Policy Updates replies=0  TSB-C-0043 published
 ...
```

</details>

**Outcome:** ✅ No trap labels in any payload.

**3.6 Post the messages** — 14 thread starters, then 17 replies, posted one round at a time so each thread stays in order.

```text
workiq create_entity POST /teams/{t}/channels/{c}/messages
{"subject":"TSB-C-0043 published","body":{"contentType":"html",
 "content":"<p><b>Anjali Rao (Warranty Operations Head)</b> · 12 Nov 2025, 10:15</p><p>TSB-C-0043 is live. …</p>"}}
workiq create_entity POST /teams/{t}/channels/{c}/messages/{root-id}/replies   {...}
```

Posts as the signed-in user. The original author and date are written into the message text.

<details><summary><strong>Captured output</strong> (first post, trimmed)</summary>

```json
{"id":"1791005174597","subject":"TSB-C-0043 published","messageType":"message",
 "from":{"user":{"displayName":"Srikantan Sankaran"}},"createdDateTime":"2026-10-03T05:26:14.597Z"}  statusCode 201
```

</details>

**Outcome:** ✅ 31/31 returned 201.

**3.7 Read back from Teams**

```text
workiq fetch /teams/{t}/channels/{c}/messages?$top=20&$expand=replies   (x3)
```

Counts what Teams actually stored and scans for leaked labels.

<details><summary><strong>Captured output</strong></summary>

```text
Field Escalations        threads=6 replies=14 total=20 leak=False
Warranty Policy Updates  threads=5 replies=0  total=5  leak=False
Partner Fabrikam         threads=3 replies=3  total=6  leak=False
membershipType: standard x3
```

</details>

| Discovered | Inferred | Gate |
| --- | --- | --- |
| A deleted channel's name can't be reused straight away · every post shows the signed-in user as author and today's date | 💭 Trap 11 depends on *who* approved, so the author has to be in the message text, not in the Teams sender field | ✅ 20 + 5 + 6 = 31 read back · 0 leaks · all standard |

---

### P4 — Azure SQL · 2026-10-03

**4.1 Locate the server**

```powershell
az sql server list --query "[?fullyQualifiedDomainName=='az-sqldb-common.database.windows.net'].{rg:resourceGroup,loc:location,adOnly:administrators.azureAdOnlyAuthentication}"
```

Finds the resource group and the authentication mode.

<details><summary><strong>Captured output</strong></summary>

```json
[{"adOnly": true, "admin": "sansri_microsoft.com#EXT#@fdpo.onmicrosoft.com",
  "loc": "swedencentral", "name": "az-sqldb-common", "rg": "az-sqldb-common-rg"}]
```

</details>

**Outcome:** ✅ Entra-only server — no SQL logins, so the deploy guide's password steps don't apply. Client IP was already allowed by an existing firewall rule.

**4.2 Create the serverless database**

```powershell
az sql db create -g az-sqldb-common-rg -s az-sqldb-common -n contoso-warranty `
  --edition GeneralPurpose --compute-model Serverless --family Gen5 --capacity 1 `
  --min-capacity 0.5 --auto-pause-delay 60 --backup-storage-redundancy Local
```

Serverless General Purpose, 0.5–1 vCore, pauses after 60 minutes idle.

<details><summary><strong>Captured output</strong></summary>

```json
{"autoPause": 60, "max": 34359738368, "min": 0.5, "name": "contoso-warranty", "sku": "GP_S_Gen5", "status": "Online"}
```

</details>

**Outcome:** ✅ Online.

**4.3 Load schema and seed** — no `sqlcmd` or `pyodbc` was available, so Windows PowerShell's built-in SqlClient was used with an Entra token.

```powershell
$tok = az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv
# load-sql.ps1 (Windows PowerShell 5.1):
#   SqlConnection(...Database=contoso-warranty...) ; .AccessToken = $tok ; .Open()
#   split out/db/seed.azuresql.sql on ^GO$ ; ExecuteNonQuery per batch ; stop on first error
```

`seed.azuresql.sql` drops and recreates all 11 tables, then inserts every row.

<details><summary><strong>Captured output</strong></summary>

```text
OK: 8 batches executed
```

</details>

**Outcome:** ✅ Loaded.

**4.4 Compare with the local build**

```powershell
# Azure: sys.partitions row counts + trap queries ; local: sqlite3 out\db\contoso.db
```

Every table's count and both trap markers, Azure against SQLite.

<details><summary><strong>Captured output</strong></summary>

```text
AZ Assets=117            LITE Assets=117
AZ AssetTelemetry=2989   LITE AssetTelemetry=2989
AZ Claims=90             LITE Claims=90
AZ ServiceHistory=89     LITE ServiceHistory=89
AZ Parts=14 · Dealers=4 · GoodwillAuthority=4 · TsbApplicability=4      (same in LITE)
AZ ClaimAdjudicationDraft=0 · EvidenceRequest=0 · GoodwillEscalation=0  (same in LITE)
TRAP1 TSB-C-0051 serial_to=1500   (LITE 1500)
TRAP12 null commissioning=3       (LITE 3)
```

</details>

| Discovered | Inferred | Gate |
| --- | --- | --- |
| Entra-only server · no SQL client tools installed | 💭 The design target in 03 § 13 (e.g. 120 assets) differs from the generated counts (117). The generated counts are the truth | ✅ 11/11 tables equal · trap 1 = 1500 · trap 12 = 3 |

---

### P5 — MCP server on Azure Container Apps · 2026-10-03

**5.1 Build the image in ACR**

```powershell
az acr build -r pcdotaiagentd10b5a -t contoso-service-mcp:v1-1c30b85 -t contoso-service-mcp:latest --platform linux/amd64 mcp --no-logs
```

Builds `mcp/Dockerfile` in the cloud, so nothing runs locally.

<details><summary><strong>Captured output</strong></summary>

```text
Sending context (29.780 KiB) to registry: pcdotaiagentd10b5a...
Queued a build with ID: ct30
tags: latest, v1-1c30b85
```

</details>

**Outcome:** ✅ Pushed.

**5.2 Create the Container App with a managed identity**

```powershell
az containerapp create -g pcdotai-agent -n contoso-service-mcp --environment pcdotai-agent `
  --image pcdotaiagentd10b5a.azurecr.io/contoso-service-mcp:v1-1c30b85 `
  --registry-server pcdotaiagentd10b5a.azurecr.io --registry-identity system --system-assigned `
  --target-port 8000 --ingress external --min-replicas 1 --max-replicas 3 --cpu 0.5 --memory 1.0Gi `
  --env-vars "AZURE_SQL_CONNECTION_STRING=<ODBC, no password>" "AZURE_SQL_USE_MANAGED_IDENTITY=true"
```

A system-assigned identity pulls the image and logs in to SQL. There are no secrets.

<details><summary><strong>Captured output</strong></summary>

```json
{"fqdn": "contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io",
 "principal": "8d54c7a6-667a-4011-8c52-fc630d1bdfd2", "revision": "contoso-service-mcp--0000001", "state": "Succeeded"}
```

</details>

**Outcome:** ⚠️ Provisioned, but `/healthz` never answered.

**5.3 Fix 1 — crash on start**

```powershell
az containerapp logs show -g pcdotai-agent -n contoso-service-mcp --type console --tail 40
```

<details><summary><strong>Captured output</strong></summary>

```text
ModuleNotFoundError: No module named 'mcp.server.fastmcp'. This is mcp 2.x, where FastMCP was renamed ...
or pin 'mcp<2' to keep running v1 code.
```

</details>

**Outcome:** ✅ Pinned `mcp>=1.2.0,<2` in `mcp/requirements.txt` → rebuilt as `v2-…` → revision healthy.

**5.4 Fix 2 — `Invalid Host header` on every `/mcp` call**

```powershell
az acr build ... -t contoso-service-mcp:v3-1c30b85-hosts mcp
az containerapp update -g pcdotai-agent -n contoso-service-mcp --image ...:v3-1c30b85-hosts `
  --set-env-vars "MCP_ALLOWED_HOSTS=contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io"
```

The SDK's DNS-rebinding check accepts only `localhost`. `server.py` now reads an allow-list from `MCP_ALLOWED_HOSTS`.

**Outcome:** ✅ Revision `--0000003` is healthy and taking 100% of traffic.

**5.5 Give the identity database access**

```sql
DECLARE @sid varbinary(16) = CAST(CAST('7fc1bdfd-95af-4c4b-bbeb-82203b1300b1' AS uniqueidentifier) AS varbinary(16));
DECLARE @stmt nvarchar(400) = N'CREATE USER [contoso-service-mcp] WITH SID = ' + CONVERT(varchar(34), @sid, 1) + N', TYPE = E';
EXEC(@stmt);
ALTER ROLE db_datareader ADD MEMBER [contoso-service-mcp];
ALTER ROLE db_datawriter ADD MEMBER [contoso-service-mcp];
```

Creates the user from the identity's app id. Using the SID means the server needs no directory lookup.

<details><summary><strong>Captured output</strong></summary>

```text
contoso-service-mcp | EXTERNAL_USER | db_datareader
contoso-service-mcp | EXTERNAL_USER | db_datawriter
```

</details>

**Outcome:** ✅ Two syntax errors on the way (`Join-String` is missing in PS 5.1; `EXEC()` can't take a function call), both fixed.

**5.6 Call all 12 tools over `/mcp`**

```powershell
# mcp-probe.ps1: initialize -> notifications/initialized -> tools/call x13 (incl. one unknown claim)
```

Calls every tool with real inputs. The 3 action tools are aimed at claim C-2026-04114.

<details><summary><strong>Captured output</strong> (trimmed)</summary>

```text
/healthz -> {"status":"ok","assets":117}   server: contoso-service 1.30.0   tools: 12
get_asset                  isError=False  2638ms
get_running_hours          isError=False   612ms | as_of_date 2026-06-04, running_hours 4120
get_service_history        isError=False   594ms
find_prior_claims          isError=False   599ms
get_claim                  isError=False   605ms
get_dealer                 isError=False   587ms | Fabrikam, INR, uplift 0.0
lookup_part                isError=False  1111ms | P-44120 superseded_by P-44120-A
get_tsb_index              isError=False   584ms | TSB-C-0051 serial_to 1500 + authority_warning
get_goodwill_authority     isError=False  2269ms | 60000 INR -> tier 2, Regional Service Manager
create_claim_adjudication  isError=False  1117ms | ADJ-9CA93DB134
request_missing_evidence   isError=False  1585ms | EVR-92F90BF41C, claim Held
escalate_goodwill          isError=False  3015ms | GWE-D1A06E6DB1
get_claim (unknown)        isError=False  2441ms | found:false
```

</details>

**5.7 Remove the test writes**

```sql
DELETE ... WHERE draft_id='ADJ-9CA93DB134' / request_id='EVR-92F90BF41C' / escalation_id='GWE-D1A06E6DB1';
UPDATE Claims SET status='Submitted' WHERE claim_id='C-2026-04114' AND status='Held';
```

<details><summary><strong>Captured output</strong></summary>

```text
BEFORE: drafts 1 · evid 1 · esc 1 · C-2026-04114 Held · non_submitted 1
rows affected: 4
AFTER:  drafts 0 · evid 0 · esc 0 · C-2026-04114 Submitted · non_submitted 0
```

</details>

| Discovered | Inferred | Gate |
| --- | --- | --- |
| `mcp` 2.x breaks the server · SDK host check · `/mcp/` redirects to plain HTTP · **`auth.py` is never called** · `test_tools.py` writes into the committed `contoso.db` | 💭 The open endpoint can contaminate a baseline, so check the action tables before every run (P6) | ✅ 12/12 tools · reads and writes via managed identity · DB restored to its seeded state |

---

### P7 — Pre-flight and world init · 2026-10-03

Plan from 03 § 11: provision a throwaway **dev** world, probe it, then commit the same file to **main**.

**7.1 Identity and token**

```powershell
frontier-tuning whoami; frontier-tuning check; frontier-tuning environments list -o json
```

Confirms who the CLI acts as, and that it's the same tenant as the SharePoint site and the Teams team.

<details><summary><strong>Captured output</strong> (trimmed)</summary>

```text
UPN        sansri@microsoft.com
Tenant     72f988bf-86f1-41af-91ab-2d7cd011db47
Expires    2026-10-03 12:43 UTC
✓ Token valid  (expires in 85 min)
environments: 2 x "Vendor Contract Renewal Review" (earlier upstream exploration — untouched)
```

</details>

**Outcome:** ✅ Same tenant as the content. Token valid.

**7.2 World definition** — [`world/env.md`](../../world/env.md), written from the 0.3.16 `init-md` template.

| Section | Content |
| --- | --- |
| Instructions | Two neutral sentences. **No rubric wording**, because they stay constant through every stage |
| `OneDriveAndSharePoint` | `…/teams/ContosoFieldService/Warranty%20Operations` |
| `TeamsMessages` | The 3 standard channel URLs from P3 |

**7.3 Provision dev**

```powershell
$devId = [guid]::NewGuid().ToString(); "DEV_AGENT_ID=$devId"
frontier-tuning environments init --file world\env.md --agent-id $devId --name "Contoso Warranty Operations (wce-dev)" --output json
```

Creates the world from `world/env.md` under an agent ID generated beforehand, so the ID is known even if the call fails. `--name` overrides the file's name.

<details><summary><strong>Captured output</strong></summary>

```text
DEV_AGENT_ID=6bec3bf9-0222-4285-8a5b-214867ac42cc
{
  "IsWorkspaceReady": true,
  "DebugContext": {
    "Logs": []
  }
}
```

</details>

**Outcome:** ✅ Provisioned. That proves nothing about the URLs (CLI trap 3), so 7.3b checks them.

**7.3b What dev registered**

```powershell
$e = '6bec3bf9-0222-4285-8a5b-214867ac42cc'
frontier-tuning knowledge list --env-id $e -o json 2>&1 | Set-Content "$env:TEMP\wce-dev-knowledge.json"
$k = Get-Content "$env:TEMP\wce-dev-knowledge.json" -Raw | ConvertFrom-Json
$items = if ($k.value) { $k.value } else { $k }
$items | ForEach-Object { [pscustomobject]@{ type=$_.type; displayName=$_.displayName; siteId=$_.sharepointIds.siteId; listId=$_.sharepointIds.listId; all=$_.isAllItemsIncluded; url=($_.url, $_.webUrl | Where-Object { $_ } | Select-Object -First 1) } } | Format-List
```

Lists the knowledge sources the world registered from `env.md`, keeping only the fields that show whether each one resolved.

<details><summary><strong>Captured output</strong></summary>

```text
type        : folder
displayName : Warranty Operations
siteId      :
listId      :
all         : False
url         : https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty%20Operations

type        : teamsMessage
displayName : Field Escalations
siteId      :
listId      :
all         : False
url         : https://teams.microsoft.com/l/channel/19%3Apa0gYhAXW0BXkOG7tu7BNf7CcITOssLeL63nB7uhoRM1%40thread.tacv2/Fi
              eld%20Escalations?groupId=1d67f268-f548-46ec-b5d0-ce84dc68e032&tenantId=72f988bf-86f1-41af-91ab-2d7cd011d
              b47

type        : teamsMessage
displayName : Warranty Policy Updates
siteId      :
listId      :
all         : False
url         : https://teams.microsoft.com/l/channel/19%3A2b6fa5f0482b434da9bced8da3a0c1e7%40thread.tacv2/Warranty%20Pol
              icy%20Updates?groupId=1d67f268-f548-46ec-b5d0-ce84dc68e032&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47

type        : teamsMessage
displayName : Partner Fabrikam
siteId      :
listId      :
all         : False
url         : https://teams.microsoft.com/l/channel/19%3Aa8344ee1fb54414d98aef124ae27627e%40thread.tacv2/Partner%20Fabr
              ikam?groupId=1d67f268-f548-46ec-b5d0-ce84dc68e032&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47
```

</details>

**Outcome:** ✅ All 4 names resolved. ⚠️ `siteId` and `listId` are empty, which the CLI reference says *may* mean a source did not resolve. 7.3c checks that.

**7.3c Compare with a world where retrieval is known to work**

```powershell
frontier-tuning knowledge list --env-id 2dc7f43b-d807-4853-bff5-db8f951209ef -o json 2>&1 | ConvertFrom-Json | ForEach-Object { $i = if ($_.value) { $_.value } else { $_ }; $i } | ForEach-Object { "{0} | {1} | siteId='{2}' listId='{3}'" -f $_.type, $_.displayName, $_.sharepointIds.siteId, $_.sharepointIds.listId }
```

The same check, run on the earlier contract-renewal world.

<details><summary><strong>Captured output</strong></summary>

```text
folder | Contracts | siteId='' listId=''
folder | Spend | siteId='' listId=''
teamsMessage | rle-contract-renewal | siteId='' listId=''
```

</details>

**Outcome:** ✅ Same empty IDs there, so empty IDs are normal for `items_by_url` sources.

**7.4 Model lists**

```powershell
$e = '6bec3bf9-0222-4285-8a5b-214867ac42cc'
frontier-tuning models list --env-id $e -o json 2>&1
```

Re-reads which models can be evaluated and which can be tuned.

<details><summary><strong>Captured output</strong></summary>

```json
{
  "TrainingModels": [
    {
      "Id": "prod-gpt-56-reasoning-sol",
      "Name": "GPT-5.6-Sol",
      "BaseModel": "GPT-5.6-Sol",
      "DisplayName": "GPT-5.6-Sol",
      "IsFineTuned": false,
      "IsSelected": true
    },
    {
      "Id": "dev-ct-gpt-54-mini-mp",
      "Name": "GPT-5.4-Mini",
      "BaseModel": "GPT-5.4-Mini",
      "DisplayName": "GPT-5.4-Mini",
      "IsFineTuned": false,
      "IsSelected": false
    },
    {
      "Id": "dev-ct-mai-code-mp",
      "Name": "MAI-CODE-5b",
      "BaseModel": "DEV-CT-MAI-CODE-MP",
      "DisplayName": "MAI-CODE-5b",
      "IsFineTuned": false,
      "IsSelected": false
    }
  ],
  "EvaluationModels": [
    {
      "Id": "prod-gpt-56-reasoning-sol",
      "Name": "GPT-5.6-Sol",
      "BaseModel": "GPT-5.6-Sol",
      "DisplayName": "GPT-5.6-Sol",
      "IsFineTuned": false,
      "IsSelected": true
    },
    {
      "Id": "dev-ct-gpt-54-mini-mp",
      "Name": "GPT-5.4-Mini",
      "BaseModel": "GPT-5.4-Mini",
      "DisplayName": "GPT-5.4-Mini",
      "IsFineTuned": false,
      "IsSelected": false
    },
    {
      "Id": "dev-ct-mai-code-mp",
      "Name": "MAI-CODE-5b",
      "BaseModel": "DEV-CT-MAI-CODE-MP",
      "DisplayName": "MAI-CODE-5b",
      "IsFineTuned": false,
      "IsSelected": false
    }
  ],
  "SearchModels": [],
  "FTBaseModels": [
    {
      "Id": "gpt-54-mini",
      "Name": "GPT-5.4-Mini",
      "BaseModel": "GPT-5.4-Mini",
      "DisplayName": null,
      "IsFineTuned": false,
      "IsSelected": false
    },
    {
      "Id": "mai-code-1-flash",
      "Name": "MAI-Code-1-Flash",
      "BaseModel": "MAI-Code-1-Flash",
      "DisplayName": null,
      "IsFineTuned": false,
      "IsSelected": false
    }
  ],
  "DebugContext": {
    "Logs": []
  }
}
```

</details>

**Outcome:** ✅ The frontier model for stages 0–3 is still available and is the default. A new `EvaluationModels` list mirrors `TrainingModels`.

**7.5 Retrieval probes on dev** — one per source type, frontier model, `--strategy simple`. The content was 5.5 h old.

```powershell
$e = '6bec3bf9-0222-4285-8a5b-214867ac42cc'; $d = '<session folder>'
frontier-tuning chat --env-id $e -q "What serial range does bulletin TSB-C-0051 cover, and what coverage does it extend?" --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content "$d\p7-probe-sharepoint.json" -Encoding utf8
"sp exit=$LASTEXITCODE size=$((Get-Item "$d\p7-probe-sharepoint.json").Length)"
frontier-tuning chat --env-id $e -q "In the Field Escalations channel, what did Vikram Shetty say about claim C-2026-04141, and how did Meera Krishnan respond?" --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content "$d\p7-probe-teams.json" -Encoding utf8
"teams exit=$LASTEXITCODE size=$((Get-Item "$d\p7-probe-teams.json").Length)"
```

Proves the agent can actually *read* each source: the P10 test, run early to validate the URLs before main. The full JSON for each execution is saved.

<details><summary><strong>Captured output</strong></summary>

```text
sp exit=0 size=38774
teams exit=0 size=15808
```

</details>

Raw execution JSON (unedited): [`evidence/p7/p7-probe-sharepoint.json`](p7/p7-probe-sharepoint.json) · [`evidence/p7/p7-probe-teams.json`](p7/p7-probe-teams.json)

**7.5b What each probe did and answered**

```powershell
foreach ($f in 'p7-probe-sharepoint','p7-probe-teams') { $j = Get-Content "docs\evidence\p7\$f.json" -Raw | ConvertFrom-Json; "== $f  status=$($j.status)  exec=$($j.executionId)  $($j.startDateTime) -> $($j.endDateTime)"; $j.toolExecutions | ForEach-Object { $o = $_.Output | ConvertTo-Json -Depth 8 -Compress; $frd = if ($o -match '"FileRetrievalDetails":\[\]') { 'FileRetrievalDetails EMPTY' } elseif ($o -match 'FileRetrievalDetails') { 'FileRetrievalDetails non-empty' } else { '' }; "  {0} | {1} | {2} ms | {3} | inputs: {4}" -f $_.Title, $_.Status, $_.LatencyMs, $frd, (($_.Inputs | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join '; ') }; "  response:"; (($j.response | Out-String).Trim() -split "`n" | ForEach-Object { "    $_" }) }
```

Pulls the tool trace, the retrieval check and the answer out of the saved JSON.

<details><summary><strong>Captured output</strong></summary>

```text
== p7-probe-sharepoint  status=Completed  exec=0f7d98b5-cc5d-40ad-a646-68a51951ec84  10/03/2026 16:51:51 -> 10/03/2026 16:52:43
  m365__search_enterprise_files | Completed | 11165 ms | FileRetrievalDetails non-empty | inputs: searchQuery="TSB-C-0051"; from=0; size=10
  response:
    Bulletin **TSB-C-0051** covers the **4000-series industrial chiller** serial range **CIE-4000-CH-01200 through CIE-4000-CH-01850, inclusive**.

    For units in that range, it extends warranty coverage for the **hydraulic circuit and compressor** to **36 months from the commissioning date or 8,000 running hours, whichever occurs first**. The bulletin is effective from **January 15, 2026**, and its specified coverage takes precedence over the regional addendum and Global Warranty Policy.

    ## Sources

    1. `tsb-c-0051` [Technical Service Bulletin TSB-C-0051 — Extended coverage: 4000-series hydraulic circuit and compressor](<https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty Operations/02-Bulletins/TSB-C-0051 Extended coverage - 4000-series hydraulic circuit and compre.docx>)
== p7-probe-teams  status=Completed  exec=04bee64c-3338-490b-8c2a-a1cfe70540e0  10/03/2026 16:52:52 -> 10/03/2026 16:54:12
  teams__ListTeams | Completed | 2466 ms |  | inputs:
  teams__ListChannels | Completed | 2868 ms |  | inputs: teamId=1d67f268-f548-46ec-b5d0-ce84dc68e032; nextLink=
  teams__SearchTeamsMessages | Completed | 2786 ms |  | inputs: message=C-2026-04141; conversationId=19:pa0gYhAXW0BXkOG7tu7BNf7CcITOssLeL63nB7uhoRM1@thread.tacv2; top=25; nextLink=
  teams__get_channel_message | Completed | 3102 ms |  | inputs: teamId=1d67f268-f548-46ec-b5d0-ce84dc68e032; channelId=19:pa0gYhAXW0BXkOG7tu7BNf7CcITOssLeL63nB7uhoRM1@thread.tacv2; messageId=1791005263629; replyId=
  teams__ListChannelMessageReplies | Completed | 2785 ms |  | inputs: teamId=1d67f268-f548-46ec-b5d0-ce84dc68e032; channelId=19:pa0gYhAXW0BXkOG7tu7BNf7CcITOssLeL63nB7uhoRM1@thread.tacv2; messageId=1791005263629; maxReplies=50; nextLink=
  teams__get_channel_message | Completed | 2819 ms |  | inputs: teamId=1d67f268-f548-46ec-b5d0-ce84dc68e032; channelId=19:pa0gYhAXW0BXkOG7tu7BNf7CcITOssLeL63nB7uhoRM1@thread.tacv2; messageId=1791005263629; replyId=1791005324238
  teams__get_channel_message | Completed | 2877 ms |  | inputs: teamId=1d67f268-f548-46ec-b5d0-ce84dc68e032; channelId=19:pa0gYhAXW0BXkOG7tu7BNf7CcITOssLeL63nB7uhoRM1@thread.tacv2; messageId=1791005263629; replyId=1791005331391
  response:
    In the **Field Escalations** thread for **claim C-2026-04141**:

    - **Vikram Shetty** told Ravi to **cover the full amount** and said he would handle the paperwork. He added that this was the **third such issue at the site**, so it was **not the service partner’s fault**, and asked Meera to push the claim through.
    - **Meera Krishnan** replied that she **couldn’t authorize it based only on the Teams message**. She said **section 7.1 requires the authority to be recorded against the claim in the system**; if Vikram entered it there, she would process the claim the same day.

    ## Sources

    1. `vikram-reply` Result from <code>get_channel_message</code>
    2. `meera-reply` Result from <code>get_channel_message</code>
```

</details>

**Outcome:** ✅ Both answers correct. Each Teams author was taken from the bold author line in the message text, not from the poster, who is the signed-in user.

**7.6 Provision main**

```powershell
$mainId = [guid]::NewGuid().ToString(); "MAIN_AGENT_ID=$mainId"
frontier-tuning environments init --file world\env.md --agent-id $mainId --name "Contoso Warranty Operations (wce-main)" --output json 2>&1
"--- knowledge"
frontier-tuning knowledge list --env-id $mainId -o json 2>&1 | ConvertFrom-Json | ForEach-Object { if ($_.value) { $_.value } else { $_ } } | ForEach-Object { "{0} | {1}" -f $_.type, $_.displayName }
```

The same `env.md` as dev, so main inherits URLs already proven in 7.5. The second command lists what main registered.

<details><summary><strong>Captured output</strong></summary>

```text
MAIN_AGENT_ID=598fd1b0-36f1-402f-ba36-aa00c8a67cc4
{
  "IsWorkspaceReady": true,
  "DebugContext": {
    "Logs": []
  }
}
--- knowledge
folder | Warranty Operations
teamsMessage | Field Escalations
teamsMessage | Warranty Policy Updates
teamsMessage | Partner Fabrikam
```

</details>

**Outcome:** ✅ Provisioned, with the same 4 sources as dev.

**7.6b Built-in tools and the CLI default**

```powershell
frontier-tuning environments get --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json 2>&1 | ConvertFrom-Json | ForEach-Object { "name: $($_.Name ?? $_.DisplayName ?? $_.declarativeCopilot.name)"; $_.Tools | ForEach-Object { "  {0,-12} enabled={1}" -f $_.Name, $_.Enabled } }
frontier-tuning config show 2>&1 | Select-String -Pattern 'env'
```

Shows which built-in tool slots main has switched on, and which environment the CLI now uses by default.

<details><summary><strong>Captured output</strong></summary>

```text
name:
  fabriciq     enabled=False
  Me           enabled=True
  Word         enabled=False
  M365Chat     enabled=False
  SharePoint   enabled=True
  OneDrive     enabled=True
  Teams        enabled=True
  Calendar     enabled=False
  Email        enabled=False
│  env_id      │  598fd1b0-36f1-402f-ba36-aa00c8a67cc4  │
```

</details>

**Outcome:** ✅ SharePoint, OneDrive and Teams are on. `wce-main` is now the CLI default, because `init` saved it. `name:` is blank only because my field guess was wrong, not because the world has no name.

| Discovered | Inferred | Gate |
| --- | --- | --- |
| Indexing took < 5.5 h, not a day · `--strategy simple` accepted without error · the GPT-5.4-Mini pair shares `BaseModel: GPT-5.4-Mini`; the MAI pair doesn't (`DEV-CT-MAI-CODE-MP` vs `MAI-Code-1-Flash`) · Teams author attribution comes from the message text | 💭 The MAI pair may be **different models** (5b vs Flash), which would weaken stage 4 narrative A. GPT-5.4-Mini may allow a true before/after on one model — 🔬 the names alone prove nothing about the weights. 🔬 That `--strategy` was *accepted* doesn't prove it *took effect* — compare simple vs BestOfN results in stage 3 | ✅ Both worlds `IsWorkspaceReady` · 4/4 sources resolved by name · SharePoint and Teams retrieval correct on dev |

---

### P8 — MCP server registered in both worlds · 2026-10-03

`env.md` can't hold an MCP server: only SharePoint/OneDrive, Teams, Meetings and Graph connectors go there. Custom tools are added after `init` with `tools create`. P6 (Entra auth) isn't done, so the server is registered as `NoAuth` for now. 🔬 `tools upsert` should switch it to `AzureAD` later, at the same ID.

**8.1 Register on dev**

```powershell
frontier-tuning tools create --env-id 6bec3bf9-0222-4285-8a5b-214867ac42cc --name contoso-service --description "Contoso service claim system: asset registry, running-hours telemetry, service history, claims, partner master, parts, goodwill authority, and draft adjudication actions." --url https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/mcp --auth-scheme NoAuth -o json 2>&1
```

Registers the server with the world. The platform connects to it to check it works.

<details><summary><strong>Captured output</strong></summary>

```json
{
  "Id": "34d14238-fe93-48b5-ba70-3f3a949f6d64",
  "Type": "Custom",
  "Name": "contoso-service",
  "Description": "Contoso service claim system: asset registry, running-hours telemetry, service history, claims, partner master, parts, goodwill authority, and draft adjudication actions.",
  "Url": "https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/mcp",
  "IsMcpRemoteTool": true,
  "AuthenticationScheme": "NoAuth",
  "AudienceUrl": "api://none",
  "AnnotatedActions": [],
  "AdditionalHeaderNames": null,
  "Enabled": true,
  "DebugContext": {
    "Logs": []
  }
}
```

</details>

**Outcome:** ✅ Registered on dev.

**8.2 Did the platform discover the tools?**

```powershell
$e = '6bec3bf9-0222-4285-8a5b-214867ac42cc'
frontier-tuning tools status 34d14238-fe93-48b5-ba70-3f3a949f6d64 --env-id $e 2>&1
$raw = frontier-tuning tools available --env-id $e -o json 2>&1 | Out-String
[regex]::Matches($raw, '"Name":\s*"([^"]+)"') | ForEach-Object { $_.Groups[1].Value } | Where-Object { $_ -like '34d14*' }
```

`status` reports discovery. `available` is the list the agent is offered.

<details><summary><strong>Captured output</strong></summary>

```text
Tool: contoso-service
ID: 34d14238-fe93-48b5-ba70-3f3a949f6d64
Observed Callable Tools: 12
Discovery Status: observed
34d14__get_asset
34d14__get_running_hours
34d14__get_service_history
34d14__find_prior_claims
34d14__get_claim
34d14__get_dealer
34d14__lookup_part
34d14__get_tsb_index
34d14__get_goodwill_authority
34d14__create_claim_adjudication
34d14__request_missing_evidence
34d14__escalate_goodwill
```

</details>

**Outcome:** ✅ All 12 discovered. ⚠️ Tools are named `<first 5 chars of server id>__<tool>`, **not** `contoso-service__<tool>`. `tools list` doesn't show them at all (50 built-ins only). Use `tools available`.

**8.3 Can the agent use them? — first probe, before any fix**

```powershell
$e = '6bec3bf9-0222-4285-8a5b-214867ac42cc'
New-Item -ItemType Directory -Force -Path docs\evidence\p8 | Out-Null
frontier-tuning chat --env-id $e -q "What is the commissioning date of asset CIE-4000-CH-01700, and what are its running hours as of 18 June 2026?" --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content docs\evidence\p8\p8-probe-mcp-dev.json -Encoding utf8
"exit=$LASTEXITCODE size=$((Get-Item docs\evidence\p8\p8-probe-mcp-dev.json).Length)"
$j = Get-Content docs\evidence\p8\p8-probe-mcp-dev.json -Raw | ConvertFrom-Json; "== p8-probe-mcp-dev  status=$($j.status)  exec=$($j.executionId)  $($j.startDateTime) -> $($j.endDateTime)"; $j.toolExecutions | ForEach-Object { "  {0} | {1} | {2} ms | inputs: {3}" -f $_.Title, $_.Status, $_.LatencyMs, (($_.Inputs | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join '; ') }; "  response:"; (($j.response | Out-String).Trim() -split "`n" | ForEach-Object { "    $_" })
```

A question only the database can answer. Raw: [`evidence/p8/p8-probe-mcp-dev.json`](p8/p8-probe-mcp-dev.json)

<details><summary><strong>Captured output</strong></summary>

```text
exit=0 size=335715
== p8-probe-mcp-dev  status=Completed  exec=b3bf6b06-2a52-4f2b-90f1-69ad7980192f  10/03/2026 17:13:52 -> 10/03/2026 17:17:48
  m365__search_enterprise_files | Completed | 6984 ms | inputs: searchQuery="CIE-4000-CH-01700"; from=0; size=10
  m365__search_enterprise_files | Completed | 3047 ms | inputs: searchQuery="CIE-4000-CH-01700" commissioning; from=0; size=10
  m365__search_enterprise_files | Completed | 5976 ms | inputs: searchQuery=CIE-4000-CH-01700 commissioning date asset register; from=0; size=25
  mcp_SharePointRemoteServer__getSiteByPath | Completed | 7808 ms | inputs: hostname=microsoftapc.sharepoint.com; serverRelativePath=teams/ContosoFieldService
  mcp_SharePointRemoteServer__listLists | Completed | 9350 ms | inputs: siteId=microsoftapc.sharepoint.com,ee5fd16e-cda8-4f89-90ca-01b0d154b5b2,5fc7228e-1e45-42a3-86fe-f6b4894cd380; pageCursor=
  m365__search_enterprise_files | Completed | 3819 ms | inputs: searchQuery=asset registry commissioning records CIE 4000; from=0; size=25
  mcp_SharePointRemoteServer__listDocumentLibrariesInSite | Failed | 7345 ms | inputs: siteId=microsoftapc.sharepoint.com,ee5fd16e-cda8-4f89-90ca-01b0d154b5b2,5fc7228e-1e45-42a3-86fe-f6b4894cd380; pageCursor=
  mcp_SharePointRemoteServer__getDefaultDocumentLibraryInSite | Failed | 2589 ms | inputs: siteId=microsoftapc.sharepoint.com,ee5fd16e-cda8-4f89-90ca-01b0d154b5b2,5fc7228e-1e45-42a3-86fe-f6b4894cd380
  mcp_SharePointRemoteServer__getFileOrFolderMetadataByUrl | Completed | 10980 ms | inputs: fileOrFolderUrl=https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty%20Operations
  mcp_SharePointRemoteServer__getFolderChildren | Completed | 8249 ms | inputs: documentLibraryId=b!btFf7qjNiU-QygGw0VS1so4ix19FHqNChv72tIlM04CvSo4n6A1NQLAFuB7fhxAE; parentFolderId=root; pageCursor=
  mcp_SharePointRemoteServer__getFolderChildren | Completed | 8632 ms | inputs: documentLibraryId=b!btFf7qjNiU-QygGw0VS1so4ix19FHqNChv72tIlM04CvSo4n6A1NQLAFuB7fhxAE; parentFolderId=01DRFRACRXVLXBR6FWWBEY3ZURLRFCVIR4; pageCursor=
  mcp_SharePointRemoteServer__getFolderChildren | Completed | 9651 ms | inputs: documentLibraryId=b!btFf7qjNiU-QygGw0VS1so4ix19FHqNChv72tIlM04CvSo4n6A1NQLAFuB7fhxAE; parentFolderId=01DRFRACSWXW2KSRX3MBGY5ZSA2K6GGBPW; pageCursor=
  teams__SearchTeamsMessages | Completed | 2283 ms | inputs: message=CIE-4000-CH-01700; conversationId=; top=25; nextLink=
  m365__search_enterprise_files | Completed | 4808 ms | inputs: searchQuery="C-2026-04114"; from=0; size=25
  response:
    For asset **CIE-4000-CH-01700**:

    - **Commissioning date:** **Not recorded / unavailable in the asset registry.** The governing warranty policy says that when a commissioning record is absent, the commissioning certificate must be requested and neither the dispatch nor installation date may be substituted.
    - **Running hours as of 18 June 2026:** **4,120 hours**, recorded in the field inspection report on that date.
```

</details>

**Outcome:** ⛔ 14 calls, **zero** to the MCP server, and the answer is **wrong**: the database has 2024-04-04. A second probe that named "the service claim system" explicitly did the same. Raw: [`p8-probe-mcp-dev-explicit.json`](p8/p8-probe-mcp-dev-explicit.json).

**8.4 Server side during the probes**

```powershell
az containerapp logs show -g pcdotai-agent -n contoso-service-mcp --type console --tail 120 --format text 2>$null | Select-String -Pattern 'POST /mcp|GET /mcp|DELETE /mcp|tools/|healthz' | Select-Object -Last 40 | ForEach-Object { $_.Line }
```

Shows whether the platform reached the server at all.

<details><summary><strong>Captured output</strong></summary>

```text
2026-10-03T11:44:00.4077074Z stdout F INFO:     100.100.1.0:58240 - "POST /mcp HTTP/1.1" 200 OK
2026-10-03T11:44:00.6468856Z stdout F INFO:     100.100.1.0:58240 - "DELETE /mcp HTTP/1.1" 200 OK
2026-10-03T11:48:41.4043083Z stdout F INFO:     100.100.0.54:40322 - "POST /mcp HTTP/1.1" 200 OK
2026-10-03T11:48:41.6318255Z stdout F INFO:     100.100.0.54:40322 - "DELETE /mcp HTTP/1.1" 200 OK
```

</details>

**Outcome:** ⚠️ The platform connects once per execution. This log stream covers **one replica only**, which mattered: see 8.6.

**8.5 Register on main — fails**

```powershell
$m = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
frontier-tuning tools create --env-id $m --name contoso-service --description "Contoso service claim system: asset registry, running-hours telemetry, service history, claims, partner master, parts, goodwill authority, and draft adjudication actions." --url https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/mcp --auth-scheme NoAuth -o json 2>&1
```

The same command as 8.1, against main. Run twice, then a third time with `-v`.

<details><summary><strong>Captured output</strong> (verbose run trimmed)</summary>

```text
Error: API error (400): {"code": "ER05017", "message": "Failed to connect to the MCP server. Please verify the URL and try again."}
Transaction ID: 4c6b54e8-e5d7-9553-79c8-afd316c69791
Error: API error (400): {"code": "ER05017", "message": "Failed to connect to the MCP server. Please verify the URL and try again."}
Transaction ID: 17437392-50e6-a5b1-b0ee-bdac3088564a
[frontier-tuning.client] POST
https://substrate.office.com/KnowledgeGraph/api/v1.0/Workspaces/598fd1b0-36f1-402f-ba36-aa00c8a67cc4/McpServers
[frontier-tuning.client] Response status: 400
Error: API error (400): {"code": "ER05017", "message": "Failed to connect to the MCP server. Please verify the URL and
try again."}
Transaction ID: 46be0e5a-4ed1-898c-060b-700d10b1bf66
```

</details>

**Outcome:** ⛔ The same URL works for dev but fails for main. Meanwhile `/healthz` returned `200 {"status":"ok","assets":117}`.

**8.6 Why — server logs and replicas**

```powershell
az containerapp logs show -g pcdotai-agent -n contoso-service-mcp --type console --tail 300 --format text 2>&1 | Select-String -Pattern 'mcp|Processing|Error|Exception|Traceback' | Select-Object -Last 60 | ForEach-Object { $_.Line }
az containerapp replica list -g pcdotai-agent -n contoso-service-mcp --query "[].{name:name,created:properties.createdTime,state:properties.runningState}" -o table 2>$null
```

Shows what the platform sent during the failed attempts, and how many copies of the app are running.

<details><summary><strong>Captured output</strong> (trimmed — first two lines are log-stream connection notices)</summary>

```text
2026-10-03T11:53:39.9044193Z stdout F INFO:     100.100.1.0:37828 - "POST /mcp HTTP/1.1" 200 OK
2026-10-03T11:53:40.1344741Z stdout F INFO:     100.100.1.0:37828 - "DELETE /mcp HTTP/1.1" 200 OK
2026-10-03T11:54:22.7653766Z stdout F INFO:     100.100.0.54:60536 - "GET /mcp HTTP/1.1" 404 Not Found
2026-10-03T11:54:43.6903942Z stdout F INFO:     100.100.1.0:50242 - "GET /mcp HTTP/1.1" 404 Not Found
Name                                           Created               State
---------------------------------------------  --------------------  -------
contoso-service-mcp--0000003-5f6dc99bb4-cq7tx  2026-10-03T11:43:32Z  Running
contoso-service-mcp--0000003-5f6dc99bb4-hbq2g  2026-10-03T06:26:40Z  Running
```

</details>

**Outcome:** 💡 **Root cause.** A second replica started at 11:43:32. MCP sessions live in one replica's memory, so a request that lands on the other gets **404 "session not found"**. The platform reports that as "failed to connect", and during executions it gets no tools, which explains 8.3. Dev registered at 11:39, while only one replica was running.

**8.7 Fix — make the server stateless**

```python
# mcp/contoso_service_mcp/server.py
mcp = FastMCP(
    "contoso-service",
    transport_security=_transport_security(),
    stateless_http=True,
    ...
```

```powershell
.\.venv\Scripts\python.exe -m py_compile mcp\contoso_service_mcp\server.py; "compile exit=$LASTEXITCODE"
az acr build -r pcdotaiagentd10b5a -t contoso-service-mcp:v4-1c30b85-stateless -t contoso-service-mcp:latest --platform linux/amd64 mcp --no-logs -o none 2>&1 | Select-String 'Queued|error' ; "build exit=$LASTEXITCODE"
az containerapp update -g pcdotai-agent -n contoso-service-mcp --image pcdotaiagentd10b5a.azurecr.io/contoso-service-mcp:v4-1c30b85-stateless --query "{rev:properties.latestRevisionName,state:properties.provisioningState}" -o json 2>&1 | Where-Object { $_ -notmatch 'altered by|Running' }
```

With no sessions kept in memory, any replica can answer any request.

<details><summary><strong>Captured output</strong></summary>

```text
compile exit=0

WARNING: Queued a build with ID: ct33
build exit=0

{
  "rev": "contoso-service-mcp--0000004",
  "state": "Succeeded"
}
```

</details>

**8.8 Verify stateless behaviour**

```powershell
Start-Sleep 30
$base = 'https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/mcp'
$h = @{ Accept = 'application/json, text/event-stream' }
function Rpc($body) { Invoke-WebRequest $base -Method Post -Body $body -ContentType 'application/json' -Headers $h -UseBasicParsing -TimeoutSec 90 -MaximumRedirection 0 }
function Parse-Rpc($r) { $j = ($r.Content -split "`n" | Where-Object { $_ -like 'data:*' } | Select-Object -First 1) -replace '^data:\s*',''; if (-not $j) { $j = $r.Content }; $j | ConvertFrom-Json }
$r = Rpc '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}'
"initialize -> $($r.StatusCode)  mcp-session-id='$($r.Headers['mcp-session-id'])'  server=$((Parse-Rpc $r).result.serverInfo.name)"
$t = Parse-Rpc (Rpc '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'); "tools/list (no session) -> $(@($t.result.tools).Count) tools"
$c = Parse-Rpc (Rpc '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_asset","arguments":{"serial":"CIE-4000-CH-01700"}}}'); "get_asset -> isError=$($c.result.isError) $(($c.result.content[0].text -replace '\s+',' ').Substring(0,120))"
try { $g = Invoke-WebRequest $base -Method Get -Headers $h -UseBasicParsing -TimeoutSec 20 -MaximumRedirection 0; "GET -> $($g.StatusCode)" } catch { "GET -> $($_.Exception.Response.StatusCode.value__)" }
```

Calls the server the way the platform does, but sends no session header after `initialize`.

<details><summary><strong>Captured output</strong></summary>

```text
initialize -> 200  mcp-session-id=''  server=contoso-service
tools/list (no session) -> 12 tools
get_asset -> isError=False { "found": true, "serial": "CIE-4000-CH-01700", "family": "4000-CH", "dealer_id": "D-IN-01", "customer_name": "Litware M
```

</details>

**Outcome:** ✅ No session ID is issued, and every request stands alone. The final `GET` didn't return: it opened the standard event stream and held it, so I stopped the shell.

**8.9 Register on main, and re-run the 8.3 probe unchanged**

```powershell
$m = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
frontier-tuning tools create --env-id $m --name contoso-service --description "Contoso service claim system: asset registry, running-hours telemetry, service history, claims, partner master, parts, goodwill authority, and draft adjudication actions." --url https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/mcp --auth-scheme NoAuth -o json 2>&1
frontier-tuning tools status 1c171d49-7f85-4997-8126-ae20829a4dbf --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 2>&1
"-----"
$e = '6bec3bf9-0222-4285-8a5b-214867ac42cc'
frontier-tuning chat --env-id $e -q "What is the commissioning date of asset CIE-4000-CH-01700, and what are its running hours as of 18 June 2026?" --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content docs\evidence\p8\p8-probe-mcp-dev-rerun.json -Encoding utf8
"exit=$LASTEXITCODE size=$((Get-Item docs\evidence\p8\p8-probe-mcp-dev-rerun.json).Length)"
# + the 8.3 extraction one-liner, pointed at p8-probe-mcp-dev-rerun.json
```

Raw: [`evidence/p8/p8-probe-mcp-dev-rerun.json`](p8/p8-probe-mcp-dev-rerun.json). The probe output below came from the same extraction one-liner as 8.3.

<details><summary><strong>Captured output</strong> (trimmed — <code>tools create</code> JSON: Description, AnnotatedActions, AdditionalHeaderNames, DebugContext cut; identical to 8.1)</summary>

```text
{
  "Id": "1c171d49-7f85-4997-8126-ae20829a4dbf",
  "Type": "Custom",
  "Name": "contoso-service",
  "Url": "https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/mcp",
  "IsMcpRemoteTool": true,
  "AuthenticationScheme": "NoAuth",
  "AudienceUrl": "api://none",
  "Enabled": true,
  ...
}
Tool: contoso-service
ID: 1c171d49-7f85-4997-8126-ae20829a4dbf
Observed Callable Tools: 12
Discovery Status: observed
-----
exit=0 size=1888
== p8-probe-mcp-dev-rerun  status=Completed  exec=6e31f065-f2e7-4594-8cbc-e6b7aea39ec9  10/03/2026 17:30:56 -> 10/03/2026 17:31:49
  34d14__get_asset | Completed | 6933 ms | inputs: serial=CIE-4000-CH-01700
  34d14__get_running_hours | Completed | 3386 ms | inputs: serial=CIE-4000-CH-01700; as_of=2026-06-18
  response:
    Asset **CIE-4000-CH-01700** was commissioned on **4 April 2024**.

    Its latest recorded meter reading at or before **18 June 2026** was **4,120 running hours**, recorded on **4 June 2026**.

    ## Sources

    1. `asset` Result from <code>get_asset</code>
    2. `hours` Result from <code>get_running_hours</code>
```

</details>

**Outcome:** ✅ Main registered. The **same question** now takes 2 MCP calls instead of 14 searches, and the answer is **correct**.

**8.10 Switch it off in main for stage 0**

```powershell
$m = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
frontier-tuning tools disable 1c171d49-7f85-4997-8126-ae20829a4dbf --env-id $m 2>&1
frontier-tuning tools sources --env-id $m -o json 2>&1 | ConvertFrom-Json | ForEach-Object { if ($_.value) { $_.value } else { $_ } } | Where-Object { $_.Name -eq 'contoso-service' } | ForEach-Object { "{0} | {1} | Enabled={2} | Auth={3}" -f $_.Id, $_.Name, $_.Enabled, $_.AuthenticationScheme }
$raw = frontier-tuning tools available --env-id $m -o json 2>&1 | Out-String
$names = [regex]::Matches($raw, '"Name":\s*"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }
"main available total: $($names.Count)"; "names containing get_asset|get_tsb_index|escalate_goodwill: $(@($names | Where-Object { $_ -match 'get_asset|get_tsb_index|escalate_goodwill' }).Count)"
```

Stage 0's single condition: registered, but not offered to the agent.

<details><summary><strong>Captured output</strong></summary>

```text
Tool 1c171d49-7f85-4997-8126-ae20829a4dbf disabled.
1c171d49-7f85-4997-8126-ae20829a4dbf | contoso-service | Enabled=False | Auth=NoAuth
main available total: 125
names containing get_asset|get_tsb_index|escalate_goodwill: 0
```

</details>

**Outcome:** ✅ Main offers 125 tools: dev's 137 minus the 12. Dev stays **enabled** for probing.

**8.11 Baseline still clean**

```powershell
$s = @'
param($Token)
$cn = New-Object System.Data.SqlClient.SqlConnection("Server=tcp:az-sqldb-common.database.windows.net,1433;Database=contoso-warranty;Encrypt=True;Connection Timeout=90;")
$cn.AccessToken = $Token; $cn.Open(); $c = $cn.CreateCommand()
$c.CommandText = "SELECT (SELECT COUNT(*) FROM ClaimAdjudicationDraft) drafts, (SELECT COUNT(*) FROM EvidenceRequest) evidence, (SELECT COUNT(*) FROM GoodwillEscalation) escalations, (SELECT COUNT(*) FROM Claims WHERE status <> 'Submitted') non_submitted"
$r = $c.ExecuteReader(); $r.Read() | Out-Null; "drafts={0} evidence={1} escalations={2} non_submitted={3}" -f $r[0], $r[1], $r[2], $r[3]; $cn.Close()
'@
$p = '<session folder>\baseline-check.ps1'; Set-Content $p $s -Encoding UTF8
$tok = az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $p -Token $tok
```

Confirms the probes wrote nothing to the draft tables. This is the pre-run check from 03 § 13.

<details><summary><strong>Captured output</strong></summary>

```text
drafts=0 evidence=0 escalations=0 non_submitted=0
```

</details>

| Discovered | Inferred | Gate |
| --- | --- | --- |
| MCP servers are added by `tools create`, not `env.md` · callable names are `<5-char server id>__<tool>`, so the runbook's `contoso-service__…` and `Select-String contoso` checks need fixing (P11) · **the stateful MCP server broke under 2 replicas**: 404 on registration, and no tools offered during executions | 💭 8.3's "agent ignores the tools" was the replica bug, not tool selection — the 8.9 re-run, with no other change, used the tools at once. 💭 Any MCP server on a scale-out host should be stateless | ✅ Registered in dev (enabled) and main (**disabled**) · 12/12 discovered in each · agent answers correctly from the DB on dev · action tables 0/0/0/0 |

---

### Ad hoc — GPT-5.6 vs MAI, same question · 2026-10-03

Requested by the user. Not a stage, and not scored: no skill or rubric exists. Run on `wce-dev`, where the MCP server is enabled. MAI is `dev-ct-mai-code-mp` ("MAI-CODE-5b"), the only MAI model `chat` can run; `mai-code-1-flash` is tune-only.

**Expected** (`GROUND-TRUTH.md`, C-2026-04114): covered · governing TSB-C-0051 · expires 2027-04-04 or 8,000 h · 4,120 h at repair. Trap 1: the DB index says the bulletin ends at serial 1500, while the document says 1850.

**A1 Run both models**

```powershell
$e = '6bec3bf9-0222-4285-8a5b-214867ac42cc'
$q = "Is the hydraulic pump repair on claim C-2026-04114 covered under warranty? State the governing instrument and when that coverage expires. Do not record or change anything in the claim system."
New-Item -ItemType Directory -Force -Path docs\evidence\adhoc-model-compare | Out-Null
frontier-tuning chat --env-id $e -q $q --model prod-gpt-56-reasoning-sol --strategy simple --wait -o json 2>&1 | Set-Content docs\evidence\adhoc-model-compare\gpt56.json -Encoding utf8
"exit=$LASTEXITCODE size=$((Get-Item docs\evidence\adhoc-model-compare\gpt56.json).Length)"
# then identical, with --model dev-ct-mai-code-mp -> mai.json
```

<details><summary><strong>Captured output</strong></summary>

```text
exit=0 size=84962
exit=0 size=125341
```

</details>

Raw: [`gpt56.json`](adhoc-model-compare/gpt56.json) · [`mai.json`](adhoc-model-compare/mai.json)

**A2 What each did and answered**

```powershell
foreach ($n in 'gpt56','mai') { $raw = Get-Content "docs\evidence\adhoc-model-compare\$n.json" -Raw; $j = $raw.Substring($raw.IndexOf('{')) | ConvertFrom-Json
  $wall = ([datetime]$j.endDateTime - [datetime]$j.startDateTime).TotalSeconds; $t = @($j.toolExecutions); $sum = ($t | Measure-Object LatencyMs -Sum).Sum/1000
  "== $n  status=$($j.status)  exec=$($j.executionId)  $($j.startDateTime) -> $($j.endDateTime)  wall=$([int]$wall)s tools=$($t.Count) tool-time=$([int]$sum)s error=$($j.error)"
  "  billing: " + ($j.billingSummary | ConvertTo-Json -Compress)
  $t | ForEach-Object { "  {0} | {1} | {2} ms | inputs: {3}" -f $_.Title, $_.Status, $_.LatencyMs, (($_.Inputs | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join '; ') }
  "  response:"; (($j.response | Out-String).Trim() -split "`n" | ForEach-Object { "    $_" }) }
```

<details><summary><strong>Captured output</strong></summary>

```text
== gpt56  status=Completed  exec=432fd86b-6665-405f-8569-6dcd002d3683  10/03/2026 18:03:36 -> 10/03/2026 18:04:38  wall=62s tools=8 tool-time=42s error=
  billing: null
  34d14__get_claim | Completed | 3353 ms | inputs: claim_id=C-2026-04114
  34d14__get_asset | Completed | 4035 ms | inputs: serial=CIE-4000-CH-01700
  34d14__get_running_hours | Completed | 3318 ms | inputs: serial=CIE-4000-CH-01700; as_of=2026-06-18
  34d14__get_service_history | Completed | 3243 ms | inputs: serial=CIE-4000-CH-01700; months=24
  34d14__find_prior_claims | Completed | 4506 ms | inputs: serial=CIE-4000-CH-01700; component=hydraulic pump
  34d14__get_tsb_index | Completed | 4034 ms | inputs: family=null; serial=CIE-4000-CH-01700
  m365__search_enterprise_files | Completed | 8940 ms | inputs: searchQuery=TSB-C-0051; from=0; size=10
  m365__search_enterprise_files | Completed | 10122 ms | inputs: searchQuery=Global Warranty Policy; from=0; size=10
  response:
    **Yes — the hydraulic pump repair on claim C-2026-04114 is covered under warranty.**

    - The claim concerns a hydraulic-pump remove-and-replace repair performed on **18 June 2026** for asset **CIE-4000-CH-01700**.
    - The governing instrument is **Technical Service Bulletin TSB-C-0051, “Extended coverage — 4000-series hydraulic circuit and compressor,”** read with **Global Warranty Policy POL-WAR-4.2, clause 1.4** on precedence. The bulletin is current, covers hydraulic-circuit repairs for serials **CIE-4000-CH-01200 through CIE-4000-CH-01850 inclusive**, and therefore covers serial 01700. It takes precedence over the shorter India regional coverage period.
    - TSB-C-0051 extends coverage to **36 months from commissioning or 8,000 running hours, whichever occurs first**. The asset was commissioned on **4 April 2024**, so the time limit is **4 April 2027**.
    - At the repair date, the latest available reading was **4,120 hours as of 4 June 2026**, below the 8,000-hour limit. Thus, the repair was within both applicable limits.

    **Coverage expiry:** **4 April 2027, or upon reaching 8,000 running hours if that happens earlier.**

    The claim-system applicability index incorrectly shows this serial as outside the bulletin range. That does not alter the result: under POL-WAR-4.2 clause 1.4, the published bulletin document governs when it conflicts with the index.

    I did **not** record, update, or otherwise change anything in the claim system.

    ## Sources

    1. `claim` Result from <code>get_claim</code>
    2. `tsb` [TSB-C-0051 — Extended coverage: 4000-series hydraulic circuit and compressor](<https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty Operations/02-Bulletins/TSB-C-0051 Extended coverage - 4000-series hydraulic circuit and compre.docx>)
    3. `policy` [POL-WAR-4.2 — Contoso Industrial Global Warranty Policy v4.2](<https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty Operations/01-Policy/POL-WAR-4.2 Contoso Industrial Global Warranty Policy v4.2.docx>)
    4. `asset` Result from <code>get_asset</code>
    5. `hours` Result from <code>get_running_hours</code>
    6. `index` Result from <code>get_tsb_index</code>
== mai  status=Completed  exec=63081bc7-0f41-416e-b972-81151dd79f13  10/03/2026 18:04:59 -> 10/03/2026 18:06:25  wall=86s tools=9 tool-time=37s error=
  billing: {"inputTokens":115928,"outputTokens":435,"cacheCreationTokens":0,"cacheReadTokens":112640,"toolInvocations":8,"raiChecks":4,"infraSeconds":0,"orchestratorCpuSeconds":26.8072112,"totalTokens":116363}
  34d14__get_claim | Completed | 7386 ms | inputs: claim_id=C-2026-04114
  34d14__get_asset | Completed | 3270 ms | inputs: serial=CIE-4000-CH-01700
  34d14__get_running_hours | Completed | 3849 ms | inputs: serial=CIE-4000-CH-01700; as_of=2026-06-18
  34d14__get_service_history | Completed | 3377 ms | inputs: serial=CIE-4000-CH-01700; months=24
  34d14__find_prior_claims | Completed | 3849 ms | inputs: serial=CIE-4000-CH-01700; component=P-44120-A
  34d14__get_tsb_index | Completed | 3277 ms | inputs: family=4000-CH; serial=CIE-4000-CH-01700
  m365__search_enterprise_files | Completed | 4467 ms | inputs: searchQuery=TSB-C-0051; from=0; size=10
  m365__search_enterprise_files | Completed | 4204 ms | inputs: searchQuery=Global Warranty Policy 4000-CH hydraulic pump coverage commissioning running hours; from=0; size=10
  m365__search_enterprise_files | Completed | 3575 ms | inputs: searchQuery=C-2026-04114; from=0; size=10
  response:
    **Yes — the hydraulic pump repair on claim C-2026-04114 is covered under warranty.**

    - **Governing instrument:** **Technical Service Bulletin TSB-C-0051, “Extended coverage — 4000-series hydraulic circuit and compressor.”** It applies to 4000-series chillers in serial range **CIE-4000-CH-01200 through CIE-4000-CH-01850**, which includes this asset, **CIE-4000-CH-01700**. It extends hydraulic-circuit and compressor coverage to **36 months from commissioning or 8,000 running hours, whichever occurs first**. Under clause 1.4 of **POL-WAR-4.2**, this serial-specific bulletin takes precedence over the regional addendum and global-policy baseline.
    - **Coverage at the repair date:** The repair occurred on **18 June 2026**. The asset was commissioned on **4 April 2024**, and its latest reading at or before the repair was **4,120 hours**—within both the 36-month and 8,000-hour limits. The inspection report also records a seized hydraulic pump, no external impact damage, and 4,120 running hours.
    - **Expiration:** The time-based endpoint is **4 April 2027**. However, the coverage ends earlier if the asset reaches **8,000 running hours** before that date. Because the available reading is 4,120 hours, the exact future date on which the hours limit might be reached cannot yet be determined.

    The claim-system applicability index incorrectly says this serial is outside the bulletin range. That index is informational only; both TSB-C-0051 and policy clause 1.4 say the published bulletin governs when they conflict.

    I did **not** record or change anything in the claim system.

    ## Sources

    1. `tsb-c-0051` [TSB-C-0051 Extended coverage — 4000-series hydraulic circuit and compressor](<https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty Operations/02-Bulletins/TSB-C-0051 Extended coverage - 4000-series hydraulic circuit and compre.docx>)
    2. `pol-war-4-2` [POL-WAR-4.2 Contoso Industrial Global Warranty Policy v4.2](<https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty Operations/01-Policy/POL-WAR-4.2 Contoso Industrial Global Warranty Policy v4.2.docx>)
    3. `claim` Result from <code>get_claim</code>
    4. `asset` Result from <code>get_asset</code>
    5. `hours` Result from <code>get_running_hours</code>
    6. `inspection` [C-2026-04114 Inspection Report CIE-4000-CH-01700](<https://microsoftapc.sharepoint.com/teams/ContosoFieldService/Warranty Operations/06-ClaimEvidence/C-2026-04114 Inspection Report CIE-4000-CH-01700.docx>)
    7. `index` Result from <code>get_tsb_index</code>
```

</details>

**A3 GPT-5.6 token counts, then the baseline check**

```powershell
$raw = frontier-tuning executions get 432fd86b-6665-405f-8569-6dcd002d3683 --env-id 6bec3bf9-0222-4285-8a5b-214867ac42cc -o json 2>&1 | Out-String; $j = $raw.Substring($raw.IndexOf('{')) | ConvertFrom-Json; "gpt56 BillingSummary: " + ($j.BillingSummary | ConvertTo-Json -Compress)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $p -Token $tok    # baseline-check.ps1 from P8 step 8.11
```

`chat --wait` returned `billing: null` for GPT-5.6, so the counts were fetched from the execution record.

<details><summary><strong>Captured output</strong></summary>

```text
gpt56 BillingSummary: {"InputTokens":143361,"OutputTokens":1238,"CacheReadTokens":86016,"CacheCreationTokens":0,"TotalTokens":144599,"ToolInvocations":10.0,"RaiChecks":4.0,"InfraSeconds":0.0,"OrchestratorCpuSeconds":26.176876299999996}
drafts=0 evidence=0 escalations=0 non_submitted=0
```

</details>

| | GPT-5.6 (`prod-gpt-56-reasoning-sol`) | MAI (`dev-ct-mai-code-mp`) |
| --- | --- | --- |
| Covered? / instrument / expiry | ✅ Yes · TSB-C-0051 · 4 Apr 2027 or 8,000 h | ✅ Yes · TSB-C-0051 · 4 Apr 2027 or 8,000 h |
| Trap 1 (stale index) | ✅ Noticed, document followed, cites 1.4 | ✅ Noticed, document followed, cites 1.4 |
| Wrote to the DB? | No | No |
| Wall time | 62 s | 86 s |
| Tool calls (listed / billed) | 8 / 10 | 9 / 8 |
| MCP · knowledge calls | 6 · 2 | 6 · 3 (also read the inspection report) |
| Tokens in / out | 143,361 / 1,238 | 115,928 / 435 |

| Discovered | Inferred | Gate |
| --- | --- | --- |
| **First single run that used documents and the DB together.** Both models chose the same 6 MCP calls in the same order. MAI ran fine through `chat` and was 24 s slower | 💭 One easy question can't show a gap between the models — this is the *covered / precedence* slice, the easiest. 🔬 The response doesn't say which model served the call, so the comparison rests on the `--model` flag. 💭 The different token and tool patterns suggest two genuinely different models | n/a — ad hoc, not a prerequisite or stage |

---

### P9 — Stage-0 skill (verbatim) · 2026-10-03

**9.1 Template and help**

```powershell
frontier-tuning skills --help 2>&1 | Select-Object -Skip 0 -First 40; "-----"; frontier-tuning skills create --help 2>&1; "-----"; frontier-tuning skills generate-rubrics --help 2>&1
$f = "$env:TEMP\ft-skill-template.md"; frontier-tuning skills init-md --help 2>&1 | Select-Object -First 12; frontier-tuning skills init-md --output $f 2>&1; Get-Content $f
$f = "$env:TEMP\ft-skill-template.md"; frontier-tuning skills init-md --out-file $f --force 2>&1; Get-Content $f
```

The second line failed: `Error: No such option '--output'.` The correct flag is `--out-file`. Key help text: `generate-rubrics` *"Generate evaluation rubrics for a skill from its instructions"*; `create` is *"Idempotent by name … re-running create … with a name that already exists … updates that skill in place"*.

**9.2 Create on dev (rubrics generated)**

```powershell
New-Item -ItemType Directory -Force -Path docs\evidence\p9 | Out-Null
frontier-tuning skills create --file skills\warranty-assistant.md --env-id 6bec3bf9-0222-4285-8a5b-214867ac42cc -o json 2>&1 | Tee-Object -FilePath docs\evidence\p9\skill-create-dev.json
```

Raw: [p9/skill-create-dev.json](p9/skill-create-dev.json). Skill file at that point: `generateRubrics: true`.

```powershell
$j = Get-Content docs\evidence\p9\skill-create-dev.json -Raw | ConvertFrom-Json
"skill: $($j.Name)  id=$($j.Id)  rubrics=$(@($j.Rubrics).Count)"
```

```text
skill: warranty-assistant  id=8e9d12a2-b0a5-4683-95f1-b225ed9ade44  rubrics=5
```

**9.3 Create on main**

```powershell
frontier-tuning skills create --file skills\warranty-assistant.md --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json 2>&1 | Set-Content docs\evidence\p9\skill-create-main.json -Encoding utf8
"exit=$LASTEXITCODE"
$j = Get-Content docs\evidence\p9\skill-create-main.json -Raw | ConvertFrom-Json
"skill: $($j.Name)  id=$($j.Id)  enabled=$($j.Enabled)  version=$($j.Version)  rubrics=$(@($j.Rubrics).Count)  items=$(($j.Rubrics | ForEach-Object { @($_.ChecklistItems).Count } | Measure-Object -Sum).Sum)"
$i = 0; foreach ($r in $j.Rubrics) { $i++; "[$i] $($r.RubricName)  (importance=$($r.Importance), type=$($r.RubricType), items=$(@($r.ChecklistItems).Count))" }
```

```text
exit=0
skill: warranty-assistant  id=cf00d339-5217-4cd1-b390-cc0d911735da  enabled=True  version=1  rubrics=1  items=14
[1] Warranty adjudication answer requirements  (importance=critical, type=user_facing, items=14)
```

Raw: [p9/skill-create-main.json](p9/skill-create-main.json).

**9.4 Preview a regeneration on main (not applied)**

```powershell
frontier-tuning skills generate-rubrics cf00d339-5217-4cd1-b390-cc0d911735da --mode replace --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json 2>&1 | Set-Content docs\evidence\p9\generate-rubrics-preview-main-1.json -Encoding utf8
```

```text
exit=0
top-level: id, mode, changed, applied, generated_count, generation_was_empty, before_count, after_count, added, removed, rubrics
generated rubrics: 5
  - Warranty Decision Requirement Set  items=5
  - Requested Result Delivery  items=2
  - Warranty Adjudication Accuracy and Grounding  items=5
  - Decision Coherence and Actionability  items=5
  - Professional and Proportionate Communication  items=4
```

Raw: [p9/generate-rubrics-preview-main-1.json](p9/generate-rubrics-preview-main-1.json).

**9.5 Pin dev's set and apply it to main**

```powershell
$dev = Get-Content docs\evidence\p9\skill-create-dev.json -Raw | ConvertFrom-Json
$dev.Rubrics | ConvertTo-Json -Depth 10 | Set-Content skills\warranty-assistant.rubrics.json -Encoding utf8
$raw = frontier-tuning skills get cf00d339-5217-4cd1-b390-cc0d911735da --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json 2>&1 | Out-String
$main = $raw.Substring($raw.IndexOf('{')) | ConvertFrom-Json; $main.Rubrics = $dev.Rubrics
$main | ConvertTo-Json -Depth 12 | Set-Content "$env:TEMP\main-skill-payload.json" -Encoding utf8
frontier-tuning skills update cf00d339-5217-4cd1-b390-cc0d911735da --file "$env:TEMP\main-skill-payload.json" --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 -o json 2>&1 | Set-Content docs\evidence\p9\skill-update-main.json -Encoding utf8
```

```text
pinned rubrics: 5  items=28
main get fields: Id, TaskTemplateId, Name, Description, FormattedDescription, ShortDescription, Type, Rubrics, Prompt, Enabled, IsSkillSuggested, IsSkillEnriched, Knowledge, DebugContext
payload rubrics: 5
exit=0
main rubrics now: 5  items=28
identical to pinned (name, importance, type, items): True
  - Requested Outcome Delivery  (critical, user_facing, 6 items)
  - Claim Determination Requirements  (critical, user_facing, 5 items)
  - Internal Record Use and Grounding  (critical, trajectory_non_tool, 10 items)
  - Adjudicator-Ready Presentation and Traceability  (high, user_facing, 6 items)
  - Claim-System Draft Execution  (critical, trajectory_non_tool, 1 items)
prompt unchanged: True
```

Correction: an earlier chat message said 29 items. The count is 28.

**9.6 Final state**

```powershell
foreach ($e in '598fd1b0-36f1-402f-ba36-aa00c8a67cc4','6bec3bf9-0222-4285-8a5b-214867ac42cc') { "== $e"; frontier-tuning skills list --env-id $e -o json 2>&1 | ConvertFrom-Json | ForEach-Object { if ($_.value) { $_.value } else { $_ } } | ForEach-Object { "  {0} | {1} | enabled={2} | rubrics={3}" -f $_.Id, $_.Name, $_.Enabled, @($_.Rubrics).Count } }
```

```text
== 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
  cf00d339-5217-4cd1-b390-cc0d911735da | warranty-assistant | enabled=True | rubrics=5
== 6bec3bf9-0222-4285-8a5b-214867ac42cc
  8e9d12a2-b0a5-4683-95f1-b225ed9ade44 | warranty-assistant | enabled=True | rubrics=5
```

The skill file was then switched to `generateRubrics: false`, with a comment pointing to the pinned JSON.

---

### Correction · 2026-10-03 21:10 — `tools list` is paged, not filtered

P8 step 8.2 said *"`tools list` doesn't show them at all (50 built-ins only)"*. **That was wrong.** `tools list` defaults to 50 results.

```powershell
$m = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
foreach ($cmd in 'list','available') {
  $raw = frontier-tuning tools $cmd --env-id $m -o json 2>&1 | Out-String
  $names = [regex]::Matches($raw, '"Name":\s*"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }
  "tools $cmd -> $($names.Count) tools: " + (($names | ForEach-Object { ($_ -split '__')[0] } | Group-Object | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join '  ')
  "   has m365__search_enterprise_files: $([bool]($names -contains 'm365__search_enterprise_files'))   has teams__SearchTeamsMessages: $([bool]($names -contains 'teams__SearchTeamsMessages'))"
}
$raw = frontier-tuning tools list --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4 --limit 500 -o json 2>&1 | Out-String
$raw = frontier-tuning tools list --env-id 6bec3bf9-0222-4285-8a5b-214867ac42cc --limit 500 -o json 2>&1 | Out-String
```

```text
tools list -> 50 tools: mcp_OneDriveRemoteServer=18  mcp_SharePointRemoteServer=31  teams=1
   has m365__search_enterprise_files: False   has teams__SearchTeamsMessages: False
tools available -> 125 tools: lumina_sandbox=9  m365=5  mcp_OneDriveRemoteServer=18  mcp_SharePointRemoteServer=31  polymer_atomic=17  teams=43  workspace_health=2
   has m365__search_enterprise_files: True   has teams__SearchTeamsMessages: True
tools list --limit 500 -> 125 tools: lumina_sandbox=9  m365=5  mcp_OneDriveRemoteServer=18  mcp_SharePointRemoteServer=31  polymer_atomic=17  teams=43  workspace_health=2
has m365__search_enterprise_files: True
dev: tools list --limit 500 -> 137 tools; our MCP tools (34d14__*): 12
```

---

### Note · 2026-10-04 — skill files moved to `stages/stage-0/`

`skills/warranty-assistant.md` and `skills/warranty-assistant.rubrics.json` were moved, unchanged, to `stages/stage-0/` so that every stage keeps its own artefacts. The commands above show the paths as they were run.

```powershell
New-Item -ItemType Directory -Force -Path stages\stage-0 | Out-Null
Move-Item skills\warranty-assistant.md stages\stage-0\warranty-assistant.md
Move-Item skills\warranty-assistant.rubrics.json stages\stage-0\warranty-assistant.rubrics.json
if (-not (Get-ChildItem skills -Force)) { Remove-Item skills }
```

Separately, `frontier-tuning versions skill list cf00d339-5217-4cd1-b390-cc0d911735da --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4` returned `Skill 'cf00d339-5217-4cd1-b390-cc0d911735da' was not found in this workspace.` The platform's skill version history doesn't cover this skill (🔬 why), so history is kept in the repo.
