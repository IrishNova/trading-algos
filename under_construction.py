"""
__ ** This model is under construction, anything and everything may still change** __

Building off the basic_backtest model, this is what it looks like for researching.

"""

import pandas as pd
import random


class SimulatedTrading:

    def __init__(self, ema1, ema2, trade_book):
        self.span_1 = ema1
        self.span_2 = ema2
        self.tb = trade_book
        self.raw = None
        self.price_now = None
        self.bar = None
        self.stop = None
        self.limit = None
        self.open_long = False
        self.open_short = False
        self.wait_long = False
        self.wait_short = False

    def run(self):
        self.data_fetch()
        self.signal_generation()
        self.simulation()

    def data_fetch(self):
        x = pd.read_csv('/Users/ryanmoloney/Desktop/Furvus_Research/PortfolioProject/CL_minute_full.csv')
        self.raw = x.set_index(x.time).tail(2500)

    def signal_generation(self):
        """Real-world, these signals are all generated in their own Class because they're proprietary. 
        You're thick if you try to make money with the ones here."""
        self.raw['delta'] = self.raw.closePrice.pct_change()
        self.raw['signal_1'] = self.raw.closePrice.ewm(span=self.span_1, adjust=False).mean()
        self.raw['signal_2'] = self.raw.closePrice.ewm(span=self.span_2, adjust=False).mean()
        self.raw['signal_3'] = self.raw.signal_1 - self.raw.signal_2
        self.raw['signal_4'] = self.raw.signal_3.ewm(span=self.span_1 // 2, adjust=False).mean()
        self.raw['signal_5'] = self.raw.signal_3 - self.raw.signal_4
        self.raw = self.raw.dropna()

    def open_position(self, direction):
        print(self.bar)
        # calculate position size
        # set risk management (stops & limits)
        # generate ticket 

    def long_in_play(self):
        if self.price_now > self.limit:
            print("Close long, limit")
            self.wait_short = True
            self.open_long = False
        elif self.price_now < self.stop:
            print("Close Position, stop")
            self.wait_short = True
            self.open_long = False

    def short_in_play(self):
        # print("short on triggered")
        if self.price_now > self.stop:
            print("Close short, stop")
            self.wait_long = True
            self.open_short = False
        elif self.price_now < self.limit:
            print("Close short, limit")
            self.wait_long = True
            self.open_short = False

    def long_search(self):
        if self.raw.signal_4.iloc[self.bar] > self.raw.signal_5.iloc[self.bar]:
            print("open long")
            self.open_long = True
            self.wait_long = False
            self.limit, self.stop = trade_bk.place_order(self.raw.index[self.bar],
                                                         self.raw.closePrice.iloc[self.bar],
                                                         True)

    def short_search(self):
        if self.raw.signal_4.iloc[self.bar] < self.raw.signal_5.iloc[self.bar]:
            print("open short")
            self.open_short = True
            self.wait_short = False
            self.limit, self.stop = trade_bk.place_order(self.raw.index[self.bar],
                                                         self.raw.closePrice.iloc[self.bar],
                                                         False)

    def new_cycle(self):
        # Not ideal to have this and the above methods almost identical, but is the juice worth the squeeze on a
        # research algo?
        if self.raw.signal_4.iloc[self.bar] > self.raw.signal_5.iloc[self.bar]:
            print("first open Long")
            self.open_long = True
            self.limit, self.stop = trade_bk.place_order(self.raw.index[self.bar],
                                                         self.raw.closePrice.iloc[self.bar],
                                                         True)
        elif self.raw.signal_4.iloc[self.bar] < self.raw.signal_5.iloc[self.bar]:
            print("first open Short")
            self.open_short = True
            self.limit, self.stop = trade_bk.place_order(self.raw.index[self.bar],
                                                         self.raw.closePrice.iloc[self.bar],
                                                         False)

    def scanner(self):
        if self.wait_long:
            self.long_search()  # look for long signal

        elif self.wait_short:
            self.short_search()  # look for short signal

        else:
            self.new_cycle()  # look for breakout

    def first_level_logic(self):
        if self.open_long:
            self.long_in_play()

        elif self.open_short:
            self.short_in_play()

        else:
            self.scanner()

    def simulation(self):
        for i in range(len(self.raw)):
            self.bar = i
            self.price_now = self.raw.closePrice.iloc[i]
            self.first_level_logic()
