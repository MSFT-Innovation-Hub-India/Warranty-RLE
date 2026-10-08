"""Database access for the Contoso service claim system.

SQLite locally and in tests, **Azure SQL Database** when deployed. The two
dialects differ in three ways that matter, all handled here so that neither
tools.py nor the tests have to know which engine they are talking to:

1. **Row limiting.** SQLite has ``LIMIT n``; T-SQL has ``TOP (n)``. SQL in
   tools.py is written with no limiting clause at all, and the adapter adds the
   right one.
2. **Types coming back.** pyodbc returns ``datetime.date`` and ``Decimal``
   objects where SQLite returns strings and floats. Both are JSON-hostile and
   would break string date comparisons, so mssql rows are normalised on the way
   out.
3. **Placeholders.** Both use ``?``, which is the one thing that is already
   consistent.

Configuration, in precedence order:

    AZURE_SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:<srv>.database.windows.net,1433;Database=contoso;Encrypt=yes;TrustServerCertificate=no;"
    AZURE_SQL_USE_MANAGED_IDENTITY=true      # omit UID/PWD from the string above
    DATABASE_URL=sqlite:///./contoso.db      # local development and tests
"""

from __future__ import annotations

import os
import re
import sqlite3
import struct
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator

DEFAULT_URL = "sqlite:///./contoso.db"

# SQL_COPT_SS_ACCESS_TOKEN - the ODBC attribute Azure SQL uses for AAD tokens.
_SQL_COPT_SS_ACCESS_TOKEN = 1256
_AZURE_SQL_SCOPE = "https://database.windows.net/.default"


def _managed_identity_token_struct() -> bytes:
    """Encode an Entra access token the way the ODBC driver expects it."""
    from azure.identity import DefaultAzureCredential

    token = DefaultAzureCredential().get_token(_AZURE_SQL_SCOPE).token
    raw = token.encode("utf-16-le")
    return struct.pack("<I", len(raw)) + raw


@contextmanager
def connect() -> Iterator[Any]:
    odbc = os.environ.get("AZURE_SQL_CONNECTION_STRING", "").strip()

    if odbc:
        import pyodbc

        attrs = {}
        if os.environ.get("AZURE_SQL_USE_MANAGED_IDENTITY", "").lower() in ("1", "true", "yes"):
            attrs[_SQL_COPT_SS_ACCESS_TOKEN] = _managed_identity_token_struct()

        con = pyodbc.connect(odbc, attrs_before=attrs) if attrs else pyodbc.connect(odbc)
        try:
            yield _MssqlAdapter(con)
            con.commit()
        finally:
            con.close()
        return

    url = os.environ.get("DATABASE_URL", DEFAULT_URL)
    path = url.replace("sqlite:///", "", 1)
    con = sqlite3.connect(Path(path))
    con.row_factory = sqlite3.Row
    try:
        yield _SqliteAdapter(con)
        con.commit()
    finally:
        con.close()


class _SqliteAdapter:
    """SQLite. Placeholders are ?, limiting is a trailing LIMIT clause."""

    dialect = "sqlite"

    def __init__(self, con: sqlite3.Connection) -> None:
        self._con = con

    @staticmethod
    def _limit(sql: str, n: int | None) -> str:
        return sql if n is None else f"{sql} LIMIT {int(n)}"

    def all(self, sql: str, params: tuple = (), limit: int | None = None) -> list[dict]:
        cur = self._con.execute(self._limit(sql, limit), params)
        return [dict(r) for r in cur.fetchall()]

    def one(self, sql: str, params: tuple = ()) -> dict | None:
        rows = self.all(sql, params, limit=1)
        return rows[0] if rows else None

    def execute(self, sql: str, params: tuple = ()) -> None:
        self._con.execute(sql, params)


class _MssqlAdapter:
    """Azure SQL Database via pyodbc.

    Two translations happen here and nowhere else: TOP (n) in place of LIMIT,
    and normalisation of date and Decimal values so callers see the same ISO
    strings and floats they get from SQLite.
    """

    dialect = "mssql"
    _SELECT = re.compile(r"^\s*SELECT\s+", re.IGNORECASE)

    def __init__(self, con) -> None:
        self._con = con

    @classmethod
    def _limit(cls, sql: str, n: int | None) -> str:
        if n is None:
            return sql
        if not cls._SELECT.match(sql):
            raise ValueError("limit can only be applied to a SELECT")
        return cls._SELECT.sub(f"SELECT TOP ({int(n)}) ", sql, count=1)

    @staticmethod
    def _normalise(value: Any) -> Any:
        # datetime must be tested before date - it is a subclass of it. And the
        # time has to survive: these are audit stamps on draft adjudications,
        # and truncating them to a date would quietly destroy the trail.
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (bytes, bytearray)):
            return value.decode("utf-8", "replace")
        return value

    def all(self, sql: str, params: tuple = (), limit: int | None = None) -> list[dict]:
        with self._con.cursor() as cur:
            cur.execute(self._limit(sql, limit), params)
            cols = [c[0] for c in cur.description]
            return [{c: self._normalise(v) for c, v in zip(cols, row)}
                    for row in cur.fetchall()]

    def one(self, sql: str, params: tuple = ()) -> dict | None:
        rows = self.all(sql, params, limit=1)
        return rows[0] if rows else None

    def execute(self, sql: str, params: tuple = ()) -> None:
        with self._con.cursor() as cur:
            cur.execute(sql, params)
