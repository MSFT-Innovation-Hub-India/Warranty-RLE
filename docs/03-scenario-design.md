# Guide 03 — Designing a showcase world you can actually hill-climb

**Status: design, not record.** Nothing in this document has been built or
measured. Every number in it is a **target or a prediction**, marked as such.
The conventions of [guides/README.md](README.md) apply — 📄 is upstream, 🔬 is
unverified, 💭 is a judgement call with the reasoning shown, ⚠️ is a step that
destroys state.

This document answers one question: **what world would demonstrate the full
frontier-tuning journey — inner-loop quality work first, then RFT on a small
model — using content that looks like a real enterprise?**

It does not curate the content. It decides *what* to curate, and justifies it.
The manifest in [§ 13](#13-content-manifest--what-gets-curated-next) is the input
to that next step.

---

## Table of contents

1. [The design problem, stated precisely](#1-the-design-problem-stated-precisely)
2. [What only training can fix](#2-what-only-training-can-fix)
3. [Design principles that fall out of that](#3-design-principles-that-fall-out-of-that)
4. [Choosing the domain](#4-choosing-the-domain)
5. [The scenario](#5-the-scenario--contoso-industrial-warranty-adjudication)
6. [Source architecture — what lives where, and why](#6-source-architecture--what-lives-where-and-why)
7. [The trap surface](#7-the-trap-surface)
8. [A worked example, end to end](#8-a-worked-example-end-to-end)
9. [Skills and rubrics](#9-skills-and-rubrics)
10. [Samples](#10-samples)
11. [The climb, stage by stage](#11-the-climb-stage-by-stage)
12. [The RFT stage, and the comparison problem](#12-the-rft-stage-and-the-comparison-problem)
13. [Content manifest — what gets curated next](#13-content-manifest--what-gets-curated-next)
14. [Operational budget](#14-operational-budget)
15. [Risks and pre-flight checks](#15-risks-and-pre-flight-checks)
16. [Open questions for you](#16-open-questions-for-you)

---

## 1. The design problem, stated precisely

You are not asking for "a good demo". You are asking for a world with a
**specific, engineered difficulty curve**. That is a much narrower target, and
most realistic-looking scenarios fail it.

Four constraints have to hold at once:

| # | Constraint | Why it is hard |
| --- | --- | --- |
| 1 | The naive build must score **low for a diagnosable reason** | Easy to make a world score low by breaking retrieval. Useless — 📄 your own decision bands say *"near zero everywhere → almost always retrieval → fix retrieval, do not tune"*. The low score must come from **reasoning and procedure**, with retrieval demonstrably working |
| 2 | Inner-loop work must move the number **visibly and attributably** | Not "it went up". You need to point at a rubric and say *this* bullet moved *that* much. That requires per-rubric failure modes that are independent of each other |
| 3 | After the inner loop is exhausted, **headroom must remain** | This is the constraint that kills most designs. If good rubrics + a thin prompt + a frontier model reach 0.97, you are back where guide 01 ended. Something must survive a competent model and a well-written prompt |
| 4 | The surviving headroom must be **the kind RFT closes** | Residual difficulty that training cannot touch either (e.g. genuinely ambiguous ground truth) produces a flat tuning result and a dead demo |

Constraints 3 and 4 together are the whole design. Everything else is
craftsmanship.

### The trajectory you are engineering

Target shape — **predictions, not measurements**:

```text
 1.00 ┤                                                  ceiling (frontier + good world)
      │                                         ╭────────●  ~0.90  frontier model, tuned world
 0.90 ┤                               ╭─────────╯
      │                     ╭─────────╯  ~0.82  frontier model, good rubrics
 0.80 ┤           ╭─────────╯                            ●  ~0.80  TUNED mini  ← the money shot
      │           │                                    ╱
 0.70 ┤     ╭─────╯  ~0.66  tools registered          ╱
      │     │                                        ╱
 0.60 ┤     │                                       ╱
      │     │                                      ╱
 0.50 ┤─────╯  ~0.48  naive build                  ╱
      │                                   ────────●  ~0.55  UNTUNED mini
 0.40 ┤
      └──────┬──────┬──────┬──────┬──────┬──────┬────────
          Stage0 Stage1 Stage2 Stage3  │   Stage4
                                       │
                          the gap RFT is asked to close
```

Two separate stories, and they must not be conflated:

- **The inner-loop story** (Stage 0 → 3) is *the world got better*. Same model
  throughout. This is where most of the gain lives, and 📄 upstream says so
  outright: *"a world with good rubrics and no fine-tuning often outperforms one
  with a fine-tuned model and weak rubrics."*
- **The RFT story** (Stage 4) is *a small model learned to do what only a large
  model could do*. Different model, same world. The claim is about **cost and
  latency at held quality**, not about making a frontier model smarter.

💭 Conflating these is the single most common way this demo goes wrong. If you
show one line going from 0.48 to 0.80 and call it "fine-tuning", you have
misrepresented roughly 0.30 of work that was rubric authoring. Keep two axes.

---

## 2. What only training can fix

This is the hardest question in the design and everything downstream depends on
getting it right. If you cannot name what survives a good prompt, you cannot
build a world with headroom.

Four candidate answers, assessed honestly:

| Candidate | Does prompting fix it? | Does RFT fix it? | Verdict |
| --- | --- | --- | --- |
| **Missing knowledge** (facts not in the corpus) | No | No — RFT is not knowledge injection | ❌ Useless. Produces a flat tuning result |
| **Long conditional procedure** — precedence chains, caps, unit rules | Yes on a frontier model, **poorly on a small one** | **Yes** | ✅ **Primary lever** |
| **Multi-hop tool orchestration** — which tool, in what order, how many times, when to stop | Partially. Small models drop hops and hallucinate the missing one | **Yes — this is what RL over trajectories is for** | ✅ **Primary lever** |
| **Calibrated abstention** — knowing when evidence is insufficient and naming what is missing | Badly. Prompted abstention is either over-triggered or ignored | **Yes** — it is a reward-shaped behaviour | ✅ **Secondary lever, high demo value** |
| **Output protocol discipline** under a long context | Yes, cheaply | Yes | ⚠️ Weak lever alone — but a good *consistency* signal |

💭 **The conclusion that shapes the whole scenario.** The headroom you want is
not *difficulty* in the abstract. It is **procedural depth that a frontier model
can follow from a thin prompt and a small model cannot**. That is a precise,
buildable target:

> Build a task whose correct execution requires a **4–6 hop tool trajectory**,
> a **3-level precedence rule**, a **conditional arithmetic cap**, and a
> **defensible refusal path** — then write the standard into rubrics rather than
> the prompt, so the small model has to learn it rather than read it.

That sentence is the specification. Sections 5–9 are an instance of it.

### Why the small model matters to the business story

The RFT narrative only lands if the tuned model is one a customer would actually
want to run. `gpt-54-mini` is in `FTBaseModels` ([CLI-REFERENCE § models](CLI-REFERENCE.md#models)).
The claim becomes:

> "This task needed a frontier reasoning model. After tuning, a mini model does
> it at **0.80 vs the frontier model's 0.90** — at a fraction of the cost and
> latency, inside our compliance boundary."

That is a procurement-grade claim. "We fine-tuned and the number went up" is not.

⚠️ Section 12 covers the reason this claim is currently **at risk** on your
tenant, and what to do about it.

---

## 3. Design principles that fall out of that

Seven rules. Each one is a decision you will be tempted to break later.

| # | Principle | Consequence if broken |
| --- | --- | --- |
| 1 | **Difficulty comes from reasoning, never from broken retrieval** | A world that scores low because content is unreachable teaches nothing and points the diagnosis at the wrong place |
| 2 | **Every fact needed for a correct answer must be reachable** — and provably so, by a `chat` probe | Otherwise you cannot tell a reasoning failure from a plumbing failure, which is exactly the day guide 01 lost |
| 3 | **Rubrics before skills**, always | 📄 *"A rubric written after the skill tends to describe what the skill already does."* This is the documented cause of guide 01's saturation |
| 4 | **The standard lives in rubrics, not in the prompt** | Restating rubrics in the prompt solves the task at inference and leaves the weights nothing to learn. [rubric-defects § 3](rubric-defects.md#defect-3--the-prompt-gives-away-every-rubric) |
| 5 | **Every rubric must be satisfiable *or* skippable on every legitimate path** — including the empty and refusal paths | [rubric-defects § 1](rubric-defects.md#defect-1--rubrics-penalise-correct-refusals). Under tuning this is not a bad measurement, it is a reward function that trains hallucination |
| 6 | **Traps must be independent** | Correlated traps move rubrics together and you lose attribution. Each trap gets its own rubric line and its own samples |
| 7 | **Ground truth must be computable by a human in under two minutes** | If you cannot check an answer quickly by hand, you cannot audit the grader, and you will trust a number you should not |

Principle 7 deserves emphasis. [rubric-defects § 2](rubric-defects.md#defect-2--nothing-measures-cross-source-provenance)
is the record of a confidently wrong answer scoring 1.00 five times. The only
defence is out-of-band ground truth that a person can verify. Section 8 shows
what that looks like.

---

## 4. Choosing the domain

Six domains were assessed against the four constraints in § 1 plus your explicit
requirement for SharePoint + Teams + structured database + MCP actions.

| Domain | Four sources natural? | Computable ground truth | Procedural depth | Action surface | Audience reach | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **Warranty & field-service claim adjudication** | ✅ Policy/TSB docs, rate-card sheets, asset + claim DB, field channel | ✅ Coverage and payable amount are arithmetic | ✅ 3-level precedence, dual-limit expiry, conditional caps | ✅ Draft adjudication, request evidence, escalate goodwill | ✅ Manufacturing, auto, durables, energy | ✅ **Recommended** |
| **Deal desk / quote approval** | ✅ Discount policy, approval matrix, pricebook DB, deal room | ✅ Floor price, margin, approval tier | ✅ Tiered approvals, effective dates | ✅ Submit for approval | ✅ B2B software, distribution | ✅ **Strong runner-up** |
| Supplier quality / NCR & CAPA | ✅ | ⚠️ Partly — disposition is judgement | ✅ | ✅ | ⚠️ Narrower | ⚠️ Viable |
| ITSM change / incident review | ✅ CMDB is a great DB fit | ⚠️ "Is this change safe" is contestable | ✅ | ✅ | ✅ | ⚠️ Ground truth too soft |
| Rev-rec / O2C exception handling | ✅ | ✅ Very computable | ✅ | ⚠️ Actions are audit-sensitive | ⚠️ Dry | ⚠️ Risky to demo |
| Customer renewal / churn (CSM) | ✅ QBR decks fit naturally | ❌ Churn risk has no right answer | ⚠️ | ⚠️ | ✅ | ❌ Fails constraint 2 |

### Why warranty adjudication wins

1. **The answer is a number and a decision, both checkable.** Covered or not;
   payable ₹X under instrument Y. A human verifies it in ninety seconds. That
   satisfies principle 7, which the softer domains fail.
2. **The precedence rule is real, not contrived.** Every manufacturer has
   bulletins that override base policy for specific serial ranges. You are not
   inventing difficulty — you are reproducing difficulty that exists.
3. **The database is load-bearing, not decorative.** Install date, running
   hours, prior claims and part supersession genuinely cannot live in documents.
   A model that skips the DB *cannot* produce the right number, which makes the
   join gradeable by [the derived-quantity pattern](rubric-patterns.md#second-lever--require-a-derived-quantity)
   you already documented.
4. **The action surface is natural and safe.** Draft an adjudication, request a
   missing record, escalate for goodwill. All idempotent, all reversible,
   nothing that fires an email at a real person.
5. **It has a long tail.** Serial ranges, regional addenda, superseded
   bulletins, data-quality gaps. You can author 70+ genuinely distinct samples
   without repeating yourself — which you will need for RFT.
6. **The failure modes are legible to a business audience.** "It paid out on a
   claim that a bulletin had already excluded" needs no explanation in a
   boardroom.

### When to prefer the runner-up

💭 Pick **deal desk** instead if the showcase audience is predominantly software
/ services rather than industrial, or if a finance-led narrative lands better in
the room. The architecture transfers almost unchanged — policy doc, matrix
spreadsheet, pricebook DB, CRM MCP, deal-room Teams — and every trap in § 7 has a
direct analogue (bulletin → pricing exception memo; serial range → product SKU
family; flat-rate cap → discount floor; goodwill authority → approval tier).

The rest of this document commits to warranty. Say the word and it re-skins.

---

## 5. The scenario — Contoso Industrial, warranty adjudication

All entities are Microsoft's standard fictional names. Nothing is real.

### The cast

| Entity | Role |
| --- | --- |
| **Contoso Industrial Equipment** | The manufacturer. Makes the 4000-series industrial chillers and 2200-series compressors |
| **Fabrikam Service Partners** | Authorised service partner, India region. Standard agreement, no handling uplift |
| **Northwind Field Services** | Authorised service partner, India + APAC. Negotiated **5% handling uplift** on parts |
| **Tailwind Equipment Services** | Service partner, EMEA. Present mainly as a distractor — different addendum, different currency |
| **Litware Manufacturing**, **Woodgrove Foods**, **Relecloud Data Centres**, **Adventure Works Brewing** | End customers. Own the installed assets |
| **The Warranty Operations team** | Contoso staff. The agent's user. Adjudicates claims submitted by partners |

### The job the agent does

> A service partner submits a warranty claim against an installed asset.
> **Is it covered, under which instrument, how much is payable, and what happens
> next?**

One question, four sub-decisions, each independently gradeable:

| Sub-decision | Requires |
| --- | --- |
| **Coverage** — in or out of warranty | Policy + addendum + bulletins, asset install/commissioning date, running hours |
| **Instrument** — *which* document governs | The precedence rule, applied to conflicting instruments |
| **Valuation** — how much is payable | Flat-rate hours, regional labour rate at repair date, part supersession, dealer uplift |
| **Disposition** — what to do about it | Approve / decline / request evidence / escalate for goodwill, with the right authority tier |

### Why this is a good RL target

It maps exactly onto the specification in § 2:

| § 2 requirement | How this scenario supplies it |
| --- | --- |
| 4–6 hop tool trajectory | search policy → search bulletins → `get_asset` → `get_running_hours` → `find_prior_claims` → `lookup_part` → rate-card lookup → action call |
| 3-level precedence rule | Bulletin ▸ regional addendum ▸ global policy, with superseded bulletins void |
| Conditional arithmetic cap | Payable labour = **min**(claimed hours, flat-rate hours) × rate effective **at repair date**, plus parts at the **superseding** part number, plus dealer uplift **if the agreement grants one** |
| Defensible refusal path | Commissioning date absent in the asset registry → state the missing field, name the record required, call `request_missing_evidence`, do not guess |

---

## 6. Source architecture — what lives where, and why

The discipline: **each fact lives in exactly one system, chosen because that is
where it would really live.** No fact is duplicated for convenience — except
where the duplication *is* the trap, and then it is deliberate and documented.

| Fact | System | Format | Why not elsewhere |
| --- | --- | --- | --- |
| Base coverage terms, exclusions, **the precedence rule** | SharePoint | Word | Policy is a controlled document with clause numbers people cite |
| Regional variations | SharePoint | Word | Addenda are separate controlled documents, versioned separately |
| Serial-range coverage extensions, exclusion reversals | SharePoint | Word (many, short) | Bulletins are issued continuously and never folded back into policy |
| Flat-rate labour hours per operation | SharePoint | Excel | It is a rate table maintained by an engineering team |
| Labour rates by region and effective date | SharePoint | Excel | Same, maintained by finance, revised annually |
| Parts list prices and supersession | SharePoint **and** DB | Excel + table | ⚠️ **Deliberate duplication — see trap 7** |
| Partner commercial terms (uplift, SLA) | SharePoint | Word | Contracts are documents |
| Quarterly warranty performance and policy summaries | SharePoint | **PowerPoint** | ⚠️ **Deliberate staleness — see trap 6** |
| Per-claim inspection evidence | SharePoint | Word | Field reports are documents attached to claims |
| Asset registry: serial → model, dates, region, owner | **Database** | SQL | Transactional master data. Cannot sensibly be a document |
| Running hours telemetry | **Database** | SQL | Time series. Cannot be a document |
| Service history and prior claims | **Database** | SQL | Transactional ledger |
| Partner master, uplift percentage | **Database** | SQL | ⚠️ Duplicated against the agreement doc — see trap 8 |
| Goodwill authority thresholds | **Database** | SQL | Operational config that changes without reissuing policy |
| Bulletin applicability index | **Database** | SQL | ⚠️ **Deliberately stale against the bulletin documents — trap 1** |
| Field escalations, partner chatter, verbal approvals | **Teams** | Messages | This is where humans actually negotiate |
| Policy change announcements | **Teams** | Messages | Announcement ≠ the controlled document |

### The four-source discipline, and how it is enforced

📄 Your [rubric-patterns.md](rubric-patterns.md) already establishes the
technique: you cannot grade a join, so you grade **provenance per claim type**
and **a derived quantity only a correct join can produce**. This scenario is
built so that mapping is total:

| Claim type in the answer | Must be attributed to |
| --- | --- |
| Coverage term, exclusion, precedence | The policy, addendum or bulletin, **by reference code and clause** |
| Asset date or running-hours figure | The asset registry / telemetry, **naming the as-of date** |
| Prior repair or duplicate claim | Service history, **naming the claim or job id** |
| Any monetary figure | The rate card or parts list **for the applicable region and effective date**, and the part number actually fitted |
| Partner commercial term | The partner agreement **by reference**, cross-checked against the partner master |
| Anything a person said | The Teams channel, **explicitly labelled as not constituting authority** |
| Anything else | **Nothing.** Unsourced content is a rubric failure |

That last row is the closure axis, and it is what makes invention gradeable.

### Retrieval reachability — the thing to prove first

⚠️ Principle 2 is non-negotiable and guide 01 is the evidence. Before a single
rubric is written, run one `chat` probe per source type and confirm each returns
real content with real links:

| Probe | Proves |
| --- | --- |
| "What does the global warranty policy say about precedence between instruments?" | Word retrieval from `01-Policy/` |
| "Summarise bulletin TSB-C-0051." | Retrieval across many small documents — the hardest case |
| "What is the FY26 India labour rate?" | Excel retrieval, which behaves differently from Word |
| "What did the field team say about 4000-series bearing failures?" | Teams capability |
| "Look up asset CIE-4000-CH-01642." | MCP server reachable and authenticated |
| "What was the headline warranty cost in the Q2 review?" | PowerPoint retrieval |

📄 `environments get` and `environments export` under-report and cannot audit
scope. Only a probe proves it.

---

## 7. The trap surface

Twelve designed difficulties. Each is independent, each maps to one rubric, each
gets dedicated samples. The **Bites at** column is the stage where it starts
costing score — which is how the climb is engineered.

| # | Trap | Mechanism | Sources required | Rubric that catches it | Bites at |
| --- | --- | --- | --- | --- | --- |
| 1 | **Stale bulletin index** | The DB applicability index says a serial is out of range; the bulletin document says it is in range. Policy § 1.4: *the bulletin document governs; the index is informational* | Bulletin (Word) + DB index | Precedence discipline | Stage 2 |
| 2 | **Three-level precedence** | Bulletin ▸ regional addendum ▸ global policy. The addendum is *shorter* than base, so grabbing the most generous or the first hit both fail | Policy + addendum + bulletin | Precedence discipline | Stage 2 |
| 3 | **Dual-limit expiry** | 24 months **or** 6,000 running hours, whichever first. Months from DB commissioning date, hours from DB telemetry | DB × 2 | Coverage determination | Stage 1 |
| 4 | **Serial-range boundary** | Bulletin covers `01200`–`01850`. Samples sit at `01199`, `01200`, `01850`, `01851` | Bulletin text | Coverage determination | Stage 2 |
| 5 | **Superseded bulletin** | TSB-P-0107 is superseded by TSB-P-0112. Both retrievable. Only 0112 has effect | Two bulletins | Precedence discipline | Stage 2 |
| 6 | **Stale deck** | The Q2 review PowerPoint states *"standard coverage: 24 months"* — accurate for base policy, wrong once a bulletin applies. A confident model quotes the deck | PowerPoint | Evidence grounding | Stage 2 |
| 7 | **Part supersession** | Claim names P-44120; service history shows P-44120-A was fitted; prices differ. Excel carries list price, DB carries supersession | Excel + DB | Valuation accuracy | Stage 2 |
| 8 | **Uplift asymmetry** | Northwind's agreement grants 5% handling uplift; Fabrikam's does not. Applying it uniformly is wrong in both directions | Agreement (Word) + DB partner master | Valuation accuracy | Stage 2 |
| 9 | **Rate effective-date** | FY26 rate effective 1 Apr 2026. Repairs either side of it. The rate is chosen by **repair date**, not submission date or today | Excel (effective-dated rows) | Valuation accuracy | Stage 3 |
| 10 | **Flat-rate cap** | Partner claims 7.0 h; flat rate allows 5.5 h. Payable is the cap, and the difference must be stated, not silently dropped | Excel + claim | Valuation accuracy | Stage 2 |
| 11 | **Verbal authority** | A regional manager writes *"go ahead and cover it, I'll sort the paperwork"* in Teams. Policy § 7 requires written authority recorded in the claim system | Teams + policy + DB authority table | Authority and action | Stage 3 |
| 12 | **Missing record → abstain** | Commissioning date is NULL for some serials. Correct behaviour names the field, names the record needed, calls `request_missing_evidence`, and does **not** fall back to install date | DB (null) + policy § 2.3 | Evidence closure | Stage 3 |

### Why twelve, and why staged

💭 The staging is deliberate. Traps that bite at **Stage 1** are plumbing — they
disappear once tools are registered, and they are what makes the naive baseline
low *for a diagnosable reason* rather than low because retrieval is broken.
Traps that bite at **Stage 2** are the inner-loop story: they are fixed by
writing the right rubric, not by touching the model. Traps that bite at
**Stage 3** are the ones that **survive good rubrics on a small model** — the
reserved headroom. Trap 9, 11 and 12 in particular are conditional, low-frequency
and easy to get right once and wrong the next time, which is precisely the
consistency profile RFT improves.

⚠️ **Do not add a thirteenth trap that makes ground truth ambiguous.** A unit
mismatch between two telemetry tables was considered and rejected: it produces
defensible disagreement about the right answer, which corrupts both the rubric
and the training signal. Difficulty is welcome; ambiguity is not.

---

## 8. A worked example, end to end

This exists to prove principle 7 — that a human can verify an answer quickly.
If this example cannot be checked by hand, the design fails.

**Claim `C-2026-04187`** — Fabrikam Service Partners, India.

| Input | Value | Source |
| --- | --- | --- |
| Serial | `CIE-4000-CH-01642` | Claim |
| Operation | `HYD-PUMP-RR` (hydraulic pump remove & replace) | Claim |
| Repair date | 18 Jun 2026 | Claim |
| Labour claimed | 7.0 h | Claim |
| Part claimed | P-44120 | Claim |
| Model | 4000-series chiller | DB `Assets` |
| Commissioning date | 04 Apr 2024 | DB `Assets` |
| Running hours at repair | 4,120 | DB `AssetTelemetry` |
| Part actually fitted | **P-44120-A** | DB `ServiceHistory` |
| Partner uplift | **0%** | DB `Dealers` + Fabrikam agreement |

**Step 1 — coverage under base policy.** 24 months from commissioning →
expires 04 Apr 2026. Repair is 18 Jun 2026. Hours limit 6,000, actual 4,120.
Months exceeded → **not covered under base policy**.

**Step 2 — regional addendum.** India addendum v2.1 sets 18 months →
expires 04 Oct 2025 → **also not covered**. A model that stops here declines a
valid claim.

**Step 3 — bulletins.** TSB-C-0051, effective 15 Jan 2026, extends compressor
and hydraulic-circuit coverage to **36 months or 8,000 hours** for serials
`CIE-4000-CH-01200` through `01850`. `01642` is in range → expires 04 Apr 2027
and 8,000 hours → **covered**.

**Step 4 — the conflict.** DB `TsbApplicability` records `serial_to = 01500`
for TSB-C-0051 — stale. Policy § 1.4 states the bulletin document governs and
the index is informational. Correct answer applies the bulletin **and says the
index disagrees.**

**Step 5 — valuation.**

| Component | Computation | Amount |
| --- | --- | --- |
| Labour | min(7.0, **5.5** flat rate) × **₹1,450**/h (India, effective 1 Apr 2026) | ₹7,975 |
| Parts | P-44120-**A** list price (supersedes P-44120) | ₹191,200 |
| Uplift | Fabrikam: none | ₹0 |
| **Payable** | | **₹199,175** |

Variance to state: 1.5 h of claimed labour above flat rate, not payable.

**Step 6 — Teams.** The field channel carries a regional manager writing *"just
cover the extra hours, I'll sort the paperwork."* Correct handling: note it,
state it is not valid authority under policy § 7, and observe that no goodwill is
needed because the claim is covered outright.

**Step 7 — action.** `create_claim_adjudication(claim_id="C-2026-04187",
decision="approve", payable=199175, currency="INR",
instrument_refs=["TSB-C-0051", "POL-WAR-4.2 §1.4"], notes=...)`.

### What this example exercises

Eight of the twelve traps (1, 2, 3, 4, 7, 8, 10, 11), six tool calls, two
document types, four database tables, one Teams thread and one action — in a
single question whose correct answer is a five-digit number you can check with a
calculator.

💭 That is the test of a well-designed sample: **maximum trap density, minimum
verification effort.**

---

## 9. Skills and rubrics

### 9.1 Skill decomposition

📄 *"A skill that does one job well is easier to evaluate, easier to fix, and
easier to trust."* Three skills, built in this order:

| Skill | Job | Why it is separate |
| --- | --- | --- |
| `warranty-coverage-check` | Is this asset covered on this date, under which instrument? | Pure precedence + dates. No money. Isolates traps 1–6 so they can be measured without valuation noise |
| `claim-valuation` | Given a covered claim, what is payable? | Pure arithmetic + provenance. Isolates traps 7–10 |
| `claim-adjudication-brief` | The full decision, disposition and action | **The showcase skill.** Composes both, adds traps 11–12 and the action surface |

💭 **The decomposition is itself part of the demo.** Stage 0 deliberately ships
*one* broad skill that does all three, which is how most people build. Splitting
it at Stage 2 is one of the measurable inner-loop wins, and it makes the
attribution argument for you: after the split you can point at
`warranty-coverage-check` scoring 0.91 while `claim-valuation` scores 0.64 and
know exactly where to work.

⚠️ Multi-skill worlds have two consequences you already documented: evaluation
defaults to whole-workspace, and `tune start` snapshots every enabled skill.
Scope evaluations with `--skill-id`, and disable what you are not tuning.

### 9.2 Rubrics for the flagship skill — written before the skill exists

Six rubrics for `claim-adjudication-brief`. Draft, for review, not final.

```text
### Coverage determination
Description: The coverage conclusion follows from the asset's own dates and limits.
- States whether the claim is covered, declined, or cannot be determined
- Names the expiry basis actually used, in both months and running hours
- Compares the repair date and the running hours at repair against those limits
- Where one limit is exceeded and the other is not, says which one governs

### Precedence discipline
Description: The governing instrument is identified and justified against the alternatives.
- Names exactly one governing instrument, by reference code
- States why it governs over the other instruments that mention this asset
- Treats a superseded bulletin as having no effect, and says so where one was found
- Where the service system index and a bulletin document disagree, follows the document and reports the disagreement

### Evidence grounding
Description: Every factual claim is traceable to the source that owns it.
- Attributes every coverage term or exclusion to a policy, addendum or bulletin reference and clause
- Attributes every date and running-hours figure to the asset registry or telemetry, naming the as-of date
- Attributes every monetary figure to the rate card or parts list, naming the region and the effective date
- Introduces no figure, date, part number or reference that is absent from the sources

### Valuation accuracy
Description: The payable amount is derived, shown, and internally consistent.
- States payable labour as the lesser of claimed hours and the flat-rate allowance, and names both
- Applies the labour rate in force on the repair date, and names that rate
- Prices the part actually fitted, naming the part number and any supersession
- Applies the partner handling uplift only where the partner agreement grants one
- States the total payable, and states any claimed amount not payable as an explicit variance

### Authority and action
Description: The disposition is one the requester is entitled to take.
- Names the disposition: approve, decline, request evidence, or escalate
- Where escalation is required, names the approving role and the threshold that triggered it
- Treats an approval given in conversation as not constituting authority, where one is present
- Names the action to be taken and the identifiers it needs

### Evidence closure
Description: Gaps and silences are reported rather than filled.
- Names any required record that is missing, and the field that is absent
- States explicitly where a consulted source contained nothing relevant
- Does not substitute a different field for a missing one
- Where the evidence is sufficient, states that the required records were present
```

### 9.3 Satisfiability audit

⚠️ Principle 5, applied. This is the check that guide 01's rubrics failed and
which matters ten times more here, because these rubrics become the **reward
function**.

| Path | Coverage | Precedence | Grounding | Valuation | Authority | Closure |
| --- | --- | --- | --- | --- | --- | --- |
| Covered, simple | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ final bullet |
| Covered under a bulletin, index disagrees | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Declined, out of warranty | ✅ | ✅ | ✅ | ⏭️ skip — nothing payable | ✅ | ✅ |
| Declined on exclusion | ✅ | ✅ | ✅ | ⏭️ skip | ✅ | ✅ |
| **Cannot determine — record missing** | ✅ "cannot be determined" branch | ⏭️ skip | ✅ | ⏭️ skip | ✅ "request evidence" | ✅ **primary path** |
| **Serial not in the registry at all** | ✅ | ⏭️ skip | ✅ | ⏭️ skip | ✅ | ✅ |
| Covered, goodwill escalation needed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Every rubric is satisfiable or skippable on all seven paths. The two bolded rows
are the ones guide 01's design would have scored 0.00 for being right.

💭 Note how the fix is structural, not cosmetic: *Coverage determination* offers
three outcomes rather than two, and *Evidence closure* has a bullet that is
satisfiable when nothing is missing. Both were written that way on purpose.

### 9.4 The grading limitation you must design around

This is the most important caveat in the document, and it constrains sample
design.

> **Rubrics attach to the skill, not the sample.** There is no per-question
> rubric and no reference answer in the grading path. So **no rubric can say
> "the payable amount is ₹199,175".**

Consequences:

| Consequence | Mitigation |
| --- | --- |
| A model can produce a **wrong number with a right structure** and score well | *Valuation accuracy* forces all three inputs to be **shown**. A grader that can see `min(7.0, 5.5) × ₹1,320 = ₹7,260` alongside a cited rate card saying ₹1,450 can mark it down. Make the inputs visible and the error becomes visible with them |
| Coverage can be right by luck | *Precedence discipline* requires the **losing** instruments to be named and dismissed. Luck does not produce that text |
| Nothing detects a trap that no rubric mentions | Trap → rubric mapping in § 7 is a **completeness contract**. Every trap has a named rubric or it is not in the world |
| 🔬 The grader may not verify arithmetic at all | **Verify this before building.** Run one probe with a deliberately wrong total and read `RubricResults[].Reasoning`. If the grader does not catch it, valuation must be graded on *derivation shown* and numeric correctness checked out-of-band by script |

🔬 **Open, and worth testing early:** does the sample schema accept a reference
or expected answer alongside `Prompt`? [CLI-REFERENCE](CLI-REFERENCE.md#samples)
records *"at least a `Prompt` field"*, which implies other fields exist. If a
reference answer is supported, grading gets materially stronger and several
mitigations above become unnecessary. Check `samples create --help` before
authoring seventy samples.

---

## 10. Samples

### Volume

| Type | Count | Driven by |
| --- | --- | --- |
| Evaluation | **30** | Enough for per-trap attribution (2–3 per trap) without an eight-hour run |
| Training | **45** | `tune start` requires ≥ 11; 45 gives RFT room to generalise rather than memorise |
| **Total** | **75** | |

⚠️ 45 training prompts is a floor, not a target. If tuning underdelivers, the
first thing to add is more training samples, not more epochs.

### Stratification

Evaluation set, by trap and by outcome — so the score breakdown is attributable:

| Slice | Samples | Purpose |
| --- | --- | --- |
| Straightforward covered | 3 | Sanity. Should be ~1.00 at every stage after Stage 1 |
| Straightforward declined | 2 | The decline path must not be penalised |
| Bulletin precedence (traps 1, 2, 5) | 5 | The core inner-loop win |
| Serial boundary (trap 4) | 4 | `01199`, `01200`, `01850`, `01851` |
| Dual-limit expiry (trap 3) | 3 | One limited by months, one by hours, one close to both |
| Valuation (traps 7, 8, 9, 10) | 6 | The derived-quantity story |
| Stale deck (trap 6) | 2 | Only fails if the model prefers the deck |
| Authority (trap 11) | 2 | Teams promise present, and a genuine escalation |
| Abstention (trap 12) | 3 | Missing commissioning date, unknown serial, no telemetry |

Training set mirrors the distribution at 1.5×, with **no prompt reused** between
the two sets.

### Tiered eval sets — an operational necessity

⚠️ Six samples took **~55 minutes** on your tenant. Thirty will take roughly
**four and a half hours**. At five hill-climb iterations that is over twenty
hours of wall clock. Do not run the full set on every change.

| Tier | Samples | Run when | Wall clock |
| --- | --- | --- | --- |
| **Smoke** | 3 | After any skill or rubric edit | ~25 min |
| **Dev** | 10 — one per trap family | Mid-stage, to check direction | ~1.5 h |
| **Full** | 30 | **Only at stage boundaries**, and for the record | ~4.5 h |

Scope with `--sample-id` (repeatable) rather than maintaining three sample sets.

⚠️ And the trap that will cost you a day if you forget it: **samples snapshot
the skill's rubrics at upload time.** Every rubric edit needs a re-upload, and
re-uploading **adds copies rather than replacing**. Delete by skill first.

---

## 11. The climb, stage by stage

All scores are **predictions**. The point of the design is that each stage moves
a *specific* rubric for a *specific* reason.

| Stage | What changes | Predicted | What it teaches | Evidence to capture |
| --- | --- | --- | --- | --- |
| **0 — Naive** | One broad skill. Rubrics from `generate-rubrics`. Prompt restates them. MCP server registered but **disabled**. 8 samples | **0.45–0.55** | This is how most people build. The number is low and the breakdown says why | Job id, per-rubric breakdown, two execution traces showing invented DB facts |
| **1 — Plumbing** | `tools enable` the MCP server. Verify every source with a probe | **0.62–0.70** | 📄 *Fix retrieval before you tune.* Roughly a third of the total gain, from zero model work | Before/after on the same samples; tool-call traces showing real DB reads |
| **2 — Inner loop** | Split into three skills. **Rubrics authored first.** Prompts thinned to role and goal. Trap → rubric contract closed | **0.76–0.84** | The core lesson: the standard belongs in rubrics, not the prompt | Per-skill scores; the prompt diff; the rubric set |
| **3 — Honest samples** | Add the full 30-sample eval set including boundary, authority and abstention slices | **0.72–0.80** — *may fall* | ⚠️ **The most valuable stage.** A harder eval set reveals difficulty that the easy set hid. The dip is the finding | The dip, and the per-slice breakdown showing *where* |
| **4 — RFT** | Tune a small model on the workspace snapshot | small model **~0.55 → ~0.80** | A small model learns procedure it could not follow from a prompt | Two job ids, `evaluate compare`, token and latency deltas |

### Why stage 3 must be allowed to lower the score

💭 This is counter-intuitive and worth defending, because the instinct will be to
skip it.

If you build the easy eval set, climb to 0.84, and tune, you are tuning against a
measurement that overstates how good the world is. 📄 *"Fine-tuning amplifies what
is there; it does not repair it."* An eval set that avoids the hard cases bakes in
a model that is good at easy cases.

**Stage 3 is where the headroom for stage 4 is created** — not by making the
world worse, but by measuring it honestly. A drop from 0.84 to 0.76 on a harder
set, with the breakdown showing the loss concentrated in abstention and
effective-date handling, is the single most credible slide in the deck. It says:
*we know exactly what our agent is bad at, and here is the number.*

### Staging inside one world

⚠️ Capability URLs are frozen at `init`, so the SharePoint and Teams scope must
be right on day one. Everything else can be staged **within** one environment:

| Mechanism | Used for |
| --- | --- |
| `tools disable` / `enable` | Staging the MCP server in and out between stage 0 and 1 — reversible, no re-provisioning |
| `skills disable` | Keeping the stage-0 broad skill for comparison while excluding it from evaluation and tuning |
| `versions` | Rolling back a skill version if a stage regresses |
| `--skill-id` / `--sample-id` on `evaluate start` | Scoping runs so stages stay comparable |
| Retained job ids | Every stage's evaluation is retained and re-readable. `evaluate compare` reads them side by side |

Recommend **two environments regardless**: `wce-dev` as a throwaway for scope and
capability experiments, `wce-main` as the one the climb is recorded in. Provision
dev first and probe it before committing main's URLs.

---

## 12. The RFT stage, and the comparison problem

### What gets tuned

`tune start` snapshots the **whole workspace** — every enabled skill, every tool,
both sample types. Before tuning:

1. `skills disable` the stage-0 broad skill.
2. Delete duplicate samples from re-uploads (`samples list`, check for repeats).
3. Confirm ≥ 11 training-usable prompts. 45 is the design target.
4. Re-read the rubrics **as a reward function**, not as a measurement. Run the
   § 9.3 satisfiability audit again. A rubric that penalises a correct refusal
   here does not merely mis-score — it trains the model to invent.

### ⚠️ The comparison problem, stated plainly

Your own notes record that `evaluate start` validates against `TrainingModels`
and `tune start` against `FTBaseModels`, and that 📄 upstream concludes *"you
cannot baseline the model you are going to tune."*

That constraint, if it holds, **breaks the clean version of this demo**. So it
must be settled before Stage 4, not during it. Three narratives, in order of
preference:

| # | Narrative | Requires | Strength |
| --- | --- | --- | --- |
| **A** | *"Same model, before and after tuning: 0.55 → 0.80."* | 🔬 `dev-ct-gpt-54-mini-mp` and `gpt-54-mini` resolving to the same weights — the open question already in 02-next-fine-tuning | ✅ Cleanest. **Test this first** |
| **B** | *"Tuned mini reaches 0.80 against the frontier model's 0.90, at a fraction of cost and latency."* | The tuned model appearing in `TrainingModels` so it can be scored on the same samples. 🔬 Also unverified | ✅ Still a procurement-grade claim. **The safe default** |
| **C** | *"Tuning moved the workspace from X to Y on a smaller base."* | Nothing beyond the tune completing | ⚠️ Weakest. Acceptable only with the disjoint-list caveat stated out loud |

🔬 **Pre-flight, before any content is curated:** run `models list -o json`, check
current membership of both lists, and — if possible — run a cheap identical probe
against `dev-ct-gpt-54-mini-mp` and confirm whether a completed tune appears in
`TrainingModels`. If the answer to both is no, design the deck around narrative B
from the start rather than discovering it at the end.

⚠️ One more from your notes: **training can take days** on fungible capacity, and
`status` reporting training complete does not mean `readyForEvaluation`. Do not
schedule the showcase against an unstarted tune.

### What "closing the headroom" should look like

| Claim | Honest? |
| --- | --- |
| "Tuning took a mini model from 0.55 to 0.80 on this task" | ✅ If narrative A holds |
| "The tuned mini closes 70% of the gap to the frontier model at a fraction of the cost" | ✅ Under B, with both numbers shown |
| "Tuning improved our agent from 0.48 to 0.80" | ❌ **No.** That conflates the inner loop with training. Most of that was rubric work |
| "Fine-tuning made GPT-5.4 better at warranty adjudication" | ❌ **No.** You did not tune that model |

---

## 13. Content manifest — what gets curated next

This is the build list. Counts are deliberate — enough noise that retrieval is
real work, not so much that curation becomes the project.

### SharePoint — site `Contoso Field Service`, library `Warranty Operations`

| Folder | Files | Format | Carries |
| --- | --- | --- | --- |
| `01-Policy/` | Global Warranty Policy v4.2 | Word | Base terms, exclusions § 5, **precedence rule § 1.4**, authority § 7, missing-record rule § 2.3 |
| | Regional Addendum — India v2.1 | Word | Trap 2. 18-month term, monsoon clause |
| | Regional Addendum — EMEA v1.3 | Word | Distractor. Different currency, different term |
| | Goodwill & Authority Matrix v3 | Word | Tier table referenced by trap 11 |
| `02-Bulletins/` | TSB-C-0043 | Word | Reverses the contamination exclusion for a filter defect |
| | TSB-C-0051 | Word | **Trap 1 + 4.** Serial range `01200`–`01850`, 36 months / 8,000 h |
| | TSB-P-0107 | Word | **Trap 5.** Superseded |
| | TSB-P-0112 | Word | Supersedes 0107 |
| | 8 further bulletins | Word | Noise for other models and families. Retrieval precision |
| `03-RateCards/` | `Flat-Rate-Labour-FY26.xlsx` | Excel | Operation code → allowed hours. Trap 10 |
| | `Labour-Rates-By-Region-FY26.xlsx` | Excel | Region, currency, rate, **effective from/to**. Trap 9 |
| | `Parts-Price-List-FY26.xlsx` | Excel | Part, list price, region. Trap 7 |
| `04-PartnerAgreements/` | Fabrikam, Northwind, Tailwind | Word ×3 | Trap 8. Northwind's 5% uplift |
| `05-Reviews/` | `FY26-Q2-Warranty-Review.pptx` | **PowerPoint** | **Trap 6.** Stale "24 months standard" summary, cost trend charts |
| | `FY26-Q3-Warranty-Review.pptx` | PowerPoint | Current. Bulletin impact slide |
| `06-ClaimEvidence/` | ~12 inspection reports | Word | Oil analysis, photo logs, failure narratives. Feeds exclusion decisions |
| `07-Reference/` | Service manual extract, partner FAQ | Word ×2 | Plausible distractors. Retrieval precision |

**~35 documents.** Enough that search has to work.

### Teams — team `Contoso Field Service`

| Channel | Threads | Carries |
| --- | --- | --- |
| `Field-Escalations` | ~25 messages across 6 threads | **Trap 11** — the verbal goodwill promise. Plus partner escalations and 4000-series failure chatter |
| `Warranty-Policy-Updates` | ~10 messages | Bulletin announcements, rate-card effective dates. Announcement ≠ controlled document |
| `Partner-Fabrikam` | ~12 messages | Noise and one legitimate evidence thread |

### Database

Azure SQL Database, reached only through the MCP server.

| Table | Rows | Notes |
| --- | --- | --- |
| `Assets` | 120 | serial, model, family, dealer_id, customer_site, install_date, **commissioning_date (3 NULL — trap 12)**, region |
| `AssetTelemetry` | ~1,400 | serial, as_of_date, running_hours. Monthly per asset |
| `ServiceHistory` | ~200 | job_id, serial, date, operation_code, part_fitted, labour_hours, claim_id |
| `Claims` | 75 | One per sample, plus prior-claim history. Status, repair_date, claimed values |
| `Parts` | 60 | part_no, description, **supersedes (trap 7)**, family |
| `Dealers` | 4 | **uplift_pct (trap 8)**, region, agreement_ref |
| `GoodwillAuthority` | 4 | tier, max_amount, approver_role, region |
| `TsbApplicability` | 12 | **Deliberately stale for TSB-C-0051 — trap 1** |

### MCP server — `contoso-service-mcp`

Registered with `tools create --auth-scheme AzureAD --aud <app-id-uri>`.

**Read tools**

| Tool | Returns |
| --- | --- |
| `get_asset(serial)` | Registry record, or a typed not-found |
| `get_running_hours(serial, as_of)` | Nearest telemetry reading and its date |
| `get_service_history(serial, months)` | Jobs, parts fitted, labour |
| `find_prior_claims(serial, component)` | Prior claims — repair-warranty and duplicate detection |
| `get_claim(claim_id)` | The submitted claim |
| `get_dealer(dealer_id)` | Partner master including uplift |
| `lookup_part(part_no)` | Supersession chain |
| `get_tsb_index(model)` | ⚠️ The **stale** index. Its own description must say it is informational |
| `get_goodwill_authority(amount, region)` | Tier and approving role |

**Action tools** — all draft-only, all idempotent

| Tool | Effect |
| --- | --- |
| `create_claim_adjudication(...)` | Writes a **draft** adjudication, returns a draft id |
| `request_missing_evidence(claim_id, field, reason)` | Records an evidence request |
| `escalate_goodwill(claim_id, amount, approver_role)` | Records an escalation |

💭 Two deliberate choices. First, `get_tsb_index` **must** describe itself as
informational in its own tool description — the trap is that the model believes a
structured source over a document, and the honest version of that trap tells the
model the truth and sees whether it acts on it. Second, every action writes a
draft. Nothing in this world can send, pay, or notify.

📄 `tools mocktools` lets skills and rubrics be built against these contracts
**before the server exists** — which removes the hosting dependency from the
critical path.

### Ground truth

`GROUND-TRUTH.md`, one row per sample: expected coverage decision, governing
instrument, payable amount, expected disposition, and the traps exercised. This
is the human audit trail principle 7 requires, and the input to any out-of-band
numeric check script.

---

## 14. Operational budget

Rough, and worth agreeing before starting.

| Phase | Effort | Notes |
| --- | --- | --- |
| Content curation (docs, sheets, deck, Teams, DB seed) | **2–3 days** | Scriptable. `python-docx` / `openpyxl` / `python-pptx` are already pinned in `requirements-seed.txt` |
| DB provisioning + seeding | 0.5 day | |
| MCP server build + host + Entra app | **1–2 days** | ⚠️ The critical path. May need tenant admin |
| World provisioning + retrieval probes | 0.5 day | Plus SharePoint indexing lag — allow overnight |
| Rubric authoring + skills | 1 day | Rubrics first |
| Sample authoring (75) + ground truth | **1.5 days** | The most tedious part; do not underestimate |
| Stages 0–3, including eval wall clock | **3–4 days** | Dominated by evaluation runtime, not work |
| Stage 4 tuning | **days, largely waiting** | Fungible capacity |

⚠️ Evaluation wall clock is the hidden cost: ~9 minutes per sample, and a full
30-sample run is ~4.5 hours. The tiering in § 10 exists for this reason.

---

## 15. Risks and pre-flight checks

### Check these before curating anything

| # | Check | Why it blocks |
| --- | --- | --- |
| 1 | Can you host an internet-reachable, Entra-authenticated endpoint the substrate can call? | No MCP server ⇒ no database story ⇒ the scenario loses half its point. Confirm before building content |
| 2 | Does `samples` accept a reference answer field? | Changes how much rubric machinery § 9.4 needs |
| 3 | Do `dev-ct-gpt-54-mini-mp` and `gpt-54-mini` share weights? | Decides narrative A vs B in § 12 |
| 4 | Does a completed tune appear in `TrainingModels`? | If not, narrative B is also at risk |
| 5 | Does the grader verify arithmetic, or only structure? | Decides whether valuation needs an out-of-band check |
| 6 | Is a new SharePoint site + Teams team provisionable in this tenant? | Guide 01's most expensive lesson was scope. Do not reuse a personal OneDrive |

### Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Capability URLs frozen at `init` | A scope mistake costs the world and every skill id in it | Provision `wce-dev` first, probe it, then commit `wce-main` |
| SharePoint indexing lag | Probes fail for hours after upload and look like scope failures | Load content, wait overnight, probe before concluding anything |
| MCP hosting needs admin consent | Blocks the critical path | Start the Entra app registration on day one; build skills against `mocktools` meanwhile |
| Traps make ground truth ambiguous | Corrupts both grading and training signal | The § 7 exclusion rule. Every sample must have one defensible answer |
| Rubrics penalise correct abstention | Trains the model to invent | § 9.3 audit, re-run before `tune start` |
| Samples duplicated by re-upload | Inflates counts, skews tuning | `samples delete-by-skill` before every re-upload |
| Content curation expands without limit | The project becomes document-writing | Manifest in § 13 is a contract. Extra documents need a trap to justify them |
| Model lists shift under you | A stage becomes non-comparable | `models list` before every run; record the model id with every job id |

---

## 16. Decisions taken, and what is still open

### Locked — 22 September 2026

| # | Decision | Consequence |
| --- | --- | --- |
| 1 | **Domain: warranty adjudication.** Contoso Industrial, as drafted | § 13's manifest is the build list. Deal desk is shelved, not discarded — the architecture transfers if the audience changes |
| 2 | **Full Azure + Entra path.** Internet-reachable MCP endpoint over Azure SQL Database | The real MCP server is in scope. `tools mocktools` is still used to keep hosting off the critical path while skills and rubrics are authored |
| 3 | **India / INR primary**, EMEA addendum as distractor | Trap 9's effective dates are INR: ₹1,320/h FY25, ₹1,450/h from 1 Apr 2026. Tailwind's EMEA agreement supplies the currency distractor |

### Still open

| # | Question | Why it matters |
| --- | --- | --- |
| 4 | Is the showcase audience **technical or business**? | Decides whether the artefact is a guide, a deck, or both — and how much of § 12's caveat surfaces |
| 5 | Is there an existing SharePoint site and Teams team, or is one being created? | Determines when content can be loaded. Does not block curation |

---

## Related

| Document | Covers |
| --- | --- |
| 01-contract-renewal.md | The reference world, and why it saturated |
| 02-next-fine-tuning.md | The model-list constraint this design has to work around |
| [rubric-design.md](rubric-design.md) | Why rubrics come before skills |
| [rubric-patterns.md](rubric-patterns.md) | The provenance and derived-quantity techniques § 9.2 applies |
| [rubric-defects.md](rubric-defects.md) | The three defects § 3's principles exist to prevent |
| [../CLI-REFERENCE.md](CLI-REFERENCE.md) | Command surface and the 20 traps § 14 budgets around |
