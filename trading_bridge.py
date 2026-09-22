import os
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
