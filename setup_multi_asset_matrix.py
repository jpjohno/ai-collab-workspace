import re

# 1. Update autonomous_trader.py with Multi-Instrument Monitoring
trader_code = '''import os
import time
import logging
from trading_bridge import CapitalAPI, IGAPI
from arbitrage_engine import ArbitrageEngine
from telegram_notifier import TelegramNotifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AutonomousTrader")

DEFAULT_INSTRUMENTS = [
    {"symbol": "EUR/USD", "capital_epic": "EURUSD", "ig_epic": "CS.D.EURUSD.TODAY.IP", "min_spread": 0.0001, "size": 1.0},
    {"symbol": "GBP/USD", "capital_epic": "GBPUSD", "ig_epic": "CS.D.GBPUSD.TODAY.IP", "min_spread": 0.0002, "size": 1.0},
    {"symbol": "Gold (XAU/USD)", "capital_epic": "GOLD", "ig_epic": "CS.D.CFDGOLD.TODAY.IP", "min_spread": 0.50, "size": 0.5},
    {"symbol": "Bitcoin (BTC/USD)", "capital_epic": "BTCUSD", "ig_epic": "CS.D.BITCOIN.TODAY.IP", "min_spread": 15.0, "size": 0.1},
]

class AutonomousTrader:
    def __init__(self, capital_epic="EURUSD", ig_epic="CS.D.EURUSD.TODAY.IP", min_spread=0.5, trade_size=1.0, instruments=None):
        self.capital_api = CapitalAPI()
        self.ig_api = IGAPI()
        self.engine = ArbitrageEngine(self.capital_api, self.ig_api, min_spread_threshold=min_spread)
        self.capital_epic = capital_epic
        self.ig_epic = ig_epic
        self.min_spread = min_spread
        self.trade_size = trade_size
        self.instruments = instruments or DEFAULT_INSTRUMENTS
        self.notifier = TelegramNotifier()

    def execute_arbitrage_cycle(self, instrument=None):
        cap_epic = instrument["capital_epic"] if instrument else self.capital_epic
        ig_epic = instrument["ig_epic"] if instrument else self.ig_epic
        threshold = instrument["min_spread"] if instrument else self.min_spread
        size = instrument["size"] if instrument else self.trade_size
        name = instrument["symbol"] if instrument else cap_epic

        logger.info(f"Scanning {name}: Capital ({cap_epic}) vs IG ({ig_epic})...")
        eval_result = self.engine.evaluate_spread(cap_epic, ig_epic)

        spread = eval_result["best_spread"]
        opportunity = spread >= threshold
        direction = eval_result["direction"]

        logger.info(f"[{name}] Spread: {spread:.4f} | Target: {threshold} | Opportunity: {opportunity}")

        if opportunity:
            logger.info(f"🚀 Arbitrage triggered for {name}! Direction: {direction}")
            if direction == "SELL_CAPITAL_BUY_IG":
                cap_res = self.capital_api.place_order(cap_epic, "SELL", size)
                ig_res = self.ig_api.place_order(ig_epic, "BUY", size)
            else:
                cap_res = self.capital_api.place_order(cap_epic, "BUY", size)
                ig_res = self.ig_api.place_order(ig_epic, "SELL", size)

            try:
                alert_msg = (
                    f"🚨 *Arbitrage Executed!*\\n"
                    f"• Pair: `{name}`\\n"
                    f"• Strategy: `{direction}`\\n"
                    f"• Spread: `{spread:.4f}`\\n"
                    f"• Size: `{size}`\\n"
                    f"• Capital Order: {cap_res.get('order_id', 'N/A')}\\n"
                    f"• IG Order: {ig_res.get('order_id', 'N/A')}"
                )
                self.notifier.send_message(alert_msg)
            except Exception as e:
                logger.warning(f"Telegram alert skipped: {e}")

            return {
                "executed": True,
                "symbol": name,
                "direction": direction,
                "spread": spread,
                "capital_order": cap_res,
                "ig_order": ig_res
            }
        else:
            return {"executed": False, "symbol": name, "spread": spread}

    def run_continuous_loop(self, interval=2, max_iterations=None):
        logger.info(f"Starting multi-asset scan loop across {len(self.instruments)} instruments (Interval: {interval}s)...")
        iteration = 0
        try:
            while True:
                iteration += 1
                logger.info(f"================ Cycle #{iteration} ================")
                for inst in self.instruments:
                    self.execute_arbitrage_cycle(instrument=inst)
                
                if max_iterations and iteration >= max_iterations:
                    logger.info("Reached maximum iterations requested.")
                    break
                    
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Graceful shutdown requested by user.")
'''

with open("autonomous_trader.py", "w", encoding="utf-8") as f:
    f.write(trader_code)
print("✅ Multi-asset matrix written to autonomous_trader.py.")

# 2. Update test suite
test_code = '''import unittest
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
'''

with open("test_autonomous_trader.py", "w", encoding="utf-8") as f:
    f.write(test_code)
print("✅ Updated test_autonomous_trader.py.")
