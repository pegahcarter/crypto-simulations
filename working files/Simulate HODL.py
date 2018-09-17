import pandas as pd
import numpy as np
import random
import os
import inspect

# Retrieve location of historical prices file
filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename)) + '/backtests/'
historical_prices = pd.read_csv(path + 'historical prices.csv')

# get date ranges used for simulations
historical_cap = pd.read_csv(path + 'historical market cap.csv')
historical_cap = np.array(historical_market_cap)

start_dates = historical_cap[:len(historical_cap) - 365]
end_dates = historical_cap[365:]

# Subtract the ending market caps from each other, located in the 4th column
cap_diffs = end_dates[:, 3] - start_dates[:, 3]

diff_large_start = cap_diffs.argmax()
diff_small_start = cap_diffs.argmin()

cap_diffs = list(cap_diffs)

middle_diff = (max(cap_diffs) - min(cap_diffs)) / 2
diff_middle_start = cap_diffs.index(min(cap_diffs, key=lambda x: abs(x - middle_diff)))

# List of coins
coin_list = historical_prices.columns.tolist()[1:]

# Convert historical_prices to numpy array to improve performance
data = np.array(historical_prices[coin_list])

# Start with $5000 of Bitcoin at day 0 price
start_amt = 5000

#----------------------------------------------
# loop through different date ranges
sim_dates = [diff_small_start, diff_middle_start, diff_large_start]


for sim_date in sim_dates:

	# Make dataframe for date range
	df = data[sim_date:sim_date + 366]

	for num_coins in range(2,11,2):
		amt_each = start_amt / num_coins
		for sim_num in range(1000):

			random_list = random.sample(range(0, len(coin_list) - 1), num_coins)
			col_name = '-'.join([coin_list[i] for i in random_list])

			coin_amts = amt_each / df[0][random_list]


#----------------------------------------------

# Simulate 2, 4, 6, 8, and 10 coins
for num_to_select in range(2,11,2):
    amt_each = start_amt / num_to_select
    simulations = pd.DataFrame({'date':historical_prices['date'].tolist()})

	# Run 1000 simulations
    for x in range(1000):

		# Randomly select coins to simulate
        random_list = random.sample(range(0, len(coin_list)-1), num_to_select)
        col_name = '-'.join([coin_list[i] for i in random_list])

		# Get coin amount
        coin_amts = amt_each / data[0][random_list]

		# Record simulation
        simulations[col_name] = data[:, random_list].dot(coin_amts)

    simulations.set_index(['date'], inplace=True)
    simulations.to_csv(path + str(num_to_select) + '/' + str(num_to_select) + '_HODL.csv')
