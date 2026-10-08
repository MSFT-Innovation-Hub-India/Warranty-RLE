"""MCP server for the Contoso Industrial service claim system.

Exposes one read tool (get_claim_dossier, world v3) and three draft-only
action tools over the MCP streamable-HTTP transport, which is what the frontier-tuning runtime calls
after the server is registered with:

    frontier-tuning tools create \
        --name contoso-service \
        --description "Asset registry, telemetry, claims and adjudication actions" \
        --url https://<app>.<region>.azurecontainerapps.io/mcp \
        --auth-scheme AzureAD \
        --aud api://<app-id>

The tool docstrings are part of the world's design. Since world v3 they
describe records only: no tool tells the agent which source governs. Reading
the policy and weighing the documents against the claim system's records is
the competence being measured.

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
    # Stateless: Container Apps runs several replicas, and an in-memory MCP
    # session started on one is unknown to the others (404, "failed to connect").
    stateless_http=True,
    instructions=(
        "Service claim system for Contoso Industrial warranty adjudication. Holds the "
        "asset registry, running-hours telemetry, service history, submitted claims, "
        "partner master data, the parts price list, a bulletin applicability index and "
        "the goodwill authority matrix, and records draft adjudications, evidence "
        "requests and goodwill escalations.\n\n"
        "It does not hold the warranty policy, the regional addenda, the bulletins or "
        "the labour rate card. Those are documents in the Warranty Operations library."
    ),
)


# ---------------------------------------------------------------------------
# read tool - world v3: one dossier per claim
# ---------------------------------------------------------------------------

@mcp.tool()
def get_claim_dossier(claim_id: str) -> dict:
    """Everything the service claim system holds about one claim, in one response.

    Returns:
    - claim: the claim as submitted (repair date, operation code, part claimed,
      labour hours claimed, goodwill requested, status)
    - asset: the registry record for the claim's serial (family, region, site,
      installation and commissioning dates); found=false if the serial is unknown
    - running_hours_at_repair_date: the latest reading on or before the repair date
    - service_history: repair jobs on the asset, with the part fitted on each
    - related_claims: other claims referenced by those jobs, with their status
    - service_partner: the partner record (currency, uplift_pct, agreement_ref,
      submission SLA)
    - parts: price-list records for the parts claimed and fitted, with
      supersession and list prices by currency
    - tsb_applicability_index: the claim system's bulletin index for the family
    - goodwill_authority_matrix: approval tiers by amount

    Absent records are returned as found=false with a reason, not as errors.
    """
    with connect() as db:
        return T.get_claim_dossier(db, claim_id)


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
    instrument_refs names every document relied on, each with its clause or
    row where one applies.

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

    field_name names the record requested. The claim's status becomes Held.
    """
    with connect() as db:
        return T.request_missing_evidence(db, claim_id, field_name, reason)


@mcp.tool()
def escalate_goodwill(claim_id: str, amount: float, approver_role: str) -> dict:
    """Raise a goodwill escalation to the approving role for an amount.

    Records a request for authority. It does not grant authority and it does not
    pay.
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
