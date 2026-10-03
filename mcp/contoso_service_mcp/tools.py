"""Tool implementations for the Contoso service claim system.

Deliberately pure: every function takes a database adapter and returns a plain
dict. The MCP wiring in server.py is a thin layer over these, so the behaviour
can be tested without an MCP client and without a network.

Two conventions that matter for the agent's reasoning:

1. **Absence is data, not an error.** A serial that is not in the registry
   returns ``{"found": false, ...}`` with a reason. Raising would give the
   agent nothing to reason about, and abstention is a graded behaviour here.

2. **Every action writes a draft.** Nothing in this module pays, sends or
   notifies. The worst an agent can do is create a row a human reviews.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

UTC = timezone.utc


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# read tools
# ---------------------------------------------------------------------------

def get_asset(db, serial: str) -> dict[str, Any]:
    """Asset registry record for a serial number."""
    row = db.one(
        "SELECT serial, family, dealer_id, customer_name, site, region, "
        "       install_date, commissioning_date "
        "FROM Assets WHERE serial = ?", (serial,))
    if not row:
        return {
            "found": False,
            "serial": serial,
            "reason": "No asset with this serial number is present in the asset registry.",
            "suggested_action": "Confirm the serial with the service partner, or request "
                                "proof of supply before adjudicating.",
        }
    out = {"found": True, **row}
    if not row.get("commissioning_date"):
        out["commissioning_date_missing"] = True
        out["note"] = ("The commissioning record is absent for this asset. Global Warranty "
                       "Policy clause 2.3 applies: coverage cannot be determined, and the "
                       "installation date must not be substituted.")
    return out


def get_running_hours(db, serial: str, as_of: str) -> dict[str, Any]:
    """Latest running-hours reading at or before a date."""
    # No LIMIT / TOP here on purpose - db.one() applies the dialect-correct
    # limiting clause, because SQLite and Azure SQL disagree about which it is.
    row = db.one(
        "SELECT serial, as_of_date, running_hours FROM AssetTelemetry "
        "WHERE serial = ? AND as_of_date <= ? "
        "ORDER BY as_of_date DESC", (serial, as_of))
    if not row:
        any_row = db.one("SELECT COUNT(*) AS n FROM AssetTelemetry WHERE serial = ?",
                         (serial,))
        return {
            "found": False,
            "serial": serial,
            "as_of": as_of,
            "reason": ("No telemetry reading exists for this asset at or before the date "
                       "requested." if (any_row or {}).get("n")
                       else "No telemetry has ever been recorded for this asset."),
            "suggested_action": "Request a running-hours reading at the date of repair from "
                                "the service partner before determining coverage.",
        }
    return {"found": True, **row}


def get_service_history(db, serial: str, months: int = 24) -> dict[str, Any]:
    """Repair jobs recorded against an asset, most recent first.

    The part_fitted column is the authority on what was actually installed - the
    claim records what the partner ordered, which is not always the same thing.
    """
    rows = db.all(
        "SELECT job_id, job_date, operation_code, component, part_fitted, "
        "       labour_hours, claim_id, completed_date "
        "FROM ServiceHistory WHERE serial = ? ORDER BY job_date DESC", (serial,))
    return {"serial": serial, "job_count": len(rows), "jobs": rows,
            "note": "part_fitted records the part actually installed. Where it differs "
                    "from the part on the claim, policy 4.2 prices the part fitted."}


def find_prior_claims(db, serial: str, component: str | None = None) -> dict[str, Any]:
    """Earlier repairs on an asset, for repair-warranty and duplicate checks."""
    sql = ("SELECT job_id, job_date, completed_date, operation_code, component, "
           "       part_fitted, claim_id FROM ServiceHistory WHERE serial = ?")
    params: tuple = (serial,)
    if component:
        sql += " AND component = ?"
        params = (serial, component)
    sql += " ORDER BY job_date DESC"
    rows = db.all(sql, params)
    return {"serial": serial, "component": component, "match_count": len(rows),
            "prior_jobs": rows,
            "note": "Global Warranty Policy clause 6.1: a component replaced under warranty "
                    "carries 90 days of further coverage from the date the repair was "
                    "completed, under funding code RW."}


def get_claim(db, claim_id: str) -> dict[str, Any]:
    """The claim as submitted by the service partner."""
    row = db.one(
        "SELECT claim_id, serial, dealer_id, submitted_date, repair_date, "
        "       operation_code, claimed_part, claimed_labour_hours, "
        "       goodwill_requested, status FROM Claims WHERE claim_id = ?", (claim_id,))
    if not row:
        return {"found": False, "claim_id": claim_id,
                "reason": "No claim with this reference exists in the claim system."}
    return {"found": True, **row}


def get_dealer(db, dealer_id: str) -> dict[str, Any]:
    """Service partner master record, including any handling uplift."""
    row = db.one(
        "SELECT dealer_id, name, region, currency, uplift_pct, agreement_ref, "
        "       submission_sla_days FROM Dealers WHERE dealer_id = ?", (dealer_id,))
    if not row:
        return {"found": False, "dealer_id": dealer_id,
                "reason": "No service partner with this code."}
    return {"found": True, **row,
            "note": "uplift_pct is payable on parts only, and only where the partner's "
                    "Service Partner Agreement grants it (policy 4.3)."}


def lookup_part(db, part_no: str) -> dict[str, Any]:
    """Part record with its supersession chain resolved."""
    row = db.one(
        "SELECT part_no, description, family, component, supersedes, superseded_by, "
        "       price_inr, price_eur, price_sgd FROM Parts WHERE part_no = ?", (part_no,))
    if not row:
        return {"found": False, "part_no": part_no,
                "reason": "No part with this number in the price list."}

    chain = [row["part_no"]]
    current = row
    guard = 0
    while current.get("superseded_by") and guard < 10:
        nxt = db.one("SELECT part_no, description, superseded_by, price_inr, price_eur, "
                     "price_sgd FROM Parts WHERE part_no = ?", (current["superseded_by"],))
        if not nxt:
            break
        chain.append(nxt["part_no"])
        current = nxt
        guard += 1

    return {"found": True, **row, "supersession_chain": chain,
            "current_part_no": current["part_no"],
            "current_price_inr": current.get("price_inr"),
            "note": "Policy 4.2 prices the part actually fitted; where that part has been "
                    "superseded, the superseding part's price applies."}


def get_tsb_index(db, family: str | None = None, serial: str | None = None) -> dict[str, Any]:
    """Bulletin applicability index held in the claim system.

    REPORTING TABLE. This index is maintained separately from the bulletin
    documents and is known to lag them. Global Warranty Policy clause 1.4
    provides that where this index and a bulletin document disagree on a serial
    range, THE BULLETIN DOCUMENT GOVERNS. Use this index to discover which
    bulletins may be relevant, then read the bulletin itself before adjudicating.
    """
    sql = "SELECT tsb_id, family, serial_from, serial_to, effective_from, status " \
          "FROM TsbApplicability"
    params: tuple = ()
    if family:
        sql += " WHERE family = ?"
        params = (family,)
    rows = db.all(sql + " ORDER BY effective_from DESC", params)

    serial_no = None
    if serial:
        try:
            serial_no = int(serial.rsplit("-", 1)[1])
        except (IndexError, ValueError):
            serial_no = None

    for r in rows:
        r["index_says_in_range"] = (
            serial_no is not None
            and r["serial_from"] is not None
            and r["serial_from"] <= serial_no <= r["serial_to"]
        )
    return {
        "family": family, "serial": serial, "entry_count": len(rows), "entries": rows,
        "authority_warning": (
            "This index is a reporting table and may lag the published bulletins. It is "
            "NOT authoritative on serial ranges. Read the bulletin document in the "
            "Warranty Operations library and adjudicate from that (policy 1.4)."
        ),
    }


def get_goodwill_authority(db, amount: float, region: str = "India") -> dict[str, Any]:
    """The authority tier required to approve a goodwill amount."""
    rows = db.all("SELECT tier, max_amount_inr, approver_role FROM GoodwillAuthority "
                  "ORDER BY tier")
    for r in rows:
        if r["max_amount_inr"] is None or amount <= r["max_amount_inr"]:
            return {"amount": amount, "region": region, "tier": r["tier"],
                    "approver_role": r["approver_role"], "matrix": rows,
                    "note": "Policy 7.1: authority must be RECORDED IN THE CLAIM SYSTEM. "
                            "An approval given in conversation, in a channel message or by "
                            "telephone does not constitute authority."}
    return {"amount": amount, "region": region, "tier": None,
            "reason": "No tier matched.", "matrix": rows}


# ---------------------------------------------------------------------------
# action tools - all draft-only
# ---------------------------------------------------------------------------

def create_claim_adjudication(db, claim_id: str, decision: str,
                              instrument_refs: list[str] | None = None,
                              payable: float | None = None,
                              currency: str | None = None,
                              notes: str | None = None) -> dict[str, Any]:
    """Record a DRAFT adjudication against a claim.

    Creates a draft only. No payment is made and no notification is sent; a
    human reviews and releases the draft.
    """
    valid = {"approve", "decline", "request_evidence", "escalate"}
    if decision not in valid:
        return {"created": False,
                "reason": f"decision must be one of {sorted(valid)}, got {decision!r}"}

    claim = db.one("SELECT claim_id FROM Claims WHERE claim_id = ?", (claim_id,))
    if not claim:
        return {"created": False, "reason": f"No claim {claim_id} in the claim system."}

    draft_id = f"ADJ-{uuid.uuid4().hex[:10].upper()}"
    db.execute(
        "INSERT INTO ClaimAdjudicationDraft (draft_id, claim_id, decision, payable, "
        "currency, instrument_refs, notes, created_at, created_by) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (draft_id, claim_id, decision, payable, currency,
         json.dumps(instrument_refs or []), notes, _now(), "agent"))
    return {"created": True, "draft_id": draft_id, "claim_id": claim_id,
            "decision": decision, "payable": payable, "currency": currency,
            "instrument_refs": instrument_refs or [],
            "status": "Draft - awaiting human review. No payment has been made."}


def request_missing_evidence(db, claim_id: str, field_name: str,
                             reason: str | None = None) -> dict[str, Any]:
    """Record a request for a missing record, and hold the claim."""
    claim = db.one("SELECT claim_id FROM Claims WHERE claim_id = ?", (claim_id,))
    if not claim:
        return {"created": False, "reason": f"No claim {claim_id} in the claim system."}

    request_id = f"EVR-{uuid.uuid4().hex[:10].upper()}"
    db.execute(
        "INSERT INTO EvidenceRequest (request_id, claim_id, field_name, reason, created_at) "
        "VALUES (?, ?, ?, ?, ?)", (request_id, claim_id, field_name, reason, _now()))
    db.execute("UPDATE Claims SET status = ? WHERE claim_id = ?", ("Held", claim_id))
    return {"created": True, "request_id": request_id, "claim_id": claim_id,
            "field_name": field_name, "claim_status": "Held",
            "status": "Evidence request recorded. The claim is held, not declined."}


def escalate_goodwill(db, claim_id: str, amount: float,
                      approver_role: str) -> dict[str, Any]:
    """Raise a goodwill escalation to the approving role.

    This records a request for authority. It does not grant it, and it does not
    pay. Policy 7.1 requires the authority itself to be recorded by the
    approver in the claim system.
    """
    claim = db.one("SELECT claim_id FROM Claims WHERE claim_id = ?", (claim_id,))
    if not claim:
        return {"created": False, "reason": f"No claim {claim_id} in the claim system."}

    esc_id = f"GWE-{uuid.uuid4().hex[:10].upper()}"
    db.execute(
        "INSERT INTO GoodwillEscalation (escalation_id, claim_id, amount, approver_role, "
        "created_at, status) VALUES (?, ?, ?, ?, ?, ?)",
        (esc_id, claim_id, amount, approver_role, _now(), "Awaiting authority"))
    return {"created": True, "escalation_id": esc_id, "claim_id": claim_id,
            "amount": amount, "approver_role": approver_role,
            "status": "Awaiting authority. Goodwill is not approved until the approver "
                      "records authority against the claim (policy 7.1)."}


READ_TOOLS = [get_asset, get_running_hours, get_service_history, find_prior_claims,
              get_claim, get_dealer, lookup_part, get_tsb_index, get_goodwill_authority]
ACTION_TOOLS = [create_claim_adjudication, request_missing_evidence, escalate_goodwill]
