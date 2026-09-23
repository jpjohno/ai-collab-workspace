import subprocess
from github import Github, Auth
import os

def run_fix():
    token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(token) if token else None
    g = Github(auth=auth) if auth else None
    repo = g.get_user().get_repo("ai-collab-workspace") if g else None

    # Standardize arbitrage_engine.py with transparent calculation
    engine_code = '''import logging

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
'''
    with open("arbitrage_engine.py", "w", encoding="utf-8") as f:
        f.write(engine_code)

    # Unit tests with clear numeric bounds
    test_code = '''import unittest
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
'''
    with open("test_arbitrage_engine.py", "w", encoding="utf-8") as f:
        f.write(test_code)

    # Commit to GitHub
    if repo:
        try:
            f_obj = repo.get_contents("arbitrage_engine.py")
            repo.update_file("arbitrage_engine.py", "Refactor evaluation logic in ArbitrageEngine", engine_code, f_obj.sha)
            print("✅ Updated arbitrage_engine.py on GitHub.")
        except Exception as e:
            print(f"GitHub notice (arbitrage_engine): {e}")

        try:
            t_obj = repo.get_contents("test_arbitrage_engine.py")
            repo.update_file("test_arbitrage_engine.py", "Fix test mock values in test_arbitrage_engine.py", test_code, t_obj.sha)
            print("✅ Updated test_arbitrage_engine.py on GitHub.")
        except Exception as e:
            print(f"GitHub notice (test_arbitrage_engine): {e}")

    # Run discovered test suite
    print("\n🧪 Running full test suite...")
    res = subprocess.run(["python", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)

if __name__ == "__main__":
    run_fix()
