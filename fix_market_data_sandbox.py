with open("trading_bridge.py", "r", encoding="utf-8") as f:
    code = f.read()

# Mock Capital get_market_data in sandbox mode
capital_target = '''    def get_market_data(self, epic):
        url = f"{self.base_url}/markets/{epic}"
        headers = {"X-SECURITY-TOKEN": self.api_key}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            logger.error(f"CapitalAPI request failed: {e}")
            raise'''

capital_replacement = '''    def get_market_data(self, epic):
        if IS_SANDBOX:
            base_bid = round(1.0850 + random.uniform(-0.0020, 0.0040), 4)
            base_ask = round(base_bid + 0.0002, 4)
            return {"epic": epic, "snapshot": {"bid": base_bid, "offer": base_ask}, "bid": base_bid, "ask": base_ask}
        url = f"{self.base_url}/markets/{epic}"
        headers = {"X-SECURITY-TOKEN": self.api_key}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            logger.error(f"CapitalAPI request failed: {e}")
            raise'''

# Mock IG get_market_data in sandbox mode
ig_target = '''    def get_market_data(self, epic):
        url = f"{self.base_url}/markets/{epic}"
        headers = {"X-IG-API-KEY": self.api_key}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            logger.error(f"IGAPI request failed: {e}")
            raise'''

ig_replacement = '''    def get_market_data(self, epic):
        if IS_SANDBOX:
            base_bid = round(1.0850 + random.uniform(-0.0020, 0.0020), 4)
            base_ask = round(base_bid + 0.0002, 4)
            return {"epic": epic, "snapshot": {"bid": base_bid, "offer": base_ask}, "bid": base_bid, "ask": base_ask}
        url = f"{self.base_url}/markets/{epic}"
        headers = {"X-IG-API-KEY": self.api_key}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            logger.error(f"IGAPI request failed: {e}")
            raise'''

code = code.replace(capital_target, capital_replacement)
code = code.replace(ig_target, ig_replacement)

with open("trading_bridge.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Added sandbox market data simulation to trading_bridge.py")
