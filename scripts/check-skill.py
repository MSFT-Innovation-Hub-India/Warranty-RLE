"""Check a skill's instructions before applying them.

    python scripts/check-skill.py <skill.md or instructions.txt> <rubrics.json>

Fails (exit 1) if the instructions share a 5-word phrase with the rubrics (the
standard lives in the rubrics, which the grader sees and the model does not), or
contain anything that would hand the agent an answer: a claim number, a serial
number, a rupee or euro amount, or a named governing instrument for a case.
"""
import json
import re
import sys


def grams(text: str, n: int = 5) -> set[str]:
    w = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def main() -> int:
    skill_path, rubrics_path = sys.argv[1], sys.argv[2]
    text = open(skill_path, encoding="utf-8-sig").read()
    if "## Instructions" in text:
        text = text.split("## Instructions", 1)[1]
    rubrics = json.load(open(rubrics_path, encoding="utf-8-sig"))
    rtext = " ".join([r.get("RubricName", "") + " " + r.get("Description", "") + " " +
                      " ".join(r.get("ChecklistItems", [])) for r in rubrics])
    problems = []
    shared = sorted(grams(text) & grams(rtext))
    if shared:
        problems.append(f"shares {len(shared)} 5-word phrase(s) with the rubrics: {shared[:8]}")
    for label, pat in [("claim number", r"\bC-\d{4}-\d{5}\b"),
                       ("serial number", r"\bCIE-\d{4}-[A-Z]{2}-\d{5}\b"),
                       ("amount", r"(?:₹|INR\s?|EUR\s?|€)\s?\d[\d,]*"),
                       ("bulletin code", r"\bTSB-[A-Z]-\d{4}\b")]:
        hits = sorted(set(re.findall(pat, text)))
        if hits:
            problems.append(f"contains {label}(s): {hits[:8]}")
    if problems:
        print("FAIL")
        for p in problems:
            print("  -", p)
        return 1
    print("OK: no rubric phrases, no claim-specific answers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
