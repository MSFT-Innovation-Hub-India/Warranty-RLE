"""Population generator: assets, telemetry, claims, and computed ground truth.

Claims are authored as explicit slices rather than sampled at random, because
the trap distribution in guide 03 section 10 is a requirement, not an outcome.
Every claim declares the slice it belongs to, and the generator refuses to write
anything if the distribution drifts from the design.

    .venv/Scripts/python.exe build/populate.py
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from adjudicate import (Asset, Claim, adjudicate, add_months, d,
                        ENTITIES, OPERATIONS)

OUT = Path(__file__).resolve().parent.parent / "out"
DATA = OUT / "data"

ASSETS: dict[str, Asset] = {}
CLAIMS: list[tuple[str, str, Claim]] = []      # (split, slice, claim)


def asset(serial_no: int, family: str, commissioned: str | None,
          dealer: str = "D-IN-01", customer: str = "C-LIT",
          region: str = "India", known: bool = True) -> Asset:
    prefix = "CIE-4000-CH-" if family == "4000-CH" else "CIE-2200-AC-"
    serial = f"{prefix}{serial_no:05d}"
    if serial in ASSETS:
        # Silently returning the existing asset once destroyed the whole
        # abstention slice: a claim asked for a serial with no commissioning
        # date and got back one that had a date, so it approved instead of
        # abstaining. Two of three samples were wrong and nothing said so.
        existing = ASSETS[serial]
        if (existing.commissioning_date != commissioned
                or existing.known != known
                or existing.dealer_id != dealer):
            raise ValueError(
                f"serial collision on {serial}: already defined as "
                f"commissioned={existing.commissioning_date!r} known={existing.known} "
                f"dealer={existing.dealer_id}, redefined as "
                f"commissioned={commissioned!r} known={known} dealer={dealer}"
            )
        return existing
    install = (d(commissioned) - timedelta(days=23)).isoformat() if commissioned else "2024-02-01"
    a = Asset(serial=serial, family=family, dealer_id=dealer, customer_id=customer,
              region=region, install_date=install, commissioning_date=commissioned,
              known=known)
    ASSETS[serial] = a
    return a


def claim(split: str, slice_: str, cid: str, a: Asset, op: str, repair: str,
          hours: float, part: str | None, fitted: str | None,
          running: int | None = 3000, **kw) -> None:
    c = Claim(claim_id=cid, serial=a.serial, dealer_id=a.dealer_id,
              repair_date=repair,
              submitted_date=(d(repair) + timedelta(days=6)).isoformat(),
              op_code=op, claimed_hours=hours, claimed_part=part,
              part_fitted=fitted, hours_at_repair=running, **kw)
    CLAIMS.append((split, slice_, c))


# ---------------------------------------------------------------------------
# the claim slices - guide 03 section 10
# ---------------------------------------------------------------------------

_counter = [0]


def cid() -> str:
    _counter[0] += 1
    return f"C-2026-{4100 + _counter[0]:05d}"


def build_slices() -> None:
    # --- straightforward covered -------------------------------------
    # Varied across family, component, part and date. Near-identical samples
    # inflate an eval set's apparent confidence and, in a training set, teach
    # memorisation of one shape instead of the rule behind it. Kept on D-IN-01
    # so the handling uplift (trap 8) does not bleed into a control slice.
    simple = [
        ("4000-CH", 1050, "2025-03-15", "CTRL-BD-RR",  "P-44900",   "2026-05-10", 2400),
        ("4000-CH", 1052, "2025-01-08", "COND-FAN-RR", "P-44520",   "2026-02-18", 1900),
        ("2200-AC",  320, "2025-05-02", "SEAL-KIT-RR", "P-22120",   "2026-04-22", 2750),
        ("4000-CH", 1054, "2025-02-11", "FILT-HSG-RR", "P-44080",   "2026-06-30", 3100),
        ("2200-AC",  322, "2025-04-19", "BEARING-RR",  "P-22200",   "2026-01-15", 2200),
        ("4000-CH", 1056, "2025-06-01", "HYD-PUMP-RR", "P-44210",   "2026-07-08", 2600),
        ("2200-AC",  324, "2025-03-27", "MOTOR-RR",    "P-22610",   "2026-05-30", 3050),
        ("4000-CH", 1058, "2025-07-14", "DIAG-FIELD",  None,        "2026-08-05", 1450),
    ]
    for split, picks in (("eval", simple[:3]), ("train", simple[3:])):
        for fam, sn, com, op, part, rep_date, hrs in picks:
            a = asset(sn, fam, com)
            claim(split, "covered-simple", cid(), a, op, rep_date,
                  OPERATIONS[op]["flat_hours"], part, part, hrs)

    # --- straightforward declined ------------------------------------
    declined = [
        ("4000-CH", 1900, "2023-06-01", "CTRL-BD-RR",  "P-44900", "2026-05-10", 5200),
        ("2200-AC",  330, "2023-02-14", "SEAL-KIT-RR", "P-22120", "2026-03-03", 6100),
        ("4000-CH", 1902, "2022-11-20", "COND-FAN-RR", "P-44520", "2026-06-12", 7400),
        ("2200-AC",  332, "2023-08-09", "BEARING-RR",  "P-22200", "2026-04-27", 5800),
        ("4000-CH", 1904, "2023-04-05", "FILT-HSG-RR", "P-44080", "2026-07-19", 6600),
    ]
    for split, picks in (("eval", declined[:2]), ("train", declined[2:])):
        for fam, sn, com, op, part, rep_date, hrs in picks:
            a = asset(sn, fam, com)
            claim(split, "declined-simple", cid(), a, op, rep_date,
                  OPERATIONS[op]["flat_hours"], part, part, hrs)

    # --- bulletin precedence: traps 1, 2, 5 --------------------------
    precedence = [
        ("4000-CH", 1700, "2024-04-04", "HYD-PUMP-RR",  "2026-06-18", 4120, "P-44120-A"),
        ("4000-CH", 1640, "2024-04-04", "COMP-RR",      "2026-07-02", 4400, "P-44310"),
        ("4000-CH", 1950, "2024-09-01", "CTRL-BD-RR",   "2026-05-01", 3000, "P-44900"),
        ("2200-AC",  800, "2024-03-01", "VALVE-PLT-RR", "2026-06-01", 3000, "P-22450-C"),
        ("2200-AC",  600, "2024-03-01", "VALVE-PLT-RR", "2026-06-01", 3000, "P-22450-C"),
    ]
    for split, reps in (("eval", [0]), ("train", [1, 2])):
        for rep in reps:
            for fam, sn, com, op, rep_date, hrs, part in precedence:
                a = asset(sn + rep, fam, com)
                claim(split, "precedence", cid(), a, op, rep_date,
                      OPERATIONS[op]["flat_hours"], part, part, hrs)

    # --- serial boundary: trap 4 -------------------------------------
    # Training serials must differ from the eval ones: the same serial gives the
    # same asset, and the same repair then gives a claim identical to the eval
    # claim in every field, which leaks eval answers into training.
    for split, serials in (("eval", [1199, 1200, 1850, 1851]),
                           ("train", [1198, 1201, 1848, 1849, 1852, 1853])):
        for sn in serials:
            a = asset(sn, "4000-CH", "2024-04-04")
            claim(split, "serial-boundary", cid(), a, "HYD-PUMP-RR",
                  "2026-06-18", 5.0, "P-44120-A", "P-44120-A", 4120)

    # --- dual-limit expiry: trap 3 -----------------------------------
    dual = [
        (1400, "2025-06-01", "2026-06-01", 8400),   # hours exceeded, months fine
        (1410, "2023-02-01", "2026-06-01", 2100),   # months exceeded, hours fine
        (1420, "2023-07-01", "2026-06-20", 7900),   # close on both
    ]
    for split, reps in (("eval", [0]), ("train", [3, 6])):
        for rep in reps:
            for sn, com, rep_date, hrs in dual:
                a = asset(sn + rep, "4000-CH", com)
                claim(split, "dual-limit", cid(), a, "HYD-PUMP-RR", rep_date,
                      5.5, "P-44120-A", "P-44120-A", hrs)

    # --- valuation: traps 7, 8, 9, 10 --------------------------------
    # Serials are held below 1500 on purpose. Above 1500 the stale applicability
    # index (trap 1) also fires, and a valuation sample that carries two traps
    # cannot attribute a lost point to either. Principle 6: traps stay separate.
    valuation = [
        # Trap 7, flavour (a): the partner claimed the old number and the service
        # history shows a different part was actually fitted. Only the database
        # can tell you that, and policy 4.2 prices what was fitted.
        ("D-IN-02", 1440, "2024-10-01", "HYD-PUMP-RR", "2026-06-18", 8.0, "P-44120",   "P-44120-A"),
        ("D-IN-01", 1442, "2024-10-01", "COMP-RR",     "2026-03-31", 9.0, "P-44310",   "P-44310"),
        ("D-IN-01", 1444, "2024-10-01", "COMP-RR",     "2026-04-01", 9.0, "P-44310",   "P-44310"),
        # Trap 7, flavour (b): the part claimed IS the part fitted, but it has
        # been superseded, so the superseding part's price applies anyway. The
        # money is right only if the price list supersession column is read.
        ("D-IN-02", 1446, "2025-01-10", "FILT-HSG-RR", "2026-05-20", 3.5, "P-44080",   "P-44080"),
        ("D-IN-01", 1448, "2025-01-10", "HYD-PUMP-RR", "2026-05-20", 4.0, "P-44120-A", "P-44120-A"),
        ("D-IN-02", 1450, "2025-02-01", "CTRL-BD-RR",  "2026-06-05", 2.5, "P-44900",   "P-44900"),
    ]
    for split, reps in (("eval", [0]), ("train", [12, 24])):
        for rep in reps:
            for dealer, sn, com, op, rep_date, hrs, part, fitted in valuation:
                a = asset(sn + rep, "4000-CH", com, dealer=dealer)
                claim(split, "valuation", cid(), a, op, rep_date, hrs, part, fitted, 3000)

    # --- stale deck: trap 6 (an ordinary claim; the deck is the lure) -
    deck = [
        (1300, "2024-02-20", "HYD-PUMP-RR", "P-44120-A", "2026-08-12", 5300),
        (1302, "2024-05-06", "COMP-RR",     "P-44310",   "2026-09-01", 4700),
        (1304, "2024-03-18", "HYD-PUMP-RR", "P-44120-A", "2026-07-24", 5900),
        (1306, "2024-06-11", "COMP-RR",     "P-44310",   "2026-08-29", 4100),
        (1308, "2024-01-30", "FILT-HSG-RR", "P-44080-B", "2026-09-14", 6200),
    ]
    for split, picks in (("eval", deck[:2]), ("train", deck[2:])):
        for sn, com, op, part, rep_date, hrs in picks:
            a = asset(sn, "4000-CH", com)
            claim(split, "stale-deck", cid(), a, op, rep_date,
                  OPERATIONS[op]["flat_hours"], part, part, hrs)

    # --- authority: trap 11 ------------------------------------------
    # Amounts chosen to land in each authority tier: 18,400 (tier 1),
    # 67,400 (tier 2), 312,000 (tier 3), 742,000 (tier 4). A model that ignores
    # the matrix and always names one approver cannot pass all four.
    authority = [
        (1960, "CTRL-BD-RR",  "P-44900",   67400),
        (1962, "HYD-PUMP-RR", "P-44120-A", 312000),
        (1964, "CTRL-BD-RR",  "P-44900",   18400),
        (1966, "COMP-RR",     "P-44310",   742000),
        (1968, "COND-FAN-RR", "P-44520",   43800),
    ]
    for split, picks in (("eval", authority[:2]), ("train", authority[2:])):
        for sn, op, part, amount in picks:
            a = asset(sn, "4000-CH", "2024-09-01")
            claim(split, "authority", cid(), a, op, "2026-05-01",
                  OPERATIONS[op]["flat_hours"], part, part, 3000,
                  goodwill_requested=amount)

    # --- abstention: trap 12 ------------------------------------------
    for split, reps in (("eval", [0]), ("train", [1, 2])):
        for rep in reps:
            a = asset(2100 + rep, "4000-CH", None)
            claim(split, "abstention", cid(), a, "HYD-PUMP-RR", "2026-06-18",
                  5.5, "P-44120-A", "P-44120-A", 3000)

            a = asset(9990 + rep, "4000-CH", "2024-10-01", known=False)
            claim(split, "abstention", cid(), a, "HYD-PUMP-RR", "2026-06-18",
                  5.5, "P-44120-A", "P-44120-A", 3000)

            # commissioned recently enough that the time limit has NOT run out:
            # only then does the missing hours reading decide the outcome
            a = asset(2110 + rep, "4000-CH", "2025-10-01")
            claim(split, "abstention", cid(), a, "HYD-PUMP-RR", "2026-06-18",
                  5.5, "P-44120-A", "P-44120-A", None)

    # --- exclusion and its reversal: reserve trap, training only ------
    # Policy 5.2 excludes fluid-contamination damage; TSB-C-0043 reverses that
    # exclusion where the contamination came from the filter housing defect.
    # The inspection report is what tells the two apart, so these claims are the
    # only ones that force a document in 06-ClaimEvidence to be opened.
    for sn, com, from_housing in ((1360, "2025-06-01", True),
                                  (1362, "2025-06-01", False),
                                  (1364, "2025-04-10", True),
                                  (1366, "2025-04-10", False)):
        a = asset(sn, "4000-CH", com)
        claim("train", "exclusion", cid(), a, "HYD-PUMP-RR", "2026-06-01",
              5.5, "P-44120-A", "P-44120-A", 3000,
              exclusion_flags=["5.2"], contamination_from_filter_housing=from_housing)

    # --- repair warranty: reserve trap, training only -----------------
    # The corpus supports it fully; no evaluation samples are written yet, so it
    # is available to harden the eval set at stage 3 without touching the world.
    for i in range(2):
        a = asset(1980 + i, "4000-CH", "2023-01-01")
        claim("train", "repair-warranty", cid(), a, "CTRL-BD-RR", "2026-06-01",
              1.5, "P-44900", "P-44900", 6100,
              prior_claim={"claim_id": "C-2026-03110",
                           "completed_date": "2026-04-20", "component": "controls"})


def pad_assets(target: int = 120) -> None:
    """Filler so that an asset-registry lookup is real work, not a two-row table."""
    customers = [c["customer_id"] for c in ENTITIES["customers"]]
    dealers = ["D-IN-01", "D-IN-02", "D-EM-01", "D-AP-01"]
    regions = {"D-IN-01": "India", "D-IN-02": "India",
               "D-EM-01": "EMEA", "D-AP-01": "APAC"}
    i = 0
    while len(ASSETS) < target:
        fam = "4000-CH" if i % 2 == 0 else "2200-AC"
        num = (1600 + i) if fam == "4000-CH" else (900 + i)
        prefix = "CIE-4000-CH-" if fam == "4000-CH" else "CIE-2200-AC-"
        if f"{prefix}{num:05d}" in ASSETS:
            i += 1
            continue
        dealer = dealers[i % 4]
        asset(num, fam, f"2024-{(i % 12) + 1:02d}-{(i % 27) + 1:02d}",
              dealer=dealer, customer=customers[i % len(customers)],
              region=regions[dealer])
        i += 1
        if i > 2000:
            break


def telemetry() -> list[dict]:
    """Monthly readings that pass exactly through each claim's hours-at-repair."""
    anchors = {c.serial: (c.repair_date, c.hours_at_repair)
               for _, _, c in CLAIMS if c.hours_at_repair is not None}

    # Assets whose claim carries no running-hours reading must have NO telemetry
    # at all. Generating a default ramp for them would quietly disarm the third
    # abstention path: the agent would find a reading and answer instead of
    # reporting the gap.
    no_telemetry = {c.serial for _, _, c in CLAIMS if c.hours_at_repair is None}

    rows = []
    for serial, a in ASSETS.items():
        if not a.known or not a.commissioning_date or serial in no_telemetry:
            continue
        start = d(a.commissioning_date)
        if serial in anchors:
            rep, hrs = anchors[serial]
            months = max(1, (d(rep).year - start.year) * 12 + d(rep).month - start.month)
            rate = hrs / months
        else:
            rate = 180.0
        m = 0
        while add_months(start, m) <= date(2026, 9, 1):
            rows.append({"serial": serial,
                         "as_of_date": add_months(start, m).isoformat(),
                         "running_hours": int(round(rate * m))})
            m += 1
    return rows


def main() -> None:
    build_slices()
    pad_assets()
    DATA.mkdir(parents=True, exist_ok=True)

    records = []
    for split, slice_, c in CLAIMS:
        a = ASSETS[c.serial]
        adj = adjudicate(c, a)
        records.append({"split": split, "slice": slice_,
                        "claim": dict(c.__dict__), "adjudication": adj.to_dict()})

    by_split = Counter(r["split"] for r in records)
    eval_slices = Counter(r["slice"] for r in records if r["split"] == "eval")
    expected = {"covered-simple": 3, "declined-simple": 2, "precedence": 5,
                "serial-boundary": 4, "dual-limit": 3, "valuation": 6,
                "stale-deck": 2, "authority": 2, "abstention": 3}

    problems = []
    if by_split["eval"] != 30:
        problems.append(f"eval count {by_split['eval']} != 30")
    for slice_, want in expected.items():
        if eval_slices[slice_] != want:
            problems.append(f"eval slice {slice_}: {eval_slices[slice_]} != {want}")
    if by_split["train"] < 45:
        problems.append(f"train count {by_split['train']} < 45")

    decisions = Counter(r["adjudication"]["decision"] for r in records)
    for needed in ("approve", "decline", "request_evidence", "escalate"):
        if decisions[needed] == 0:
            problems.append(f"no {needed} outcomes generated")

    dupes = [k for k, v in Counter(r["claim"]["claim_id"] for r in records).items() if v > 1]
    if dupes:
        problems.append(f"duplicate claim ids: {dupes[:5]}")

    def _fingerprint(c: dict) -> str:
        return json.dumps({k: v for k, v in c.items() if k not in ("claim_id", "submitted_date")},
                          sort_keys=True)
    twins = Counter(_fingerprint(r["claim"]) for r in records)
    twin_ids = [r["claim"]["claim_id"] for r in records if twins[_fingerprint(r["claim"])] > 1]
    if twin_ids:
        problems.append(f"claims identical apart from id (eval/train leakage): {twin_ids[:8]}")

    for r in records:
        a, c = r["adjudication"], r["claim"]
        if r["slice"] == "abstention" and a["decision"] != "request_evidence":
            problems.append(f"abstention claim {c['claim_id']} decides {a['decision']}, not request_evidence")

    tele = telemetry()
    (DATA / "assets.json").write_text(
        json.dumps([a.__dict__ for a in ASSETS.values()], indent=2), encoding="utf-8")
    (DATA / "telemetry.json").write_text(json.dumps(tele, indent=2), encoding="utf-8")
    (DATA / "claims.json").write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"assets      {len(ASSETS)}")
    print(f"telemetry   {len(tele)} rows")
    print(f"claims      {len(records)}  (eval {by_split['eval']} / train {by_split['train']})")
    print(f"decisions   {dict(decisions)}")
    print(f"eval slices {dict(eval_slices)}")
    if problems:
        print("\nDESIGN CONFORMANCE FAILURES:")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    print("\nDesign conformance: OK")


if __name__ == "__main__":
    main()
