import logging

logger = logging.getLogger("ArbitrageEngine")

class ArbitrageEngine:
    def __init__(self, capital_api, ig_api, min_spread_threshold=0.5):
        self.capital_api = capital_api
        self.ig_api = ig_api
        self.min_spread_threshold = min_spread_threshold

    def evaluate_spread(self, capital_epic, ig_epic):
        capital_data = self.capital_api.get_market_data(capital_epic)
        ig_data = self.ig_api.get_market_data(ig_epic)

        # Extract bid/ask safely
        cap_bid = float(capital_data.get("bid", capital_data.get("snapshot", {}).get("bid", 0)))
        cap_ask = float(capital_data.get("ask", capital_data.get("snapshot", {}).get("offer", 0)))
        
        ig_bid = float(ig_data.get("bid", ig_data.get("snapshot", {}).get("bid", 0)))
        ig_ask = float(ig_data.get("ask", ig_data.get("snapshot", {}).get("offer", 0)))

        # Strategy 1: Buy IG, Sell Capital
        spread_1 = cap_bid - ig_ask
        # Strategy 2: Buy Capital, Sell IG
        spread_2 = ig_bid - cap_ask

        best_spread = max(spread_1, spread_2)
        direction = "SELL_CAPITAL_BUY_IG" if spread_1 >= spread_2 else "SELL_IG_BUY_CAPITAL"

        opportunity = best_spread >= self.min_spread_threshold

        return {
            "opportunity": opportunity,
            "best_spread": best_spread,
            "direction": direction,
            "capital": {"bid": cap_bid, "ask": cap_ask},
            "ig": {"bid": ig_bid, "ask": ig_ask}
        }
