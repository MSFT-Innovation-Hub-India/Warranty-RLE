# Hand-check: stage 1 (GPT-5.6-Sol, 60 Training claims)

Every answer the automatic scorer marked wrong or couldn't read ([ground-truth-check.md](ground-truth-check.md): 45/60), read in full against the answer key (`world-builder/out/data/claims.json`) and, where it mattered, the claim-system actions Sol recorded. Result: **57/60 right**, 1 wrong, 1 world-data defect, 1 platform failure.

## Scorer misread a right answer (12)

| Claim | Scorer said | By hand | Why the scorer missed it |
| --- | --- | --- | --- |
| C-2026-04119 | decision unclear, no amount | ✅ "Yes, within coverage under TSB-C-0051" | The prompt asks only "still in warranty?"; no amount was asked for |
| C-2026-04170 | no amount | ✅ Same: in warranty under TSB-C-0051 | Same narrow question |
| C-2026-04121 | request evidence | ✅ Decline under ADD-IN-2.1 | Read "I did not … request evidence" as a request |
| C-2026-04161 | escalate | ✅ Approve ₹753,880 under TSB-C-0051 | Read "no goodwill approval or other escalation is required" as an escalation |
| C-2026-04159 | governing TSB-C-0051 | ✅ Approve ₹72,945 under ADD-IN-2.1 | Took the bulletin Sol named to rule it out |
| C-2026-04187 | governing ADD-IN-2.1 | ✅ Approve ₹199,175 under TSB-C-0051 | Same: another instrument named in passing |
| C-2026-04186 | governing TSB-C-0043 | ✅ Decline; TSB-C-0051 coverage, clause 5.2 exclusion stands | Sol cites TSB-C-0043 for the exclusion question, correctly |
| C-2026-04188 | governing ADD-IN-2.1 | ✅ Decline; TSB-C-0051 window, clause 5.2 exclusion | Same |
| C-2026-04189 | governing ADD-IN-2.1 | ✅ Approve ₹69,575 under POL-WAR-4.2 § 6.1 (90-day repair warranty) | The scorer doesn't recognise a policy clause as the governing instrument |
| C-2026-04190 | governing ADD-IN-2.1 | ✅ Same as 04189 | Same |
| C-2026-04173 | decision decline | ✅ Warranty declined; ₹18,400 goodwill **escalated** to the Service Supervisor (the Tier 1 role up to ₹25,000), recorded as `escalate_goodwill` and an `escalate` draft | The answer opens with "not covered" |
| C-2026-04175 | governing TSB-C-0051 | ✅ Warranty declined; ₹43,800 goodwill **escalated** to the Regional Service Manager (Tier 2), recorded | Took the bulletin Sol ruled out |

## Wrong (1)

| Claim | Right answer | Sol | Rubric |
| --- | --- | --- | --- |
| C-2026-04174 | Escalate the ₹742,000 goodwill request to the Director, Aftermarket (Tier 4) | Named the right authority but **recorded no escalation**: "consider goodwill only as a separate, properly authorised exception"; "No adjudication or other claim-system action has been recorded". The prompt ended "…and advise" | **0.85**, with **Authority and action 1.00** |

## World-data defect (1)

| Claim | Answer key | Sol | Finding |
| --- | --- | --- | --- |
| C-2026-04106 | Approve ₹26,875 | Held the claim and recorded an evidence request: operation `HYD-PUMP-RR` (pump remove and replace, 5.5 h) conflicts with the part fitted, P-44210 (hydraulic hose set) | It is the **only** `HYD-PUMP-RR` claim in the world fitted with a hose set; every other one fits P-44120-A. A generator defect. Sol's hold is defensible; not counted as a Sol error |

## Platform failure (1)

| Claim | What happened |
| --- | --- |
| C-2026-04185 | Execution `Failed` after 6 minutes with "We encountered an issue while processing your request. Please try again in a new chat." The claim record and documents had been read. No answer to grade |
