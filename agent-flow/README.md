# Agent execution flow

How the warranty agent reasons through a claim, written for a business reader.

| Document | What it explains |
| --- | --- |
| [01-claim-execution-flow.md](01-claim-execution-flow.md) | The overall flow: sources, what the skill does and does not say, the step-by-step path, tool-call budget, a worked claim, where each trap bites |
| Per-question paths (next) | One path per prompt in [samples.jsonl](../stages/stage-0/samples.jsonl): which tools to call, what to conclude from each result, the next call, the recommendation |
