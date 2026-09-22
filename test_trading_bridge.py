import unittest
from unittest.mock import patch, Mock
import requests
from trading_bridge import CapitalAPI, IGAPI

class TestCapitalAPI(unittest.TestCase):
    @patch('trading_bridge.requests.Session.get')
    def test_get_market_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'symbol': 'AAPL', 'price': 150.0}
        
        capital_api = CapitalAPI()
        result = capital_api.get_market_data('AAPL')
        
        self.assertEqual(result, {'symbol': 'AAPL', 'price': 150.0})
        mock_get.assert_called_once()

    @patch('trading_bridge.requests.Session.get')
    def test_get_market_data_failure(self, mock_get):
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found", response=Mock(status=404, text='Not Found'))
        
        capital_api = CapitalAPI()
        result = capital_api.get_market_data('FAKE')
        
        self.assertIsNone(result)
        mock_get.assert_called_once()

class TestIGAPI(unittest.TestCase):
    @patch('trading_bridge.requests.Session.post')
    def test_authenticate_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.headers = {
            'CST': 'fake-cst',
            'X-SECURITY-TOKEN': 'fake-security-token'
        }
        
        ig_api = IGAPI()
        cst, x_sec_token = ig_api.authenticate()
        
        self.assertEqual((cst, x_sec_token), ('fake-cst', 'fake-security-token'))
        mock_post.assert_called_once()

    @patch('trading_bridge.requests.Session.post')
    def test_authenticate_failure(self, mock_post):
        mock_post.return_value.status_code = 403
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("Unauthorized", response=Mock(status=403, text='Unauthorized'))
        
        ig_api = IGAPI()
        cst, x_sec_token = ig_api.authenticate()
        
        self.assertEqual((cst, x_sec_token), (None, None))
        mock_post.assert_called_once()

    @patch('trading_bridge.requests.Session.get')
    def test_get_market_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'market': 'US500', 'bid': 3700.0}
        
        ig_api = IGAPI()
        cst_token = 'fake-cst'
        security_token = 'fake-security-token'
        result = ig_api.get_market_data('US500', cst_token, security_token)
        
        self.assertEqual(result, {'market': 'US500', 'bid': 3700.0})
        mock_get.assert_called_once()

    @patch('trading_bridge.requests.Session.get')
    def test_get_market_data_failure(self, mock_get):
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("Market Not Found", response=Mock(status=404, text='Market Not Found'))
        
        ig_api = IGAPI()
        cst_token = 'fake-cst'
        security_token = 'fake-security-token'
        result = ig_api.get_market_data('FAKE', cst_token, security_token)
        
        self.assertIsNone(result)
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()