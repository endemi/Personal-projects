# trend.py

from lumibot.strategies import Strategy
from config import SYMBOL, START_DATE, STOP_LOSS_PERCENT, RSI_PERIOD, RSI_CONFIRMATION_LEVEL
from indicators import calculate_sma, calculate_rsi
import pandas as pd


def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr


class MaximizedTrendStrategy(Strategy):
    parameters = {
        "symbol": SYMBOL
    }

    def initialize(self):
        self.vars.signal = None
        self.vars.start = START_DATE
        self.vars.trailing_stop_price = None
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        symbol = self.parameters["symbol"]
        bars = self.get_historical_prices(symbol, 50, "day")
        df = bars.df

        df["sma_short"] = calculate_sma(df, 9)
        df["sma_long"] = calculate_sma(df, 21)
        df["rsi"] = calculate_rsi(df, RSI_PERIOD)
        df["atr"] = calculate_atr(df, 14)

        buy_signal = (
            (df["sma_short"].iloc[-1] > df["sma_long"].iloc[-1]) and
            (df["sma_short"].iloc[-2] < df["sma_long"].iloc[-2]) and
            (df["rsi"].iloc[-1] > RSI_CONFIRMATION_LEVEL)
        )

        sell_signal = (
            (df["sma_short"].iloc[-1] < df["sma_long"].iloc[-1]) and
            (df["sma_short"].iloc[-2] > df["sma_long"].iloc[-2]) and
            (df["rsi"].iloc[-1] < RSI_CONFIRMATION_LEVEL)
        )

        last_price = self.get_last_price(symbol)
        pos = self.get_position(symbol)
        atr = df["atr"].iloc[-1] if not df["atr"].isnull().iloc[-1] else 1

        # ATR-based position sizing (risk 1 ATR per trade)
        risk_per_trade = self.get_cash() * 0.01  # risk 1% per trade
        quantity = int(risk_per_trade / atr) if atr > 0 else 0

        # Take profit at 2x ATR above entry
        take_profit_price = None
        if pos:
            entry_price = getattr(pos, "avg_price", last_price)  # fallback to last_price if not found
            take_profit_price = entry_price + 2 * atr

        # Buy logic
        if buy_signal and not pos and quantity > 0:
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)
            self.vars.trailing_stop_price = last_price * (1 - STOP_LOSS_PERCENT)

        # Sell logic
        elif sell_signal and pos:
            self.sell_all()
            self.vars.trailing_stop_price = None

        # Trailing stop or take profit
        elif pos:
            if last_price < self.vars.trailing_stop_price:
                self.sell_all()
                self.vars.trailing_stop_price = None
            elif take_profit_price and last_price >= take_profit_price:
                self.sell_all()
                self.vars.trailing_stop_price = None
            else:
                new_stop = last_price * (1 - STOP_LOSS_PERCENT)
                if new_stop > self.vars.trailing_stop_price:
                    self.vars.trailing_stop_price = new_stop
