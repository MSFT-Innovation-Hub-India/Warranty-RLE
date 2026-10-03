# Rubric defects seen in practice

**Cross-cutting case library.** Each entry is a rubric defect found while building
one scenario. The *specifics* belong to that scenario; the *mechanism* generalises,
which is why they are collected here rather than buried in a build log.

Companion to [rubric-design.md](rubric-design.md) — that page says what a rubric
is and why it is required. This one shows what goes wrong.

> One scenario is covered so far. Add a section per scenario as they are built.

| # | Defect | Found in | Mechanism that generalises |
| --- | --- | --- | --- |
| 1 | [Rubrics penalise correct refusals](#defect-1--rubrics-penalise-correct-refusals) | Contract renewal | A rubric that cannot be satisfied on the empty-result path turns correct behaviour into a zero |
| 2 | [Nothing measures cross-source provenance](#defect-2--nothing-measures-cross-source-provenance) | Contract renewal | A question outside the skill's remit still scores 1.00, because the rubrics have no opinion about it |
| 3 | [The prompt gives away every rubric](#defect-3--the-prompt-gives-away-every-rubric) | Contract renewal | Restating the rubrics in the instructions solves the task in the prompt, leaving the weights nothing to contribute |

---

## Scenario — contract renewal (`renewal-notice-check`)

Found during the probe sweep on 19 September 2026. Full transcripts:
probe-sweep.md. Summary and scope:
guide 01 § 9.

None of the three are *model* defects. They are also not all *this scenario's*
defects, and that distinction decides what to fix now — the scope table lives in
guide 01.

### Defect 1 — Rubrics penalise correct refusals

*Date accuracy* and *Sourcing* have no "not applicable when nothing was found"
escape. Probe 5 scored 0.00 for being right.

> 📍 **Scope check, honestly.** Probe 5 asked about a vendor that does not exist.
> The asset *does* have an in-scope empty case — sample 6, *"Are there any notice
> deadlines between 1 January 2027 and 31 March 2027?"* — and the design sidesteps
> the problem neatly: the skill is instructed to *"say so in one sentence and give
> the date of the next deadline that falls after the window."* That answer still
> contains a date and an agreement reference, so both rubrics remain satisfiable.
>
> **The gap only opens for a subject that does not exist at all**, where there is
> no "next deadline" to fall back on. Real corpora are full of those — misspelled
> vendors, lapsed entities, wrong business unit — so the gap is worth closing even
> though the reference samples never hit it.

**Fix:** add a satisfiable branch, e.g. *"or states plainly that no matching
agreement exists in the library."*

⚠️ Samples snapshot rubrics **at upload time**. Edit a rubric after uploading and
scores will not move — and you will conclude the edit did nothing. Re-upload. Note
that re-uploading *adds* copies rather than replacing them.

### Defect 2 — Nothing measures cross-source provenance

*(Next scenario's problem.)*

> 📍 **Scope check.** Probe 4 asked a spend question. **No sample in this
> scenario asks about spend** — that is `renewal-risk-brief`, and upstream already
> ships it with the provenance rubric this finding calls for
> ([rubric-patterns.md](rubric-patterns.md)).
> The `renewal-notice-check` rubric is *correct for its job*; it simply has no
> opinion about a question it was never given.
>
> Keep reading anyway. The mechanism it demonstrates — a confidently wrong answer
> scoring 1.00 because nothing measured the relevant thing — is general, and it is
> exactly what you will face when you *do* build the cross-source skill.

Probe 4 quoted contractual commitments where actual spend was asked for — wrong by
**$528,000 on Fabrikam alone** — buried the answer, and scored 1.00 across the
board.

> 📍 **Correction of framing — this is not a defect in the reference asset.**
> Probe 4 asked a `renewal-risk-brief` question of the `renewal-notice-check`
> skill. The rubrics scored 1.00 because the model performed the notice-deadline
> task correctly, which is exactly what that skill and those rubrics are for. The
> asset is behaving as designed.
>
> **Do not "fix" this by adding spend rubrics to `renewal-notice-check`.** That
> would make one skill grade work that belongs to another, and is the opposite of
> the upstream pattern.

**The real lesson is about scope, not about a bug:** a skill answers whatever you
ask it, graded only against its own rubrics. Ask outside its remit and you get a
confident, well-formed, perfectly-scored answer to a question it was never built
for. **Nothing in the score tells you that happened.**

**The actual fix** is the one upstream already wrote: create the second skill.
`renewal-risk-brief` owns the cross-source work and carries an *Evidence
grounding* rubric that binds monetary figures to the workbook.
[rubric-patterns.md](rubric-patterns.md)
works through why that rubric would have caught every error above.

> 📄 **Authored guidance, not runtime output.** Upstream names this exact symptom
> — *"score good, output visibly wrong → the rubric is measuring the wrong
> thing"* — in `20-product/worlds-and-rles.md` and
> `10-engagement/03-build-and-evaluate.md`, and a third time in
> `10-engagement/04-pilot-and-prove.md` as a pilot signal (*"high correction rate
> → output is close but not trusted → examine rubrics"*).
>
> These are markdown files written by a person, **not something the environment
> reports.** The execution above returned `Score`, `Reasoning` and `Skip` and
> nothing else — no warning field, no diagnostic, no confidence signal. The
> service said 1.00 five times.
>
> So probe 4 is not an exotic edge case. It is a **documented, expected failure
> mode** — and the guidance is to treat a good score with a visibly wrong output
> as evidence about the *rubric*, not the model. But you have to notice it
> yourself; nothing will flag it.

### Defect 3 — The prompt gives away every rubric

The side-by-side in
guide 01 § 7
shows all five rubrics restated in the instructions.

**Consequence:** the task is solved in the prompt, so there is nothing left for
model weights to contribute. This is the primary documented cause of a saturated
world.

**Fix:** thin the instructions to role and goal only. Let the standard live in the
rubrics, which the grader sees and the model does not. Guide 02's asset does
exactly this — its entire instruction block is:

```text
You support the Vendor Review Board on contract renewals.

When someone asks about non-renewal notice deadlines, work out from the
contracts library which agreements require notice inside the window they are
asking about, and tell them what they need to know to act.
```

Two sentences. No ordering rule, no citation rule, no format rule. Compare that to
the twelve-sentence prompt we shipped.

> 📖 Upstream gives the root cause as an ordering rule: **"Define rubrics before
> the skill. Success criteria first. A rubric written after the skill tends to
> describe what the skill already does."** We did it the other way round, and got
> exactly the predicted result. See
> [rubric-design.md § 3](rubric-design.md#3-sequencing--rubrics-before-skills).

---

## Can the platform catch these?

Worth answering directly, because it determines how much of the quality burden
sits with you.

### What exists

🖥️ Verified against CLI 0.3.11 on this tenant:

| Capability | Command | Status |
| --- | --- | --- |
| Rubric **generation** from instructions | `skills generate-rubrics` | ✅ Available |
| Rubric **refinement** from evaluation signal | `rubrics refine start … apply` | ✅ Available |
| Environment quality scoring | `rle-quality check` | ❌ **`Environment not found, or quality scoring is not enabled for it.`** |
| Workspace health + LLM insights | `health get` / `health insights` | Available, not exercised here |
| Evaluation diagnostics | `evaluate diagnostics` | 🔬 Flighted — gated per tenant |

`rubrics refine` is the closest thing to "the platform fixes your rubrics". It
runs a job against the current rubrics and returns a **proposal**:

```powershell
frontier-tuning rubrics refine start  --skill-id <id>
frontier-tuning rubrics refine detail <refinement-id>
frontier-tuning rubrics refine apply  <refinement-id> --skill-id <id>
```

### The limits — and one that really matters

**1. Nothing is automatic.** Refinement is *"a proposal, not an edit. Nothing
changes until you apply it."* There is no closed loop.

**2. 💭 Refinement learns from evaluation signal — and defect 2 produces none.**

This is the important one, and it is worth stating plainly:

> A rubric that measures the wrong thing **does not generate failing evidence**.
> Probe 4 scored 1.00 on all five. There is no low score to diagnose, no failing
> sample to learn from, no signal for a refinement job to act on.
>
> **The blind spot conceals itself in exactly the data a refiner would use to
> find it.**

Refinement is good at *"this rubric is scoring harshly / inconsistently / is hard
to satisfy"* — visible in the scores. It is structurally weak at *"you never wrote
a rubric for the thing that actually matters"*, because absence leaves no trace.

Defect 1 is the opposite case and **is** refinable: probe 5's 0.00s are loud,
attributable, and exactly the kind of signal refinement consumes.

| Defect | Visible in scores? | Could refinement find it? |
| --- | --- | --- |
| 1 — penalises correct refusals | ✅ Two 0.00s | ✅ Plausibly |
| 2 — nothing measures the real question | ❌ Everything is 1.00 | ❌ **No signal to work from** |
| 3 — prompt restates rubrics | ❌ Everything is 1.00 | ❌ Not a rubric defect — a skill defect |

**3. Upstream says the human review is the control, not the algorithm:**

> *"Review proposals with the workflow owner. **A rubric that drifts away from the
> customer's real standard scores well and means nothing.**"*
> — `70-roadmap/features/rubric-refinement.md`

> *"Generate, then edit by hand. This is the recommended practice, not a
> compromise. Generation gives you the shape; **manual editing is what captures
> the customer's actual standard.**"*
> — `70-roadmap/features/rubric-generation.md`

### So: is the concern justified?

**Yes.** If the rubrics are wrong, everything downstream inherits it — upstream is
unambiguous:

> *"Everything in the world contributes: a half-finished skill, a set of weak
> samples, or **a rubric that measures the wrong thing** all affect the result.
> Get skills, rubrics, and samples into good shape first — **fine-tuning amplifies
> what is there; it does not repair it.**"*
> — `20-product/worlds-and-rles.md`

Fine-tuning optimises *toward the rubric*. It has no mechanism for noticing the
rubric was the wrong target. A misaligned rubric does not merely mis-report
quality — under tuning it actively trains the wrong behaviour, which is precisely
the danger in defect 1.

**The practical rule:** the platform will help you *write* rubrics faster
(`generate-rubrics`) and *tighten* rubrics that visibly misbehave
(`rubrics refine`). **Deciding what should be measured at all remains entirely
yours,** and no amount of tuning compensates for getting it wrong.
