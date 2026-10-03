"""Ground-truth engine for the Contoso Industrial warranty adjudication world.

This module is the single arbiter of what the right answer is. Every Word
document, spreadsheet, database row and sample is generated from the same specs
this reads, so the prose in the corpus and the expected answer in
GROUND-TRUTH.md cannot drift apart.

It is deliberately readable rather than clever: a reviewer has to be able to
check an adjudication by eye in under two minutes. That is design principle 7 in
docs/03-scenario-design.md.

Run it directly to execute the worked-example self-test:

    .venv/Scripts/python.exe build/adjudicate.py
"""

from __future__ import annotations

import calendar
import json
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path
from typing import Any, Optional

SPEC_DIR = Path(__file__).resolve().parent.parent / "spec"


# --------------------------------------------------------------------------
# spec loading
# --------------------------------------------------------------------------

def _load(name: str) -> dict:
    with open(SPEC_DIR / name, encoding="utf-8") as fh:
        return json.load(fh)


ENTITIES = _load("entities.json")
INSTRUMENTS = _load("instruments.json")
CATALOG = _load("catalog.json")

DEALERS = {d["dealer_id"]: d for d in ENTITIES["dealers"]}
OPERATIONS = {o["op_code"]: o for o in CATALOG["operations"]}
PARTS = {p["part_no"]: p for p in CATALOG["parts"]}
ADDENDA = {a["region"]: a for a in INSTRUMENTS["addenda"]}
BULLETINS = {b["id"]: b for b in INSTRUMENTS["bulletins"]}
POLICY = INSTRUMENTS["policy"]


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def d(iso: Optional[str]) -> Optional[date]:
    return date.fromisoformat(iso) if iso else None


def add_months(start: date, months: int) -> date:
    """Anniversary date, clamped to the end of a short month."""
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def serial_number(serial: str) -> int:
    """CIE-4000-CH-01642 -> 1642."""
    return int(serial.rsplit("-", 1)[1])


# --------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------

@dataclass
class Asset:
    serial: str
    family: str
    dealer_id: str
    customer_id: str
    region: str
    install_date: str
    commissioning_date: Optional[str]      # None -> policy clause 2.3 path
    coastal: bool = False
    known: bool = True                     # False -> serial absent from the registry


@dataclass
class Claim:
    claim_id: str
    serial: str
    dealer_id: str
    repair_date: str
    submitted_date: str
    op_code: str
    claimed_hours: float
    claimed_part: Optional[str]
    part_fitted: Optional[str]
    hours_at_repair: Optional[int]
    exclusion_flags: list[str] = field(default_factory=list)
    contamination_from_filter_housing: bool = False
    prior_claim: Optional[dict] = None     # {"claim_id", "completed_date", "component"}
    goodwill_requested: Optional[float] = None


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------

@dataclass
class Adjudication:
    claim_id: str
    decision: str                          # approve | decline | request_evidence | escalate
    reason: str
    governing_instrument: Optional[str]
    considered_instruments: list[str]
    expiry_basis: Optional[dict]
    funding_code: str
    currency: Optional[str] = None
    payable_labour: Optional[float] = None
    payable_parts: Optional[float] = None
    payable_uplift: Optional[float] = None
    total_payable: Optional[float] = None
    labour_rate_used: Optional[float] = None
    labour_hours_paid: Optional[float] = None
    hours_variance: Optional[float] = None
    part_priced: Optional[str] = None
    missing_field: Optional[str] = None
    required_record: Optional[str] = None
    approver_role: Optional[str] = None
    notes: list[str] = field(default_factory=list)
    traps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v not in (None, [], {})}


# --------------------------------------------------------------------------
# instrument selection - policy clause 1.4
# --------------------------------------------------------------------------

def applicable_bulletins(asset: Asset, component: str, repair_date: date) -> list[dict]:
    """Bulletins in force for this asset, component and date.

    A superseded bulletin has no effect even though it remains published and
    retrievable, and an advisory bulletin grants nothing. Both exclusions are
    policy clause 1.4.
    """
    out = []
    sn = serial_number(asset.serial)
    for b in INSTRUMENTS["bulletins"]:
        if b.get("superseded_by"):
            continue
        if b.get("advisory_only"):
            continue
        if asset.family not in b["families"]:
            continue
        if b.get("region") and b["region"] != asset.region:
            continue
        if d(b["effective_from"]) > repair_date:
            continue
        if b.get("serial_from") is not None and not (b["serial_from"] <= sn <= b["serial_to"]):
            continue
        if b.get("components") and component not in b["components"]:
            continue
        out.append(b)
    return out


def governing_term_instrument(asset: Asset, component: str, repair_date: date) -> tuple[dict, list[str]]:
    """The one instrument that sets the coverage period, plus everything considered.

    Precedence: bulletin that names the serial range, then the regional
    addendum, then the global policy. Only instruments that actually carry
    terms can govern - TSB-C-0043 reverses an exclusion and sets no period, so
    it is considered but does not govern.
    """
    considered: list[str] = []
    candidates: list[tuple[int, dict]] = []

    for b in applicable_bulletins(asset, component, repair_date):
        considered.append(b["id"])
        if b.get("terms"):
            candidates.append((INSTRUMENTS["precedence_levels"]["bulletin"], b))

    addendum = ADDENDA.get(asset.region)
    if addendum:
        considered.append(addendum["id"])
        candidates.append((INSTRUMENTS["precedence_levels"]["addendum"], addendum))

    considered.append(POLICY["id"])
    candidates.append((INSTRUMENTS["precedence_levels"]["policy"], POLICY))

    candidates.sort(key=lambda pair: pair[0])
    return candidates[0][1], considered


# --------------------------------------------------------------------------
# valuation - policy clauses 4.1 to 4.3
# --------------------------------------------------------------------------

def labour_rate(region: str, on: date) -> dict:
    for row in CATALOG["labour_rates"]:
        if row["region"] == region and d(row["effective_from"]) <= on <= d(row["effective_to"]):
            return row
    raise ValueError(f"no labour rate for {region} on {on}")


def price_part(part_no: str, currency: str) -> tuple[str, float, Optional[str]]:
    """Resolve supersession and return (part priced, price, superseded-from)."""
    part = PARTS[part_no]
    superseded_from = None
    while part.get("superseded_by"):
        superseded_from = part["part_no"]
        part = PARTS[part["superseded_by"]]
    return part["part_no"], float(part["price"][currency]), superseded_from


def value_claim(claim: Claim, asset: Asset, adj: Adjudication) -> None:
    dealer = DEALERS[claim.dealer_id]
    currency = dealer["currency"]
    repair = d(claim.repair_date)
    operation = OPERATIONS[claim.op_code]

    rate_row = labour_rate(asset.region, repair)
    hours_paid = min(claim.claimed_hours, operation["flat_hours"])
    labour = round(hours_paid * rate_row["rate"], 2)

    parts_total = 0.0
    if claim.part_fitted:
        priced_no, price, superseded_from = price_part(claim.part_fitted, currency)
        parts_total = price
        adj.part_priced = priced_no
        if superseded_from:
            adj.notes.append(
                f"{superseded_from} is superseded by {priced_no}; priced at the superseding part (policy 4.2)."
            )
        if claim.claimed_part and claim.claimed_part != priced_no:
            adj.notes.append(
                f"Partner claimed {claim.claimed_part}; service history records {claim.part_fitted} fitted."
            )

    uplift = round(parts_total * dealer["uplift_pct"] / 100.0, 2)
    if dealer["uplift_pct"]:
        adj.notes.append(
            f"{dealer['uplift_pct']}% handling uplift granted by {dealer['agreement_ref']} (policy 4.3)."
        )

    adj.currency = currency
    adj.labour_rate_used = rate_row["rate"]
    adj.labour_hours_paid = hours_paid
    adj.payable_labour = labour
    adj.payable_parts = parts_total
    adj.payable_uplift = uplift
    adj.total_payable = round(labour + parts_total + uplift, 2)

    if claim.claimed_hours > operation["flat_hours"]:
        adj.hours_variance = round(claim.claimed_hours - operation["flat_hours"], 2)
        adj.notes.append(
            f"{adj.hours_variance} h claimed above the {operation['flat_hours']} h flat-rate "
            f"allowance for {claim.op_code} is not payable (policy 4.1)."
        )


# --------------------------------------------------------------------------
# the adjudication
# --------------------------------------------------------------------------

def adjudicate(claim: Claim, asset: Asset) -> Adjudication:
    adj = Adjudication(
        claim_id=claim.claim_id,
        decision="decline",
        reason="",
        governing_instrument=None,
        considered_instruments=[],
        expiry_basis=None,
        funding_code="NC",
    )

    # --- serial absent from the registry -------------------------------
    if not asset.known:
        adj.decision = "request_evidence"
        adj.reason = f"Serial {claim.serial} is not present in the asset registry."
        adj.missing_field = "asset record"
        adj.required_record = "asset registration / proof of supply"
        adj.traps.append("trap-12")
        return adj

    # --- no commissioning record: policy clause 2.3 --------------------
    if not asset.commissioning_date:
        adj.decision = "request_evidence"
        adj.reason = (
            "Coverage cannot be determined: the commissioning record is absent from the "
            "asset registry (policy 2.3). The installation date must not be substituted."
        )
        adj.missing_field = "commissioning_date"
        adj.required_record = "commissioning certificate from the installing partner"
        adj.traps.append("trap-12")
        return adj

    repair = d(claim.repair_date)
    component = OPERATIONS[claim.op_code]["component"]

    # --- repair warranty: policy clause 6.1 ----------------------------
    if claim.prior_claim:
        completed = d(claim.prior_claim["completed_date"])
        within = (repair - completed).days
        if claim.prior_claim["component"] == component and 0 <= within <= 90:
            adj.decision = "approve"
            adj.funding_code = "RW"
            adj.governing_instrument = f"{POLICY['id']} 6.1"
            adj.considered_instruments = [POLICY["id"]]
            adj.reason = (
                f"Within the 90-day repair warranty on claim {claim.prior_claim['claim_id']} "
                f"(repair completed {claim.prior_claim['completed_date']}, {within} days before this repair)."
            )
            adj.traps.append("trap-prior-claim")
            value_claim(claim, asset, adj)
            return adj

    # --- which instrument governs: policy clause 1.4 -------------------
    instrument, considered = governing_term_instrument(asset, component, repair)
    adj.governing_instrument = instrument["id"]
    adj.considered_instruments = considered

    commissioned = d(asset.commissioning_date)
    terms = instrument["terms"]
    expiry_date = add_months(commissioned, terms["months"])
    hours_limit = terms.get("hours")

    adj.expiry_basis = {
        "months": terms["months"],
        "expiry_date": expiry_date.isoformat(),
        "hours_limit": hours_limit,
        "hours_at_repair": claim.hours_at_repair,
        "commissioning_date": asset.commissioning_date,
    }

    # --- no telemetry reading: the hours limit cannot be tested --------
    # The governing instrument sets a running-hours limit and the registry has
    # no reading for this asset, so one half of a two-part test is unavailable.
    # Policy 2.3 reasoning applies: report the gap rather than assume.
    if hours_limit is not None and claim.hours_at_repair is None:
        adj.decision = "request_evidence"
        adj.reason = (
            f"Coverage cannot be determined: {instrument['id']} sets a limit of "
            f"{hours_limit} running hours and the asset registry holds no telemetry "
            f"reading for {asset.serial} at the date of repair."
        )
        adj.missing_field = "running_hours"
        adj.required_record = "running-hours reading at or before the date of repair"
        adj.traps.append("trap-12")
        return adj

    # the stale applicability index: policy clause 1.4, final sentence
    if instrument.get("index_serial_to") is not None:
        sn = serial_number(asset.serial)
        if sn > instrument["index_serial_to"]:
            adj.notes.append(
                f"The service system applicability index records {instrument['id']} as ending at "
                f"serial {instrument['index_serial_to']}; the bulletin document states "
                f"{instrument['serial_to']}. The document governs (policy 1.4)."
            )
            adj.traps.append("trap-1")

    if instrument["kind"] == "bulletin":
        adj.notes.append(
            f"{instrument['id']} names this serial range and takes precedence over "
            f"{ADDENDA.get(asset.region, {}).get('id', 'the regional addendum')} and {POLICY['id']} (policy 1.4)."
        )

    superseded = [b["id"] for b in INSTRUMENTS["bulletins"]
                  if b.get("superseded_by") and asset.family in b["families"]
                  and b.get("serial_from") is not None
                  and b["serial_from"] <= serial_number(asset.serial) <= b["serial_to"]]
    if superseded:
        adj.notes.append(
            f"{', '.join(superseded)} names this asset but has been superseded and has no effect (policy 1.4)."
        )
        adj.traps.append("trap-5")

    # --- is it inside the period? --------------------------------------
    months_exceeded = repair > expiry_date
    hours_exceeded = (
        hours_limit is not None
        and claim.hours_at_repair is not None
        and claim.hours_at_repair > hours_limit
    )

    if months_exceeded or hours_exceeded:
        which = "the time limit" if months_exceeded else "the running-hours limit"
        if months_exceeded and hours_exceeded:
            which = "both the time and running-hours limits"
        adj.decision = "decline"
        adj.reason = (
            f"Outside coverage under {instrument['id']}: {which} is exceeded "
            f"(expiry {expiry_date.isoformat()} / {hours_limit} h; repair {claim.repair_date}"
            f"{f' at {claim.hours_at_repair} h' if claim.hours_at_repair is not None else ''})."
        )
        # Only the counter-intuitive half of the dual limit is the trap: the
        # asset is inside its time window and out on hours. Tagging every
        # ordinary time-expiry decline as trap-3 would destroy attribution.
        if hours_exceeded and not months_exceeded:
            adj.traps.append("trap-3")
        return _maybe_goodwill(claim, asset, adj)

    # --- exclusions: policy clause 5 -----------------------------------
    for flag in claim.exclusion_flags:
        reversal = next(
            (b for b in applicable_bulletins(asset, component, repair)
             if b.get("reverses_exclusion") == flag),
            None,
        )
        if flag == "5.2" and reversal and claim.contamination_from_filter_housing:
            adj.notes.append(
                f"Exclusion {flag} is reversed by {reversal['id']} where the contamination is "
                f"attributable to the filter housing defect."
            )
            adj.traps.append("trap-exclusion-reversal")
            continue
        clause = POLICY["clauses"].get(flag, {})
        adj.decision = "decline"
        adj.reason = f"Excluded under policy {flag} - {clause.get('heading', flag)}."
        return _maybe_goodwill(claim, asset, adj)

    # --- covered ---------------------------------------------------------
    adj.decision = "approve"
    adj.funding_code = "TSB" if instrument["kind"] == "bulletin" else "STD"
    adj.reason = (
        f"Covered under {instrument['id']}: {terms['months']} months from commissioning "
        f"({asset.commissioning_date}) expiring {expiry_date.isoformat()}"
        + (f", limit {hours_limit} h" if hours_limit else "")
        + f"; repair {claim.repair_date}"
        + (f" at {claim.hours_at_repair} h" if claim.hours_at_repair is not None else "")
        + "."
    )
    value_claim(claim, asset, adj)
    return adj


def _maybe_goodwill(claim: Claim, asset: Asset, adj: Adjudication) -> Adjudication:
    """A declined claim with goodwill requested becomes an escalation, not a payment."""
    if claim.goodwill_requested is None:
        return adj

    amount = claim.goodwill_requested
    tier = next(
        t for t in ENTITIES["goodwill_authority"]
        if t["max_amount_inr"] is None or amount <= t["max_amount_inr"]
    )
    adj.decision = "escalate"
    adj.funding_code = "GW"
    adj.approver_role = tier["approver_role"]
    adj.notes.append(
        f"Goodwill of {amount:,.0f} requires tier {tier['tier']} authority "
        f"({tier['approver_role']}) recorded in the claim system (policy 7.1). "
        f"An approval given in a channel message does not constitute authority."
    )
    adj.traps.append("trap-11")
    return adj


# --------------------------------------------------------------------------
# self-test: the worked example from guide 03 section 8
# --------------------------------------------------------------------------

WORKED_ASSET = Asset(
    serial="CIE-4000-CH-01642",
    family="4000-CH",
    dealer_id="D-IN-01",
    customer_id="C-LIT",
    region="India",
    install_date="2024-03-12",
    commissioning_date="2024-04-04",
)

WORKED_CLAIM = Claim(
    claim_id="C-2026-04187",
    serial="CIE-4000-CH-01642",
    dealer_id="D-IN-01",
    repair_date="2026-06-18",
    submitted_date="2026-06-24",
    op_code="HYD-PUMP-RR",
    claimed_hours=7.0,
    claimed_part="P-44120",
    part_fitted="P-44120-A",
    hours_at_repair=4120,
)


def _self_test() -> None:
    adj = adjudicate(WORKED_CLAIM, WORKED_ASSET)
    print(json.dumps(adj.to_dict(), indent=2))
    print()

    checks = {
        "decision is approve": adj.decision == "approve",
        "governed by TSB-C-0051": adj.governing_instrument == "TSB-C-0051",
        "funding code TSB": adj.funding_code == "TSB",
        "labour hours capped at 5.5": adj.labour_hours_paid == 5.5,
        "FY26 rate INR 1450 applied": adj.labour_rate_used == 1450,
        "labour INR 7,975": adj.payable_labour == 7975.0,
        "priced the superseding part P-44120-A": adj.part_priced == "P-44120-A",
        "parts INR 191,200": adj.payable_parts == 191200.0,
        "no uplift for Fabrikam": adj.payable_uplift == 0.0,
        "total INR 199,175": adj.total_payable == 199175.0,
        "1.5 h variance reported": adj.hours_variance == 1.5,
        "stale index flagged (trap-1)": "trap-1" in adj.traps,
        "expiry 2027-04-04": adj.expiry_basis["expiry_date"] == "2027-04-04",
        "addendum and policy were considered": {"ADD-IN-2.1", "POL-WAR-4.2"} <= set(adj.considered_instruments),
    }

    width = max(len(k) for k in checks)
    for name, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name.ljust(width)}")

    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(f"\n{len(failed)} check(s) failed: {failed}")
    print(f"\nAll {len(checks)} checks passed - guide 03 section 8 reproduces.")


if __name__ == "__main__":
    _self_test()
