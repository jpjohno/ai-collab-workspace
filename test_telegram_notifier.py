import unittest
from unittest.mock import patch
from telegram_notifier import TelegramNotifier

class TestTelegramNotifier(unittest.TestCase):
    def setUp(self):
        self.token = "TEST_TOKEN"
        self.chat_id = "TEST_CHAT_ID"
        self.notifier = TelegramNotifier(self.token, self.chat_id, max_messages_per_minute=2)

    @patch('requests.post')
    def test_send_message_success(self, mock_post):
        mock_post.return_value.status_code = 200
        result = self.notifier.send_message("Hello World")
        self.assertTrue(result)
        self.assertEqual(self.notifier.messages_sent, 1)

    @patch('requests.post')
    def test_send_message_failure(self, mock_post):
        mock_post.return_value.status_code = 403
        result = self.notifier.send_message("Hello World")
        self.assertFalse(result)
        self.assertEqual(self.notifier.messages_sent, 0)

    @patch('requests.post')
    def test_rate_limiting(self, mock_post):
        mock_post.return_value.status_code = 200
        self.notifier.send_message("Message 1")
        self.notifier.send_message("Message 2")
        result = self.notifier.send_message("Message 3")  # This should exceed the rate limit
        self.assertFalse(result)
        self.assertEqual(self.notifier.messages_sent, 2)

if __name__ == "__main__":
    unittest.main()
