# The Contoso warranty RLE: journey

How this world is built, where the climb stands, and what we learned on the way. **Where we are** is all you need on a return visit.

| Part | What it gives you |
| --- | --- |
| [1. The scenario](#1-the-scenario-in-two-minutes) | What the agent does, where its facts live, why it's hard, and how a run works |
| [2. The world](#2-the-world) | Where the world lives, and where its build recipe is |
| [3. The climb](#3-the-climb) | The stages on world v3, [stage 0 in brief](#stage-0-in-brief), [stage 1 in brief](#stage-1-in-brief-the-reward-now-tracks-correctness) and [the road ahead](#the-road-ahead); detail in [stages/](../stages/README.md) |
| [4. What we carried from the first climb](#4-what-we-carried-from-the-first-climb) | The lessons from world v2 that shaped v3 |
| [Appendix](#appendix--helper-snippets) | Helper snippets |

Legend: ✅ done · ⬜ not started · 🖥️ measured here · 📄 upstream guidance · 🔬 unverified · 💭 reasoning. The verbatim record is in [evidence/](evidence/README.md).

---

## Where we are

| | |
| --- | --- |
| **Status** | **World v3. Stage 4 exploratory pilot submitted (2026-10-09, 10:59 IST).** User explicitly waived measured-headroom prerequisite; stage 3 gate remains unpassed. Job `c77feaed-96de-4b88-9802-e0f265601eb8`: Running, training/deployment NotStarted, not ready for evaluation. No tuning gain measured |
| **Next** | Monitor [stage 4](../stages/stage-4/README.md) status; verify sample selection and actual deployment/model ID before evaluating. Snapshot captured 90 prompts (60 Training + 30 Evaluation inventory), not proof of training on either bucket. Stronger stage 1 skill retained; preflight SQL baseline 0 0 0 0; do not reset during an active tuning job |
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
| [1](../stages/stage-1/README.md) | Hand-written rubrics ([reviewed set](../stages/stage-1/rubrics.md)) | **0.637** | **23/30** | The reward now tracks correctness better: ranks right above wrong 93% (was 83%); correct answers lose points unless working, sources and next action are shown. Weakest: authority and action (0.46) |
| [2](../stages/stage-2/README.md) | Enrich no-op; platform refinement rejected; our approach guidance (2b) | **0.526** | **17/29**, hand-checked | Regression vs matched stage 1: 0.637 · 22/29; more calls and non-answers. User excluded 04130 |
| [3](../stages/stage-3/README.md) | Existing stage 1 `Simple` vs new `BestOfN`, N=4, same skill/model and 29 claims | Unmeasured cohort | Unmeasured cohort | Stopped by user: service failure before claim execution; probe only 0.900 · 1/1; headroom gate not passed |
| 4 | RFT on `mai-code-1-flash`; compare with GPT-5.6-Sol | | | |

### Stage 0 in brief

**What we did**
- Rebuilt the world as **v3**. One claim-system call (`get_claim_dossier`) replaces nine, and it returns records only, so no tool gives away an answer. The labour rate cards are one workbook. The answer key is unchanged.
- Ran the honest starting point on all 30 eval claims: **MAI-CODE-5b**, the naive business-brief skill, and the rubrics the platform generated.
- Found that **5 claims per evaluation job** cuts a 30-claim run from ~12 h to ~2.5 h. Each job pays ~9 min of platform start-up, whatever the claim.

**Result** 🖥️

| Rubric score | Correct (hand-checked) | Context overflows | Tool calls per claim | Agent time per claim |
| --- | --- | --- | --- | --- |
| **0.744** | **23/30 (77%)** | **0** (the blocker in v2) | median 10 (2–32), against a ~5-call minimum | median 6.6 min (v2: 15–30) |

**What it shows: the headroom the climb works on**

| Weakness | Evidence | Addressed by |
| --- | --- | --- |
| **Authority: 0/2** | Both goodwill requests beyond the requester's authority were declined, not escalated | Stage 1 (a rubric checks escalation), stage 2 (skill) |
| **Echoed hand-ins: 4 claims lost** | MAI handed in the user's question as its answer (5 runs; one recovered on re-run) | Stage 2 (how to hand in); with the platform team |
| **The generated rubrics overrate** | 0.744 rubric vs 77% correct: wrong answers scored 0.85–1.0, correct but terse ones below 0.6 | Stage 1 (hand-written rubrics) |
| **Wandering** | Folder browsing, file downloads, searches for documents the claim doesn't need | Stage 2 (method and folder map), stage 4 (RFT) |
| The scorer misreads | 7 correct answers misread (labour sub-line taken as payable, missed negations) | ✅ Fixed: 23/30 automatically, matching the hand check |

Detail: [stages/stage-0](../stages/stage-0/README.md) · [per-claim table](../stages/stage-0/run-summary.md) · [hand check](../stages/stage-0/hand-check.md).

### Stage 1 in brief: the reward now tracks correctness

**What we did**
1. **Fixed the ground-truth scorer.** It now scores both stages without a hand check (53/53 tests).
2. **Reviewed and revised the hand-written rubrics.** Six rubrics; [stages/stage-1/rubrics.md](../stages/stage-1/rubrics.md) ends with a table of each change and the evidence for it. The main ones:
   - Rubrics can now be met when a record is genuinely missing.
   - Authority now requires escalation "rather than approving, declining outright or leaving it open".
   - Sources are updated for world v3.
   - Items that rewarded boilerplate are dropped.
   - After the first batch, valuation was made to apply **only to covered claims**: it had scored a correct decline at 0.0.
3. **Ran stage 1** on all 30 claims. Only the rubrics changed: same model, skill and prompts.

**Result** 🖥️

| | Stage 0 (generated rubrics) | **Stage 1 (hand-written)** |
| --- | --- | --- |
| Correct | 23/30 | **23/30**: unchanged, as it should be, since the agent didn't change |
| Rubric score | 0.744 | **0.637** |
| Average score, right answers | 0.86 | **0.72**: now marked down when working, sources or next action aren't shown |
| Average score, wrong answers | 0.37 | 0.38 |
| **Right answer scored above a wrong one** | 83% | **93%** |

The hand-written rubrics separate right from wrong more reliably, and that score is the reward RFT will optimise.

**What it shows for stage 2.** The weakest rubrics:
- **Authority and action (0.46):** naming the next action and who takes it; escalating goodwill beyond the requester's authority.
- **Precedence (0.54) and grounding (0.54):** explaining why an instrument governs, and citing clauses.

There are also hand-in failures: one echoed question and two answers cut to a stub (e.g. *"Approve the claim."*) even though the drafts written to the claim system were complete. Two answers claimed the documents "aren't accessible" without searching for them.

**What went wrong during the run, and the fixes**
- **Stalled claims.** The platform reran 3 claims from scratch: the agent finished each attempt, but the platform never registered it as done. Evidence added to the [platform note](evidence/platform-issue-finish-rejection.md). The runner, [scripts/eval-batches.ps1](../scripts/eval-batches.ps1), now cancels after 15 minutes without progress and requeues automatically.
- **The `frontier-tuning` CLI broke mid-run.** An interrupted upgrade left it unusable, and the runner waited silently for 2 hours. Version 0.3.16 restored exactly; the runner now warns when it can't read status.

**What stage 1 did and didn't do.** It didn't make the agent any better: correctness is 23/30 in both stages, by design. It made the **measurement** better. Stage 0's generated rubrics could give a wrong answer full marks (04172 scored 1.0) and a correct one half marks. Under the hand-written rubrics, a randomly chosen right answer outscores a wrong one 93% of the time instead of 83%. That matters most at stage 4, where the rubric score is the RFT reward: rubrics that reward wrong answers would train the model to give them. Two wrong answers still score above 0.6 (04172 at 0.63, 04166 at 0.67), so the reward isn't perfect yet; stage 2 watches them.

Detail: [stages/stage-1](../stages/stage-1/README.md) · [per-claim table](../stages/stage-1/run-summary.md) · [rubrics and review](../stages/stage-1/rubrics.md).

#### What we do next: stage 2

**Stage 2 is skill refinement: it improves the agent itself.** The measuring stick from stage 1 (the hand-written rubrics) stays fixed, as do the model (MAI-CODE-5b) and the 30 prompts. **Only the skill changes**, in two measured steps:

| Step | What changes | Who writes it | What it tells us |
| --- | --- | --- | --- |
| **2a · The platform's tools** | `skills enrich` rewrites the skill's description; `skills refine` runs the agent on the **Training** claims (never the 30 evaluation claims), analyses where it lost points against the rubrics, and proposes a refined skill | The platform | What the platform's own optimisation is worth (AGENTS.md goal 3: find out what the tools actually do) |
| **2b · Our guidance** | On top of 2a: how to approach a claim, the library's folder map, and how to hand in a complete answer | Us. Each edit is shown next to the rubric it serves, without echoing the rubric's wording | What domain guidance adds beyond the platform's tools |

**Why these targets.** Stage 1 showed where the points are lost:

| Weakness | Evidence (stage 1) | What the skill can do about it |
| --- | --- | --- |
| **Authority and action (0.46)** | Both goodwill claims declined instead of escalated; next action often unnamed | Say that a goodwill request beyond the requester's authority goes to the role in the authority matrix, and that every answer names the next action and who takes it |
| **Precedence (0.54) and grounding (0.54)** | Governing instrument named without saying why; clauses not cited | Ask for the reasoning across bulletin, addendum and policy, with the clause behind each term |
| **Hand-in failures** | 1 echoed question, 2 answers cut to a stub, although the drafts were complete | Say how to hand in: the whole answer, once, in the response |
| **Giving up and wandering** | "Documents aren't accessible" without searching; median 16 tool calls against a ~5-call minimum | A short method, and the folder map so searches go straight to the right place |

**Safeguards**
- **The rubrics stay as they are.** A refined skill is applied with `--definition-only`, so the platform can't swap the rubrics.
- **No rubric wording in the skill.** Every new skill version is checked for shared 5-word phrases with the rubrics. One that copies rubric text is rejected, because that would teach to the test.
- **Training and evaluation stay separate.** Refinement only sees the 60 Training claims. These are uploaded now, which also prepares them for RFT.
- **The database is reset** after refinement runs, which also write drafts.

**What we should look forward to**
- **Correctness above 23/30.** The reachable misses: authority (0/2), hand-in losses (3), giving up (2).
- **Rubric score above 0.637**, mostly on authority and action, precedence and grounding.
- **Fewer tool calls and shorter runs**, and so fewer stalls.
- **If 2a doesn't help, that's a finding, not a failure:** we'll report what the platform's tools did and didn't change.

**The goal in one line:** *the best skill we can give MAI, with the gain from the platform's tools and from our own guidance measured separately; that skill is what stage 3's headroom check runs on.*

### Stage 2 in brief: guidance did not improve the agent

**What we did**
1. Tried the platform's own tools: `skills enrich` changed nothing; `skills refine` copied the rubric checklist into the skill, so we rejected it.
2. Added method, folder navigation and hand-in guidance to stage 1's skill. Model and rubrics stayed fixed.
3. Closed on **29 claims**, at the user's request, rather than waiting for 04130's third attempt. Cancelled that job and excluded 04130 from both sides of the comparison.

**Result** 🖥️

| | Stage 1, same 29 claims | Stage 2b |
| --- | --- | --- |
| Correct | **22/29 (76%)** | **17/29 (59%)** |
| Rubric score | **0.637** | **0.526** |
| Tool calls, mean / median | 15.4 / 14 | 20.3 / 17 |
| Echoed questions / inability answers / incomplete answers | 1 / 2 / 2 | 4 / 5 / 1 |
| Authority correct | 0/2 | 0/2 |

**What it means.** Four claims recovered, but nine previously correct claims failed. The guidance did not deliver the hoped-for improvement in this run. Stage 1 remains the stronger measured configuration; more instructions are not automatically better.

**What we did not control.** Retries condition the retained answers, and the cohort is 29 rather than 30. SQL public access was blocked when we tried the final cleanup; the user re-enabled it and the reset/baseline then passed **0 0 0 0**. Overnight reset success is not established. These limitations prevent attributing every lost claim solely to the skill.

**Was the regression caused by SQL shutting down at midnight?** 🖥️ The retained evidence does not support that: **six of nine newly wrong answers finished before midnight**, all **63 SQL-backed dossier reads and 31 writes returned successful payloads**, and local snapshots still succeeded through 04:54. The 05:54 snapshot was denied. Failed tool calls instead increased from **11 on 5 claims** to **66 on 17 claims**, mostly SharePoint navigation failures. The SQL cleanup defect is real, but it is distinct from an established cause of wrong answers. [Timing and payload check](evidence/journey-record-2026-10-09.md#sql-causality-check).

| Issue | What we did |
| --- | --- |
| Automatic scorer reported 14/29 with four review flags | Checked the responses: three extraction errors resolved to correct; remaining review flags resolved to wrong → **17/29**. Kept the automatic report unchanged alongside the hand check |
| “Gaps” rose (0.722 → 0.821) while correctness fell; wrong authority answer 04172 scored 0.771 | Recorded reward-alignment concerns; no tuning started |
| A retry batch ran 216 minutes despite the runner's 75-minute default | Recorded timeout-enforcement failure; harden before unattended runs, without claiming an unverified cause |
| Last claim still running | Cancelled at the user's request; no result from it used |

**Next:** do not promote 2b. Restore the stage 1 skill and settle operational/reward issues before the headroom check.

Detail: [stage 2 result](../stages/stage-2/README.md) · [hand check](../stages/stage-2/hand-check.md) · [session evidence](evidence/journey-record-2026-10-09.md).

### The road ahead

**Before stage 1** (done)
1. ✅ **Fix the scorer's 7 misreads**, so correctness is scored without a hand check (done 2026-10-08).
2. ✅ **Review the hand-written rubrics:** reviewed against stage 0 and world v3 and revised ([the set and what changed](../stages/stage-1/rubrics.md)). They become the RFT reward, so they are settled before any tuning.
3. *Deferred (user, 2026-10-08):* a **GPT-5.6-Sol reference run** on stage 0's configuration, to measure the frontier gap on v3.

**The stages**

| Stage | One change | What it should show | Time |
| --- | --- | --- | --- |
| **1 · Hand-written rubrics** ✅ | Replace the generated rubrics; re-upload the 30 samples (they capture the rubrics at upload) | Done: correctness 23/30 (unchanged); the rubric score ranks right above wrong 93% (was 83%) | ~6 h with stalls |
| **2 · Skill refinement** ✅ | Platform tools, then method, folder map and hand-in guidance | Measured regression: 17/29 vs matched 22/29; stage 1 remains stronger | ~9 h 51 min to user-requested cancellation, with retries and an unenforced timeout |
| **3 · Headroom** | `Simple` vs `BestOfN` on the same model and skill | Whether tuning has anything to capture. A near-zero gap means stop and report | 2.5–5 h |
| **4 · RFT** | Tune `mai-code-1-flash`; compare before, after, and GPT-5.6-Sol | Whether a tuned small model matches the frontier, stating what was and wasn't controlled | platform-dependent |

#### Stage 3, explained: the headroom check

It answers one question before we spend anything on tuning: **is there anything for RFT to learn?**

**What we do:** run the same 30 claims twice, on stage 2's final skill, with the model, rubrics and prompts unchanged. Only the platform's **strategy** differs between the two runs:

| Run | What the platform does per claim | What it tells us |
| --- | --- | --- |
| `Simple` | One attempt, graded | How the model performs today |
| `BestOfN` (e.g. N = 4) | **4 attempts**; the grader scores each and keeps the best | How well the same model performs *when it gets it right* |

**Why the gap matters.** RFT doesn't teach the model new knowledge. It makes the model's **good attempts more likely**: rollouts that score well are reinforced, and the rest are discouraged. 📄 The playbook puts it as *"fine-tuning amplifies what is there; it does not repair it."*
- **Big gap** (BestOfN well above Simple): the model *can* produce the better answer, just not reliably. That variance is exactly what RFT converts into consistency, so we go to stage 4 with a measured target. A tuned model with `Simple` should approach today's `BestOfN`.
- **Near-zero gap:** the model gives the same quality every time, so there's nothing to amplify. Per AGENTS.md, **we don't tune; we report that**, and the remaining lever is the skill, the world or a different model.

**What we measure, as in every stage:**
1. **Rubric score:** Simple vs BestOfN. This is the headroom as the reward sees it.
2. **Ground-truth correctness:** Simple vs BestOfN, plus **"right in any of the N attempts"**. That last number is the true ceiling: claims MAI can solve at least sometimes.
3. **A reward check:** does picking the best-scoring attempt also pick the *correct* one? If BestOfN's rubric score rises but its correctness doesn't, the rubrics are steering toward the wrong answers. We'd fix that before RFT, because the reward would teach it.

**Where we'd expect headroom**, from stages 0 and 1:
- **Claims MAI gets right only sometimes:** the stalls, echoed or stubbed hand-ins, and claims where it wandered and gave up (04129, 04141). These look like variance, which is good for RFT.
- **Claims MAI gets wrong consistently, like authority (0/2 in both stages):** if all N attempts decline instead of escalating, that's a **systematic** error. RFT can't amplify a behaviour that never occurs, so the fix is the skill (stage 2) or the rubric, not tuning.

**Practicalities:**
- **It also settles one of our open questions:** whether `--strategy BestOfN` actually works on this tenant (🔬 in AGENTS.md). If it isn't enabled, the fallback is to run `Simple` 4 times and take each claim's best attempt ourselves.
- **Cost:** about **4× the inference**, so roughly 120 executions plus the Simple run.
- **Two ways to reduce cost:** run BestOfN only on the claims Simple got wrong or scored below 0.8, or use N = 3.
- **Safeguard:** with 4 attempts per claim the database collects several drafts, so the runner's snapshot and reset after every job matters even more.

**The goal in one line:** *a measured, numeric target for RFT, or an honest "don't tune" before spending the tuning budget.*

**Open questions to resolve before stage 4** 🔬
- Are MAI-CODE-5b (`dev-ct-mai-code-mp`) and `mai-code-1-flash` the same weights?
- Does tuning use the 60 Training samples, or the Evaluation samples?
- Echoed and rejected hand-ins: with the platform team ([note](evidence/platform-issue-finish-rejection.md)).

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
| Each evaluation job pays ~9 min of platform start-up + ~2.5 min grading, whatever the claim | Batches of 5 claims per job (`scripts/eval-batches.ps1 -BatchSize 5`): 5 claims in 20–27 min. (Parallel runs stalled on world v2's heavy runs, not on v3's light ones) |
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
