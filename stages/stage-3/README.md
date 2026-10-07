# Stage 3: small model, with research split into its own skill

**Status:** ⬜ ready to run in `wce-main`. Configuration trialled on 6 runs in `wce-dev` (below).

## The change (against stage 2)
| | Stage 2 | **Stage 3** |
| --- | --- | --- |
| Model | GPT-5.6-Sol | **MAI-CODE-5b** `dev-ct-mai-code-mp` (to be tuned later as `mai-code-1-flash`) |
| Skills | one: `warranty-assistant` | **two:** [library-research.md](library-research.md) (new) + [warranty-assistant.md](warranty-assistant.md) (new description and instructions) |

Rubrics ([warranty-assistant.rubrics.json](warranty-assistant.rubrics.json), the same pinned generated set) and samples ([samples.jsonl](samples.jsonl), the same 30) are unchanged. `library-research` has no rubrics yet.

⚠️ **Two things change at once.** The split was needed for the small model to finish heavy claims at all (see Findings), so the model and the skill design move together. GPT-5.6-Sol hasn't been measured on the split design; by user decision, that comes later.

## How it works
- **One request; the platform orchestrates.** A top-level agent reads both skill descriptions. `library-research` says *"Use this first…"*; `warranty-assistant` says it *"expects the facts… gathered first with library-research"*. So the platform calls research first, then adjudication. Skills can't call each other, so only the descriptions steer the order.
- **Each skill runs as a separate sub-agent with its own context window.** Research does the document searching and returns only the passages, figures and rows asked for. Adjudication reads the claim system, works from those facts, records a draft and hands in the answer.
- **Every search is limited to one folder** (`path:"<library>/<folder>"` in the query). The folder map is the **`## Library folders`** section at the end of both skill files: **the one place to edit** if the library's folders change. New documents filed in an existing folder need no skill change.

## Apply (wce-main)
```powershell
$e='598fd1b0-36f1-402f-ba36-aa00c8a67cc4'; $sk='cf00d339-5217-4cd1-b390-cc0d911735da'; $d='stages\stage-3'
frontier-tuning skills create --file $d\library-research.md --env-id $e -o json          # generateRubrics: false; note its id
$f = Get-Content $d\warranty-assistant.md -Raw
$desc = [regex]::Match($f,'(?m)^description: (.*)$').Groups[1].Value.Trim()
$body = ($f -split '## Instructions',2)[1].Trim()
frontier-tuning skills update $sk --description $desc --instructions $body --env-id $e    # partial update; rubrics untouched
frontier-tuning skills get $sk --env-id $e -o json                                      # check: 5 rubrics, source auto_generated
```

## Run
```powershell
# pre-flight
az sql server show -g az-sqldb-common-rg -n az-sqldb-common --query publicNetworkAccess   # Enabled (switched off daily)
.\scripts\sql-run.ps1 -File scripts\db-baseline.sql                                       # 0 0 0 0 (needs your IP in the SQL firewall)
Invoke-WebRequest https://contoso-service-mcp.whitemoss-1ee70859.southindia.azurecontainerapps.io/healthz -UseBasicParsing
frontier-tuning tools available --env-id $e -o json                                       # record the count
# smoke test: one sample. Check both skills ran (Skills[] in the execution) before going on
frontier-tuning evaluate start --skill-id $sk --limit 1 --base-model dev-ct-mai-code-mp --strategy simple --env-id $e -o json
# three batches of 10 (--sample-id ×10 each); after each: results, score_ground_truth.py, snapshot, reset
frontier-tuning evaluate start --sample-id <id> ... --base-model dev-ct-mai-code-mp --strategy simple --env-id $e -o json
```
Report **three numbers**: the rubric score, ground-truth correctness, and the **hand-in rejection rate** (runs whose grader notes say the hand-in was rejected). Stop before any tuning if rejections are frequent.

## Results
⬜ Not yet run in wce-main.

**Trial in wce-dev, 2026-10-06** (`chat`, not an evaluation). The files are the same as here, except that the 04103 and 04189 runs and one 04185 run still had the hand-in line removed later (see Findings):

| Claim | Kind | Tool output | Decision | Ground truth |
| --- | --- | --- | --- | --- |
| 04185 ×4 | exclusion, heavy | 57–161k | approve ₹199,175 TSB, 4/4 | ✅ |
| 04103 | covered-simple | 116k | approve ₹19,150 | ✅ |
| 04189 | repair warranty | 67k | approve ₹69,575 RW | ✅ |

No context overflow. Remaining misses were the model's own, and the rubrics scored them: a wrong first draft amount, a duplicate draft, a missing draft.

## Findings: why stage 3 looks like this
| Issue we hit | What we did |
| --- | --- |
| **GPT-5.4-Mini** (tried first): its answers often never reached the user. The platform's finish tool rejected the hand-in (22 of 28), and it often skipped the documents (17 of 28) | Skill guidance fixed the research order but not the hand-ins. Reported to the platform team ([note](../../docs/evidence/platform-issue-finish-rejection.md)). Switched to MAI (user decision) |
| **MAI ran out of context** (`ContextLength`) on heavy claims, although its decisions were right. Each search returns large document extracts (~18k characters), and the same documents (policy, review decks) come back for different queries, about half of every context. GPT-5.6-Sol copes because its window is larger | **Split the skill:** research and adjudication run as separate sub-agents, each with its own window. **Scope each search to a folder:** heaviest claim 610k → 57k characters of tool output |
| Asked to work out folder names itself, MAI invented them (`05-Policies`, `02-RateCards`) | The folder map is given in the skill's `## Library folders` section |
| Queries stuffed with claim identifiers, or "rate card" (a word the workbooks never use), found nothing | The research skill searches with the references the claim system returns (agreement ref, bulletin code, operation code, part number) plus the kind of document |
| MAI's full answer was rejected at hand-in. It then handed in test lines (*"Test [cite:claim]"*), the platform re-ran the skill, and duplicate drafts were written | Removed the skill line *"leave the hand-in's sources list empty"*: 0 rejections in 3 runs. Not proven, so the rejection rate is tracked |
| 04189 was declined: the earlier warranty claim it rests on didn't exist in the claim system | **World v2.3:** prior claims seeded as `Paid`; `gen_db.py` refuses dangling references |
| Rubrics still don't check correctness, and the research skill has none | Rubrics v2 drafted ([rubrics-v2-draft.md](../rubrics-v2-draft.md)) for a later stage, before RFT |

Full trial record: [archive/stages/research-skill-wce-dev](../../archive/stages/research-skill-wce-dev/README.md).
