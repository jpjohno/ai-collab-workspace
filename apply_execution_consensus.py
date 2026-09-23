import subprocess
import os
from github import Github, Auth

def apply_and_verify():
    token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(token) if token else None
    g = Github(auth=auth) if auth else None
    repo = g.get_user().get_repo("ai-collab-workspace") if g else None

    # 1. Update trading_bridge.py with order execution architecture
    trading_bridge_code = '''import os
import random
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradingBridge")

# Safe configuration loading
IS_SANDBOX = os.getenv("SANDBOX_MODE", "True").lower() == "true"

def create_mock_response(provider, details, force_failure=False):
    if force_failure:
        return {"status": "failure", "provider": provider, "message": "Simulated order placement rejection"}
    order_id = f"mock_{provider}_{random.randint(1000, 9999)}"
    return {
        "status": "success",
        "provider": provider,
        "order_id": order_id,
        "details": details,
        "message": "Order executed in sandbox mode"
    }

class CapitalAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("CAPITAL_API_KEY")
        if not self.api_key:
            raise ValueError("CAPITAL_API_KEY environment variable is not set.")
        self.base_url = "https://api-capital.backend-capital.com/api/v1"

    def get_market_data(self, epic):
        url = f"{self.base_url}/markets/{epic}"
        headers = {"X-SECURITY-TOKEN": self.api_key}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            logger.error(f"CapitalAPI request failed: {e}")
            raise

    def place_order(self, epic, direction, size):
        details = {"epic": epic, "direction": direction, "size": size}
        if IS_SANDBOX:
            logger.info(f"[SANDBOX] CapitalAPI order executed: {details}")
            return create_mock_response("capital", details)
        
        # Real execution placeholder
        url = f"{self.base_url}/positions"
        headers = {"X-SECURITY-TOKEN": self.api_key, "Content-Type": "application/json"}
        payload = {"epic": epic, "direction": direction, "size": size}
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()

class IGAPI:
    def __init__(self, username=None, password=None, api_key=None):
        self.username = username or os.getenv("IG_USERNAME")
        self.password = password or os.getenv("IG_PASSWORD")
        self.api_key = api_key or os.getenv("IG_API_KEY")
        if not all([self.username, self.password, self.api_key]):
            raise ValueError("One or more IG credentials environment variables are not set.")
        self.base_url = "https://api.ig.com/deal"

    def authenticate(self):
        url = f"{self.base_url}/session"
        headers = {"X-IG-API-KEY": self.api_key, "Content-Type": "application/json"}
        payload = {"identifier": self.username, "password": self.password}
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            logger.error(f"IGAPI authentication failed: {e}")
            raise

    def get_market_data(self, epic):
        url = f"{self.base_url}/markets/{epic}"
        headers = {"X-IG-API-KEY": self.api_key}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            logger.error(f"IGAPI request failed: {e}")
            raise

    def place_order(self, epic, direction, size):
        details = {"epic": epic, "direction": direction, "size": size}
        if IS_SANDBOX:
            logger.info(f"[SANDBOX] IGAPI order executed: {details}")
            return create_mock_response("ig", details)

        url = f"{self.base_url}/positions/otc"
        headers = {"X-IG-API-KEY": self.api_key, "Content-Type": "application/json"}
        payload = {"epic": epic, "direction": direction, "size": size}
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()
'''
    with open("trading_bridge.py", "w", encoding="utf-8") as f:
        f.write(trading_bridge_code)

    # 2. Update test suite with place_order tests
    test_bridge_code = '''import unittest
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
'''
    with open("test_trading_bridge.py", "w", encoding="utf-8") as f:
        f.write(test_bridge_code)

    # 3. Sync to GitHub
    if repo:
        try:
            b_obj = repo.get_contents("trading_bridge.py")
            repo.update_file("trading_bridge.py", "Implement order execution methods from AI consensus", trading_bridge_code, b_obj.sha)
            print("✅ Pushed updated trading_bridge.py to GitHub.")
        except Exception as e:
            print(f"Bridge sync note: {e}")

        try:
            t_obj = repo.get_contents("test_trading_bridge.py")
            repo.update_file("test_trading_bridge.py", "Add tests for sandbox order placement", test_bridge_code, t_obj.sha)
            print("✅ Pushed updated test_trading_bridge.py to GitHub.")
        except Exception as e:
            print(f"Test sync note: {e}")

    # 4. Run test suite locally
    print("\n🧪 Running full test suite...")
    res = subprocess.run(["python", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)

if __name__ == "__main__":
    apply_and_verify()
