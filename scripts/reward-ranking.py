"""Does the rubric score rank right answers above wrong ones?

    python scripts/reward-ranking.py <stage>/results [--set C-2026-04153=correct ...]

Reads <results>/ground-truth-check.csv (written by score_ground_truth.py). --set overrides the
scorer with the hand-check outcome for a claim (correct | wrong). Compares the rubric score of
every (right, wrong) pair: during RFT the rubric score is the reward, so a wrong answer that
outscores right ones is a reward the model would learn from.
"""
import argparse
import csv
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("results")
ap.add_argument("--set", action="append", default=[], metavar="CLAIM=correct|wrong")
a = ap.parse_args()

hand = {}
for s in a.set:
    claim, v = s.split("=", 1)
    hand[claim.strip()] = v.strip().lower() in ("correct", "true", "right", "1")

rows = list(csv.DictReader(open(Path(a.results) / "ground-truth-check.csv", encoding="utf-8")))
lab = [(r["claim"], float(r["rubric"]), hand.get(r["claim"], r["correct"] == "True"))
       for r in rows if r.get("rubric") not in ("", None)]
right = [s for _, s, ok in lab if ok]
wrong = [(c, s) for c, s, ok in lab if not ok]
pairs = [(x, s) for x in right for _, s in wrong]

print(f"correct (with hand-check): {len(right)} of {len(lab)}")
print(f"mean rubric: right {sum(right) / max(1, len(right)):.3f} · wrong "
      + (f"{sum(s for _, s in wrong) / len(wrong):.3f}" if wrong else "n/a"))
if pairs:
    above = sum(x > s for x, s in pairs)
    print(f"right ranked above wrong: {above} of {len(pairs)} pairs ({above / len(pairs):.0%}); ties {sum(x == s for x, s in pairs)}")
for c, s in wrong:
    print(f"  wrong: {c} rubric {s} - outscores {sum(x < s for x in right)} of {len(right)} right answers")
