"""
Logs trades into a MongoDB collection (TBD).

Disclaimer:
    Trading futures comes with substantial risk.
    This app is intended for informational purposes only.
    By using any part of this code, the user accepts
    full ownership of the risks associated.
"""

from pymongo import MongoClient
from result_calculator import run_results

class TradeBook:

    def __init__(self, initial: dict):
        self.setup_details = initial
        self.trade_tickets = []
        self.open_ticket = False
        self.holder = None

    def final_ticket(self, details):
        if details['direction']:
            price = details['price'] - self.holder['price']
            direction = True
        else:
            price = self.holder['price'] - details['price']
            direction = False

        self.trade_tickets.append(
            {"openPrice": self.holder['price'],
             "closePrice": details['price'],
             "pl": price,
             "openTime": self.holder['tradeTime'],
             "closeTime": details['tradeTime'],
             "direction": direction}
        )

    def log_trade(self, details):
        if self.open_ticket:
            self.final_ticket(details)
            self.open_ticket = False
        else:
            self.holder = details
            self.open_ticket = True

