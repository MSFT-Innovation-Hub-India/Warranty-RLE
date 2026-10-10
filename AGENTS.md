# AGENTS.md: Contoso Industrial warranty adjudication RLE

Read this first, every session. It states what this repository is for and the rules for working in it. When a request conflicts with something here, say so rather than quietly doing it.

---

## What this repository is

A Microsoft 365 **Frontier Tuning** world (an RLE) where an agent adjudicates warranty claims for a fictional manufacturer, plus the record of a **hill climb** on it: measure a frontier model, measure a small model, and close the gap one change at a time, ending with reinforcement fine-tuning (RFT).

Everything is **synthetic**: fictional companies, serial numbers and money. No customer or private content, ever.

**Current attempt:** climb 2 (restarted 2026-10-10). Attempt 1 is archived in `archive/attempt-1/` and is read-only.

---

## The Frontier Tuning CLI documentation: look here first

**<https://ft-cli-docs.bluebeach-20303fe3.eastus2.azurecontainerapps.io/v1>**

Use it whenever you need to know how a command works, which options exist, what an error means, or how a hill climb should be run. Don't guess from memory or from old runs.

| Need | Where in the docs |
| --- | --- |
| A command and its options | Main page (`/v1`), sections Setup · Run an execution · Samples · Models · Tune & Evaluate |
| How to run the climb (skill → rubric → inference → tuning) | `/v1/agent-guidance/GUIDE.html` and the playbooks: `tuning-flows`, `evaluation`, `skill-tuning`, `rubric-tuning`, `harness-tuning`, `model-tuning` (under `/v1/agent-guidance/playbooks/`) |
| A platform error | Main page § *API error diagnostics* and *Job and execution diagnostics*; playbook `troubleshooting.html` |
| What changed between CLI versions | Main page § *Release notes* |

Two cautions:
- The docs describe CLI **1.0.x**. Check the installed version with `frontier-tuning --version`. On 2026-10-10 it was **0.3.17**, which lacks `skills refine --mode` and returns PascalCase JSON. When the docs and the installed `--help` disagree, the installed `--help` decides what will run. Record the difference.
- Docs are 📄 upstream guidance, not measurements on this tenant.

---

## The goals, in priority order

1. **Measure the ceiling first.** GPT-5.6-Sol on the fixed world, skill and rubrics shows what is achievable. Claims Sol gets wrong are world or answer-key problems, not model problems.
2. **Measure the small model's floor and reach.** MAI-CODE-5b with repeats: average correctness, and correctness "in any attempt". The difference is what RFT can capture.
3. **Close the gap with the right lever.** Skill for behaviour the model never shows, rubrics for a reward that ranks wrong attempts higher, RFT for behaviour it shows inconsistently. The reasoning is in [docs/04-hill-climb-method.md](docs/04-hill-climb-method.md).
4. **Use the platform's own tools** where they fit (`skills refine`, `skills generate-rubrics`, `health quality check`, `evaluate compare`), and record what they actually do.
5. **Finish with an honest comparison**: tuned small model vs base small model vs frontier, stating what was and was not controlled.

---

## Rules that are not negotiable

**One variable per stage.** Each stage changes one thing against the previous stage's `config/`. If two things must change together, say so in the stage README.

**Two numbers, always.** The platform's rubric score is never reported alone. Every stage also runs `scripts/score_ground_truth.py` (decision, governing instrument, payable against `world-builder/out/data/claims.json`). During RFT the rubric score *is* the reward, so a rubric score that rises while correctness doesn't must be fixed before tuning.

**Measure before changing.** No edit to rubrics, samples or skill without a baseline to compare against. Changed rubrics need a new baseline.

**Evaluation claims stay held out.** The 30 Evaluation samples are never used for `skills refine`, rubric refinement or training. Refinement and tuning use the 60 Training samples only.

**One source of truth for the world.** Every document, workbook, database row, sample and expected answer is generated from `world-builder/spec/` and computed by `world-builder/build/adjudicate.py`. Gates (`adjudicate.py` 14 checks, `test_traps.py` 31 checks) pass before any generator runs.

**Rubrics before skills, and never the rubric's wording in the skill.** The standard lives only in the rubrics, which the grader sees and the model does not. Check with `scripts/check-skill.py` before applying a skill.

**Paid or outward-facing actions need the user's go-ahead**: evaluations, refinements, tuning jobs, cancellations, rubric generation, CLI upgrades. An unknown submission outcome is read with `status`/`list`, never resubmitted.

**The database is reset between runs, never during one.** Baseline `0 0 0 0` before every evaluation; snapshot and reset after. Never reset while a tuning or evaluation job is active.

---

## How every stage is documented

Each stage lives in `climb/stage-N/`, copied from [climb/_template/](climb/_template/):

| File | Reader | Holds |
| --- | --- | --- |
| `README.md` | A business reader | Goal · what changed · how the run went · results (the numbers) · findings · conclusion · next step. Tables over prose. No CLI output |
| `RUNBOOK.md` | Someone replaying the stage, or an auditor | Every CLI command **exactly as run**, in order, each followed by its response (verbatim, or marked *trimmed*). Platform errors with their transaction IDs |
| `config/` | The platform | What was applied: `skill.md`, `rubrics.json` (+ readable `rubrics.md`), samples and their platform IDs. See [climb/_template/config/README.md](climb/_template/config/README.md) |
| `results/` | Both | Platform results JSON, `ground-truth-check.md`, `run-summary.md` |
| `raw/` | An auditor | Run logs, database snapshots, status/diagnostics JSON |

Writing rules:
- **Label the source.** 🖥️ measured on this tenant · 📄 CLI docs / upstream guidance · 🔬 unverified · 💭 reasoning. Never present an inference as a measurement.
- **Crisp.** Short paragraphs, tables where possible, findings as *issue → what we did*, one line each.
- **Report failures plainly.** A stage that did not improve is a finding.
- **Never invent output.** Excerpts are marked as excerpts.
- Keep **"Where we are"** in [README.md](README.md) true at the end of every session, and the scoreboard in [climb/README.md](climb/README.md).

---

## When the platform errors

1. Look the error up in the CLI docs (§ *API error diagnostics*, § *Job and execution diagnostics*, `troubleshooting.html`).
2. Read the job's own diagnostics (`evaluate diagnostics`, `tune diagnostics`, `executions diagnostics`) and status `Stages[].Errors`.
3. Record it in [docs/06-platform-issues.md](docs/06-platform-issues.md) with the fields the docs ask for: CLI version, command (sensitive args removed), environment/job/execution IDs, UTC time window, exit code, error text, transaction ID, and what we did. Then reference it from the stage RUNBOOK.
4. Don't retry a write, cancel, or resubmit without the user's go-ahead.

---

## Layout

| Path | Holds |
| --- | --- |
| `README.md` | Where we are, and a map of the repository |
| `docs/` | The scenario, world configuration, claim flow, hill-climb method, operations runbook, platform issues ([index](docs/README.md)) |
| `climb/` | One folder per stage of the current climb, and the template |
| `scripts/` | Evaluation runner, scorer, database scripts ([what each does](scripts/README.md)) |
| `world-builder/` | Everything that creates and deploys the world, including the MCP server. Touch only to rebuild or redeploy |
| `archive/attempt-1/` | The first climb on world v3: read-only record and lessons |

---

## Open questions (🔬 unverified)

| Question | Status |
| --- | --- |
| Are `dev-ct-mai-code-mp` (MAI-CODE-5b, evaluation) and `mai-code-1-flash` (tuning base) the same weights? | Open. Decides whether base vs tuned is like-for-like |
| Does `tune start` use Training or Evaluation samples? | 📄 Docs: Training only, minimum 11. Not yet confirmed on this tenant |
| Does tuning reuse rollouts or grader scores from earlier evaluations? | Open |
| Does the grader see the world's sources, or only the answer and tool trace? | Open. Decides how far rubrics can check correctness |
| Why does the finish tool sometimes reject a correct hand-in? | With the platform team ([docs/06](docs/06-platform-issues.md)) |
