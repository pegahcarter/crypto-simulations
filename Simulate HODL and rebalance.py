import ccxt
import pandas as pd
import numpy as np
import random
from Portfolio import Portfolio, hist_prices, coins
from functions import hodl, rebalance
# %load_ext line_profiler

# Limit dataframe dates to the date range
sim_dates = hist_prices['timestamp']

# create hodl.csv
hodl()
hodl_df = pd.read_csv('data/simulations/hodl.csv')

# Intervals for rebalancing
intervals = {1:'hourly', 24:'daily', 24*30:'monthly'}

#for interval in intervals.keys():

interval = 24
sims = pd.DataFrame(sim_dates, columns=['timestamp'])

# Use the same random coin portfolios that we selected for hodl simulations
# for col in hodl_df.drop('timestamp', axis=1).columns:

col = hodl_df.columns[2]
coin_list = col.split('-')
myPortfolio = Portfolio(coin_list)
hist_prices_small = np.array(hist_prices[coins])
hr_totals = [5000]

for hr in range(1, len(hist_prices)):
	current_prices = hist_prices_small[hr]
	if hr % interval == 0:
		myPortfolio = rebalance(myPortfolio, hr)

	# hr_totals.append(np.dot(myPortfolio.daily_prices[hr], myPortfolio.quantities))
	hr_totals.append(myPortfolio.total_dollar_value(hr))

sims[col] = hr_totals

sims.to_csv('data/simulations/' + intervals[interval] + '.csv')
