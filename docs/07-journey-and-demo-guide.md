# Frontier Tuning: our journey, demo and business value

**Presenter guide | 23 October 2026**

Use sections 1-4 to tell the story, section 5 to demonstrate it, and section 6
for CLI examples. Sections 7-8 explain the platform's broader value.

**Evidence labels:** 🖥️ measured in our tenant · 📄 documented platform capability ·
💭 interpretation / positioning · 🔬 not yet demonstrated here.

## 1. The story in a minute

> We gave an agent a realistic warranty job: read company policy and repair
> evidence, decide what is covered, calculate the payable amount, and record
> the next action for a human reviewer.
>
> We first measured a strong model rather than assuming the task was ready for
> a smaller one. It got 29 of 30 evaluation claims right. But we discovered
> that an incorrect answer could still earn a very high quality score.
>
> So we improved how success was judged before improving the instructions.
> Then one targeted instruction change reduced claims with no draft recorded
> from 11 to 6, while correctness held at 59 of 60 development claims.
>
> Frontier Tuning gave us a shared place to run the agent, grade its work,
> manage instructions and quality criteria, and test changes. The smaller-model
> and reinforcement-training steps remain blocked; we have not proved a
> cheaper tuned model yet.

**The message:** this is a measured improvement process, not a claim that
fine-tuning automatically makes an agent better.

## 2. What we built

Everything is synthetic: fictional customers, assets, claims and money.
The agent uses three kinds of business evidence:

| Evidence | Why it matters |
| --- | --- |
| SharePoint policies, bulletins, rate cards and inspection reports | What the warranty rules and repair evidence actually say |
| Teams discussions and announcements | Relevant operational context, checked against the authoritative documents |
| A claim system exposed through MCP tools | Asset facts and the ability to record draft decisions, evidence requests or escalations |

The model prepares a decision for a person. It does not make a payment.
The claim-system draft writes do persist, so we snapshot and reset between runs.

Three simple terms:

- **Skill:** the agent's job instructions.
- **Rubrics:** the grader's checklists for judging the work.
- **Learning environment:** the shared home for skills, rubrics, examples,
  knowledge, tools and improvement runs. The CLI calls this an RLE; current
  guidance also uses Agent Learning Environment, or ALE.

## 3. The hill climb so far

🖥️ This is **attempt 2**, restarted on 10 October. We kept the first attempt's
lessons rather than treating its unsuccessful experiments as improvements.

| Step | What happened | Result and learning |
| --- | --- | --- |
| Earlier attempt: test generation and refinement | Tried platform-generated rubrics and automated instruction refinement | Generated checks missed important business mistakes. One refined instruction copied grader wording and was rejected. Proposals need review. |
| **Stage 0: establish a reference** | GPT-5.6-Sol on 30 held-out evaluation claims | **29/30 correct; rubric 0.956.** One wrong calculation still scored 0.96: a good-looking answer is not necessarily right. |
| **Stage 1: find weaknesses** | Same skill/model on 60 separate Training claims used for development | **57/60 correct; rubric 0.934.** A missed goodwill escalation received full marks on the relevant rubric. Fix the judge before optimising against its scores. |
| **Stage 2: improve the judge** | Revised two rubric checklists, not the skill or model | **59/60 correct; rubric 0.940.** Missing draft actions were penalised more appropriately. Do not attribute the correctness difference to rubrics: they are not shown to the answering model. |
| **Stage 2b: test the checks** | Used deliberate wrong-answer probes and corrected an irrelevant scoring condition | An unrecorded escalation's Authority score fell from **1.00 to 0.33**; mispricing scored **0.60** on Valuation. One goodwill-decline case still escaped the checks. This was not a full accuracy benchmark. |
| **Stage 3: improve the instruction** | Added one clear requirement to record a draft for claim-outcome questions | **59/60 correct; rubric 0.942.** Claim questions without a draft fell **11 → 6**. Better operational follow-through, with no observed loss in correctness on this run. |
| **Stage 4: measure the small model** | Tried MAI-CODE-5b | **No valid baseline.** Tool-access failures and stalled/incomplete executions blocked measurement. An infrastructure failure is not evidence of poor reasoning. |
| **Stage 5: reinforcement fine-tuning** | Intended next step after a valid small-model baseline | **Not completed in this attempt.** Tuning's claim-tool limitation remains a blocker. No demonstrated tuned-model gain or cost saving. |

Sources: [scoreboard](../climb/README.md), [stage 0](../climb/stage-0/README.md),
[stage 1](../climb/stage-1/README.md), [stage 2](../climb/stage-2/README.md),
[stage 2b](../climb/stage-2b/README.md), [stage 3](../climb/stage-3/README.md),
and [small-model attempts](../climb/stage-4/README.md).

**How to read the numbers:** Stage 0 used 30 Evaluation claims; stages 1-3 used
60 Training claims. They are not the same test set. Stage 0 also used evaluation
jobs, while later stages used direct executions after tool-access problems.
Changed rubrics change the scoring instrument, so those rubric averages are
not a single like-for-like improvement curve.

### The later TreeSearch demo

🖥️ Outside the climb scoreboard, the 22 October demo correctly approved
**C-2026-04101 for INR 69,575**. Decision, governing instrument and payable all
passed the independent answer-key check; the mean scored rubric was **1.000**.
It took **5m49s** and created **five drafts**.

It used the deployed **Stage 3 skill**, reported as version **11**, and the
Stage 2b/3 rubrics. It was **one claim**, not proof that TreeSearch beats Simple.
The export shows tool activity, but not an explicit tree of candidate branches,
their scores and the final selection reason.

## 4. What the platform did, and what we did

Do not describe every improvement as "the platform refined it automatically."

| Activity | What actually happened | Frontier Tuning's contribution |
| --- | --- | --- |
| Initial skill | We authored the business brief | Stored and executed it as a reusable skill |
| Rubric generation | Used in attempt 1; tried again on a development copy during attempt 2 | Generated checklists from the skill. We reviewed them; they were not the final adopted criteria. |
| Automated skill refinement | Tried in attempt 1; the proposal was rejected | Produced a candidate rewrite. Acceptance was not automatic. |
| Adopted rubric improvements | We edited the checklists from observed grading errors | Applied the changes through `rubrics update`; its grader then evaluated subsequent answers against them |
| Adopted Stage 3 skill improvement | We authored a targeted one-line change | Applied it through `skills update --prompt` and executed the updated skill |
| Execution and grading | The platform ran queries against connected tools/knowledge and graded results | Native executions, rubric results, run IDs, diagnostics and usage counters |
| Inference search | We selected Simple or TreeSearch; BestOfN is available for comparison | The service provides the execution strategies; we did not implement search in Streamlit |
| Factual accuracy check | Our deterministic Python scorer checked the synthetic answer key | **Our additional safeguard**, not a built-in ground-truth test supplied by Frontier Tuning |
| Demo UI and evidence management | We built a local Streamlit CLI wrapper and repository records | **Our tooling**, not a native Frontier Tuning web portal |
| Reinforcement fine-tuning | Still blocked in this attempt | A documented platform capability, not an improvement demonstrated by this climb |

Provenance: [skill and rubric history](04-hill-climb-method.md#6-where-the-skill-and-rubrics-came-from).

**The lesson:** the platform supports the improvement loop; business owners
still define policy, review proposals, check outcomes and approve changes.

## 5. Run and present the Streamlit demo

### Start the app

In PowerShell, using the full local paths:

```powershell
Set-Location 'C:\Users\sansri\contoso-warranty-rle'
& 'C:\Users\sansri\contoso-warranty-rle\.venv\Scripts\python.exe' -m streamlit run 'C:\Users\sansri\contoso-warranty-rle\ui\app.py' --server.address 127.0.0.1 --server.port 8502 --browser.gatherUsageStats false
```

Open **<http://127.0.0.1:8502>**. If it is already running there, use the existing
app rather than starting a second server.

If dependencies are missing, install them once:

```powershell
Set-Location 'C:\Users\sansri\contoso-warranty-rle'
.\.venv\Scripts\python.exe -m pip install -r ui\requirements.txt
```

Existing CLI sign-in and SQL connectivity must already be ready. This app runs
under your local signed-in identity: keep it on localhost.

### A simple five-minute walkthrough

| Show | Say |
| --- | --- |
| **Live skill & rubrics** | "Here is the deployed job instruction, and separately the standards the grader uses." |
| Environment ID and skill ID | "This is a live platform configuration, not an instruction file being read from a stage folder." |
| **Saved runs & results** | "We can reopen an existing execution without paying to execute it again." |
| Existing TreeSearch demo `c9fffec9-426a-4eca-93b6-2b0616acd810` | "The answer explains the coverage, sources, amount and recorded draft." |
| **Check ground-truth accuracy** | "We also check the actual decision against our answer key, not just how convincing it sounds." |
| **Raw execution JSON** and **Usage and tool activity** | "The formatted view comes from this returned evidence. Missing branch details remain missing." |
| **Execute** | "We can choose Simple, TreeSearch or BestOfN without building those strategies ourselves." |

For a **new** live run: check no other job is active, confirm SQL baseline
`0 0 0 0`, agree the spend and writes, then click **Execute once**. Open
**Saved runs & results**, select that new run, and **Refresh execution by ID**.
Do not click Execute again to retrieve results.

TreeSearch's form defaults to an explicit **0.95** cutoff; BestOfN defaults to
explicit **N=4**. These are demo UI settings, not proven optimal settings.
Snapshot/reset through **Claim database** only after all activity has ended.
More detail: [UI guide](../ui/README.md).

## 6. Copy-paste CLI examples

These are **examples, not a batch script to run from top to bottom**.
Syntax was checked against installed **CLI 1.0.14** on 23 October.
Use the stable [v1 reference](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1);
installed `--help` decides what this machine supports. No upgrade is required
for this guide.

### A. Set the known parameters

These variables affect only this PowerShell session:

```powershell
Set-Location 'C:\Users\sansri\contoso-warranty-rle'
$e = '598fd1b0-36f1-402f-ba36-aa00c8a67cc4'
$sid = 'cf00d339-5217-4cd1-b390-cc0d911735da'
$model = 'prod-gpt-56-reasoning-sol'
$demo = 'c9fffec9-426a-4eca-93b6-2b0616acd810'
```

### B. Inspect the environment, skills, rubrics and examples — read-only

```powershell
frontier-tuning environments get $e -o json
frontier-tuning -e $e skills list -o json
frontier-tuning -e $e skills get $sid --show-rubrics -o json
frontier-tuning -e $e rubrics list --skill-id $sid -o json
frontier-tuning -e $e models list -o json
frontier-tuning -e $e samples list --limit 100 -o json
frontier-tuning -e $e executions list --limit 10 -o json
frontier-tuning -e $e evaluate list --limit 10 -o json
frontier-tuning -e $e tune list --limit 10 -o json
```

The lists limited to ten are convenient for browsing, **not sufficient proof
that no older job is active**. The UI performs fuller preflight checks.

### C. Reopen the existing demo and check accuracy — no new model execution

```powershell
New-Item -ItemType Directory -Force '.local\presenter-demo' | Out-Null
frontier-tuning -e $e executions get $demo -o json-legacy | Tee-Object -FilePath '.local\presenter-demo\execution.json'
```

Only after the read succeeds and returns the intended completed execution:

```powershell
.\.venv\Scripts\python.exe scripts\score_ground_truth.py '.local\presenter-demo\execution.json' --out '.local\presenter-demo'
```

`json-legacy` is still JSON; it retains historical metadata that the simplified
formatter can omit. The final answer inside the JSON is Markdown text.

### D. Execute one strategy — paid and capable of business writes

**Choose ONE block.** Obtain approval, use the preflight/database process in
section 5, and start each trial from the same clean state. Never reset while a
run is active. These commands submit once without `--wait`; retain the returned
execution ID and read it afterward.

**Simple**

```powershell
frontier-tuning -e $e executions run --query 'Adjudicate claim C-2026-04101.' --model $model --strategy Simple -o json-legacy
```

**TreeSearch, with an explicit cutoff**

```powershell
frontier-tuning -e $e executions run --query 'Adjudicate claim C-2026-04101.' --model $model --strategy TreeSearch --early-stop-score 0.95 -o json-legacy
```

**BestOfN, with an explicit candidate count**

```powershell
frontier-tuning -e $e executions run --query 'Adjudicate claim C-2026-04101.' --model $model --strategy BestOfN --best-of-n 4 -o json-legacy
```

Read the execution you just submitted, not the old `$demo`:

```powershell
$executionId = Read-Host 'Paste the execution ID returned by your new run'
frontier-tuning -e $e executions get $executionId -o json-legacy
```

A timeout or missing response is **not** permission to submit again.
Use `executions list`/`get` to reconcile it first.

### E. Learning-lifecycle examples — optional, not the live-demo sequence

The examples below show additional platform capabilities. They **were not run
to write this guide**. Writes and paid jobs require separate approval. Keep
the main climb pinned; use the existing development environment for experiments.
Development tools can still reach shared business systems: it is not a
guaranteed simulation sandbox.

**Create a separate demonstration skill from the Stage 3 instructions.**
This creates a skill, not an environment, and does not change CLI defaults.

```powershell
$dev = '6bec3bf9-0222-4285-8a5b-214867ac42cc'
$demoName = 'warranty-presenter-' + (Get-Date -Format 'yyyyMMddHHmmss')
$instructions = ((Get-Content 'climb\stage-3\config\skill.md' -Raw) -split '## Instructions', 2)[1].Trim()
frontier-tuning -e $dev skills create --name $demoName --description 'Demonstration copy: adjudicate warranty claims from company evidence and record a draft for human review.' --prompt $instructions --rubric-title 'Evidence-based decision' --success-criteria 'Explains the decision using the relevant company records.' -o json
$devSkill = Read-Host 'Paste the new demonstration skill ID'
frontier-tuning -e $dev skills get $devSkill --show-rubrics -o json
```

The one starter criterion above is for illustrating creation, **not** a
replacement for the climb's six reviewed rubrics. Same-name skill creation can
update an existing skill; the timestamped name reduces accidental collisions.
Adding a similar skill to an environment can also affect routing there.

**Alternatively, generate a local definition template.** This does not create
a platform skill or write tailored instructions; fill in its placeholders first.

```powershell
New-Item -ItemType Directory -Force '.local\presenter-demo' | Out-Null
frontier-tuning skills init-md --out-file '.local\presenter-demo\morning-brief.md'
```

**Generate rubrics from the demonstration skill — paid, saves immediately.**
Review before using them as a reward.

```powershell
frontier-tuning -e $dev skills generate-rubrics $devSkill --yes -o json
frontier-tuning -e $dev skills get $devSkill --show-rubrics -o json
```

**Apply an exact instruction edit**, as we did for Stage 3, rather than starting
a generation job. This example restores the pinned Stage 3 text on the copy:

```powershell
frontier-tuning -e $dev skills update $devSkill --prompt $instructions -o json
```

**Update a rubric**, as we did in stages 2/2b. Supply the FULL reviewed checklist:
repeating `--checklist-item` replaces that rubric's whole checklist, not just one
item. This example copies a complete pinned checklist onto the corresponding
rubric of the demonstration skill.

```powershell
$valuation = Get-Content 'climb\stage-3\config\rubrics.json' -Raw | ConvertFrom-Json | Where-Object { $_.RubricName -eq 'Valuation accuracy' }
$rubricId = Read-Host 'Paste the Valuation rubric ID from the development skill; stop if it has no corresponding rubric'
$rubricArgs = @('-e', $dev, 'rubrics', 'update', $rubricId, '--skill-id', $devSkill)
foreach ($item in $valuation.ChecklistItems) { $rubricArgs += @('--checklist-item', $item) }
$rubricArgs += @('-o', 'json')
frontier-tuning @rubricArgs
frontier-tuning -e $dev skills get $devSkill --show-rubrics -o json
```

**Upload development Training examples once**, then inspect their actual IDs.
Do not upload the 30 held-out Evaluation claims as Training.

```powershell
frontier-tuning -e $dev samples upload 'climb\stage-0\config\training-samples.jsonl' --skill-id $devSkill --type Training -o json
frontier-tuning -e $dev samples list -o json
$trainingSample = Read-Host 'Paste one Training sample ID belonging to the demonstration skill'
```

**Request an instruction-only refinement — paid proposal.**
The current climb's adopted Stage 3 edit was manual; this illustrates the
platform alternative, not a step we claim to have adopted.

```powershell
frontier-tuning -e $dev skills refine start --skill-id $devSkill --mode instruction --sample-id $trainingSample -o json
$refinementId = Read-Host 'Paste the returned refinement ID'
frontier-tuning -e $dev skills refine status $refinementId -o json
frontier-tuning -e $dev skills refine detail $refinementId -o json
```

For a **separate rubric-only proposal**, after separate approval:

```powershell
frontier-tuning -e $dev skills refine start --skill-id $devSkill --mode rubrics --sample-id $trainingSample -o json
```

Each start returns a different ID. Read that run's status/detail. After it
completes, review the proposal and obtain approval before applying that exact ID:

```powershell
$approvedRefinementId = Read-Host 'Paste the completed, reviewed refinement ID approved for application'
frontier-tuning -e $dev skills refine apply $approvedRefinementId --skill-id $devSkill --yes -o json
frontier-tuning -e $dev skills get $devSkill --show-rubrics -o json
```

Apply uses the mode chosen at start; it is not a selective merge. Review skill
proposals with our skill checker before adopting them in the climb. Changed
rubrics require a new baseline.

**Run an environment-quality assessment — separate approval for LLM-backed checks.**
This checks configuration/readiness, not warranty decision accuracy.

```powershell
frontier-tuning -e $dev health quality check -o json
```

**Evaluate one development example — paid.** Use the same reviewed configuration
and reset discipline. Our tenant's evaluation-job claim-tool issue remains
recorded in [P11](06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error);
this is a capability example, not a promise that the blocked route now works.

```powershell
frontier-tuning -e $dev evaluate start --base-model $model --skill-id $devSkill --sample-id $trainingSample --strategy Simple -o json
$evaluationId = Read-Host 'Paste the returned evaluation job ID'
frontier-tuning -e $dev evaluate status $evaluationId -o json
frontier-tuning -e $dev evaluate results $evaluationId --samples -o json
frontier-tuning -e $dev evaluate diagnostics $evaluationId -o json
```

To compare **two already completed, comparable evaluation jobs**:

```powershell
$baselineEvaluation = Read-Host 'Paste the baseline evaluation job ID'
$candidateEvaluation = Read-Host 'Paste the candidate evaluation job ID'
frontier-tuning -e $dev evaluate compare $baselineEvaluation $candidateEvaluation -o json
```

Use identical cases and rubric definitions; verify actual grading coverage.
Do not compare the current stage scores as if their rubric versions matched.

**Train a model — future capability, NOT recommended while our tool blocker is open.**
Training uses the environment's eligible Training samples, not just
`$trainingSample`. Inspect all of them and agree the full scope first. The
documented minimum is 11, not a guarantee that the data is sufficient.

```powershell
frontier-tuning -e $dev models list -o json
frontier-tuning -e $dev samples list -o json
```

Only after the blocker is resolved, the catalog confirms this base model,
the complete training scope is approved, and spend is agreed:

```powershell
frontier-tuning -e $dev tune start --base-model mai-code-1-flash --new-model ('warranty-presenter-' + (Get-Date -Format 'yyyyMMddHHmmss')) -o json
$tuningId = Read-Host 'Paste the returned tuning job ID'
frontier-tuning -e $dev tune status $tuningId -o json
frontier-tuning -e $dev tune diagnostics $tuningId -o json
frontier-tuning -e $dev models list --fine-tuned -o json
```

Do not equate a finished training job with a deployed or improved model. Confirm
deployment/readiness and evaluate the actual output model on untouched cases.

## 7. Multiple skills and platform-native orchestration

📄 **Yes: an environment can contain multiple skills.** Each skill has its own
job instructions and associated grading criteria. For example, one environment
could contain warranty adjudication, asset-coverage enquiries and
service-partner enquiries as separate skills.

Those examples describe a possible design, **not three skills we deployed**.
Our warranty demo uses one broad `warranty-assistant` skill that handles those
question types.

### What happens when a user asks a question?

```text
User's prompt
    → Selected environment
    → Platform routes the query to a relevant enabled skill
    → Agent follows its instructions and uses available knowledge/tools
    → Platform returns the answer and available grading/execution evidence
```

The CLI's `executions run` does not require a skill ID. The service performs
query routing, and the returned skill results tell us which skill was actually
used. Clear names/descriptions and distinct responsibilities help make the
intended choice understandable; they do not guarantee perfect routing.

| Provided by the platform | Still our responsibility |
| --- | --- |
| Skill selection/routing for native executions | Define sensible skills and test ambiguous prompts |
| Agent runtime and connected-tool invocation | Provide working tools, data access and business permissions |
| Simple, BestOfN and TreeSearch strategies | Choose the strategy and agree its cost |
| Grading against attached rubrics | Make the criteria correct and validate real outcomes |
| Refinement and training job lifecycle | Review/apply changes and remeasure before accepting them |

🖥️ Our demo confirms routing to `warranty-assistant`, model/tool execution and
returned grading. 🔬 It does **not** benchmark routing among competing skills.
V1 native execution does not expose an exact-skill selector; inspecting a skill
in our UI does not force the service to use it. Evaluation jobs offer explicit
skill/sample scoping, which is a different operation.

**Do not overstate "orchestration":** this native routing/runtime is useful
platform orchestration. It is not evidence of an arbitrary workflow graph,
guaranteed multi-skill chaining, or a team of independently collaborating
agents. Those behaviours need specific documented support and their own tests.

## 8. The business value: a closed enterprise learning loop

📄 The [Frontier Tuning guidance](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1/agent-guidance/GUIDE.html)
brings the following resources and operations together:

```text
Enterprise task + knowledge + tools
    → reusable skills + examples + business success criteria
    → execute and evaluate
    → inspect failures
    → improve instructions OR improve grading OR change inference strategy
    → where justified, train a model
    → evaluate again and keep only changes that earn their place
```

💭 **The differentiator to emphasise is the integrated, enterprise-task learning
environment—not a claim that prompts, evaluations or fine-tuning are new.**

| Value | Business explanation |
| --- | --- |
| A reusable definition of the job | Instructions, evidence sources, tools and quality criteria stay together rather than living in disconnected experiments. |
| Business standards become actionable | Rubrics can judge executions and provide the reward for reinforcement fine-tuning. Getting those standards right matters. |
| More than one improvement lever | A team can fix instructions or grading before paying to change model weights; it can also test additional inference search. |
| Enterprise context is part of the task | The loop works around connected organisational knowledge and tools, not only a spreadsheet of question/answer pairs. |
| Platform-managed execution and routing | The local app is a thin interface; we did not build the agent harness, routing or search strategies ourselves. |
| Repeatable evidence | Saved resources, run IDs, scores, diagnostics and model outputs make changes inspectable. Our repository adds independent accuracy checks and stage records. |
| A path to model specialisation | A smaller model can potentially learn better task behaviour; that is the intended destination, not a result we have proved here. |

**"Closed loop" does not mean unattended self-improvement.** In the documented
workflow, people still choose examples, author/review criteria, approve writes
and spend, apply accepted proposals, and decide whether measured results justify
keeping a change. The service does not automatically turn every production
interaction into an approved training example.

### How to position it alongside Microsoft Foundry

📄 Microsoft Foundry already provides agents, tools, tracing, evaluations,
enterprise governance and model fine-tuning. Its documented training options
include supervised fine-tuning, preference optimisation and reinforcement
fine-tuning for supported models, plus interactive training in preview.
It would be inaccurate to say Foundry only hosts models or has no learning loop.

💭 The positioning here is **the Microsoft 365, tenant-scoped integration of the
business skill, its knowledge/tools, its grading criteria, and the operations
for measuring and improving it**. Foundry is a broader Azure agent/model
development platform; Frontier Tuning packages a task-centred improvement
workflow around these shared learning-environment resources. The difference
to demonstrate is the amount of workflow the service provides, not an assertion
that the same outcome is impossible to engineer elsewhere.

**Suggested audience statement**

> "Frontier Tuning brings the enterprise task and the improvement process into
> one learning environment: the agent's skills, connected knowledge and tools,
> business grading standards, evaluation and refinement, and a path to
> reinforcement fine-tuning. Our warranty climb shows why that matters:
> we could diagnose the difference between a weak instruction, a weak grading
> rule and a tool-access problem, and measure a targeted change instead of
> assuming that more training was the answer."

**Do not claim "nothing else in the market offers this."** The sources reviewed
establish the integration and workflow, not market-wide exclusivity. Our
measured story is narrower still: reliable baseline measurement, better grading,
and improved draft recording. Small-model gains, cost savings and full
branch-level search explainability remain unproved.

## 9. Sources and follow-up

**Our measurements**

- [Climb scoreboard](../climb/README.md) and the stage records linked in section 3.
- [Skill/rubric provenance](04-hill-climb-method.md#6-where-the-skill-and-rubrics-came-from).
- [Operations and preflight](05-operations.md), [platform issues](06-platform-issues.md),
  and [Streamlit console](../ui/README.md).

**Platform capabilities — upstream guidance, not tenant measurements**

- [Stable v1 CLI reference](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1).
- [Agent learning environment guide](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1/agent-guidance/GUIDE.html).
- [Quick, Light and Deep flows](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1/agent-guidance/playbooks/tuning-flows.html).
- [Skill refinement](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1/agent-guidance/playbooks/skill-tuning.html)
  and [rubric generation/refinement](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1/agent-guidance/playbooks/rubric-tuning.html).
- [Inference strategies and routing](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1/agent-guidance/playbooks/harness-tuning.html)
  and [model tuning](https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1/agent-guidance/playbooks/model-tuning.html).
- [Microsoft Foundry overview](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)
  and [Foundry fine-tuning](https://learn.microsoft.com/en-us/azure/foundry/fine-tuning/overview).

**Next measured step:** finish the remaining targeted skill fix, evaluate the
final configuration on the 30 held-out claims, then resume the small-model
baseline when its tool-access blocker is resolved. Do not jump directly from
the single-claim search demo to a training or savings claim.
