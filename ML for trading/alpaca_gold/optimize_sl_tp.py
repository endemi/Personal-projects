from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from trend import TrendStrategy

STOP_LOSS_PERCENTS = [0.01, 0.02, 0.03, 0.05, 0.07]
TAKE_PROFIT_PERCENTS = [0.03, 0.05, 0.07, 0.1, 0.15]

results = []

for sl in STOP_LOSS_PERCENTS:
    for tp in TAKE_PROFIT_PERCENTS:
        params = {
            "symbol": "GLD",
            "quantity": None,
            "stop_loss": sl,
            "take_profit": tp
        }
        stats, _ = TrendStrategy.backtest(
            YahooDataBacktesting,
            datetime(2025, 1, 1),
            datetime(2025, 7, 4),
            benchmark_asset="GLD",
            parameters=params,
            initial_cash=2000,
            show_plot=False
        )
        results.append({
            "stop_loss": sl,
            "take_profit": tp,
            "sharpe": stats.sharpe if hasattr(stats, "sharpe") else None,
            "total_return": stats.total_return if hasattr(stats, "total_return") else None
        })

# Sort and print top results
results.sort(key=lambda x: (x["sharpe"] if x["sharpe"] is not None else 0), reverse=True)
for res in results[:5]:
    print(res)