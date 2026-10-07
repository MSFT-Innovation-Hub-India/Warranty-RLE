# Journey record — 2026-10-05

Verbatim record of the day's commands and output. The readable story is in [JOURNEY.md](../JOURNEY.md).

## F.1 SQL public access off overnight

```text
healthz first try: Response status code does not indicate success: 503 (Service Unavailable).
{"status": "degraded", "error": "('42000', '[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Reason: An instance-specific error occurred while establishing a connection to SQL Server. Connection was denied because Deny Public Network Access is set to Yes. ...')"}
```

User (08:59 IST): *"the az sql database public network gets disabled everyday for SFI. i have to enable public network access now."* After the user re-enabled it: `09:00:03 OK {"status":"ok","assets":117}`; baseline `0 0 0 0`.

## F.2 Hand runs on two failed hand-ins (GPT-5.4-Mini)

User: *"proceed with running it by hand like you said above. tell me how it goes"*.

```text
tools read 1: 88      ← the transient again
tools read 2: 137
--- 04150 : Please assess C-2026-04150 on serial CIE-4000-CH-01444 and give me the payable figure.
d04446c1-6e93-4a11-bc1d-3b9a9659f63d
--- 04103 : Can you work up C-2026-04103 for me — coverage position and payable amount?
c9c64dc9-4cd5-4456-bf1c-d673beed33c9
```

`executions get <id>` works for chat executions (205 KB and 241 KB); for evaluation executions it returns "not found". `executions diagnostics` → `API error (403) … The execution diagnostics API is not enabled.` Neither record contains the finish attempts or a finish-tool schema (searched for keys matching source/finish/citation: only `RubricResults[].Source = null`; `TaskSnapshot` null).

Tool order (DB = `1c171__*`, DOCS = `m365__search_enterprise_files`):

```text
04150  0-8 DB (+read_from_storage) · 9 create_claim_adjudication → ADJ-A50B2C878E request_evidence
       10-14 DB · 15-18 DOCS · 19-21 DB · 22-25 DOCS · 26 create_claim_adjudication → ADJ-D0D83CA33B approve 755050
04103  0-8 DB · 9 create_claim_adjudication → ADJ-62DB35A7CF request_evidence
       10-16 DOCS · 17-20 DB · 21 create_claim_adjudication → ADJ-101EA04112 approve 19150
```

Stored `Response`: 04150 *"Assessment: approve — Payable: INR 755,050"* (correct); 04103 *"Decision: Approve — INR 19,150"* (correct).

Grader, verbatim:
- 04150 Outcome 0.4: *"The successful finish gives an evidence-gap explanation and states that no payable can responsibly be calculated…"*; Presentation 0.6: *"…its source traceability is only partial because the successful finish carried an empty sources list."*
- 04103, first grading, Presentation 1.0: *"…despite the final successful finish call omitting formal source objects."*
- 04103, second grading, Outcome 0.4: *"The successful completion message gives a definite approval, total payable, draft ID, and human-review status, but omits the governing instruments… The detailed attempted handoffs were rejected by the finish tool and were not the successful response."*; Presentation 0.4: *"…it is framed as a completion-tool failure…"*

DB snapshot: the 4 drafts above → `db-reset-actions.sql` → `0 0 0 0`. Files: `docs/evidence/stage-3-mini-base/finish-probes/` (chat-*.json, exec-*.json, db-after-probes.txt).

## F.3 Model throughput (user question)

User: *"did you run those jobs in parallel or sequential? … i am not sure what throughput capacity has been allocated"*, then *"i meant the throughput capacity of the language models in the world, not the azure resources"*.

- The hand runs are sequential (one `chat --wait` after another). Evaluations: the platform runs all samples concurrently; `evaluate start` has only `--limit` and `--sample-id`, no concurrency option.
- Azure SQL `cpu_percent`/`workers_percent` max: 2-base 1%/3%; 3-mini-base 0%/3%.
- `models list`: no capacity fields. `health token-usage` (04:01Z):

```text
Prompt 105,286,263 · Completion 819,217 · Total 106,105,480 · Cached prompt 100,652,416 · Measured executions 41
dev-ct-gp…  prompt 96,517,196  completion 687,200  total 97,204,396  cached 94,346,880  executions 39
prod-gpt-…  prompt  7,671,467  completion 117,983  total  7,789,450  cached  5,285,376  executions 41
dev-ct-ma…  prompt  1,097,600  completion  14,034  total  1,111,634  cached  1,020,160  executions 1
```

## F.4 MAI on the same two claims

User: *"can you try the same 2 questions with the MAI model … and tell me how it goes"*.

```text
healthz ok · baseline 0 0 0 0 · tools read 1: 137
--- 04150 exec ce09af1e-7d96-48ff-9e79-933ce73848d8  (475 s)
--- 04103 exec 181a5c12-157d-417f-a627-00e938101f39  (655 s)
```

- 04150: 20 tool calls: 7 DB, then 13 DOCS. Response *"Decision: Covered — The payable amount for claim C-2026-04150 is INR 755,050."* Rubrics 0.833 / 0.8 / 1.0 / 1.0 / None. Billing 1,058,667 tokens, 33 tool invocations.
- 04103: 42 tool calls (DB sequence ×3, 20 DOCS, `lumina_sandbox__run_in_terminal` ×1). Response *"Recommended decision: APPROVE · Coverage basis: Standard warranty under ADD-IN-2.1 (India) · Payable: INR 19,150"*. rubricResults: **0**; status Completed, timedOut False, error None. Billing 1,738,796 tokens, 62 tool invocations.
- DB snapshot: no drafts, evidence requests or escalations → reset → 0 0 0 0.

## F.5 Who grades, and when

User: *"is this grader our own custom code? … how did this know something that the platform is not able to tell us about?"* and *"when we called the ft run/chat command with the input, was the evaluation called automatically within it?"*

- The grader is the platform's own model; our code (`score_ground_truth.py`) only reads its output. Grading is automatic: `chat` output carries `rubricResults` (e.g. MAI 04150: 5 scores); evaluation jobs grade their own samples. No separate grading call was ever made.
- Seen: graded twice (04103 mini v1: 10 scores; 04150 mini v2: 10 scores), and not graded (MAI 04103: 0 rubric results, status Completed, error None).
- `diag execution d04446c1-…` → `API error (403) … The execution diagnostics API is not enabled.` `executions get … -v` adds only the HTTP request lines.

## F.6 Skill v2 (stage 3b)

- Live skill fields: Id, TaskTemplateId, Name, Description, …, `Rubrics` (5), `Prompt` (the instructions), Enabled, Knowledge, DebugContext. Saved v1: `docs/evidence/stage-3b-mini-skill/skill-v1-platform.json`.
- New text vs the 28 rubric items: no shared 5-word phrase. Removed before applying: an unverified line claiming that file-name search is faster.
- `skills update cf00d339 --instructions <body>` → `Prompt` == v2 apart from line endings (3,076 chars); `Rubrics` == pinned; Enabled true.
- Pre-flight: healthz ok · baseline 0 0 0 0 · tools **136** ×4.

```text
--- 04150 exec b377f130-cf32-4689-af3e-70ef6042fbf6 (360 s)
--- 04103 exec ad565697-c2af-4d31-8a0b-56bfa1198c7f (248 s)
04150 v2: calls 28 · docs 8 (before 1st draft 8) · repeats 10 · drafts 1 · decision request_evidence · total 742000
04103 v2: calls 12 · docs 6 (before 1st draft 6) · repeats 0 · drafts 1 · decision request_evidence
order 04103: get_claim · get_asset · get_tsb_index · get_service_history · DOCS ×6 · get_goodwill_authority · create_claim_adjudication
```

Grader excerpts: 04150 *"The accepted hand-in is an inability statement rather than the requested assessment…"*; *"The investigation reached a covered/approve conclusion under TSB-C-0051 in its attempted hand-ins, which called for a draft adjudication, but no claim-system draft was recorded."* 04103 *"The successful hand-in is abbreviated and begins with a tool-formatting disclaimer before the result… supplies no valid source list."*

Delivery check widened ("attempted hand-ins", "accepted hand-in", "tool-formatting"; also "rejected by the formatter", "rejected finish", "successful final output/response/handoff"). Tests 38/38. All stages re-scored: unchanged except 3-mini-base → 0/28 verified, 22/28 delivered ≠ stored. GPT-5.6-Sol: 0 of 62 flagged.

DB: ADJ-7CA848C79F (04103 request_evidence), ADJ-AF99423F10 (04150 request_evidence) → reset → 0 0 0 0.

Tools after: 136 · 1c171=12 lumina_sandbox=9 **m365=4** mcp_OneDriveRemoteServer=18 mcp_SharePointRemoteServer=31 polymer_atomic=17 teams=43 workspace_health=2. m365 now: search_enterprise_files, GetSpoId, write_to_storage, read_from_storage. **Missing: `m365__call_copilot`** (present in stage-0 traces).

## F.7 Skill v2.1 + OneDrive off (user away; recommended option taken)

- v2 saved as `stages/stage-3b-mini-skill/warranty-assistant.v2.md` and `instructions-v2.0.txt`. v2.1 line: *"Put every citation inside the answer text, and leave the hand-in's separate sources list empty."* Shared 5-word phrases with rubrics: none.
- `skills update cf00d339 --instructions` → Prompt == v2.1, Rubrics == pinned. `tools disable c33f274c-2451-45df-8bfa-99281b9c11b8` → `Tool … disabled.` → tools 118 ×4 (1c171=12 lumina_sandbox=9 m365=4 mcp_SharePointRemoteServer=31 polymer_atomic=17 teams=43 workspace_health=2).
- `environments export` tool slots: contoso-service on · fabriciq off · Me on · Word off · M365Chat off · SharePoint on · **OneDrive on → off** · Teams on · Calendar off · Email off.

```text
--- 04150 exec 934bcb81-c91b-439b-9b05-db639a848626 (437 s)
--- 04103 exec c6a77b7d-5176-49b8-9b3d-646321677ecd (815 s)
04150 v2.1: calls 30 · docs 17 (before draft 17) · repeats 4 · drafts 0 · input tok 5021k · stored: approve 755050 · rubrics [0.6, 0.2, 0.56, 0.2, None]
04103 v2.1: Status Failed · ErrorCode 8 "Exception" · "We encountered an issue while processing your request. Please try again in a new chat." · 14 calls, 0 docs · rubric results 0
order 04103: get_claim · get_tsb_index · get_asset · get_service_history · find_prior_claims · mcp_SharePointRemoteServer__listDocumentLibrariesInSite · mcp_SharePointRemoteServer__listLists · mcp_SharePointRemoteServer__getDefaultDocumentLibraryInSite · teams__ListChats · get_goodwill_authority · lookup_part · get_claim · get_asset · get_claim
```

- 04150 grader: *"The handed-in response definitively says the claim is covered, identifies TSB-C-0051, states its 36-month/8,000-hour period, and definitively explains that the payable cannot be calculated without the missing India rate and price records."*; *"The final hand-in begins with inability to calculate… the successful submission has no inline citations… supplies no arithmetic."* Stored Response: *"Recommended decision: Approve under TSB-C-0051 · Payable: INR 755,050"*.
- `chat --wait` on the failed run printed `Warning: failed to retrieve execution diagnostics: API error (403)` before the JSON, which broke parsing of the chat file. Read the `executions get` file instead.
- Live-progress check: `executions list` returns `[]`. Our MCP logs across 5 replicas showed 58 POSTs from 06:56Z to 07:11Z. My first log filter compared UTC timestamps as local time and wrongly showed 0, and my folder check at 12:38 IST wrongly suggested 04150 was still running; it had finished at ~07:03Z.
- Delivery check: added "successful submission". DB: no drafts → reset → 0 0 0 0.

## F.8 MAI-CODE-5b on v2.1, then v2.2 (user: "baseline with mai-code-5b and fine tune the flash version")

v2.1 runs: `4c2b8243-009b-418e-947a-e43f0b9f3f18` (04150, 626 s; the tools read before it showed 87, a short read), `09e562d7-9860-4ff7-9c2e-3d21bbd9cd06` (04103, 678 s). Both stored a correct approve (₹755,050 / ₹19,150). Neither was graded.

`Skills[]` per run (status, ErrorCodeString):

```text
MAI v1 04150   [Completed]                          graded 10 rubric results
MAI v1 04103   [Failed ContextLength, Failed ContextLength]   0
MAI v2.1 04150 [Failed ContextLength, Failed ContextLength]   0
MAI v2.1 04103 [Failed ContextLength, Failed ContextLength]   0
ErrorResponse: {"ErrorCode": 2, "ErrorCodeString": "ContextLength", "ErrorMessage": "The skill failed before completion."}
2-base (Sol): 30 × [Completed] · 3-mini-base: 23 × [Completed], 4 × [Completed, Completed], 1 × [Completed ×3], 2 × [] (hung)
```

Passes (split at each `get_claim`; start index, calls, tool-output chars): MAI v2.1 04150 (0, 16, 233k) (16, 12, 271k) (28, 15, 143k); MAI v2.1 04103 (0, 18, 260k) (18, 12, 226k) (30, 13, 111k); MAI v1 04103 (0, 12, 275k) (12, 16, 259k) (28, 14, 132k). Sol 2-base: per-run median 208k, max 386k, all completed.

Search breakdown (MAI v2.1 04150): 21 searches, all `size=25`; 7 returned 0 hits; call 13 `"Warranty Operations/03-RateCards"` returned Flat-Rate-Labour-FY26.xlsx (COMP-RR … 9) and Labour-Rates-By-Region-FY26.xlsx (India INR 1450 2026-04-01 – 2027-03-31); 7 searches for a non-existent C-2026-04150 inspection report; rate cards searched again at calls 40–41. Raw search output 621k chars = 292k extract text (of which 36% markup) + JSON escaping/metadata (53% of raw).

User: lever 2 (lean documents) rejected (*"we can't be putting limits on the documents themselves"*); lever 3 (split) *"seems inevitable"*.

CLI: no `environments update` (only access, export, get, import, init, init-md, list, mapping). `skills create`: name, description, instructions, knowledge; no chaining field.

v2.2 runs: `a2db95bc-7677-4d22-bc55-1d652e082a64` (04150, 666 s): Skills [Completed]; 19 calls, 12 searches (size 10 ×10, 15, 20), 0 repeats, 1 draft (ADJ-0CD9B99EAC approve 755050), tool output 201k; rubrics 0.83 / 0.8 / 1.0 / 0.67 / 1.0. `0af5028b-33e4-4efa-8267-631be8e65c4a` (04103, 1007 s): Skills [Failed ContextLength ×2]; 52 calls, 29 searches, 15 repeats, 0 drafts, 627k. DB reset → 0 0 0 0.

Scorer: the "successful …" alternative now needs non-answer wording; added `delivered_decision()` (the grader's described delivered decision ≠ the stored one → mismatch); "cannot yet be conclusively decided" added to the request_evidence pattern. Tests 43/43. Re-score: Sol stages unchanged (0 flags); 3-mini-base 19/28 flagged, 1/28 verified correct; MAI v2.2 04150 verified ✅.

Rubrics v2 drafted: `stages/rubrics-v2-draft.md` (design guide 03 §9.2, adapted). Two rubric phrasings reworded to avoid 5-word overlap with the v1 skill text; overlap now none.

## F.9 Research-skill experiment (wce-dev)

- `skills create --file stages/experiments/research-skill-wce-dev/library-research.md` → `9db9be9a-f862-4444-a904-f63373f387fa` (Rubrics [], Version 1, Tools [read_from_storage], SupplementaryGraderConfig "{}"). Dev `warranty-assistant` 8e9d12a2 → delegating instructions. Dev OneDrive slot `ded2a328-…` disabled → 118 tools.
- Run 1 (instruction-only delegation), 04103, execution `783e24c7-494f-4c89-bce7-f45f8f726b13`: Skills [warranty-assistant Failed ContextLength, warranty-assistant Failed ContextLength, library-research Running]; 53 calls, 27 searches, 608k chars; Response *"This request is taking longer than expected to complete. Please reply with "continue" to resume from where I left off."*
- The user asked to stop after 04103. The 04185 run had already been submitted. It left draft `ADJ-DC80DA034A` C-2026-04185 approve 199175 (refs TSB-C-0051, TSB-C-0043, POL-WAR-4.2, ADD-IN-2.1, SPA-2023…), found and reset at 17:02. A tool call at ~15:47 (`executions list`/`cancel --help`) was interrupted; `executions list` on dev had returned [] earlier.
- Run 2 (description steering), 04103, execution `06a3c7a8-8859-4c6f-83eb-ddb0b368140f`, 823 s: Skills [library-research Completed, warranty-assistant Completed (5 rubric results)]; 29 calls, 11 searches, 180k chars; stored and delivered *"Approve C-2026-04103 as covered. Total payable: INR 19,150."*; draft ADJ-9666AD27EB approve 19150; rubrics 0.8 / 0.8 / 1.0 / 0.5 / 1.0. DB reset → 0 0 0 0.
