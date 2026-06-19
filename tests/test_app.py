"""
RPi Zero 2W LED Controller - Web Server Testing Suite

This module contains unit tests to verify that the Flask routes in 'app.py' correctly
handle HTTP GET/POST requests and return the expected HTML template or JSON payloads.

Resources Used:
- 'unittest' framework: Standard Python testing suite.
- 'unittest.mock': Used to patch 'app.controller' calls so we don't hit the physical
  sysfs files during route validation.
- 'app.app.test_client()': Flask's built-in testing client that simulates browser
  requests without starting a real network socket server.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

# Import the Flask application under test
import app


class TestFlaskWebApp(unittest.TestCase):
    """
    TestCase class defining tests for Flask routes and JSON REST APIs.
    """

    def setUp(self) -> None:
        """
        Runs before each test. Creates a clean Flask testing client.
        """
        # Configure app in testing mode (suppresses normal error logging)
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

        # Reset any permission error state for isolated testing
        app.permission_error_message = None

    def test_index_route(self) -> None:
        """
        Verifies that GET / renders the dashboard HTML page successfully.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        # Decode binary response data to string
        html_content = response.data.decode("utf-8")
        self.assertIn("LED Dashboard", html_content)
        self.assertIn("DietPi LED Controller Dashboard", html_content)

    @patch("app.controller.read_status")
    @patch("app.controller.get_trigger")
    def test_api_status(self, mock_get_trig: MagicMock, mock_read_status: MagicMock) -> None:
        """
        Verifies GET /api/led/status returns status, brightness and trigger JSON.
        """
        mock_read_status.return_value = 1
        mock_get_trig.return_value = "heartbeat"

        response = self.client.get("/api/led/status")
        self.assertEqual(response.status_code, 200)

        # Parse JSON output from the response
        data = json.loads(response.data)
        self.assertEqual(data["status"], "ON")
        self.assertEqual(data["brightness"], 1)
        self.assertEqual(data["trigger"], "heartbeat")

    @patch("app.controller.turn_on")
    def test_api_turn_on(self, mock_turn_on: MagicMock) -> None:
        """
        Verifies POST /api/led/on invokes the turn_on method.
        """
        response = self.client.post("/api/led/on")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data["success"])
        mock_turn_on.assert_called_once()

    @patch("app.controller.turn_off")
    def test_api_turn_off(self, mock_turn_off: MagicMock) -> None:
        """
        Verifies POST /api/led/off invokes the turn_off method.
        """
        response = self.client.post("/api/led/off")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data["success"])
        mock_turn_off.assert_called_once()

    @patch("app.controller.set_trigger")
    def test_api_set_trigger(self, mock_set_trig: MagicMock) -> None:
        """
        Verifies POST /api/led/trigger updates trigger value via JSON payload.
        """
        payload = {"name": "heartbeat"}
        # Send a POST request containing JSON data
        response = self.client.post(
            "/api/led/trigger",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data["success"])
        mock_set_trig.assert_called_once_with("heartbeat")

    @patch("app.controller.blink")
    def test_api_blink(self, mock_blink: MagicMock) -> None:
        """
        Verifies POST /api/led/blink starts blinking cycle with JSON arguments.
        """
        payload = {"delay": 0.2, "count": 10}
        response = self.client.post(
            "/api/led/blink",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data["success"])
        mock_blink.assert_called_once_with(0.2, 10)

    def test_api_status_permission_denied(self) -> None:
        """
        Verifies API endpoints return 403 error if a permission check fails on startup.
        """
        # Set a simulated permission error message
        app.permission_error_message = "Mocked permission error (Run with sudo)"

        response = self.client.get("/api/led/status")
        self.assertEqual(response.status_code, 403)

        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Mocked permission error (Run with sudo)")


if __name__ == "__main__":
    unittest.main()
