"""Entra ID bearer-token validation.

Enabled when ENTRA_TENANT_ID and API_AUDIENCE are both set; skipped otherwise so
the server runs locally without an identity provider. The frontier-tuning
runtime calls this server with a token whose audience is the app ID URI
registered via `frontier-tuning tools create --auth-scheme AzureAD --aud <uri>`.
"""

from __future__ import annotations

import os
from functools import lru_cache

TENANT_ID = os.environ.get("ENTRA_TENANT_ID", "")
AUDIENCE = os.environ.get("API_AUDIENCE", "")
ENABLED = bool(TENANT_ID and AUDIENCE)


@lru_cache(maxsize=1)
def _jwks_client():
    from jwt import PyJWKClient
    return PyJWKClient(f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys")


def validate(authorization_header: str | None) -> dict:
    """Return the decoded claims, or raise ValueError."""
    if not ENABLED:
        return {"sub": "local-dev", "aud": "local", "_validation": "disabled"}

    if not authorization_header or not authorization_header.lower().startswith("bearer "):
        raise ValueError("Missing or malformed Authorization header")

    import jwt
    token = authorization_header.split(" ", 1)[1]
    try:
        key = _jwks_client().get_signing_key_from_jwt(token).key
        return jwt.decode(
            token, key, algorithms=["RS256"], audience=AUDIENCE,
            issuer=f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
        )
    except Exception as exc:                       # noqa: BLE001 - surfaced as 401
        raise ValueError(f"Token validation failed: {exc}") from exc
