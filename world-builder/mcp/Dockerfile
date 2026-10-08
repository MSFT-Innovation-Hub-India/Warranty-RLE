# Contoso Industrial service claim system - MCP server
# Target: Azure Container Apps (single container, HTTP ingress on $PORT)
# Data:   Azure SQL Database via ODBC Driver 18

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ACCEPT_EULA=Y

WORKDIR /app

# Microsoft ODBC Driver 18 for SQL Server. pyodbc will not import without it,
# and the failure mode is an unhelpful "can't open lib" at runtime.
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl gnupg ca-certificates \
 && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
      | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
 && echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
https://packages.microsoft.com/debian/12/prod bookworm main" \
      > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends msodbcsql18 unixodbc \
 && apt-get purge -y gnupg \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY contoso_service_mcp/ ./contoso_service_mcp/

# Container Apps injects PORT; default to 8000 for local runs.
ENV PORT=8000
EXPOSE 8000

RUN useradd --create-home --uid 10001 appuser
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -fsS "http://localhost:${PORT}/healthz" || exit 1

CMD ["python", "-m", "contoso_service_mcp.server"]
