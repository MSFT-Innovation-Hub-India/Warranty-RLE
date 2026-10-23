# Documentation

Read in order the first time. After that, jump to what you need.

| # | Document | Answers |
| --- | --- | --- |
| 1 | [Scenario](01-scenario.md) | What the agent does, where the facts live, why it's hard, how a run is graded |
| 2 | [World configuration](02-world-configuration.md) | Architecture (CLI → REST service, public vs legacy connection; platform → MCP server), environments, knowledge sources, tools (incl. the MCP server), skill, rubrics, samples, models: what is configured and where it lives |
| 3 | [Claim execution flow](03-claim-execution-flow.md) | How the agent should work through a claim, step by step and tool by tool, with a worked example and where each trap bites |
| 4 | [Hill-climb method](04-hill-climb-method.md) | The stages, why in this order, and what skills, rubrics, inference strategy and RFT can and cannot fix |
| 5 | [Operations runbook](05-operations.md) | Pre-flight checks, running an evaluation, scoring, the database reset, checking long jobs |
| 6 | [Platform issues](06-platform-issues.md) | Every platform error, with the details the platform team needs |
| 7 | [Journey and demo guide](07-journey-and-demo-guide.md) | Business-friendly hill-climb story, what the platform did, Streamlit demo, copy-paste CLI commands, multiple-skill routing and the enterprise learning-loop value proposition |

Also: the stages are in [climb/](../climb/README.md); the scripts in [scripts/](../scripts/README.md); how the world is built in [world-builder/](../world-builder/README.md); the first attempt in [archive/attempt-1/](../archive/attempt-1/README.md).

The Frontier Tuning CLI documentation: <https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1>.
