import unittest

from app import create_app


class AgentAdamCoreTests(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_health_is_operational(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["service"], "Agent Adam Core")
        self.assertEqual(response.json["status"], "operational")

    def test_agent_pool_has_twenty_agents(self):
        response = self.client.get("/api/v1/agents")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total_capacity"], 20)
        self.assertEqual(len(response.json["agents"]), 20)

    def test_readiness_does_not_claim_unconfigured_settlement(self):
        response = self.client.get("/api/v1/readiness")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["orchestration"], "ready")
        self.assertEqual(response.json["settlement"], "not_configured")

    def test_settlement_cannot_be_called_before_integration(self):
        response = self.client.post("/api/v1/settlement/micro", json={"amount": "100"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["status"], "not_configured")

    def test_subscription_cannot_activate_access(self):
        response = self.client.post("/api/v1/subscriptions/verify", json={"user_id": "user-001"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["status"], "not_configured")

    def test_unknown_endpoint_is_json_404(self):
        response = self.client.get("/unknown")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["status"], "error")


if __name__ == "__main__":
    unittest.main()
