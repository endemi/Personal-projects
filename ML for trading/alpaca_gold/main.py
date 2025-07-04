# main.py

from datetime import datetime
from lumibot.traders import Trader
from lumibot.credentials import IS_BACKTESTING
from lumibot.backtesting import YahooDataBacktesting
from trend import SimpleETFStrategy
from config import SYMBOL

if __name__ == "__main__":
    if not IS_BACKTESTING:
        bot = Trader()
        bot.add_strategy(SimpleETFStrategy)
        bot.run_all()
    else:
        start = datetime(2023, 1, 1)
        end = datetime(2025, 7, 4)
        SimpleETFStrategy.backtest(
            YahooDataBacktesting,
            start,
            end,
            benchmark_asset=SYMBOL
        )
