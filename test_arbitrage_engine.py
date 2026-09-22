import unittest
from unittest.mock import MagicMock
from arbitrage_engine import ArbitrageEngine

class TestArbitrageEngine(unittest.TestCase):
    def setUp(self):
        self.mock_cap = MagicMock()
        self.mock_ig = MagicMock()
        self.engine = ArbitrageEngine(self.mock_cap, self.mock_ig, min_spread_threshold=1.0)

    def test_positive_spread(self):
        # Cap Bid 105, IG Ask 100 -> Spread = +5.0 (exceeds threshold 1.0)
        self.mock_cap.get_market_data.return_value = {"bid": 105.0, "ask": 106.0}
        self.mock_ig.get_market_data.return_value = {"bid": 99.0, "ask": 100.0}

        result = self.engine.evaluate_spread("CAP_EURUSD", "IG_EURUSD")
        self.assertTrue(result["opportunity"])
        self.assertEqual(result["best_spread"], 5.0)
        self.assertEqual(result["direction"], "SELL_CAPITAL_BUY_IG")

    def test_negative_spread(self):
        # Cap Bid 100, IG Ask 102 -> No arbitrage
        self.mock_cap.get_market_data.return_value = {"bid": 100.0, "ask": 101.0}
        self.mock_ig.get_market_data.return_value = {"bid": 101.0, "ask": 102.0}

        result = self.engine.evaluate_spread("CAP_EURUSD", "IG_EURUSD")
        self.assertFalse(result["opportunity"])

    def test_api_exception_handling(self):
        self.mock_cap.get_market_data.side_effect = RuntimeError("Feed disconnected")
        with self.assertRaises(RuntimeError):
            self.engine.evaluate_spread("CAP_EURUSD", "IG_EURUSD")

if __name__ == "__main__":
    unittest.main()
