-- Baseline check: are the action tables clean and every claim back to its seeded status?
-- Seeded status: the live claims (C-2026-04xxx) are 'Submitted'; the settled earlier claims that
-- repair-warranty claims rest on (C-2026-03xxx) are 'Paid'.
-- Expect 0 · 0 · 0 · 0 before every evaluation run.
SELECT (SELECT COUNT(*) FROM ClaimAdjudicationDraft)                 AS drafts,
       (SELECT COUNT(*) FROM EvidenceRequest)                        AS evidence_requests,
       (SELECT COUNT(*) FROM GoodwillEscalation)                     AS escalations,
       (SELECT COUNT(*) FROM Claims WHERE status <> CASE WHEN claim_id LIKE 'C-2026-03%' THEN 'Paid' ELSE 'Submitted' END) AS claims_not_seeded;
