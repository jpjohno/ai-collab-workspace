import time
import requests

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str, max_messages_per_minute: int = 20):
        self.token = token
        self.chat_id = chat_id
        self.max_messages_per_minute = max_messages_per_minute
        self.messages_sent = 0
        self.start_time = None

    def send_message(self, text: str) -> bool:
        if self.start_time is None or time.time() - self.start_time > 60:
            self.start_time = time.time()
            self.messages_sent = 0

        if self.messages_sent >= self.max_messages_per_minute:
            print('Rate limit exceeded. Try again later.')
            return False
        
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {'chat_id': self.chat_id, 'text': text}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            self.messages_sent += 1
            return True
        else:
            print('Failed to send message:', response.content)
            return False
