-- What the agent wrote: every row in the action tables, and any claim whose status changed.
-- Run after an evaluation and before db-reset-actions.sql; save the output with the stage's results.
SELECT 'draft' AS kind, draft_id AS id, claim_id,
       CONCAT(decision, ' | payable=', COALESCE(CONVERT(NVARCHAR(40), payable), '-'), ' ', COALESCE(currency, ''), ' | refs=', COALESCE(instrument_refs, '')) AS detail,
       created_at
  FROM ClaimAdjudicationDraft
UNION ALL
SELECT 'evidence', request_id, claim_id, CONCAT('field=', field_name), created_at FROM EvidenceRequest
UNION ALL
SELECT 'escalation', escalation_id, claim_id, CONCAT('amount=', CONVERT(NVARCHAR(40), amount), ' | role=', approver_role), created_at FROM GoodwillEscalation
ORDER BY claim_id, kind;
SELECT claim_id, status FROM Claims WHERE status <> 'Submitted' ORDER BY claim_id;
