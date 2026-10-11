"""Check that the live skill and rubrics match a stage's pinned config/.

    python scripts/check-live-config.py <stage>/config [--env <env-id>] [--skill <skill-id>]

Compares, after newline normalisation:
  * the skill's instructions (live `prompt`) with the text after "## Instructions" in config/skill.md
  * each rubric's name, importance, enabled state and checklist items with config/rubrics.json
Then checks that every sample ID in config/eval-sample-ids.json exists in the environment
as an Evaluation sample of this skill.

Exit 0 when everything matches, 1 otherwise. Read-only: it only runs `skills get` and
`samples list`.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("config")
ap.add_argument("--env", default="598fd1b0-36f1-402f-ba36-aa00c8a67cc4")
ap.add_argument("--skill", default="cf00d339-5217-4cd1-b390-cc0d911735da")
a = ap.parse_args()
cfg = Path(a.config)


def cli(*args):
    out = subprocess.run(["frontier-tuning", "-e", a.env, "-o", "json", *args],
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        sys.exit(f"CLI failed: frontier-tuning {' '.join(args)}\n{out.stderr or out.stdout}")
    t = out.stdout
    return json.loads(t[min(i for i in (t.find("{"), t.find("[")) if i >= 0):])


def g(d, *names):
    for n in names:
        if isinstance(d, dict) and d.get(n) is not None:
            return d[n]
    return None


norm = lambda s: "\n".join(l.rstrip() for l in (s or "").replace("\r\n", "\n").strip().split("\n"))
ok = True

live = cli("skills", "get", a.skill, "--show-rubrics")
skill = g(live, "skill", "Skill") or live
pinned = (cfg / "skill.md").read_text(encoding="utf-8").split("## Instructions", 1)[1]
same = norm(g(skill, "prompt", "Prompt", "instructions")) == norm(pinned)
print(f"instructions match config/skill.md: {same}")
ok &= same

want = {g(r, "RubricName", "rubricName", "name"): r
        for r in json.loads((cfg / "rubrics.json").read_text(encoding="utf-8-sig"))}
have = {g(r, "RubricName", "rubricName", "name"): r for r in g(live, "rubrics", "Rubrics") or []}
print(f"rubrics: live {len(have)}, pinned {len(want)}")
ok &= set(want) == set(have)
for name in sorted(set(want) | set(have)):
    w, h = want.get(name), have.get(name)
    if not (w and h):
        print(f"  {name}: {'missing live' if w else 'not pinned'}"); ok = False; continue
    checks = {
        "items": [norm(x) for x in g(w, "ChecklistItems", "checklistItems")] == [norm(x) for x in g(h, "checklistItems", "ChecklistItems")],
        "importance": (g(w, "Importance", "importance") or "").lower() == (g(h, "importance", "Importance") or "").lower(),
        "enabled": g(h, "isEnabled", "IsEnabled") is not False,
    }
    print(f"  {name}: " + ", ".join(f"{k} {'ok' if v else 'DIFFERS'}" for k, v in checks.items()))
    ok &= all(checks.values())

ids = cfg / "eval-sample-ids.json"
if ids.exists():
    wanted = {e["id"]: e["claim"] for e in json.loads(ids.read_text(encoding="utf-8-sig"))}
    listed = cli("samples", "list", "--limit", "500")
    listed = g(listed, "value", "items", "samples") if isinstance(listed, dict) else listed
    live_s = {g(s, "id", "Id"): s for s in listed or []}
    missing = [c for i, c in wanted.items() if i not in live_s]
    wrong = [c for i, c in wanted.items() if i in live_s and
             (str(g(live_s[i], "type", "Type", "label", "sampleType") or "Evaluation").lower() != "evaluation"
              or g(live_s[i], "skillId", "SkillId") not in (None, a.skill))]
    print(f"evaluation samples: {len(wanted) - len(missing)}/{len(wanted)} present; wrong type or skill: {wrong or 'none'}")
    ok &= not missing and not wrong
    if missing:
        print("  missing: " + ", ".join(missing))

print("ALL MATCH" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
