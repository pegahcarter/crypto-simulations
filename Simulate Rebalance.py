import pandas as pd
import numpy as np
import random
import ccxt
import os
import time
import sys
import timeit


def update_quantity(add_side, add_amt, subtract_side, subtract_amt):
	coin_amts[coin_list.index(add_side)] += add_amt
	coin_amts[coin_list.index(subtract_side)] -= subtract_amt

exchange = ccxt.bittrex()
tickers = set()
[tickers.add(ticker) for ticker in exchange.fetch_tickers()]

start_amt = 5000
thresh = .01

data = pd.read_csv('historical prices.csv')
coins = list(data.columns.values)
dates = list(data['date'])
historical_prices = np.array(data[coins][data.columns.values[1:]])


for num_coins in range(2,11,2):
	simulation_summary, rebalance_simulations = [], dates

	avg_weight = 1/num_coins
	weighted_thresh = np.float32(avg_weight * thresh)
	amt_each = start_amt / num_coins

	path = os.getcwd() + '/backtests/' + str(num_coins) + '/' + str(num_coins) + '_'
	hodl_simulations = pd.read_csv(path + 'HODL.csv')
	hodl_simulations = hodl_simulations.drop(hodl_simulations.columns[[0]], axis=1)
	cols = hodl_simulations.columns.tolist()
	hodl_simulations = np.array(hodl_simulations)

	coin_lists = [col.split('-') for col in cols]
	coin_lists_indexes = [[coins.index(coin) for coin in coin_list] for coin_list in coin_lists]
	num_simulation = 0
	for col, coin_list, coin_list_index in zip(cols, coin_lists, coin_lists_indexes):

		fees, trade_count, trades_eliminated = 0, 0, 0
		daily_totals = [start_amt]
		small_historical_prices = historical_prices[:, coin_list_index]
		coin_amts = amt_each / small_historical_prices[0]

		for num_day in range(1,len(historical_prices)):
			while True:

				dollar_values = small_historical_prices[num_day] * coin_amts

				total_dollar_value = sum(dollar_values)
				weights = dollar_values / total_dollar_value

				light_index, heavy_index = weights.argmin(), weights.argmax()
				differences = [avg_weight - weights[light_index], weights[heavy_index] - avg_weight]

				if weighted_thresh > max([avg_weight - min(weights), max(weights) - avg_weight]):
					break


				weight_to_sell = min([avg_weight - min(weights), max(weights) - avg_weight]):




				elif avg_weight - light_weight < heavy_weight - avg_weight:
					weight_to_sell = (heavy_weight - avg_weight)
				else:
					weight_to_sell = (avg_weight - light_weight)

				dollar_amt = weight_to_sell * total_dollar_value

				light_coin, heavy_coin = coin_list[light_index], coin_list[heavy_index]
				ratios = [light_coin + '/' + heavy_coin, heavy_coin + '/' + light_coin]
				ticker = list(set(ratios) & tickers)

				if not ticker:
					trade_count += 2
					numer, denom = heavy_coin, light_coin
					ticker = [heavy_coin + '/BTC', light_coin + '/BTC']
				else:
					trade_count += 1
					numer, denom = ticker[0][:ticker[0].find('/')], ticker[0][ticker[0].find('/') + 1:]
					trades_eliminated += 1

				rate = len(ticker) * .0025
				fees += (dollar_amt * rate)

				numer_quantity = np.divide(dollar_amt, small_historical_prices[num_day][coin_list.index(numer)])
				denom_quantity = np.divide(dollar_amt, small_historical_prices[num_day][coin_list.index(denom)])
				denom_quantity_after_fees = (1-rate) * denom_quantity

				if numer == light_coin:
					update_quantity(numer, numer_quantity, denom, denom_quantity_after_fees)
				else:
					update_quantity(denom, denom_quantity_after_fees, numer, numer_quantity)

			daily_totals.append(sum(small_historical_prices[num_day] * coin_amts)) #document total portfolio value on that day

		end_price_HODL = hodl_simulations[len(hodl_simulations)-1, num_simulation] # Document important features of the simulations
		num_simulation += 1
		end_price_rebalanced = daily_totals[len(daily_totals)-1]
		rebalance_simulations.append(daily_totals)
		simulation_summary.append([col, fees, trade_count, trades_eliminated, end_price_HODL, end_price_rebalanced])

	rebalance_simulations = np.transpose(rebalance_simulations)
	rebalance_simulations = pd.DataFrame(rebalance_simulations, columns=cols)

	simulation_summary = pd.DataFrame(simulation_summary, columns=['portfolio','total_fees','num_trades','num_trades_saved','end_price_HODL','end_price_rebalanced'])
	print(len(coin_lists))
	print(time.time() - t0)
	rebalance_simulations.to_csv(path + 'rebalanced.csv')
	simulation_summary.to_csv(path + 'summary.csv')


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
	# 2 - 12,000/min
	# 4 - 7,700/min
