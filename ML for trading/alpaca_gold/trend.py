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

    def initialize(self):
        self.vars.signal = None
        self.vars.start = START_DATE
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        bars = self.get_historical_prices(self.parameters['symbol'], 22, "day")
        df = bars.df

        df['9-day'] = df['close'].rolling(9).mean()
        df['21-day'] = df['close'].rolling(21).mean()

        df['Signal'] = np.where(
            (df['9-day'] > df['21-day']) & (df['9-day'].shift(1) < df['21-day'].shift(1)),
            "BUY", None
        )
        df['Signal'] = np.where(
            (df['9-day'] < df['21-day']) & (df['9-day'].shift(1) > df['21-day'].shift(1)),
            "SELL", df['Signal']
        )

        self.vars.signal = df.iloc[-1].Signal
        self.execute_trade()

    def execute_trade(self):
        symbol = self.parameters['symbol']
        price = self.get_last_price(symbol)
        cash = self.get_cash()
        quantity = cash * 0.5 // price
        pos = self.get_position(symbol)

        if self.vars.signal == 'BUY':
            if pos:
                self.sell_all()
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)

        elif self.vars.signal == 'SELL':
            if pos:
                self.sell_all()
            quantity = cash * 0.5 // price
            order = self.create_order(symbol, quantity, "sell")
            self.submit_order(order)
