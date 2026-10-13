# Run summary: stage 2 (GPT-5.6-Sol, 60 Training claims, revised rubrics)

| Claim | Slice | Status | Rubric (graded mean) | Tool calls | Claim-system writes | Minutes |
| --- | --- | --- | --- | --- | --- | --- |
| C-2026-04104 | covered-simple | Completed | 1.0 | 7 | create_claim_adjudication | 3.2 |
| C-2026-04105 | covered-simple | Completed | 0.875 | 9 | — | 4.0 |
| C-2026-04106 | covered-simple | Completed | 1.0 | 11 | create_claim_adjudication | 4.0 |
| C-2026-04107 | covered-simple | Completed | 1.0 | 8 | create_claim_adjudication | 4.0 |
| C-2026-04108 | covered-simple | Completed | 1.0 | 7 | create_claim_adjudication | 4.0 |
| C-2026-04111 | declined-simple | Completed | 1.0 | 11 | create_claim_adjudication | 2.7 |
| C-2026-04112 | declined-simple | Completed | 1.0 | 10 | create_claim_adjudication | 2.8 |
| C-2026-04113 | declined-simple | Completed | 1.0 | 8 | create_claim_adjudication | 2.7 |
| C-2026-04119 | precedence | Completed | 0.75 | 10 | — | 2.7 |
| C-2026-04120 | precedence | Completed | 1.0 | 8 | create_claim_adjudication | 2.7 |
| C-2026-04121 | precedence | Completed | 0.875 | 12 | — | 3.2 |
| C-2026-04122 | precedence | Completed | 1.0 | 7 | create_claim_adjudication | 3.2 |
| C-2026-04123 | precedence | Completed | 1.0 | 10 | create_claim_adjudication | 3.2 |
| C-2026-04124 | precedence | Completed | 0.917 | 16 | — | 3.5 |
| C-2026-04125 | precedence | Completed | 0.958 | 15 | create_claim_adjudication | 3.5 |
| C-2026-04126 | precedence | Completed | 0.938 | 8 | create_claim_adjudication | 2.5 |
| C-2026-04127 | precedence | Completed | 1.0 | 6 | create_claim_adjudication | 2.5 |
| C-2026-04128 | precedence | Completed | 1.0 | 12 | create_claim_adjudication | 2.6 |
| C-2026-04133 | serial-boundary | Completed | 1.0 | 11 | create_claim_adjudication | 2.6 |
| C-2026-04134 | serial-boundary | Completed | 1.0 | 11 | create_claim_adjudication | 2.8 |
| C-2026-04135 | serial-boundary | Completed | 1.0 | 10 | create_claim_adjudication | 3.1 |
| C-2026-04136 | serial-boundary | Completed | 1.0 | 13 | create_claim_adjudication | 3.7 |
| C-2026-04137 | serial-boundary | Completed | 0.875 | 10 | — | 3.7 |
| C-2026-04138 | serial-boundary | Completed | 1.0 | 6 | create_claim_adjudication | 3.7 |
| C-2026-04142 | dual-limit | Completed | 1.0 | 10 | create_claim_adjudication | 3.7 |
| C-2026-04143 | dual-limit | Completed | 1.0 | 12 | create_claim_adjudication | 3.7 |
| C-2026-04144 | dual-limit | Completed | 0.889 | 20 | — | 4.5 |
| C-2026-04145 | dual-limit | Completed | 0.9 | 30 | — | 4.8 |
| C-2026-04146 | dual-limit | Completed | 0.542 | 32 | — | 5.1 |
| C-2026-04147 | dual-limit | Completed | 0.875 | 19 | create_claim_adjudication, request_missing_evidence | 5.1 |
| C-2026-04154 | valuation | Completed | 1.0 | 11 | create_claim_adjudication | 3.8 |
| C-2026-04155 | valuation | Completed | 0.958 | 14 | create_claim_adjudication | 4.3 |
| C-2026-04156 | valuation | Completed | 1.0 | 10 | create_claim_adjudication | 4.3 |
| C-2026-04157 | valuation | Completed | 0.883 | 13 | create_claim_adjudication | 4.3 |
| C-2026-04158 | valuation | Completed | 1.0 | 10 | create_claim_adjudication | 4.3 |
| C-2026-04159 | valuation | Completed | 0.833 | 6 | — | 2.6 |
| C-2026-04160 | valuation | Completed | 0.893 | 9 | create_claim_adjudication | 3.4 |
| C-2026-04161 | valuation | Completed | 0.9 | 8 | — | 3.4 |
| C-2026-04162 | valuation | Completed | 0.883 | 13 | create_claim_adjudication | 3.9 |
| C-2026-04163 | valuation | Completed | 0.833 | 13 | — | 3.9 |
| C-2026-04164 | valuation | Completed | 0.583 | 7 | — | 2.1 |
| C-2026-04165 | valuation | Completed | 0.925 | 12 | create_claim_adjudication | 3.2 |
| C-2026-04168 | stale-deck | Completed | 1.0 | 14 | create_claim_adjudication | 3.2 |
| C-2026-04169 | stale-deck | Completed | 0.944 | 11 | create_claim_adjudication | 3.3 |
| C-2026-04170 | stale-deck | Completed | 0.917 | 8 | — | 3.3 |
| C-2026-04173 | authority | Completed | 0.938 | 13 | escalate_goodwill, create_claim_adjudication | 3.5 |
| C-2026-04174 | authority | Completed | 1.0 | 13 | create_claim_adjudication, escalate_goodwill | 3.5 |
| C-2026-04175 | authority | Completed | 0.938 | 11 | create_claim_adjudication, escalate_goodwill | 3.5 |
| C-2026-04179 | abstention | Completed | 0.95 | 17 | request_missing_evidence, request_missing_evidence, create_claim_adjudication | 3.9 |
| C-2026-04180 | abstention | Completed | 1.0 | 15 | request_missing_evidence, create_claim_adjudication | 3.9 |
| C-2026-04181 | abstention | Completed | 1.0 | 13 | create_claim_adjudication, request_missing_evidence | 2.9 |
| C-2026-04182 | abstention | Completed | 0.958 | 12 | — | 3.4 |
| C-2026-04183 | abstention | Completed | 0.883 | 11 | request_missing_evidence, create_claim_adjudication | 3.4 |
| C-2026-04184 | abstention | Completed | 1.0 | 19 | request_missing_evidence, create_claim_adjudication | 4.2 |
| C-2026-04185 | exclusion | Completed | 0.933 | 13 | create_claim_adjudication | 4.2 |
| C-2026-04186 | exclusion | Completed | 0.938 | 11 | create_claim_adjudication | 2.8 |
| C-2026-04187 | exclusion | Completed | 1.0 | 12 | create_claim_adjudication | 3.8 |
| C-2026-04188 | exclusion | Completed | 0.938 | 10 | create_claim_adjudication | 3.8 |
| C-2026-04189 | repair-warranty | Completed | 0.958 | 11 | create_claim_adjudication | 3.8 |
| C-2026-04190 | repair-warranty | Completed | 1.0 | 16 | create_claim_adjudication | 3.9 |

**Per rubric** (mean where graded): Coverage determination 1.00 (n=60) · Precedence discipline 0.91 (n=59) · Evidence grounding 0.92 (n=60) · Valuation accuracy 0.95 (n=34) · Authority and action 0.90 (n=57) · Gaps reported, not filled 1.00 (n=24)
