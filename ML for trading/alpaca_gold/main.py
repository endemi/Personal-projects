# main.py

from datetime import datetime
from lumibot.traders import Trader
from lumibot.credentials import IS_BACKTESTING
from lumibot.backtesting import YahooDataBacktesting
from trend import MaximizedTrendStrategy
from config import SYMBOL

if __name__ == "__main__":
    if not IS_BACKTESTING:
        bot = Trader()
        bot.add_strategy(MaximizedTrendStrategy)
        bot.run_all()
    else:
        start = datetime(2023, 1, 1)
        end = datetime(2024, 11, 24)
        MaximizedTrendStrategy.backtest(
            YahooDataBacktesting,
            start,
            end,
            benchmark_asset=SYMBOL
        )
