# trend.py

from lumibot.strategies import Strategy
from config import SYMBOL, START_DATE, STOP_LOSS_PERCENT, RSI_PERIOD, RSI_CONFIRMATION_LEVEL
from indicators import calculate_sma, calculate_rsi
import pandas as pd
from risk import calculate_quantity


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

        # Use faster/shorter SMAs for more signals
        df["sma_short"] = calculate_sma(df, 5)
        df["sma_long"] = calculate_sma(df, 20)
        df["rsi"] = calculate_rsi(df, 10)  # Shorter RSI for more sensitivity
        df["atr"] = calculate_atr(df, 14)

        # Lower RSI threshold for more trades
        buy_signal = (
            (df["sma_short"].iloc[-1] > df["sma_long"].iloc[-1]) and
            (df["sma_short"].iloc[-2] <= df["sma_long"].iloc[-2]) and
            (df["rsi"].iloc[-1] > 45)
        )

        sell_signal = (
            (df["sma_short"].iloc[-1] < df["sma_long"].iloc[-1]) and
            (df["sma_short"].iloc[-2] >= df["sma_long"].iloc[-2]) and
            (df["rsi"].iloc[-1] < 55)
        )

        last_price = self.get_last_price(symbol)
        pos = self.get_position(symbol)
        atr = df["atr"].iloc[-1] if not df["atr"].isnull().iloc[-1] else 1

        # Use your risk.py for sizing, cap at 50% of portfolio
        cash = self.get_cash()
        max_risk = 0.5
        quantity = int(min(calculate_quantity(cash, last_price, risk_percent=max_risk), cash // last_price))

        # ATR-based stop loss and take profit
        take_profit_price = None
        stop_loss_price = None
        if pos:
            entry_price = getattr(pos, "avg_price", last_price)
            take_profit_price = entry_price + 2 * atr
            stop_loss_price = entry_price - 1.5 * atr

        # Buy logic (allow pyramiding if trend continues and have cash)
        if buy_signal and quantity > 0:
            if not pos or (pos and cash > last_price * quantity):
                order = self.create_order(symbol, quantity, "buy")
                self.submit_order(order)
                self.vars.trailing_stop_price = last_price * (1 - STOP_LOSS_PERCENT)

        # Sell logic
        elif sell_signal and pos:
            self.sell_all()
            self.vars.trailing_stop_price = None

        # ATR-based stop loss or take profit
        elif pos:
            if stop_loss_price and last_price < stop_loss_price:
                self.sell_all()
                self.vars.trailing_stop_price = None
            elif take_profit_price and last_price >= take_profit_price:
                self.sell_all()
                self.vars.trailing_stop_price = None
            else:
                # Trailing stop update
                new_stop = last_price * (1 - STOP_LOSS_PERCENT)
                if new_stop > getattr(self.vars, "trailing_stop_price", 0):
                    self.vars.trailing_stop_price = new_stop


class SimpleETFStrategy(Strategy):
    parameters = {
        "symbol": SYMBOL
    }

    def initialize(self):
        self.vars.trailing_stop_price = None
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        symbol = self.parameters["symbol"]
        bars = self.get_historical_prices(symbol, 60, "day")  # shorter lookback for shorter SMAs
        df = bars.df

        # Use shorter SMAs for more signals
        df["sma_fast"] = calculate_sma(df, 20)
        df["sma_slow"] = calculate_sma(df, 50)
        df["atr"] = calculate_atr(df, 14)

        last_price = self.get_last_price(symbol)
        pos = self.get_position(symbol)
        cash = self.get_cash()
        atr = df["atr"].iloc[-1] if not df["atr"].isnull().iloc[-1] else 1

        # Buy when fast SMA crosses above slow SMA
        buy_signal = (
            (df["sma_fast"].iloc[-1] > df["sma_slow"].iloc[-1]) and
            (df["sma_fast"].iloc[-2] <= df["sma_slow"].iloc[-2])
        )

        # Sell when fast SMA crosses below slow SMA
        sell_signal = (
            (df["sma_fast"].iloc[-1] < df["sma_slow"].iloc[-1]) and
            (df["sma_fast"].iloc[-2] >= df["sma_slow"].iloc[-2])
        )

        quantity = int(calculate_quantity(cash, last_price, risk_percent=0.9))

        # Calculate potential take profit price for buy filter
        potential_take_profit = last_price + 2 * atr
        min_profit_percent = 0.02  # Require at least 2% potential gain

        if (
            buy_signal
            and not pos
            and quantity > 0
            and ((potential_take_profit - last_price) / last_price) >= min_profit_percent
        ):
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)
            self.vars.trailing_stop_price = last_price * (1 - STOP_LOSS_PERCENT)

        elif sell_signal and pos:
            self.sell_all()
            self.vars.trailing_stop_price = None

        # ATR-based trailing stop
        elif pos:
            entry_price = getattr(pos, "avg_price", last_price)
            stop_loss_price = entry_price - 2 * atr
            take_profit_price = entry_price + 2 * atr  # <-- Take profit at 2x ATR above entry

            if last_price < stop_loss_price:
                self.sell_all()
                self.vars.trailing_stop_price = None
            elif last_price >= take_profit_price:  # <-- Take profit condition
                self.sell_all()
                self.vars.trailing_stop_price = None
            else:
                new_stop = last_price * (1 - STOP_LOSS_PERCENT)
                if new_stop > getattr(self.vars, "trailing_stop_price", 0):
                    self.vars.trailing_stop_price = new_stop
