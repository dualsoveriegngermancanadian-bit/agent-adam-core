# Agent Adam Core

**Copyright & Ownership (c) 2026 Melvyn Douglas Braun (Prince Mel Braun). All Rights Reserved.**  
**Business Entity:** Dual Sovereign Braun Autonomous Ecosystems

Agent Adam Core is a Flask service that publishes a read-only 20-agent orchestration view and reports integration readiness. It deliberately does **not** execute settlement, activate subscriptions, verify hardware tokens, or move funds until those capabilities have separately approved authenticated integrations.

## Implemented capabilities

| Endpoint | Purpose | Side effects |
| --- | --- | --- |
| `GET /health` | Liveness and release metadata | None |
| `GET /api/v1/agents` | Read-only agent-pool status | None |
| `GET /api/v1/readiness` | Integration-readiness summary | None |
| `POST /api/v1/settlement/micro` | Settlement integration status | Returns `503`; no funds move |
| `POST /api/v1/subscriptions/verify` | Subscription integration status | Returns `503`; no access changes |
| `POST /api/v1/access/hardware-token` | Identity integration status | Returns `503`; no token is accepted |

The service rejects oversized request bodies. Browser-origin access is disabled by default and can be restricted with `CORS_ALLOWED_ORIGINS` when a browser client is introduced.

## Local run

Create a virtual environment, install dependencies, and start the service:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
```

For local development only, `python app.py` is also supported. Do not use Flask development mode for a public deployment.

## Configuration

Copy `.env.example` to your deployment provider’s environment configuration. `APP_VERSION` is optional. Set `CORS_ALLOWED_ORIGINS` only to the exact HTTPS origins that need browser access. No banking, payment, or provider credentials belong in this repository.

## Release checks

Before releasing, run:

```bash
gunicorn --check-config app:app
curl http://127.0.0.1:5000/health
```

Real settlement, subscriptions, and hardware-token verification need separately approved integrations, durable audit storage, authorization controls, webhook verification, rate limiting, and operational monitoring before release.

## Ownership

Unauthorized copying, distribution, modification, or commercial utilization of this software, its routing logic, or architecture without explicit written consent from the owner is prohibited.
