"""Score agent answers against the ground truth.

The rubric score says how well an answer *reads*; this says whether it is
*right*. For each answer it compares three things with the expected
adjudication in out/data/claims.json, the same engine output that
GROUND-TRUTH.md is rendered from:

    decision            approve | decline | request_evidence | escalate
    governing           the instrument that governs (TSB-…, ADD-…, POL-…)
    total payable       for approvals, within ±1 of the expected amount

Extraction is deterministic, with no model involved. Anything it cannot read
confidently is marked "review" rather than guessed.

Inputs, any mix of:
  * an evaluation results file   (frontier-tuning evaluate results <job> -o json)
  * single execution files        (frontier-tuning chat … --wait -o json, executions get -o json)
  * folders containing either

    .venv/Scripts/python.exe build/score_ground_truth.py <inputs…> --out <stage folder>
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAIMS = ROOT / "out" / "data" / "claims.json"

CLAIM_RE = re.compile(r"\bC-\d{4}-\d{5}\b")
INSTRUMENT_RE = re.compile(r"\b(TSB-[A-Z]-\d{4}|ADD-[A-Z]{2}-\d\.\d|POL-WAR-\d\.\d|MTX-GW-\d)\b")
AMOUNT_RE = re.compile(r"(?:₹|INR\s?|Rs\.?\s?|EUR\s?|€)\s?(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+(?:\.\d+)?)")
LEAD_CHARS = 600

# Order matters: negative and "can't decide" phrasings are checked before the
# bare word "covered", so "not covered" never reads as an approval.
DECISION_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("request_evidence", re.compile(
        r"cannot (?:yet )?(?:be )?(?:finally )?(?:decided|determined)|can't (?:yet )?be (?:finally )?(?:decided|determined)|"
        r"cannot yet decide|not yet be decided|on hold|\bhold (?:for|pending) (?:evidence|commissioning|the)|"
        r"\bhold\b[^.\n]{0,20}\b(?:evidence|request)|hold the claim|claim (?:is|should be|has been) (?:placed on )?held|"
        r"request(?:ing|ed)? (?:the )?(?:missing|commissioning|evidence|certificate|inspection)|"
        r"evidence request|insufficient (?:records|evidence)", re.I)),
    ("escalate", re.compile(r"\bescalat\w*", re.I)),
    ("decline", re.compile(
        r"\bdeclin\w*|\bnot covered\b|\bisn't covered\b|\bis not covered\b|\bout of warranty\b|"
        r"\boutside (?:the )?(?:warranty|coverage)\b|\breject\w*", re.I)),
    ("approve", re.compile(r"\bapprov\w*|\bis covered\b|\bcovered under\b|\bcovered by\b|\bwithin (?:the )?(?:warranty|coverage)\b", re.I)),
]


def load_expected() -> dict[str, dict]:
    rows = json.loads(CLAIMS.read_text(encoding="utf-8"))
    out = {}
    for r in rows:
        a = r["adjudication"]
        out[a["claim_id"]] = {
            "split": r["split"], "slice": r["slice"],
            "decision": a["decision"],
            "governing": a.get("governing_instrument"),
            "total": a.get("total_payable"),
            "currency": a.get("currency"),
        }
    return out


# ---------------------------------------------------------------------------
# reading platform output
# ---------------------------------------------------------------------------

def _get(d: dict, *names):
    for n in names:
        if isinstance(d, dict) and n in d and d[n] is not None:
            return d[n]
    return None


def _text(v) -> str:
    """Plain text from a response, which is a string in `chat` output and a list
    of parts ([{"Content": "…"}]) in `evaluate results --samples`."""
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        parts = []
        for p in v:
            if isinstance(p, dict):
                c = _get(p, "Content", "content", "Text", "text")
                if c is not None:
                    parts.append(c if isinstance(c, str) else json.dumps(c, ensure_ascii=False))
            elif isinstance(p, str):
                parts.append(p)
        if parts:
            return "\n".join(parts)
    return json.dumps(v, ensure_ascii=False)


def _rubric_score(execution: dict) -> float | None:
    """Mean rubric score for one execution, wherever the platform put it."""
    scores = []
    for skill in _get(execution, "Skills", "skills") or []:
        for rr in _get(skill, "RubricResults", "rubricResults") or []:
            s = _get(rr, "Score", "score")
            if isinstance(s, (int, float)):
                scores.append(float(s))
    for rr in _get(execution, "RubricResults", "rubricResults") or []:
        s = _get(rr, "Score", "score")
        if isinstance(s, (int, float)):
            scores.append(float(s))
    return round(sum(scores) / len(scores), 3) if scores else None


def _as_execution(obj: dict) -> dict | None:
    if not isinstance(obj, dict):
        return None
    if _get(obj, "Response", "response") is not None or _get(obj, "UserQuery", "userQuery") is not None:
        return obj
    inner = _get(obj, "Execution", "execution")
    return inner if isinstance(inner, dict) else None


def read_executions(path: Path) -> list[dict]:
    """Return [{id, prompt, response, rubric}] from one file of any supported shape."""
    raw = path.read_text(encoding="utf-8-sig")
    raw = raw[raw.find("{") if raw.lstrip()[:1] != "[" else raw.find("["):]
    data = json.loads(raw)
    candidates = []
    if isinstance(data, list):
        candidates = data
    elif isinstance(data, dict):
        subs = _get(data, "Submissions", "submissions", "Results", "results", "Samples", "samples")
        candidates = subs if isinstance(subs, list) else [data]
    out = []
    for c in candidates:
        ex = _as_execution(c)
        if not ex:
            continue
        prompt = _text(_get(ex, "UserQuery", "userQuery") or _get(c, "Prompt", "prompt"))
        out.append({
            "id": _get(ex, "Id", "id", "ExecutionId", "executionId") or "",
            "prompt": prompt,
            "response": _text(_get(ex, "Response", "response")),
            "rubric": _rubric_score(ex),
            "source": path.name,
        })
    return out


# ---------------------------------------------------------------------------
# extracting the agent's answer
# ---------------------------------------------------------------------------

NEGATION_RE = re.compile(r"\b(?:no|not|without|nor|never|no need to|doesn't need|does not need|isn't|is not)\b[^.;\n]{0,25}$", re.I)
# "no draft adjudication, evidence request, or escalation was created": the negation
# reaches the last item of a list, however far away it is.
LIST_NEGATION_RE = re.compile(r"\b(?:no|not|neither)\b[^.;:\n]{0,100},?\s+(?:or|nor)\s+$", re.I)


def _first_unnegated(pat: re.Pattern, text: str) -> int | None:
    for m in pat.finditer(text):
        before = text[max(0, m.start() - 120):m.start()]
        if not NEGATION_RE.search(before[-40:]) and not LIST_NEGATION_RE.search(before):
            return m.start()
    return None


def extract_decision(response: str) -> str | None:
    """Read the disposition from the opening of the answer.

    Escalation and evidence requests are dispositions in their own right: an
    answer that says "not covered … escalate the goodwill request" is an
    escalation. So those two win when present and not negated; otherwise the
    earliest of decline/approve wins.
    """
    lead = response[:LEAD_CHARS]
    pats = dict(DECISION_PATTERNS)
    for label in ("request_evidence", "escalate"):
        if _first_unnegated(pats[label], lead) is not None:
            return label
    found = []
    for label in ("decline", "approve"):
        pos = _first_unnegated(pats[label], lead)
        if pos is not None:
            found.append((pos, label))
    if not found:
        return None
    found.sort()
    return found[0][1]


def extract_governing(response: str) -> str | None:
    sentences = re.split(r"(?<=[.!?\n])\s+", response)
    for s in sentences:
        if re.search(r"govern|applies|applicable instrument|covered under|under\b", s, re.I):
            m = INSTRUMENT_RE.search(s)
            if m:
                return m.group(1)
    m = INSTRUMENT_RE.search(response)
    return m.group(1) if m else None


def _num(s: str) -> float:
    return float(s.replace(",", ""))


def extract_total(response: str) -> float | None:
    lines = response.splitlines()
    for line in lines:
        if re.search(r"\btotal\b|\bpayable\b|\bamount payable\b", line, re.I):
            amounts = [_num(a) for a in AMOUNT_RE.findall(line)]
            if amounts:
                return max(amounts)
    amounts = [_num(a) for a in AMOUNT_RE.findall(response)]
    return max(amounts) if amounts else None


# ---------------------------------------------------------------------------

def score(rows: list[dict], expected: dict[str, dict]) -> list[dict]:
    out = []
    for r in rows:
        ids = CLAIM_RE.findall(r["prompt"]) or CLAIM_RE.findall(r["response"])
        claim = ids[0] if ids else None
        exp = expected.get(claim) if claim else None
        got_dec = extract_decision(r["response"])
        got_gov = extract_governing(r["response"])
        got_tot = extract_total(r["response"])
        row = {
            "claim": claim or "?", "slice": exp["slice"] if exp else "?",
            "exp_decision": exp["decision"] if exp else "?", "got_decision": got_dec or "review",
            "exp_governing": (exp["governing"] or "—") if exp else "?", "got_governing": got_gov or "—",
            "exp_total": exp["total"] if exp else None, "got_total": got_tot,
            "rubric": r["rubric"], "execution": r["id"], "source": r["source"],
        }
        if not exp:
            row.update(decision_ok=None, governing_ok=None, total_ok=None, correct=None, note="claim not found")
            out.append(row)
            continue
        dec_ok = None if got_dec is None else (got_dec == exp["decision"])
        gov_ok = (got_gov == exp["governing"]) if exp["governing"] else True
        if exp["decision"] == "approve" and exp["total"]:
            tot_ok = None if got_tot is None else abs(got_tot - exp["total"]) <= 1
        else:
            tot_ok = True
        notes = []
        if dec_ok is None:
            notes.append("decision unclear")
        if exp["decision"] == "approve" and got_dec not in (None, "approve"):
            # A held or declined answer has no payable; any figure read is contingent or incidental.
            notes.append(f"{got_dec.replace('_', ' ')} given, so payable not assessed")
            tot_ok = False
        elif tot_ok is None:
            notes.append("no amount stated")
        correct = None if (dec_ok is None) else (dec_ok and gov_ok and tot_ok is True)
        row.update(decision_ok=dec_ok, governing_ok=gov_ok, total_ok=tot_ok, correct=correct,
                   note="; ".join(notes))
        out.append(row)
    return out


def _mark(v) -> str:
    return "✅" if v is True else "❌" if v is False else "❓"


def _pct(n: int, d: int) -> str:
    return f"{n}/{d} ({(100 * n / d):.0f}%)" if d else "—"


def report(rows: list[dict], label: str) -> str:
    n = len(rows)
    known = [r for r in rows if r["correct"] is not None]
    rub = [r["rubric"] for r in rows if r["rubric"] is not None]
    lines = [f"# Ground-truth check — {label}", "",
             f"Scored by `build/score_ground_truth.py` against `out/data/claims.json` (the source of GROUND-TRUTH.md).", "",
             "| Measure | Result |", "| --- | --- |",
             f"| Answers scored | {n} |",
             f"| Decision correct | {_pct(sum(1 for r in rows if r['decision_ok'] is True), n)} |",
             f"| Governing instrument correct | {_pct(sum(1 for r in rows if r['governing_ok'] is True), n)} |",
             f"| Payable correct (approvals) | {_pct(sum(1 for r in rows if r['exp_decision'] == 'approve' and r['total_ok'] is True), sum(1 for r in rows if r['exp_decision'] == 'approve'))} |",
             f"| **Fully correct** | **{_pct(sum(1 for r in known if r['correct']), n)}** |",
             f"| Needs human review | {sum(1 for r in rows if r['note'])} |",
             f"| Mean rubric score (platform) | {round(sum(rub) / len(rub), 3) if rub else '—'} |", ""]
    by = defaultdict(list)
    for r in rows:
        by[r["slice"]].append(r)
    lines += ["## By slice", "", "| Slice | Answers | Fully correct | Mean rubric score |", "| --- | --- | --- | --- |"]
    for s, rs in sorted(by.items()):
        rr = [x["rubric"] for x in rs if x["rubric"] is not None]
        lines.append(f"| {s} | {len(rs)} | {sum(1 for x in rs if x['correct'])} | {round(sum(rr) / len(rr), 3) if rr else '—'} |")
    lines += ["", "## Per answer", "",
              "| Claim | Slice | Decision exp → got | Governing exp → got | Payable exp → got | Rubric | Correct | Note |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in sorted(rows, key=lambda x: x["claim"]):
        et = f"₹{r['exp_total']:,.0f}" if r["exp_total"] else "—"
        gt = f"₹{r['got_total']:,.0f}" if r["got_total"] else "—"
        lines.append(f"| `{r['claim']}` | {r['slice']} | {r['exp_decision']} → {r['got_decision']} {_mark(r['decision_ok'])} | "
                     f"{r['exp_governing']} → {r['got_governing']} {_mark(r['governing_ok'])} | {et} → {gt} {_mark(r['total_ok'])} | "
                     f"{r['rubric'] if r['rubric'] is not None else '—'} | {_mark(r['correct'])} | {r['note']} |")
    lines += ["", "❓ = could not be read confidently; check that answer by hand against GROUND-TRUTH.md.", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", type=Path, help="result/execution JSON files or folders")
    ap.add_argument("--out", type=Path, help="folder to write ground-truth-check.md and .csv into")
    ap.add_argument("--label", default=None, help="title for the report (default: the --out folder name)")
    args = ap.parse_args()

    files = []
    for p in args.inputs:
        files += sorted(p.rglob("*.json")) if p.is_dir() else [p]
    rows = []
    for f in files:
        try:
            rows += read_executions(f)
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"skip {f}: {exc}", file=sys.stderr)
    if not rows:
        print("No executions found in the inputs.", file=sys.stderr)
        return 2

    scored = score(rows, load_expected())
    label = args.label or (args.out.name if args.out else "ad hoc")
    md = report(scored, label)
    print(md)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "ground-truth-check.md").write_text(md, encoding="utf-8")
        with (args.out / "ground-truth-check.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(scored[0].keys()))
            w.writeheader()
            w.writerows(scored)
    counts = Counter(r["got_decision"] for r in scored)
    print(f"\n{len(scored)} answers from {len(files)} file(s); decisions read: {dict(counts)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
