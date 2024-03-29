"""
Brief:
    A lot of people overcomplicate things. This is the simplest version of an automated trading strategy I could
    come up with. It's mainly for informational purposes, as I've recently had classmates ask to see how these things
    work, but they're new to coding.

    The strategy could be easily calculated using excel because it's just column after column of data, initially based
    on the close price for each bar.

    The data used is minute-tick from CL (WTI Crude Oil) futures.

How it works:
    1: Data is imported.
    2: The signals are constructed.
    3: Performance is simulated (this model is simple so doesn't have slippage or transaction fees).
    4: Results are displayed.

Disclaimer:
    Trading futures comes with substantial risk.
    This app is intended for informational purposes only.
    By using any part of this code, the user accepts
    full ownership of the risks associated.
"""

import pandas as pd


def dummy_data():
    """
    Imports csv with minute tick data
    Sets datetime index.
    :return: pandas dataframe
    """
    raw = pd.read_csv("cl_minute_tick.csv")
    return raw.set_index(raw.time)


def signals(df, span_1=30, span_2=60):
    """
    signal_1 = EMA with a 30 period lookback
    signal_2 = EMA with a 60 period lookback
    signal_3 = MACD 15
    signal_4 = Signal Line
    signal_5 = MACD Histogram
    :param df: dataframe
    """
    df['delta'] = df.closePrice.pct_change()
    df['signal_1'] = df.closePrice.ewm(span=span_1, adjust=False).mean()    #In excel, these would be columns
    df['signal_2'] = df.closePrice.ewm(span=span_2, adjust=False).mean()
    df['signal_3'] = df.signal_1 - df.signal_2
    df['signal_4'] = df.signal_3.ewm(span=span_1//2, adjust=False).mean()
    df['signal_5'] = df.signal_3 - df.signal_4
    df['long_short'] = df.signal_5 > 0 # Booline Operator. True = Long, False = Short 


def p_and_l(df, starting_capital=100000):
    """Runs simulation on 100,000 as if it were fully invested at all times"""
    df['daily_returns'] = df.closePrice.pct_change()
    df['position'] = df.long_short.shift(1)
    df['daily_pnl'] = df.daily_returns * df.position.map({True: 1, False: -1})
    df['daily_portfolio_change'] = df.daily_pnl * starting_capital
    df['daily_portfolio_change'].fillna(0)
    df['p_and_l'] = df.daily_portfolio_change.cumsum() + starting_capital


if __name__ == "__main__":
    df = dummy_data()
    signals(df)
    p_and_l(df)
