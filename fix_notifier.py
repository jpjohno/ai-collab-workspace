import re

with open("telegram_notifier.py", "r", encoding="utf-8") as f:
    code = f.read()

# Make token and chat_id optional with env var / sandbox fallbacks
old_init = re.search(r"def __init__\(self,.*?\):", code, re.DOTALL)
if old_init:
    new_init = (
        "def __init__(self, token=None, chat_id=None):\n"
        "        import os\n"
        "        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN') or 'sandbox_token'\n"
        "        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID') or 'sandbox_chat_id'"
    )
    # Replace the __init__ signature and variable assignments
    code = re.sub(
        r"def __init__\(self,.*?\):(\s+self\.token\s*=\s*token)?(\s+self\.chat_id\s*=\s*chat_id)?",
        new_init,
        code,
        count=1
    )

with open("telegram_notifier.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Patched telegram_notifier.py with environment fallbacks.")
