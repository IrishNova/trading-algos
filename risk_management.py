"""
Dynamically generates stop and limits based on market conditions.

Still a helluva lot of work to do. 

This is simply a jumping off point showing how someone could meld a sort of AI and price
action into developing a view of risk. 

How it works: (in theory)
  1: Slices the the 20 days from current date.
  2: Searches for similar periods.
  3: Takes the last date of each similar period
  4: Slices the dataframe from that date 30 periods forward
  5: (TBD) Looks at the metrics of those periods against the larger dataset.
  6: (TBD) Uses this to set stops... more vol, looser. Less vol, tighter.
  7: (TBD) Calculates how many ticks to allow & returns a stop-loss or limit price.

Disclaimer:
    Trading futures comes with substantial risk.
    This app is intended for informational purposes only.
    By using any part of this code, the user accepts
    full ownership of the risks associated.
"""


import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

from datetime import datetime   #TODO delete this with the rest of the dummy code


class RiskManager:

    def __init__(self):
        self.df = None
        self.dx = None
        self.closest_date = None
        self.working = None
        self.sim_x = None
        self.ad = None
        self.load_data()

    def load_data(self):
        self.df = pd.read_csv('vix_daily_data.csv', index_col='Date', parse_dates=True)
        self.df['delta'] = self.df.Close.pct_change()
        self.df = self.df.dropna()

    def date_match(self, d):
        if d in self.df.index:
            self.closest_date = d
        else:
            self.closest_date = self.df.index[self.df.index < d][-1]

    def slice_data(self):
        self.dx = self.df.loc[:self.closest_date].copy()
        self.working = self.dx.tail(20)

    def finder(self, n_clusters=5):
        rolling_windows = self.dx['delta'].rolling(window=20)
        feature_vectors = np.array([window for window in rolling_windows if len(window) == 20])
        if len(feature_vectors) > 0:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            kmeans.fit(feature_vectors)

            working_features = np.array(self.working['delta']).reshape(1, -1)
            working_cluster = kmeans.predict(working_features)

            self.sim_x = np.where(kmeans.labels_ == working_cluster[0])[0]

    def forward(self):
        window_offset = 20 - 1
        self.ad = [self.dx.index[i + window_offset] for i in self.sim_x]

    def individual_vol(self):
        for x in self.ad:
            y = self.dx.loc[x:].head(30)
            print(y)

    def manage(self, d):
        self.date_match(d)
        self.slice_data()
        self.finder()
        self.forward()
        self.individual_vol()


temp_dates = [datetime(2018, 11, 22, 11, 26),
              datetime(2019, 9, 15, 14, 26),
              datetime(2020, 8, 6, 14, 26),
              datetime(2021, 7, 16, 14, 26),
              datetime(2022, 12, 28, 14, 26),
              datetime(2023, 12, 28, 14, 26)
              ]

rm = RiskManager()
for dx in temp_dates:
    rm.manage(dx)
    print("-----"*25)

