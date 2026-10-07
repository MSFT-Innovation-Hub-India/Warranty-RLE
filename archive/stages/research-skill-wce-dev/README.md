# Experiment — a library-research skill to keep document bulk out of the adjudication skill (wce-dev, 2026-10-05)

**Status:** ⚠️ Mixed. Description steering works on 04103 (✅ correct, graded). On the heaviest claims the research skill itself overflows: 04185 correct after 32.5 min (attempt 2), failed (attempt 3); 04189 failed. Not yet robust.

**Question.** MAI-CODE-5b's adjudication skill overflows its context window (`ContextLength`) when its own document searches pile up (~230–275k characters). Can a separate **library-research** skill run the searches in **its own sub-agent context** and hand back only the relevant lines, so the adjudication skill stays small?

**User's idea (10-05):** *"not a functionality split in the skill, but having a 'technical' skill that is meant to handle the context overflow scenario calls, and return the relevant result alone to the main skill agent"*, with no extra tooling on top of the FT API surface (*"i would want to avoid building another tool"*). A skill is a native FT construct, so this stays within that surface.


## Files — which is which

| File | What it is | Used in |
| --- | --- | --- |
| [warranty-assistant.attempt2.md](warranty-assistant.attempt2.md) | **Adjudication skill as it ran in the successful run**: steering description + "work from the library facts supplied" | ✅ Attempt 2, execution `06a3c7a8-…`. Matches the live wce-dev skill (checked) |
| [library-research.attempt2.md](library-research.attempt2.md) | **Research skill as it ran in the successful run**: "Use this first…" description | ✅ Attempt 2 |
| [warranty-assistant.attempt1.md](warranty-assistant.attempt1.md) | Adjudication skill told in its *instructions* to use library-research | ❌ Attempt 1, execution `783e24c7-…` (overflowed) |
| [library-research.attempt1.md](library-research.attempt1.md) | Research skill with a plain description | ❌ Attempt 1 |
| [warranty-assistant.main-v2.2-reference.md](warranty-assistant.main-v2.2-reference.md) | A copy of wce-main's skill v2.2, the starting point. **Not applied in wce-dev** | Reference only |
| `delegate-body.txt` / `delegate2-body.txt` / `descriptions-v2.json` | The exact text pieces sent with `skills update` (attempt 1 / attempt 2) | Kept for replay |
| [warranty-assistant.attempt8b.md](warranty-assistant.attempt8b.md) (+ `-body.txt`) | **Current adjudication skill.** Attempt 8 minus the "leave the sources list empty" line | ✅ 8b: 04185 ×3, 0 rejected hand-ins, 3/3 correct |
| [library-research.attempt8.md](library-research.attempt8.md) / [warranty-assistant.attempt8.md](warranty-assistant.attempt8.md) (+ `-body.txt`) | **Current research skill** (attempt 8). Folder-scoped search in both skills; the map is in a final `## Library folders` section (edit only there) | ✅ Attempt 8: 3/3 correct, no overflow, 57–116k tool output |
| [library-research.attempt7.md](library-research.attempt7.md) / [warranty-assistant.attempt7.md](warranty-assistant.attempt7.md) (+ `-body.txt`) | **Generic scoping, no folder list**, in both skills | ❌ Attempt 7: invented folders; reverted |
| [library-research.attempt6.md](library-research.attempt6.md) (+ `-body.txt`) | **Research skill with folder-scoped search**: attempt 5 + `path:` scoping. Live in wce-dev since 21:15 | ✅ Attempt 6, execution `214300df-…` (04185 correct, one pass). Attempts 3–5 files are kept alongside |

## Setup (wce-dev `6bec3bf9-0222-4285-8a5b-214867ac42cc` only; wce-main untouched)

| | |
| --- | --- |
| `library-research` | **New skill** `9db9be9a-f862-4444-a904-f63373f387fa`, [library-research.attempt1.md](library-research.attempt1.md). Answers specific questions from the library with the passage or row and its source; specific searches, few results; two misses → not found; no commentary. No rubrics |
| `warranty-assistant` (dev `8e9d12a2-b0a5-4683-95f1-b225ed9ade44`) | **v2.2 with library reading delegated**, [warranty-assistant.attempt1.md](warranty-assistant.attempt1.md): *"To read the library, ask the library-research skill specific questions … and work from its answers rather than searching the library yourself."* The folder list and search line moved into `library-research`. Rubrics: dev's pinned set, unchanged |
| Tools | OneDrive slot `ded2a328-…` disabled (parity with main): 118 tools |
| Model | MAI-CODE-5b `dev-ct-mai-code-mp`, strategy `simple` |
| Claims | **04103** (eval; overflowed on main with v2.2) · **04185** (train, exclusion with reversal bulletin; approve ₹199,175 under TSB-C-0051) · **04189** (train, 90-day repair warranty; approve ₹69,575 under POL-WAR-4.2 6.1) |

New text vs rubrics (v1 pinned and v2 draft): `library-research` shares no 5-word phrase. The delegating skill's *new* line shares none; its v1 base text overlaps the v1 *generated* rubrics, as expected (they were generated from it).

## What we're checking

1. **Delegation:** which skills appear in `Skills[]`, how often, and whether the adjudication skill calls `library-research` itself or only the top-level agent does.
2. **Context:** each skill invocation completes, with no `ContextLength`.
3. **Correctness:** decision and amount against the answer key.
4. **Grading:** which invocation carries rubric results.

## Results — 04103 only (user: stop after 04103) · execution `783e24c7-494f-4c89-bce7-f45f8f726b13` · 2026-10-05 15:23–15:38 IST

**Status:** ❌ the delegation didn't happen; the skill overflowed as before.

`Skills[]` for the run:

| # | Skill | Status | Error | Invoked by |
| --- | --- | --- | --- | --- |
| 0 | warranty-assistant | **Failed** | **`ContextLength`** | top-level agent |
| 1 | warranty-assistant | **Failed** | **`ContextLength`** | top-level agent (re-invoked) |
| 2 | library-research | **Running** (never finished) | — | top-level agent, *after* both failures |

- **The adjudication skill never called `library-research`.** Despite the instruction, it searched the library itself: 27 searches, 53 calls, 608k characters of tool output. The same overflow as before.
- `library-research` was called only by the **top-level agent**, as a third sub-agent after the adjudication skill had failed twice, and it hadn't finished when the run stopped.
- The run ended after 15 minutes with the platform message *"This request is taking longer than expected to complete. Please reply with 'continue' to resume from where I left off."* No decision, no draft, no grade.
- 🖥️ **A skill doesn't call another skill.** Every `SubAgentId` belongs to the top-level agent, and the adjudication sub-agent didn't use `library-research` even when told to. 🔬 Most likely sub-agents don't see other skills as callable; only the top-level agent does.

**What it means.** A research skill can only work if the **top-level agent orchestrates**: call `library-research` first, then call the adjudication skill with those findings in its request. We can steer the top-level agent only through skill descriptions or the world's own instructions, which are fixed at world creation. The same applies to a coverage/valuation split.

**Side effect.** The sequence was stopped after 04103's file was saved, but the 04185 run had already been submitted (claim-system calls continued to 15:41). It may still be running on the platform, so the database is checked and reset after it ends.

**Follow-up (17:02):** the orphaned 04185 run had written one draft, `ADJ-DC80DA034A`, **approve ₹199,175** with refs TSB-C-0051, TSB-C-0043, POL-WAR-4.2, ADD-IN-2.1, SPA-2023-FAB-IN. That's the correct answer key decision; the run itself was never observed or graded. Snapshot in `docs/evidence/experiments/research-skill-wce-dev/db-snapshot-after-orphan.txt`; DB reset → 0 0 0 0.

## Option 1 — steer the top-level agent through skill descriptions (17:05)

User: *"check with option 1 above for one claim that involves research and the overflow"*. Only the descriptions and one instruction line change; nothing else.

| Skill | Change |
| --- | --- |
| `library-research` | Description now starts *"Use this first when a warranty claim needs facts from Contoso Industrial's Warranty Operations library."* |
| `warranty-assistant` (dev) | Description adds *"Expects the facts it needs from the Warranty Operations library to be gathered first with library-research and passed in with the request; it reads the service claim system itself."* Instruction line changed to *"Work from the library facts supplied with the request. Search the library yourself only for a fact that is missing from them, with specific terms and a few results at a time."* |

Texts: [descriptions-v2.json](descriptions-v2.json), [delegate2-body.txt](delegate2-body.txt). Claim: **04103**, MAI-CODE-5b, wce-dev.

### Result — execution `06a3c7a8-8859-4c6f-83eb-ddb0b368140f` (17:07–17:20 IST, 823 s) ✅

| | Every earlier MAI run on 04103 | **Description steering** |
| --- | --- | --- |
| `Skills[]` in order | warranty-assistant ❌ `ContextLength` ×2 | **library-research ✅ Completed → warranty-assistant ✅ Completed** |
| Overflow | every time | **none** |
| Answer | correct but ungraded | ✅ **approve ₹19,150**, graded |
| Draft | none | ✅ `ADJ-9666AD27EB` approve 19150 |
| Rubrics (warranty-assistant) | — | 0.8 / 0.8 / 1.0 / 0.5 / 1.0 |
| Calls · searches · tool output (whole run) | 43–53 · 25–29 · 608–627k chars | **29 · 11 · 180k** |

- 🖥️ **The top-level agent followed the descriptions:** it called `library-research` first, then `warranty-assistant` with the findings. Grader: *"The execution used supplied Contoso library findings and retrieved claim-system records…"*.
- Tool calls aren't attributed per skill in the export (`Skills[].ToolExecutions` is empty), so the split of the 29 calls between the two skills isn't visible. The order (8 claim-system lookups → 11 searches → 7 lookups + draft) fits research first, adjudication second.
- `library-research` has no rubrics, so it isn't graded; only the adjudication skill is.
- DB: `ADJ-9666AD27EB` → reset → 0 0 0 0.

**Reading it (n = 1):** decomposition works on this platform **when the top-level agent orchestrates, and skill descriptions are enough to steer it**.

**What made the platform call both skills (user question, 17:53)** — nothing configured as "use two skills":
1. **Registering `library-research`.** Every enabled skill is automatically available to the platform's coordinating step; there's no setting for which or how many. Even in attempt 1 it was called, third, after the failures.
2. **`library-research`'s description**: *"Use this first when a warranty claim needs facts from… the library"*, i.e. when to pick it.
3. **`warranty-assistant`'s description**: *"Expects the facts… to be gathered first with library-research and passed in with the request"*. It names the other skill and asks for its findings.

Plus one instruction change inside the adjudication skill ("work from the library facts supplied; search yourself only for a missing fact"), which bounds its own searching but doesn't set the order. No world-instruction, tool or code changes; the OneDrive slot was switched off only to match wce-main's tool list. The orchestration is two cross-referencing descriptions, so it's **suggestive, not guaranteed**. The stress claims test whether it holds.

**Does the platform run every registered skill? No: it picks per request (user question, 17:56).** No `chat` run ever named a skill (`chat --skill-id` returned API 500 at stage 0); the platform chooses. Tested in wce-dev with both skills registered:

| Request | Skills invoked | Tool calls | Execution |
| --- | --- | --- | --- |
| *"What is the boiling point of water at sea level in Celsius?"* | **none** | 0 | `0f74201c-6477-40ae-8b66-a193616e1743` (43 s) |
| *"What is the India labour rate per hour for warranty repairs effective from 1 April 2026, according to the rate card?"* | **library-research only** | 5 searches; answer *"INR 1,450 per hour… India \| INR \| 1450 \| 2026-04-01 \| 2027-03-31"* ✅ | `6aa56a4e-6c22-4486-8f44-600543f6ea16` (134 s) |
| *"Can you work up C-2026-04103…"* | library-research → warranty-assistant | 29 | `06a3c7a8-…` |

So unrelated skills are left alone. (Evaluations differ: `evaluate start --skill-id` scopes which samples and rubrics are used. And fine-tuning, per the playbook, takes the whole world's enabled skills.)

### Call-by-call audit of the successful run `06a3c7a8-…` (user question, 18:09)

| # | Call | Time | Output | Verdict |
| --- | --- | --- | --- | --- |
| 1–8 | DB: claim, asset, hours, history, prior claims, dealer, part, TSB index | 3.5–5.1 s | 0.2–0.7k | Needed |
| 9 | search "2200-AC warranty policy" (size 10) | 8.2 s | 36.8k | Broad but relevant |
| 10 | search "SEAL-KIT-RR India labour rate" | 3.8 s | 0.1k | ❌ nothing found |
| 11–12 | search part supersession/uplift; SPA-2023-FAB-IN | 7.4–7.6 s | 6.7–10.9k | Reasonable |
| 13 | search "submission SLA warranty claim" | 7.6 s | 28.9k | ⚠️ marginal |
| 14 | search ADD-IN-2.1 India addendum | 3.9 s | 15.5k | Needed |
| 15–18 | 4 searches for the rate cards (3 for Labour-Rates-By-Region) | 3.4–4.2 s | 4.5–5.6k | ⚠️ hunting |
| 19 | search "P-22120 parts price list superseded" (size 25) | 4.7 s | **52.3k** | ❌ unnecessary: price already from DB #7 |
| 20–26 | DB: the same 7 lookups as #1–7 | 3.4–4.0 s | small | ⟲ **7 repeats**: structural (fresh context in the adjudication skill) |
| 27 | DB: create_claim_adjudication | 3.8 s | 0.8k | Needed |
| 28 | sandbox: Python date arithmetic | 2.9 s | 0.2k | Fine |
| 29 | DB: get_claim | 3.7 s | — | ⟲ repeat |

**Time:** wall 805 s; **tool calls 126 s (16%)**; **679 s (84%) elsewhere**, i.e. model generation and orchestration (billing: `outputTokens` 40,102; `orchestratorCpuSeconds` 567; `inputTokens` 828,210 of which 700,032 cached). No tool call is an outlier (DB 3.4–5.1 s; search 3.4–8.2 s).

**Findings**
- **Time is in the model, not the tools.** Shortening runs means fewer model turns and less generated text, not faster tools.
- **The 7 repeated lookups are structural.** The first set (#1–8) came before research; 💭 most likely the top-level step, framing its questions (the export doesn't attribute calls to sessions). The adjudication skill starts fresh and fetches them again. Cost: ~26 s and little context.
- **Search waste ≈ half of the 180k characters searched:** #19 (52k, a price the DB already gave), #13 (29k, marginal), #10 (empty), and 4 rate-card searches where 2 would do.
- 🔬 **Billing counts 40 tool invocations; the record lists 29.** The 11 unlisted are probably the 2 skill calls plus hidden steps (hand-in attempts?). Not visible in the export.

**How a two-skill run is graded (user question, 18:04).** Per **skill invocation**, against **that skill's own rubrics**, automatically. 🖥️ In run `06a3c7a8-…`: `warranty-assistant` 5 rubric results (0.8 / 0.8 / 1.0 / 0.5 / 1.0); `library-research` **0**, because it has no rubrics. The run's top-level `RubricResults` is identical to `warranty-assistant`'s. So:
- ✅ **The final answer is graded properly**: the adjudication skill's rubrics judge the delivered decision, and its grader saw and credited the supplied findings (*"used supplied Contoso library findings"*).
- ⚠️ **The research step isn't graded at all.** A wrong fact from `library-research` would surface only as a wrong decision, with no attribution. 🔬 For fine-tuning, an ungraded skill may get no reward signal, so its habits wouldn't be trained.
- ➡️ **Before using this on wce-main, give `library-research` its own small rubric set**, e.g. returns exactly the facts asked, each with document and clause or row; adds nothing and decides nothing; reports not-found plainly; stays brief. Write it alongside rubrics v2. The research bulk stays in `library-research`'s context, and the adjudication skill completes within MAI's window. Next: the heaviest claims (exclusion 04185, repair-warranty 04189) to check it holds, then apply to wce-main as one stage change, and re-measure GPT-5.6-Sol on the same design.

## Stress check — heaviest claims (user: "proceed", 18:15)

Attempt 2 design, MAI, wce-dev. The CLI stops waiting at ~16 min (`timedOut: true`); runs continue on the platform, so final records were fetched afterwards with `executions get`.

| | **04185** exclusion (key: approve ₹199,175, TSB-C-0051) | **04189** repair warranty (key: approve ₹69,575, POL-WAR-4.2 6.1) |
| --- | --- | --- |
| Execution | `519691c1-ddd1-4fd3-99df-190c60cdcea3` | `cf7226f5-77f7-4a41-9041-d5487d3739d7` |
| `Skills[]` | library-research ❌ `ContextLength` ×2 → warranty-assistant ✅ | library-research ❌ `ContextLength` → library-research `UserInterrupted` |
| Final status | **Completed after 32.5 min** | ❌ **Failed after 17.4 min**, `ErrorCode 8 "Exception"` |
| Answer | ✅ **approve ₹199,175**, draft ADJ-BBD5F0E1B5; graded 1.0 / 1.0 / 1.0 / 0.83 / 1.0 | none |
| Calls · tool output | 57 · 809k chars | 32 · 422k |
| Research searches before the first overflow | 19 (484k) | 23 (422k) |

**Reading it:** the overflow **moved into the research skill**. On heavy claims the platform sends `library-research` many questions in **one** call, and one context can't hold 19–23 searches. 04185 still came right (the adjudication skill completed after two research failures), but slowly. 04189 failed. 🔬 `UserInterrupted` on 04189's second research call may relate to the CLI's wait ending, though 04185 continued past it.

**DB:** 04185's draft landed after the script's reset (during 04189's run) and was captured in `stress/db-after-04189.txt` and reset. Final check at 18:59: clean.

## Attempt 3 — cap each research call at three questions (19:05)

Changes to `library-research` only ([library-research.attempt3.md](library-research.attempt3.md)):
- description adds *"Ask it up to three specific questions per call, and call it again for further questions."* (steers the coordinator);
- instructions add *"Take at most three questions per call. If you were given more, answer the first three and list the rest under 'Not yet looked up', so they can be asked in a new call."* (the skill enforces the cap itself).

No shared 5-word phrase with the research rubrics draft. Re-running **04185**.

### Attempt 3 result — execution `de6810f4-32ad-43e5-9738-050b6db54e6c` (19:02–19:23 IST) ❌

| | Attempt 2 · 04185 | **Attempt 3 · 04185** |
| --- | --- | --- |
| `Skills[]` | research ❌ `ContextLength` ×2 → adjudication ✅ | research ❌ **`ContextLength` ×2** → adjudication **Running** when the run ended |
| Searches · calls · tool output | 57 calls, 809k | **39 searches (36 distinct queries)**, 65 calls, 766k |
| Outcome | ✅ approve ₹199,175 after 32.5 min | ❌ *"This request is taking longer than expected… reply with 'continue'"* after **20.7 min**; no answer, no grade |

DB after: clean (0 0 0 0).

**Reading it:** capping *questions* per call didn't cap *searches*. Each research invocation still ran ~20 searches at 10–25 results each until its window filled. **Skill wording (descriptions, instructions, caps) has not been enough to bound MAI's search behaviour on heavy claims**: three attempts at the research skill, two at search discipline in the single skill. In this world, with this search tool, MAI-CODE-5b's context window is the binding constraint.

### Why "five results" didn't hold (user question, 19:52)

| Run | Searches | `size` requested | Chars/search median (max) | Total |
| --- | --- | --- | --- | --- |
| single v2.2 · 04150 ✅ | 12 | 10 ×10, 15, 20 | 16k (39k) | 198k |
| single v2.2 · 04103 ❌ | 29 | 10 ×21, 20 ×5, 25 ×2, 15 | 29k (45k) | 577k |
| research a2 · 04103 ✅ | 11 | 10 ×7, 20 ×2, 25 ×2 | 7k (52k) | 172k |
| research a2 · 04185 | 32 | 10 ×12, 25 ×11, 20 ×3, 15, 5 ×5 | 25k (62k) | 759k |
| research a2 · 04189 ❌ | 23 | 10 ×9, 20 ×6, 25 ×8 | 12k (40k) | 416k |
| research a3 · 04185 ❌ | 39 | 10 ×24, 25 ×11, 20 ×4 | 10k (77k) | 637k |

- `size` is a tool argument **the model chooses per call**. A skill can only suggest it; nothing on the platform fixes a tool argument. MAI used 5 only 5 times out of 146 searches.
- "About five" was in the single skill (v2.2). In `library-research` it became "a few results at a time", **with no number** (an oversight).
- **Count matters more than size:** the failing runs made 23–39 searches, the successful ones 11–12. At 5 results, 39 searches would still be ~300k characters.

## Attempt 4 — explicit size and search budget (19:55)

`library-research` instructions: "asking for a few results at a time" → *"set size to 5 on every search, and use at most six searches per call; if a question is still open after that, list it under 'Not yet looked up'"*. Description unchanged from attempt 3. Run on **04185**.

### Direct search tests — `tools invoke m365__search_enterprise_files`, size 5 (20:10)

User: *"can you stop what is running now and fire the search query better formulated?… is there something in the excel workbook format that prevents it from getting searched easily?"* (attempt 4 run stopped at the client; it continued on the platform).

**Workbook format:** nothing blocks indexing. The cell text is extracted (`<sheet_1> … Flat Rate Labour Schedule — FY26 … HYD-PUMP-RR … 5.5`). But **document title metadata is empty** in all three workbooks, and **the phrase "rate card" appears in none of them**; their titles are "Flat Rate Labour Schedule — FY26", "Regional Labour Rates — FY25 and FY26" and "Parts Price List — FY26". The labour workbooks contain no dealer IDs, part numbers or claim dates.

| Query | Result |
| --- | --- |
| `HYD-PUMP-RR P-44120-A rate card labour allowance` | ❌ 5 inspection reports |
| `Flat Rate Labour schedule India labour rate 2026 HYD-PUMP-RR` | ❌ 1 review deck |
| `labour rate card India` | ❌ 1 review deck |
| `03-RateCards` | ∅ 0 |
| `Flat Rate Labour Schedule` | ✅ workbook rank 1 (2 hits, 9k chars) |
| `"Flat Rate Labour" HYD-PUMP-RR` | ✅ rank 1 (1 hit, 3k) |
| `Regional Labour Rates` | ✅ rank 1, with the flat-rate schedule (5 hits, 18k) |
| `"Regional Labour Rates" India` | ∅ 0 |
| `Parts Price List P-44120-A` | ✅ rank 1 |
| `Flat-Rate-Labour-FY26` / `Labour-Rates-By-Region-FY26` | ✅ rank 1, but file names are brittle (user: *"we cannot hard code file names… new files getting added every year"*) |

**Rule that follows:** search by the **kind of document, in its title words**, plus at most one term the document contains. Never pile on claim identifiers. Title words survive yearly files; picking the row in force on the repair date is left to the agent, as intended.

## Attempt 5 — search by document title words (20:20)

[library-research.attempt5.md](library-research.attempt5.md): *"Search by the kind of document you need, using the words of its title or its reference code: for example the flat rate labour schedule, the regional labour rates, the parts price list, a bulletin's or an addendum's reference code. Add at most one term that appears in that document… Do not add claim numbers, dealer IDs, dates or other identifiers the document would not contain."* Keeps size 5 and the six-search budget. No file names or years. No shared 5-word phrase with the v2 rubrics.

### Attempt 5 result — execution `2ff8c480-1423-48e5-80ce-2ff18a9a0be5` (20:22–20:40 IST) ❌

`Skills[]`: library-research ❌ `ContextLength` ×2 → warranty-assistant ❌ `UserInterrupted`; run **Failed**. 48 calls, 33 searches, 610k characters. (The stopped attempt-4 run went idle by 20:20 and wrote nothing; DB reset before and after.)

- **Size instruction mostly followed:** 25 of 33 searches at `size 5` (the rest 10).
- **Query style improved:** mostly short title or reference queries (`TSB-C-0051`, `ADD-IN-2.1 India 18 mo 5000 h`, `P-44120-A parts price list`).
- **Repeats remained:** `TSB-C-0051` ×4 and the labour-rates workbook ~×6 (MAI took the file name from earlier results), largely across the research restart.
- **5 results ≠ small:** searches averaged ~18k characters; one policy hit alone is ~36k.

**Capacity arithmetic for a heavy claim.** 04185 needs about 10 documents: the governing bulletin and the reversal bulletin, policy, addendum, flat-rate schedule, labour rates, parts list, partner agreement, the documentation bulletin, and inspection evidence. At ~18k each that's **~180k characters with zero waste**, against MAI's ~230–275k limit. Any repetition overflows it, and after an overflow the restarted skill repeats its searches.

**Conclusion after seven skill-level attempts** (two in the single skill, five in the research skill): on heavy claims, MAI-CODE-5b with this search tool sits *at* its context capacity even when it searches well. Skill wording cannot bring it safely under. Direction is a user decision: platform team (window size, shorter extracts), GPT-5.4-Mini (larger window; hand-in defect with the platform), or a change to how documents are served (conflicts with earlier user decisions).

## Is SharePoint search the wrong tool? (20:40, discussion with user)

User: *"this would not happen with vector search, would it?… is the SharePoint search approach flawed for the use case?"*

| | Vector / passage retrieval | Basis |
| --- | --- | --- |
| Size per result | ✅ Much smaller (top-k chunks, ~1–2k characters, instead of document extracts of ~18k) | 💭 |
| Identifier-heavy queries returning nothing | ✅ Similarity search always returns near matches | 🖥️ keyword-like misses measured above |
| Picking the right rate row | ⚠️ Can be worse: table rows get split from headers and effective dates, and FY25 and FY26 rows embed almost identically | 💭 |
| Near-miss documents (other claims' inspection reports) | ⚠️ Same risk | 💭 |
| Repeat searches and re-hunting | ❌ Unchanged: that's model behaviour | 🖥️ audit above |

**Verdict:** not flawed. It's how M365 agents really ground on SharePoint, and it works for GPT-5.6-Sol (29/30 🖥️). It is **coarse** for a small-window model: document-level extracts are the main context cost.

**Finer-grained options inside FT** (no tool built on top):

1. **Skill knowledge pins.** Native: `--knowledge` accepts `file`, `folder`, `library`, `subsite` and `site` 📄 (playbook `ft-cli.md`). A `file` entry resolves from its URL alone; a `folder` entry needs IDs. Pinning the rate-tables **folder** keeps the no-file-names rule. 🔬 How pinned knowledge reaches the model is undocumented. Test it in wce-dev on 04185 before relying on it. Trade-off: valuation becomes less of a retrieval test, so record it as a design choice.
2. **Platform team:** ask for passage-level or shorter extracts from `search_enterprise_files`.
3. **A vector index through a Graph connector:** heavier, and it changes the world's retrieval.

Not run yet; awaiting the user's direction.

## A large model for research and a small one for adjudication? (20:44)

User: *"if for the research part alone we could have the agent use an LLM and an SLM for the remaining? do we have the ability to control that"*

**What controls exist (checked 20:45–20:55)**

| Where | What it offers | Per skill? |
| --- | --- | --- |
| Skill record (`skills get -o json`) | No model field | ❌ 🖥️ |
| `run`/`chat --model` | One model for the whole run | ❌ 🖥️ |
| `run --model A --model B` | "Ordered multi-model execution" 📄; for evaluation, repeated models give one **blended** score 📄 | 🔬 Role assignment undocumented |
| `models set` | Turns a model on or off for the environment | ❌ 🖥️ |
| Environment `Models.SearchModels` / `TrainingModels` | Both empty; purpose undocumented | 🔬 |
| Execution record | Names no model, for the run or for any skill | Can't observe 🖥️ |

**Answer: not controllable today, as far as we can see.** Added to the platform-team note as a question.

**Design implications if it becomes possible** 💭

| Concern | Effect |
| --- | --- |
| What RFT learns | The SLM is tuned on adjudication given gathered facts. Clean, but the end result is a **hybrid**, not "SLM matches frontier" |
| Headroom | Several traps (governing bulletin, superseded addendum, rate on the repair date) are partly retrieval. If the LLM resolves them while researching, the SLM's task shrinks and headroom may collapse (goal 2) |
| Cost and latency | Research is where the tokens go (~610k characters in one heavy run 🖥️), so the LLM would still carry most of the cost. That weakens the SLM case |
| One variable per stage | Fine if the research model is held fixed across stages |

## Why Sol copes and MAI doesn't: measured from the stored records (21:00)

User: *"did Sol cope because of a larger window, cutting through the same bloated results? … is it the number of searches, or are failures re-executing the same searches and bloating the window?"*

Source: per-call records in Sol's 30-claim evaluation (`stage-2-base/eval-results-samples.json`, skill v1) and the MAI probe records. Analysis script in the session folder (`search_load.py`). An "attempt" is one skill sub-agent run, from its claim lookup to the next.

**Same claim and same skill v1, C-2026-04103** 🖥️

| | Searches | Results asked per search | Tool output | Outcome |
| --- | --- | --- | --- | --- |
| Sol, whole run | 8 | 25 | 211k | ✅ one attempt |
| MAI, attempt 1 | 7 | 10–25 | 275k | ❌ `ContextLength` |
| MAI, attempt 2 (fresh restart) | 7 | 10–20 | 259k | ❌ `ContextLength` |
| MAI, attempt 3 | 6 | 10 | 131k | ✅ (run ungraded) |

**Sol across all 30 claims** 🖥️: 2–12 searches per run (median 9); 7k–386k characters of tool output (median 208k). **6 of 30 runs took in more than 230k**, the level at which MAI overflows, and completed.

**Repeated content inside one attempt** 🖥️: share of search-result characters that are documents already retrieved earlier in the same attempt.

| | Repeat share |
| --- | --- |
| Sol, 30 runs | median 48% (range 0–68%) |
| MAI, attempts on 04103 and 04150 | 28–66% |

**What this shows**

1. **Before its first overflow, MAI searches about as much as Sol** (7 vs 8 on 04103). It isn't over-searching on its first pass.
2. **About half of each context is the same documents coming back again**, for *both* models. Overlapping queries return the same top documents (the policy is ~36k characters each time). That's how this search tool behaves, not a MAI fault.
3. **Sol simply has room for it.** Sol completed runs at up to 386k characters, so its usable window is at least that 🖥️; its exact size is 🔬. MAI fails at ~230–275k.
4. **A restart doesn't carry the old context forward.** Attempt 2 starts fresh and overflows again on its own volume, by repeating the same searches. Restarts multiply time and tokens: billed input tokens on 04103 were 0.57M for Sol and 1.72M for MAI. They don't enlarge any single window.
5. **No evidence MAI reasons worse on the same material.** It answered correctly on every run that fit (04150 v2.2; 04103 with the split skills).
6. **GPT-4o-class windows (128k tokens) would hit the same wall** 💭: Sol's heavier runs here (363k and 386k characters, plus a ~30k-token tool catalogue) are over ~120k tokens. The difference from past experience is likely the retrieval granularity, not the model.

## Why the same documents come back, and folder scoping (21:05)

User: *"is the same query being fired again? … is the problem that everything is in one library under different folders? would segregating them help?"*

**No query is repeated** 🖥️: Sol made 252 searches across 30 runs, with **0 exact duplicate queries**. The repeats are different queries matching the same "hub" documents.

| Most repeated documents (Sol, share of repeated characters) | Why they match many queries 💭 |
| --- | --- |
| FY26-Q2 and FY26-Q3 Warranty Review decks (27%) | They summarise claims, parts, partners and models, so they match almost anything |
| Global Warranty Policy (11%) | It mentions every concept |
| Other claims' inspection reports (~3–4% each) | Same product model: the near-miss distractors, by design |

**One library vs several:** 🔬, but likely irrelevant. Search spans everything the user can access; moving files to separate libraries wouldn't change results unless the query is scoped. The search tool has only `searchQuery`, `from` and `size` 🖥️ (schema), so it can't be scoped by parameter.

**Scoping in the query text works** 🖥️ (`tools invoke`, size 10):

| Query | Docs | Characters |
| --- | --- | --- |
| `labour rates India` | 5: labour workbook, 2 partner agreements, 2 review decks | 18,270 |
| `labour rates India path:"…/Warranty Operations/03-RateCards"` | 1: labour workbook | 1,687 |
| `warranty period path:"…/Warranty Operations/01-Policy"` | 4: policy and 3 addenda only | 15,055 |

The existing folders (01-Policy, 03-RateCards, 04-PartnerAgreements, 05-Reviews, 06-ClaimEvidence) are enough; **no restructuring is needed**. A folder path survives yearly files, unlike file names. Three probes only: wider testing is needed before relying on it.

Also available, but not tested: SharePoint MCP `getFolderChildren` (list a folder) and `readSmallTextFile`/`readSmallBinaryFile` (read one file).

**Open design point for the user:** naming the library's folders in the skill is navigation guidance (where kinds of document live), not an answer. It does tie the skill to this library's layout.

## Attempt 6: scope each search to its folder (21:15)

[library-research.attempt6.md](library-research.attempt6.md) = attempt 5 plus **one change**: *"Limit each search to the folder that holds that kind of document, by adding path:"<library address>/<folder>" to the query text… Only search without a folder when you do not know which folder holds the document."* The library address and folder list are in the skill. No shared 5-word phrase with the rubrics (v1 and v2 draft).

### Attempt 6 result: execution `214300df-ff60-46f7-9d3e-7e3b23e7f132` (21:16–21:26 IST) ✅

Both skills **Completed** in one pass; **graded**; decision **approve ₹199,175, TSB-C-0051, funding TSB = ground truth** 🖥️. Rubrics: 0.8 / 0.8 / 1.0 / 0.75, draft execution not scored (no draft recorded). DB untouched.

| 04185 on MAI | Attempt 5 (no scope) | **Attempt 6 (scoped)** |
| --- | --- | --- |
| Outcome | ❌ research `ContextLength` ×2, run Failed | ✅ one pass, graded, correct |
| Duration | 18 min (failed) | **10 min** |
| Tool calls / searches | 48 / 33 | **22 / 9** (all 9 scoped) |
| Tool output | 610k characters | **123k** (−80%) |
| Repeated-document share | 74% | **31%** |
| Billed input tokens | 1.92M | **0.69M** |

**How it searched** 🖥️: by reference codes the **claim system had returned**: `TSB-C-0051` (bulletin index), `SPA-2023-FAB-IN` (dealer record), `HYD-PUMP-RR` and `P-44120-A` (claim). Each was paired with the matching folder. Rate-card searches came back at 2–6k characters each.

| Remaining cost or quirk | Note |
| --- | --- |
| Last search was unscoped (library root, size 10): 32k, the largest single result | The "folder unknown" fallback |
| One query used a workbook file name learned from earlier results | The model's choice; not in the skill |
| Claim lookups done twice (once per skill) | Structural to the two-skill split |
| No draft recorded | Adjudication-skill behaviour, unrelated to search |

n = 1. Confirm on 04189 (failed in attempt 2) and 04103 before relying on it.

## Making scoping generic: design (21:30) 💭

The user asked how to avoid editing the skill whenever documents are added or moved, possibly using a cataloguing discipline and the database lookups.

**Three parts, each already partly in place:**

| Part | What it is | Where it lives | Status |
| --- | --- | --- | --- |
| 1. Filing convention | One top-level folder per *kind* of document, named for the kind. Files carry their reference code and version. New years and revisions go into the same folder | The library: a document-control rule for whoever files documents | ✅ Already true |
| 2. Skill states the convention, not the inventory | "Folders are named for the kind of document they hold; find the folder for the kind you need, and scope the search to it." No folder list | Skill | To test: discovery cost (below) |
| 3. Claim system supplies the search terms | Use the references the claim system returns: agreement reference, bulletin IDs, region, operation code, part number | Database (already) + one generic skill line | ✅ MAI did this unprompted in attempt 6 |

**What then needs a skill edit:**

| Change in the world | Skill edit? |
| --- | --- |
| New year's rate card in 03-RateCards | No |
| New or superseding bulletin (file in 02-Bulletins + bulletin-index row) | No |
| New partner (agreement file + dealer row with `agreement_ref`) | No |
| New *kind* of document (new folder) | No with part 2; yes with a folder list |
| Library moves | Yes: one address |

**Folder discovery options** (part 2) 🔬:

| Option | Cost | Note |
| --- | --- | --- |
| Read folder names off the address of the first search result | 0 extra calls | Relies on the model inferring the pattern |
| SharePoint `getSiteByPath` → `listDocumentLibrariesInSite` → `getFolderChildren` | 3 calls, verbose JSON | MAI did exactly this in attempt 5, unprompted |
| Keep a short folder list in the skill (attempt 6) | 0 calls | Edit only when a new kind of document appears |

**Not recommended now:** a controlled document register (a SharePoint list of document ID, kind, version, effective dates, status). It's realistic and fully generic, but its status and effective-date columns would hand the agent the supersession traps and reduce headroom (goal 2).

**Guard to add:** read documents through search, never by downloading the file. `readSmallBinaryFile` returns raw base64 (seen in attempt 5).

**Proposed sequence:** (1) attempt 6 on 04189 and 04103 → (2) attempt 7 = part 2 + part 3 wording (no folder list) on the same three claims → (3) adopt the winner in wce-main as one stage change, and re-measure Sol with it too.

### Attempt 6 on 04103 and 04189 (21:33–21:58, run in parallel)

User (21:32): *"forget about SOL… proceed"*. Sol is out of scope until MAI works.

| Claim | Execution | Skills | Tool output | Decision | Ground truth |
| --- | --- | --- | --- | --- | --- |
| 04185 | `214300df-…` | research ✅ → adjudication ✅ | 123k | ✅ approve ₹199,175 TSB | approve ₹199,175 TSB |
| 04103 | `4d12a942-…` | research ✅ → adjudication ❌ `ContextLength` → adjudication ✅ | 426k | ✅ approve ₹19,150 STD (rubrics 1/1/1/1) | approve ₹19,150 STD |
| 04189 | `68dcdf7b-…` | research ✅ → research ✅ → adjudication ✅ | 270k | ❌ decline ₹0 (determination 0.0) | approve ₹69,575 RW |

All three graded 🖥️. Both later runs exceeded the CLI's ~16-minute wait (25 min each) and were followed with `executions get`.

**04103: the adjudication skill searched for itself, unscoped.** Research finished with 6 scoped searches. The adjudication skill then ran 17 of its own searches, none scoped, including `C-2026-04103` at size 25 twice (45k each). It overflowed once, then succeeded on the platform's re-invocation. Scoping in only one skill leaves the other unguarded.

**04189: wrong answer, but from a world defect, not from scoping** 🖥️. The agent found the earlier control-board replacement (job J-00087, 2026-04-20, 42 days before) and priced RW exactly at ₹69,575. It declined because:

- the prior claim **C-2026-03110 does not exist in the claim system** (`get_claim` → "No claim with this reference exists"), and
- policy 6.1 requires the earlier replacement to have been made *"under warranty"*.

In `build/populate.py`, the repair-warranty claims (04189, 04190; training only) carry `prior_claim = C-2026-03110` only as a reference on the service job. That claim is never inserted into Claims, and both claims (serials 01980 and 01981) point to the **same** prior claim ID. The ground truth assumes a warranty claim the database denies, so **the corpus and the ground truth disagree** (AGENTS.md: the measurement is worthless). ⚠️ **Needs a world fix** (insert settled prior claims, one per asset, then re-run the gates). Flagged to the user; not changed.

## Attempt 7: generic scoping, no folder list (22:03–22:37, three claims in parallel)

[library-research.attempt7.md](library-research.attempt7.md) drops the folder list. It states the convention (*"one folder for each kind of document, named for that kind, and every document's address shows its folder"*), scopes searches once folder names have been seen, uses claim-system references as search terms, and says *"do not download files"*. [warranty-assistant.attempt7.md](warranty-assistant.attempt7.md) = attempt 2 plus the same generic scoping and no-download line. No shared 5-word phrase with the rubrics.

| Claim | Execution | Skills | Scoped searches | Tool output | Decision |
| --- | --- | --- | --- | --- | --- |
| 04185 | `8577bdbd-…` | research ✅ → adjudication ✅ → adjudication ✅ | 4 of 10 | 105k | ✅ approve ₹199,175; **2 drafts written** (one per invocation) |
| 04103 | `6e8ca35f-…` | research ✅ → adjudication ✅ → adjudication ✅ | 3 of 12 | 138k | ✅ approve ₹19,150 |
| 04189 | `a6369412-…` | research ✅ → adjudication ✅ → adjudication stuck "Running" | 6 of 27 | 383k | ❌ no answer: *"taking longer than expected… reply continue"* |

🖥️ Findings:

- **MAI invents folder names** when it has to infer them: `05-Policies` and `02-RateCards`, both of which returned 0 results. Scoping fell from near-total (attempt 6 research skill) to 27% of searches.
- **"Do not download files" was ignored** on 04189: SharePoint navigation + `readSmallBinaryFile` ×2.
- **The adjudication skill was invoked twice** on every claim. Both invocations were graded (the first set at 0.0 on outcome, the second at 1.0); which set counts is 🔬. On 04185 the duplicate wrote **two drafts**. Cause unknown; not seen in attempt 6.
- Runs took 22–30 min (attempt 6 on 04185: 10 min).

DB reset after the runs (2 drafts on 04185 removed → 0 0 0 0). wce-dev restored to **research attempt 6 + adjudication attempt 2** (verified).

### Revised design: what can be generic, and what must be stated (22:40) 💭

| Changes… | Example | Mechanism | Skill edit? | Evidence |
| --- | --- | --- | --- | --- |
| Often | New year's rate card, revised addendum, new bulletin, new partner | File into the kind's folder; the claim system supplies the reference; search scoped to that folder | **No** | 🖥️ attempt 6: MAI used DB references as terms unprompted |
| Rarely | A new *kind* of document (a new folder) | The folder map must be **given** to the model; MAI does not infer it reliably | Depends where the map lives | 🖥️ attempt 7: invented folders |

Where the folder map (kind → folder) can live:

| Option | Skill edits | World change | Note |
| --- | --- | --- | --- |
| A. In the skill (attempt 6) | One line, only when a new kind of document is introduced | None | Simplest; proven |
| B. In the claim system: a document-locations table returned by a lookup | None | New table + MCP read tool or field | Realistic (document control); adds a tool to the line-of-business system: user decision |
| C. A "library guide" SharePoint list in the site, read with native list tools | None | New list | No new tool, but the SharePoint list tools are verbose and chain 2–3 calls |

**Recommendation:** A now. B or C only if zero-edit becomes a requirement. Also give the adjudication skill the same explicit map, or stop it searching at all: its unscoped searches caused the 04103 overflow in attempt 6.

## World v2.3 and attempt 8: folder map in one section (2026-10-06, 06:57–07:19)

User (06:44): *"provide the folder map as a part of instructions… in such a way that i can easily locate it… and change it later"* and *"what do we do about the issue with 04189?"*

**World v2.3** fixed the 04189 defect: prior claims C-2026-03110 and C-2026-03111 were seeded as `Paid`, one per asset, with a gate against dangling references. Details are in [journey-record-2026-10-06.md](../../../docs/evidence/journey-record-2026-10-06.md) G.1.

**Attempt 8 skills:**

- [library-research.attempt8.md](library-research.attempt8.md): attempt 6's scoping, with the map moved to a final **`## Library folders`** section, plus "search with the reference the claim system gives you" and "do not download files".
- [warranty-assistant.attempt8.md](warranty-assistant.attempt8.md): attempt 2, plus "scope any search you make to a folder under Library folders" and the same section.

**To change the map later, edit only the `## Library folders` section at the end of each skill.**

| Claim | Execution | Skills | Searches (scoped) | Tool output | Decision vs ground truth | Rubrics (adjudication) |
| --- | --- | --- | --- | --- | --- | --- |
| 04185 | `33cee794-…` | research ✅ → adjudication ✅ ×2 | 8 (7) | **57k** | ✅ approve ₹199,175 TSB-C-0051 | 0/0/1/0/1 and 0/0/1/0.2/1: **hand-ins rejected** (below) |
| 04103 | `97c5ad36-…` | research ✅ → adjudication ✅ | 17 (8) | **116k** | ✅ approve ₹19,150 | 0.8/0.8/1/1/– |
| 04189 | `c0cbeec3-…` | research ✅ → adjudication ✅ | 12 (12) | **67k** | ✅ **approve ₹69,575, POL-WAR-4.2 6.1, RW** | 0.8/0.8/0.875/0.75/– |

🖥️ **No `ContextLength` on any claim.** 16–21 min each, run in parallel. **3/3 decisions correct**, including 04189 on world v2.3.

| Compared with | 04185 tool output | 04103 | 04189 |
| --- | --- | --- | --- |
| Attempt 5 (no scope) | 610k ❌ | – | – |
| Attempt 6 (map in research only) | 123k | 426k (adjudication overflowed once) | 270k (wrong: world defect) |
| **Attempt 8** | **57k** | **116k** | **67k** |

**Rejected hand-ins on MAI: the platform's finish-tool defect** 🖥️. On 04185 the adjudication skill's full answers were rejected by the finish tool, and the only accepted hand-ins were probes: *"A test [cite:claim]"* and *"Test sentence [cite:src1]"* (grader notes). The platform re-invoked the skill; the top-level agent then wrote the (correct) answer to the user. The grader scores the skill's accepted hand-in, so outcome scored 0.0.

Across attempts 6–8, **every duplicate adjudication invocation followed a rejected hand-in**: 4 of 11 invocations in attempts 7–8, 0 of 4 in attempt 6. This is the defect already reported for GPT-5.4-Mini ([platform note](../../../docs/evidence/platform-issue-finish-rejection.md)), now seen on MAI. It's independent of search scoping. It also wrote 3 drafts on 04185 (one per hand-in cycle).

DB reset after the runs (3 drafts on 04185 → 0 0 0 0; prior claims stay `Paid`). **wce-dev now holds attempt 8 in both skills.**

## Attempt 8b: remove the "leave the sources list empty" line (2026-10-06, 07:59–08:20)

User: *"what should we do about the above? Will it be an issue if we move this to wce main and proceed with the full blown run?"*

**Hypothesis** 💭: MAI's rejected hand-ins came with probes such as *"Test [cite:claim]"* and *"Test sentence [cite:src1]"*, i.e. it was trying out citation syntax. Our adjudication skill told it *"Put every citation inside the answer text, and leave the hand-in's separate sources list empty"*. That line was a v2.1 guess for GPT-5.4-Mini, and it didn't help there. MAI's accepted hand-ins *did* carry a sources list.

[warranty-assistant.attempt8b.md](warranty-assistant.attempt8b.md) = attempt 8 minus that one line. Research skill unchanged (attempt 8). Run: 04185, the most rejection-prone claim, ×3 in parallel.

| Rep | Execution | Adjudication invocations | Hand-in rejected | Decision | Rubrics (outcome / determination / grounding / presentation / draft) | Drafts |
| --- | --- | --- | --- | --- | --- | --- |
| a | `7960457c-…` | 1 | no | ✅ approve ₹199,175 TSB | 1.0 / 1.0 / 1.0 / 0.8 / 1.0 | 1 |
| b | `6d0418ef-…` | 1 | no | ✅ approve ₹199,175 TSB | 0.8 / 0.8 / 1.0 / 0.83 / **0.0** | 2: ₹194,375 then ₹199,175 (grader: "two contradictory drafts") |
| c | `65529d26-…` | 1 | no | ✅ approve ₹199,175 TSB | 1.0 / 1.0 / 1.0 / 0.8 / – | **0** ("not recorded the adjudication yet") |

Tool output 61k / 61k / 161k; no `ContextLength`; 14–20 min.

**MAI adjudication hand-ins, all records** 🖥️ (grader notes read by hand):

| Adjudication skill | Sources line | Invocations completed | Rejected |
| --- | --- | --- | --- |
| v1, v2.2, attempt 2 (incl. attempt 6) | present | 8 | 0 |
| attempts 7–8 (+ scoping, no-download, map section) | present | 8 | **4** |
| **attempt 8b** | **removed** | 3 | **0** |

**Reading** 💭 🔬: consistent with the line contributing when combined with the attempt 7–8 additions, but **not proven**. The line was also present in the 8 clean early invocations, and the rejections all fell between 22:03 (10-05) and 07:19 (10-06), so a time-varying platform cause can't be ruled out. n = 3.

**What 8b exposes instead:** model behaviour the rubrics should and do score: a wrong first draft amount, duplicate drafts, a missing draft. That's genuine headroom for RFT.

**Adopted:** 8b is the adjudication skill carried forward; the line had no measured benefit on either model. wce-dev holds research attempt 8 + adjudication attempt 8b. DB reset after the runs (3 drafts on 04185 → 0 0 0 0); snapshot in `docs/evidence/experiments/research-skill-wce-dev/attempt8b/db-after.txt`.
