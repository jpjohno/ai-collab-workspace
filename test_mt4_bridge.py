import unittest
from mt4_bridge import MT4Bridge

class TestMT4Bridge(unittest.TestCase):
    def setUp(self):
        self.bridge = MT4Bridge()

    def test_push_and_poll_tick(self):
        tick = self.bridge.push_tick("EURUSD", 1.0850, 1.0852)
        self.assertEqual(tick["symbol"], "EURUSD")
        self.assertEqual(tick["bid"], 1.0850)
        polled = self.bridge.poll_ticks("EURUSD")
        self.assertIsNotNone(polled)
        self.assertEqual(polled["ask"], 1.0852)

if __name__ == "__main__":
    unittest.main()
