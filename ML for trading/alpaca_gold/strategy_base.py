# strategy_base.py

from lumibot.strategies import Strategy

class BaseStrategy(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
