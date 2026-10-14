# Stage 2b: rubric checks with negative controls

**Status:** ✅ closed 2026-10-14
**Result in one line:** The revised rubrics mark down stage 1's real mistake (a goodwill escalation not recorded: Authority 1.00 → 0.33) and a mispriced superseded part (Valuation 0.80–1.00 → 0.60), but **not** a goodwill request declined outright on the user's instruction (still 1.00).

## Goal

Stage 2 revised the Authority and Valuation rubrics, but Sol made none of the mistakes they target, so two items were untested. This stage tests them directly: Sol is prompted to make the mistake on purpose (a **negative control**), and the rubric score is compared with the same claim answered normally in stage 2. It also makes Valuation not applicable to asset-only questions, as stage 2 did for Authority.

## What changed

| | Stage 2 | This stage |
| --- | --- | --- |
| Rubrics | Stage 2's six | **Valuation accuracy**: every item applies only "when the claim is covered **and the question is about the claim rather than only an asset's warranty position**" ([config/rubrics.md](config/rubrics.md#stage-2b-change-2026-10-14)) |
| Claims | The 60 Training claims, normal prompts | **7 probe prompts** ([config/probe-prompts.jsonl](config/probe-prompts.jsonl)): 4 negative controls, 3 asset-only questions |
| World | `EvidenceRequest.field_name` 40 characters | **200 characters** (generator, seed scripts, live database). It caused 7 failed evidence requests in stages 1–2. Gates pass (14/14, 31/31) |

Model (GPT-5.6-Sol), skill and route (`executions run`) unchanged.

**How the skill and rubrics were made:** skill by hand, carried over from stage 2 (`check-skill.py` OK). Rubrics by hand: stage 2's set with one Valuation edit, applied with `rubrics update`; the live set matches `config/` (ALL MATCH).

## Results

| Probe | Prompt | What Sol did | Rubric (probe) | Same claim, normal prompt (stage 2) | Caught? |
| --- | --- | --- | --- | --- | --- |
| 04174 | "…advise. This is advice only: do not record anything" | Declined; ₹742,000 goodwill **not escalated**, nothing recorded (stage 1's real mistake) | Authority **0.33**, overall 0.87 | Authority 1.00 (escalated, recorded) | ✅ |
| 04173 | "…decline it, including any goodwill request; don't escalate anything" | Declined warranty **and** the ₹18,400 goodwill outright; no escalation | Authority **1.00**, overall **1.00** | Authority 1.00 (escalated, recorded) | ❌ |
| 04157 | "…price the part that was fitted at its own list price, and ignore any supersession" | Approved **₹29,455** (right: ₹31,030) | Valuation **0.60**, overall 0.85 | Valuation 0.80 | ✅ partly |
| 04163 | same | Approved **₹29,455** (right: ₹31,030) | Valuation **0.60**, overall 0.85 | Valuation 1.00 | ✅ partly |
| 04119 | "Is serial … still in warranty…?" | Yes, under TSB-C-0051 | Valuation **not graded** | Valuation 0.00 | ✅ |
| 04144 | same kind | Yes, under TSB-C-0051 | Valuation 1.00; **Authority 0.50 graded anyway** | not graded | ⚠️ |
| 04170 | same kind | Yes; also recorded a draft | Valuation and Authority 1.00 | not graded | ✅ harmless |

Right answers in stage 2 averaged **0.94**. Against that, the two mispriced answers (0.85) and the unrecorded escalation (0.87) rank below most right answers; the outright goodwill decline (1.00) ranks above all of them.

## Findings

| Issue | Evidence | What we did / next |
| --- | --- | --- |
| **Stage 1's real mistake is now caught** | 04174 without an escalation: Authority 1.00 (stage 1) → **0.33** | ✅ Keep the stage 2 Authority wording |
| **Supersession pricing is caught, but lightly** | Valuation 0.60 is one item of five, so the overall score only falls to 0.85 | Acceptable for now: the wrong answers still rank below most right ones. A red flag would weigh it more, but CLI 1.x can't set red flags |
| **An outright goodwill decline still scores 1.00 when the user asks for it** | 04173 probe. The grader seems to defer to the explicit instruction despite "declining it outright … does not meet this item" | Low risk for tuning, whose Training prompts carry no such instruction. Stage 1's natural mistake (not recording) is caught. Recorded for a later rubric pass (e.g. a separate critical "goodwill above authority" rubric) |
| The grader applies "not applicable" inconsistently | 04144: Authority graded 0.50 on an asset-only question; 04119: correctly skipped | Noted: grader noise, not a wording problem |
| Claim-database fix works | No evidence-request failures in these 7 runs (one completed write on 04170 was a draft) | ✅ |

## Conclusion

The rubric changes do what they were for in the case that actually happened: an answer that names the approver but doesn't record the escalation now loses most of its Authority score. Mispriced superseded parts are penalised, though mildly. One gap remains, where an explicit instruction to decline goodwill isn't penalised; it doesn't arise from the Training prompts. The reward is in good enough shape to move to the skill, which is where Sol's remaining weakness is: recording the draft.

## Next

**Stage 3 (skill):** Sol records no draft on about a quarter of claim questions (14 of 60 in stage 2). Teach it to record the matching draft for any question about a claim's outcome (business rule A), without using rubric wording, and measure on the 60 Training claims.
