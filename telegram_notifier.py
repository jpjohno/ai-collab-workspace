import os
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

        # In sandbox mode without a real token, simulate sending
        if self.token == "sandbox_token":
            logger.info(f"[SANDBOX ALERT] Simulated Telegram alert: {message[:50]}...")
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
            # Fail if status code is not 200 (handles test mocks that set status_code)
            if response.status_code != 200:
                logger.error(f"Failed to send message: HTTP {response.status_code}")
                return False
            response.raise_for_status()
            self.message_timestamps.append(current_time)
            self.messages_sent += 1
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
