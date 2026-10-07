# Stage 2: all 30 evaluation prompts (frontier model)

**Result:** rubric **0.978** · correct **27/30** (29/30 by the world's own rules) · 2026-10-04 · job `9f4ad313-9629-4571-8f58-13a7bba63c97` · ⚠️ no frontier headroom

## The change (against stage 1)
Evaluation samples go from 8 easy prompts to **all 30** ([samples.jsonl](samples.jsonl)). These cover every slice: valuation 6 · precedence 5 · serial-boundary 4 · covered-simple 3 · dual-limit 3 · abstention 3 · declined-simple 2 · stale-deck 2 · authority 2. Everything else is as in stage 1 (GPT-5.6-Sol, one skill, the same pinned rubrics, MCP on).

## Apply and run
```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $sk='cf00d339-5217-4cd1-b390-cc0d911735da'
frontier-tuning samples upload stages\stage-2\samples.jsonl --skill-id $sk --type Evaluation --env-id $e
frontier-tuning samples delete <old-sample-id> --yes --env-id $e          # each of stage 1's 8 (no delete-by-skill in CLI 0.3.16)
az containerapp update -n contoso-service-mcp -g pcdotai-agent --min-replicas 5 --max-replicas 5
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql                      # expect 0 0 0 0
frontier-tuning evaluate start --skill-id $sk --base-model prod-gpt-56-reasoning-sol --strategy simple --env-id $e -o json
# then results, score_ground_truth.py, snapshot and reset, as in stage 1
```

## Result
| Rubric score | Correct | Per rubric (Outcome · Determination · Grounding · Presentation · Draft) |
| --- | --- | --- |
| **0.978** | **27/30** · 29/30 by the world's rules | 0.994 · 0.960 · 0.997 · 0.982 · 0.958 |

Every hard slice was right: precedence, serial boundary, dual limit, valuation (supersession, uplift, dated labour rates), stale deck, abstention. Detail: [ground-truth-check.md](ground-truth-check.md) · [eval-results.json](eval-results.json).

## Findings
| Issue | What we did |
| --- | --- |
| **The frontier model saturates the world:** GPT-5.6-Sol with tools handles every designed trap | The climb moves to a small model (stage 3); the frontier line ends here |
| One genuine miss: 04172 hedged on a ₹312k goodwill request instead of escalating, and the rubrics gave it **1.0** | More evidence the generated rubrics don't check correctness; hand-written rubrics before RFT |
| World defect: 4 eval claims had identical training twins (eval answers would leak into RFT) | **World v2.2:** training claims use their own serials; `populate.py` refuses identical twins |
| Answer-key defect (04178): a missing hours reading was tested before an already-expired time limit | **World v2.2:** the engine tests the time limit first |
| The scorer misread 3 correct answers ("covered by X", "X does not govern", negated lists) | Scorer fixed and tested; flagged answers are now read by hand |
