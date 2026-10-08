# Uploading the samples

```powershell
$skillId = '<skill-id>'
$envId   = '<env-id>'

frontier-tuning samples upload .\warranty-adjudication.eval.jsonl  `
  --skill-id $skillId --type Evaluation --env-id $envId
frontier-tuning samples upload .\warranty-adjudication.train.jsonl `
  --skill-id $skillId --type Training   --env-id $envId
```

Expect `Uploaded: 30 | Failed: 0` and
`Uploaded: 60 | Failed: 0`.

## Four things that will cost you a day

1. **Samples snapshot the skill's rubrics at upload time.** Edit a rubric
   afterwards and the scores will not move. You will conclude the edit did
   nothing. Re-upload.
2. **Re-uploading adds copies, it does not replace.** Run
   `samples delete-by-skill` first, every time.
3. **`evaluate start` is whole-workspace by default** and only considers
   Evaluation-typed samples. Scope with `--skill-id`.
4. **Submitted is not graded.** A prompt that fires no skill produces no rubric
   rows, drops out of the mean rather than scoring zero, and leaves
   `FailureRate: 0.0`. Check the counts on every run.

## Tiered runs

| Tier | File | When | Wall clock |
| --- | --- | --- | --- |
| Smoke | `warranty-adjudication.smoke.jsonl` | After any skill or rubric edit | ~25 min |
| Full | `warranty-adjudication.eval.jsonl` | Stage boundaries only | ~4.5 h |

The expected answers are in `../GROUND-TRUTH.md`, one block per evaluation claim
with the full working.
