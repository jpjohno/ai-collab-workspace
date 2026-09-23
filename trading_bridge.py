import os
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
        self.api_key = api_key or os.getenv("CAPITAL_API_KEY") or ("sandbox_cap_key" if IS_SANDBOX else None)
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
        self.username = username or os.getenv("IG_USERNAME") or ("sandbox_user" if IS_SANDBOX else None)
        self.password = password or os.getenv("IG_PASSWORD") or ("sandbox_pass" if IS_SANDBOX else None)
        self.api_key = api_key or os.getenv("IG_API_KEY") or ("sandbox_ig_key" if IS_SANDBOX else None)
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
