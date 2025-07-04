# trend.py

from datetime import datetime
from lumibot.strategies import Strategy
import numpy as np
import pandas as pd
from config import SYMBOL, QUANTITY, START_DATE


class TrendStrategy(Strategy):
    parameters = {
        "symbol": SYMBOL,
        "quantity": QUANTITY,
        "stop_loss": 0.02,      # 2% stop-loss (can be optimized)
        "take_profit": 0.06     # 6% take-profit (3:1 ratio, can be optimized)
    }
    initial_cash = 2000

    def initialize(self):
        self.vars.signal = None
        self.vars.start = START_DATE
        self.sleeptime = "1D"  # Daily bars for Yahoo

    def on_trading_iteration(self):
        bars = self.get_historical_prices(self.parameters['symbol'], 4, "day")
        df = bars.df

        # Ultra-fast EMAs for high trade frequency
        df['fast_ema'] = df['close'].ewm(span=2).mean()
        df['slow_ema'] = df['close'].ewm(span=5).mean()
        df['momentum'] = df['close'].pct_change(2)

        # Signal logic: EMA cross + momentum filter
        buy_signal = (
            (df['fast_ema'].iloc[-1] > df['slow_ema'].iloc[-1]) and
            (df['fast_ema'].iloc[-2] <= df['slow_ema'].iloc[-2]) and
            (df['momentum'].iloc[-1] > 0.01)
        )
        sell_signal = (
            (df['fast_ema'].iloc[-1] < df['slow_ema'].iloc[-1]) and
            (df['fast_ema'].iloc[-2] >= df['slow_ema'].iloc[-2]) and
            (df['momentum'].iloc[-1] < -0.01)
        )

        if buy_signal:
            self.vars.signal = "BUY"
        elif sell_signal:
            self.vars.signal = "SELL"
        else:
            self.vars.signal = None

        self.execute_trade()

    def execute_trade(self):
        symbol = self.parameters['symbol']
        price = self.get_last_price(symbol)
        cash = self.get_cash()
        pos = self.get_position(symbol)
   
        quantity = int(cash * 0.8 // price)

        # Percentage-based stop-loss and take-profit
        if pos:
            entry_price = getattr(pos, "avg_price", None)
            if entry_price is not None:
                stop_loss = self.parameters.get("stop_loss", 0.02)
                take_profit = self.parameters.get("take_profit", 0.06)
                if price <= entry_price * (1 - stop_loss):
                    self.sell_all()
                    return
                if price >= entry_price * (1 + take_profit):
                    self.sell_all()
                    return

        # Buy if signal and can afford at least 1 share
        if self.vars.signal == 'BUY' and quantity > 0:
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)
        # Sell only if signal and have a position
        elif self.vars.signal == 'SELL' and pos:
            self.sell_all()
