import pandas as pd
import pprint


def neg_std(df):
    x = df[df['pl_delta'] < 0]
    return x.pl_delta.std()


def pos_std(df):
    x = df[df['pl_delta'] > 0]
    return x.pl_delta.std()


def nav(df, aum):
    df['nav'] = aum + df.pl.cumsum()
    df['pl_delta'] = df.nav.pct_change() * 100
    df.loc[0, 'pl_delta'] = ((df.loc[0, 'nav'] - aum) / aum) * 100


def run_results(data, aum=1000):
    df = pd.DataFrame(data)
    nav(df, aum)
    results = {
        "startingNaV": aum,
        "endingNaV": df.nav.iloc[-1],
        "pl": ((df.nav.iloc[-1] - aum) / aum) * 100,
        "averageReturn": df.pl_delta.mean(),
        "returnStDev": df.pl_delta.std(),
        "avgPosMonthlyReturns": None,
        "avgNegMonthlyReturns": None,
        "posStdev": pos_std(df),
        "negStdev": neg_std(df),
        "shoreRatio": pos_std(df) / neg_std(df),
        "skew": df.pl_delta.skew(),
        "kurtosis": df.pl_delta.kurtosis(),
        "sortin": None,
        "sharpe": None,
        "treynor": None,
        "calmar": None,
        "goesNeg": None,
        "maxDrawDown": None,
        "tenDrawDowns": {},
        "timeToRecovery": {},
        "bestPeriods": {},
    }
    pprint.pprint(results, sort_dicts=False)


# Performance Details
#   - Starting NaV
#   - Ending NaV
#   - PL
#   - Average Return
#   - Stdev of returns
#   - Avg Positive Monthly returns
#   - Avg Negative Monthly returns
#   - Pos stdev
#   - Neg stdev
#   - Shore Ratio
#   - Skew
#   - Kurtosis
#   - Sortin Ratio
#   - Sharpe Ratio
#   - Treynor Ratio
#   - Calmar Ratio
#   - Goes Negative (True/False)
#   - Max Drawdown
#       • top 10
#   - Time to recovery
#       • top 10
#   - Best Period
#       • top 10
#   - Time of best periods
#       • top 10
