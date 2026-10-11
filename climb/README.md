# The climb (attempt 2)

One folder per stage. Each holds a business-readable `README.md`, a `RUNBOOK.md` with every command and response, and the `config/`, `results/` and `raw/` files. New stages start from [_template/](_template/). Why the stages are in this order: [docs/04-hill-climb-method.md](../docs/04-hill-climb-method.md).

**Fixed throughout:** world v3 (`wce-main`), the 30 evaluation claims, the ground-truth scorer. **Reference model:** GPT-5.6-Sol. **Climbing model:** MAI-CODE-5b (`dev-ct-mai-code-mp`), tuned as `mai-code-1-flash` in stage 4.

## Scoreboard

Every stage reports two numbers: **right answers**, checked against the answer key (automatic scorer plus a hand-check of anything it marks wrong or can't read), and the platform's **rubric score**.

| Stage | Model and change | Question | Right answers | Rubric | Status |
| --- | --- | --- | --- | --- | --- |
| [0 · Baseline](stage-0/README.md) | GPT-5.6-Sol, current skill and rubrics | How well does the strongest model do on this use case? | **29/30** | 0.956 | ✅ 2026-10-11 |
| [1 · MAI-CODE-5b](stage-1/RUNBOOK.md) | MAI-CODE-5b, same configuration | How does the small model do on the same use case? | | | ⛔ blocked: MAI calls fail with `500` ([P10](../docs/06-platform-issues.md#p10-every-call-naming-mai-code-5b-fails-with-500-er99000)) |
| 2 · Reward alignment | Rubrics only | Does the reward prefer the right answer? | | | ⬜ |
| 3 · Skill, one fix at a time | Skill only (3a, 3b, …) | Can a missing procedure be taught? | | | ⬜ |
| 4 · RFT | Model weights | Does tuning turn "sometimes right" into "usually right"? | | | ⬜ blocked by [P7](../docs/06-platform-issues.md#p7-tuning-excludes-the-claim-system-tools) |
