# Configuration applied in this stage

What the platform held while this stage ran. A new stage copies this folder and changes one file.

| File | What it is | Applied with |
| --- | --- | --- |
| `skill.md` | The skill's description and instructions (text after `## Instructions`) | `skills update <skill-id> --description … --instructions …` |
| `rubrics.json` | The six rubrics, exactly as sent to the platform | `skills update <skill-id> --file <payload>` (see [docs/05](../../../docs/05-operations.md)) |
| `rubrics.md` | The same rubrics, readable | — |
| `eval-samples.jsonl` | The 30 evaluation prompts, one `{"Prompt": …}` per line | `samples upload … --type Evaluation` (only when rubrics change) |
| `eval-sample-ids.json` | Claim number → platform sample ID for those 30. Needed because `evaluate start` takes sample IDs, while the answer key is by claim number | Written from `samples list` after upload |
| `training-samples.jsonl` / `training-sample-ids.json` | The 60 training prompts and their IDs. Used only by refinement and tuning | `samples upload … --type Training` |

Samples capture the rubrics at upload. If `rubrics.json` changes, re-upload both sample sets and rewrite both ID files.
