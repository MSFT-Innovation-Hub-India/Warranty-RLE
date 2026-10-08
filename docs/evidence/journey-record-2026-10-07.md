# Journey record: 2026-10-07 (world v3)

Verbatim record. The readable story is in [JOURNEY.md](../JOURNEY.md). The morning's stage-3 work on world v2 (evaluation runs one skill per sample) is recorded in archive/world-v2/evidence/journey-record-2026-10-06.md G.6.

## V.1 Decision (user, 14:31–16:31)

*"I am getting tired of this wait… for each claim there are ~16 to 17 tool calls… can we reduce this while still retaining the complexity… maybe 1 SharePoint call, one MCP call and one Teams call"*, then *"proceed… archive all that we did so far, and have a clean working folder… the journey needs to be honored… the authenticity of the use case scenario and how we hill climb that would be paramount."*

## V.2 Archive

`git mv` (tracked) or `Move-Item` (untracked): `stages/` → `archive/world-v2/stages/`; `docs/evidence/` → `archive/world-v2/evidence/`; earlier `archive/stages/` → `archive/world-v2/superseded-runs/`; `archive/docs/` → `archive/world-v2/docs-old/`; `docs/JOURNEY.md` copied to `archive/world-v2/JOURNEY.md`. Links inside the archive rewritten by old→new path map: 44 fixed; 6 left in the historical stage index (pre-rename names).

## V.3 World v3: code

| File | Change |
| --- | --- |
| `build/gen_sheets.py` | `flat_rate_labour()` + `labour_rates()` → `labour_rate_card()`: `Warranty-Labour-Rate-Card-FY26.xlsx`, sheets *Flat Rate Labour*, *Labour Rates*, *Notes*. Removes the two v2 files from `out/` |
| `mcp/contoso_service_mcp/tools.py` | `get_claim_dossier(db, claim_id)`: claim, asset, running hours at the repair date, service history, related claims, service partner, parts (claimed and fitted), bulletin index, goodwill matrix. Drops the keys `note`, `authority_warning`, `suggested_action` |
| `mcp/contoso_service_mcp/server.py` | MCP tools: `get_claim_dossier` + 3 actions (9 reads removed). Server instructions and action docstrings made factual (no "the document governs", no example instrument refs) |
| `mcp/tests/test_tools.py` | +8 dossier checks: sections, no guidance keys, < 6,000 characters, stale index 0051 → 1500, P-44120 and P-44120-A both present, missing commissioning as a fact, C-2026-03110 `Paid`, unknown claim |

Gates, as run (`.venv\Scripts\python.exe build\<script>.py`):

```
adjudicate    exit=0  All 14 checks passed - guide 03 section 8 reproduces.
test_traps    exit=0  31/31 checks passed.
populate      exit=0  Design conformance: OK
ground_truth  exit=0  wrote C:\Users\sansri\contoso-warranty-rle\out\GROUND-TRUTH.md  (993 lines)
gen_db        exit=0  Written to C:\Users\sansri\contoso-warranty-rle\out\db
gen_sheets    exit=0  2 workbooks written to C:\Users\sansri\contoso-warranty-rle\out\sharepoint\03-RateCards
```

`GROUND-TRUTH.md` diff: the "Produced" date line only. MCP tests: **45/45**. Dossier sizes: 04114 2,169 · 04185 2,168 · 04189 2,636 · 04103 2,457 characters.

## V.4 Deploy

```
az acr build -r pcdotaiagentd10b5a -t contoso-service-mcp:v5-dossier-20261007-1646 --platform linux/amd64 mcp
   -> log streaming crashed locally (UnicodeEncodeError, cp1252); the build itself: az acr task list-runs -> Succeeded
az containerapp update -g pcdotai-agent -n contoso-service-mcp --image pcdotaiagentd10b5a.azurecr.io/contoso-service-mcp:v5-dossier-20261007-1646
image now: pcdotaiagentd10b5a.azurecr.io/contoso-service-mcp:v5-dossier-20261007-1646
{"status":"ok","assets":117}
main: mcp=4 -> get_claim_dossier, create_claim_adjudication, request_missing_evidence, escalate_goodwill   (total 110 on re-read; first read 79)
dev:  mcp=4 -> same
frontier-tuning tools invoke 1c171__get_claim_dossier --args '{"claim_id":"C-2026-04189"}' -> found, related_claims C-2026-03110 status Paid
```

No re-registration was needed: both worlds discovered the new tool list immediately.

## V.5 SharePoint (03-RateCards)

Via the world's SharePoint MCP tools (`tools invoke`, library `b!btFf7qjN…fhxAE`, folder `01DRFRACQMSJPJ66NQGJA247UHAHDYTO2E`):

- `deleteFileOrFolder` × 2: `Flat-Rate-Labour-FY26.xlsx`, `Labour-Rates-By-Region-FY26.xlsx` → `{'Status': 'Successful', …}` (the listing showed them for ~1 min more).
- `createSmallBinaryFile` `Warranty-Labour-Rate-Card-FY26.xlsx`: the first attempt failed with `The command line is too long.` (`cmd.exe` limit; base64 args 10,687 characters). Re-run with `subprocess` and no shell → created, id `01DRFRACSM3BJU32O3Y5H3B3T33X7ZCGOP`.
- Folder now: `Parts-Price-List-FY26.xlsx` (15,546) · `Warranty-Labour-Rate-Card-FY26.xlsx` (15,612). Files: `sp-03-ratecards-before.json`, `sp-03-ratecards-v3.json`.
- Search probe: `Warranty Labour Rate Card` → the new workbook at rank 1; `labour rate card India path:".../03-RateCards"` → the new workbook only.

## V.6 Platform state for stage 0

- Both worlds: `warranty-assistant` set to the stage-0 business brief (`skills update --description --instructions`); instructions verified equal; 5 pinned rubrics, `auto_generated`. `library-research` deleted in both (`10a3d801` main, `9db9be9a` dev; content archived).
- The cancelled dev job `a5e9d489-…` stayed `Paused`; a second `evaluate cancel` → `API error (500): InternalServerError`. Its 04103 execution wrote draft `ADJ-8499F75D51` at 08:35 UTC, after the 14:05 IST reset; found by the baseline check (`1 0 0 0`) and reset.
- `scripts/eval-sequential.ps1`: `-Samples` is now one comma-separated string (passing an array through `powershell -File` arrived as one string → `ER07008 sample ids were not found`).

## V.7 Stage 0 run (2026-10-07 17:15 → 2026-10-08 00:22 IST)

- Smoke 04150, job `e29b39ef-e75e-47ab-8c5e-4e51b20d075f`: Succeeded after 26 min; execution 12.4 min; 32 calls; fully correct.
- One claim per job (`eval-sequential.ps1`, 04101 → 04140, 15 jobs): every job Succeeded, 15–26 min each. Per-job timestamps: **~9 min from job creation to execution start** on every claim (e.g. 04101 created 12:14 UTC, execution 12:23:26–12:33:10, graded 12:34:17); execution 3.0–12.8 min; grading 1.0–5.2 min after execution.
- Paused at 23:03 for a network change (`stop_powershell`). New client IP 106.222.203.228 → `az sql server firewall-rule create … -n ClientIPAddress_2026-10-7_23-6-12`. 04140 (job `899b19b3-7d59-4c66-9d7a-019aedc41b0d`) finished server-side and was collected at 23:10.
- Remaining 13 in batches (`-BatchSize 5 -TimeoutMin 60`), from the run log:

```
23:11:57 04141+04148+04149+04151+04152 job 92cf4f5f-3035-4ded-b763-9f441477fe35 started
23:38:52 04141+04148+04149+04151+04152 Succeeded after 27 min
23:39:50 04153+04166+04167+04171+04172 job 6ba0f977-6c44-4c9f-9fbe-d4ac087385fd started
00:00:20 04153+04166+04167+04171+04172 Succeeded after 20 min
00:01:22 04176+04177+04178 job afecf010-7b79-4e8a-9bf3-99bd8fd6d3dd started
00:21:56 04176+04177+04178 Succeeded after 21 min
```

  Batch 1 diagnostics at ~17 min: `completed 4, running 1 … Retried: 0 … Resubmissions: 0`.
- `python scripts\summarise-stage.py docs\evidence\stage-0 stages\stage-0` → `Claims: 30 · mean calls 11.1 · mean tool output 112.6k · overflows 0`; scorer: 16/30 fully correct, 7 ❓, mean rubric 0.744. Hand check (stages/stage-0/hand-check.md): **23/30**. Echoed hand-ins found by grader-note regex: 04115, 04139, 04140, 04167, 04176; partly rejected: 04103, 04152.

## V.8 Clean-up (2026-10-08 06:24; user: "I want all the baggage from the previous scenario removed completely… I have taken a backup")

Removed from the workspace (kept in the user's backup and in git history): `archive/` (the whole world-v2 climb: stages, evidence, journey, superseded runs), `docs/05-hill-climb-runbook.md`, the cross-cutting references from the earlier contract-renewal exploration (`rubric-design.md`, `rubric-patterns.md`, `rubric-defects.md`, `troubleshooting.md`, `CLI-REFERENCE.md`), and `scripts/migrations/` (the v2.3 database migration; the generator builds the current state directly). `platform-issue-finish-rejection.md` was moved into this folder (an open item). Links to removed files were turned into plain text (16); JOURNEY P11 (runbook update) removed; v3 notes added to the top of guides 03 and 04; AGENTS.md rule: a superseded run is deleted, git keeps it.
