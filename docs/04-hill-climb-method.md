# The hill-climb method

How this climb is run, why it is in this order, and what each lever can and cannot do. Read it before starting any stage. The stage scoreboard is in [climb/README.md](../climb/README.md); what went wrong last time is in [archive/attempt-1](../archive/attempt-1/README.md).

Legend: 🖥️ measured on this tenant · 📄 CLI docs / upstream guidance · 🔬 unverified · 💭 reasoning.

---

## 1. The question the climb answers

> With a fixed world, skill and rubrics, GPT-5.6-Sol gets *X* claims right. How close can MAI-CODE-5b get, and **which lever** closes each part of the gap?

So the climb has three measured reference points before anything is changed:

| Point | What it is | How we get it |
| --- | --- | --- |
| **Ceiling** | What the world allows with this skill and these rubrics | GPT-5.6-Sol, `Simple` |
| **Floor** | What the small model does today, on average | MAI-CODE-5b, `Simple`, averaged over repeats |
| **Reach** | What the small model *can* do, at least some of the time | MAI-CODE-5b, best of its repeats ("right in any of k") |

Ceiling − floor is the **total gap**. Reach − floor is the part that **RFT can capture**. Ceiling − reach is the part that **only a better skill (or a bigger model) can close**.

---

## 2. The levers, and what each one actually changes

| Lever | What it changes | Changes the model's weights? | Fixes | Cannot fix |
| --- | --- | --- | --- | --- |
| **Skill** (instructions) | What the model is told to do at run time | No | Things the model *never* does because it doesn't know to: a missing procedure, a wrong hand-in format | Things it knows but does inconsistently |
| **Rubrics** | How every answer is scored. In RFT, the score **is the reward** | Only indirectly, through RFT | A reward that prefers wrong answers, or can't tell right from wrong | Anything at run time. Rubrics are never shown to the model |
| **Inference strategy** (`BestOfN`, `TreeSearch`) | How many attempts are made and which one is kept | No | Variance, at 2–4× the cost per claim | Systematic errors that every attempt makes |
| **RFT** (`tune start`) | The weights, so good attempts become more likely | **Yes** | Variance: makes the model's *own* best behaviour its default | Behaviour that never occurs in its attempts |

📄 The CLI's agent guidance gives the same mapping: missing procedure → skill refinement; incorrect grading → rubric refinement; benefit from alternatives → inference comparison; suitable training data → fine-tuning; missing access or data → troubleshooting, not tuning.

### How rubrics reach the weights 💭 (consistent with 📄 the CLI docs)

RFT does not read the rubrics as rules. For each **Training** prompt the model produces several attempts; the grader scores each attempt with the rubrics; attempts that score **above their siblings** are made more likely, and those below less likely. So:

1. **Only the *ranking* among the model's own attempts matters.** A rubric item that every attempt passes, or every attempt fails, contributes no signal.
2. **Adding rules helps only if they separate right attempts from wrong ones that the model actually produces.** More rules that don't discriminate dilute the signal and make reward hacking easier (writing the right words instead of reaching the right answer).
3. **The grader has no answer key.** 📄 "Sample-specific rubrics are not supported; grading uses the owning skill's current rubrics." So a rubric cannot say "the payable is ₹199,175". It can only check that the procedure was followed and shown: the governing bulletin named and justified, the rate taken on the repair date, goodwill escalated rather than declined. That is why the rubric score and ground-truth correctness can disagree, and why both are always reported.
4. **Red flags are the sharp tool.** Each rubric has a `RedFlags` list (empty today). A red flag that fires on a specific known-wrong behaviour (e.g. declining a goodwill request above the requester's authority) pushes the score of exactly those attempts down. Use them for systematic errors the checklist doesn't catch.

**What this means for MAI-CODE-5b:**

| If a claim is… | then the lever is… | because… |
| --- | --- | --- |
| right on some MAI attempts, wrong on others | **RFT** (after checking the reward ranks the right attempts higher) | the behaviour exists; RFT makes it the default |
| wrong on every MAI attempt, right on Sol | **Skill** | RFT cannot reinforce what never happens. Teach the procedure first, then RFT can sharpen it |
| wrong on Sol too | **World or rubrics**, not the model | if the frontier model can't do it with this skill, the task is mis-specified, too hard, or the answer key is wrong. Fix that before the climb |
| right on every MAI attempt | nothing | already won |

---

## 3. The stages

One change per stage. Each stage starts as a copy of the previous one's `config/`. Stages close with a written README and a git tag (`climb2-stage-N`).

| Stage | One change | Question it answers | Gate to go on |
| --- | --- | --- | --- |
| **0 · Frontier reference** | Model = GPT-5.6-Sol | What does the world allow with this skill and these rubrics? Which claims are unwinnable even for Sol? | Sol correct on ≥ 26/30. Claims Sol gets wrong are investigated (world, answer key, skill) before stage 1 |
| **1 · Small-model baseline and headroom** | Model = MAI-CODE-5b, each claim run **k = 3** times | Floor (mean), reach (any of 3), variance, and whether the rubric score ranks MAI's right attempts above its wrong ones | Every claim classified (§2 table). Headroom stated as two numbers: total gap and RFT-capturable gap |
| **2 · Reward alignment** | Rubrics only (checklist and red flags) | Does the reward prefer MAI's right attempts? | Within-claim ranking ≥ 90%; no wrong answer scores ≥ 0.6. Skip this stage if stage 1 already passes |
| **3 · Skill, one fix at a time** | Skill only: 3a, 3b … each one targeted fix for one "never right" class | Can a procedure the model lacks be taught? | Each sub-stage kept only if correctness rises against the previous one. A regression is reverted, not stacked |
| **4 · RFT** | Model weights (`tune start` on `mai-code-1-flash`) | Does tuning convert reach into floor? | Tuned `Simple` vs base `Simple` on the 30 evaluation claims, with GPT-5.6-Sol as reference |

### Why in this order

- **Sol first.** Without a ceiling you can't tell a weak model from an unfair world. Attempt 1 skipped this on world v3 and spent two stages tuning against claims that may be broken.
- **Repeats before changes.** Attempt 1 compared single runs, so a 5-claim drop in stage 2 could not be separated from run-to-run noise. Three repeats give a variance estimate and the "right in any of k" reach, with every candidate answer visible (the platform's `BestOfN` returns only the winner).
- **Rubrics before skills.** The reward must be right before anything is optimised against it; changing the rubrics also resets every score baseline (📄 "changed rubrics require a new baseline").
- **One skill fix at a time.** Attempt 1's stage 2b added method, a folder map and hand-in rules together; correctness fell 22 → 17 and the cause could not be isolated.
- **RFT last.** 📄 "Deep starts from stable Light artifacts." Tuning bakes the current skill, rubrics and tools into the weights; changing them afterwards needs a new tuning job.

---

## 4. What every stage measures

| Number | Source | Why |
| --- | --- | --- |
| Rubric score | The platform (`evaluate results`) | It is the RFT reward |
| Correct (decision + governing instrument + payable) | `scripts/score_ground_truth.py` against `world-builder/out/data/claims.json` | Whether the answer is right |
| Hand-in failures | Echoed questions, stubs, "could not access" answers | Platform/agent failures that are neither reasoning nor reward |
| Calls and minutes per claim | Execution records | Cost, and a sign of wandering |
| Reward ranking | % of (right, wrong) answer pairs where right scores higher | Whether the reward can be trusted |

A stage that doesn't improve is still closed and written up. That is a finding.

---

## 5. Rules carried from the CLI docs 📄

| Rule | Source |
| --- | --- |
| `tune start` uses the environment's eligible **Training** samples, not a per-command subset; minimum 11 | Model-tuning playbook |
| Keep the 30 Evaluation claims out of every refinement and training step; they are the final test | Guide, "Keep comparisons meaningful" |
| `skills refine start --mode instruction` changes only the skill; `--mode rubrics` only the rubrics. Never use `both` for a one-variable stage | Skill- and rubric-tuning playbooks (CLI ≥ 1.0) |
| A refinement's predicted score is not a measurement; re-evaluate the same claims | Skill-tuning playbook |
| `tune status … readyForEvaluation: true` is the only signal that a tuned model can be evaluated | Fine-tuning reference |
| After tuning: base `Simple` vs tuned `Simple` isolates the model gain; tuned `TreeSearch` is an optional third arm | Tuning-flows playbook |
| An unknown submission outcome is read, never resubmitted | Troubleshooting playbook |

Full docs: <https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1> (agent guidance under `/v1/agent-guidance/GUIDE.html`).

---

## 6. Where the skill and rubrics came from

Every stage README records, in its *What changed* table, how its skill and rubrics were made: **by hand**, **generated by the platform** (and from what), or **carried over unchanged** (from which stage). This section is the history so far. 🖥️ It is reconstructed from `world-builder/docs/03-scenario-design.md`, `world-builder/SETUP.md` (step P9) and `archive/attempt-1/`; file identities were checked on 2026-10-13.

### Before this project

The earlier showcases in `C:\Users\sansri\finetuning samples\` (supply-chain allocation recovery, retail, rft-sample) are **separate projects**. They didn't use the Frontier Tuning CLI, skills or rubrics. Each fine-tuned models directly in Azure AI Foundry with a fixed policy prompt and a **deterministic Python grader**. The supply-chain one used `gpt-5.2` as teacher, `gpt-4.1-mini` for SFT and `o4-mini` for RFT. What carried over is the method: a frontier teacher first, a pilot gate on reward variation, held-out evaluation, and a pre-submit audit of the reward.

### The warranty project

| When | Skill | Rubrics | Made with the platform? |
| --- | --- | --- | --- |
| **Design** (world-builder 03 § 9.2) | Not yet written | **Six rubrics designed by hand first** ("written before the skill exists"), one per group of the 12 traps. Every trap must map to a rubric item | No |
| **World v2, first climb** | 🔬 Not recorded here (files removed 2026-10-08; in git history) | Platform-generated | Generation used. Lesson carried forward: the generated rubrics gave wrong answers full marks |
| **Attempt 1, stage 0** (2026-10-03) | **Hand-written business brief**: the job, the sources, how to write. It deliberately leaves out the rules that solve the traps | **Generated by the platform from the skill**: `skills create` with `generateRubrics: true` on `wce-dev`. Five rubrics, pinned and copied to `wce-main` | **Yes: skill → rubrics.** Not repeatable: the same file gave 5, then 1, then a different 5 rubrics |
| **Attempt 1, stage 1** (2026-10-08) | Unchanged | **The hand-designed six**, reviewed and revised against stage 0's answers ([changes and evidence](../archive/attempt-1/stages/stage-1/rubrics.md)) | No. Right answer ranked above wrong: 83% → 93% |
| **Attempt 1, stage 2** (2026-10-09) | 2a: `skills enrich` (no change); `skills refine` (CLI 0.3.17) rewrote the skill **from the rubrics**, copying their wording, so it was **rejected**. 2b: our hand-written guidance, a regression (22 → 17/29), **not kept** | Unchanged | **Yes: rubrics → skill**, rejected. That's why `check-skill.py` exists and why only `--mode instruction` is used now |
| **Attempt 2, stage 0** (2026-10-11) | Attempt 1's hand-written business brief, **identical text** (description restored) | Attempt 1 stage 1's hand-written six, **identical** (verified 2026-10-13) | No |

**In short: the rubrics were designed by hand first; the skill was then written by hand as a business brief without the trap rules.** The platform generated rubrics *from* the skill once (attempt 1, stage 0), and those were replaced. The platform rewrote the skill *from* the rubrics once (attempt 1, stage 2a), and that was rejected. The skill has never been generated from the rubrics in a version that was kept.

### How this shapes the stages ahead

| Stage | Skill | Rubrics | Platform tool, if used |
| --- | --- | --- | --- |
| Rubric stage (reward alignment) | Carried over | **Edited**: by hand from measured misrankings (e.g. 04151, where Valuation must require *applying* the superseding price), or by `rubrics refine` / `skills refine --mode rubrics`, which proposes changes for review | Proposals reviewed before applying; never `--mode both` |
| Skill stage(s) | **Edited**, one fix at a time: by hand or `skills refine --mode instruction` (Training claims only) | Carried over | Every candidate checked with `check-skill.py` for rubric wording |
| Small-model stages | Carried over from the final Sol stages | Carried over | — |
