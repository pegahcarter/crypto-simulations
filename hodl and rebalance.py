import ccxt
import pandas as pd
import numpy as np
import random
from Portfolio import Portfolio, hist_prices
from functions import hodl, rebalance

# create hodl.csv
hodl()
hodl_df = pd.read_csv('data/simulations/hodl.csv')

# Intervals for rebalancing
intervals = {
	1:'hourly',
	24:'daily',
	24*7:'weekly',
	24*30:'monthly'
}

for interval in intervals.keys():

	sims = pd.DataFrame(index=hodl_df['timestamp'])

	# Use the same random coin portfolios that we selected for hodl simulations
	for col in hodl_df.drop('timestamp', axis=1).columns:

		coins = col.split('-')
		myPortfolio = Portfolio(coins)
		hist_prices_small = np.array(hist_prices[coins])
		hr_totals = [5000]

		for hr in range(1, len(hist_prices)):

			current_prices = hist_prices_small[hr]
			if hr % interval == 0:
				myPortfolio = rebalance(myPortfolio, current_prices)
			hr_totals.append(np.dot(current_prices, myPortfolio.quantities))

		sims[col] = hr_totals

	sims.to_csv('data/simulations/' + intervals[interval] + '.csv')
