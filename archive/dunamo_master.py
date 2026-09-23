import sys
import subprocess
import os

REQUIRED_PACKAGES = ["pandas", "numpy", "plotly", "bs4", "lxml"]

def setup_environment():
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

setup_environment()

import pandas as pd
import numpy as np

def load_data(file_path="eurusd_m1.csv"):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        print(f"[DATA] Loaded historical data from: {file_path}")
    else:
        print(f"[DATA] '{file_path}' not found. Generating synthetic M1 EUR/USD dataset...")
        np.random.seed(42)
        dates = pd.date_range("2026-01-01", periods=1000, freq="1min")
        prices = 1.0800 + np.cumsum(np.random.normal(0, 0.00015, 1000))
        df = pd.DataFrame({"Timestamp": dates, "Open": prices, "High": prices+0.0001, "Low": prices-0.0001, "Close": prices})
        df.to_csv(file_path, index=False)
        print(f"[DATA] Created sample dataset: {file_path}")
    return df

class StrategyEngine:
    def __init__(self, df, initial_balance=10000.0, lot_size=0.1, spread_pips=1.0):
        self.df = df.copy()
        self.initial_balance = initial_balance
        self.lot_size = lot_size
        self.spread_cost = spread_pips * 0.0001  # 1 pip on EUR/USD = 0.0001

    def run_ma_crossover(self, fast=10, slow=30):
        df = self.df.copy()
        df['fast_ma'] = df['Close'].rolling(window=fast).mean()
        df['slow_ma'] = df['Close'].rolling(window=slow).mean()
        df['position'] = np.where(df['fast_ma'] > df['slow_ma'], 1, -1)
        df['position'] = df['position'].shift(1)
        
        # Calculate raw price change minus spread on trade entries
        trade_entry = df['position'].diff().abs() > 0
        df['pnl'] = (df['Close'].diff() * df['position']) - (trade_entry * self.spread_cost)
        return self._evaluate("MA Crossover (w/ 1 Pip Spread)", df)

    def run_rsi_reversion(self, period=14, oversold=35, overbought=65):
        df = self.df.copy()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        df['position'] = np.where(df['rsi'] < oversold, 1, np.where(df['rsi'] > overbought, -1, 0))
        df['position'] = df['position'].shift(1)
        
        trade_entry = df['position'].diff().abs() > 0
        df['pnl'] = (df['Close'].diff() * df['position']) - (trade_entry * self.spread_cost)
        return self._evaluate("RSI Mean Reversion (w/ 1 Pip Spread)", df)

    def run_martingale_recovery(self, multiplier=1.5, max_levels=3, grid_pips=0.0020):
        df = self.df.copy()
        balance = self.initial_balance
        trades = []
        equity = [balance]
        
        position = 0
        entry_price = 0.0
        current_lot = self.lot_size
        level = 0

        for price in df['Close']:
            if position == 0:
                position = 1
                entry_price = price
                current_lot = self.lot_size
                level = 1
            else:
                if price <= entry_price - (grid_pips * level) and level < max_levels:
                    level += 1
                    current_lot *= multiplier
                    entry_price = price
                elif price >= entry_price + grid_pips:
                    pnl = ((price - entry_price) - self.spread_cost) * 100000 * current_lot
                    balance += pnl
                    trades.append(pnl)
                    position = 0
                    level = 0
            equity.append(balance)

        return self._calculate_metrics("Martingale Recovery (Grid)", balance, trades, pd.Series(equity))

    def _evaluate(self, name, df):
        pnl = (df['pnl'].fillna(0)) * 100000 * self.lot_size
        equity = self.initial_balance + pnl.cumsum()
        trades = pnl[pnl != 0]
        return self._calculate_metrics(name, equity.iloc[-1], trades, equity)

    def _calculate_metrics(self, name, final_balance, trades, equity_series):
        net_profit = final_balance - self.initial_balance
        trades_series = pd.Series(trades) if not isinstance(trades, pd.Series) else trades
        wins = trades_series[trades_series > 0]
        losses = trades_series[trades_series < 0]
        
        total_trades = len(trades_series)
        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
        profit_factor = (wins.sum() / abs(losses.sum())) if len(losses) > 0 and losses.sum() != 0 else 1.0
        
        peak = equity_series.cummax()
        drawdown = ((equity_series - peak) / peak * 100).min()
        
        return {
            "Strategy": name,
            "Net Profit ($)": round(net_profit, 2),
            "Win Rate (%)": round(win_rate, 2),
            "Profit Factor": round(profit_factor, 2),
            "Max Drawdown (%)": round(abs(drawdown) if not np.isnan(drawdown) else 0, 2),
            "Total Trades": total_trades
        }

if __name__ == "__main__":
    # Target custom CSV if passed via command line argument, else load default
    file_target = sys.argv[1] if len(sys.argv) > 1 else "eurusd_m1.csv"
    
    df = load_data(file_target)
    engine = StrategyEngine(df, spread_pips=1.0)
    
    results = [
        engine.run_ma_crossover(fast=10, slow=30),
        engine.run_rsi_reversion(period=14, oversold=35, overbought=65),
        engine.run_martingale_recovery(multiplier=1.5, max_levels=3)
    ]
    
    summary = pd.DataFrame(results)
    
    print("\n==================================================")
    print("            DUNAMO BACKTEST RESULTS               ")
    print("==================================================")
    print(summary.to_string(index=False))
    print("==================================================\n")
