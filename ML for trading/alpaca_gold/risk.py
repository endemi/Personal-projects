# risk.py

def calculate_quantity(cash, price, risk_percent=0.5):
    return (cash * risk_percent) // price
