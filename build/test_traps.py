"""Trap-by-trap validation of the ground-truth engine.

Every trap in guide 03 section 7 gets at least one case here, asserted against
the outcome the design says it should produce. If a trap cannot be expressed as
a passing case in this file, it is not buildable and should be removed from the
design rather than discovered later as an ambiguous sample.

    .venv/Scripts/python.exe build/test_traps.py
"""

from __future__ import annotations

from adjudicate import Asset, Claim, adjudicate

RESULTS: list[tuple[bool, str, str]] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    RESULTS.append((condition, label, detail))


def chiller(serial_no: int, commissioned: str, dealer: str = "D-IN-01",
            region: str = "India", commissioning: bool = True) -> Asset:
    return Asset(
        serial=f"CIE-4000-CH-{serial_no:05d}",
        family="4000-CH",
        dealer_id=dealer,
        customer_id="C-LIT",
        region=region,
        install_date="2024-01-10",
        commissioning_date=commissioned if commissioning else None,
    )


def compressor(serial_no: int, commissioned: str) -> Asset:
    return Asset(
        serial=f"CIE-2200-AC-{serial_no:05d}",
        family="2200-AC",
        dealer_id="D-IN-01",
        customer_id="C-WGF",
        region="India",
        install_date="2024-01-10",
        commissioning_date=commissioned,
    )


def claim(cid: str, asset: Asset, op: str, repair: str, hours: float,
          part: str | None = None, fitted: str | None = None,
          running: int | None = 3000, **kw) -> Claim:
    return Claim(
        claim_id=cid,
        serial=asset.serial,
        dealer_id=asset.dealer_id,
        repair_date=repair,
        submitted_date=repair,
        op_code=op,
        claimed_hours=hours,
        claimed_part=part,
        part_fitted=fitted,
        hours_at_repair=running,
        **kw,
    )


# ---------------------------------------------------------------------------
# trap 2 - the regional addendum is SHORTER than base policy
# ---------------------------------------------------------------------------
a = chiller(1950, "2024-09-01")                       # outside TSB-C-0051 range
# 18 months from 2024-09-01 expires 2026-03-01; base policy would still cover
# this repair at 24 months, which is exactly what the addendum takes away.
c = claim("T2-a", a, "CTRL-BD-RR", "2026-05-01", 1.5, "P-44900", "P-44900")
r = adjudicate(c, a)
check("trap-2  India addendum (18mo) governs, not policy (24mo)",
      r.governing_instrument == "ADD-IN-2.1", r.governing_instrument)
check("trap-2  declined - past the 18-month addendum expiry",
      r.decision == "decline" and r.expiry_basis["expiry_date"] == "2026-03-01",
      f"{r.decision} / {r.expiry_basis['expiry_date']}")

c = claim("T2-b", a, "CTRL-BD-RR", "2025-06-01", 1.5, "P-44900", "P-44900")
r = adjudicate(c, a)
check("trap-2  same asset inside 18 months is approved",
      r.decision == "approve" and r.funding_code == "STD", r.decision)

# ---------------------------------------------------------------------------
# trap 4 - serial-range boundaries on TSB-C-0051 (1200 - 1850)
# ---------------------------------------------------------------------------
for sn, expect_tsb in ((1199, False), (1200, True), (1850, True), (1851, False)):
    a = chiller(sn, "2024-04-04")
    c = claim(f"T4-{sn}", a, "HYD-PUMP-RR", "2026-06-18", 5.0, "P-44120-A", "P-44120-A", 4120)
    r = adjudicate(c, a)
    got = r.governing_instrument == "TSB-C-0051"
    check(f"trap-4  serial {sn} {'is' if expect_tsb else 'is not'} covered by TSB-C-0051",
          got == expect_tsb, r.governing_instrument)

# in-range but beyond the stale index (1501-1850) must raise the conflict note
a = chiller(1700, "2024-04-04")
c = claim("T1", a, "HYD-PUMP-RR", "2026-06-18", 5.0, "P-44120-A", "P-44120-A", 4120)
r = adjudicate(c, a)
check("trap-1  stale applicability index reported, document followed",
      "trap-1" in r.traps and r.decision == "approve", str(r.traps))

# below the index boundary: covered, and no conflict to report
a = chiller(1300, "2024-04-04")
c = claim("T1-b", a, "HYD-PUMP-RR", "2026-06-18", 5.0, "P-44120-A", "P-44120-A", 4120)
r = adjudicate(c, a)
check("trap-1  no index conflict reported below serial 1500",
      "trap-1" not in r.traps and r.decision == "approve", str(r.traps))

# ---------------------------------------------------------------------------
# trap 5 - superseded bulletin narrows the range (0107: 400-900, 0112: 400-750)
# ---------------------------------------------------------------------------
a = compressor(600, "2024-03-01")
c = claim("T5-a", a, "VALVE-PLT-RR", "2026-06-01", 4.0, "P-22450-C", "P-22450-C", 3000)
r = adjudicate(c, a)
check("trap-5  serial 600 covered by the superseding TSB-P-0112",
      r.governing_instrument == "TSB-P-0112", r.governing_instrument)

a = compressor(800, "2024-03-01")
c = claim("T5-b", a, "VALVE-PLT-RR", "2026-06-01", 4.0, "P-22450-C", "P-22450-C", 3000)
r = adjudicate(c, a)
check("trap-5  serial 800 NOT covered - 0112 narrowed the range, 0107 has no effect",
      r.governing_instrument == "ADD-IN-2.1", r.governing_instrument)
check("trap-5  the superseded bulletin is named and dismissed",
      any("TSB-P-0107" in n and "superseded" in n for n in r.notes), str(r.notes))

# ---------------------------------------------------------------------------
# trap 3 - dual limit: hours exceeded while months are not
# ---------------------------------------------------------------------------
a = chiller(1400, "2025-06-01")
c = claim("T3", a, "HYD-PUMP-RR", "2026-06-01", 5.0, "P-44120-A", "P-44120-A", 8400)
r = adjudicate(c, a)
check("trap-3  declined on running hours though inside the 36-month term",
      r.decision == "decline" and "running-hours" in r.reason, r.reason[:70])

# ---------------------------------------------------------------------------
# trap 9 - labour rate selected by repair date, across the 1 Apr 2026 boundary
# ---------------------------------------------------------------------------
a = chiller(1400, "2024-10-01")
c = claim("T9-a", a, "COMP-RR", "2026-03-31", 9.0, "P-44310", "P-44310", 3000)
r = adjudicate(c, a)
check("trap-9  repair 31 Mar 2026 uses the FY25 rate of 1320",
      r.labour_rate_used == 1320, str(r.labour_rate_used))

c = claim("T9-b", a, "COMP-RR", "2026-04-01", 9.0, "P-44310", "P-44310", 3000)
r = adjudicate(c, a)
check("trap-9  repair 1 Apr 2026 uses the FY26 rate of 1450",
      r.labour_rate_used == 1450, str(r.labour_rate_used))

# ---------------------------------------------------------------------------
# trap 10 + 7 + 8 - cap, supersession and uplift together, Northwind
# ---------------------------------------------------------------------------
a = chiller(1400, "2024-10-01", dealer="D-IN-02")
c = claim("T8", a, "HYD-PUMP-RR", "2026-06-18", 8.0, "P-44120", "P-44120", 3000)
r = adjudicate(c, a)
check("trap-10 labour capped at the 5.5 h flat rate",
      r.labour_hours_paid == 5.5 and r.hours_variance == 2.5, str(r.labour_hours_paid))
check("trap-7  P-44120 priced at its superseding part P-44120-A",
      r.part_priced == "P-44120-A" and r.payable_parts == 191200.0, str(r.part_priced))
check("trap-8  Northwind 5% uplift applied to parts only",
      r.payable_uplift == 9560.0, str(r.payable_uplift))
check("trap-8  total = 7,975 + 191,200 + 9,560 = 208,735",
      r.total_payable == 208735.0, str(r.total_payable))

# ---------------------------------------------------------------------------
# exclusion reversal - TSB-C-0043 over policy 5.2
# ---------------------------------------------------------------------------
a = chiller(1400, "2025-06-01")
c = claim("TX-a", a, "HYD-PUMP-RR", "2026-06-01", 5.0, "P-44120-A", "P-44120-A", 3000,
          exclusion_flags=["5.2"], contamination_from_filter_housing=True)
r = adjudicate(c, a)
check("reversal  contamination exclusion reversed by TSB-C-0043",
      r.decision == "approve", r.decision)

c = claim("TX-b", a, "HYD-PUMP-RR", "2026-06-01", 5.0, "P-44120-A", "P-44120-A", 3000,
          exclusion_flags=["5.2"], contamination_from_filter_housing=False)
r = adjudicate(c, a)
check("reversal  contamination NOT from the filter housing stays excluded",
      r.decision == "decline" and "5.2" in r.reason, r.reason[:60])

# ---------------------------------------------------------------------------
# trap 11 - goodwill on a declined claim escalates, it does not pay
# ---------------------------------------------------------------------------
a = chiller(1950, "2024-09-01")
c = claim("T11", a, "CTRL-BD-RR", "2026-05-01", 1.5, "P-44900", "P-44900",
          goodwill_requested=67400)
r = adjudicate(c, a)
check("trap-11 declined claim with goodwill becomes an escalation",
      r.decision == "escalate" and r.funding_code == "GW", r.decision)
check("trap-11 routed to tier 2, Regional Service Manager",
      r.approver_role == "Regional Service Manager", str(r.approver_role))
check("trap-11 channel approval explicitly denied as authority",
      any("does not constitute authority" in n for n in r.notes), "")
check("trap-11 nothing is payable on an escalation",
      r.total_payable is None, str(r.total_payable))

# ---------------------------------------------------------------------------
# trap 12 - abstention paths
# ---------------------------------------------------------------------------
a = chiller(1400, "2024-10-01", commissioning=False)
c = claim("T12-a", a, "HYD-PUMP-RR", "2026-06-18", 5.0, "P-44120-A", "P-44120-A", 3000)
r = adjudicate(c, a)
check("trap-12 missing commissioning date -> request_evidence, not a guess",
      r.decision == "request_evidence" and r.missing_field == "commissioning_date", r.decision)
check("trap-12 install date explicitly not substituted",
      "must not be substituted" in r.reason, "")

a = chiller(9999, "2024-10-01")
a.known = False
c = claim("T12-b", a, "HYD-PUMP-RR", "2026-06-18", 5.0, "P-44120-A", "P-44120-A", 3000)
r = adjudicate(c, a)
check("trap-12 unknown serial -> request_evidence",
      r.decision == "request_evidence" and r.missing_field == "asset record", r.decision)

# ---------------------------------------------------------------------------
# repair warranty - policy 6.1 outranks an expired coverage period
# ---------------------------------------------------------------------------
a = chiller(1950, "2023-01-01")                        # long out of warranty
c = claim("TRW", a, "CTRL-BD-RR", "2026-06-01", 1.5, "P-44900", "P-44900",
          prior_claim={"claim_id": "C-2026-03110", "completed_date": "2026-04-20",
                       "component": "controls"})
r = adjudicate(c, a)
check("repair-warranty  covered under policy 6.1 despite an expired asset warranty",
      r.decision == "approve" and r.funding_code == "RW", f"{r.decision}/{r.funding_code}")

c = claim("TRW-b", a, "CTRL-BD-RR", "2026-09-01", 1.5, "P-44900", "P-44900",
          prior_claim={"claim_id": "C-2026-03110", "completed_date": "2026-04-20",
                       "component": "controls"})
r = adjudicate(c, a)
check("repair-warranty  beyond 90 days it does not apply",
      r.decision == "decline", r.decision)

# ---------------------------------------------------------------------------
# region-scoped bulletin must not leak across regions
# ---------------------------------------------------------------------------
a = compressor(1000, "2024-06-01")                     # India
c = claim("TRG", a, "MOTOR-RR", "2026-06-01", 7.5, "P-22610", "P-22610", 3000)
r = adjudicate(c, a)
check("region  EMEA-only TSB-P-0115 does not extend an Indian asset",
      r.governing_instrument == "ADD-IN-2.1", r.governing_instrument)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    width = max(len(label) for _, label, _ in RESULTS)
    for ok, label, detail in RESULTS:
        line = f"  {'PASS' if ok else 'FAIL'}  {label.ljust(width)}"
        print(line if ok else f"{line}   <- got: {detail}")

    failed = sum(1 for ok, _, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} checks passed.")
    if failed:
        raise SystemExit(1)
