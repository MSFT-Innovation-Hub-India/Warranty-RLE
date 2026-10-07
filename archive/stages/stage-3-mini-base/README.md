# Stage 3-mini-base — The same setup, on the small model

**Status:** ⏹️ cancelled 2026-10-04 22:53 IST (2 runs hung). Job `73fa5456-45f6-411c-92e1-b553931acab8`: **rubric 0.415 on 28/30**. Ground-truth number **not yet trustworthy**: on 12 runs the delivered answer differs from the stored one.

**Why this stage, and why now.** Stage 2-base showed the frontier model has no headroom
(29/30 right by the world's rules). The plan was to write better rubrics next (2a).
The user challenged that on 2026-10-04:

> *"do we now not create the need for better rubrics by using the SLM first and then go about
> improving it? Would we not be assuming the mini model would fail with the same rubrics
> before indeed finding them to be so? I am trying to progress the hill climb with the
> realization at every step for the next."*

Agreed. The case for new rubrics rests on **one** clearly wrong answer the rubrics scored 1.0
(04172), plus one ambiguous one (04103 in stage 1 v2). That's a hint, not a measurement. The small
model will be wrong more often, so the same rubrics and the answer key, run side by side, will
show whether the rubrics follow correctness or not. Only then is 2a justified, or not.

**This changes the runbook's order.** The frontier track ends at stage 2-base, because it's
saturated. The climb continues on the small model, starting with this baseline. GPT-5.6-Sol
(2-base: rubric 0.978, 27/30) is the target to match. Stage 2b (split skills) is set aside
unless the small model's failures call for it.

## The one change (against stage 2-base)

| | Stage 2-base | **Stage 3-mini-base** |
| --- | --- | --- |
| Model | `prod-gpt-56-reasoning-sol` (GPT-5.6-Sol) | **`dev-ct-gpt-54-mini-mp` (GPT-5.4-Mini)** |

Everything else is identical: skill `cf00d339` and its pinned generated rubrics (same files
and hashes), the same 30 uploaded Evaluation samples, MCP on, strategy `simple`, 5 MCP replicas.

**World:** v2.2. The 2 defects found by 2-base are fixed (answer key 04178; eval/train twins).
The DB was reloaded. The 30 eval prompts and their expected answers are unchanged from 2-base.

## Hand probe — 2026-10-04 · execution `bb32816e-189d-4819-9889-05d84e2ceb95`

`chat -q "Adjudicate claim C-2026-04114." --model dev-ct-gpt-54-mini-mp`

| | GPT-5.6-Sol (stage 1 v2 probe) | **GPT-5.4-Mini** |
| --- | --- | --- |
| Tool calls | 17: 8 MCP, then 6 document searches and 2 Teams searches | **19, all MCP**; no SharePoint, no Teams |
| Answer | approve ₹199,175 under TSB-C-0051 ✅ | **"Request evidence — cannot yet be finally adjudicated"** ❌ |
| Drafts recorded | 1 | **2** (both `request_evidence`) |

🔬 **Caveat.** The `tools available` read just before the evaluation returned **106**,
which is exactly 137 minus the 31 SharePoint tools. Four re-reads minutes later gave 137. The
probe's response doesn't record which tools were offered, so "no document reads" may be the
model's choice or a missing tool source. To check after the run: how many of the 30 runs
used SharePoint or Teams, and a second probe after a stable 137 read.

## Results

**Cancelled at the user's request**, 2026-10-04 22:53 IST, after 2 runs (04118, 04110) hung from 16:49 UTC with resubmissions rising 5 → 8. Final status `Cancelled`; `OverallScore` null. The platform's running score for the 28 graded answers was **0.415**.

Per rubric, computed from the 28 graded answers (165 rubric scores, as in diagnostics; per-rubric n exceeds 28 because some samples carry more than one grading):
Outcome 0.537 · **Determination 0.119** · Grounding 0.300 · Presentation 0.393 · Draft Execution 0.724.

DB: 36 drafts · 6 evidence requests · 0 escalations → reset → 0 0 0 0.

### Preliminary, from the 28 finished answers (2026-10-04 22:50 IST)

| | 2-base (GPT-5.6-Sol) | **3-mini-base (GPT-5.4-Mini), 28/30** |
| --- | --- | --- |
| Rubric score (platform, running) | 0.978 | **0.415** |
| Correct by the scorer (reads the stored `Response`) | 27/30 | 10/28, 4 ❓ |
| Runs that used SharePoint or Teams at all | all | **11/28** (the other 17 used only the claim system) |
| Runs where the grader says the **delivered** final message differs from the stored answer | 0 | **12/28** |

**First reading, which was wrong:** correct answers averaged rubric 0.31 and wrong ones 0.47, so the rubrics seemed to reward wrong answers.

**Checked by hand, that's a measurement artefact.**
- On 12 runs the grader says, for example, *"The only successfully delivered finish message states that the agent was 'not able to complete a final…adjudication'… Earlier detailed finish attempts…"* (04103).
- The stored `Response` holds the detailed approval (₹19,150, correct). The "not able to complete" text exists **only in the grader's reasoning**, not anywhere in the exported execution.
- So the mini model's detailed answers often **failed to deliver**, and what reached the user was a non-answer. The grader scored what was delivered; our scorer read what was stored. Most of the scorer's "correct" mini answers (04103, 04114, 04116, 04139, 04140, 04152, 04153) are in this group.

**What this means so far**
- 🖥️ **The 106-tools caveat is resolved.** 11 runs searched documents (up to 10 searches each), so SharePoint was available. Not reading documents was the model's choice in 17 runs.
- 🖥️ The mini model's failures are **behavioural**: it skips the documents and often fails to deliver its final answer. It isn't (yet) evidence that the rubrics reward wrong answers.
- ⚠️ **The ground-truth scorer must score what was delivered.** The export doesn't contain the delivered message for these runs. 🔬 Open: where the platform keeps it, and why the finish attempts failed.

### Hand runs to explain the failed hand-ins — 2026-10-05

`chat --model dev-ct-gpt-54-mini-mp` on two claims whose answers failed to deliver in the evaluation. Executions `d04446c1-6e93-4a11-bc1d-3b9a9659f63d` (04150) and `c9c64dc9-4cd5-4456-bf1c-d673beed33c9` (04103). Full records via `executions get` are in [docs/evidence/stage-3-mini-base/finish-probes/](../../../docs/evidence/stage-3-mini-base/finish-probes/). **Reproduced on both.**

| Phase | 04150 | 04103 |
| --- | --- | --- |
| 1. Claim system only (9 DB calls, no documents) | draft `ADJ-A50B2C878E` **request_evidence** | draft `ADJ-62DB35A7CF` **request_evidence** |
| 2. **Finishes early**: short answer **accepted** | *"no payable can responsibly be calculated"* | *"coverage and payable cannot yet be determined"* |
| 3. Keeps working: **reads the documents** | 8 searches | 7 searches |
| 4. Reaches the **correct** answer, records it | draft `ADJ-D0D83CA33B` **approve ₹755,050** ✅ | draft `ADJ-101EA04112` **approve ₹19,150** ✅ |
| 5. Detailed hand-in **rejected by the finish tool** | stored as `Response`; never delivered | grader: *"The detailed attempted handoffs were rejected by the finish tool"*; a short note *"framed as a completion-tool failure"* got through |

**Conclusions**
- 🖥️ **Two behaviours, not one.** (a) **It finishes too early**: it answers from the claim system alone and calls the documents "unavailable" *without having searched*. (b) **Its detailed hand-ins are rejected.** It does the right work only *after* finishing, by which point the answer can't be delivered.
- 🖥️ **The skill isn't too complex.** Given the room, the mini model reached the correct answer on both claims, the same answers as GPT-5.6-Sol.
- 🔬 **Why the detailed hand-ins are rejected isn't visible to us.** The finish attempts aren't in the exported record. The grader twice notes that the *accepted* finish carried *"an empty sources list"* / *"omitting formal source objects"*, which hints that the rejected ones carried sources in a form the finish tool refused. Unconfirmed.
- 🖥️ **The stored `Response` is the last *attempted* message, not the delivered one.** For the mini model, the ground-truth scorer currently reads a message the user never received.
- DB after the probes: 4 drafts (above) → reset → 0 0 0 0.

### The same two claims on MAI — 2026-10-05 (side probe)

`chat --model dev-ct-mai-code-mp` (MAI-CODE-5b), run one at a time, same prompts. Executions `ce09af1e-7d96-48ff-9e79-933ce73848d8` (04150) and `181a5c12-157d-417f-a627-00e938101f39` (04103). Files: [finish-probes-mai/](../../../docs/evidence/stage-3-mini-base/finish-probes-mai/).

| | GPT-5.4-Mini | **MAI-CODE-5b** |
| --- | --- | --- |
| 04150: delivered answer | "no payable can be calculated" ❌ | **"Decision: Covered — INR 755,050"** ✅ |
| 04150: order of work | DB → **finish** → docs → rejected hand-in | DB (7) → **docs (13)** → answer; no early finish, no rejection |
| 04150: rubrics | 0.4 / 0.0 / 0.25 / 0.6 / 1.0 | **0.83 / 0.8 / 1.0 / 1.0** / not scored |
| 04103: stored answer | approve ₹19,150 (not delivered) | **approve ₹19,150 under ADD-IN-2.1** ✅ |
| 04103: run | 22 calls, rejected hand-in | **42 calls in 10.6 min** (billing says 62), looping: claim/asset/hours/history fetched 3×, 20 doc searches, one sandbox terminal call. **Not graded** (0 rubric results, no error, not timed out) 🔬 |
| Drafts recorded in the claim system | 4 | **0** |
| Tokens per run | ~0.5 M (probe) | 1.06 M · 1.74 M |

**Reading it (n = 2, a hint, not a measurement)**
- MAI **researches before concluding** and **delivers its answer**: the two behaviours GPT-5.4-Mini fails at.
- It reached the correct answer on both claims, but it **never records a draft** in the claim system, and on 04103 it **loops** (repeated lookups, 42–62 calls).
- 🔬 Why 04103 wasn't graded is unknown. The platform returned no rubric results and no error.
