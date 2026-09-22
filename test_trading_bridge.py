import unittest
from unittest.mock import patch, MagicMock
from trading_bridge import CapitalAPI, IGAPI

class TestCapitalAPI(unittest.TestCase):
    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_capital_key"})
    @patch("requests.get")
    def test_get_market_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"epic": "EURUSD", "bid": 1.0850}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        api = CapitalAPI()
        data = api.get_market_data("EURUSD")
        self.assertEqual(data["epic"], "EURUSD")

    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_capital_key"})
    @patch("requests.get")
    def test_get_market_data_failure(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("API Network Down")
        api = CapitalAPI()
        with self.assertRaises(requests.RequestException):
            api.get_market_data("EURUSD")

class TestIGAPI(unittest.TestCase):
    @patch.dict("os.environ", {"IG_USERNAME": "test_user", "IG_PASSWORD": "password123", "IG_API_KEY": "mock_ig_key"})
    @patch("requests.post")
    def test_authenticate_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"currentAccountId": "ACC123"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        api = IGAPI()
        result = api.authenticate()
        self.assertEqual(result["currentAccountId"], "ACC123")

    @patch.dict("os.environ", {"IG_USERNAME": "test_user", "IG_PASSWORD": "password123", "IG_API_KEY": "mock_ig_key"})
    @patch("requests.post")
    def test_authenticate_failure(self, mock_post):
        import requests
        mock_post.side_effect = requests.RequestException("Auth Rejected")
        api = IGAPI()
        with self.assertRaises(requests.RequestException):
            api.authenticate()

    @patch.dict("os.environ", {"IG_USERNAME": "test_user", "IG_PASSWORD": "password123", "IG_API_KEY": "mock_ig_key"})
    @patch("requests.get")
    def test_get_market_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"instrument": {"name": "Spot Gold"}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        api = IGAPI()
        data = api.get_market_data("CS.D.CFDGOLD.TODAY.IP")
        self.assertEqual(data["instrument"]["name"], "Spot Gold")

    @patch.dict("os.environ", {"IG_USERNAME": "test_user", "IG_PASSWORD": "password123", "IG_API_KEY": "mock_ig_key"})
    @patch("requests.get")
    def test_get_market_data_failure(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("Timeout")
        api = IGAPI()
        with self.assertRaises(requests.RequestException):
            api.get_market_data("CS.D.CFDGOLD.TODAY.IP")

if __name__ == "__main__":
    unittest.main()
