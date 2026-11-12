import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "flask-mongodb-app")))

try:
    from app import app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class FlaskAppTestCase(unittest.TestCase):
    # Initializes test client and verifies Flask availability before running tests
    def setUp(self):
        if not FLASK_AVAILABLE:
            self.skipTest("Flask is not installed in the local host interpreter. Install requirements.txt or execute in Docker.")
        self.client = app.test_client()
        self.client.testing = True

    # Verifies root endpoint returns HTTP 200 and expected welcome message
    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to the Flask app! The current time is:", response.data)

    # Verifies data insertion on POST endpoint returns HTTP 201
    @patch("app.collection")
    def test_post_data_success(self, mock_collection):
        mock_collection.insert_one.return_value = MagicMock()
        payload = {"sampleKey": "sampleValue"}
        response = self.client.post("/data", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"status": "Data inserted"})
        mock_collection.insert_one.assert_called_once_with(payload)

    # Verifies data endpoint returns HTTP 400 when invalid non-JSON body is sent
    def test_post_data_invalid_json(self):
        response = self.client.post(
            "/data",
            data="plain string, not json",
            content_type="text/plain"
        )
        self.assertEqual(response.status_code, 400)

    # Verifies data retrieval on GET endpoint returns list of stored records
    @patch("app.collection")
    def test_get_data(self, mock_collection):
        mock_collection.find.return_value = [{"sampleKey": "sampleValue"}]
        response = self.client.get("/data")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [{"sampleKey": "sampleValue"}])


if __name__ == "__main__":
    unittest.main()
