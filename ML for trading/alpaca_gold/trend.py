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
        "atr_mult_sl": 1.0,      # ATR multiplier for stop-loss (tighter)
        "atr_mult_tp": 2.5       # ATR multiplier for take-profit (aggressive)
    }
    initial_cash = 2000

    def initialize(self):
        self.vars.signal = None
        self.vars.start = START_DATE
        self.sleeptime = "1D"  # Daily bars for Yahoo

    def on_trading_iteration(self):
        bars = self.get_historical_prices(self.parameters['symbol'], 20, "day")
        df = bars.df

        # Calculate momentum (rate of change)
        df['momentum'] = df['close'].pct_change(3)

        # Volatility breakout: price above recent high or below recent low
        df['recent_high'] = df['high'].rolling(5).max()
        df['recent_low'] = df['low'].rolling(5).min()

        # ATR for dynamic stops
        df['H-L'] = df['high'] - df['low']
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(7).mean()

        # Buy signal: strong momentum up or breakout above recent high
        buy_signal = (df['momentum'].iloc[-1] > 0.01) or (df['close'].iloc[-1] > df['recent_high'].iloc[-2])
        # Sell signal: strong momentum down or breakdown below recent low
        sell_signal = (df['momentum'].iloc[-1] < -0.01) or (df['close'].iloc[-1] < df['recent_low'].iloc[-2])

        if buy_signal:
            self.vars.signal = "BUY"
        elif sell_signal:
            self.vars.signal = "SELL"
        else:
            self.vars.signal = None

        self.vars.atr = df['ATR'].iloc[-1]
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
                stop_loss = self.parameters.get("atr_mult_sl", 1.0) * atr
                take_profit = self.parameters.get("atr_mult_tp", 2.5) * atr
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
