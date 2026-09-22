import requests
import logging
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class APIBase:
    def __init__(self):
        self.session = requests.Session()

    def handle_response(self, response):
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error occurred: {e.response.text}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        return None

class CapitalAPI(APIBase):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("CAPITAL_API_KEY", "default_capital_api_key")
        self.base_url = "https://api-capital.backend-capital.com"

        if self.api_key == "default_capital_api_key":
            logging.warning("Using default API key for CapitalAPI. Set the CAPITAL_API_KEY environment variable for production use.")

    def get_market_data(self, symbol):
        url = f"{self.base_url}/trading/markets/{symbol}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            return self.handle_response(response)
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get market data from Capital: {e}")
            return None

class IGAPI(APIBase):
    def __init__(self):
        super().__init__()
        self.username = os.getenv("IG_USERNAME", "default_username")
        self.password = os.getenv("IG_PASSWORD", "default_password")
        self.api_key = os.getenv("IG_API_KEY", "default_ig_api_key")
        self.base_url = "https://demo-api.ig.com/gateway/deal"

        if "default_" in {self.username, self.password, self.api_key}:
            logging.warning("Using default credentials for IGAPI. Set the IG_USERNAME, IG_PASSWORD, and IG_API_KEY environment variables for production use.")

    def authenticate(self):
        url = f"{self.base_url}/session"
        headers = {
            "X-IG-API-KEY": self.api_key,
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json; charset=UTF-8",
            "Version": "2"
        }
        data = {
            "identifier": self.username,
            "password": self.password
        }

        try:
            response = self.session.post(url, json=data, headers=headers, timeout=10, verify=True)
            response.raise_for_status()
            cst = response.headers.get("CST")
            x_sec_token = response.headers.get("X-SECURITY-TOKEN")
            if cst and x_sec_token:
                logging.info("Authentication successful")
                return cst, x_sec_token
            logging.error("Authentication headers missing in response")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to authenticate with IG: {e}")

        return None, None

    def get_market_data(self, symbol, cst_token, security_token):
        url = f"{self.base_url}/markets/{symbol}"
        headers = {
            "X-IG-API-KEY": self.api_key,
            "X-SECURITY-TOKEN": security_token,
            "CST": cst_token,
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            return self.handle_response(response)
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get market data from IG: {e}")
            return None