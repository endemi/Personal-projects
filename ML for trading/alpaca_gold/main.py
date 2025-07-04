# main.py

from datetime import datetime
from lumibot.credentials import IS_BACKTESTING
from lumibot.traders import Trader
from lumibot.backtesting import YahooDataBacktesting
from trend import TrendStrategy

if __name__ == "__main__":
    if not IS_BACKTESTING:
        strategy = TrendStrategy()
        bot = Trader()
        bot.add_strategy(strategy)
        bot.run_all()
    else:
        start = datetime(2024, 1, 1)
        end = datetime(2025, 4, 7)
        TrendStrategy.backtest(
            YahooDataBacktesting,
            start,
            end,
            benchmark_asset="GLD"
        )
