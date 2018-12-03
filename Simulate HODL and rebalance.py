import os
import sys
import ccxt
import numpy as np
import pandas as pd
import inspect
import random
import datetime

def simulate_HODL():
	sims = pd.DataFrame(index=sim_dates)

	for sim_num in range(1000):
		random_list = random.sample(range(len(coins)-1), num_coins)
		coin_amts = amt_each / hist_prices[0, random_list]

		col = '-'.join([coins[i] for i in random_list])

		sims[col] = hist_prices[:, random_list].dot(coin_amts)

	sims.to_csv(path + str(num_coins) + '/' + str(num_coins) + '_HODL.csv')
	return sims


def simulate_rebalance(df):

	# Set the threshold of weight difference to trigger a trade
	thresh = 0.05
	avg_weight = 1 / num_coins
	weighted_thresh = np.float32(avg_weight * thresh)

	# Exclude date column
	cols = df.columns.tolist()
	hodl_sims = np.array(df)

	# Create arrays to be transformed to CSV's
	sim_summary = [[] for x in range(len(cols))]
	rebalance_sims = np.empty(shape=(len(cols), len(hist_prices)))

	# Use the same coin combinations as the HODL simulation
	coin_lists = [col.split('-') for col in cols]

	# For each simulation, convert the symbol into the corresponding column # in hist_prices
	coin_lists_indices = [[coins.index(coin) for coin in coin_list] for coin_list in coin_lists]

	for num, (col, coin_list, coin_list_index) in enumerate(zip(cols, coin_lists, coin_lists_indices)):

		fees, trade_count, trades_eliminated, taxes_owed = 0, 0, 0, 0
		daily_totals = [start_amt]

		# Reduce hist_prices array to only the coins used in the simulation
		hist_prices_small = hist_prices[:, coin_list_index]

		# Calculate starting coin amounts
		coin_amts = amt_each / hist_prices_small[0]

		purchase_prices = hist_prices_small[0].tolist()

		# Simulate each day
		for num_day in range(1,len(hist_prices)):
			while True:
				d_vals = hist_prices_small[num_day] * coin_amts
				d_vals_total = sum(d_vals)
				l_index, h_index = d_vals.argmin(), d_vals.argmax()

				# See how far the lightest and heaviest coin weight deviates from average weight
				weight_to_move = min([avg_weight - d_vals[l_index]/d_vals_total, d_vals[h_index]/d_vals_total - avg_weight])

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

				d_amt = weight_to_move * d_vals_total
				fees += (d_amt * rate)

				# Get coin quantities to buy/sell based on current market price
				l_quantity = d_amt / hist_prices_small[num_day, l_index]
				h_quantity = d_amt / hist_prices_small[num_day, h_index] * (1 + rate)

				price_diff = hist_prices_small[num_day, h_index] - purchase_prices[h_index]

				taxes_owed += (price_diff * h_quantity * 0.25)

				# adjust avg purchase price for bought coin
				purchase_prices[l_index] = (purchase_prices[l_index] * coin_amts[l_index] + hist_prices_small[num_day, l_index] * l_quantity)/(coin_amts[l_index] + l_quantity)

				# Adjust coin quantities
				coin_amts[l_index] += l_quantity
				coin_amts[h_index] -= h_quantity

			# document total portfolio value on that day
			daily_totals.append(np.dot(hist_prices_small[num_day], coin_amts))

		# Document important features of the sims
		end_price_HODL = hodl_sims[len(hodl_sims)-1, num]
		end_price_rebalanced = daily_totals[len(daily_totals)-1]
		sim_summary[num] = [col, fees, taxes_owed, trade_count, trades_eliminated, end_price_HODL, end_price_rebalanced]
		rebalance_sims[num] = daily_totals

	rebalance_sims = pd.DataFrame(np.transpose(rebalance_sims), columns=cols, index=sim_dates)
	rebalance_sims.to_csv(path + str(num_coins) + '/' + str(num_coins) + '_rebalanced.csv')

	sim_summary = pd.DataFrame(sim_summary,columns=['portfolio','total_fees','taxes_owed','num_trades','num_trades_saved','end_price_HODL','end_price_rebalanced'])
	sim_summary.to_csv(path + str(num_coins) + '/' + str(num_coins) + '_summary.csv', index=False)


if __name__ == '__main__':

	# Retrieve location of historical prices file
	filename = inspect.getframeinfo(inspect.currentframe()).filename
	path = os.path.dirname(os.path.abspath(filename)) + '/data/'
	hist_prices = pd.read_csv(path + 'historical prices.csv')

	sim_dates = list(hist_prices['date'])
	coins = hist_prices.columns.tolist()[1:]

	# Exclude date column from historical prices
	hist_prices = np.array(hist_prices[coins])

	# get date ranges used for sims
	hist_cap = pd.read_csv(path + 'historical market cap.csv')
	hist_cap = np.array(hist_cap)

	start_dates = hist_cap[:len(hist_cap) - 365]
	end_dates = hist_cap[365:]

	# Subtract the ending market caps from each other, located in the 4th column
	cap_diffs = list(end_dates[:, 3] - start_dates[:, 3])

	# Make sure there's an odd number of dates, so the median value can be indexed
	if len(cap_diffs) % 2 == 0:
		cap_diffs.pop(len(cap_diffs)-1)

	# Start date for sims
	start_date = cap_diffs.index(np.median(cap_diffs))

	# Limit dataframe dates to the date range
	hist_prices = hist_prices[start_date:start_date + 365]
	sim_dates = sim_dates[start_date:start_date + 365]

	# Retrieve all current tickers on exchange
	exchange = ccxt.bittrex()
	tickers = set()
	[tickers.add(ticker) for ticker in exchange.fetch_tickers()]

	# Start with $5000 of Bitcoin at day 0 price
	start_amt = 5000

	for num_coins in range(2,11,2):

		amt_each = start_amt / num_coins

		print('Simulating HODL of ' + str(num_coins) + ' coins...')
		df = simulate_HODL()
		print('Finished\n')
		print('Simulating rebalance of ' + str(num_coins) + ' coins...')
		simulate_rebalance(df)
		print('Finished\n')

# ------------------------------------------------------------------------------
# Testing for simulations with different interval rates

def hodl():
	sims = pd.DataFrame(index=sim_dates)
	for sim_num in range(1000):
		random_list = random.sample(range(len(coins)-1), num_coins)
		coin_amts = amt_each / hist_prices[0, random_list]
		col = '-'.join([coins[i] for i in random_list])
		sims[col] = hist_prices[:, random_list].dot(coin_amts)
		sims.to_csv('hodl.csv')
		return sims


def rebalance(df, time_num):

	return df


timestamps = []
start_date = '2017-01-01 00:00:00'
start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

for i in range(16500):
	timestamps.append(start)
	start += datetime.timedelta(hours=1)



num_coins = 5
start_amt = 5000
amt_each = start_amt/num_coins

for coin_list in coin_lists:
	df_hour = []
	df_day = []
	df_month = []

	for i, time in enumerate(timestamps[1:]):

		df_hour = rebalance(df_hour)

		if i % 24 == 0:
			df_day = rebalance(df_day)

		if i % (24 * 20) == 0:
			df_month = rebalance(df_month)









# day = 1
# month = 1
# if time.day != day:
# 	function(df_day)
# 	day = time.day
#
# if time.month != month:
# 	function(df_month)
# 	month = time.month
# ------------------------------------------------------------------------------
