# Documentation

Read in order. The first three are specific to this scenario; the rest are
cross-cutting references that apply to any Frontier Tuning world.

| # | Document | What it covers |
| --- | --- | --- |
| 03 | [Scenario design](03-scenario-design.md) | Why this world exists, the entity model, the traps, and how ground truth is derived |
| 04 | [Walkthrough](04-walkthrough.md) | Build the corpus, stand up the MCP server, provision the world |
| 05 | [Hill-climb runbook](05-hill-climb-runbook.md) | Baseline, diagnose, tune, re-measure |

## Cross-cutting references

| Document | What it covers |
| --- | --- |
| [rubric-design.md](rubric-design.md) | What a rubric is, why it is required, and why rubrics come before skills |
| [rubric-patterns.md](rubric-patterns.md) | Grading things a rubric cannot see directly — multi-source joins |
| [rubric-defects.md](rubric-defects.md) | Rubric defects found in practice, and whether the platform can catch them |
| [troubleshooting.md](troubleshooting.md) | Retrieval failures, upload routes, indexing lag, reading the JSON |
| [CLI-REFERENCE.md](CLI-REFERENCE.md) | Every CLI command, its parameters, output fields, and known traps |

## A note on numbering

Documents start at 03 because 01 and 02 belong to an earlier exploration of the
upstream reference scenario (contract renewal), which lives in a separate
repository. The numbering is kept so cross-references in the cross-cutting
documents still make sense.

Where those documents refer to *the contract-renewal world*, *probe sweep* or
*guide 01*, they mean that earlier work. Nothing here depends on it.
