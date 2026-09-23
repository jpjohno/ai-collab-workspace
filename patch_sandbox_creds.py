with open("trading_bridge.py", "r", encoding="utf-8") as f:
    code = f.read()

# Make __init__ fallback to mock credentials when IS_SANDBOX is True
code = code.replace(
    'self.api_key = api_key or os.getenv("CAPITAL_API_KEY")\n        if not self.api_key:\n            raise ValueError("CAPITAL_API_KEY environment variable is not set.")',
    'self.api_key = api_key or os.getenv("CAPITAL_API_KEY") or ("sandbox_cap_key" if IS_SANDBOX else None)\n        if not self.api_key:\n            raise ValueError("CAPITAL_API_KEY environment variable is not set.")'
)

code = code.replace(
    'self.username = username or os.getenv("IG_USERNAME")\n        self.password = password or os.getenv("IG_PASSWORD")\n        self.api_key = api_key or os.getenv("IG_API_KEY")\n        if not all([self.username, self.password, self.api_key]):\n            raise ValueError("One or more IG credentials environment variables are not set.")',
    'self.username = username or os.getenv("IG_USERNAME") or ("sandbox_user" if IS_SANDBOX else None)\n        self.password = password or os.getenv("IG_PASSWORD") or ("sandbox_pass" if IS_SANDBOX else None)\n        self.api_key = api_key or os.getenv("IG_API_KEY") or ("sandbox_ig_key" if IS_SANDBOX else None)\n        if not all([self.username, self.password, self.api_key]):\n            raise ValueError("One or more IG credentials environment variables are not set.")'
)

with open("trading_bridge.py", "w", encoding="utf-8") as f:
    f.write(code)
print("✅ Patched trading_bridge.py with seamless sandbox credential fallbacks.")
