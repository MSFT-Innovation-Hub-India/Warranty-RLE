-- Baseline check: are the action tables clean and every claim back to its seeded status?
-- Expect 0 · 0 · 0 · 0 before every evaluation run.
SELECT (SELECT COUNT(*) FROM ClaimAdjudicationDraft)                 AS drafts,
       (SELECT COUNT(*) FROM EvidenceRequest)                        AS evidence_requests,
       (SELECT COUNT(*) FROM GoodwillEscalation)                     AS escalations,
       (SELECT COUNT(*) FROM Claims WHERE status <> 'Submitted')     AS claims_not_submitted;
