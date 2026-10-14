# The climb (attempt 2)

One folder per stage. Each holds a business-readable `README.md`, a `RUNBOOK.md` with every command and response, and the `config/`, `results/` and `raw/` files. New stages start from [_template/](_template/). Why the stages are in this order: [docs/04-hill-climb-method.md](../docs/04-hill-climb-method.md).

**Fixed throughout:** world v3 (`wce-main`), the 30 evaluation claims, the ground-truth scorer. **Stages 0–3:** GPT-5.6-Sol, to settle the skill and rubrics. **Stages 4–5:** the small model, MAI-CODE-5b (`dev-ct-mai-code-mp`), tuned as `mai-code-1-flash` in stage 5. Training claims (60) are used for refinement; the 30 Evaluation claims stay held out.

## Scoreboard

Every stage reports two numbers: **right answers**, checked against the answer key (automatic scorer plus a hand-check of anything it marks wrong or can't read), and the platform's **rubric score**.

| Stage | Model and change | Question | Right answers | Rubric | Status |
| --- | --- | --- | --- | --- | --- |
| [0 · Baseline](stage-0/README.md) | GPT-5.6-Sol, current skill and rubrics | How well does the strongest model do on this use case? | **29/30** | 0.956 | ✅ 2026-10-11 |
| [1 · Broaden the evidence](stage-1/README.md) | GPT-5.6-Sol on the 60 Training claims, no change | Where do the skill and rubrics fall short? | **57/60** (Training) | 0.934 | ✅ 2026-10-13: the Authority rubric gave the one wrong answer full marks |
| [2 · Reward alignment](stage-2/README.md) | Rubrics only: Authority and Valuation revised | Does the reward prefer the right answer? | **59/60** (Training) | 0.940 | ✅ 2026-10-13: asset-only questions no longer penalised, unrecorded drafts now are; the escalation and supersession items untested (Sol didn't make those errors) |
| [2b · Rubric checks](stage-2b/README.md) | Valuation not applicable to asset-only questions; 4 negative controls | Do the revised rubrics mark down the mistakes they target? | — | — | ✅ 2026-10-14: unrecorded escalation 1.00 → 0.33; mispriced part Valuation → 0.60; outright goodwill decline on instruction still 1.00 |
| [3 · Skill: record the draft](stage-3/README.md) | Skill only: one line on recording the draft | Does Sol record the draft for every claim question? | | | 🔄 2026-10-14 |
| [4 · Small model](stage-4/README.md) | MAI-CODE-5b on the final configuration, with repeats | How far is the small model from Sol, and what could close it? | | | ⛔ first attempts blocked ([P11](../docs/06-platform-issues.md#p11-mai-code-5b-runs-cannot-call-the-claim-system-virtualization-error)) |
| 5 · Close the gap | Small-model skill, then RFT | Does tuning turn "sometimes right" into "usually right"? | | | ⬜ blocked by [P7](../docs/06-platform-issues.md#p7-tuning-excludes-the-claim-system-tools) |
