# Rubric design

**Cross-cutting reference.** Applies to every scenario, not just the contract
renewal one. Read it before writing rubrics for a new skill.

Quotes marked 📄 are from the upstream `m365-core/orbit` playbook, pinned at
`a4b21bd`. Anything marked **[observed]** is our own measurement.

For what goes wrong in practice, see
[rubric-defects.md](rubric-defects.md) — a case library kept across scenarios.
For grading things a rubric cannot see directly, see
[rubric-patterns.md](rubric-patterns.md).

---

## 1. What a rubric is

One short success criterion, written in markdown in the same file as the skill and
uploaded with it. A skill carries a handful of them.

- **The judge sees it. The model never does.** A rubric is not an instruction. The
  model is given the skill and the question; the rubric goes only to the grader,
  afterwards.
- **It must be checkable from the output alone.** *"Cites the sources used"* can be
  marked by a reader. *"Demonstrates good judgement"* cannot.
- **It is scored on every inference**, returning a `Score`, a `Reasoning` string,
  and a `Skip` reason when the criterion did not apply. You do not have to run an
  evaluation to get rubric scores.

### One rubric set per skill, not one per question

Rubrics attach to the **skill**, so every question routed to that skill is graded
against all of them. There is no per-question rubric, and there cannot be —
nothing in the pipeline knows what kind of question arrived.

When a criterion does not apply to the question asked, the grader returns
`Score: null` with a written `Skip` reason. **A skipped rubric drops out of the
mean rather than scoring zero.**

> **[observed]** All seven probes were graded against the same five rubrics.
> Probe 1 skipped two: *"The request explicitly asks for the full accessible
> inventory … window inclusion, exclusion, and boundary handling cannot be
> evaluated."*

So the requirement is not a rubric per question type. It is that **every rubric
must be satisfiable — or skippable — across the whole range of questions the
skill serves.** A bullet that is unmeetable on some legitimate path is a bug, not
strictness.

> **[observed]** A correct refusal scored **0.00 on two rubrics** instead of
> skipping, because both demanded a date and a reference code that could not exist
> when nothing matched. See
> probe-sweep.md, probe 5.

When questions diverge too far for one honest rubric set, that is the signal to
split the skill — see [§ 3](#3-sequencing--rubrics-before-skills).

---

## 2. Why a rubric is required

It does three jobs at once, which is why it matters more than people expect:

📄 `20-product/worlds-and-rles.md`

| Job | Effect |
| --- | --- |
| **Inference-time selection** | Test-time search uses rubrics to pick the strongest of several candidate responses |
| **Reward function** | Fine-tuning uses rubrics to decide what "better" means |
| **Evaluation score** | Per-inference scores you can read and act on |

Two consequences worth internalising:

**Rubrics improve quality before any model is fine-tuned.**

> *"A world with good rubrics and no fine-tuning often outperforms one with a
> fine-tuned model and weak rubrics."*

**A bad rubric is not merely a bad measurement — under tuning it becomes a bad
training signal.**

> *"Everything in the world contributes: a half-finished skill, a set of weak
> samples, or a rubric that measures the wrong thing all affect the result. Get
> skills, rubrics, and samples into good shape first — **fine-tuning amplifies
> what is there; it does not repair it.**"*

---

## 3. Sequencing — rubrics before skills

Upstream calls this *"the single most important sequencing rule"* of the build
phase:

> **"Define the rubric before you build the skill.** Success criteria first. A
> skill built before anyone agreed what good looks like will be evaluated against
> criteria invented to fit it."
> — `10-engagement/03-build-and-evaluate.md`

The prescribed order of work:

1. Set up the world, confirm access for the people who will validate it
2. Connect tools — usually the long pole
3. **Define rubrics for the first skill**
4. Author the skill
5. Add samples
6. Iterate with validator review
7. Build the evaluation contract and establish the baseline
8. Run validation cycles with real users on real cases

**Why the order matters:** if the skill comes first, its instructions tend to
encode the standard, and the rubrics end up restating the instructions. The task
is then solved in the prompt, the weights have nothing to contribute, and the
world saturates.

> **[observed]** In the reference scenario, all five rubrics are restated nearly
> verbatim in the skill prompt. Upstream names this as the primary cause of a
> saturated world. See guide 01 § 7.

Related rule — keep the skill narrow:

> *"A skill that does one job well is easier to evaluate, easier to fix, and
> easier to trust. Broad skills fail in ways nobody can diagnose."*

---

## Sources

📄 quotes come from `20-product/worlds-and-rles.md` and
`10-engagement/03-build-and-evaluate.md`, relative to
`.upstream/orbit/FT-Playbook/`, pinned at `a4b21bd`.

**[observed]** items come from this repo's probe sweep on 19 September 2026 —
see probe-sweep.md.
