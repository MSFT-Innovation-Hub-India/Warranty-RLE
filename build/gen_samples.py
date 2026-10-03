"""Turn the claim population into sample prompt files.

Sample files carry a Prompt and nothing else - the platform's grading path uses
the skill's rubrics, not a reference answer. The expected answers live in
GROUND-TRUTH.md for human audit and for any out-of-band numeric check.

Phrasing is varied on purpose. Eighty-six copies of "Adjudicate claim X" would
train a model to recognise one sentence shape rather than to do the job, and
would tell you nothing about how it behaves when a real adjudicator types
something else.

    .venv/Scripts/python.exe build/gen_samples.py
"""

from __future__ import annotations

import json
from pathlib import Path

from adjudicate import DEALERS

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "out" / "data"
OUT = ROOT / "out" / "samples"

# Phrasings an adjudicator might actually use. Index into these by position so
# the split is deterministic and reruns are stable.
PHRASINGS = [
    "Adjudicate claim {claim}.",
    "{dealer} have submitted {claim}. Is it covered, and what do we pay?",
    "Can you work up {claim} for me — coverage position and payable amount?",
    "What's the position on {claim}?",
    "Review {claim} and tell me the decision, the instrument it turns on, and the amount.",
    "{claim} came in from {dealer} this morning. Where do we land?",
    "I need a decision on {claim} before the partner call. What have we got?",
    "Please assess {claim} on serial {serial} and give me the payable figure.",
    "Run the numbers on {claim} — is it in warranty and how much?",
    "{claim}: covered or not? If covered, what's payable and under what?",
    "Take a look at {claim} for the {dealer} account and advise.",
    "Give me the adjudication for {claim}, with the instrument you relied on.",
]

# A few prompts that start from the asset rather than the claim, so the skill is
# not only ever entered through a claim reference.
SERIAL_PHRASINGS = [
    "Is serial {serial} still in warranty as at {repair}? There's a claim, {claim}.",
    "Customer is asking about {serial}. Claim {claim} is open — what's the coverage position?",
]


def build() -> dict[str, int]:
    records = json.loads((DATA / "claims.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    for split, filename in (("eval", "warranty-adjudication.eval.jsonl"),
                            ("train", "warranty-adjudication.train.jsonl")):
        rows = [r for r in records if r["split"] == split]
        lines = []
        for i, r in enumerate(rows):
            c = r["claim"]
            dealer = DEALERS[c["dealer_id"]]["name"]
            fields = {"claim": c["claim_id"], "serial": c["serial"],
                      "dealer": dealer, "repair": c["repair_date"]}
            if i % 9 == 8:
                template = SERIAL_PHRASINGS[(i // 9) % len(SERIAL_PHRASINGS)]
            else:
                template = PHRASINGS[i % len(PHRASINGS)]
            lines.append(json.dumps({"Prompt": template.format(**fields)},
                                    ensure_ascii=False))
        (OUT / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")
        counts[filename] = len(lines)

    # A three-prompt smoke set for use after any rubric edit. Six samples took
    # ~55 minutes on this tenant; thirty will take about four and a half hours,
    # so nothing but a stage boundary justifies the full run.
    evals = [r for r in records if r["split"] == "eval"]
    smoke = [next(r for r in evals if r["slice"] == s)
             for s in ("covered-simple", "precedence", "abstention")]
    lines = []
    for i, r in enumerate(smoke):
        c = r["claim"]
        lines.append(json.dumps(
            {"Prompt": PHRASINGS[i].format(
                claim=c["claim_id"], serial=c["serial"],
                dealer=DEALERS[c["dealer_id"]]["name"], repair=c["repair_date"])},
            ensure_ascii=False))
    (OUT / "warranty-adjudication.smoke.jsonl").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    counts["warranty-adjudication.smoke.jsonl"] = len(lines)

    # Upload guidance, kept with the files so the traps in CLI-REFERENCE are not
    # rediscovered the hard way.
    (OUT / "UPLOAD.md").write_text(f"""# Uploading the samples

```powershell
$skillId = '<skill-id>'
$envId   = '<env-id>'

frontier-tuning samples upload .\\warranty-adjudication.eval.jsonl  `
  --skill-id $skillId --type Evaluation --env-id $envId
frontier-tuning samples upload .\\warranty-adjudication.train.jsonl `
  --skill-id $skillId --type Training   --env-id $envId
```

Expect `Uploaded: {counts['warranty-adjudication.eval.jsonl']} | Failed: 0` and
`Uploaded: {counts['warranty-adjudication.train.jsonl']} | Failed: 0`.

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
""", encoding="utf-8")

    return counts


if __name__ == "__main__":
    counts = build()
    for name, n in counts.items():
        print(f"  {name:42} {n:>3} prompts")
    print(f"\nWritten to {OUT}")
    print("\nFirst three evaluation prompts:")
    for line in (OUT / "warranty-adjudication.eval.jsonl").read_text(
            encoding="utf-8").splitlines()[:3]:
        print(f"  {json.loads(line)['Prompt']}")
