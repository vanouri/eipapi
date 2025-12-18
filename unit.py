import unittest
import requests

class TestP2PPredictionAPI(unittest.TestCase):
    BASE_URL = "http://217.182.105.192:8000"

    def test_root_endpoint(self):
        """Check if the API is online and returns available routes."""
        response = requests.get(f"{self.BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("available_routes", response.json())

    def test_prediction_endpoint(self):
        """Verify the /prediction endpoint returns a valid signal."""
        response = requests.get(f"{self.BASE_URL}/prediction")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("prediction", data)
        
        valid_signals = [-1, 0, 1]
        self.assertIn(data["prediction"], valid_signals, f"Signal {data['prediction']} is not valid")

    def test_reference_endpoint(self):
        """Check if the reference mapping is consistent."""
        response = requests.get(f"{self.BASE_URL}/ref")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["reference"]["1"], "Long Position")
        self.assertEqual(data["reference"]["-1"], "Short Position")

if __name__ == "__main__":
    unittest.main()
