"""
MT4 Live Tick Bridge & Tick Feed Normalizer
Connects MetaTrader 4 Expert Advisor feeds into TradingBridge.
"""
import os
import json
import time
import logging

logger = logging.getLogger("MT4Bridge")

class MT4Bridge:
    def __init__(self, data_pipe_path="/tmp/mt4_ticks.json"):
        self.data_pipe_path = data_pipe_path
        self.last_tick = {}

    def push_tick(self, symbol, bid, ask):
        payload = {
            "symbol": symbol,
            "bid": float(bid),
            "ask": float(ask),
            "timestamp": time.time()
        }
        self.last_tick[symbol] = payload
        return payload

    def poll_ticks(self, symbol):
        if symbol in self.last_tick:
            return self.last_tick[symbol]
        return None
