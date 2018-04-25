from enum import Enum


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class Order:
    def __init__(self, order_type, transaction_currency, counter_currency, timestamp, value, unit_price,
                 transaction_cost_percent):
        self.order_type = order_type
        self.transaction_currency = transaction_currency
        self.counter_currency = counter_currency
        self.timestamp = timestamp
        self.value = value
        self.unit_price = unit_price
        self.transaction_cost_percent = transaction_cost_percent

    def execute(self):
        if self.order_type == OrderType.BUY:
            return (self.value * (1 - self.transaction_cost_percent)) / self.unit_price, -self.value
        elif self.order_type == OrderType.SELL:
            return -self.value, (self.value * self.unit_price) * (1 - self.transaction_cost_percent)
