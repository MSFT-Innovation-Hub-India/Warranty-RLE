-- Row count for every table in the claim database. Compare with the seeded counts after a
-- full re-seed (world-builder/out/db/seed.azuresql.sql) to see whether anything outside the
-- three action tables was changed. The three action tables are 0 when seeded.
SELECT 'Dealers' AS tbl, COUNT(*) AS n FROM Dealers
UNION ALL SELECT 'Parts', COUNT(*) FROM Parts
UNION ALL SELECT 'Assets', COUNT(*) FROM Assets
UNION ALL SELECT 'AssetTelemetry', COUNT(*) FROM AssetTelemetry
UNION ALL SELECT 'Claims', COUNT(*) FROM Claims
UNION ALL SELECT 'ServiceHistory', COUNT(*) FROM ServiceHistory
UNION ALL SELECT 'GoodwillAuthority', COUNT(*) FROM GoodwillAuthority
UNION ALL SELECT 'TsbApplicability', COUNT(*) FROM TsbApplicability
UNION ALL SELECT 'ClaimAdjudicationDraft', COUNT(*) FROM ClaimAdjudicationDraft
UNION ALL SELECT 'EvidenceRequest', COUNT(*) FROM EvidenceRequest
UNION ALL SELECT 'GoodwillEscalation', COUNT(*) FROM GoodwillEscalation;
