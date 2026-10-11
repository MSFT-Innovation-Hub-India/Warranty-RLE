# The climb (attempt 2)

One folder per stage. Each holds a business-readable `README.md`, a `RUNBOOK.md` with every command and response, and the `config/`, `results/` and `raw/` files. New stages start from [_template/](_template/). Why the stages are in this order: [docs/04-hill-climb-method.md](../docs/04-hill-climb-method.md).

**Fixed throughout:** world v3 (`wce-main`), the 30 evaluation claims, the ground-truth scorer. **Reference model:** GPT-5.6-Sol. **Climbing model:** MAI-CODE-5b (`dev-ct-mai-code-mp`), tuned as `mai-code-1-flash` in stage 4.

## Scoreboard

| Stage | One change | Question | Rubric | Correct | Status |
| --- | --- | --- | --- | --- | --- |
| [0 · Frontier reference](stage-0/README.md) | Model = GPT-5.6-Sol | What does the world allow? | **0.956** | **29/30** | ✅ 2026-10-11 · gate passed; the one miss (supersession) scored 0.96 |
| 1 · Small-model baseline and headroom | Model = MAI-CODE-5b, 3 runs per claim | Floor, reach, and does the reward rank MAI's right answers higher? | | /30 (mean) · /30 (any) | ⬜ |
| 2 · Reward alignment | Rubrics only | Does the reward prefer the right attempt? | | | ⬜ skipped if stage 1 passes |
| 3 · Skill, one fix at a time | Skill only (3a, 3b, …) | Can a missing procedure be taught? | | | ⬜ |
| 4 · RFT | Model weights | Does tuning turn "sometimes right" into "usually right"? | | | ⬜ blocked by [P7](../docs/06-platform-issues.md#p7-tuning-excludes-the-claim-system-tools) |

## Starting point carried from attempt 1 🖥️

| Configuration | Model | Rubric | Correct |
| --- | --- | --- | --- |
| Business-brief skill + hand-written rubrics (= stage 0 config here) | MAI-CODE-5b, one run | 0.637 | 23/30 |
