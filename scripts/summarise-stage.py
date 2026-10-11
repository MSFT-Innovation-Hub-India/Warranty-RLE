"""Merge per-claim evaluation results and summarise a stage run.

    python scripts/summarise-stage.py climb/stage-N/raw climb/stage-N/results [--consolidate]

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


def g(d, *names):
    """First present field: the CLI 0.3.x results use PascalCase, CLI 1.0 camelCase."""
    for n in names:
        if isinstance(d, dict) and d.get(n) is not None:
            return d[n]
    return None


def rubric_scores(x):
    """(name, score) per graded rubric. A rubric the grader skipped as not applicable is
    Score None in CLI 0.3.x; in CLI 1.0 (camelCase displayName) score 0.0 with no scoreReason."""
    out = []
    for r in g(x, "RubricResults", "rubricResults") or []:
        s = g(r, "Score", "score")
        if s is None or ("displayName" in r and s == 0 and not (r.get("scoreReason") or r.get("reasoning"))):
            continue
        out.append((g(r, "RubricName", "displayName", "name"), float(s)))
    return out


subs, rows, by_rubric = [], [], {}
for p in sorted(glob.glob(os.path.join(ev_dir, "results-*.json"))):
    label = os.path.basename(p)[8:-5]
    d = load(p)
    for s in g(d, "Submissions", "submissions") or []:
        x = g(s, "Execution", "execution") or {}
        status = g(x, "Status") or g(s, "Status", "status")
        if not x or status not in ("Completed", "Failed", "Graded"):
            continue  # cancelled or timed out before it finished; rerun separately
        subs.append(s)
        tools = x.get("ToolExecutions")              # the full call list: CLI 0.3.x only
        bill = g(x, "BillingSummary", "billingSummary") or {}
        skills = g(x, "Skills", "skills") or []
        notes = " ".join(g(r, "Reasoning", "reasoning", "scoreReason") or "" for r in g(x, "RubricResults", "rubricResults") or [])
        mins = ""
        if x.get("StartDateTime") and x.get("EndDateTime"):
            from datetime import datetime
            f = lambda v: datetime.fromisoformat(v[:19])
            mins = round((f(x["EndDateTime"]) - f(x["StartDateTime"])).total_seconds() / 60, 1)
        elif bill.get("infraSeconds"):
            mins = round(bill["infraSeconds"] / 60, 1)    # CLI 1.0: platform-reported seconds (0 when not measured), not wall clock
        prompt = g(s.get("Sample") or {}, "Prompt") or g(s, "prompt") or g(x, "UserQuery", "userQuery") or ""
        m = re.search(r"C-2026-(\d{5})", prompt)
        rs = rubric_scores(x)
        for name, v in rs:
            by_rubric.setdefault(name, []).append(v)
        platform = g(s, "score")
        row = {
            "claim": m.group(1) if m else label, "status": status, "retries": g(s, "RetryCount"),
            "skill_runs": len(skills),
            "overflow": sum(1 for k in skills if (k.get("ErrorResponse") or {}).get("ErrorCodeString") == "ContextLength") if tools is not None else "",
            "calls": len(tools) if tools is not None else g(bill, "toolInvocations", "ToolInvocations"),
            "minutes": mins,
            "rubric": round(platform, 3) if isinstance(platform, (int, float)) else (round(sum(v for _, v in rs) / len(rs), 3) if rs else ""),
            "rejected_handin": bool(REJECTED.search(notes)),
        }
        if tools is not None:
            searches = [t for t in tools if "search_enterprise" in t["Title"]]
            row.update({
                "searches": len(searches),
                "scoped": sum("path:" in json.dumps(t["Inputs"]) for t in searches),
                "teams": sum(t["Title"].startswith("teams__") for t in tools),
                "mcp": sum("__get_claim_dossier" in t["Title"] or "__create_" in t["Title"]
                           or "__request_" in t["Title"] or "__escalate_" in t["Title"] for t in tools),
                "tool_k": sum(len(t.get("Output") or "") for t in tools) // 1000,
            })
        rows.append(row)

os.makedirs(stage_dir, exist_ok=True)
merged = {"EvaluationResults": {"Results": [], "StatusMessage": f"merged from {len(rows)} per-claim jobs"},
          "Submissions": subs}
json.dump(merged, open(os.path.join(stage_dir, "eval-results-samples.json"), "w", encoding="utf-8"))

cols = ["claim", "status", "rubric", "calls", "mcp", "searches", "scoped", "teams", "tool_k",
        "minutes", "skill_runs", "overflow", "retries", "rejected_handin"]
cols = [c for c in cols if any(c in r and r[c] not in ("", None) for r in rows)]   # CLI 1.0 has no per-tool detail
lines = ["| " + " | ".join(cols) + " |", "|" + " --- |" * len(cols)]
rows.sort(key=lambda r: r["claim"])
lines += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
n = len(rows) or 1
def avg(k, places=1):
    v = [r[k] for r in rows if isinstance(r.get(k), (int, float)) and not isinstance(r.get(k), bool)]
    return round(sum(v) / len(v), places) if v else "n/a"
lines += ["", f"Claims: {len(rows)} · mean rubric {avg('rubric', 3)} · mean calls {avg('calls')} · "
              f"mean tool output {avg('tool_k')}{'k' if avg('tool_k') != 'n/a' else ''} · overflows {sum(r['overflow'] for r in rows if isinstance(r.get('overflow'), int))} · "
              f"rejected hand-ins {sum(r['rejected_handin'] for r in rows)}",
          "", "Per rubric (mean over graded, skipped excluded): " +
          " · ".join(f"{k} {round(sum(v) / len(v), 3)}" for k, v in by_rubric.items())]
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
    key = lambda s: g(s, "ExecutionId", "id")
    merged_ids = {key(s) for s in subs}
    for p in glob.glob(os.path.join(ev_dir, "results-*.json")):
        if {key(s) for s in g(load(p), "Submissions", "submissions") or []} <= merged_ids:
            os.remove(p)
    for p in snaps:
        os.remove(p)
    print(f"consolidated: {len(snaps)} snapshots -> db-snapshots.txt; per-job results removed")
