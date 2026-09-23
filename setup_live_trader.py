import subprocess
import os
from github import Github, Auth

def setup_and_run():
    token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(token) if token else None
    g = Github(auth=auth) if auth else None
    repo = g.get_user().get_repo("ai-collab-workspace") if g else None

    trader_code = '''import os
import time
import logging
from trading_bridge import CapitalAPI, IGAPI
from arbitrage_engine import ArbitrageEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LiveTrader")

class AutonomousTrader:
    def __init__(self, capital_epic="EURUSD", ig_epic="CS.D.EURUSD.TODAY.IP", min_spread=0.5, trade_size=1.0):
        self.capital_api = CapitalAPI()
        self.ig_api = IGAPI()
        self.engine = ArbitrageEngine(self.capital_api, self.ig_api, min_spread_threshold=min_spread)
        self.capital_epic = capital_epic
        self.ig_epic = ig_epic
        self.trade_size = trade_size

    def execute_arbitrage_cycle(self):
        logger.info(f"Scanning spreads for Capital ({self.capital_epic}) vs IG ({self.ig_epic})...")
        
        # In sandbox mode, mock prices can be injected or live snapshot polled
        eval_result = self.engine.evaluate_spread(self.capital_epic, self.ig_epic)
        
        spread = eval_result["best_spread"]
        opportunity = eval_result["opportunity"]
        direction = eval_result["direction"]

        logger.info(f"Spread detected: {spread:.4f} | Threshold target met: {opportunity}")

        if opportunity:
            logger.info(f"🚀 Arbitrage opportunity triggered! Strategy direction: {direction}")
            if direction == "SELL_CAPITAL_BUY_IG":
                cap_res = self.capital_api.place_order(self.capital_epic, "SELL", self.trade_size)
                ig_res = self.ig_api.place_order(self.ig_epic, "BUY", self.trade_size)
            else:
                cap_res = self.capital_api.place_order(self.capital_epic, "BUY", self.trade_size)
                ig_res = self.ig_api.place_order(self.ig_epic, "SELL", self.trade_size)

            return {
                "executed": True,
                "direction": direction,
                "spread": spread,
                "capital_order": cap_res,
                "ig_order": ig_res
            }
        else:
            logger.info("No actionable spread discrepancy exceeding threshold.")
            return {"executed": False, "spread": spread}

if __name__ == "__main__":
    trader = AutonomousTrader()
    # Execute a single scan and execution cycle
    trader.execute_arbitrage_cycle()
'''

    with open("autonomous_trader.py", "w", encoding="utf-8") as f:
        f.write(trader_code)

    # Sync to GitHub
    if repo:
        try:
            existing = repo.get_contents("autonomous_trader.py")
            repo.update_file("autonomous_trader.py", "Add live autonomous trader runner", trader_code, existing.sha)
            print("✅ Pushed autonomous_trader.py to GitHub.")
        except Exception:
            repo.create_file("autonomous_trader.py", "Add live autonomous trader runner", trader_code)
            print("✨ Created autonomous_trader.py on GitHub.")

    # Unit test for the trader loop
    test_trader_code = '''import unittest
from unittest.mock import patch, MagicMock
from autonomous_trader import AutonomousTrader

class TestAutonomousTrader(unittest.TestCase):
    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_cap", "IG_USERNAME": "u", "IG_PASSWORD": "p", "IG_API_KEY": "k", "SANDBOX_MODE": "True"})
    @patch("trading_bridge.CapitalAPI.get_market_data")
    @patch("trading_bridge.IGAPI.get_market_data")
    def test_trader_cycle_execution(self, mock_ig_market, mock_cap_market):
        # Cap Bid 105 vs IG Ask 100 -> Spread 5.0 (Opportunity)
        mock_cap_market.return_value = {"bid": 105.0, "ask": 106.0}
        mock_ig_market.return_value = {"bid": 99.0, "ask": 100.0}

        trader = AutonomousTrader(min_spread=1.0)
        res = trader.execute_arbitrage_cycle()
        self.assertTrue(res["executed"])
        self.assertEqual(res["direction"], "SELL_CAPITAL_BUY_IG")
        self.assertEqual(res["capital_order"]["status"], "success")
        self.assertEqual(res["ig_order"]["status"], "success")

if __name__ == "__main__":
    unittest.main()
'''
    with open("test_autonomous_trader.py", "w", encoding="utf-8") as f:
        f.write(test_trader_code)

    if repo:
        try:
            existing_t = repo.get_contents("test_autonomous_trader.py")
            repo.update_file("test_autonomous_trader.py", "Add test suite for autonomous trader", test_trader_code, existing_t.sha)
            print("✅ Pushed test_autonomous_trader.py to GitHub.")
        except Exception:
            repo.create_file("test_autonomous_trader.py", "Add test suite for autonomous trader", test_trader_code)
            print("✨ Created test_autonomous_trader.py on GitHub.")

    print("\n🧪 Executing full test suite with new trader module...")
    res = subprocess.run(["python", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)

if __name__ == "__main__":
    setup_and_run()
