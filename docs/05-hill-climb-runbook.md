# Guide 05 — The hill climb, stage by stage

> ⚠️ **Superseded as the plan (2026-10-06).** This is the original design. The stages as actually run, and the current plan, are in [stages/README.md](../stages/README.md).

**An operational runbook.** Guide 04 tells the story; this tells you what to
run, in what order, and how to read what comes back.

**Status: not executed.** Every score in this document is a **prediction**, and
every command is written against CLI 0.3.11 as documented in
[CLI-REFERENCE](CLI-REFERENCE.md). Nothing here has been measured on a
tenant.

Each stage has the same seven sections, so you can work through them
mechanically:

| | |
| --- | --- |
| **Prerequisites** | What must be true before you start |
| **World configuration** | Exactly what is enabled, disabled and uploaded |
| **Skills and rubrics in play** | What the grader is scoring against |
| **Commands** | What to run |
| **What the agent will do** | The tool trajectory you should see in the trace |
| **Expected outcome** | Score band and the per-rubric shape |
| **The gate** | The specific reading that says *proceed*, *stay*, or *stop* |

---

## The model ladder

This is the spine of the whole exercise, so it goes first.

📄 Two lists, and they do not overlap. `evaluate start` validates against
`TrainingModels`; `tune start` validates against `FTBaseModels`.

🖥️ As captured on **20 September 2026** — ⚠️ **re-read before every run**, the
list changes and `prod-gpt-54-reasoning` has already dropped out of it:

| Role in this runbook | Model ID | Which list | Used in |
| --- | --- | --- | --- |
| **Frontier — the climbing model** | `prod-gpt-56-reasoning-sol` | `TrainingModels` | Stages 0–3, held constant |
| **Small model, untuned** | `dev-ct-mai-code-mp` | `TrainingModels` | Stage 4a — the "before" |
| **Small model, tuned** | `mai-code-1-flash` → your `--new-model` | `FTBaseModels` | Stage 4c — the "after" |

> 💭 **On GPT-5.5.** It is not in the captured list. The strongest *evaluable*
> model you recorded is `prod-gpt-56-reasoning-sol`. Run `models list -o json`
> and use whatever the strongest reasoning model in `TrainingModels` is on the
> day — the runbook does not depend on which one it is, only that it is **held
> constant from stage 0 to stage 3**.

### Why the frontier model must not change during the climb

Stages 0 to 3 make one claim: *the world got better.* That claim only holds if
the model is the same throughout. Change the model mid-climb and the score
delta becomes uninterpretable — you can no longer say whether the rubrics did it
or the model did.

**One variable per stage.** That is the whole discipline of this runbook.

### The MAI pair, and the risk attached to it

You want to finish by matching a frontier LLM with a small MAI model. The pair
available to you is:

```text
dev-ct-mai-code-mp   (evaluable, not tunable)  ← measure the "before" here
mai-code-1-flash     (tunable, not evaluable)  ← tune this
```

🔬 **Whether these are the same weights is unverified**, and it decides which
story you can tell at the end. It is the same open question already recorded for
the GPT-5.4-Mini pair in guide 02.

⚠️ **Settle it in stage 4a, before you spend days on a tuning run.** Section
"Stage 4 pre-flight" below is how.

---

## Stage 0 — The naive build

> **Goal.** Produce a low score *for a diagnosable reason*, and prove the
> documents are reachable so that the reason is not retrieval.

### Prerequisites

| | |
| --- | --- |
| World provisioned | `environments init` complete, `IsWorkspaceReady: true` |
| Corpus loaded | 34 Word + 3 Excel + 2 PPTX in SharePoint, 3 Teams channels posted |
| **Indexing settled** | ⚠️ Loaded **the previous day**. M365 crawl latency is hours and you cannot force it |
| Database seeded | `seed.azuresql.sql` loaded, `/healthz` returns `{"status":"ok","assets":117}` |
| MCP server registered | `tools create` done, server id captured from `tools sources` |
| Samples | The **8 easiest** evaluation prompts only — the `covered-simple`, `declined-simple` and `precedence` slices |

### World configuration

```powershell
frontier-tuning tools disable <server-id> --env-id $envId     # ← the stage-0 condition
```

| Component | State |
| --- | --- |
| Knowledge sources | SharePoint folders + Teams channels, **enabled** |
| MCP server `contoso-service` | **DISABLED** |
| Skills | One: `warranty-assistant` (broad, does all three jobs) |
| Rubrics | **Generated** — `generateRubrics: true`, so they restate the prompt |
| Samples | 8 Evaluation, 0 Training |

### Skills and rubrics in play

One skill, deliberately built the way most people build:

```markdown
---
name: warranty-assistant
description: Answers questions about warranty claims, coverage and payable amounts.
generateRubrics: true
---

## Instructions

You help the Warranty Operations team adjudicate claims. Work out whether the
claim is covered, which instrument applies, and how much is payable. Cite the
policy clause. State the payable amount. Order your answer with the decision
first. Do not approve anything outside the coverage period.
```

⚠️ Note what is wrong with it on purpose: it is broad, and its instructions
encode the standard. Generated rubrics will restate those instructions, so the
task gets solved in the prompt. That is
[defect 3](rubric-defects.md#defect-3--the-prompt-gives-away-every-rubric),
reproduced deliberately.

### Commands

```powershell
frontier-tuning skills create --file skills/warranty-assistant.md --env-id $envId -o json
$skill0 = '<returned-id>'

frontier-tuning samples upload .\warranty-adjudication.stage0.jsonl `
  --skill-id $skill0 --type Evaluation --env-id $envId

# Probe ONE claim by hand before spending an evaluation run
frontier-tuning chat --query "Adjudicate claim C-2026-04114." `
  --skill-id $skill0 --model prod-gpt-56-reasoning-sol --strategy simple `
  --conversation-id ([guid]::NewGuid()) --env-id $envId

frontier-tuning executions get <execution-id> --env-id $envId -o json > stage0-probe.json

frontier-tuning evaluate start --skill-id $skill0 `
  --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $envId
```

### What the agent will do

| Tool type | Server | Expected calls |
| --- | --- | --- |
| **Knowledge** | `m365` | `search_enterprise_files` — finds the policy, the India addendum, TSB-C-0051 |
| **Knowledge** | `mcp_SharePointRemoteServer` | File reads on the documents it found |
| **Knowledge** | `teams` | Possibly a channel search |
| **Action** | — | **None. The MCP server is off.** |

The agent will find the *rules* and none of the *facts*. Commissioning date,
running hours, part fitted, partner uplift — all unreachable.

It will do one of two things, and both are informative:

1. **Invent them.** A confident answer with a fabricated commissioning date.
2. **Say it cannot determine coverage.** Correct behaviour, scored badly by
   rubrics that were written assuming an answer.

### Expected outcome

**Predicted 0.45 – 0.55.**

| Rubric (generated) | Expected | Why |
| --- | --- | --- |
| Anything about citing a clause | **High** | The documents retrieve fine |
| Anything about the decision | Mixed | Right by luck on the easy cases |
| Anything about an amount | **Low** | The inputs do not exist |

### The gate

⚠️ **This gate is the most important one in the runbook**, because it separates
"the world is hard" from "the world is broken".

Open `stage0-probe.json` and check:

| Signal | Reading | Meaning |
| --- | --- | --- |
| `ToolExecutions[].Output` → `FileRetrievalDetails` | **Non-empty** | ✅ Documents are reachable. Proceed |
| `FileRetrievalDetails: []` | Empty on every call | ❌ **STOP.** Scoping or indexing failure. Do not proceed — see [troubleshooting § 1](troubleshooting.md) |
| Tool inputs naming sites you did not register | Present | ❌ Scoping failed, the agent is guessing at paths |
| `Submitted` vs `Graded` | Equal | ✅ Routing works |
| `Skill: —` on any row | Present | ⚠️ That sample fired no skill and was dropped from the mean, not scored zero |

| Then | Action |
| --- | --- |
| Score 0.40–0.60 **and** documents retrieving | ✅ **Proceed to stage 1** |
| Score < 0.30 | ❌ Almost always retrieval. 📄 *"Fix retrieval, do not tune"* |
| Score > 0.70 | ⚠️ Your stage-0 samples are too easy. Check you used the 8-sample easy set, not the full 30 |

---

## Stage 1 — Enable the tools

> **Goal.** Show that a third of the total gain comes from plumbing, with zero
> model work and zero content change.

### Prerequisites

- Stage 0 job id recorded, with its per-rubric breakdown
- `/healthz` on the Container App returns `ok`
- ⚠️ If the Azure SQL database is serverless with auto-pause, **warm it first** —
  the first call otherwise times out and looks like a tool failure

### World configuration

**Exactly one thing changes.**

```powershell
frontier-tuning tools enable <server-id> --env-id $envId
frontier-tuning tools available --env-id $envId -o json | Select-String contoso
```

| Component | State | Changed? |
| --- | --- | --- |
| Knowledge sources | Unchanged | No |
| **MCP server** | **ENABLED** | ✅ **the only change** |
| Skills | `warranty-assistant` | No |
| Rubrics | Same generated set | No |
| Samples | Same 8 | No |

### Skills and rubrics in play

Identical to stage 0. **Do not touch them.** If you change the skill here you
lose the ability to attribute the gain to the tools.

### Commands

```powershell
frontier-tuning evaluate start --skill-id $skill0 `
  --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $envId

frontier-tuning evaluate compare <stage0-job> <stage1-job> --env-id $envId
```

### What the agent will do

| Tool type | Tool | Purpose |
| --- | --- | --- |
| Knowledge | `m365__search_enterprise_files` | Policy, addendum, bulletins |
| **Knowledge (new)** | `contoso-service__get_claim` | The submitted claim |
| **Knowledge (new)** | `contoso-service__get_asset` | Commissioning date |
| **Knowledge (new)** | `contoso-service__get_running_hours` | The second coverage limit |
| Knowledge (new) | `contoso-service__lookup_part` | Price and supersession |
| Knowledge (new) | `contoso-service__get_dealer` | Uplift |
| **Action** | `contoso-service__create_claim_adjudication` | Possibly — a broad skill will not do it reliably |

**Expect 4–6 tool calls.** Fewer than 4 means it is not gathering enough;
the trace will show which hop it skipped.

### Expected outcome

**Predicted 0.62 – 0.70.** A jump of roughly **+0.15** on the same samples,
same model, same rubrics.

### The gate

| Signal | Meaning | Action |
| --- | --- | --- |
| Score up ≥ 0.10 and DB tools appear in the trace | ✅ Plumbing was the bottleneck | **Proceed to stage 2** |
| Score flat, DB tools **absent** from trace | Tool not actually enabled, or unreachable | Check `tools available`, `/healthz`, ingress is public |
| Score flat, DB tools **present** in trace | ⚠️ **The interesting failure.** The agent has the facts and the score did not move — the rubrics are not measuring the thing that improved | This is the stage-2 problem arriving early. Proceed, but expect stage 2 to matter more than predicted |
| `get_asset` returns `found: false` a lot | Serial mismatch between corpus and DB | Regenerate — `populate.py` and `gen_db.py` must be run from the same population |

> 💭 Stage 1 is where you get to say, with evidence, that **most agent projects
> that "need fine-tuning" actually need a tool connection.** Capture the
> before/after trace side by side — it is the most persuasive artefact in the
> whole climb and it cost nothing but a flag.

---

## Stage 2 — The inner loop

> **Goal.** The largest single gain in the exercise, from rubric and skill
> design alone. No model change, no content change.

### Prerequisites

- Stage 1 per-rubric breakdown read, not just the mean
- ⚠️ **Rubrics written before the skills.** 📄 *"A rubric written after the skill
  tends to describe what the skill already does."* If you author the skills
  first you will reproduce guide 01's saturation

### World configuration

| Component | State |
| --- | --- |
| Knowledge sources | Unchanged |
| MCP server | Enabled |
| **Skills** | **Three new narrow skills**; `warranty-assistant` **disabled** |
| **Rubrics** | **Hand-authored, written first** |
| Samples | Same 8, **re-uploaded** against the new skills |

⚠️ **Samples snapshot the skill's rubrics at upload time.** New skills mean new
sample rows. And re-uploading *adds* copies rather than replacing, so:

```powershell
frontier-tuning samples delete-by-skill --skill-id $skill0 --env-id $envId
```

### Skills and rubrics in play

Three skills, split so failures are attributable:

| Skill | Job | Rubrics |
| --- | --- | --- |
| `warranty-coverage-check` | Is it covered, under which instrument? | Coverage determination · Precedence discipline · Evidence grounding · Evidence closure |
| `claim-valuation` | Given cover, what is payable? | Valuation accuracy · Evidence grounding · Evidence closure |
| `claim-adjudication-brief` | The full decision and action | All six from [guide 03 § 9.2](03-scenario-design.md#92-rubrics-for-the-flagship-skill--written-before-the-skill-exists) |

And the prompts get **thin**. The whole instruction block for the flagship:

```text
You support Contoso Industrial's Warranty Operations team.

When a claim is put to you, work out from the warranty library and the service
claim system whether it is covered, what is payable, and what should happen
next, and tell the adjudicator what they need to act.
```

Two sentences. No ordering rule, no citation rule, no format rule, no precedence
rule. **All of that now lives only in the rubrics, which the grader sees and the
model does not.**

### Commands

```powershell
foreach ($s in 'warranty-coverage-check','claim-valuation','claim-adjudication-brief') {
    frontier-tuning skills create --file "skills/$s.md" --env-id $envId -o json
}
frontier-tuning skills disable $skill0 --env-id $envId

# confirm the rubrics landed as authored and were NOT regenerated
frontier-tuning skills get $skillBrief --env-id $envId --show-rubrics -o json

frontier-tuning samples upload .\warranty-adjudication.stage0.jsonl `
  --skill-id $skillBrief --type Evaluation --env-id $envId

frontier-tuning evaluate start --skill-id $skillBrief `
  --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $envId
```

⚠️ **`generateRubrics: false` in every skill file.** Successful generation
*replaces* your hand-written `## Rubrics`. The `skills init-md` template sets it
`true` — following it literally destroys the work this stage depends on.

### What the agent will do

Same tools as stage 1, but the *trajectory should tighten*: the rubrics now
demand provenance and a derived quantity, so the model has to open the workbook
rather than guess a rate, and has to call `get_service_history` to find the part
actually fitted.

| Tool type | What changes from stage 1 |
| --- | --- |
| Knowledge | `get_service_history` now appears — the supersession rubric forces it |
| Knowledge | Excel retrieval becomes reliable — *Valuation accuracy* requires the rate be named |
| **Action** | `create_claim_adjudication` called consistently, with `instrument_refs` populated |
| **Action** | `request_missing_evidence` appears on the abstention path |

### Expected outcome

**Predicted 0.76 – 0.84.**

More useful than the mean: **the three skills should diverge.**

| Skill | Predicted | Why |
| --- | --- | --- |
| `warranty-coverage-check` | ~0.88 | Documents plus two DB fields. The easiest job |
| `claim-valuation` | ~0.68 | Four sources, a cap, a supersession and a conditional uplift |
| `claim-adjudication-brief` | ~0.78 | Composes both, plus authority and abstention |

### The gate

| Signal | Meaning | Action |
| --- | --- | --- |
| Skills diverge as above | ✅ Attribution is working | **Proceed to stage 3** |
| All three score the same | ⚠️ The rubrics are not discriminating | Re-read them — are they all measuring "did it answer?" |
| Score did not move from stage 1 | Check `skills get --show-rubrics` | Almost always: generation replaced your rubrics, or samples were not re-uploaded |
| A rubric scores 1.00 on every sample | ⚠️ It is not measuring anything | [defect 2](rubric-defects.md#defect-2--nothing-measures-cross-source-provenance) — a rubric with no opinion |
| A rubric scores 0.00 on a *correct* answer | ❌ **Fix before stage 4** | [defect 1](rubric-defects.md#defect-1--rubrics-penalise-correct-refusals). Under tuning this trains hallucination |

> ⚠️ That last row is a hard gate, not a nice-to-have. Rubrics become the reward
> function at stage 4. Re-run the satisfiability audit from
> [guide 03 § 9.3](03-scenario-design.md#93-satisfiability-audit)
> before going anywhere near `tune start`.

---

## Stage 3 — Honest samples

> **Goal.** Measure the world as it actually is, and *create* the headroom that
> stage 4 will close.

### Prerequisites

- Stage 2 rubrics stable and satisfiability-audited
- The full 30-sample evaluation set generated
- ⚠️ Time. **~4.5 hours** of wall clock for 30 samples at ~9 min each

### World configuration

| Component | State |
| --- | --- |
| Everything from stage 2 | Unchanged |
| **Samples** | **Full 30**, replacing the easy 8 |

The corpus does not change. The hard cases were always in it — they were simply
not being measured.

### Skills and rubrics in play

Unchanged from stage 2. **One variable per stage.**

### Commands

```powershell
frontier-tuning samples delete-by-skill --skill-id $skillBrief --env-id $envId
frontier-tuning samples upload .\warranty-adjudication.eval.jsonl `
  --skill-id $skillBrief --type Evaluation --env-id $envId

# smoke first - never start a 4.5-hour run blind
frontier-tuning evaluate start --skill-id $skillBrief --limit 3 `
  --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $envId

# then the full run
frontier-tuning evaluate start --skill-id $skillBrief `
  --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $envId
```

### What the agent will do

The new slices exercise trajectories the easy 8 never did:

| Slice | New behaviour required | Tools |
| --- | --- | --- |
| `serial-boundary` | Exact range comparison at 4 boundary values | Bulletin doc + `get_asset` |
| `abstention` | **Stop and report.** Three different missing-record shapes | `get_asset` / `get_running_hours` returning `found: false` → `request_missing_evidence` |
| `authority` | Read Teams, discount it, look up the tier | Teams search + `get_goodwill_authority` → `escalate_goodwill` |
| `dual-limit` | Hours exceeded while months are not | `get_running_hours` |
| `stale-deck` | Prefer the policy over a confident slide | PPTX retrieval + policy |

### Expected outcome

**Predicted 0.72 – 0.80 — and it may be *lower* than stage 2.**

💭 That is the point, and it is worth saying out loud to whoever is watching.
📄 *"Fine-tuning amplifies what is there; it does not repair it."* An eval set
that avoids the hard cases bakes in a model that is good at easy cases. A drop
here, with the loss concentrated in named slices, is the most credible slide in
the deck: *we know exactly what our agent is bad at, and here is the number.*

Read the **per-slice breakdown**, not the mean:

| Slice | Predicted | If it is low, that is… |
| --- | --- | --- |
| `covered-simple` | ~0.95 | …a problem. These should be near-perfect by now |
| `precedence` | ~0.80 | …a rubric or prompt issue — the rule is stated in one clause |
| `serial-boundary` | **~0.65** | **…an RFT candidate.** Mechanical, and small models fumble it |
| `valuation` | **~0.70** | **…an RFT candidate.** Four-source arithmetic under a cap |
| `abstention` | **~0.55** | **…the strongest RFT candidate.** Reward-shaped behaviour |
| `authority` | ~0.70 | …an RFT candidate if the tier lookup is being skipped |

### The gate — the tuning decision

📄 Upstream's bands, applied to the overall score:

| Baseline | Meaning | Action |
| --- | --- | --- |
| Near zero | Retrieval | Fix retrieval, do not tune |
| < 0.5 | Too hard or broken | Check retrieval first |
| **0.6 – 0.75** | **Target band** | **Proceed to stage 4** |
| 0.8 – 0.95 | Modest headroom | Usable, but the tuning gain will be small |
| **> 0.95** | **Saturated** | ⚠️ **Harden first — deploy the reserve** |

**If you land above 0.90**, the world is too easy for a frontier model. Do not
touch the corpus. Instead write evaluation samples against the two **reserve
trap families** that are already built and already indexed:

| Reserve | Content that supports it | Currently |
| --- | --- | --- |
| Exclusion reversal (TSB-C-0043) | 4 claims + inspection reports with fluid analysis | Training samples only |
| Repair warranty (policy 6.1) | 2 claims + prior-job rows in `ServiceHistory` | Training samples only |

Promote them to evaluation samples and re-run. **No world change, no
re-provisioning, no indexing wait.**

---

## Stage 4 — RFT: matching the LLM with an SLM

> **Goal.** Take a small MAI model from well below the frontier model to within
> touching distance of it, on the same samples, in the same world.

### Stage 4 pre-flight — settle this before spending days

⚠️ Tuning runs take **days** on fungible capacity. Three questions decide which
story you can tell at the end, and all three are cheap to answer now.

```powershell
frontier-tuning models list --env-id $envId -o json
```

| # | Question | How to settle it | If the answer is no |
| --- | --- | --- | --- |
| 1 | Is `dev-ct-mai-code-mp` still in `TrainingModels`? | The command above | No untuned small-model baseline — fall back to narrative B below |
| 2 | Do `dev-ct-mai-code-mp` and `mai-code-1-flash` share weights? | 🔬 No direct way. Run identical probes against `dev-ct-mai-code-mp` and against a **1-epoch throwaway tune** of `mai-code-1-flash`, compare behaviour | You cannot claim "same model before and after" — use narrative B |
| 3 | Does a completed tune appear in `TrainingModels`? | 🔬 Run a **minimal tune first** — `--epochs 1` — and check `tune status` for `readyForEvaluation`, then `models list` | ❌ **The tuned model cannot be scored at all.** There is no flag to work around it. Stop and re-plan |

> 💭 **Do question 3 first and do it small.** A one-epoch tune that exists only
> to prove the tuned model becomes evaluable is worth a day. Discovering it
> after a full run is worth a week.

### Stage 4a — The small model's "before"

**Same 30 samples, same rubrics, same world. Only the model changes.**

```powershell
frontier-tuning evaluate start --skill-id $skillBrief `
  --base-model dev-ct-mai-code-mp --strategy simple --env-id $envId
```

Better still, run both in one shot so they are directly comparable:

```powershell
frontier-tuning evaluate start --skill-id $skillBrief --per-model `
  --base-model prod-gpt-56-reasoning-sol --base-model dev-ct-mai-code-mp `
  --strategy simple --env-id $envId
```

⚠️ **`--per-model` matters.** Without it you get ONE job with both models offered
as candidates per sample and a **single blended score** — not per-model scores.

**Predicted: 0.50 – 0.60.** The gap to the frontier model is the thing tuning is
being asked to close.

| Where the small model should lose most | Why |
| --- | --- |
| `abstention` | Small models answer rather than stop |
| `valuation` | Drops a hop, guesses a rate |
| `precedence` | Takes the first instrument retrieved |
| `serial-boundary` | Off-by-one on range comparisons |

### Stage 4b — Prepare the workspace for tuning

⚠️ `tune start` **snapshots the entire workspace.** No `--skill-id`, no sample
filter. Everything enabled is in scope.

```powershell
# 1. exclude the naive stage-0 skill from the snapshot
frontier-tuning skills disable $skill0 --env-id $envId

# 2. check for duplicate samples from re-uploads
frontier-tuning samples list --env-id $envId -o json

# 3. upload the training set (60 prompts; the floor is 11)
frontier-tuning samples upload .\warranty-adjudication.train.jsonl `
  --skill-id $skillBrief --type Training --env-id $envId
```

| Pre-tune checklist | Why |
| --- | --- |
| ☐ Stage-0 skill disabled | Disabled skills are excluded from inference **and** training |
| ☐ No duplicate sample prompts | Re-uploads add copies; duplicates skew the training signal |
| ☐ ≥ 11 training-usable prompts | Hard server-side limit — `ER07010` otherwise |
| ☐ **Rubric satisfiability re-audited** | They are now the **reward function** |
| ☐ No rubric scores 0.00 on a correct refusal | Otherwise you train the model to invent |

### Stage 4c — Tune

```powershell
frontier-tuning tune start `
  --base-model mai-code-1-flash `
  --new-model contoso-warranty-mai-v1 `
  --epochs 3 `
  --env-id $envId
```

⚠️ **Use long options.** `-e` means *both* `--epochs` and `--env-id` in 0.3.11,
and the CLI warns `The parameter -e is used more than once.`

```powershell
frontier-tuning tune status <job-id> --env-id $envId
```

⚠️ Training can take **days**. Slowness is never a reason to resubmit. And
`training complete` is not the same as `readyForEvaluation` — poll for the
latter.

### Stage 4d — The "after"

```powershell
frontier-tuning models list --env-id $envId -o json      # confirm it appears

frontier-tuning evaluate start --skill-id $skillBrief `
  --base-model contoso-warranty-mai-v1 --strategy simple --env-id $envId

frontier-tuning evaluate compare <4a-mai-job> <4d-tuned-job> <3-frontier-job> --env-id $envId
frontier-tuning health token-usage --env-id $envId
```

### Expected outcome

**Predicted: tuned MAI 0.76 – 0.82, against a frontier model at ~0.78.**

### What counts as "matched"

Set the bar before you see the number, not after:

| Criterion | Bar |
| --- | --- |
| Overall | Tuned SLM within **0.05** of the frontier model |
| Per-rubric | No rubric more than **0.10** below the frontier model's |
| Abstention | ⚠️ Specifically checked — the behaviour most likely to be lost |
| Cost | Token cost per sample materially lower — the reason for the exercise |
| Latency | Measurably lower wall clock per sample |

A tuned model that matches on the mean but collapses on abstention has not
matched. It has learned to always answer.

### The gate — what you are allowed to claim

| Claim | Allowed? |
| --- | --- |
| "Tuning took a MAI small model from 0.55 to 0.80 on this task" | ✅ **Only if** pre-flight question 2 resolved yes |
| "The tuned small model reaches 0.80 against the frontier model's 0.78, at a fraction of cost and latency" | ✅ The safe default. Show both numbers and both token counts |
| "Our agent improved from 0.48 to 0.80 through fine-tuning" | ❌ **No.** That conflates stages 0–3 with stage 4. Most of it was rubric work |
| "Fine-tuning made GPT-5.6 better at warranty adjudication" | ❌ **No.** You did not tune that model and you cannot |

---

## The whole climb on one page

| Stage | One variable changed | Model | Samples | Predicted | Gate to pass |
| --- | --- | --- | --- | --- | --- |
| **0** | — (baseline) | Frontier | 8 easy | 0.45–0.55 | Documents demonstrably retrieving |
| **1** | MCP server enabled | Frontier | 8 easy | 0.62–0.70 | DB tools visible in the trace |
| **2** | Skills split, rubrics authored first | Frontier | 8 easy | 0.76–0.84 | The three skills diverge |
| **3** | Full honest eval set | Frontier | **30** | 0.72–0.80 | Lands in 0.6–0.75, or deploy the reserve |
| **4a** | Model → small MAI | `dev-ct-mai-code-mp` | 30 | 0.50–0.60 | A gap worth closing exists |
| **4c/d** | Model → tuned MAI | `contoso-warranty-mai-v1` | 30 | 0.76–0.82 | Within 0.05 of frontier, abstention intact |

**Two stories, two axes.** Stages 0→3 are *the world got better* — same model
throughout, and where most of the gain lives. Stage 4 is *a small model learned
what only a large one could do* — same world, different model. Draw them as two
lines. One line from 0.48 to 0.80 labelled "fine-tuning" misrepresents roughly
0.30 of rubric authoring as training.

---

## Related

| Document | Covers |
| --- | --- |
| [04-scenario-walkthrough.md](04-walkthrough.md) | What the world is, told as a story |
| [03-showcase-scenario-design.md](03-scenario-design.md) | Why it is shaped this way; the rubric drafts |
| [rubric-design.md](rubric-design.md) | Why rubrics come before skills |
| [rubric-defects.md](rubric-defects.md) | The three defects the gates test for |
| [../CLI-REFERENCE.md](CLI-REFERENCE.md) | Command surface and the 20 traps |
| [../scenario/mcp/deploy/azure.md](../mcp/deploy/azure.md) | Standing the MCP server up before stage 0 |
