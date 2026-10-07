"""Tool-level tests against the seeded SQLite database.

Runs without the mcp package and without a network: the tool functions are pure
and take a database adapter. What is being checked is not just that queries
work, but that each tool exposes the specific fact a designed trap depends on.

    cd scenario/mcp
    ../.venv/Scripts/python.exe tests/test_tools.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DB = ROOT.parent / "out" / "db" / "contoso.db"
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from contoso_service_mcp import tools as T          # noqa: E402
from contoso_service_mcp.db import connect, _MssqlAdapter   # noqa: E402

RESULTS: list[tuple[bool, str, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((ok, label, detail))


# ---------------------------------------------------------------------------
# Azure SQL dialect translation
#
# These run without a SQL Server. The T-SQL path is only exercised in Azure, so
# the two translations that could silently produce wrong answers there - row
# limiting and type normalisation - are tested as pure functions here.
# ---------------------------------------------------------------------------
from datetime import date, datetime, timezone       # noqa: E402
from decimal import Decimal                         # noqa: E402

sql = ("SELECT serial, as_of_date FROM AssetTelemetry WHERE serial = ? "
       "ORDER BY as_of_date DESC")
check("mssql: LIMIT becomes TOP (n) after SELECT",
      _MssqlAdapter._limit(sql, 1) ==
      "SELECT TOP (1) serial, as_of_date FROM AssetTelemetry WHERE serial = ? "
      "ORDER BY as_of_date DESC",
      _MssqlAdapter._limit(sql, 1))
check("mssql: no limit leaves the statement untouched",
      _MssqlAdapter._limit(sql, None) == sql, "")
try:
    _MssqlAdapter._limit("UPDATE Claims SET status = ?", 1)
    check("mssql: limiting a non-SELECT is refused", False, "no error raised")
except ValueError:
    check("mssql: limiting a non-SELECT is refused", True)

check("mssql: DATE columns normalise to ISO date strings",
      _MssqlAdapter._normalise(date(2026, 6, 18)) == "2026-06-18", "")
check("mssql: DATETIMEOFFSET keeps its time - an audit stamp is not a date",
      _MssqlAdapter._normalise(datetime(2026, 6, 18, 14, 30, 5))
      == "2026-06-18T14:30:05",
      _MssqlAdapter._normalise(datetime(2026, 6, 18, 14, 30, 5)))
check("mssql: DATETIMEOFFSET keeps its UTC offset",
      _MssqlAdapter._normalise(
          datetime(2026, 6, 18, 14, 30, 5, tzinfo=timezone.utc)).endswith("+00:00"),
      _MssqlAdapter._normalise(datetime(2026, 6, 18, 14, 30, 5, tzinfo=timezone.utc)))
check("mssql: DECIMAL money normalises to float",
      _MssqlAdapter._normalise(Decimal("191200.00")) == 191200.0
      and isinstance(_MssqlAdapter._normalise(Decimal("5.00")), float), "")
check("mssql: ordinary values pass through unchanged",
      _MssqlAdapter._normalise("P-44120-A") == "P-44120-A"
      and _MssqlAdapter._normalise(None) is None, "")


with connect() as db:
    # --- get_asset ----------------------------------------------------
    a = T.get_asset(db, "CIE-4000-CH-01642")
    check("get_asset returns a known serial", a["found"], str(a.get("reason", "")))
    check("get_asset exposes commissioning date, not just install date",
          a.get("commissioning_date") is not None and "install_date" in a, "")

    missing = db.one("SELECT serial FROM Assets WHERE commissioning_date IS NULL")
    a = T.get_asset(db, missing["serial"])
    check("get_asset flags a missing commissioning record (trap 12)",
          a.get("commissioning_date_missing") is True and "2.3" in a.get("note", ""), "")

    a = T.get_asset(db, "CIE-4000-CH-09999")
    check("get_asset returns found=false, not an error, for an unknown serial",
          a["found"] is False and "suggested_action" in a, "")

    # --- get_running_hours -------------------------------------------
    h = T.get_running_hours(db, "CIE-4000-CH-01642", "2026-06-18")
    check("get_running_hours returns a reading at or before the repair date",
          h["found"] and h["as_of_date"] <= "2026-06-18", str(h))

    no_tele = db.one(
        "SELECT c.serial FROM Claims c LEFT JOIN AssetTelemetry t ON t.serial = c.serial "
        "WHERE t.serial IS NULL AND c.serial IN (SELECT serial FROM Assets)")
    if no_tele:
        h = T.get_running_hours(db, no_tele["serial"], "2026-06-18")
        check("get_running_hours reports absence for an asset with no telemetry (trap 12)",
              h["found"] is False and "suggested_action" in h, str(h))
    else:
        check("an asset with a claim but no telemetry exists (trap 12)", False,
              "none found - the abstention path is not armed in the database")

    # --- lookup_part: supersession (trap 7) ---------------------------
    p = T.lookup_part(db, "P-44120")
    check("lookup_part resolves the supersession chain (trap 7)",
          p["current_part_no"] == "P-44120-A" and p["supersession_chain"] ==
          ["P-44120", "P-44120-A"], str(p.get("supersession_chain")))
    check("lookup_part prices the superseding part at 191,200",
          p["current_price_inr"] == 191200, str(p.get("current_price_inr")))

    # --- get_dealer: uplift asymmetry (trap 8) ------------------------
    f, n = T.get_dealer(db, "D-IN-01"), T.get_dealer(db, "D-IN-02")
    check("get_dealer shows Fabrikam with no uplift (trap 8)", f["uplift_pct"] == 0.0,
          str(f.get("uplift_pct")))
    check("get_dealer shows Northwind with a 5% uplift (trap 8)", n["uplift_pct"] == 5.0,
          str(n.get("uplift_pct")))

    # --- get_tsb_index: THE STALE TABLE (trap 1) ----------------------
    idx = T.get_tsb_index(db, family="4000-CH", serial="CIE-4000-CH-01642")
    entry = next(e for e in idx["entries"] if e["tsb_id"] == "TSB-C-0051")
    check("index records TSB-C-0051 ending at 1500, not 1850 (trap 1 armed)",
          entry["serial_to"] == 1500, str(entry["serial_to"]))
    check("index says serial 01642 is OUT of range - and is wrong",
          entry["index_says_in_range"] is False, str(entry))
    check("index carries an explicit non-authority warning",
          "NOT authoritative" in idx["authority_warning"]
          or "not authoritative" in idx["authority_warning"].lower(), "")

    # --- superseded bulletin is visible and marked (trap 5) -----------
    idx = T.get_tsb_index(db, family="2200-AC")
    statuses = {e["tsb_id"]: e["status"] for e in idx["entries"]}
    check("superseded TSB-P-0107 is present and marked Superseded (trap 5)",
          statuses.get("TSB-P-0107") == "Superseded", str(statuses))
    check("current TSB-P-0112 is present and marked Current (trap 5)",
          statuses.get("TSB-P-0112") == "Current", str(statuses))

    # --- goodwill authority tiers (trap 11) ---------------------------
    for amount, role in ((18400, "Service Supervisor"),
                         (67400, "Regional Service Manager"),
                         (312000, "Warranty Operations Head"),
                         (742000, "Director, Aftermarket")):
        g = T.get_goodwill_authority(db, amount)
        check(f"goodwill {amount:>7,} routes to {role}", g["approver_role"] == role,
              str(g.get("approver_role")))
    g = T.get_goodwill_authority(db, 67400)
    check("goodwill response states a channel approval is not authority (trap 11)",
          "does not constitute authority" in g["note"], "")

    # --- service history exposes the part actually fitted -------------
    claim = db.one("SELECT claim_id, serial, claimed_part FROM Claims "
                   "WHERE claimed_part = 'P-44120'")
    if claim:
        hist = T.get_service_history(db, claim["serial"])
        fitted = {j["part_fitted"] for j in hist["jobs"]}
        check("service history shows a different part fitted than claimed (trap 7)",
              "P-44120-A" in fitted and claim["claimed_part"] == "P-44120",
              f"claimed={claim['claimed_part']} fitted={fitted}")
    else:
        check("a claim exists naming a superseded part (trap 7)", False, "none found")

    # --- repair warranty (policy 6.1) ---------------------------------
    rw = db.one("SELECT serial FROM ServiceHistory GROUP BY serial HAVING COUNT(*) > 1")
    prior = T.find_prior_claims(db, rw["serial"])
    check("find_prior_claims returns more than one job for a repeat-repair asset",
          prior["match_count"] > 1, str(prior["match_count"]))
    check("find_prior_claims cites the 90-day repair warranty rule",
          "6.1" in prior["note"] and "90 days" in prior["note"], "")

    # --- actions are drafts -------------------------------------------
    row = db.one("SELECT claim_id, status FROM Claims WHERE status = 'Submitted' "
                 "ORDER BY claim_id")
    cid, seeded_status = row["claim_id"], row["status"]
    r = T.create_claim_adjudication(db, cid, "approve", ["TSB-C-0051"], 199175.0, "INR",
                                    "test draft")
    check("create_claim_adjudication writes a draft", r["created"] and
          r["draft_id"].startswith("ADJ-"), str(r))
    check("the draft says plainly that nothing has been paid",
          "No payment has been made" in r["status"], str(r.get("status")))

    r = T.create_claim_adjudication(db, cid, "pay_immediately")
    check("an invalid decision is rejected", r["created"] is False, str(r))

    r = T.create_claim_adjudication(db, "C-DOES-NOT-EXIST", "approve")
    check("adjudicating an unknown claim is rejected", r["created"] is False, str(r))

    r = T.request_missing_evidence(db, cid, "commissioning_date", "absent from registry")
    check("request_missing_evidence holds the claim rather than declining it",
          r["created"] and r["claim_status"] == "Held", str(r))

    r = T.escalate_goodwill(db, cid, 67400, "Regional Service Manager")
    check("escalate_goodwill records a request, not an approval",
          r["created"] and "not approved" in r["status"], str(r))

    # leave the database as we found it
    db.execute("DELETE FROM ClaimAdjudicationDraft WHERE created_by = 'agent'")
    db.execute("DELETE FROM EvidenceRequest WHERE claim_id = ?", (cid,))
    db.execute("DELETE FROM GoodwillEscalation WHERE claim_id = ?", (cid,))
    db.execute("UPDATE Claims SET status = ? WHERE claim_id = ?", (seeded_status, cid))


if __name__ == "__main__":
    width = max(len(l) for _, l, _ in RESULTS)
    for ok, label, detail in RESULTS:
        line = f"  {'PASS' if ok else 'FAIL'}  {label.ljust(width)}"
        print(line if ok else f"{line}   <- {detail}")
    failed = sum(1 for ok, _, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} checks passed.")
    if failed:
        raise SystemExit(1)
