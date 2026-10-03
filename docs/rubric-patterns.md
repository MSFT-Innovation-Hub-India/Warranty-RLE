# Rubric patterns for hard cases

**Cross-cutting reference.** Techniques for grading things a rubric cannot see
directly. Companion to [rubric-design.md](rubric-design.md), which covers what a
rubric is and why it is required.

> One pattern so far — multi-source joins. Add sections as new shapes of problem
> come up.

Worked through using the contract renewal scenario
(guide 01 § 9),
but the recipe is not specific to it.

---

## Multi-source joins

*A join is a reasoning step. Rubrics grade text. How can a rubric possibly cover
"did it correctly combine two sources"?*

### The reframe — grade provenance, not process

Upstream's constraint is explicit:

> *"Write criteria that are **observable in the output**. A grader marks what it
> can see. 'Cites the sources used' is checkable; 'demonstrates good judgement'
> is not."*
> — `20-product/worlds-and-rles.md`

You cannot grade the join. But **you do not need to** — because a join that
happened and a join that did not leave *different text behind*.

Look at probe 4. The model told us exactly what it had done:

> *"Exact spend source: SA-2024-089 Contoso Facilities Management.docx, §4
> 'Charges and escalation,' clause 4.1"*

**The failure was already visible in the output.** It named a contract where the
workbook was required. No rubric asked, so nobody looked. The problem was never
observability — it was that nothing was watching.

### First lever — bind each claim type to its required source

Upstream ships a skill that does exactly this. `renewal-risk-brief` joins three
sources — contracts, spend workbook, Teams channel — and its first rubric is:

```text
### Evidence grounding
Description: Every factual claim is traceable to a named source.
- Names the agreement reference code and the clause behind each contractual term
- Attributes every monetary figure to the spend workbook and names the contract year
- Attributes service and adoption concerns to the vendor operations channel
- Introduces no figure, date, or issue that is absent from the sources
```

Read what that is doing. It never says "perform a join". It establishes a
**claim-type → required-source mapping**, one bullet per source:

| Claim type | Must be attributed to |
| --- | --- |
| Contractual term | The agreement, **naming the clause** |
| Monetary figure | **The spend workbook**, naming the contract year |
| Service / adoption concern | The vendor operations channel |
| Anything else | *Nothing* — fourth bullet forbids unsourced content |

A model that skips the workbook now has nowhere to hide. To satisfy bullet 2 it
must cite the workbook; to cite the workbook it must open it. **The join becomes
a precondition of a well-formed answer**, and the grader checks the trace rather
than the reasoning.

> 💡 Apply that rubric to probe 4 and it fails immediately: monetary figures
> attributed to a `.docx` clause, and no contract year named. Both halves of
> bullet 2, missed.

### Second lever — require a derived quantity

`renewal-risk-brief` has another rubric that catches the join from a different
angle:

```text
### Commercial accuracy
- States the annual commitment and the most recent actual spend correctly
- States actual spend as a percentage of commitment
- Correctly identifies whether the vendor is over or under commitment
```

**Commitment lives in the contract. Actual spend lives in the workbook.** A
percentage of one against the other is a number that *cannot be produced without
both*. You are not grading the join — you are grading an artefact only a correct
join can generate.

That is the stronger technique, because it is not fooled by a citation that
merely *looks* right: get either input wrong and the percentage is wrong.

Under this rubric probe 4's Fabrikam claim collapses. It reported $840,000. The
workbook says $312,000 against an $840,000 commitment — **37.1%**, badly under.
The answer implied the opposite.

### Third lever — say what happens when sources disagree

The skill instructions add:

> *"Where the sources disagree, say so rather than choosing one."*

Joins fail in a way single-source lookups do not: two sources answer the same
question differently. Decide whether the model should reconcile, prefer a
precedence order, or surface the conflict — then make that choice gradeable.
Guide 02's harder world does this with amendment precedence (*"uses the notice
period set by the most recent amending instrument"*).

### The general recipe

For any multi-source task, write rubrics on four axes:

| Axis | Bullet shape | Catches |
| --- | --- | --- |
| **Provenance** | "Attributes every ⟨claim type⟩ to ⟨source⟩" | Right answer, wrong source |
| **Derived quantity** | "States ⟨A from source 1⟩ as a proportion of ⟨B from source 2⟩" | A join that never happened |
| **Conflict** | "Where sources disagree, states both" / "⟨source X⟩ governs" | Silent, arbitrary tie-breaking |
| **Closure** | "Introduces no figure absent from the sources" / "reports explicitly when a source has nothing" | Invention, and silent omission |

That fourth axis is easy to forget. `renewal-risk-brief` spends a bullet on it —
*"Explicitly reports when the vendor operations channel records nothing"* —
because a source that contributed nothing is indistinguishable, in the output,
from a source that was never consulted. **Force the negative to be stated** and
the distinction becomes gradeable.

### Applied to the contract renewal world

[Defect 2](rubric-defects.md#defect-2--nothing-measures-cross-source-provenance)'s
fix is now concrete — **for `renewal-risk-brief`, when we build it.** Upstream
already ships that skill with an `Evidence grounding` rubric doing exactly this.
Our own version would add:

```text
### Evidence grounding
Description: Every factual claim is traceable to the source that owns it.
- Attributes every contractual term to the agreement reference code and clause
- Attributes every monetary figure to the spend workbook, naming the contract year
- Distinguishes contractual commitment from actual spend, and labels which is which
- Introduces no figure absent from the sources

### Directness
Description: The question asked is answered before any supporting detail.
- States the single item the question asks for as the first claim in the response
- Where a comparison is requested, states the basis of comparison used
```

> ⚠️ **Do not add these to `renewal-notice-check`.** That skill has no spend
> remit, no spend samples, and adding spend rubrics to it would make every
> notice-deadline sample score against criteria it cannot satisfy — manufacturing
> the *opposite* failure. Rubrics belong to the skill whose job they describe.

The third bullet of *Evidence grounding* is the one that would have caught probe
4's half-million-dollar error — not because it mentions joins, but because it
forces the two quantities to be told apart.

> 💭 **The insight worth carrying:** rubrics cannot see reasoning, so make the
> reasoning *leave evidence*. Demand provenance per claim type, demand a figure
> that requires both sources, and demand that absence be stated out loud. The
> join then becomes observable — and anything observable is gradeable.
