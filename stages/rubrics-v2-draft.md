# Rubrics v2 — draft for review (2026-10-05)

**Status:** draft. Not applied to the platform. Pinned and applied only after the user approves.

**Why.** The generated rubrics (v1, pinned since stage 0):
- gave **1.0 to wrong answers**: GPT-5.6-Sol 04172 (hedged on ₹312k goodwill) and 04103 (a held seal kit);
- **marked down correct answers for wording**. *Claim Determination* requires the exact words "covered / declined / cannot yet be decided", so correct approvals scored 0.8 (Sol) and correct declines and holds scored 0.0 (GPT-5.4-Mini).

In fine-tuning the rubric score is the **only reward**, so v1 would teach vocabulary rather than correctness. The baseline and the post-tuning evaluation must use the same, final rubrics, so v2 must be settled **before** the MAI baseline.

**Source.** [Design guide 03 § 9.2](../docs/03-scenario-design.md#92-rubrics-for-the-flagship-skill--written-before-the-skill-exists), written before any skill existed (AGENTS.md: rubrics before skills). Its satisfiability audit (§ 9.3) holds: every rubric can be met or skipped on every claim path, including "cannot be determined" and "serial not in the registry".

**Changes from § 9.2**, each traced to evidence:

| Change | Evidence |
| --- | --- |
| Outcome and action accepted **in any equivalent wording** (approve = covered; hold / request evidence = cannot yet be decided) | v1 penalised correct answers for words: 4 cases in 2-base, 5 in 3-mini-base |
| Kept v1's **"the draft was actually recorded"** check (the trajectory must show it) | It's the only v1 rubric that checks an action, not text; MAI skipped drafts |
| Goodwill above authority must be **escalated, not approved or hedged** | Sol 04172 hedged, and v1 gave it 1.0 |
| Valuation and precedence items apply **only where relevant** (nothing is payable on a decline or a hold) | § 9.3 skip paths |

**Limit (guide 03 § 9.4):** the grader has no answer key, so no rubric can say "the payable is ₹199,175". These rubrics require the working to be **shown**, so a wrong input becomes visible. The ground-truth scorer stays the second number.

---

### 1. Coverage determination
Description: The coverage conclusion follows from the asset's own dates and limits.
- States the coverage outcome: the repair is covered, it is declined, or a decision is not yet possible; any equivalent wording counts (for example "approve" for covered, "hold" or "request evidence" when a decision is not yet possible)
- Names the coverage limits actually applied, in months and in running hours, and the date the coverage period started from
- Compares the repair date, and the running hours at the date of repair, against those limits
- Where one limit is exceeded and the other is not, says which limit ends the cover

### 2. Precedence discipline
Description: The governing instrument is identified and justified against the alternatives.
- Names exactly one governing instrument, by reference code
- States why it governs over the other instruments that mention this asset
- Treats a superseded bulletin as having no effect, and says so where one was found
- Where the service system's bulletin index and a bulletin document disagree, follows the document and reports the disagreement

### 3. Evidence grounding
Description: Every factual claim is traceable to the source that owns it.
- Attributes every coverage term or exclusion to a policy, addendum or bulletin, by reference and clause
- Attributes every date and running-hours figure to the asset registry or the telemetry reading, naming the as-of date
- Attributes every monetary figure to the rate card or the parts list, naming the region and the effective date
- Introduces no figure, date, part number or reference that is absent from the sources

### 4. Valuation accuracy
Description: Where the claim is covered, the payable amount is derived, shown, and internally consistent.
- States payable labour as the lesser of the claimed hours and the flat-rate allowance, and names both
- Applies the labour rate in force on the date of repair, and names that rate
- Prices the part actually fitted, naming the part number and any supersession
- Applies a partner handling uplift only where the partner agreement grants one
- States the total payable, and states any claimed amount not payable as an explicit variance

### 5. Authority and action
Description: The disposition is one the requester is entitled to take, and it is carried out.
- Names the next action: approve, decline, request evidence, or escalate; any equivalent wording counts
- Where goodwill is requested beyond the requester's authority, escalates it to the approving role named in the authority matrix rather than approving it or leaving the choice open
- Treats an approval given in a conversation or channel message as not constituting authority, where one is present
- When the decision requires a claim-system action, the execution shows the matching draft, evidence request or escalation was actually recorded, with content consistent with the decision

### 6. Evidence closure
Description: Gaps and silences are reported rather than filled.
- Names any required record that is missing, and the field that is absent
- States explicitly where a consulted source contained nothing relevant
- Does not substitute a different field for a missing one
- Where the evidence is sufficient, states that the required records were present

---

**Not carried over from v1:** *Requested Outcome Delivery* (now inside 1 and 5); *Adjudicator-Ready Presentation* (attribution moves to 3; "lead with the decision" is style, not correctness). *Internal Record Use* is replaced by 3, which checks attribution per fact rather than a list of sources consulted.

**Before applying:**
1. Check the skill against these rubrics: no shared 5-word phrases (AGENTS.md).
2. Apply with `skills update --file`.
3. Delete and re-upload the 30 Evaluation samples; samples capture rubrics at upload time.
4. Re-score a handful of existing answers by hand to confirm v2 marks down 04172 (Sol) and doesn't mark down 04153 (correct).

---

## Rubrics for `library-research` (new skill) — draft for review (2026-10-05)

**Why.** In the research-skill design ([experiment](experiments/research-skill-wce-dev/README.md)), each skill is graded only on its own rubrics. `library-research` has none, so its work is unmeasured, and 🔬 probably unrewarded in fine-tuning. The audit of the successful run showed the habits worth shaping: a 52k-character search for a price the claim system had already returned, 4 searches for one rate card, an empty search, and a marginal 29k one.

### R1. Answers what was asked
Description: Each question put to the research step gets a direct answer or a plain not-found.
- Gives an answer for every question it received
- For each answer, returns the specific wording, number or rate-card line that settles it, rather than a summary of the whole document
- Where a question could not be answered from the library, says so for that question instead of offering something else

### R2. Source attribution
Description: Every returned fact can be located by an adjudicator.
- Names the document for every fact, by reference code or file name
- Names the clause, section or table row for every fact, with the row's effective dates where the row carries them

### R3. Restraint
Description: The research step reports and does not adjudicate.
- Does not state or recommend a claim outcome, coverage position or payable amount
- Adds no information beyond what the questions asked for
- Introduces no figure, date or reference that is absent from the retrieved documents

### R4. Search economy
Description: The library is searched efficiently.
- Does not repeat a search for a fact it has already retrieved
- Does not search for a value that was already supplied in the request
- Stops searching on a question once that question is answered

**Satisfiability:** every item can be met on every path: a found fact, a not-found fact, a request with one or many questions. R4 is judged from the trajectory, which the grader sees.
