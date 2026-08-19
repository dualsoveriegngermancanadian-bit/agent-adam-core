"""Agent Adam Core service.

The service exposes a read-only orchestration status view and controlled readiness
endpoints. Financial settlement, subscription activation, and hardware-token
verification are deliberately unavailable until separately implemented through
approved, authenticated providers.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from flask import Flask, jsonify
from flask_cors import CORS

APP_NAME = "Agent Adam Core"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
POOL_CAPACITY = 20
AGENT_POOL = tuple(
    {
        "id": f"ADAM-{index:02d}",
        "status": "ready",
        "specialization": "execution_core" if index <= 5 else "routing_subsystem",
    }
    for index in range(1, POOL_CAPACITY + 1)
)


def _allowed_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _error(message: str, status: int) -> tuple[Any, int]:
    return jsonify({"status": "error", "message": message}), status


def _not_configured(capability: str) -> tuple[Any, int]:
    return jsonify(
        {
            "status": "not_configured",
            "capability": capability,
            "message": f"{capability} is unavailable until an approved, authenticated integration is configured.",
        }
    ), 503


def create_app() -> Flask:
    """Create the HTTP application without enabling development-only settings."""
    app = Flask(__name__)
    app.config.update(JSON_SORT_KEYS=False, MAX_CONTENT_LENGTH=16 * 1024)

    origins = _allowed_origins()
    if origins:
        CORS(app, resources={r"/api/*": {"origins": origins}}, methods=["GET", "POST"])

    @app.get("/health")
    def health_check() -> tuple[Any, int]:
        return jsonify(
            {
                "service": APP_NAME,
                "version": APP_VERSION,
                "status": "operational",
                "timestamp": _timestamp(),
            }
        ), 200

    @app.get("/api/v1/agents")
    def get_agents() -> tuple[Any, int]:
        return jsonify(
            {
                "total_capacity": POOL_CAPACITY,
                "active_agents": len(AGENT_POOL),
                "agents": AGENT_POOL,
                "timestamp": _timestamp(),
            }
        ), 200

    @app.get("/api/v1/readiness")
    def readiness() -> tuple[Any, int]:
        return jsonify(
            {
                "orchestration": "ready",
                "settlement": "not_configured",
                "subscription_provider": "not_configured",
                "hardware_identity_provider": "not_configured",
                "timestamp": _timestamp(),
            }
        ), 200

    @app.post("/api/v1/settlement/micro")
    def settlement_status() -> tuple[Any, int]:
        return _not_configured("Settlement processing")

    @app.post("/api/v1/subscriptions/verify")
    def subscription_status() -> tuple[Any, int]:
        return _not_configured("Subscription verification")

    @app.post("/api/v1/access/hardware-token")
    def hardware_token_status() -> tuple[Any, int]:
        return _not_configured("Hardware-token authentication")

    @app.errorhandler(404)
    def not_found(_: Any) -> tuple[Any, int]:
        return _error("The requested resource was not found.", 404)

    @app.errorhandler(413)
    def request_too_large(_: Any) -> tuple[Any, int]:
        return _error("Request body exceeds the 16 KB limit.", 413)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
