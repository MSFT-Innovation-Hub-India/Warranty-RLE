# Stage 4: exploratory RFT pilot (world v3)

**Status:** submitted at 10:59:38 IST on 2026-10-09; job
`c77feaed-96de-4b88-9802-e0f265601eb8` is Running, with training and deployment
both NotStarted and `readyForEvaluation: false`. No tuning result.
User explicitly approved an exploratory
pilot without measured cohort headroom on 2026-10-09. **Stage 3 gate remains
unpassed.** This is not a gate-passed hill climb.

## The intended change

Tune `mai-code-1-flash` with the existing world. Keep the stronger stage 1 skill,
six hand-written rubrics, tools, knowledge and sample prompts unchanged. Pins in
this folder are copied from stage 3 (skill/rubrics/evaluation prompts) and stage 2
(Training prompts and IDs).

| Input | Preflight |
| --- | --- |
| World | `wce-main`, `598fd1b0-36f1-402f-ba36-aa00c8a67cc4`; one enabled warranty skill |
| CLI | Frontier Tuning 0.3.17, verified after user upgrade |
| Base model | `mai-code-1-flash`, present in live `FTBaseModels` |
| Skill | Stage 1 instructions restored; compare live `Prompt` with pin after newline normalization |
| Reward | Six authored checklists; platform applies rubrics, not our local ground-truth scorer |
| Samples | Live inventory: 60 Training + 30 Evaluation; intended train/test separation |
| SQL | Preflight baseline: drafts, evidence requests, escalations, claims-not-seeded = 0 0 0 0 |
| Epochs | Omit override; use server default for the first pilot |

## What the reward means

The playbook documents rubrics as inference-time selection criteria, evaluation
criteria and fine-tuning reward functions. No separate custom grader deployment
is required by this CLI workflow. The reward covers coverage, precedence,
grounding, valuation, authority/action and missing evidence.

The checked Training sample (04104) embeds all six checklists. Its sample DTO
omits rubric descriptions and scoring direction, while the live skill retains
them. The measured stage 1 Evaluation sample uses the same embedded serialization
(direction null, description absent). Do not rewrite snapshots on that basis:
compare the fields actually embedded, and keep the original service output.
Only one Training sample's embedded rubric payload was inspected; do not claim
all 60 were individually verified.

## Controls and limitations

- Whole-world tuning: no per-skill scoping. Submit only after validating the
  enabled skill and inventory; inspect returned workspace snapshot counts.
- The playbook intends Training prompts for training; CLI 0.3.17 says the service
  determines sample selection. Exact backend selection and any reuse of prior
  evaluation rollouts remain unverified. Snapshot counts alone do not prove a
  held-out evaluation split.
- `dev-ct-mai-code-mp` versus `mai-code-1-flash` weight equivalence is unverified.
  A tuned-model comparison is operational unless equivalence is established.
- Rubric score is not ground-truth correctness. Run the local scorer and inspect
  extraction/review flags after evaluation; do not claim tuning gains yet.
- No buffering of MCP database writes has been verified for tuning. Monitor and
  reconcile activity before any database reset; never reset during an active job.
- Deployment capacity may delay completion for days. Inspect training/deployment
  stages, not only the job's last-updated timestamp.

## Submit and inspect

Submission timed out in the CLI, but reconciliation found exactly one matching
server-side job; **no second submission**. Snapshot: one skill, three registered
tools, **90 sample prompts**, four knowledge sources. This confirms whole-world
capture, not that all 90 prompts will be used as training examples. Training
sample selection remains unverified. Diagnostics returned `state: NotAvailable`;
no training metrics are available.

Exactly submitted:

```powershell
frontier-tuning --output json tune start --base-model mai-code-1-flash --new-model contoso-warranty-v3-stage4-pilot-20261009 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
frontier-tuning --output json tune status c77feaed-96de-4b88-9802-e0f265601eb8 --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
frontier-tuning --output json tune diagnostics c77feaed-96de-4b88-9802-e0f265601eb8 --include-metrics --env-id 598fd1b0-36f1-402f-ba36-aa00c8a67cc4
```

Retain submission/status/diagnostics under [evidence](../../docs/evidence/stage-4/).
When deployment is ready, discover the actual evaluation model ID and score the
same held-out cohort with rubric score, ground-truth correctness and hand-in
failures. Do not attribute any gain to tuning if evaluation prompts were consumed
for training; disclose that uncertainty until resolved.

## Sources

- [Playbook: fine-tuning](https://github.com/m365-core/orbit/blob/main/FT-Playbook/70-roadmap/features/fine-tuning.md)
- [Playbook: worlds and rubrics](https://github.com/m365-core/orbit/blob/main/FT-Playbook/20-product/worlds-and-rles.md)
- [Playbook: tuning runbook](https://github.com/m365-core/orbit/blob/main/FT-Playbook/40-assets/rle-hill-climbing-runbook.md)

Upstream guidance is not a measurement on this tenant. Live preflight facts and
dead ends are recorded separately in the evidence log.
