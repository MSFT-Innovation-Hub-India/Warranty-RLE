-- Reset the agent's writes so the next run starts from the seeded state.
-- The seed (out/db/seed.azuresql.sql) has all three action tables empty and all 90 claims 'Submitted'.
DELETE FROM ClaimAdjudicationDraft;
DELETE FROM EvidenceRequest;
DELETE FROM GoodwillEscalation;
UPDATE Claims SET status = 'Submitted' WHERE status <> 'Submitted';
SELECT (SELECT COUNT(*) FROM ClaimAdjudicationDraft)                 AS drafts,
       (SELECT COUNT(*) FROM EvidenceRequest)                        AS evidence_requests,
       (SELECT COUNT(*) FROM GoodwillEscalation)                     AS escalations,
       (SELECT COUNT(*) FROM Claims WHERE status <> 'Submitted')     AS claims_not_submitted;
