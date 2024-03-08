"""
Dynamically generates stop and limits based on market conditions.

Needs annotatations and to be refactored a bit, but this is how a person could use machine learning
to look for similar patterns of volatility to set stop/limits. I also have to set it up to accept 
a price and direction. We're about 95% there though. 

This is simply a jumping off point showing how someone could meld a sort of AI and price
action into developing a view of risk. 

How it works: (in theory)
  1: Slices the the 20 days from current date.
  2: Searches for similar periods.
  3: Takes the last date of each similar period
  4: Slices the dataframe from that date 30 periods forward
  5: Looks at the metrics of those periods against the larger dataset.
  6: Uses this to set stops... more vol, looser. Less vol, tighter.
  7: Calculates how many ticks to allow & returns a stop-loss or limit price.

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

class PatternRecognition:
    """
    Searches historical data to find timeframes with the most similar pattern to
    the past 20 days of data.
    """
    def __init__(self, w, data):
        self.working = w
        self.dx = data
        self.model = None
        self.sim_x = None
        self.start_index = None
        self.fd = None
        self.sorted_indices = None
        self.data_view = []
        self.operator()

    def operator(self):
        self.pattern_generator()
        self.individual_vol()
        self.ten_closest_matches()
        self.end_dates()
        self.next_periods()
        return self.data_view

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
        self.sorted_indices = np.argsort(flat_distances)[:self.dx.shape[0] * self.model.cluster_centers_.shape[0]]

    def ten_closest_matches(self):
        unique_closest_points = []
        seen = set()

        # Iterate over sorted indices to pick unique entries until you fill your quota of 10 unique points
        for idx in self.sorted_indices:
            data_idx = idx // self.model.cluster_centers_.shape[0]  # Convert flat index back to data index
            if data_idx not in seen:
                seen.add(data_idx)
                unique_closest_points.append(data_idx)
            if len(seen) >= 10:
                break

        self.start_index = self.dx.iloc[unique_closest_points]

    def end_dates(self):
        future_dates_list = []

        # Iterate over each date in the self.start_index DataFrame
        for date in self.start_index.index:
            # Check if the date exists in self.dx
            if date in self.dx.index:
                # Get the position of this date in self.dx
                current_pos = self.dx.index.get_loc(date)

                # Calculate the position of the date 20 rows down
                future_pos = current_pos + 20

                # Check if the future position is within the bounds of self.dx
                if future_pos < len(self.dx):
                    # If within bounds, get the future date
                    future_date = self.dx.index[future_pos]
                    # Append the future date to the list
                    future_dates_list.append(future_date)

        # Create a new DataFrame with the rows corresponding to the future dates
        self.fd = self.dx.loc[future_dates_list]

    def next_periods(self):
        # Iterate over each date in self.fd
        for date in self.fd.index:
            # Ensure the date is within self.dx
            if date in self.dx.index:
                # Get the position of this date in self.dx
                start_pos = self.dx.index.get_loc(date)

                # Create a slice of self.dx starting from this position
                # Note: Adjust the slicing as per your requirement.
                # Here, it's assumed you want to include all data from the start_pos to the end of self.dx.
                df_slice = self.dx.iloc[start_pos:]

                # Append the slice to the list
                self.data_view.append(df_slice)


class MetricCalc:

    def __init__(self, periods, data, price, direction):
        self.filtered = periods
        self.dy = data
        self.price = price
        self.direction = direction
        self.model_skew = None
        self.model_kurtosis = None
        self.high_skew = False
        self.high_kurtosis = False
        self.price = None

    def operator_results(self):
        self.raw_stats()
        self.logic_one()
        return self.price

    def raw_stats(self):
        skew = []
        kurtosis = []

        for d in self.filtered:
            skew.append(d.delta.skew())
            kurtosis.append(d.delta.kurtosis())

        self.model_skew = np.mean(skew)
        self.model_kurtosis = np.mean(kurtosis)

    def logic_one(self):
        if self.model_skew > self.dy.delta.skew():
            self.high_skew = True

        if self.model_kurtosis > self.dy.delta.kurtosis():
            self.high_kurtosis = True

    def logic_two(self):
        if self.high_skew and self.high_kurtosis:
            if self.direction:
                self.price -= 0.50
            else:
                self.price += 0.50
        else:
            if self.direction:
                self.price -= 0.25
            else:
                self.price += 0.25


class RiskManager:

    def __init__(self):
        self.df = None
        self.dx = None
        self.closest_date = None
        self.working = None
        self.load_data()

    def load_data(self):
        self.df = pd.read_csv('vix_daily_data.csv', index_col='Date', parse_dates=True)
        self.df['d'] = self.df.Close.pct_change()
        self.df['delta'] = np.log1p(self.df['d'])
        self.df = self.df.dropna()

    def date_match(self, d):
        if d in self.df.index:
            self.closest_date = d
        else:
            self.closest_date = self.df.index[self.df.index < d][-1]

    def slice_data(self):
        self.dx = self.df.loc[:self.closest_date].copy() # data for each simulation
        self.working = self.dx.tail(20) # base data for clusters. Each cluster should look like this

    def manage(self, d):
        self.date_match(d)
        self.slice_data()
        return MetricCalc(
            PatternRecognition(self.working, self.dx).operator(),
            self.dx,
            85.50,
            True
            ).operator_results()
