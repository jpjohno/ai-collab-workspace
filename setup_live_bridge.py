with open("trading_bridge.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add a live credential validation & ping method to CapitalAPI
validation_methods = '''
    def verify_live_connection(self):
        """Verifies active session credentials against live endpoints."""
        if IS_SANDBOX:
            logger.info(f"[{self.__class__.__name__}] Operating in SANDBOX mode. Live connection check bypassed.")
            return True
        try:
            # Simple ping/account details call to verify token
            url = f"{self.base_url}/session"
            headers = {"X-SECURITY-TOKEN": self.api_key}
            res = requests.get(url, headers=headers, timeout=5)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Connection verification failed: {e}")
            return False
'''

if "def verify_live_connection" not in code:
    # Insert verification method into CapitalAPI and IGAPI
    code = code.replace("    def get_market_data(self, epic):", validation_methods + "\n    def get_market_data(self, epic):")
    with open("trading_bridge.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Injected live connection verification into trading_bridge.py.")
else:
    print("ℹ️ Connection verification already present.")

