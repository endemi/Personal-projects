from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.stream import TradingStream
import config

# Initialize the Alpaca trading client
client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
account = dict(client.get_account())


#order_details = MarketOrderRequest(
order_details = MarketOrderRequest(
    symbol="ETHUSD",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.GTC  # <-- use GTC for crypto
)

#Function to place a buy order
def buy_order():
    order = client.submit_order(order_details)

    trades = TradingStream(config.API_KEY, config.SECRET_KEY, paper=True)

    async def trade_updates_handler(trade):
        print(f"Trade update: {trade}")


    trades.subscribe_trade_updates(trade_updates_handler)
    trades.run()


#Function to place a sell order
def cancel_all_order(order_id):
    client.close_all_positions(cancel_orders=True)


#check positions and print them
assets = [asset for asset in client.get_all_positions()]
positions = [(asset.symbol, asset.qty, asset.current_price) for asset in assets]
print("Postions")
print(f"{'Symbol':9}{'Qty':>4}{'Value':>15}")
print("-" * 28)
for position in positions:
    print(f"{position[0]:9}{position[1]:>4}{float(position[1]) * float(position[2]):>15.2f}")
