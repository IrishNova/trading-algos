"""
__ ** This model is under construction, anything and everything may still change** __

Building off the basic_backtest model, this is what it looks like for researching. 

"""

import pandas as pd
import random


class TradeBook:    # TODO ultimately this will be tied in to MongoDB
    def __init__(self):
        self.aum = 100000
        self.fee = 0.50    # Not many people get this treatment, but I happen to work for a guy who does. Adjust it according to YOUR trading costs. 
        self.long_stop = 0.025
        self.long_limit = 0.015
        self.short_limit = 0.025
        self.long_stop = 0.015
        self.trade_log = {}

    def slippage(self, price):
        slippage_percentage = random.uniform(0, 0.0025)  # 0.25% max, need to measure slippage of CL in future research project
        slippage_amount = price * slippage_percentage
        return slippage_amount

    def stop_target(self, price, direction):    # day one, week one risk management here people. Probalby will move this to another Class long at some point.
        high_mark = price + (price * self.long_limit)
        low_mark = price - (price * self.long_stop)
        if direction:
            return high_mark, low_mark
        else:
            return low_mark, high_mark

    def position_size(self, price):
        return self.aum // price    # Place holder Not the way to do it, needs to model with leverage. Ultimately this will be another Class w/it's own risk management. 

    def slip_generator(self, time, price, direction):
        if direction:
            paid = price + self.slippage(price)
            self.trade_log[time] = {"transaction_price": paid,
                                    "direction": direction,
                                    "contracts": self.position_size(price)}
        else:
            paid = price - self.slippage(price)
            self.trade_log[time] = {"transaction_price": paid,
                                    "direction": direction}     

    def place_order(self, time, price, direction):
        high_mark, low_mark = self.stop_target(price, direction)
        self.slip_generator(time, price, direction)
        return high_mark, low_mark


class SimulatedTrading:

    def __init__(self, ema1, ema2):
        self.span_1 = ema1
        self.span_2 = ema2
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
        x = pd.read_csv('CL_minute_full.csv')
        self.raw = x.set_index(x.time).tail(2500)

    def signal_generation(self):    # real-world, these signals are all generated in their own Class becuase they're propritary. You're thick if you try to make mone with the ones here. 
        self.raw['delta'] = self.raw.closePrice.pct_change()
        self.raw['signal_1'] = self.raw.closePrice.ewm(span=self.span_1, adjust=False).mean()
        self.raw['signal_2'] = self.raw.closePrice.ewm(span=self.span_2, adjust=False).mean()
        self.raw['signal_3'] = self.raw.signal_1 - self.raw.signal_2
        self.raw['signal_4'] = self.raw.signal_3.ewm(span=self.span_1 // 2, adjust=False).mean()
        self.raw['signal_5'] = self.raw.signal_3 - self.raw.signal_4
        self.raw = self.raw.dropna()

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
            self.limit = self.price_now + (
                    self.price_now * 0.005)  # TODO make these returned from trade ticket class
            self.stop = self.price_now - (self.price_now * 0.005)

    def short_search(self):
        if self.raw.signal_4.iloc[self.bar] < self.raw.signal_5.iloc[self.bar]:
            print("open short")
            self.open_short = True
            self.wait_short = False
            self.limit = self.price_now - (
                    self.price_now * 0.005)  # TODO make these returned from trade ticket class
            self.stop = self.price_now + (self.price_now * 0.005)

    def new_cycle(self):    # Not ideal to have this and the above methods almost identical, but is the juice worth the squeeze on a research algo? 
        if self.raw.signal_4.iloc[self.bar] > self.raw.signal_5.iloc[self.bar]:
            print("first open Long")
            self.open_long = True
            self.limit = self.price_now + (
                    self.price_now * 0.005)  # TODO make these returned from trade ticket class
            self.stop = self.price_now - (self.price_now * 0.005)
        elif self.raw.signal_4.iloc[self.bar] < self.raw.signal_5.iloc[self.bar]:
            print("fisrs open Short")
            self.open_short = True
            self.limit = self.price_now - (
                    self.price_now * 0.005)  # TODO make these returned from trade ticket class
            self.stop = self.price_now + (self.price_now * 0.005)

    def scanner(self):
        if self.wait_long:
            self.long_search()      # look for long signal

        elif self.wait_short:
            self.short_search()     # look for short signal

        else:
            self.new_cycle()    # look for breakout

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


ts = SimulatedTrading(30, 60)
ts.run()
