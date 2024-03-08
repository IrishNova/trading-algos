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
from tslearn.metrics import dtw
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.clustering import TimeSeriesKMeans

from datetime import datetime   #TODO delete this with the rest of the dummy code


class RiskManager:

    def __init__(self):
        self.cluster_indexes = None
        self.start_index = None
        self.model = None
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
        self.dx = self.df.loc[:self.closest_date].copy() # data for each simulation
        self.working = self.dx.tail(20) # base data for clusters. Each cluster should look like this

    def pattern_generator(self, n_clusters=5):
        """Identifies pattern of the self.working slice"""
        data = self.working.values.reshape(self.working.shape[0], -1)
        scaler = TimeSeriesScalerMeanVariance(mu=0., std=1.)
        data_scaled = scaler.fit_transform(data)
        self.model = TimeSeriesKMeans(n_clusters=n_clusters, metric="dtw", verbose=True)
        self.sim_x = self.model.fit_predict(data_scaled)

    def individual_vol(self):
        # Ensure data is appropriately scaled, as done before clustering
        scaler = TimeSeriesScalerMeanVariance(mu=0., std=1.)
        dx_scaled = scaler.fit_transform(self.dx.values.reshape(self.dx.shape[0], -1))

        # Calculate DTW distance from each point in dx to each cluster centroid
        dtw_distances = np.zeros((self.dx.shape[0], self.model.cluster_centers_.shape[0]))

        for i in range(self.dx.shape[0]):
            for j, centroid in enumerate(self.model.cluster_centers_):
                # Calculate DTW distance and store it
                dtw_distances[i, j] = dtw(dx_scaled[i], centroid)

        # Instead of finding 10 closest points per cluster, find unique closest points across all clusters
        flat_distances = dtw_distances.flatten()
        sorted_indices = np.argsort(flat_distances)[:self.dx.shape[0] * self.model.cluster_centers_.shape[0]]

        unique_closest_points = []
        seen = set()

        # Iterate over sorted indices to pick unique entries until you fill your quota of 10 unique points
        for idx in sorted_indices:
            data_idx = idx // self.model.cluster_centers_.shape[0]  # Convert flat index back to data index
            if data_idx not in seen:
                seen.add(data_idx)
                unique_closest_points.append(data_idx)
            if len(seen) >= 10:
                break

        self.start_index = self.dx.iloc[unique_closest_points]

    def end_dates(self):
        print("hello world")

    def manage(self, d):
            self.date_match(d)
            self.slice_data()
            self.pattern_generator()
            self.individual_vol()
            self.end_dates()


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
    print("--------"*25)
    print("--------" * 25)
    print("-----" * 25)
    print("-----" * 25)
    print("-----" * 25)
    print("-----" * 25)
    print("-----" * 25)
