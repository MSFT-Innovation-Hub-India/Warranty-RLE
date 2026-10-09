# Evidence: the verbatim record (world v3)

For an auditor. Commands exactly as run, outputs verbatim, raw execution JSON, and dead ends. The readable story is [JOURNEY.md](../JOURNEY.md). The record of the first climb (world v2) was removed on 2026-10-08; it is in the backup and in git history.

| File or folder | Covers |
| --- | --- |
| [journey-record-2026-10-07.md](journey-record-2026-10-07.md) | World v3: archive, dossier tool, labour workbook, deployment, stage 0 setup |
| [journey-record-2026-10-09.md](journey-record-2026-10-09.md) | Stage 2 closure, stage 3 probe and cancellation, SQL cleanup, evidence consolidation and validation |
| [stage-2/](stage-2/) | Refinement inputs/output, retained batch results, failed attempts and database evidence |
| [stage-3/](stage-3/) | Configuration verification, BestOfN probe, cancelled comparison jobs and database evidence |
| `stage-0/` | Stage 0: `run-log.txt` (every job, as run) and `db-snapshots.txt` (what each job wrote, before the reset). The results of all 30 claims are in `stages/stage-0/eval-results-samples.json` |
| `sp-03-ratecards-*.json` | The SharePoint change to `03-RateCards` |
| [platform-issue-finish-rejection.md](platform-issue-finish-rejection.md) | Note for the platform team: rejected and echoed hand-ins, model identity (open) |

## Command captures

Stage 3's small `command-<id>.stdout.txt` and `.stderr.txt` files are consolidated
into `command-captures.zip` in each of [probe/](stage-3/probe/),
[simple/](stage-3/simple/) and [bestofn/](stage-3/bestofn/). Each adjacent
`command-captures.manifest.json` records original filenames, byte lengths and
SHA-256 hashes. All 122 entries were verified against the original bytes before
the loose copies were removed, including empty stderr files. No evidence was
discarded. Raw result JSON, named diagnostics, database snapshots and run logs
remain directly readable.

To inspect a capture, open the ZIP or extract it outside the repository:

```powershell
Expand-Archive -LiteralPath docs\evidence\stage-3\probe\command-captures.zip -DestinationPath "$env:TEMP\warranty-stage3-probe-captures"
```
