from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.stream import TradingStream
import config

client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
account = dict(client.get_account())
for k,v in account.items():
    print(f"{k}: {v}")



order_details = MarketOrderRequest(
    symbol="ETHUSD",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.GTC  # <-- use GTC for crypto
)

order = client.submit_order(order_details)

trades = TradingStream(config.API_KEY, config.SECRET_KEY, paper=True)

async def trade_updates_handler(trade):
    print(f"Trade update: {trade}")


trades.subscribe_trade_updates(trade_updates_handler)
trades.run()