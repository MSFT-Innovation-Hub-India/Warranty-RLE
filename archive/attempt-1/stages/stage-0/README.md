# Stage 0: naive baseline (world v3, MAI-CODE-5b)

**Result:** rubric **0.744** · correct **23/30** (hand-checked) · hand-in problems 6/30 · 2026-10-07/08 · ✅ closed

## The configuration
The honest starting point: the skill a business owner would write, and the rubrics the platform generates from it.

| | |
| --- | --- |
| World | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4`, **world v3** |
| Model · strategy | MAI-CODE-5b `dev-ct-mai-code-mp` · `simple` |
| Skill | `warranty-assistant` `cf00d339-5217-4cd1-b390-cc0d911735da`: [warranty-assistant.md](warranty-assistant.md), a business brief: what to establish, which sources exist, how to write. No method, no tool names, no rules |
| Rubrics | 5 platform-generated, pinned: [warranty-assistant.rubrics.json](warranty-assistant.rubrics.json) |
| Samples | All 30 Evaluation prompts: [samples.jsonl](samples.jsonl) (IDs: [sample-map.json](sample-map.json)) |
| Tools | Claim system (MCP): `get_claim_dossier` + 3 draft actions · SharePoint · Teams · M365 search (110 tools in all) |

## Apply
```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $sk='cf00d339-5217-4cd1-b390-cc0d911735da'
$f = Get-Content stages\stage-0\warranty-assistant.md -Raw
$desc = [regex]::Match($f,'(?m)^description: (.*)$').Groups[1].Value.Trim(); $body = ($f -split '## Instructions',2)[1].Trim()
frontier-tuning skills update $sk --description $desc --instructions $body --env-id $e     # rubrics untouched (5, pinned)
# use --instructions, not skills create --file: the file importer drops sections it doesn't recognise
```

## Run
```powershell
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql                                         # 0 0 0 0
$s = (Get-Content stages\stage-0\sample-map.json -Raw | ConvertFrom-Json | ForEach-Object { "$($_.claim.Substring(7))=$($_.id)" }) -join ','
powershell -File scripts\eval-batches.ps1 -Env $e -Samples $s -OutDir docs\evidence\stage-0 -BatchSize 5
python scripts\summarise-stage.py docs\evidence\stage-0 stages\stage-0 --consolidate   # merges, tabulates, scores; keeps one results file and one snapshot file
# then read every ❓ and ❌ by hand (hand-check.md)
```

## Result
| Rubric score | Correct (ground truth, hand-checked) | Hand-in problems | Overflows | Calls per claim | Execution per claim |
| --- | --- | --- | --- | --- | --- |
| **0.744** | **23/30 (77%)** | 4 echoed (lost) · 2 partly rejected (still correct) · 1 echo recovered | 0 | median 10 (2–32) | median 6.6 min (max 12.8) |

By slice (correct): covered-simple 3/3 · declined-simple 2/2 · precedence 4/5 · serial-boundary 4/4 · valuation 6/6 · stale-deck 1/2 · dual-limit 1/3 · abstention 2/3 · **authority 0/2**.

Detail: [run-summary.md](run-summary.md) (per claim) · [ground-truth-check.md](ground-truth-check.md) (scorer, after the fix: 23/30) · [hand-check.md](hand-check.md) (manual reading) · run log and database snapshots in `docs/evidence/stage-0/`. Jobs: 04150 `e29b39ef`, 04101–04140 one per claim, then batches `92cf4f5f`, `6ba0f977`, `afecf010`.
## Findings
| Issue | What we did |
| --- | --- |
| The naive skill gives no method, so MAI wanders: dossier read twice, SharePoint folders browsed and binary files downloaded, 7 searches for an inspection report the claim doesn't need (04150 smoke) | Expected at stage 0: this is the efficiency headroom for stage 2 (skill) and stage 4 (RFT). Track calls and minutes per claim |
| **Echoed hand-ins:** on 5 runs MAI handed in the user's question as its answer (4 claims lost; 04139 recovered on re-invocation). The rubrics score these ~0.1 | A hand-in failure, not reasoning. Stage 2's skill guidance should address how to hand in; keep tracking it per stage |
| **Authority trap missed:** both goodwill claims declined instead of escalated; the generated rubrics scored them 0.85 and 1.0 | Hand-written rubric 5 (stage 1) checks escalation |
| 04141 said the rate card was "not available" (it is, at rank 1 in search) and recorded approve with payable 0 | Search guidance in stage 2 (folder map, title words) |
| The generated rubrics overrate: 0.744 rubric vs 77% correct, with wrong answers at 0.85–1.0 and correct-but-terse answers below 0.6 | Stage 1 replaces them |
| The scorer misread 7 correct answers (labour sub-line taken as payable, a negated instrument, bold "Covered") | **Fixed (2026-10-08):** the scorer now gives 23/30 on its own, matching the hand check; echoes and inability statements are scored wrong, not unreadable. Tests 52/52 |
| One claim per job pays ~9 min of platform start-up + ~2.5 min grading; agent execution is only ~7 min | Batches of 5 per job: 5 claims in 20–27 min, no stalls |
