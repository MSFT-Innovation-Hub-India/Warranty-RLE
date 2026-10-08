# The Contoso warranty RLE: journey

How this world is built, where the climb stands, and what we learned on the way. **Where we are** is all you need on a return visit.

| Part | What it gives you |
| --- | --- |
| [1. The scenario](#1-the-scenario-in-two-minutes) | What the agent does, where its facts live, why it's hard, and how a run works |
| [2. The world](#2-the-world) | Where the world lives, and where its build recipe is |
| [3. The climb](#3-the-climb) | The stages on world v3; detail in [stages/](../stages/README.md) |
| [4. What we carried from the first climb](#4-what-we-carried-from-the-first-climb) | The lessons from world v2 that shaped v3 |
| [Appendix](#appendix--helper-snippets) | Helper snippets |

Legend: ✅ done · ⬜ not started · 🖥️ measured here · 📄 upstream guidance · 🔬 unverified · 💭 reasoning. The verbatim record is in [evidence/](evidence/README.md).

---

## Where we are

| | |
| --- | --- |
| **Status** | **World v3** (one-call claim dossier, records only; one labour workbook). **Stage 0 closed:** MAI-CODE-5b with the naive skill and generated rubrics: rubric **0.744**, correct **23/30**, 0 overflows; 4 claims lost to echoed hand-ins |
| **Next** | Fix the scorer's 7 misreads → GPT-5.6-Sol reference run on stage 0's configuration → **stage 1**: hand-written rubrics (re-upload the 30 samples, which capture rubrics at upload) |
| **Open** | Hand-in rejections by the platform's finish tool ([note](evidence/platform-issue-finish-rejection.md)) · MAI-CODE-5b vs `mai-code-1-flash`: same weights? · does tuning use Training or Evaluation samples? · P6 endpoint auth deferred |
| **Worlds** | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` (the climb) · `wce-dev` `6bec3bf9-0222-4285-8a5b-214867ac42cc` (trials) |
| **Skill** | `warranty-assistant`: main `cf00d339-5217-4cd1-b390-cc0d911735da` · dev `8e9d12a2-b0a5-4683-95f1-b225ed9ade44`; one skill per world |
| **MCP server** | `contoso-service-mcp:v5-dossier-20261007-1646` · main `1c171d49-…` · dev `34d14238-…` · 5 replicas · OneDrive slot off · 110 tools |
| **Models** | Run: `dev-ct-mai-code-mp` (climb), `prod-gpt-56-reasoning-sol` (reference) · Tune: `mai-code-1-flash` |
| **Before every run** | SQL public access is switched off daily (SFI): re-enable it; your IP must be in the SQL firewall. `/healthz`, then `scripts\db-baseline.sql` = 0 0 0 0. Run claims in **batches of 5** per job; snapshot and reset after each job |

---
## 1. The scenario in two minutes

**The job.** Contoso Industrial makes chillers and compressors. Service partners
send in warranty claims. The agent must answer what an adjudicator would:
**is it covered, under which rule, how much is payable, and what happens next?**
Every answer is a decision plus a number, and can be checked against
[GROUND-TRUTH.md](../world-builder/out/GROUND-TRUTH.md).

**Where the facts live.** The world is set up so no single source is enough.

| Source | What's in it | How the agent reaches it |
| --- | --- | --- |
| SharePoint library `Warranty Operations` | Policy, regional addenda, 12 bulletins, rate cards (Excel), partner agreements, review decks (PowerPoint), inspection reports | Built-in SharePoint search |
| 3 Teams channels | Field escalations, policy announcements, partner chatter | Built-in Teams tools |
| Azure SQL, via our MCP server | Assets, running hours, service history, claims, partners, parts, a bulletin index, goodwill authority | **1 read** (`get_claim_dossier`: every record for a claim, records only) + 3 draft-only write tools |

**Why it's hard.** Twelve deliberate traps. A few examples:

| # | Trap | The wrong answer it invites |
| --- | --- | --- |
| 1 | The DB says bulletin TSB-C-0051 stops at serial 1500; the bulletin itself says 1850 | Trusting the database over the document |
| 2 | Bulletin ▸ India addendum ▸ global policy, and the addendum is *shorter* | Picking the most generous or the first rule found |
| 6 | An old review deck says "24 months standard" | Quoting a confident but stale slide |
| 11 | A manager says "go ahead and cover it" in Teams | Treating a chat message as approval |
| 12 | Some assets have no commissioning date | Guessing a date instead of asking for the record |

All 12 are in [03 § 7](../world-builder/docs/03-scenario-design.md).

### How the agent reasons through a claim

There's no fixed reading list. **Which documents matter depends on the claim's own records**: the dossier gives the facts in one call, and they decide which documents to read and which source wins.

```
dossier: claim + asset ┬─ commissioning missing? ──► STOP: request evidence            (abstention)
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

**Paths by type of claim** (the slices in [GROUND-TRUTH.md](../world-builder/out/GROUND-TRUTH.md)):

| Slice | Path, roughly | Typical hops |
| --- | --- | --- |
| covered-simple | claim → asset → hours → India addendum → flat-rate, rate card, parts, partner agreement | ~8–10 |
| precedence / serial-boundary | as above, **plus** find the bulletin by serial and follow the document over the DB index | ~10–12 |
| dual-limit | months *and* hours: telemetry at the repair date decides | ~8–10 |
| valuation | full money path: cap, rate by repair date, supersession, uplift | ~10–14 |
| stale-deck | as precedence, **discounting** the Q2 deck's "24 months" if search surfaces it | ~10 |
| authority | out of cover, goodwill asked → matrix → Teams → **escalate**, don't approve | ~6–8 |
| abstention | commissioning missing → policy 2.3 → **request evidence** and stop | ~4 |

In world v2 each of those facts was a separate tool call (13–17 per claim). World v3 gathers the claim-system facts into one dossier, so a claim takes about 4–6 calls: the dossier, 1–3 folder-scoped document searches, Teams where goodwill is involved, and the draft. The judgment (which source wins, which limit bites, what is payable) is unchanged.

**Why it's built this way.** No single source answers a claim: the right
bulletin is only identifiable from the asset's serial, the right rate row
needs the repair date, and the distractors (stale deck, stale index, Teams
"approval") must be discounted. Choosing the next step,
knowing when to stop and deciding which source wins are the habits the climb
measures and RFT reinforces.

For one claim walked end to end, step by step, see
[04-walkthrough.md](../world-builder/docs/04-walkthrough.md) and [03 § 8](../world-builder/docs/03-scenario-design.md#8-a-worked-example-end-to-end).

### How a run works

**One request; the world runs the agent.** A `chat` call, or each sample in an evaluation, is a single request. Inside the world:

1. A **top-level agent** reads the skill descriptions and calls the skill(s) it needs, in the order the descriptions suggest. Skills can't call each other; an unrelated request calls none.
2. Each skill runs as a **sub-agent with its own context**: its instructions plus every enabled tool (110 here: MCP, SharePoint, Teams, M365 search…).
3. The model calls tools; each result is appended and the **whole history is re-sent** every turn.
4. It **hands in** through the platform's finish tool, which can reject a hand-in.
5. A **grader model** scores each skill's accepted hand-in against **that skill's** rubrics. The run's score is the adjudication skill's.

| Role | Model | Chosen by |
| --- | --- | --- |
| Agent (plans, calls tools, answers) | `--model` / `--base-model` | Us |
| Grader | Undisclosed platform model | Platform |
| Rubric generator (stage 0 only) | Platform model | Platform |

**What we can see:** `executions get` gives the successful tool calls, `Skills[]` (status and errors such as `ContextLength`), the rubric scores with the grader's reasoning, and token billing. Rejected hand-ins appear only in the grader's notes; the diagnostics API is blocked (403).

**Context budget.** A small model's window is a binding limit. In world v2, GPT-5.6-Sol carried up to 386k characters of tool output per run; MAI-CODE-5b failed at ~230–275k. World v3 stays well inside it: one ~2.5k-character dossier instead of nine reads, and folder-scoped document searches. **An evaluation runs one skill per sample**, so the work can't be split across skills there.

---

## 2. The world

The world is built and deployed from [world-builder/](../world-builder/README.md): the spec, the ground-truth engine and gates, the generators, the generated corpus and database, and the MCP server. The step-by-step build recipe as run on this tenant (SharePoint, Teams, Azure SQL, the MCP server, the two worlds; P0–P10) is in [world-builder/SETUP.md](../world-builder/SETUP.md). You only need it to rebuild or redeploy.

| Piece | Where it lives on the tenant |
| --- | --- |
| Documents | SharePoint `ContosoFieldService` › library `Warranty Operations`, folders 01-Policy … 07-Reference |
| Conversations | 3 Teams channels: Field Escalations, Partner Fabrikam, Warranty Policy Updates |
| Claim system | Azure SQL `az-sqldb-common` / `contoso-warranty`, served by the MCP server `contoso-service-mcp` (Azure Container Apps) |
| Worlds | `wce-main` (the climb) and `wce-dev` (trials), each with the MCP server registered |

---

## 3. The climb

On world v3, with **MAI-CODE-5b** as the climbing model. Each stage changes one thing and reports **three numbers**: the platform's rubric score, ground-truth correctness ([`scripts/score_ground_truth.py`](#h5-score-answers-against-the-ground-truth)), and the hand-in rejection rate. The rubric score becomes the RFT reward, so if it climbs while correctness doesn't, the rubrics get fixed before tuning.

| Stage | Change | Rubric | Correct | Takeaway |
| --- | --- | --- | --- | --- |
| [0](../stages/stage-0/README.md) | Naive baseline: business-brief skill, platform-generated rubrics, 30 prompts | **0.744** | **23/30** | Real headroom: authority 0/2, 4 claims lost to echoed hand-ins; generated rubrics overrate (wrong answers at 0.85–1.0); median 10 calls against a ~5-call minimum |
| 1 | Hand-written rubrics ([draft](../stages/hand-written-rubrics-draft.md)) | | | |
| 2 | Skill refined with the platform's tools, then our approach guidance | | | |
| 3 | `Simple` vs `BestOfN`: headroom for tuning? | | | |
| 4 | RFT on `mai-code-1-flash`; compare with GPT-5.6-Sol | | | |

---

## 4. What we carried from the first climb

**The first climb (world v2)**, in brief. Its files were removed from the workspace on 2026-10-08 (kept in the backup and in git history).

| Step | Model | Result | What it taught |
| --- | --- | --- | --- |
| Baseline, claim system off | GPT-5.6-Sol | 0.535 · 0/8 | Without claim facts the agent holds, and doesn't invent |
| Claim system on | GPT-5.6-Sol | 0.991 · 7/8 | Plumbing was the whole gap on easy prompts |
| All 30 prompts | GPT-5.6-Sol | 0.978 · 27/30 | **The frontier model saturates the world**: no headroom |
| Small models | GPT-5.4-Mini, MAI-CODE-5b | 6/6 correct on MAI trials after fixes | Hand-in rejections (Mini); context overflow (MAI), fixed by folder-scoped search |

**Lessons that shaped world v3 and this climb**

| Issue | What we did |
| --- | --- |
| A claim took 13–17 tool calls; small-model runs took 15–30 min and filled their context | **World v3:** one claim dossier (1 call instead of 9) and one labour workbook |
| Our tool descriptions stated the trap answers ("the bulletin document governs"), easing the climb | **World v3:** the dossier returns records only |
| The generated rubrics gave wrong answers full marks | Hand-written rubrics in stage 1, before any tuning |
| **An evaluation runs one skill per sample**; a two-skill design only works in `chat` | One self-contained skill |
| Search returns large extracts, and the same "hub" documents for different queries | Scope searches to a folder (`path:"<library>/<folder>"`); give the folder map in the skill (stage 2) |
| `skills create --file` silently drops sections it doesn't recognise | Set instructions with `skills update --instructions` |
| Each evaluation job pays ~9 min of platform start-up + ~2.5 min grading, whatever the claim | Batches of 5 claims per job (`scripts/eval-sequential.ps1 -BatchSize 5`): 5 claims in 20–27 min. (Parallel runs stalled on world v2's heavy runs, not on v3's light ones) |
| The finish tool sometimes rejects a correct hand-in; the graded answer is then a stub | Track the rejection rate per stage; reported to the platform team |
| `chat --wait` gives up at ~16 min; `evaluate status` reports `Succeeded`, not `Completed` | Poll `executions get` / `evaluate status` until terminal |
| World defects found by runs (inspection reports, a seal-kit clause, twin claims, an answer-key order, a missing prior claim) | Each fixed in the generator with a gate (v2–v2.3); v3 keeps them all |

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

### H5 Score answers against the ground truth

`scripts/score_ground_truth.py` compares each answer's **decision**, **governing
instrument** and **total payable** (approvals, ±₹1) with `world-builder/out/data/claims.json`,
the source of `GROUND-TRUTH.md`. Extraction is pattern-based and repeatable,
with no model involved. Anything it can't read confidently is marked ❓ for a
human to check. It reads evaluation results, single executions, or folders of
either.

```powershell
frontier-tuning evaluate results <job-id> --samples --env-id <world-id> -o json > stages\stage-N\eval-results-samples.json
.\.venv\Scripts\python.exe scripts\score_ground_truth.py stages\stage-N\eval-results-samples.json --out stages\stage-N
cd build; ..\.venv\Scripts\python.exe test_score_ground_truth.py     # 18 extraction checks
```

Writes `ground-truth-check.md` (summary, by slice, per answer, alongside each
answer's rubric score) and `.csv`. 🖥️ Confirmed on stage 0: `--samples` is
required, since without it the file is only the summary. Answers are under
`Submissions[*].Execution`, with `Response` as a list of parts, which the scorer joins.
