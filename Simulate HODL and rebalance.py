import ccxt
import pandas as pd
import numpy as np
import random
from Portfolio import hist_prices, Portfolio
from functions import hodl, rebalance


# Set the threshold of weight difference to trigger a trade
thresh = 0.05
avg_weight = .2
weighted_thresh = np.float32(avg_weight * thresh)

hist_prices = pd.read_csv('data/historical/prices.csv')
coins = hist_prices.columns.tolist()[1:]

# Limit dataframe dates to the date range
sim_dates = hist_prices['timestamp']

# create hodl.csv
hodl_df = hodl(hist_prices)

# Intervals for rebalancing
intervals = {1:'hourly', 24:'daily', 24*30:'monthly'}

for interval in intervals:

	hr_totals = []
	sims = pd.DataFrame(sim_dates, columns=['timestamp'])

	# Use the same random coin portfolios that we selected for hodl simulations
	for col in hodl_df.columns:

		coin_list = col.split('-')

		myPortfolio = Portfolio(coin_list)

		for hr in range(1, len(hist_prices), interval):
			if num_day % trade_interval == 0:
				myPortfolio = rebalance(myPorfolio, hr)

			hr_totals.append(np.dot(myPortfolio.daily_prices[hr], myPortfolio.quantities))

		sims[col] = hr_totals

	sims.to_csv('data/simulations/' + trade_intervals[interval] + '.csv')
