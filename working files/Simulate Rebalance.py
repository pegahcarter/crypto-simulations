import pandas as pd
import numpy as np
import random
import ccxt
import os
import time
import inspect

# Retrieve all current tickers on exchange
exchange = ccxt.bittrex()
tickers = set()
[tickers.add(ticker) for ticker in exchange.fetch_tickers()]

# Retrieve historical price data
filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename)) + '/backtests/'
data = pd.read_csv(path + 'historical prices.csv')

coins = list(data.columns.values)
dates = list(data['date'])

# Exclude date column from historical prices
historical_prices = np.array(data[coins][data.columns.values[1:]])

start_amt = 5000
thresh = .05

for num_coins in range(2,5,2):

	# Divide up the start amount into how much $ per coin
	avg_weight = 1/num_coins
	amt_each = start_amt / num_coins
	weighted_thresh = np.float32(avg_weight * thresh)

	# Download HODL simulation with same # of coins as comparison
	path = os.path.dirname(os.path.abspath(filename)) + '/backtests/' + str(num_coins) + '/' + str(num_coins) + '_'
	hodl_simulations = pd.read_csv(path + 'HODL.csv')

	# Exclude date column
	hodl_simulations = hodl_simulations.drop(hodl_simulations.columns[[0]], axis=1)
	cols = hodl_simulations.columns.tolist()
	hodl_simulations = np.array(hodl_simulations)

	# Create arrays that will be transformed to CSV's
	simulation_summary = [[] for x in range(len(cols))]
	rebalance_simulations = np.empty(shape=(len(cols), len(historical_prices)))
	num_simulation = 0

	# Use the same coin combinations as the HODL simulation
	coin_lists = [col.split('-') for col in cols]

	# For each simulation, convert the symbol into the corresponding column # in historical_prices
	coin_lists_indexes = [[coins.index(coin) for coin in coin_list] for coin_list in coin_lists]

	for col, coin_list in zip(cols, coin_lists):

		fees, trade_count, trades_eliminated = 0, 0, 0
		daily_totals = [start_amt]

		# Reduce historical_prices array to only the coins used in the simulation
		small_historical_prices = historical_prices[:, coin_lists_indexes[num_simulation]]

		# Calculate starting coin amounts
		coin_amts = amt_each / small_historical_prices[0]

		# Simulate each day
		for num_day in range(1,len(historical_prices)):
			while True:
				dollar_values = small_historical_prices[num_day] * coin_amts
				total_dollar_value = sum(dollar_values)
				l_index, h_index = dollar_values.argmin(), dollar_values.argmax()

				# See how far the lightest and heaviest coin weight deviates from average weight
				weight_to_move = min([avg_weight - dollar_values[l_index]/total_dollar_value, dollar_values[h_index]/total_dollar_value - avg_weight])

				if weighted_thresh > weight_to_move:
					break

				# Does a ticker for the coins exist? - if it doesn't, it needs to convert to BTC first, which takes two trades
				ratios = {coin_list[l_index] + '/' + coin_list[h_index], coin_list[h_index] + '/' + coin_list[l_index]}
				ticker = ratios & tickers

				if not ticker:
					trade_count += 2
					rate = 0.005
				else:
					trade_count += 1
					rate = 0.0025
					trades_eliminated += 1

				dollar_amt = weight_to_move * total_dollar_value
				fees += (dollar_amt * rate)

				# Adjust coin quantities
				coin_amts[l_index] += dollar_amt / small_historical_prices[num_day, l_index]
				coin_amts[h_index] -= dollar_amt / small_historical_prices[num_day, h_index] * (1 + rate)

			# document total portfolio value on that day
			daily_totals.append(np.dot(small_historical_prices[num_day], coin_amts))

		# Document important features of the simulations
		end_price_HODL = hodl_simulations[len(hodl_simulations)-1, num_simulation]
		end_price_rebalanced = daily_totals[len(daily_totals)-1]
		simulation_summary[num_simulation] = [col, fees, trade_count, trades_eliminated, end_price_HODL, end_price_rebalanced]
		rebalance_simulations[num_simulation] = daily_totals
		num_simulation += 1

	rebalance_simulations = pd.DataFrame(np.transpose(rebalance_simulations), columns=cols, index=dates)
	simulation_summary = pd.DataFrame(simulation_summary,columns=['portfolio','total_fees','num_trades','num_trades_saved','end_price_HODL','end_price_rebalanced'])

	rebalance_simulations.to_csv(path + 'rebalanced.csv')
	simulation_summary.to_csv(path + 'summary.csv', index=False)

# ------------------------------------------------------------------------------------------------------------------------------------
	# average simulation time - 8/16
	# 2   -  60/min
	# 4   -  50/min

	# 8/20 - rafactored simulation_summary to remove .loc
	# 2 - 120/min
	# 4 - 100/min

	# 8/21 - refactored pandas DataFrames into numpy arrays
	# 2 - 4,200/min
	# 4 - 3,000/min

	# 8/23 - refactored list of lists (data) to separate numpy lists / removed update_weight function
	# 2 - 8,000/min
	# 4 - 5,700/min

	# 8/30 - converted pandas DataFrames into numpy arrays
	# 2 - 11,000/min
	# 4 - 7,700/min

	# 9/7 - Reduced # of calculated operations in central loop
	# 2 - 14,000/min
	# 4 - 10,000/min
