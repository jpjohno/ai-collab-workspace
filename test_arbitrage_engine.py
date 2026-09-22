import unittest
from unittest.mock import MagicMock, patch
from arbitrage_engine import ArbitrageEngine

class TestArbitrageEngine(unittest.TestCase):

    def setUp(self):
        self.capital_api_mock = MagicMock()
        self.ig_api_mock = MagicMock()
        self.threshold = 1.0
        self.engine = ArbitrageEngine(self.capital_api_mock, self.ig_api_mock, self.threshold)
        self.instrument = 'FOREX:EURUSD'

    def test_positive_spread(self):
        # Setup mock responses for a positive spread scenario
        self.capital_api_mock.get_market_data.return_value = {'bid': 1.1015, 'ask': 1.1025}
        self.ig_api_mock.get_market_data.return_value = {'bid': 1.1000, 'ask': 1.1005}

        result = self.engine.evaluate_arbitrage_opportunity(self.instrument)

        self.assertTrue(result['opportunity'])
        self.capital_api_mock.get_market_data.assert_called_once_with(self.instrument)
        self.ig_api_mock.get_market_data.assert_called_once_with(self.instrument)

    def test_negative_spread(self):
        # Setup mock responses for a negative spread (not passing threshold) scenario
        self.capital_api_mock.get_market_data.return_value = {'bid': 1.1010, 'ask': 1.1020}
        self.ig_api_mock.get_market_data.return_value = {'bid': 1.1015, 'ask': 1.1025}

        result = self.engine.evaluate_arbitrage_opportunity(self.instrument)

        self.assertFalse(result['opportunity'])
        self.capital_api_mock.get_market_data.assert_called_once_with(self.instrument)
        self.ig_api_mock.get_market_data.assert_called_once_with(self.instrument)

    def test_api_exception(self):
        # Setup mock to raise an exception
        self.capital_api_mock.get_market_data.side_effect = Exception("CapitalAPI error")

        with self.assertRaises(Exception) as context:
            self.engine.evaluate_arbitrage_opportunity(self.instrument)

        self.assertTrue("CapitalAPI error" in str(context.exception))
        self.capital_api_mock.get_market_data.assert_called_once_with(self.instrument)
        # The second api call should not even occur due to exception in the first call
        self.ig_api_mock.get_market_data.assert_not_called()

if __name__ == '__main__':
    unittest.main()