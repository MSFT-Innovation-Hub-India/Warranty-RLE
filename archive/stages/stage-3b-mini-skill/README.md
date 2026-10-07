# Stage 3b-mini-skill — Skill v2 on GPT-5.4-Mini

**Status:** 🧪 single-claim tests done 2026-10-05; **no evaluation run yet**. Skill v2 is live on `cf00d339`.

**Why.** Stage 3-mini-base showed GPT-5.4-Mini fails mainly at:
- **handing in** its answer: 22 of 28 runs had rejected hand-ins;
- **researching before concluding**: 17 of 28 never searched a document;
- **repeating identical calls**: 4.8 per run.

The user chose to climb with GPT-5.4-Mini (MAI's run and tune models differ) and asked for the skill changes, plus a single-claim check before any long run.

## The one change (against stage 3-mini-base)

| | 3-mini-base | **3b** |
| --- | --- | --- |
| Skill instructions | v1 ([warranty-assistant.v1.md](warranty-assistant.v1.md)) | **v2** ([warranty-assistant.md](warranty-assistant.md)): v1 word for word, plus the two sections below |

Model (GPT-5.4-Mini), rubrics (pinned, unchanged on the platform), samples, MCP and world are the same.

### What was added, and why it doesn't echo the rubrics

| Added line (v2) | Problem it targets | Nearest rubric item | Why it's guidance on approach, not the standard |
| --- | --- | --- | --- |
| Start with the claim, then the asset; they tell you what else you need | No plan | — | Order of work only; no rule or answer |
| Read the library documents before concluding; don't call a document unavailable until you've searched | 17/28 runs never searched; "documents unavailable" claimed without searching | Grounding: *"…grounds them in the global warranty policy… regional addenda… technical service bulletins…"* | Says *when* to read, not *which* document governs or what it says. v1 already listed the same sources |
| The library's folders (01-Policy … 06-ClaimEvidence) | Search hunting (MAI: 12 searches for rate cards) | — | Navigation only |
| Use what you've retrieved; don't fetch the same record twice | 4.8 identical repeats per run | — | No rubric scores efficiency |
| Record the claim-system action once, after concluding | 2 drafts per run (an early hold, then the real one) | Draft execution: *"…the appropriate draft was actually recorded…"* | v1 already asked for the draft; this adds *timing* |
| Hand in once, complete; cite sources in the text; if rejected, fix the format and resubmit the same full answer, not a shorter one | Rejected hand-ins replaced by "could not finish" notes | — | About the platform's hand-in, which no rubric covers |

Check: the new text (999 characters) shares **no 5-word phrase** with any of the 28 rubric items (script in the evidence record). Applied with `skills update cf00d339 --instructions <v2 body>`. Platform `Prompt` == v2 (only line endings differ); `Rubrics` == pinned.

To revert: `skills update cf00d339 --instructions (Get-Content docs\evidence\stage-3b-mini-skill\skill-v1-platform.json → Prompt)`.

## Single-claim tests — 2026-10-05

Same prompts and model as the failed hand runs. Executions `b377f130-cf32-4689-af3e-70ef6042fbf6` (04150) and `ad565697-c2af-4d31-8a0b-56bfa1198c7f` (04103). Files: [docs/evidence/stage-3b-mini-skill/probes/](../../../docs/evidence/stage-3b-mini-skill/probes/).

| | 04150 v1 → **v2** | 04103 v1 → **v2** |
| --- | --- | --- |
| Documents read **before** concluding | 0 → **8** ✅ | 0 → **6** ✅ |
| Calls (minimal path ~13) | 27 → 28 | 22 → **12** ✅ |
| Identical repeated calls | 6 → **10** ❌ | 4 → **0** ✅ |
| Drafts recorded | 2 → 1 | 2 → **1** ✅ |
| **Hand-in rejected** | yes → **yes** ❌ *"The accepted hand-in is an inability statement… [the covered conclusion was] in its attempted hand-ins"* | yes → **still format trouble** ❌ *"begins with a tool-formatting disclaimer… supplies no valid source list"* |
| Delivered decision | not delivered → **hold** ❌ (key: approve ₹755,050) | not delivered → **hold** ❌ (key: approve ₹19,150) |
| Time | 4.9 → 6.0 min | 8.7 → 4.1 min |

**Reading it (n = 2)**
- ⚠️ **Confound: two things changed, not one.** The world offered **136** tools during these tests, against 137 for the v1 hand runs that morning. **`m365__call_copilot`** (Microsoft 365 Copilot chat) disappeared on the platform side; we didn't change it. Earlier runs used it (stage 0). Any v1 → v2 difference could partly come from its absence. 🔬
- ✅ **The approach guidance worked.** Both runs read the documents *before* concluding, and 04103 came close to the minimal path (12 calls, no repeats, one draft).
- ❌ **The hand-in guidance didn't.** Rejections continue; the grader again saw the correct conclusion only in rejected attempts (04150). "Cite sources in the text" didn't stop it: the platform's hand-in apparently expects a structured source list, which the small model gets wrong. 🔬 The exact format rule is invisible to us (diagnostics API 403).
- ❌ **Correctness didn't improve.** Both delivered a hold. On 04103 the hold asked for "correct serial / proof of supply / commissioning evidence", a new failure.
- **Decision: don't run the 30-claim evaluation yet.** The main blocker, rejected hand-ins, is untouched, and we can't see its cause.

## v2.1 + OneDrive off — 2026-10-05 (user away; recommended option taken)

Two changes made together, because they act on different problems:
1. **Skill v2.1.** Hand-in line 2 changed from *"Cite your sources inside the answer text."* to *"Put every citation inside the answer text, and leave the hand-in's separate sources list empty."* The basis: every hand-in seen accepted had an empty sources list. v2 kept as [warranty-assistant.v2.md](warranty-assistant.v2.md). No 5-word phrase shared with any rubric; platform `Prompt` == v2.1; `Rubrics` == pinned.
2. **OneDrive slot disabled** (`tools disable c33f274c-2451-45df-8bfa-99281b9c11b8`): 136 → **118 tools**, stable across 4 reads. It's unused by the scenario and saves ~2.8k tokens per turn.

Executions `934bcb81-c91b-439b-9b05-db639a848626` (04150, 7.3 min) and `c6a77b7d-5176-49b8-9b3d-646321677ecd` (04103, 13.6 min). Files: [probes-v2.1/](../../../docs/evidence/stage-3b-mini-skill/probes-v2.1/).

| | 04150: v1 → v2 → **v2.1** | 04103: v1 → v2 → **v2.1** |
| --- | --- | --- |
| Calls · document searches | 27·8 → 28·8 → **30·17** | 22·7 → 12·6 → **14·0** |
| Repeated identical calls | 6 → 10 → **4** | 4 → 0 → 3 (claim fetched ×3) |
| Input tokens | 986k → 953k → **5,021k** ❌ | 658k → 310k → — |
| Delivered | not delivered → hold → **"covered under TSB-C-0051", no amount** | not delivered → hold → **run failed** |
| Stored (not delivered) | approve ₹755,050 → hold → **approve ₹755,050** ✅ | approve ₹19,150 → hold → error text |
| What happened | **Hand-in still degraded.** Grader: *"the final hand-in begins with inability to calculate… the successful submission has no inline citations… no arithmetic"*. The correct worked answer was stored but not delivered | Platform **`ErrorCode 8, "Exception"`**: *"We encountered an issue while processing your request."* Not graded. It never searched; it tried SharePoint **browsing** tools (`listDocumentLibrariesInSite`, `listLists`, `getDefaultDocumentLibraryInSite`) and `teams__ListChats` |

**Reading it (n = 2 per variant)**
- ❌ **The hand-in problem survives three variants of guidance** (v2: "cite in text"; v2.1: "leave the sources list empty"). The correct answer keeps being produced and not delivered. Skill wording can't reach whatever the format check rejects.
- ⚠️ The folder hint may have **backfired** on 04103: it browsed SharePoint instead of searching. On 04150, 17 searches still didn't surface the rate cards, and tokens went up five-fold. n = 1 each, a hint only.
- ⚠️ **Each variant fails differently on the same two claims.** Two claims per variant can't separate the effect of a change from run-to-run variation.
- DB after: no drafts recorded → reset → 0 0 0 0.

**Where this leaves stage 3b:** skill wording has gone as far as it can on the hand-in without seeing the format rule. Waiting on the platform team (diagnostics API, or the finish tool's schema): [platform-issue-finish-rejection.md](../../../docs/evidence/platform-issue-finish-rejection.md).

## MAI-CODE-5b on skill v2.1 — 2026-10-05 (the user switched the climb to MAI)

User: *"we will baseline with mai-code-5b and fine tune the flash version of it… make sure we are getting back predictable results from it before going full hog."* Executions `4c2b8243-009b-418e-947a-e43f0b9f3f18` (04150) and `09e562d7-9860-4ff7-9c2e-3d21bbd9cd06` (04103). Files: [probes-mai-v2.1/](../../../docs/evidence/stage-3b-mini-skill/probes-mai-v2.1/).

| | 04150: v1 → **v2.1** | 04103: v1 → **v2.1** |
| --- | --- | --- |
| Answer (stored and delivered) | ✅ ₹755,050 → ✅ **approve ₹755,050** | ✅ ₹19,150 → ✅ **approve ₹19,150** |
| Draft recorded | 0 → **1** ✅ | 0 → **0** ❌ |
| Calls · searches · repeats | 20·13·0 → **43·22·10** | 42·20·? → **43·25·11** |
| Skill sub-agent | Completed → **Failed ×2, `ContextLength`** | Failed ×2 → **Failed ×2, `ContextLength`** |
| Graded | yes → **no** | no → **no** |
| Time | 7.6 → 10.1 min | 10.6 → 11.0 min |

**Inside the 21 searches on 04150** (all calls ran without error):
- ✅ Call 13 (`"Warranty Operations/03-RateCards"`, the folder hint) returned **both rate cards with the needed rows**: COMP-RR = 9 h; India ₹1,450 from 2026-04-01.
- 🔁 It searched for them again anyway (calls 40–41).
- ❌ **7 searches for an inspection report that doesn't exist**. Searching the claim number returns *other* claims' reports (04185–04187).
- ⚠️ **7 of 21 searches returned nothing**: long many-word queries, `site:` syntax, and once plain `TSB-C-0051` (10 hits when phrased differently later).
- Every search asked for `size=25`; extracts run up to ~40k characters each.

**Reading it**
- ✅ **MAI is right** on both claims, every time (4 of 4 runs across v1 and v2.1).
- ❌ **Its skill overflows its context window** on longer runs. That causes the restarts (which look like repeats), the missing grades, and probably the missing draft. **Fix this before any baseline:** ungraded samples drop out of an evaluation's score.
- The overflow comes from search volume: 22–25 searches with 25 results each, many of them re-checks or a hunt for a document that doesn't exist.

## MAI on skill v2.2 (search discipline) — 2026-10-05

v2.2 adds one line: *"Library searches return long extracts. Ask for a few results at a time (about five), search with specific terms such as a document's reference code or its folder name, and stop searching once you have what the step needs. If two searches for a document find nothing, move on."* No 5-word phrase shared with the rubrics; Prompt == v2.2; Rubrics == pinned. v2.1 kept as [warranty-assistant.v2.1.md](warranty-assistant.v2.1.md). Executions `a2db95bc-7677-4d22-bc55-1d652e082a64` (04150) and `0af5028b-33e4-4efa-8267-631be8e65c4a` (04103). Files: [probes-mai-v2.2/](../../../docs/evidence/stage-3b-mini-skill/probes-mai-v2.2/).

| | 04150: v2.1 → **v2.2** | 04103: v2.1 → **v2.2** |
| --- | --- | --- |
| Skill sub-agent | Failed ×2 `ContextLength` → **Completed, one pass** ✅ | Failed ×2 → **Failed ×2 `ContextLength`** ❌ |
| Calls · searches · repeats | 43·22·10 → **19·12·0** ✅ | 43·25·11 → 52·29·15 ❌ |
| Results requested per search | 25 → **10** (15 and 20 once each) | 25 → mostly 10, some 20–25 |
| Tool output | 647k → **201k** chars | — → 627k |
| Draft · graded | 1 · no → **1 · yes** (0.83 / 0.8 / 1.0 / 0.67 / 1.0) ✅ | 0 · no → 0 · no |
| Answer | approve ₹755,050 → **approve ₹755,050, verified correct** ✅ | approve ₹19,150 → approve ₹19,150 (stored; ungraded) |
| Time | 10.1 → 11.1 min | 11.0 → 16.8 min |

**Reading it**
- ✅ **On 04150 the fix worked completely.** One pass, near the minimal path (19 calls against ~13), no repeats, draft recorded, graded, correct. For the first time a small model got a claim right end to end and was graded.
- ❌ **04103 still overflows.** The seal-kit claim invites more research (clause 5.4, inspection evidence) and MAI kept searching (29 searches, plus SharePoint browsing calls). It asked for ~10 results, not ~5.
- **Search discipline helps but isn't enough on its own.** The remaining lever is **splitting the work across skills**: each skill runs as its own sub-agent with its own context window. The user's view: lever 3 "seems inevitable"; document slimming (lever 2) is ruled out.

**Delivery check corrected.** "Successful hand-in" alone isn't evidence of a rejection (MAI's grader uses it for full answers). The check now flags (a) explicit rejection or non-answer wording, or (b) **a delivered decision, as described by the grader, that differs from the stored one** (e.g. 3-mini-base 04152: stored approve ₹197,000, delivered "cannot yet be conclusively decided"). Tests 43/43; GPT-5.6-Sol 0 flags; 3-mini-base now 19/28 flagged, 1/28 verified correct.
