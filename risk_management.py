"""
Dynamically generates stop and limits based on market conditions.

Still a helluva lot of work to do. There's a major error because the clusters are being found from the 
full dataset, not the subset starting with the 'current' date. 

These things take time, I'll continue to work on it so check back. For now, this is where it's at. 

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
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.clustering import TimeSeriesKMeans

from datetime import datetime   #TODO delete this with the rest of the dummy code


class RiskManager:

    def __init__(self):
        self.df = None
        self.dx = None
        self.closest_date = None
        self.working = None
        self.sim_x = None
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
        self.dx = self.df.loc[:self.closest_date].tail(20)  # Gets last 20 days up to closest_date

    def finder(self, n_clusters=5):
        # Ensure data is in correct shape (n_samples, n_timestamps, n_features)
        # Here, each "sample" is a day, and we reshape it accordingly
        data_scaled = self.dx.values.reshape(1, self.dx.shape[0], self.dx.shape[1])
        scaler = TimeSeriesScalerMeanVariance(mu=0., std=1.)
        data_scaled = scaler.fit_transform(data_scaled)

        model = TimeSeriesKMeans(n_clusters=n_clusters, metric="dtw", verbose=True)
        self.sim_x = model.fit_predict(data_scaled.reshape(self.dx.shape))  # Fit model

    def individual_vol(self):
        cluster_labels = np.unique(self.sim_x)  # Get unique cluster labels

        for label in cluster_labels:
            # Find indices of days belonging to the current cluster
            indices = np.where(self.sim_x == label)[0]

            if indices.size > 0:
                last_day_index = indices[-1]  # Last day of the cluster in 'self.dx'
                last_date = self.dx.index[last_day_index]  # Get the actual date

                # Now find this date in 'self.df' to get the next 30 days
                all_dates = self.df.index
                target_idx = all_dates.get_loc(last_date) + 1  # Get next day's index in 'self.df'

                if target_idx < len(all_dates) - 30:  # Check if there are at least 30 days ahead
                    forward_30 = self.df.iloc[target_idx:target_idx + 30]  # Get next 30 days
                    print(forward_30)  # Print the forward 30 days data

    def manage(self, d):
        self.date_match(d)
        self.slice_data()
        self.finder()
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
    print("-----" * 25)
    print("-----" * 25)
    print("-----" * 25)
    print("-----" * 25)
    print("-----" * 25)
