# trend.py

from datetime import datetime
from lumibot.strategies import Strategy
import numpy as np
import pandas as pd
from config import SYMBOL, QUANTITY, START_DATE


class TrendStrategy(Strategy):
    parameters = {
        "symbol": SYMBOL,
        "quantity": QUANTITY
    }
    initial_cash = 2000

    def initialize(self):
        self.vars.signal = None
        self.vars.start = START_DATE
        self.sleeptime = "30m"  # More frequent trading

    def on_trading_iteration(self):
        bars = self.get_historical_prices(self.parameters['symbol'], 30, "day")  # <-- changed "hour" to "day"
        df = bars.df

        # Shorter moving averages for more signals
        df['3-period'] = df['close'].rolling(3).mean()
        df['7-period'] = df['close'].rolling(7).mean()

        # Volatility filter (ATR)
        df['ATR'] = df['close'].rolling(7).std()
        if df['ATR'].iloc[-1] < 0.5:  # Adjust threshold as needed
            self.vars.signal = None
            return

        # Signal when 3-period crosses 7-period
        df['Signal'] = np.where(
            (df['3-period'] > df['7-period']) & (df['3-period'].shift(1) <= df['7-period'].shift(1)),
            "BUY", None
        )
        df['Signal'] = np.where(
            (df['3-period'] < df['7-period']) & (df['3-period'].shift(1) >= df['7-period'].shift(1)),
            "SELL", df['Signal']
        )

        self.vars.signal = df.iloc[-1].Signal
        self.execute_trade()

    def execute_trade(self):
        symbol = self.parameters['symbol']
        price = self.get_last_price(symbol)
        cash = self.get_cash()
        pos = self.get_position(symbol)
        quantity = int(cash * 0.5 // price)

        # Stop-loss and take-profit
        if pos:
            entry_price = getattr(pos, "avg_price", None)
            if entry_price is not None:
                if price <= entry_price * 0.97:
                    self.sell_all()
                    return
                if price >= entry_price * 1.05:
                    self.sell_all()
                    return

        if self.vars.signal == 'BUY':
            if (not pos or cash > price) and quantity > 0:  # Only submit if quantity > 0
                order = self.create_order(symbol, quantity, "buy")
                self.submit_order(order)

        elif self.vars.signal == 'SELL' and pos:
            self.sell_all()
