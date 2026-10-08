"""Merge per-claim evaluation results and summarise a stage run.

    python scripts/summarise-stage.py docs/evidence/stage-0 stages/stage-0 [--consolidate]

Reads every results-*.json written by eval-batches.ps1 in <evidence dir>,
writes <stage dir>/eval-results-samples.json (all submissions, the format
scripts/score_ground_truth.py reads) and <stage dir>/run-summary.md, then runs
the ground-truth scorer on the merged file.

--consolidate then folds the per-job db-after-*.txt files into one
db-snapshots.txt and deletes the per-job results-*.json, which the merged file
now holds in full.
"""
import glob
import json
import os
import re
import subprocess
import sys

ev_dir, stage_dir = sys.argv[1], sys.argv[2]
CONSOLIDATE = "--consolidate" in sys.argv[3:]
REJECTED = re.compile(r"(?i)\brejected\b|test sentence|\btest \[cite|formatter|could not complete")


def load(p):
    t = open(p, encoding="utf-8-sig").read()
    return json.loads(t[t.find("{"):])


subs, rows = [], []
for p in sorted(glob.glob(os.path.join(ev_dir, "results-*.json"))):
    label = os.path.basename(p)[8:-5]
    d = load(p)
    for s in d.get("Submissions", []):
        x = s.get("Execution") or {}
        if not x or x.get("Status") not in ("Completed", "Failed"):
            continue  # cancelled or timed out before it finished; rerun separately
        subs.append(s)
        tools = x.get("ToolExecutions") or []
        searches = [t for t in tools if "search_enterprise" in t["Title"]]
        skills = x.get("Skills") or []
        notes = " ".join(r.get("Reasoning") or "" for r in x.get("RubricResults") or [])
        mins = ""
        if x.get("StartDateTime") and x.get("EndDateTime"):
            from datetime import datetime
            f = lambda v: datetime.fromisoformat(v[:19])
            mins = round((f(x["EndDateTime"]) - f(x["StartDateTime"])).total_seconds() / 60, 1)
        m = re.search(r"C-2026-(\d{5})", (s.get("Sample") or {}).get("Prompt") or "")
        rows.append({
            "claim": m.group(1) if m else label, "status": x.get("Status"), "retries": s.get("RetryCount"),
            "skill_runs": len(skills),
            "overflow": sum(1 for k in skills if (k.get("ErrorResponse") or {}).get("ErrorCodeString") == "ContextLength"),
            "calls": len(tools), "searches": len(searches),
            "scoped": sum("path:" in json.dumps(t["Inputs"]) for t in searches),
            "teams": sum(t["Title"].startswith("teams__") for t in tools),
            "mcp": sum("__get_claim_dossier" in t["Title"] or "__create_" in t["Title"]
                       or "__request_" in t["Title"] or "__escalate_" in t["Title"] for t in tools),
            "tool_k": sum(len(t.get("Output") or "") for t in tools) // 1000,
            "minutes": mins,
            "rubric": round(sum(r["Score"] for r in x.get("RubricResults") or [] if r.get("Score") is not None)
                            / max(1, sum(1 for r in x.get("RubricResults") or [] if r.get("Score") is not None)), 3),
            "rejected_handin": bool(REJECTED.search(notes)),
        })

os.makedirs(stage_dir, exist_ok=True)
merged = {"EvaluationResults": {"Results": [], "StatusMessage": f"merged from {len(rows)} per-claim jobs"},
          "Submissions": subs}
json.dump(merged, open(os.path.join(stage_dir, "eval-results-samples.json"), "w", encoding="utf-8"))

cols = ["claim", "status", "rubric", "calls", "mcp", "searches", "scoped", "teams", "tool_k",
        "minutes", "skill_runs", "overflow", "retries", "rejected_handin"]
lines = ["| " + " | ".join(cols) + " |", "|" + " --- |" * len(cols)]
rows.sort(key=lambda r: r["claim"])
lines += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
n = len(rows) or 1
avg = lambda k: round(sum(r[k] for r in rows if isinstance(r[k], (int, float))) / n, 1)
lines += ["", f"Claims: {len(rows)} · mean rubric {avg('rubric')} · mean calls {avg('calls')} · "
              f"mean tool output {avg('tool_k')}k · overflows {sum(r['overflow'] for r in rows)} · "
              f"rejected hand-ins {sum(r['rejected_handin'] for r in rows)}"]
open(os.path.join(stage_dir, "run-summary.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))

py = os.path.join(".venv", "Scripts", "python.exe")
subprocess.run([py, os.path.join("scripts", "score_ground_truth.py"),
                os.path.join(stage_dir, "eval-results-samples.json"), "--out", stage_dir])

if CONSOLIDATE:
    snaps = sorted(glob.glob(os.path.join(ev_dir, "db-after-*.txt")))
    with open(os.path.join(ev_dir, "db-snapshots.txt"), "a", encoding="utf-8") as out:
        for p in snaps:
            body = [l for l in open(p, encoding="utf-8-sig").read().splitlines() if l.strip()]
            out.write(f"===== {os.path.basename(p)[9:-4]} (after the job, before reset)\n" + "\n".join(body) + "\n\n")
    merged_ids = {s.get("ExecutionId") for s in subs}
    for p in glob.glob(os.path.join(ev_dir, "results-*.json")):
        if {s.get("ExecutionId") for s in load(p).get("Submissions", [])} <= merged_ids:
            os.remove(p)
    for p in snaps:
        os.remove(p)
    print(f"consolidated: {len(snaps)} snapshots -> db-snapshots.txt; per-job results removed")
