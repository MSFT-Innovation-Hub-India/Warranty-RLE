# Guide 04 — The world, told as a story

**Read this first** if you want to understand what was built and why, before
looking at any of it.

This explains the scenario the way you would explain it to a colleague: as a
claim landing on someone's desk and being worked through to a decision. Every
claim reference, serial number and amount below is real — taken from the
generated corpus, computed by the same engine that produces the answer key.

- [Guide 03](03-scenario-design.md) — *why* the world is shaped this way
- [scenario/README](../README.md) — *how* it is built and regenerated
- [scenario/out/GROUND-TRUTH.md](../out/GROUND-TRUTH.md) — every expected answer, with full working

---

## 1. The setting

**Contoso Industrial Equipment** makes two product lines: 4000-series chillers
and 2200-series air compressors. It does not service them itself. Authorised
partners do that, then invoice Contoso for the work done under warranty.

**Anjali Rao's team** in Warranty Operations decides each invoice:

> *Is it covered? Under which instrument? How much do we pay? What happens next?*

That is the job. The agent does it.

### The four systems

The work is split across four places because that is genuinely where each piece
of it lives in a real company.

| System | Holds | Why it lives there |
| --- | --- | --- |
| **SharePoint** | Policy, 3 regional addenda, 12 service bulletins, partner contracts, rate cards, inspection reports, review decks | Controlled documents. People cite them by clause number |
| **Database** | Asset registry, 3,000 running-hours readings, service history, submitted claims, partner master, parts, authority tiers | Transactional and time-series data. It cannot be a Word file |
| **Teams** | Field escalations, policy announcements, partner threads | Where people actually negotiate, and where informal decisions get made |
| **MCP server** | The agent's only route into the database, plus three actions it can take | The database is not searchable content. It has to be *queried* |

**No single system can answer the question.** That is deliberate, and everything
else follows from it.

---

## 2. One claim, end to end

**Claim C-2026-04148.** Northwind Field Services replaced a hydraulic pump on a
chiller. Submitted 24 June 2026.

The adjudicator types:

> *"Northwind Field Services have submitted C-2026-04148. Is it covered, and
> what do we pay?"*

Nine steps follow. Watch which system each one touches.

### Step 1 — Read the claim
**MCP → database**

```text
serial        CIE-4000-CH-01440
repair date   18 June 2026
operation     HYD-PUMP-RR
labour        8.0 hours claimed
part          P-44120
```

Note what this does *not* contain: whether it is covered, or what it is worth.
The claim is the partner's request, not the answer.

### Step 2 — Find the machine
**MCP → database**

```text
family        4000-CH
region        India
partner       D-IN-02  (Northwind Field Services)
commissioned  1 October 2024
```

**Commissioning date is the one that matters.** Coverage runs from commissioning,
not installation. This field appears nowhere in any document.

### Step 3 — How hard has it worked?
**MCP → database**

```text
3,000 running hours as at the repair date
```

Coverage has **two** limits — months *and* hours, whichever comes first. This is
half the test, and only the database has it.

### Step 4 — What does the policy say?
**SharePoint → Word**

The agent searches the library and finds three documents that all claim to apply:

| Document | Says | At 20 months |
| --- | --- | --- |
| `POL-WAR-4.2` Global Warranty Policy | 24 months or 6,000 hours | Covered |
| `ADD-IN-2.1` Regional Addendum — India | **18 months** or 5,000 hours | **Not covered** |
| `TSB-C-0051` Service Bulletin | 36 months or 8,000 hours, serials 01200–01850 | Covered |

Three documents, three different answers.

The India addendum is **worse** than the global policy. That surprises people,
and it is deliberately there — it catches an agent that assumes a local rule is
always more generous than the global one.

### Step 5 — Which one wins?
**SharePoint → Word, clause 1.4**

> *"Where two or more instruments address the same asset, the order of precedence
> is: (a) a Technical Service Bulletin that names the serial range of the asset;
> (b) the Regional Addendum for the region in which the asset is installed;
> (c) this policy."*

Serial 01440 is inside 01200–01850, so **the bulletin governs**. 36 months,
expiring 1 October 2027, limit 8,000 hours against 3,000 actual.

**Covered.** And notice what a good answer must say here — not just "covered",
but *which* instrument, and *why it beat the other two*.

### Step 6 — What was actually fitted?
**MCP → database**

```text
job J-00043   18 June 2026   HYD-PUMP-RR   part fitted: P-44120-A
```

The claim said `P-44120`. The service record says `P-44120-A` went in. Policy
clause 4.2: price the part *actually fitted*. They differ by ₹4,800.

**Only the database knows this.** The claim is wrong in good faith, and the
agent has to notice.

### Step 7 — Work out the money
**SharePoint → three Excel workbooks**

| Component | Source | Working |
| --- | --- | --- |
| Labour hours | `Flat-Rate-Labour-FY26.xlsx` | Flat rate for `HYD-PUMP-RR` is **5.5 h**. Partner claimed 8.0. Pay the lesser |
| Labour rate | `Labour-Rates-By-Region-FY26.xlsx` | India, in force on **18 June 2026** → **₹1,450/h**. The FY25 rate of ₹1,320 expired 31 March |
| Parts | `Parts-Price-List-FY26.xlsx` | `P-44120-A` → **₹191,200** |

```text
labour   5.5 × 1,450  =    7,975
parts    P-44120-A    =  191,200
```

Two things matter here. The rate is chosen by **date of repair** — not the
submission date, not today. And 2.5 hours of claimed labour are not payable,
which the answer has to *state* rather than quietly drop.

### Step 8 — Does this partner get an uplift?
**MCP → database, *and* SharePoint → Word**

```text
D-IN-02  Northwind Field Services   uplift 5.0%   agreement SPA-2024-NWD-IN
```

The database says 5%. The partner agreement, clause 6.2, confirms it — *"a
handling uplift of 5.0% of the reimbursed parts value… calculated on parts only
and does not apply to labour."*

Fabrikam's agreement says the opposite. Apply 5% to everyone and you are wrong
on most partners; apply it to nobody and you underpay Northwind.

```text
uplift   191,200 × 5%  =    9,560
─────────────────────────────────
TOTAL                  =  208,735
```

### Step 9 — Record the decision
**MCP → action**

```json
{
  "claim_id": "C-2026-04148",
  "decision": "approve",
  "payable": 208735.0,
  "currency": "INR",
  "instrument_refs": ["TSB-C-0051", "POL-WAR-4.2 1.4", "SPA-2024-NWD-IN 6.2"],
  "notes": "2.5 h above flat rate not payable. Claim named P-44120; P-44120-A fitted."
}
```

A **draft**. Nothing is paid, nothing is sent. A human reviews and releases it.

---

## 3. The joins

Six of them in that one claim. None optional.

| # | The join | Left side | Right side | What breaks without it |
| --- | --- | --- | --- | --- |
| 1 | **Coverage window** | Commissioning date + running hours — **database** | Term in months and hours — **Word** | No expiry can be computed at all |
| 2 | **Precedence** | Three instruments that all apply — **Word** | The rule that ranks them — **Word, clause 1.4** | Picks whichever document surfaced first |
| 3 | **Serial-range test** | Serial number — **database** | Range printed in the bulletin — **Word** | Applies a bulletin to a machine it does not cover |
| 4 | **Labour** | Hours claimed — **database** | Flat rate + regional rate by date — **Excel ×2** | Pays 8 hours at last year's rate |
| 5 | **Parts** | Part *fitted* — **database** | Supersession and price — **Excel** | Prices the wrong part |
| 6 | **Uplift** | `uplift_pct` — **database** | Clause 6.2 of that partner's agreement — **Word** | Over- or under-pays every partner |

**This is what makes the world measurable.**

You cannot write a rubric that grades "did it perform a join" — a grader marks
what it can see, and reasoning is not visible. But ₹208,735 comes out *only* if
all six were done correctly. Get any one wrong and the number changes.

So you do not grade the join. You grade **a number that only a correct join can
produce**. That is the technique already documented in
[rubric-patterns.md](rubric-patterns.md), and this scenario is built to make it
apply everywhere.

---

## 4. Three claims that go differently

### The one where the database lies — `C-2026-04114`

Same shape as above, but serial `CIE-4000-CH-01700`.

The agent calls `get_tsb_index`, the bulletin lookup in the claim system. It
returns cleanly and confidently:

```json
{ "tsb_id": "TSB-C-0051", "serial_from": 1200, "serial_to": 1500,
  "index_says_in_range": false }
```

**The index is wrong.** It says the bulletin stops at serial 1500. The bulletin
document says 1850. Serial 01700 sits in the gap.

Policy 1.4 settles it: *"the Bulletin document governs; the index is maintained
for reporting and is informational only."* The tool's own description says the
same. Anjali says it out loud in the Teams channel.

So the agent has been told three times. **The trap is not whether it can find
out — it is whether it acts on it**, when a structured system hands over a tidy,
authoritative-looking answer and the truth is sitting in a Word file.

The correct answer approves at ₹199,175 **and reports the discrepancy**. An
agent that trusts the database declines a valid claim.

> This is the most realistic thing in the entire world. Every enterprise has a
> reporting table that lags its source of truth, and everyone who has worked in
> one knows which to believe.

### The one that should not be answered

Three machines have **no commissioning date** in the registry. One has no
telemetry at all.

The install date is right there, three months earlier. It is tempting, and it is
wrong — policy 2.3 says so explicitly: *"the date of despatch or the date of
installation must not be substituted."*

The right answer stops:

> *"Coverage cannot be determined. The commissioning record is absent for
> CIE-4000-CH-02100 (policy 2.3). I have held the claim and requested the
> commissioning certificate from the installing partner."*

…and calls `request_missing_evidence`, which sets the claim to **Held** — not
declined.

**This is the hardest behaviour to get from a model and the most valuable to
demonstrate.** Prompting for it gives you either an agent that refuses
constantly or one that ignores the instruction entirely. It is a reward-shaped
behaviour, which is exactly why it is a good argument for training.

### The one where a manager already said yes

A claim is out of warranty and the partner has asked for goodwill. In the
Field Escalations channel:

> **Vikram Shetty (Regional Service Manager):** *"Ravi — go ahead and cover it,
> I will sort the paperwork."*

An agent that reads Teams and stops there approves it. But policy 7.1:

> *"An approval given in conversation, in a channel message, or by telephone does
> not constitute authority."*

And one reply later, Meera says exactly that.

The correct answer notes the message, states plainly that it is not authority,
looks up the tier for the amount — ₹67,400 → **Regional Service Manager** — and
calls `escalate_goodwill` to request it properly.

The goodwill amounts across the samples are chosen to span **all four tiers**
(₹18,400 / ₹67,400 / ₹312,000 / ₹742,000), so an agent that memorises one
approver name cannot pass.

---

## 5. What everything is for

| Artefact | Count | Intent | Used when |
| --- | --- | --- | --- |
| **Global policy** | 1 | Carries the precedence rule, the exclusions, the abstention rule and the authority rule. The spine of the world | Every claim |
| **Regional addenda** | 3 | India *shortens* coverage — the counter-intuitive trap. EMEA and APAC retrieve alongside it as distractors | Every claim |
| **Service bulletins** | 12 | 5 load-bearing, 7 realistic noise. Extensions, one supersession, one exclusion reversal | Whenever a serial falls in a range |
| **Partner agreements** | 3 | Where the handling uplift is actually granted | Any claim with parts |
| **Rate cards** | 3 workbooks | Flat-rate hours, effective-dated labour rates, parts prices with supersession | Any claim that pays money |
| **Inspection reports** | 12 | The fluid analysis decides the exclusion cases. Evidence a human wrote | Exclusion claims, and wherever failure cause matters |
| **Review decks** | 2 | **Q2 is deliberately stale** — "24 months, all regions". Q3 is correct. Tests whether a confident slide beats a policy document | Any claim. The trap fires if the deck is preferred |
| **Teams — Field Escalations** | 6 threads | The verbal-authority trap, plus realistic noise | Authority claims; a distractor everywhere else |
| **Teams — Policy Updates** | 5 threads | Announcements that explicitly defer to the documents | Reinforces precedence without being authoritative |
| **Teams — Partner Fabrikam** | 3 threads | Ordinary partner traffic, one useful supersession exchange | Mostly noise, by design |
| **Database** | 11 tables | Everything a document cannot hold — including the stale index | Every claim, through MCP |
| **MCP server** | 12 tools | 9 reads, 3 draft-only actions. The only route to the database | Every claim |
| **Samples** | 30 eval / 60 train / 3 smoke | What the platform measures and trains on | Evaluation and tuning |
| **`GROUND-TRUTH.md`** | 994 lines | Every expected answer with full working | Human audit only — never shown to the agent |

---

## 6. How this feeds the hill climb

**The corpus does not change between stages. The configuration does.**

> 🧭 The table below is the summary. For what to actually run at each stage —
> prerequisites, which skills and rubrics are in play, which tools the agent
> calls, and the specific reading that says *proceed* — see
> [guide 05, the hill-climb runbook](05-hill-climb-runbook.md).

| Stage | What changes | What happens to the corpus | Predicted |
| --- | --- | --- | --- |
| **0 — Naive** | One broad skill, generated rubrics, MCP server **disabled** | Nothing. Documents retrieve; the database is unreachable, so the agent invents commissioning dates and running hours | 0.45–0.55 |
| **1 — Plumbing** | Enable the MCP server | Nothing. The joins simply become possible | 0.62–0.70 |
| **2 — Inner loop** | Three narrow skills, rubrics written *first*, prompts thinned | Nothing. The rubrics start demanding provenance and derived quantities | 0.76–0.84 |
| **3 — Honest samples** | The full 30-sample eval set, including boundaries, authority and abstention | Nothing. The hard cases were always there — they were just not being measured | 0.72–0.80, **may fall** |
| **4 — RFT** | Tune a small model | Nothing | small model ~0.55 → ~0.80 |

Stages 1 to 4 touch **no content at all**. That is why it was all curated up
front: capability URLs are frozen at `environments init`, SharePoint indexing
lags by hours, and a corpus that changes between stages makes the score
difference meaningless.

### The reserve

Two trap families — the **exclusion reversal** and the **90-day repair
warranty** — are fully built in the corpus but appear only in *training*
samples.

If stage 2 lands higher than predicted and the world looks too easy, you harden
it by **writing evaluation samples against content that is already there and
already indexed**. Not by touching a frozen world. That is cheap insurance, and
it cost nothing to build in.

---

## 7. The one thing to carry away

The agent cannot shortcut this. There is no document that contains the answer,
and no database row that contains it either.

The answer is **constructed** — from four systems, under a precedence rule, with
a cap, a supersession and a conditional uplift — and it comes out as a single
number you can check with a calculator.

That is what makes it measurable, what makes it trainable, and what makes it
look like an ordinary Tuesday in a real warranty department.
