"""
Brief:
    Building off the basic_backtest model, below is what an actual research model more or less looks like.
    Keeping with the same generic signals, the code's structure is expanded from functions to a Class.
    This class ultimately will work with other classes for things like risk management and recording trades.
    For now though, just focus on how the algo works.

How it works:
    1: The class SimulatedTrading is initiated (Object created)
    2: The run() method is called, which initiates everything
    3: Data is imported in data_fetch().
    4: The signals are constructed in signal_generation().
    5: Each row (bar) of data is looped over, as if it were coming from an API live, in simulation().
    6: Logic is applied to choose whether a long, short, or flat position should be initiated.
        in first_level_logic() and scanner().
    7: If a position is open, logic controls either profit taking or controlling losses.
        This is controlled in the four functions starting with long_in_play()

Added details:
    What's below is the jumping off point. As I find the time, I'll build out the risk management class,
    the TradeBook class, and a class that calculates performance metrics. Ultimately, all of these classes,
    including the one here, will be rolled into a brute-force backtester which simulates tens of thousands
    to millions of combinations of variables. These simulations will be saved in a database so that they're
    able to be reviewed. This will guide the researcher's understand how the model performs.

    In terms of signal generation, this is always in its own Class as well. However, for simplicity and continuity
    I've included it within the model. To reiterate, these are not real signals and will lose a
    trader money. Maybe in the future I'll build out a more robust signal class but for now, just understand
    what's below is spoofed a bit so that it's easy to follow.



Disclaimer:
    Trading futures comes with substantial risk.
    This app is intended for informational purposes only.
    By using any part of this code, the user accepts
    full ownership of the risks associated.
"""

import pandas as pd
import random
from bson import ObjectId
from risk_management import RiskManager


class TradeBook:  # TODO ultimately this will be tied in to MongoDB
    def __init__(self):
        self.aum = 100000
        self.fee = 0.50  # Not many people get this treatment, but I happen to work for a guy who does. Adjust it according to YOUR trading costs.
        self.long_stop = 0.025 # Generalize these such that there's only a stop and a limit.
        self.long_limit = 0.015
        self.short_limit = 0.025
        self.long_stop = 0.015
        self.open_ticket = None
        self.trade_log = {}     # delete this when the rest of the infrastructuer is built out

    def slippage(self, price):
        slippage_percentage = random.uniform(0,
                                             0.0025)  # 0.25% max, need to measure slippage of CL in future research project
        slippage_amount = price * slippage_percentage
        return slippage_amount

    def stop_target(self, price,
                    direction):  # day one, week one risk management here people. Probalby will move this to another Class long at some point.
        high_mark = price + (price * self.long_limit)
        low_mark = price - (price * self.long_stop)
        if direction:
            return high_mark, low_mark
        else:
            return low_mark, high_mark

    def position_size(self, price):
        return self.aum // price  # Place holder Not the way to do it, needs to model with leverage. Ultimately this will be another Class w/it's own risk management.

    def new_id(self):
        self.open_ticket = ObjectId()

    def open_position(self, date_time, direction, price):
        self.new_id()
        ticket = {"_id": self.open_ticket,
                  "type": "open",
                  "datetime": date_time,
                  "direction": direction,
                  "price": price,
                 }

    def close_position(self, date_time, direction, price):
        ticket = {"type": "close",
                  "datetime": date_time,
                  "direction": direction,
                  "price": price,
                  "open_transaction": self.open_ticket
                  }
    # Open position
    # hold that ticket
    # Close position
    # Assemble BSON document
    # load to database
    def slip_generator(self, time, price, direction):
        if direction: # Go long
            paid = price + self.slippage(price)
            self.trade_log[time] = {"transaction_price": paid,
                                    "direction": direction,
                                    "contracts": self.position_size(price)}
        else: # Go Short
            paid = price - self.slippage(price)
            self.trade_log[time] = {"transaction_price": paid,
                                    "direction": direction}

    def place_order(self, time, price, direction):      # should be good to go
        high_mark, low_mark = self.stop_target(price, direction)
        self.slip_generator(time, price, direction)
        return high_mark, low_mark


def temp_risk_mgmt(price, direction):
    """
    Ultimately, this will be at least one Class.
    At a minimum, you need to calculate how many contracts to hold, and then use that to dictate stops and limits.
    Creating this will be my next project.
    :param price:
    :param direction:
    :return:
    """
    if direction:
        stop = price - (price * .025)
        limit = price + (price * .05)
        return stop, limit
    else:
        stop = price - (price * .05)
        limit = price + (price * .025)
        return limit, stop


class SimulatedTrading:

    def __init__(self, ema1, ema2, risk_mgmt, trade_book):
        self.span_1 = ema1
        self.span_2 = ema2
        self.risk_m = risk_mgmt
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
        """
        Like an ignition on the car, this is how everything starts.
        :return:
        """
        self.data_fetch()
        self.signal_generation()
        self.simulation()

    def data_fetch(self):
        """
        Imports data from a CSV
        :return:
        """
        x = pd.read_csv('CL_minute_full.csv')
        self.raw = x.set_index(x.time).tail(2500)

    def signal_generation(self):
        """
        FOR DEMONSTRATION PURPOSES ONLY, DO NOT USE IN PRODUCTION
        Real-world, these signals are all generated in their own Class because they're proprietary.
        """
        self.raw['delta'] = self.raw.closePrice.pct_change()
        self.raw['signal_1'] = self.raw.closePrice.ewm(span=self.span_1, adjust=False).mean()
        self.raw['signal_2'] = self.raw.closePrice.ewm(span=self.span_2, adjust=False).mean()
        self.raw['signal_3'] = self.raw.signal_1 - self.raw.signal_2
        self.raw['signal_4'] = self.raw.signal_3.ewm(span=self.span_1 // 2, adjust=False).mean()
        self.raw['signal_5'] = self.raw.signal_3 - self.raw.signal_4
        self.raw = self.raw.dropna()

    def open_position(self, direction):
        """
        Here the method just allows the algo to cycle. In real-world development, this is where things like
        risk management and position size are brought into the model, from outside classes. This is also where
        a method from the TradeBook class will be called to record the trade.
        :param direction: Ture = Long, False = Short
        :return:
        """
        if direction:
            self.stop = self.risk_m.manage(self.raw.index[self.bar], self.raw.closePrice.iloc[self.bar], True)

            x, self.limit = temp_risk_mgmt(self.raw.closePrice.iloc[self.bar], direction)
        else:
            self.limit = self.risk_m.manage(self.raw.index[self.bar], self.raw.closePrice.iloc[self.bar], False)
            x, self.stop = temp_risk_mgmt(self.raw.closePrice.iloc[self.bar], direction)
        print("Open Position")

    def close_position(self):
        """
        Will close send the close price to the TradeBook and
        :return:
        """
        print("Close Position")

    def long_in_play(self):
        """
        Logic that controls an open, long position
        :return:
        """
        if self.price_now > self.limit:
            print("Close long, limit")
            self.close_position()
            self.wait_short = True
            self.open_long = False

        elif self.price_now < self.stop:
            print("Close Position, stop")
            self.close_position()
            self.wait_short = True
            self.open_long = False

    def short_in_play(self):
        """
        Logic that controls an open, short position
        :return:
        """
        if self.price_now > self.stop:
            print("Close short, stop")
            self.close_position()
            self.wait_long = True
            self.open_short = False

        elif self.price_now < self.limit:
            print("Close short, limit")
            self.close_position()
            self.wait_long = True
            self.open_short = False

    def long_search(self):
        """
        Logic that controls taking a long position
        :return:
        """
        if self.raw.signal_4.iloc[self.bar] > self.raw.signal_5.iloc[self.bar]:
            print("open long")
            self.open_position(True)
            self.open_long = True
            self.wait_long = False

    def short_search(self):
        """
        Logic that controls taking a short position
        :return:
        """
        if self.raw.signal_4.iloc[self.bar] < self.raw.signal_5.iloc[self.bar]:
            print("open short")
            self.open_position(False)
            self.open_short = True
            self.wait_short = False

    def new_cycle(self):
        """
        First clause, used on startup only.
        :return:
        """
        if self.raw.signal_4.iloc[self.bar] > self.raw.signal_5.iloc[self.bar]:
            print("first open Long")
            self.open_position(True)
            self.open_long = True

        elif self.raw.signal_4.iloc[self.bar] < self.raw.signal_5.iloc[self.bar]:
            print("first open Short")
            self.open_position(False)
            self.open_short = True

    def scanner(self):
        """
        Logic that controls what direction trade the algo is looking for.
        For instance, when it finishes a long position, it begins to look for a short position.
        If no position has been taken yet, it calls the bottom clause.
        :return:
        """
        if self.wait_long:
            self.long_search()  # look for long signal

        elif self.wait_short:
            self.short_search()  # look for short signal

        else:
            self.new_cycle()  # look for breakout

    def first_level_logic(self):
        """
        Checks to see if a position needs to be closed
        or calls next method which looks to see if a position needs to be open.
        :return:
        """
        if self.open_long:
            self.long_in_play()

        elif self.open_short:
            self.short_in_play()

        else:
            self.scanner()

    def simulation(self):
        """
        Cycles through dataframe
        :return:
        """
        for i in range(len(self.raw)):
            self.bar = i
            self.price_now = self.raw.closePrice.iloc[i]
            self.first_level_logic()


rm = RiskManager()
ts = SimulatedTrading(30, 60, rm, None)
ts.run()

