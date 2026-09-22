# arbitrage_engine.py

import trading_bridge

class ArbitrageEngine:
    def __init__(self, capital_api, ig_api, threshold):
        self.capital_api = capital_api
        self.ig_api = ig_api
        self.threshold = threshold

    def fetch_market_data(self, instrument):
        capital_data = self.capital_api.get_market_data(instrument)
        ig_data = self.ig_api.get_market_data(instrument)
        return capital_data, ig_data

    def calculate_spread_discrepancy(self, capital_data, ig_data):
        capital_bid = capital_data['bid']
        capital_ask = capital_data['ask']
        ig_bid = ig_data['bid']
        ig_ask = ig_data['ask']

        spread_discrepancy = min(
            abs(capital_bid - ig_ask),
            abs(ig_bid - capital_ask)
        )
        return spread_discrepancy

    def evaluate_arbitrage_opportunity(self, instrument):
        capital_data, ig_data = self.fetch_market_data(instrument)
        spread_discrepancy = self.calculate_spread_discrepancy(capital_data, ig_data)

        if spread_discrepancy >= self.threshold:
            return {
                "opportunity": True,
                "capital_data": capital_data,
                "ig_data": ig_data
            }
        else:
            return {
                "opportunity": False,
                "capital_data": capital_data,
                "ig_data": ig_data
            }

# trading_bridge.py (Assuming this file exists)

class CapitalAPI:
    def get_market_data(self, instrument):
        # This method should return a dictionary with 'bid' and 'ask' prices for the given instrument
        pass

class IGAPI:
    def get_market_data(self, instrument):
        # This method should return a dictionary with 'bid' and 'ask' prices for the given instrument
        pass