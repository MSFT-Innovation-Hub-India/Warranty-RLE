# Stage 1 rubrics: hand-written

**Status:** applied to `warranty-assistant` in wce-main on 2026-10-08. Pinned in [warranty-assistant.rubrics.json](warranty-assistant.rubrics.json); this page is the readable copy.

**Why hand-written.** The rubrics the platform generated in stage 0 rewarded the wrong things: both authority claims were wrong (declined instead of escalated) and scored 0.85 and 1.0, while correct but terse answers scored below 0.6. In RFT the rubric score is the only reward, so it has to follow correctness before anything is tuned. The grader has no answer key, so these rubrics require the working to be **shown**, which makes a wrong input visible; ground-truth correctness stays the second number.

**Source.** Design guide 03 § 9.2, written before any skill existed (rubrics before skills), then reviewed against stage 0's 30 answers and world v3 (2026-10-08). No 5-word phrase is shared with the skill.

### 1. Coverage determination (critical)
The coverage conclusion follows from the asset's own dates and limits.

- States the coverage outcome: the repair is covered, it is declined, or a decision is not yet possible; any equivalent wording counts (for example "approve" for covered, "hold" or "request evidence" when a decision is not yet possible)
- Names the coverage limits applied, in months and in running hours, and the date the coverage period runs from; or, where one of these cannot be established, says which record is missing
- Compares the repair date and the running hours at the date of repair against those limits, or says which of the two cannot be compared and why
- Where one limit is exceeded and the other is not, says which limit ends the cover

### 2. Precedence discipline (critical)
The governing instrument is identified and justified against the alternatives.

- Where coverage can be determined, names one governing instrument by reference code
- States why that instrument governs over the other instruments that mention this asset, such as a regional addendum or the global policy
- Treats a bulletin that is superseded, or whose serial range, component scope or region excludes this asset, as not governing, and says why where one was considered
- Where the claim system's bulletin index and a bulletin document disagree on a serial range, follows the document and reports the disagreement

### 3. Evidence grounding (high)
Every factual claim is traceable to the source that owns it.

- Attributes each coverage term or exclusion to a policy, addendum or bulletin, by reference and clause
- Attributes each date and running-hours figure to the claim-system record that holds it, naming the as-of date of any reading
- Attributes each rate and price to its source (the labour rate card, the parts price list or the claim system's part record), naming the region and the effective date where they apply
- Introduces no figure, date, part number or reference that is absent from the sources consulted

### 4. Valuation accuracy (critical)
Applies only when the claim is covered: the payable amount is derived, shown and internally consistent. A declined or held claim has no payable amount to value.

- When the claim is covered, states payable labour hours as the lesser of the hours claimed and the flat-rate allowance for the operation, and names both
- When the claim is covered, applies the labour rate in force on the date of repair, and names that rate
- When the claim is covered, prices the part actually fitted, naming the part number and any supersession
- When the claim is covered, applies a partner handling uplift only where the partner's agreement grants one
- When the claim is covered, states the total payable, and reports as a variance any claimed hours or amount above what is payable

### 5. Authority and action (critical)
The disposition is one the requester is entitled to take, and it is carried out.

- Names the next action (approve, decline, request evidence or escalate) and who takes it; any equivalent wording counts
- Where goodwill is requested above the requester's authority, escalates it to the approving role named in the authority matrix, rather than approving it, declining it outright or leaving the choice open
- Treats an approval given in a conversation or channel message as not constituting authority, where one is present
- Where the decision calls for a claim-system action, the execution shows that the matching draft, evidence request or escalation was recorded once, with content consistent with the decision

### 6. Gaps reported, not filled (high)
Missing records are named and never papered over.

- Names any record needed for the decision that is missing, and the field that is absent
- Does not substitute a different field for a missing one, such as an installation date for a missing commissioning date
- Where a record needed for the decision is missing, does not state a final outcome that depends on it

## Review: what changed from the draft, and why

| Rubric | Change | Evidence |
| --- | --- | --- |
| 1 Coverage | Limits and comparison items now accept "says which record is missing" | Unsatisfiable on abstention claims otherwise (no commissioning date, no reading); a correct hold would fail |
| 2 Precedence | "Names exactly one…" → "Where coverage can be determined, names one…"; a bulletin excluded by **scope or region** is also treated as not governing | Abstention claims have no governing instrument in the answer key; the EMEA-only bulletin trap (TSB-P-0115) is a region exclusion |
| 3 Grounding | Sources updated for world v3: claim-system records (the dossier) and the claim system's part record are valid sources for dates, hours and part prices | In v3 these facts arrive in one dossier; the draft named the old separate tables |
| 4 Valuation | Variance reported only where part of the claim isn't payable. **Revised after the first batch (2026-10-08):** every item now starts "When the claim is covered" and the description says a declined or held claim has nothing to value | The draft required a variance on every approval. In the first stage-1 batch the grader applied this rubric to a **correct decline** (04110) and scored it 0.0 for having no breakdown or variance |
| 5 Authority | The next action must name who takes it; goodwill above authority must be escalated "rather than approving it, **declining it outright** or leaving the choice open"; a claim-system action must be recorded **once** | Stage 0: both goodwill claims were declined outright and scored 0.85–1.0; duplicate and contradictory drafts seen in trials |
| 6 Gaps | Renamed. Dropped "states where a consulted source contained nothing" and "states that the required records were present"; added "does not state a final outcome that depends on a missing record" | The dropped items reward boilerplate, not judgment; the new one is the core of the abstention trap |

**Kept from the draft:** outcome in any equivalent wording (the generated rubrics marked correct answers down for wording); the "draft actually recorded" check (the only rubric that checks an action, not text); valuation and precedence items apply only where relevant.
