# The Contoso warranty RLE: journey

How this world is built, where the climb stands, and what we learned on the way. **Where we are** is all you need on a return visit.

| Part | What it gives you |
| --- | --- |
| [1. The scenario](#1-the-scenario-in-two-minutes) | What the agent does, where its facts live, why it's hard, and how a run works |
| [2. Setting up the world](#2-setting-up-the-world) | The build recipe, step by step |
| [3. The climb](#3-the-climb) | The stages, one line each; detail in [stages/](../stages/README.md) |
| [4. What we've learned](#4-what-weve-learned) | Lessons, as issue → what we did |
| [5. Side experiments](#5-side-experiments) | Runs outside the climb |
| [Appendix](#appendix--helper-snippets) | Helper snippets |

Legend: ✅ done · ⬜ not started · 🖥️ measured here · 📄 upstream guidance · 🔬 unverified · 💭 reasoning. The full chronological record, with every dead end, is in [archive/](../archive/README.md) and [evidence/](evidence/README.md).

---

## Where we are

| | |
| --- | --- |
| **Status** | Stages 0–2 done on GPT-5.6-Sol: it saturates the world (0.978 · 27/30). **Stage 3** (MAI-CODE-5b, research split into its own skill, folder-scoped search) is ready to run in wce-main; trialled 6/6 correct in wce-dev. World **v2.3** |
| **Next** | Apply [stage 3](../stages/stage-3/README.md) to wce-main → smoke test 1 sample → 30 claims in 3 batches of 10 → three numbers (rubric, correct, hand-in rejections). Then rubrics v2 (stage 4) → headroom (stage 5) → RFT (stage 6) |
| **Open** | Hand-in rejections by the platform's finish tool ([note](evidence/platform-issue-finish-rejection.md)) · MAI-CODE-5b vs `mai-code-1-flash`: same weights? · does tuning use Training or Evaluation samples? · P6 endpoint auth deferred |
| **Worlds** | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` (the climb) · `wce-dev` `6bec3bf9-0222-4285-8a5b-214867ac42cc` (trials) |
| **Skills** | main: `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da` (stage 2 config) · dev: `warranty-assistant` `8e9d12a2-b0a5-4683-95f1-b225ed9ade44` + `library-research` `9db9be9a-f862-4444-a904-f63373f387fa` (stage 3 config) |
| **MCP server** | main `1c171d49-7f85-4997-8126-ae20829a4dbf` · dev `34d14238-fe93-48b5-ba70-3f3a949f6d64` · ACA pinned at 5 replicas · OneDrive slot off in both worlds |
| **Models** | Run: `prod-gpt-56-reasoning-sol`, `dev-ct-gpt-54-mini-mp`, `dev-ct-mai-code-mp` · Tune: `gpt-54-mini`, `mai-code-1-flash` |
| **Before every run** | SQL public access is switched off daily (SFI): re-enable it. Add your IP to the SQL firewall if it changed. `/healthz`, then `scripts\db-baseline.sql` = 0 0 0 0. Snapshot and reset after every run |

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

### How the agent reasons through a claim

There's no fixed reading list. **Which documents matter depends on facts found
along the way**, so the agent works in steps: each result decides the next lookup.

```
get_claim ─► get_asset ─┬─ commissioning missing? ──► STOP: request evidence            (abstention)
                        │
                        ├─ region ──► regional addendum (India 18 mo / EMEA …)
                        ├─ family + serial ──► a bulletin naming this serial?           (precedence, serial boundary)
                        │         └─ superseded? use the newer one; DB index disagrees? the document wins
                        ├─ repair date + running hours ──► within months AND hours?     (dual limit)
                        │
                        ├─ covered ──► flat-rate (op code) · labour rate (region, repair date)
                        │              · part fitted + supersession · partner agreement (uplift)   (valuation)
                        └─ not covered + goodwill asked ──► authority matrix · Teams thread ──► escalate  (authority)
```

**Who tells the agent this?** Not the skill. The **policy document**, POL-WAR-4.2 in `01-Policy`, does, just as a human adjudicator works from the manual. Finding and applying it is the competence being measured.

| Policy clause | So the agent must… |
| --- | --- |
| 1.4: a bulletin naming the serial range beats the regional addendum, which beats the policy; superseded bulletins have no effect; the document beats the DB index | Check the serial against the bulletins, *then* the region's addendum |
| 2.3: no commissioning record → coverage can't be determined; hold the claim; don't substitute the install date | **Stop** and request the record |
| Labour: flat-rate allowance or hours claimed, whichever is less, at the rate in force on the **repair date** | Read the flat-rate schedule *and* the rate card, choosing the row by repair date |
| 4.2: price the part *fitted*; a superseded part takes the new part's price | Check service history and the parts list |
| 7.1: approval needs recorded authority at the right tier | Use the authority matrix; a Teams "cover it" isn't approval |

**Paths by type of claim** (the slices in [GROUND-TRUTH.md](../out/GROUND-TRUTH.md)):

| Slice | Path, roughly | Typical hops |
| --- | --- | --- |
| covered-simple | claim → asset → hours → India addendum → flat-rate, rate card, parts, partner agreement | ~8–10 |
| precedence / serial-boundary | as above, **plus** find the bulletin by serial and follow the document over the DB index | ~10–12 |
| dual-limit | months *and* hours: telemetry at the repair date decides | ~8–10 |
| valuation | full money path: cap, rate by repair date, supersession, uplift | ~10–14 |
| stale-deck | as precedence, **discounting** the Q2 deck's "24 months" if search surfaces it | ~10 |
| authority | out of cover, goodwill asked → matrix → Teams → **escalate**, don't approve | ~6–8 |
| abstention | commissioning missing → policy 2.3 → **request evidence** and stop | ~4 |

🖥️ The coverage-only comparison question took **8 hops in sequence**: claim → asset → hours → history → prior claims → bulletin index → bulletin → policy. A full adjudication adds the money lookups. At 3–11 s per hop, that's why a run takes 1.5–3 minutes.

**Why it's built this way.** A single search can't answer a claim: the right
bulletin is only findable *after* the serial comes back, the right rate row
needs the repair date, and the distractors (stale deck, stale index, Teams
"approval") surface mid-research and must be discounted. Choosing the next step,
knowing when to stop and deciding which source wins are the habits the climb
measures and RFT reinforces.

For one claim walked end to end, step by step, see
[04-walkthrough.md](04-walkthrough.md) and [03 § 8](03-scenario-design.md#8-a-worked-example-end-to-end).

### How a run works

**One request; the world runs the agent.** A `chat` call, or each sample in an evaluation, is a single request. Inside the world:

1. A **top-level agent** reads the skill descriptions and calls the skill(s) it needs, in the order the descriptions suggest. Skills can't call each other; an unrelated request calls none.
2. Each skill runs as a **sub-agent with its own context**: its instructions plus every enabled tool (~118 here: MCP, SharePoint, Teams, M365 search…).
3. The model calls tools; each result is appended and the **whole history is re-sent** every turn.
4. It **hands in** through the platform's finish tool, which can reject a hand-in.
5. A **grader model** scores each skill's accepted hand-in against **that skill's** rubrics. The run's score is the adjudication skill's.

| Role | Model | Chosen by |
| --- | --- | --- |
| Agent (plans, calls tools, answers) | `--model` / `--base-model` | Us |
| Grader | Undisclosed platform model | Platform |
| Rubric generator (stage 0 only) | Platform model | Platform |

**What we can see:** `executions get` gives the successful tool calls, `Skills[]` (status and errors such as `ContextLength`), the rubric scores with the grader's reasoning, and token billing. Rejected hand-ins appear only in the grader's notes; the diagnostics API is blocked (403).

**Context budget.** A small model's window is the binding limit, not the task's complexity. Per run, GPT-5.6-Sol carried up to 386k characters of tool output; MAI-CODE-5b fails at ~230–275k. Design to stay well inside it: compact tool outputs (MCP < 1k each), folder-scoped searches, and work split across sub-agents.

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
| [P9](#p9--stage-0-skill-and-prompts) | Stage-0 skill and prompts | ✅ |
| [P10](#p10--prove-every-source-is-reachable) | Prove every source is reachable | ✅ dev · ✅ main (stage-0 probe) |
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
- `tools list` shows only the **first 50** tools by default, which hides ours. Use `tools list --limit 500` or `tools available`.
- `NoAuth` is temporary. P6 switches it to `AzureAD`.

✅ **Result:** connected in both worlds. Dev is on; main is **off**, which is stage 0's condition.

### P9 — Stage-0 skill and prompts

**Why.** Stage 0 needs one broad skill, with rubrics written by the platform
rather than by us. That's the naive baseline the climb starts from.

**Do.**
1. Write [stages/stage-0/warranty-assistant.md](../stages/stage-0/warranty-assistant.md). It describes the business job: who the agent serves, what an adjudication must establish, which sources exist, and how to write for an adjudicator. It deliberately leaves out the rules that solve the traps (which instrument wins, document over index, no install-date substitute, flat-rate cap, rate by repair date, written authority). The agent has to find those in the policy documents.
2. Create it on dev with `generateRubrics: true`, and review what the platform generates.
3. Pin the generated set in [warranty-assistant.rubrics.json](../stages/stage-0/warranty-assistant.rubrics.json) and apply it to main, so both worlds are scored against identical rubrics.

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
✅ **Prompts done:** 8 eval prompts in [stages/stage-0/stage0.jsonl](../stages/stage-0/stage0.jsonl): 3 covered-simple, 2 declined-simple, and 3 precedence (04114, 04116, 04118).

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

⬜ **Before stage 1.** Three updates to [runbook 05](05-hill-climb-runbook.md):
- Add AGENTS goals 3 (use the platform's own tools) and 4 (Simple vs BestOfN headroom).
- Correct the tool names to the `<id prefix>__<tool>` form.
- Stage 4: GPT-5.4-Mini first (4a), then repeat with MAI (4b). The runbook currently plans MAI only.

---
## 3. The climb

Each stage changes one thing and reports two numbers: the platform's **rubric score**, and **ground-truth correctness** (decision, governing instrument, payable; [`build/score_ground_truth.py`](#h5-score-answers-against-the-ground-truth)). The rubric score is the RFT reward, so if it climbs while correctness doesn't, the rubrics get fixed before tuning.

| Stage | Change | Model | Rubric | Correct | Takeaway |
| --- | --- | --- | --- | --- | --- |
| [0](../stages/stage-0/README.md) | Baseline: one skill, generated rubrics, claim system off, 8 prompts | GPT-5.6-Sol | 0.535 | 0/8 | Without claim facts the agent holds, and doesn't invent |
| [1](../stages/stage-1/README.md) | Claim system (MCP) on | GPT-5.6-Sol | 0.991 | 7/8 | Plumbing was the whole gap; saturated |
| [2](../stages/stage-2/README.md) | All 30 eval prompts | GPT-5.6-Sol | 0.978 | 27/30 | The frontier model handles every trap: no headroom |
| [3](../stages/stage-3/README.md) | MAI-CODE-5b; research split into its own skill; folder-scoped search | MAI-CODE-5b | ⬜ | ⬜ | Ready; 6/6 correct in the wce-dev trial |
| 4 | Hand-written rubrics (v2) for both skills | MAI-CODE-5b | | | |
| 5 | `Simple` vs `BestOfN`: headroom for tuning? | MAI-CODE-5b | | | |
| 6 | RFT on `mai-code-1-flash`, before and after | MAI | | | |

World versions v2–v2.3 (each fixing a defect a run exposed) are listed in [stages/README](../stages/README.md).

---

## 4. What we've learned

**The platform**

| Issue | What we did |
| --- | --- |
| Skills are sub-agents chosen by the top-level agent from their descriptions; one skill can't call another | Steer the order with descriptions ("Use this first…" / "expects the facts… gathered first") |
| Grading is per skill, by that skill's own rubrics; a skill without rubrics goes unmeasured | Rubrics for `library-research` drafted (v2) |
| The finish tool rejects some hand-ins: GPT-5.4-Mini 22/28; MAI 4/8 in one window. The user gets a correct answer, but the graded hand-in is a stub, and the skill re-runs and writes duplicate drafts | Reported ([note](evidence/platform-issue-finish-rejection.md)); removed a hand-in line from the skill (0/3 after); track the rejection rate per stage |
| `chat --wait` gives up at ~16 min while the run continues | Poll `executions get` until the status settles |
| `chat --skill-id` returns error 500 | Omit it; routing works |
| No per-skill model: `--model` applies to the whole run | One model per run |
| The tool set can change without notice (`m365__call_copilot` vanished; counts briefly read 88) | Record `tools available` before every run; re-read |
| Search returns large extracts (~18k characters) and the same "hub" documents (policy, review decks) for different queries | Scope each search to a folder: `path:"<library>/<folder>"` in the query |
| Search works on title and reference words; "rate card" and queries stuffed with identifiers return nothing | Search with the references the claim system returns, plus the kind of document |

**Measuring**

| Issue | What we did |
| --- | --- |
| The generated rubrics don't check correctness: wrong holds and a hedged escalation scored 1.0 | Ground truth reported every stage; hand-written rubrics (stage 4) before RFT |
| ~0.1 moves at 8 samples are noise | Judge on 30 prompts |
| The stored answer isn't always the delivered one (rejected hand-ins) | The scorer checks delivery; flagged answers are read by hand |
| The frontier model saturates this world | The climb continues on a small model |

**The world**

| Issue | What we did |
| --- | --- |
| Runs exposed four world defects: inspection reports, a seal-kit ambiguity, twin claims and an answer-key order, a missing prior claim | Each fixed in the generator, with a gate so it can't recur (v2–v2.3) |
| Our MCP tool descriptions state trap answers (e.g. "the bulletin document governs") | 🔬 Open: keep, or make the descriptions purely factual |

**Small models**

| Issue | What we did |
| --- | --- |
| GPT-5.4-Mini skipped documents, finished early, and its hand-ins were rejected | Skill guidance fixed the research order, not the hand-ins; moved to MAI |
| MAI's decisions were right, but it ran out of context on heavy claims | Split research into its own skill; folder-scoped search (610k → 57k on the heaviest claim) |
| MAI invented folder names when left to infer them | The folder map is given in a `## Library folders` section of each skill |
| Small-model runs re-send their context every turn: ~1–2.5 M input tokens per claim (Sol ~0.2–0.9 M) | Fewer turns, compact outputs; evaluate in batches of 10 |

**The environment**

| Issue | What we did |
| --- | --- |
| SQL public access is switched off daily; the client IP changes | Pre-flight check; single-IP firewall rule |
| MCP: `Invalid Host header`; `ER05017` with stateful sessions; no tools during scale-out | `MCP_ALLOWED_HOSTS`; `stateless_http=True`; replicas pinned |

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

*Updated for world v2.3 (10-06): the last count compares with the seeded status, since the `C-2026-03xxx` prior claims are seeded `Paid`.*

```powershell
$s = @'
param($Token)
$cn = New-Object System.Data.SqlClient.SqlConnection("Server=tcp:az-sqldb-common.database.windows.net,1433;Database=contoso-warranty;Encrypt=True;Connection Timeout=90;")
$cn.AccessToken = $Token; $cn.Open(); $c = $cn.CreateCommand()
$c.CommandText = "SELECT (SELECT COUNT(*) FROM ClaimAdjudicationDraft) drafts, (SELECT COUNT(*) FROM EvidenceRequest) evidence, (SELECT COUNT(*) FROM GoodwillEscalation) escalations, (SELECT COUNT(*) FROM Claims WHERE status <> CASE WHEN claim_id LIKE 'C-2026-03%' THEN 'Paid' ELSE 'Submitted' END) non_submitted"
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

### H5 Score answers against the ground truth

`build/score_ground_truth.py` compares each answer's **decision**, **governing
instrument** and **total payable** (approvals, ±₹1) with `out/data/claims.json`,
the source of `GROUND-TRUTH.md`. Extraction is pattern-based and repeatable,
with no model involved. Anything it can't read confidently is marked ❓ for a
human to check. It reads evaluation results, single executions, or folders of
either.

```powershell
frontier-tuning evaluate results <job-id> --samples --env-id <world-id> -o json > stages\stage-N\eval-results-samples.json
.\.venv\Scripts\python.exe build\score_ground_truth.py stages\stage-N\eval-results-samples.json --out stages\stage-N
cd build; ..\.venv\Scripts\python.exe test_score_ground_truth.py     # 18 extraction checks
```

Writes `ground-truth-check.md` (summary, by slice, per answer, alongside each
answer's rubric score) and `.csv`. 🖥️ Confirmed on stage 0: `--samples` is
required, since without it the file is only the summary. Answers are under
`Submissions[*].Execution`, with `Response` as a list of parts, which the scorer joins.
