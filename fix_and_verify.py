import os
import subprocess
from github import Github, Auth

def run_fix():
    token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(token) if token else None
    g = Github(auth=auth) if auth else None
    repo = g.get_user().get_repo("ai-collab-workspace") if g else None

    # 1. Update trading_bridge.py to accept parameters or environment variables
    trading_bridge_code = '''import os
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradingBridge")

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

class IGAPI:
    def __init__(self, username=None, password=None, api_key=None):
        self.username = username or os.getenv("IG_USERNAME")
        self.password = password or os.getenv("IG_PASSWORD")
        self.api_key = api_key or os.getenv("IG_API_KEY")
        if not all([self.username, self.password, self.api_key]):
            raise ValueError("One or more IG credentials (username, password, API key) environment variables are not set.")
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
'''
    with open("trading_bridge.py", "w", encoding="utf-8") as f:
        f.write(trading_bridge_code)

    # 2. Update test_trading_bridge.py to mock environment variables & HTTP calls
    test_trading_bridge_code = '''import unittest
from unittest.mock import patch, MagicMock
from trading_bridge import CapitalAPI, IGAPI

class TestCapitalAPI(unittest.TestCase):
    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_capital_key"})
    @patch("requests.get")
    def test_get_market_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"epic": "EURUSD", "bid": 1.0850}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        api = CapitalAPI()
        data = api.get_market_data("EURUSD")
        self.assertEqual(data["epic"], "EURUSD")

    @patch.dict("os.environ", {"CAPITAL_API_KEY": "mock_capital_key"})
    @patch("requests.get")
    def test_get_market_data_failure(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("API Network Down")
        api = CapitalAPI()
        with self.assertRaises(requests.RequestException):
            api.get_market_data("EURUSD")

class TestIGAPI(unittest.TestCase):
    @patch.dict("os.environ", {"IG_USERNAME": "test_user", "IG_PASSWORD": "password123", "IG_API_KEY": "mock_ig_key"})
    @patch("requests.post")
    def test_authenticate_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"currentAccountId": "ACC123"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        api = IGAPI()
        result = api.authenticate()
        self.assertEqual(result["currentAccountId"], "ACC123")

    @patch.dict("os.environ", {"IG_USERNAME": "test_user", "IG_PASSWORD": "password123", "IG_API_KEY": "mock_ig_key"})
    @patch("requests.post")
    def test_authenticate_failure(self, mock_post):
        import requests
        mock_post.side_effect = requests.RequestException("Auth Rejected")
        api = IGAPI()
        with self.assertRaises(requests.RequestException):
            api.authenticate()

    @patch.dict("os.environ", {"IG_USERNAME": "test_user", "IG_PASSWORD": "password123", "IG_API_KEY": "mock_ig_key"})
    @patch("requests.get")
    def test_get_market_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"instrument": {"name": "Spot Gold"}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        api = IGAPI()
        data = api.get_market_data("CS.D.CFDGOLD.TODAY.IP")
        self.assertEqual(data["instrument"]["name"], "Spot Gold")

    @patch.dict("os.environ", {"IG_USERNAME": "test_user", "IG_PASSWORD": "password123", "IG_API_KEY": "mock_ig_key"})
    @patch("requests.get")
    def test_get_market_data_failure(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("Timeout")
        api = IGAPI()
        with self.assertRaises(requests.RequestException):
            api.get_market_data("CS.D.CFDGOLD.TODAY.IP")

if __name__ == "__main__":
    unittest.main()
'''
    with open("test_trading_bridge.py", "w", encoding="utf-8") as f:
        f.write(test_trading_bridge_code)

    # 3. Commit the repaired files back to GitHub
    if repo:
        try:
            b_file = repo.get_contents("trading_bridge.py")
            repo.update_file("trading_bridge.py", "Update trading bridge implementation", trading_bridge_code, b_file.sha)
            print("✅ trading_bridge.py pushed to GitHub.")
        except Exception as e:
            print(f"GitHub notice (bridge): {e}")

        try:
            t_file = repo.get_contents("test_trading_bridge.py")
            repo.update_file("test_trading_bridge.py", "Update unit tests with mock environment", test_trading_bridge_code, t_file.sha)
            print("✅ test_trading_bridge.py pushed to GitHub.")
        except Exception as e:
            print(f"GitHub notice (tests): {e}")

    # 4. Run the test suite locally
    print("\n🧪 Running updated test suite locally...")
    res = subprocess.run(["python", "-m", "unittest", "test_trading_bridge.py"], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)

if __name__ == "__main__":
    run_fix()
