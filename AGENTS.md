# AGENTS.md — Contoso Industrial warranty adjudication RLE

Read this first, every session. It states what this repository is for and the
rules that govern how it is built. When a request conflicts with something here,
say so rather than quietly doing it.

---

## What this repository is

A Microsoft 365 **Frontier Tuning** world, built from scratch to demonstrate a
measurable hill climb — from a deliberately naive starting point through to
reinforcement fine-tuning, with the gain at each stage attributable to one
change.

It is **not** the upstream reference scenario. That exploration lives separately
in `frontier-tuning-sandbox` (contract renewal) and is a finished record. Do not
copy its conclusions here; this world has its own measurements.

Everything in this repository is **synthetic**. Fictional companies, serial
numbers, money. No customer or private content, ever.

---

## The goals, in priority order

1. **Start at stage 0 and climb.** Begin with a world that is honestly weak, and
   improve it in stages where each stage changes **one variable**. The story is
   the progression, not the final number.
2. **Create and preserve headroom.** A saturated world proves nothing. If a stage
   scores above ~0.95 there is nothing left to demonstrate — harden the world
   rather than celebrate the score.
3. **Use the platform's own tools to improve the world**, not hand-editing alone:
   `skills generate-rubrics`, `rubrics refine`, `skills refine`, `skills enrich`,
   `rle-quality check`, `health insights`. Part of the exercise is finding out
   what they actually do.
4. **Measure headroom before tuning.** `Simple` vs `BestOfN` on the same model is
   the cheap test for whether fine-tuning has anything to capture. If the gap is
   near zero, do not tune — report that.
5. **Reach RFT with an honest comparison.** Finish by matching a frontier model
   with a tuned small model, stating plainly what was and was not controlled.

---

## Rules that are not negotiable

**One variable per stage.** The frontier model is held constant from stage 0 to
stage 3. Change the model mid-climb and the delta becomes uninterpretable.

**Measure before changing.** Never edit rubrics, samples or instructions without
a baseline to compare against. A change you cannot measure is a change you
cannot defend.

**One set of numbers, one arbiter.** Every document, workbook, deck, database row
and sample is generated from `spec/`, and every expected answer is computed by
`build/adjudicate.py`. Nothing is hand-written twice. If the corpus and the
ground truth can disagree, the measurement is worthless.

**Gates before artefacts.** `adjudicate.py` (14 checks) and `test_traps.py`
(31 checks) must pass before any generator runs. `populate.py` exits non-zero if
the trap distribution drifts.

**Rubrics before skills.** Success criteria first. A rubric written after the
skill tends to describe what the skill already does — which is what saturated the
contract-renewal world.

**Never put a rubric's wording into the skill instructions.** The standard lives
only in the rubric, which the grader sees and the model does not.

---

## How to write for me

I am keeping a build log, not producing marketing. Specifically:

- **Chronological.** Do not insert a later finding into an earlier section. The
  document records what was known at the time.
- **Label the source.** 🖥️ measured on this tenant · 📄 upstream guidance ·
  🔬 unverified · 💭 reasoning. Never present an inference as a measurement.
- **Upstream results are not our results.** Their numbers may guide the process;
  they are not evidence about this world.
- **Crisp.** Short paragraphs, tables over prose, no restating the obvious. If a
  section can be a table, make it a table.
- **Report failures plainly.** A stage that did not improve is a finding worth
  recording, not a problem to write around.

---

## Journey log — keep it current

Two documents, two audiences. Update both **as work happens**, every session.

| Document | Reader | Holds |
| --- | --- | --- |
| `docs/JOURNEY.md` | A human catching up | The readable story: scenario → setup recipe → climb → findings |
| `docs/evidence/` | An auditor | Every command exactly as run, full verbatim output, raw execution JSON, dead ends |

**`JOURNEY.md` — written for someone new to the scenario.**

- **Keep its shape.** Where we are → 1 Scenario → 2 Setup (P#) → 3 Climb
  (stages) → 4 What we've learned → 5 Side experiments → Appendix (helper
  snippets).
- **"Where we are" is always true.** Status · Next · Blockers · IDs.
- **Each step reads as a recipe:** **Why** (one line) · **Do** (the commands
  that matter, cleanly) · **You should see** (a collapsed excerpt of the real
  output) · **Watch out** (gotchas) · ✅ **Result** (one line).
- **Gotchas are one line each: symptom → what to do.** No debugging narratives.
  The investigation belongs in the evidence record. *Example:* "Run the MCP
  server stateless, or with more than one replica registration fails with
  `ER05017`."
- **Stages close with a short result**: score, what moved, gate passed or not.
  Don't start the next stage until it's written.
- Put long helper scripts in the Appendix (H1, H2 …) and reference them from
  steps. Say plainly whether each is *exactly as run* or simplified.
- Excerpts are fine in `JOURNEY.md`. Never invent output or present an excerpt
  as the full output.

**`docs/evidence/` — the verbatim record.**

- Commands **exactly as run**, including variables and pipes. Outputs
  **verbatim**, marked *(trimmed)* only when lines are cut.
- Raw JSON (executions, probes) under `docs/evidence/<step>/`.
- Dead ends and failed attempts are logged here, one line each.
- Start a dated record file per working session (e.g.
  `journey-record-2026-10-03.md`) and link it from `JOURNEY.md`.

---

## Layout

| Path | What it holds |
| --- | --- |
| `spec/` | Canonical source of truth — hand-authored, reviewed |
| `build/` | Ground-truth engine, trap tests, corpus generators |
| `out/` | Generated corpus, database, samples, `GROUND-TRUTH.md` |
| `mcp/` | The MCP server — 9 read + 3 action tools, ACA + Azure SQL deploy |
| `world/` | `env.md` — the world definition used by `environments init` (dev and main) |
| `docs/` | Design, walkthrough, runbook, cross-cutting references |

Run order matters: `adjudicate` → `test_traps` → `populate` → `ground_truth` →
the `gen_*` scripts. Generators read `out/data/`, so population comes first.

---

## Open questions — resolve before relying on them

| Question | Why it matters |
| --- | --- |
| Are `dev-ct-mai-code-mp` and `mai-code-1-flash` the same weights? | Decides whether a true before/after on one model is possible, or only an operational comparison |
| Does `tune start` consume Training or Evaluation samples? | The CLI help and the samples documentation contradict each other |
| Does tuning reuse rollouts and grader scores from evaluation runs? | Determines whether test-time search is part of the learning loop at all |
| Is `--strategy` enabled on this tenant? | Overrides "take effect only where the service has enabled them" |

🔬 Each of these is unverified. Do not build a claim on one without testing it
first.

---

## Status

Stages 0–4 are **designed, not executed**. Every score in
`docs/05-hill-climb-runbook.md` is a prediction. Nothing has been measured on a
tenant yet.

**Progress lives in [`docs/JOURNEY.md`](docs/JOURNEY.md).** As of 2026-10-03,
prerequisites P0–P5 and P7 are done: corpus loaded, MCP server deployed, and
worlds `wce-dev` and `wce-main` provisioned, with retrieval proven on dev.
Next is P9 (stage-0 skill and samples). P6 (endpoint auth) is still open; the
MCP server is registered as `NoAuth` (P8).

⚠️ `docs/05-hill-climb-runbook.md` does not yet encode goals 3 and 4 above —
no platform optimisation command appears in it, and headroom measurement is
mentioned only in passing. That gap needs closing before stage 2 begins.
