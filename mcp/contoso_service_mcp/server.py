"""MCP server for the Contoso Industrial service claim system.

Exposes nine read tools and three draft-only action tools over the MCP
streamable-HTTP transport, which is what the frontier-tuning runtime calls
after the server is registered with:

    frontier-tuning tools create \
        --name contoso-service \
        --description "Asset registry, telemetry, claims and adjudication actions" \
        --url https://<app>.<region>.azurecontainerapps.io/mcp \
        --auth-scheme AzureAD \
        --aud api://<app-id>

The tool docstrings are part of the world's design, not incidental comments.
get_tsb_index in particular tells the caller that it is not authoritative -
the trap is whether the agent acts on that, not whether it was told.

Run locally:

    DATABASE_URL=sqlite:///../out/db/contoso.db python -m contoso_service_mcp.server
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from . import tools as T
from .db import connect


def _transport_security():
    """DNS-rebinding protection scoped to MCP_ALLOWED_HOSTS (comma-separated).

    The SDK default only admits localhost, so a deployed server rejects its own
    public FQDN with "Invalid Host header". Unset, the SDK default applies.
    """
    hosts = [h.strip() for h in os.environ.get("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
    if not hosts:
        return None
    from mcp.server.transport_security import TransportSecuritySettings
    return TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=hosts)


mcp = FastMCP(
    "contoso-service",
    transport_security=_transport_security(),
    instructions=(
        "Service claim system for Contoso Industrial warranty adjudication. Holds the "
        "asset registry, running-hours telemetry, service history, submitted claims, "
        "partner master data, the parts price list and the goodwill authority matrix, "
        "and records draft adjudications.\n\n"
        "This system does not hold the warranty policy, the regional addenda or the "
        "Technical Service Bulletins. Those are documents in the Warranty Operations "
        "library and govern coverage. Where this system's bulletin applicability index "
        "disagrees with a bulletin document, the document governs (policy 1.4)."
    ),
)


# ---------------------------------------------------------------------------
# read tools
# ---------------------------------------------------------------------------

@mcp.tool()
def get_asset(serial: str) -> dict:
    """Look up an asset in the registry by serial number.

    Returns the product family, owning customer and site, the installing service
    partner, the region, the installation date and the commissioning date.

    Coverage runs from the COMMISSIONING date, not the installation date. Where
    the commissioning date is absent the response says so explicitly; policy 2.3
    provides that coverage cannot then be determined and the installation date
    must not be substituted.

    A serial that is not in the registry returns found=false rather than an
    error, so it can be reported rather than guessed around.
    """
    with connect() as db:
        return T.get_asset(db, serial)


@mcp.tool()
def get_running_hours(serial: str, as_of: str) -> dict:
    """Latest running-hours reading for an asset at or before a date (YYYY-MM-DD).

    Coverage periods carry a running-hours limit as well as a time limit,
    whichever is reached first, so this reading is half of the coverage test.
    Use the date of repair, not today's date.

    Returns found=false where no reading exists. That is a real condition in the
    registry, not a failure of this tool.
    """
    with connect() as db:
        return T.get_running_hours(db, serial, as_of)


@mcp.tool()
def get_service_history(serial: str, months: int = 24) -> dict:
    """Repair jobs recorded against an asset, most recent first.

    part_fitted is the authority on which part was actually installed. The claim
    records what the partner ordered, which is not always the same thing - where
    they differ, policy 4.2 prices the part fitted.
    """
    with connect() as db:
        return T.get_service_history(db, serial, months)


@mcp.tool()
def find_prior_claims(serial: str, component: str | None = None) -> dict:
    """Earlier repairs on an asset, optionally filtered to one component.

    Use this to test policy 6.1: a component replaced under warranty carries a
    further 90 days of coverage from the date that repair was completed, under
    funding code RW, even where the asset's own coverage period has expired.
    """
    with connect() as db:
        return T.find_prior_claims(db, serial, component)


@mcp.tool()
def get_claim(claim_id: str) -> dict:
    """The claim as submitted by the service partner.

    Carries the repair date, the operation code, the labour hours claimed, the
    part the partner claimed against, and any goodwill requested.
    """
    with connect() as db:
        return T.get_claim(db, claim_id)


@mcp.tool()
def get_dealer(dealer_id: str) -> dict:
    """Service partner master record.

    uplift_pct is a handling uplift payable on parts only, and only where the
    partner's Service Partner Agreement expressly grants one (policy 4.3). Most
    partners have none.
    """
    with connect() as db:
        return T.get_dealer(db, dealer_id)


@mcp.tool()
def lookup_part(part_no: str) -> dict:
    """Part record with its supersession chain resolved and list prices by currency.

    Where a part has been superseded, the superseding part's price applies
    (policy 4.2). current_part_no is the end of the chain.
    """
    with connect() as db:
        return T.lookup_part(db, part_no)


@mcp.tool()
def get_tsb_index(family: str | None = None, serial: str | None = None) -> dict:
    """Bulletin applicability index held in this claim system.

    NOT AUTHORITATIVE. This is a reporting table maintained separately from the
    bulletin documents and it is known to lag them. Policy clause 1.4 provides
    that where this index and a bulletin document disagree on a serial range,
    THE BULLETIN DOCUMENT GOVERNS.

    Use this to discover which bulletins may be relevant to a family or serial,
    then read the bulletin itself from the Warranty Operations library and
    adjudicate from that. Where the two disagree, follow the document and report
    the discrepancy.
    """
    with connect() as db:
        return T.get_tsb_index(db, family, serial)


@mcp.tool()
def get_goodwill_authority(amount: float, region: str = "India") -> dict:
    """The authority tier and approving role required for a goodwill amount.

    Policy 7.1 requires the authority to be RECORDED IN THE CLAIM SYSTEM. An
    approval given in conversation, in a channel message or by telephone does
    not constitute authority.
    """
    with connect() as db:
        return T.get_goodwill_authority(db, amount, region)


# ---------------------------------------------------------------------------
# action tools - draft only
# ---------------------------------------------------------------------------

@mcp.tool()
def create_claim_adjudication(claim_id: str, decision: str,
                              instrument_refs: list[str] | None = None,
                              payable: float | None = None,
                              currency: str | None = None,
                              notes: str | None = None) -> dict:
    """Record a DRAFT adjudication against a claim.

    decision is one of: approve, decline, request_evidence, escalate.
    instrument_refs names every instrument relied on, for example
    ["TSB-C-0051", "POL-WAR-4.2 1.4"].

    This creates a draft for human review. No payment is made and no
    notification is sent.
    """
    with connect() as db:
        return T.create_claim_adjudication(db, claim_id, decision, instrument_refs,
                                           payable, currency, notes)


@mcp.tool()
def request_missing_evidence(claim_id: str, field_name: str,
                             reason: str | None = None) -> dict:
    """Record a request for a missing record and put the claim on hold.

    Use where a record needed to determine coverage is absent - a missing
    commissioning date, or no running-hours reading at the date of repair. The
    claim is held, not declined.
    """
    with connect() as db:
        return T.request_missing_evidence(db, claim_id, field_name, reason)


@mcp.tool()
def escalate_goodwill(claim_id: str, amount: float, approver_role: str) -> dict:
    """Raise a goodwill escalation to the approving role for an amount.

    Records a request for authority. It does not grant authority and it does not
    pay. Call get_goodwill_authority first to determine the correct role.
    """
    with connect() as db:
        return T.escalate_goodwill(db, claim_id, amount, approver_role)


# ---------------------------------------------------------------------------
# transport
# ---------------------------------------------------------------------------

def build_app():
    """Starlette app: MCP at /mcp, plus a health probe for Container Apps."""
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    async def healthz(_request):
        try:
            with connect() as db:
                n = db.one("SELECT COUNT(*) AS n FROM Assets")["n"]
            return JSONResponse({"status": "ok", "assets": n})
        except Exception as exc:                        # noqa: BLE001
            return JSONResponse({"status": "degraded", "error": str(exc)},
                                status_code=503)

    app = mcp.streamable_http_app()
    app.router.routes.append(Route("/healthz", healthz, methods=["GET"]))
    return app


def main() -> None:
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(build_app(), host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
