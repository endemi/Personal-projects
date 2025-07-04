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
        "atr_mult_sl": 1.5,      # ATR multiplier for stop-loss
        "atr_mult_tp": 3.0       # ATR multiplier for take-profit
    }
    initial_cash = 2000

    def initialize(self):
        self.vars.signal = None
        self.vars.start = START_DATE
        self.sleeptime = "1D"  # Daily bars for Yahoo

    def on_trading_iteration(self):
        bars = self.get_historical_prices(self.parameters['symbol'], 10, "day")
        df = bars.df

        # Even faster EMAs for more trades
        df['fast_ema'] = df['close'].ewm(span=2).mean()
        df['slow_ema'] = df['close'].ewm(span=4).mean()

        # Signal logic: EMA cross
        df['Signal'] = np.where(
            (df['fast_ema'] > df['slow_ema']) & (df['fast_ema'].shift(1) <= df['slow_ema'].shift(1)),
            "BUY", None
        )
        df['Signal'] = np.where(
            (df['fast_ema'] < df['slow_ema']) & (df['fast_ema'].shift(1) >= df['slow_ema'].shift(1)),
            "SELL", df['Signal']
        )

        self.vars.signal = df.iloc[-1].Signal
        self.execute_trade()

    def execute_trade(self):
        symbol = self.parameters['symbol']
        price = self.get_last_price(symbol)
        cash = self.get_cash()
        pos = self.get_position(symbol)
        quantity = int(cash * 0.8 // price)
        atr = self.vars.atr if hasattr(self.vars, "atr") and self.vars.atr is not None else 1

        # ATR-based stop-loss and take-profit
        if pos:
            entry_price = getattr(pos, "avg_price", None)
            if entry_price is not None:
                stop_loss = self.parameters.get("atr_mult_sl", 1.5) * atr
                take_profit = self.parameters.get("atr_mult_tp", 3.0) * atr
                if price <= entry_price - stop_loss:
                    self.sell_all()
                    return
                if price >= entry_price + take_profit:
                    self.sell_all()
                    return

        # Buy if signal and can afford at least 1 share
        if self.vars.signal == 'BUY' and quantity > 0:
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)
        # Sell only if signal and have a position
        elif self.vars.signal == 'SELL' and pos:
            self.sell_all()
