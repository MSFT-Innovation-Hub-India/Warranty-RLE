# Journey record: 2026-10-06

Verbatim record for this session. The readable story is in [JOURNEY.md](../JOURNEY.md).

## G.1 World v2.3: repair-warranty prior claims (user: "what do we do about the issue with 04189? can you address that?")

**Defect** (found 10-05, attempt 6 on 04189, execution `68dcdf7b-c430-4d3b-87b1-8dc8301e122c`):

- `ServiceHistory` J-00087 (serial 01980) and J-00089 (serial 01981) both cited `C-2026-03110`.
- `Claims` had no such row. `get_claim("C-2026-03110")` returned `{"found": false, "reason": "No claim with this reference exists in the claim system."}`.
- Ground truth for 04189 and 04190 is approve, POL-WAR-4.2 6.1, ₹69,575, RW. Clause 6.1 needs the earlier component to have been *"replaced under warranty"*, which the claim system could not show.

**Changes:**

| File | Change |
| --- | --- |
| `build/populate.py` | Prior claim per asset: `C-2026-{3110 + i:05d}` (03110 for 01980, 03111 for 01981) |
| `build/gen_db.py` | Prior claims inserted into `Claims` as `Paid`, derived from the claim (serial, dealer, op code, part fitted, hours; submitted = completed + 6 days). Gates: prior IDs unique and in the `C-2026-03xxx` range; **every claim a service job cites must exist in Claims** |
| `scripts/db-baseline.sql`, `db-reset-actions.sql`, `db-actions-snapshot.sql` | Compare with the seeded status `CASE WHEN claim_id LIKE 'C-2026-03%' THEN 'Paid' ELSE 'Submitted' END` instead of `'Submitted'` |
| `mcp/tests/test_tools.py` | The action test picked the first claim (now `C-2026-03110`) and reset it to `Submitted`. It now picks the first `Submitted` claim and restores its own status |
| `scripts/migrations/2026-10-06-world-v2.3-prior-claims.sql` | Idempotent in-place migration for Azure SQL |

**Gates, as run** (`.venv\Scripts\python.exe build\<script>.py`, in order) *(trimmed to last lines)*:

```
===== adjudicate
All 14 checks passed - guide 03 section 8 reproduces.
===== test_traps
31/31 checks passed.
===== populate
assets      120
telemetry   3007 rows
claims      90  (eval 30 / train 60)
decisions   {'approve': 52, 'decline': 24, 'escalate': 5, 'request_evidence': 9}
eval slices {'covered-simple': 3, 'declined-simple': 2, 'precedence': 5, 'serial-boundary': 4, 'dual-limit': 3, 'valuation': 6, 'stale-deck': 2, 'authority': 2, 'abstention': 3}

Design conformance: OK
===== ground_truth
wrote C:\Users\sansri\contoso-warranty-rle\out\GROUND-TRUTH.md  (993 lines)
===== gen_db
  trap 1 armed: index says TSB-C-0051 ends at 1500, the bulletin document says 1850
```

Tests: MCP `tests\test_tools.py` **37/37**; `build\test_score_ground_truth.py` **43/43**. Local DB after the tests: `[('C-2026-03110', 'Paid'), ('C-2026-03111', 'Paid')]`. (The first test run, before the test fix, left 03110 as `Submitted`; DB regenerated.)

**Diff** of generated output: `claims.json` (04190's prior-claim ID only), `seed.*.sql` (+2 Claims rows, J-00089 → 03111), `GROUND-TRUTH.md` (date line only). Generators for documents, decks, sheets and Teams were not re-run: none reads `prior_claim`.

**Azure SQL**, as run:

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\migrations\2026-10-06-world-v2.3-prior-claims.sql
claim_id     serial            submitted_date        repair_date           operation_code claimed_part claimed_labour_hours status
C-2026-03110 CIE-4000-CH-01980 4/26/2026 12:00:00 AM 4/20/2026 12:00:00 AM CTRL-BD-RR     P-44900                      1.50 Paid
C-2026-03111 CIE-4000-CH-01981 4/26/2026 12:00:00 AM 4/20/2026 12:00:00 AM CTRL-BD-RR     P-44900                      1.50 Paid
job_id  serial            claim_id     completed_date
J-00086 CIE-4000-CH-01980 C-2026-04189 6/1/2026 12:00:00 AM
J-00087 CIE-4000-CH-01980 C-2026-03110 4/20/2026 12:00:00 AM
J-00088 CIE-4000-CH-01981 C-2026-04190 6/1/2026 12:00:00 AM
J-00089 CIE-4000-CH-01981 C-2026-03111 4/20/2026 12:00:00 AM
dangling_service_jobs
                    0
OK: 1 batch(es) executed

powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sql-run.ps1 -File scripts\db-baseline.sql
drafts evidence_requests escalations claims_not_seeded
     0                 0           0                 0
```

**Live MCP**, as run:

```
frontier-tuning tools invoke 34d14__get_claim --args '{"claim_id":"C-2026-03110"}' --env-id 6bec3bf9-0222-4285-8a5b-214867ac42cc
Tool invoked successfully. { "found": true, "claim_id": "C-2026-03110", "serial": "CIE-4000-CH-01980", "dealer_id": "D-IN-01", "submitted_date": "2026-04-26", "repair_date": "2026-04-20", "operation_code": "CTRL-BD-RR", "claimed_part": "P-44900", "claimed_labour_hours": 1.5, "goodwill_requested": null, "status": "Paid" }
```

Dead end: the first probe used the MCP prefix `34d14238__get_claim`; the registered prefix is `34d14__`.

## G.2 Attempt 8: folder map in one editable section (user: "provide the folder map as a part of instructions… so i can easily locate it… and change it later")

Both wce-dev skills carry the map in a final `## Library folders` section (library address + one line per folder); the step instructions refer to it by name. Files: `stages/experiments/research-skill-wce-dev/{library-research,warranty-assistant}.attempt8.md` and `-body.txt`. 5-gram overlap with rubrics (v1 pinned + v2 draft): none (research); none in the adjudication skill's new text.

Pushed and verified (`skills get` → `Prompt`):

```
9db9be9a (library-research): has map section=True | 07-Reference=True | points to map=True | len=2173
8e9d12a2 (warranty-assistant): has map section=True | 07-Reference=True | points to map=True | len=3941
```

## G.3 Attempt 8 runs (three claims in parallel, MAI `dev-ct-mai-code-mp`, wce-dev)

As run (one shell per claim; prompt text identical to attempts 2–7):

```
$q = Get-Content "...\files\q-$c.txt" -Raw
frontier-tuning --output json chat -q $q --model dev-ct-mai-code-mp --env-id 6bec3bf9-0222-4285-8a5b-214867ac42cc --wait 2>&1 | Out-File "$ev\chat-$c.json" -Encoding utf8
```

All three `chat --wait` calls returned `timedOut: true` at ~15 min; executions followed with `executions get` until Completed (07:12–07:19). Raw JSON: `docs/evidence/experiments/research-skill-wce-dev/attempt8/`.

Summary (`files/run_summary.py`) *(trimmed)*:

```
04185 exec 33cee794-392a-4a9b-ab53-b27e2f0d2535 status=Completed
  skills: library-research Completed | warranty-assistant Completed | warranty-assistant Completed
  calls=33 searches=8 scoped=7 tool_output=57k in_tok=1225310
  response: Decision: approve C-2026-04185 for INR 199,175 under TSB-C-0051.
04103 exec 97c5ad36-26dd-4587-a82b-a2999f7a7097 status=Completed
  skills: library-research Completed | warranty-assistant Completed
  calls=33 searches=17 scoped=8 tool_output=116k in_tok=939066
  response: Decision: Covered ... Total payable: INR 19,150
04189 exec c0cbeec3-940d-47bd-8b36-e9fa6c7b48c4 status=Completed
  skills: library-research Completed | warranty-assistant Completed
  calls=30 searches=12 scoped=12 tool_output=67k in_tok=874338
  response: Approve C-2026-04189 for INR 69,575 under Global Warranty Policy clause 6.1, funding code RW
```

04185 grader notes (verbatim, first invocation): *"Although the agent prepared comprehensive adjudication text in earlier finish attempts, those submissions were rejected. The only successful hand-in was "A test [cite:claim]," which delivers none of the requested claim results."* Second invocation: *"…the only successfully accepted hand-in was "Test sentence [cite:src1]."*

Rejected hand-ins by attempt (grader notes mention rejection or a test hand-in):

```
attempt6 04185: Completed RO=0.8 rejected=n
attempt6 04103: Failed/ContextLength | Completed RO=1.0 rejected=n
attempt6 04189: Completed RO=1.0 rejected=n
attempt7 04185: Completed RO=0.0 rejected=Y | Completed RO=1.0 rejected=n
attempt7 04103: Completed RO=0.0 rejected=Y | Completed RO=1.0 rejected=Y
attempt7 04189: Completed RO=1.0 rejected=n | Running RO=- rejected=n
attempt8 04185: Completed RO=0.0 rejected=Y | Completed RO=0.0 rejected=Y
attempt8 04103: Completed RO=0.8 rejected=n
attempt8 04189: Completed RO=0.8 rejected=n
```

DB after the runs: 3 drafts on C-2026-04185 (ADJ-1C6E58C474, ADJ-1B14357B8F, ADJ-AF8573C6AA, all approve 199,175 INR). Reset with `scripts\db-reset-actions.sql` → `0 0 0 0`; `C-2026-03110`/`03111` still `Paid`.

## G.4 Attempt 8b: hand-in rejection test

- Adjudication skill 8b = attempt 8 minus *"- Put every citation inside the answer text, and leave the hand-in's separate sources list empty."* Pushed to wce-dev `8e9d12a2`; verified live (`sources line=False | map=True`).
- **SQL firewall:** the client IP changed to 106.202.100.193 and the admin scripts failed (`Client with IP address '106.202.100.193' is not allowed to access the server`). Public access was still `Enabled`, and the MCP server was healthy (`{"status":"ok","assets":117}`), because it uses the `AllowAllWindowsAzureIps` rule. Added a single-IP rule: `az sql server firewall-rule create -g az-sqldb-common-rg -s az-sqldb-common -n ClientIPAddress_2026-10-6_7-58-40 --start-ip-address 106.202.100.193 --end-ip-address 106.202.100.193`.
- 04185 ×3 in parallel (07:59), same `chat` command as G.3 (files `attempt8b/chat-04185-{a,b,c}.json`). Executions: a `7960457c-8d5b-4419-95e9-7fcfb6f759ee`, b `6d0418ef-3dc7-41a4-b605-98be1346f730`, c `65529d26-07e5-4d4f-8a20-85da90dff879`. All Completed with one adjudication invocation each; no grader note mentions a rejection.
- Rep b draft rubric (verbatim): *"A draft was actually recorded, but the final draft is not consistent with the supported payable evidence, and the agent recorded two contradictory adjudication drafts despite the instruction to record the action once."* Draft calls: payable 194375, then 199175.
- DB after *(trimmed)*: ADJ-B7D7019A2E 199175 · ADJ-C192A674F3 199175 · ADJ-C79B9E4C19 194375, all C-2026-04185. Reset → `0 0 0 0`.
- Dead end: playbook code search for `cite:`, "sources list" and "finish tool" in m365-core/orbit returned nothing.

## G.5 Consolidation (user: "clean up the entire trail… retain the latest sub stage as the journey steps… findings captured succinctly")

| Before | After |
| --- | --- |
| `stages/stage-0`, `stage-1` (world v1) | `archive/stages/stage-0-world-v1`, `stage-1-world-v1` (`git mv`) |
| `stages/stage-0-v2`, `stage-1-v2`, `stage-2-base` | `stages/stage-0`, `stage-1`, `stage-2` (`git mv`); READMEs rewritten as change · setup · apply and run · result · findings |
| `stages/stage-3-mini-base`, `stage-3b-mini-skill`, `experiments/research-skill-wce-dev` | `archive/stages/…` |
| — | `stages/stage-3/`: `library-research.md` (= wce-dev `9db9be9a`, attempt 8), `warranty-assistant.md` (= wce-dev `8e9d12a2`, attempt 8b), pinned v1 rubrics, 30 samples. Instructions and descriptions verified equal to live: `True` × 4 |
| `docs/JOURNEY.md` (908 lines) | Rewritten (657 lines): §1 run mechanics condensed, §3 one line per stage, §4 lessons as issue → what we did. Old copy: `archive/docs/JOURNEY-full-2026-10-06.md` |
| `stages/README.md` | Rewritten; old copy `archive/stages/README-2026-10-06.md` |
| AGENTS.md | Rules updated (user decision): stage folders hold their latest configuration; consolidated rather than chronological writing; frontier model constant to stage 2 |

Ground-truth checks regenerated under the new folder names: rows unchanged for stages 0, 1 and 2. Nothing deleted.

## G.6 Stage 3 in wce-main, and how evaluation runs skills (2026-10-07)

- Pre-flight (10:59): SQL `Enabled`; client IP 167.220.238.220, covered by the existing rule `ClientIPAddress_2026-9-30_14-15-35` (167.220.238.2–250); `/healthz` 503 once (cold start), then `{"status":"ok","assets":117}`; baseline `0 0 0 0`; `tools available` 118 (12 × `1c171__`).
- Saved main `warranty-assistant` before the change: `docs/evidence/stage-3/main-skill-before.json` (5 rubrics, `auto_generated`).
- `skills create --file stages\stage-3\library-research.md` → `10a3d801-7ae8-4aaa-9279-8e528417cf4b`, but the stored instructions were 1,546 characters: **the file importer dropped the `## Library folders` section**. Fixed with `skills update 10a3d801 --instructions <body>` → 2,153 characters, map present. `warranty-assistant` `cf00d339` updated with `--description` and `--instructions`; both verified equal to the stage-3 files.
- Sample map: 30/30 eval samples ↔ claims (`docs/evidence/stage-3/sample-map.json`); `samples list` titles are truncated, so 6 were resolved with `samples get`.
- **Smoke job `ce41e2c3-98fa-41a3-972f-a393761a5e16`** (04101, MAI): Succeeded, overall 0.92. Execution `3b6821a1-…`: `Skills[]` = **warranty-assistant only**; 15 calls, 8 searches (2 scoped), 104k characters; approve ₹69,575 ADD-IN-2.1 (= ground truth); draft ADJ-BB6F542FC7 (deleted afterwards). Note: `evaluate status` reports `Succeeded`, not `Completed`.
- Two-skill sample in main (`--skill-id 10a3d801 --skill-id cf00d339`): `evaluate start` → `Error: API error (400): {"code": "ER07018", "message": "None of the selected samples are eligible for evaluation based on their attached skills."}`. Probe sample deleted (main back to 30).
- wce-dev: research rubrics R1–R4 (`docs/evidence/stage-3/library-research.rubrics.v2-draft.json`) applied to dev `9db9be9a`; a two-skill sample was then accepted. **Job `5742d845-a088-454f-975f-5811060b4c33`:** `Skills[]` = **library-research only**; 14 calls, 8/8 searches scoped, 36k characters; graded on the research rubrics only (0.417: Answers 0.33 · Attribution 0.0 · Restraint 0.67 · Economy 0.67); `warranty-assistant` never ran. Queue 46 min, execution 8 min.
- **Conclusion:** an evaluation runs **one skill per sample**; the top-level sequencing seen in `chat` does not happen. The split design can't be evaluated or tuned as a sequence.
- Stage 3 revised to a **self-contained** `warranty-assistant`: description without the library-research dependency; *"Search with the references the claim system gives you… Limit each search to the folder…"* (no "work from the library facts supplied"). No shared 5-gram with the rubrics. Applied to dev `8e9d12a2`; 3 single-skill dev samples (04185 `c0cf099f-…`, 04189 `278fc2dd-…`, 04103 `7d531d58-…`); **job `a5e9d489-2b73-418e-b13e-7d80c4c3f508`** started 12:41.
