"""Render GROUND-TRUTH.md from the computed adjudications.

This is the human audit trail design principle 7 requires: a reviewer checks an
answer against this file, not against the model's own reasoning. It is also what
an out-of-band numeric checker reads if the grader turns out not to verify
arithmetic (guide 03 section 9.4).

    .venv/Scripts/python.exe world-builder/build/ground_truth.py
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "out"
DATA = OUT / "data"

SYMBOL = {"INR": "₹", "EUR": "€", "SGD": "S$"}
SLICE_TRAPS = {
    "covered-simple":  "-",
    "declined-simple": "-",
    "precedence":      "1, 2, 5",
    "serial-boundary": "4",
    "dual-limit":      "3",
    "valuation":       "7, 8, 9, 10",
    "stale-deck":      "6",
    "authority":       "11",
    "abstention":      "12",
    "repair-warranty": "reserve",
    "exclusion":       "reserve",
}


def money(adj: dict) -> str:
    if adj.get("total_payable") is None:
        return "-"
    return f"{SYMBOL.get(adj.get('currency', ''), '')}{adj['total_payable']:,.0f}"


def render() -> str:
    recs = json.loads((DATA / "claims.json").read_text(encoding="utf-8"))
    assets = {a["serial"]: a for a in json.loads((DATA / "assets.json").read_text(encoding="utf-8"))}

    L: list[str] = []
    L.append("# Ground truth — Contoso Industrial warranty adjudication")
    L.append("")
    L.append("**Generated. Do not edit by hand.**  ")
    L.append("`.venv/Scripts/python.exe world-builder/build/ground_truth.py`")
    L.append("")
    L.append(f"Produced {date.today().isoformat()} from `scenario/spec/` via "
             "`build/adjudicate.py`. Every row is computed by the same engine that "
             "the corpus documents are rendered from, so the expected answer and the "
             "text a model will read cannot disagree.")
    L.append("")

    counts = Counter(r["split"] for r in recs)
    dec = Counter(r["adjudication"]["decision"] for r in recs)
    L.append(f"| Split | Claims |")
    L.append(f"| --- | --- |")
    L.append(f"| Evaluation | {counts['eval']} |")
    L.append(f"| Training | {counts['train']} |")
    L.append(f"| **Total** | **{len(recs)}** |")
    L.append("")
    L.append("Outcome mix: " + ", ".join(f"**{k}** {v}" for k, v in sorted(dec.items())) + ".")
    L.append("")
    L.append("---")
    L.append("")

    for split, title in (("eval", "Evaluation set"), ("train", "Training set")):
        rows = [r for r in recs if r["split"] == split]
        L.append(f"## {title} — {len(rows)} claims")
        L.append("")
        L.append("| Claim | Slice | Traps | Serial | Decision | Governing | Payable | Code |")
        L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for r in rows:
            c, a = r["claim"], r["adjudication"]
            L.append(
                f"| `{c['claim_id']}` | {r['slice']} | {SLICE_TRAPS.get(r['slice'], '-')} "
                f"| `{c['serial']}` | **{a['decision']}** "
                f"| {a.get('governing_instrument', '—')} | {money(a)} | {a['funding_code']} |"
            )
        L.append("")

    L.append("---")
    L.append("")
    L.append("## Evaluation set — full working")
    L.append("")
    L.append("One block per evaluation claim, so a reviewer can check any answer by "
             "hand in under two minutes.")
    L.append("")

    for r in [x for x in recs if x["split"] == "eval"]:
        c, a = r["claim"], r["adjudication"]
        asset = assets[c["serial"]]
        L.append(f"### `{c['claim_id']}` — {r['slice']}")
        L.append("")
        L.append(f"**{a['decision'].upper()}** · {a.get('governing_instrument', 'no governing instrument')} "
                 f"· funding `{a['funding_code']}` · payable **{money(a)}**")
        L.append("")
        L.append("| | |")
        L.append("| --- | --- |")
        L.append(f"| Serial | `{c['serial']}` ({asset['family']}, {asset['region']}) |")
        L.append(f"| Commissioned | {asset['commissioning_date'] or '**absent from the registry**'} |")
        L.append(f"| Partner | {c['dealer_id']} |")
        L.append(f"| Operation | `{c['op_code']}` |")
        L.append(f"| Repair date | {c['repair_date']} |")
        L.append(f"| Hours at repair | {c['hours_at_repair'] if c['hours_at_repair'] is not None else '**no reading**'} |")
        L.append(f"| Claimed | {c['claimed_hours']} h"
                 + (f", part `{c['claimed_part']}`" if c['claimed_part'] else "") + " |")
        if c.get("part_fitted"):
            L.append(f"| Part fitted | `{c['part_fitted']}` |")
        if a.get("goodwill_requested") or c.get("goodwill_requested"):
            L.append(f"| Goodwill requested | {c.get('goodwill_requested')} |")
        L.append("")
        L.append(f"**Reason.** {a['reason']}")
        L.append("")

        if a.get("expiry_basis"):
            e = a["expiry_basis"]
            L.append(f"**Expiry basis.** {e['months']} months from {e['commissioning_date']} "
                     f"→ {e['expiry_date']}"
                     + (f"; limit {e['hours_limit']} h" if e.get("hours_limit") else "")
                     + (f"; at repair {e['hours_at_repair']} h" if e.get("hours_at_repair") is not None else "")
                     + ".")
            L.append("")

        if a.get("considered_instruments"):
            L.append("**Instruments considered.** " + ", ".join(
                f"`{i}`" + (" ← governs" if i == a.get("governing_instrument") else "")
                for i in a["considered_instruments"]) + ".")
            L.append("")

        if a.get("total_payable") is not None:
            sym = SYMBOL.get(a["currency"], "")
            L.append("| Component | Working | Amount |")
            L.append("| --- | --- | --- |")
            L.append(f"| Labour | {a['labour_hours_paid']} h × {sym}{a['labour_rate_used']:,} "
                     f"| {sym}{a['payable_labour']:,.0f} |")
            L.append(f"| Parts | `{a.get('part_priced', '-')}` | {sym}{a['payable_parts']:,.0f} |")
            L.append(f"| Uplift | | {sym}{a['payable_uplift']:,.0f} |")
            L.append(f"| **Total** | | **{sym}{a['total_payable']:,.0f}** |")
            L.append("")

        if a.get("missing_field"):
            L.append(f"**Missing.** `{a['missing_field']}` — required record: "
                     f"{a.get('required_record', 'n/a')}.")
            L.append("")
        if a.get("approver_role"):
            L.append(f"**Approver required.** {a['approver_role']}.")
            L.append("")
        if a.get("notes"):
            L.append("**Notes the answer must carry.**")
            L.append("")
            for n in a["notes"]:
                L.append(f"- {n}")
            L.append("")
        L.append("")

    return "\n".join(L)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    text = render()
    (OUT / "GROUND-TRUTH.md").write_text(text, encoding="utf-8")
    print(f"wrote {OUT / 'GROUND-TRUTH.md'}  ({len(text.splitlines())} lines)")
