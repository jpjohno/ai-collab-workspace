import unittest
from unittest.mock import patch, MagicMock
from trading_bridge import CapitalAPI, IGAPI

class TestTradingExecution(unittest.TestCase):
    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_cap_key", "SANDBOX_MODE": "True"})
    def test_capital_sandbox_order(self):
        api = CapitalAPI()
        res = api.place_order("EURUSD", "BUY", 1.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["provider"], "capital")
        self.assertEqual(res["details"]["direction"], "BUY")

    @patch.dict("os.environ", {"IG_USERNAME": "u", "IG_PASSWORD": "p", "IG_API_KEY": "k", "SANDBOX_MODE": "True"})
    def test_ig_sandbox_order(self):
        api = IGAPI()
        res = api.place_order("CS.D.CFDGOLD.TODAY.IP", "SELL", 0.5)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["provider"], "ig")
        self.assertEqual(res["details"]["direction"], "SELL")

    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_cap_key"})
    @patch("requests.get")
    def test_get_market_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"epic": "EURUSD", "bid": 1.0850}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        api = CapitalAPI()
        data = api.get_market_data("EURUSD")
        self.assertEqual(data["epic"], "EURUSD")

if __name__ == "__main__":
    unittest.main()
