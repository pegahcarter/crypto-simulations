import pandas as pd
import numpy as np
import random
import os
import inspect

# Retrieve location of historical prices file
filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename)) + '/backtests/'
historical_prices = pd.read_csv(path + 'historical prices.csv')
sim_dates = list(historical_prices['date'])
coins = historical_prices.columns.tolist()[1:]

# get date ranges used for simulations
historical_cap = pd.read_csv(path + 'historical market cap.csv')
historical_cap = np.array(historical_cap)

start_dates = historical_cap[:len(historical_cap) - 365]
end_dates = historical_cap[365:]

# Subtract the ending market caps from each other, located in the 4th column
cap_diffs = list(end_dates[:, 3] - start_dates[:, 3])

# Make sure there's an odd number of dates, so the median value can be indexed
if len(cap_diffs) % 2 == 0:
	cap_diffs.pop(len(cap_diffs)-1)

# Start date for simulations
start_date = cap_diffs.index(np.median(cap_diffs))

# Limit dataframe dates to the date range
data = np.array(historical_prices[coins])
data = data[start_date:start_date + 365]
sim_dates = sim_dates[start_date:start_date + 365]

# Start with $5000 of Bitcoin at day 0 price
start_amt = 5000

# Simulate 2, 4, 6, 8, and 10 coins
for num_coins in range(2,11,2):
	amt_each = start_amt / num_coins
	simulations = pd.DataFrame(index=sim_dates)

	for sim_num in range(1000):
		random_list = random.sample(range(len(coins)-1), num_coins)
		coin_amts = amt_each / data[0, random_list]

		col = '-'.join([coins[i] for i in random_list])

		simulations[col] = data[:, random_list].dot(coin_amts)

	simulations.to_csv(path + str(num_coins) + '/' + str(num_coins) + '_HODL.csv')
