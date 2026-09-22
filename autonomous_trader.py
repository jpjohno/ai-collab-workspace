import os
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
