-- World v2.3: the settled earlier warranty claims that the repair-warranty claims (policy 6.1) rest on.
-- Before v2.3, service job J-00087 and J-00089 both cited C-2026-03110, which did not exist in Claims,
-- so get_claim answered "No claim with this reference exists" and the ground truth (approve, RW) could
-- not be supported from the claim system. Brings an existing v2.2 database to match out/db/seed.azuresql.sql.
-- Idempotent: safe to run twice.
IF NOT EXISTS (SELECT 1 FROM Claims WHERE claim_id = 'C-2026-03110')
  INSERT INTO Claims (claim_id, serial, dealer_id, submitted_date, repair_date, operation_code, claimed_part, claimed_labour_hours, goodwill_requested, status)
  VALUES ('C-2026-03110', 'CIE-4000-CH-01980', 'D-IN-01', '2026-04-26', '2026-04-20', 'CTRL-BD-RR', 'P-44900', 1.5, NULL, 'Paid');
IF NOT EXISTS (SELECT 1 FROM Claims WHERE claim_id = 'C-2026-03111')
  INSERT INTO Claims (claim_id, serial, dealer_id, submitted_date, repair_date, operation_code, claimed_part, claimed_labour_hours, goodwill_requested, status)
  VALUES ('C-2026-03111', 'CIE-4000-CH-01981', 'D-IN-01', '2026-04-26', '2026-04-20', 'CTRL-BD-RR', 'P-44900', 1.5, NULL, 'Paid');
UPDATE ServiceHistory SET claim_id = 'C-2026-03111' WHERE job_id = 'J-00089' AND serial = 'CIE-4000-CH-01981';
SELECT claim_id, serial, submitted_date, repair_date, operation_code, claimed_part, claimed_labour_hours, status
  FROM Claims WHERE claim_id LIKE 'C-2026-03%' ORDER BY claim_id;
SELECT job_id, serial, claim_id, completed_date FROM ServiceHistory
  WHERE serial IN ('CIE-4000-CH-01980', 'CIE-4000-CH-01981') ORDER BY job_id;
SELECT COUNT(*) AS dangling_service_jobs FROM ServiceHistory s
  WHERE NOT EXISTS (SELECT 1 FROM Claims c WHERE c.claim_id = s.claim_id);
