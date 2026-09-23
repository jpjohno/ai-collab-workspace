notifier_code = '''import os
import time
import requests
import logging

logger = logging.getLogger("TelegramNotifier")

class TelegramNotifier:
    def __init__(self, token=None, chat_id=None, max_messages_per_minute=20):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN") or "sandbox_token"
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID") or "sandbox_chat_id"
        self.max_messages_per_minute = max_messages_per_minute
        self.message_timestamps = []
        self.messages_sent = 0

    def send_message(self, message):
        current_time = time.time()
        self.message_timestamps = [t for t in self.message_timestamps if current_time - t < 60]

        if len(self.message_timestamps) >= self.max_messages_per_minute:
            logger.warning("Rate limit exceeded. Try again later.")
            return False

        # Only simulate alert if running strictly with the fallback sandbox token
        if self.token == "sandbox_token":
            logger.info(f"[SANDBOX ALERT] Telegram message simulated: {message[:60]}...")
            self.message_timestamps.append(current_time)
            self.messages_sent += 1
            return True

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            self.message_timestamps.append(current_time)
            self.messages_sent += 1
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            return False
'''

with open("telegram_notifier.py", "w", encoding="utf-8") as f:
    f.write(notifier_code)

print("✅ Aligned TelegramNotifier with test mock handling.")
