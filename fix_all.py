import os
import time
import logging
import subprocess
from trading_bridge import CapitalAPI, IGAPI
from arbitrage_engine import ArbitrageEngine

# 1. Write the clean, complete AutonomousTrader module
trader_code = '''import os
import time
import logging
from trading_bridge import CapitalAPI, IGAPI
from arbitrage_engine import ArbitrageEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AutonomousTrader")

class AutonomousTrader:
    def __init__(self, capital_epic="EURUSD", ig_epic="CS.D.EURUSD.TODAY.IP", min_spread=0.5, trade_size=1.0):
        self.capital_api = CapitalAPI()
        self.ig_api = IGAPI()
        self.engine = ArbitrageEngine(self.capital_api, self.ig_api, min_spread_threshold=min_spread)
        self.capital_epic = capital_epic
        self.ig_epic = ig_epic
        self.min_spread = min_spread
        self.trade_size = trade_size

    def execute_arbitrage_cycle(self):
        logger.info(f"Scanning spreads: Capital ({self.capital_epic}) vs IG ({self.ig_epic})...")
        eval_result = self.engine.evaluate_spread(self.capital_epic, self.ig_epic)
        
        spread = eval_result["best_spread"]
        opportunity = eval_result["opportunity"]
        direction = eval_result["direction"]

        logger.info(f"Spread detected: {spread:.4f} | Target threshold met: {opportunity}")

        if opportunity:
            logger.info(f"🚀 Arbitrage opportunity triggered! Direction: {direction}")
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
            logger.info("No actionable spread discrepancy.")
            return {"executed": False, "spread": spread}

    def run_continuous_loop(self, interval=2, max_iterations=None):
        logger.info(f"Starting continuous scan loop (Interval: {interval}s)...")
        iteration = 0
        try:
            while True:
                iteration += 1
                logger.info(f"--- Cycle #{iteration} ---")
                self.execute_arbitrage_cycle()
                
                if max_iterations and iteration >= max_iterations:
                    logger.info("Reached maximum iterations requested.")
                    break
                    
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Graceful shutdown requested by user.")
'''

with open("autonomous_trader.py", "w", encoding="utf-8") as f:
    f.write(trader_code)
print("✅ Restored complete autonomous_trader.py with loop and cycle execution.")

# 2. Write the verified test suite
test_code = '''import unittest
from unittest.mock import patch
from autonomous_trader import AutonomousTrader

class TestAutonomousTrader(unittest.TestCase):
    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_cap", "IG_USERNAME": "u", "IG_PASSWORD": "p", "IG_API_KEY": "k", "SANDBOX_MODE": "True"})
    @patch("trading_bridge.CapitalAPI.get_market_data")
    @patch("trading_bridge.IGAPI.get_market_data")
    def test_trader_cycle_execution(self, mock_ig_market, mock_cap_market):
        mock_cap_market.return_value = {"bid": 105.0, "ask": 106.0}
        mock_ig_market.return_value = {"bid": 99.0, "ask": 100.0}

        trader = AutonomousTrader(min_spread=1.0)
        res = trader.execute_arbitrage_cycle()
        self.assertTrue(res["executed"])
        self.assertEqual(res["direction"], "SELL_CAPITAL_BUY_IG")
        self.assertEqual(res["capital_order"]["status"], "success")
        self.assertEqual(res["ig_order"]["status"], "success")

    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_cap", "IG_USERNAME": "u", "IG_PASSWORD": "p", "IG_API_KEY": "k", "SANDBOX_MODE": "True"})
    @patch("trading_bridge.CapitalAPI.get_market_data")
    @patch("trading_bridge.IGAPI.get_market_data")
    def test_loop_iterations(self, mock_ig_market, mock_cap_market):
        mock_cap_market.return_value = {"bid": 100.0, "ask": 101.0}
        mock_ig_market.return_value = {"bid": 100.0, "ask": 101.0}
        
        trader = AutonomousTrader(min_spread=1.0)
        trader.run_continuous_loop(interval=0.01, max_iterations=2)

if __name__ == "__main__":
    unittest.main()
'''

with open("test_autonomous_trader.py", "w", encoding="utf-8") as f:
    f.write(test_code)
print("✅ Updated test_autonomous_trader.py.")

# 3. Run full test suite discovery
print("\n🧪 Running full test suite...")
res = subprocess.run(["python", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)

