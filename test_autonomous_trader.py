import unittest
from unittest.mock import patch, MagicMock
from autonomous_trader import AutonomousTrader

class TestAutonomousTrader(unittest.TestCase):
    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_cap", "IG_USERNAME": "u", "IG_PASSWORD": "p", "IG_API_KEY": "k", "SANDBOX_MODE": "True"})
    @patch("trading_bridge.CapitalAPI.get_market_data")
    @patch("trading_bridge.IGAPI.get_market_data")
    def test_single_cycle_execution(self, mock_ig_market, mock_cap_market):
        mock_cap_market.return_value = {"bid": 105.0, "ask": 106.0}
        mock_ig_market.return_value = {"bid": 99.0, "ask": 100.0}

        trader = AutonomousTrader(min_spread=1.0)
        res = trader.execute_arbitrage_cycle()
        self.assertTrue(res["executed"])
        self.assertEqual(res["direction"], "SELL_CAPITAL_BUY_IG")
        self.assertEqual(res["capital_order"]["status"], "success")

    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_cap", "IG_USERNAME": "u", "IG_PASSWORD": "p", "IG_API_KEY": "k", "SANDBOX_MODE": "True"})
    @patch("trading_bridge.CapitalAPI.get_market_data")
    @patch("trading_bridge.IGAPI.get_market_data")
    def test_multi_asset_loop(self, mock_ig_market, mock_cap_market):
        mock_cap_market.return_value = {"bid": 100.0, "ask": 101.0}
        mock_ig_market.return_value = {"bid": 100.0, "ask": 101.0}

        test_inst = [{"symbol": "TEST/USD", "capital_epic": "TEST", "ig_epic": "CS.D.TEST.IP", "min_spread": 0.1, "size": 1.0}]
        trader = AutonomousTrader(instruments=test_inst)
        trader.run_continuous_loop(interval=0.01, max_iterations=2)

if __name__ == "__main__":
    unittest.main()
