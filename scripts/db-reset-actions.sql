-- Reset the agent's writes so the next run starts from the seeded state.
-- The seed (out/db/seed.azuresql.sql) has all three action tables empty, the live claims (C-2026-04xxx)
-- 'Submitted', and the settled earlier claims (C-2026-03xxx) 'Paid'.
DELETE FROM ClaimAdjudicationDraft;
DELETE FROM EvidenceRequest;
DELETE FROM GoodwillEscalation;
UPDATE Claims SET status = CASE WHEN claim_id LIKE 'C-2026-03%' THEN 'Paid' ELSE 'Submitted' END WHERE status <> CASE WHEN claim_id LIKE 'C-2026-03%' THEN 'Paid' ELSE 'Submitted' END;
SELECT (SELECT COUNT(*) FROM ClaimAdjudicationDraft)                 AS drafts,
       (SELECT COUNT(*) FROM EvidenceRequest)                        AS evidence_requests,
       (SELECT COUNT(*) FROM GoodwillEscalation)                     AS escalations,
       (SELECT COUNT(*) FROM Claims WHERE status <> CASE WHEN claim_id LIKE 'C-2026-03%' THEN 'Paid' ELSE 'Submitted' END) AS claims_not_seeded;
