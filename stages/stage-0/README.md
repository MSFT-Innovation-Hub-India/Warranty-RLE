# Stage 0 — The naive baseline

**Status:** ⏳ prepared, not run. The samples file and results are still to come.

**Purpose.** Build the way most teams start, with one broad skill and
platform-generated rubrics, and measure it honestly. The MCP server is **off**,
so database facts are unreachable. Stage 1 switches it on.

## The one change

None; this is the baseline.

## World state for this stage

| | |
| --- | --- |
| World | `wce-main` `598fd1b0-36f1-402f-ba36-aa00c8a67cc4` |
| Model · strategy | `prod-gpt-56-reasoning-sol` (GPT-5.6-Sol) · `simple` |
| Knowledge | SharePoint `Warranty Operations` + 3 Teams channels ([world/env.md](../../world/env.md)) |
| MCP server | `contoso-service` `1c171d49-7f85-4997-8126-ae20829a4dbf`: **disabled** |
| Other tool sources | SharePoint, OneDrive, Teams on; Email, Calendar, Word, M365Chat, fabriciq off |
| Skill | `warranty-assistant`: main `cf00d339-5217-4cd1-b390-cc0d911735da` |
| Rubrics | 5 rubrics / 28 items, platform-generated on dev on 2026-10-03 and **pinned** |
| Samples | 8 easiest eval prompts (covered-simple, declined-simple, precedence): *to be selected* |

## Files

| File | What it is |
| --- | --- |
| [warranty-assistant.md](warranty-assistant.md) | The skill: the business job and sources, with no trap rules. `generateRubrics: false` (see its header comment) |
| [warranty-assistant.rubrics.json](warranty-assistant.rubrics.json) | The pinned rubric set, verbatim from the platform's generation |
| `stage0.jsonl` | *to come*: the 8 prompts |

## Apply (to a fresh world)

```powershell
$world = '<world-id>'
frontier-tuning skills create --file stages\stage-0\warranty-assistant.md --env-id $world -o json   # note the skill id
# apply the pinned rubrics: put the JSON array into the skill payload's "Rubrics" field
$raw  = frontier-tuning skills get <skill-id> --env-id $world -o json | Out-String
$s    = $raw.Substring($raw.IndexOf('{')) | ConvertFrom-Json
$s.Rubrics = Get-Content stages\stage-0\warranty-assistant.rubrics.json -Raw | ConvertFrom-Json
$s | ConvertTo-Json -Depth 12 | Set-Content "$env:TEMP\payload.json" -Encoding utf8
frontier-tuning skills update <skill-id> --file "$env:TEMP\payload.json" --env-id $world
frontier-tuning tools disable <mcp-server-id> --env-id $world                                        # stage 0: MCP off
```

## Run

*To come.* Upload `stage0.jsonl` as Evaluation samples for the skill; run
`evaluate start` with the model and strategy above; score each answer against
`GROUND-TRUTH.md`.

## Results

*To come.* The rubric score (overall and per rubric), correctness against
`GROUND-TRUTH.md`, the evaluation job ID, and the gate decision.
