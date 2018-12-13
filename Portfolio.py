import pandas as pd
import numpy as np

hist_prices = pd.read_csv('data/historical/prices.csv')
coins = hist_prices.columns[1:].tolist()

class Portfolio(object):

	def __init__(self, coins):
		self.coins = coins
		self.quantities = [1000 / hist_prices[coin][0] for coin in coins]
		# self.daily_prices = np.array(hist_prices[coins])

	# make outliers to only return $ amounts
	def dollar_values(self, current_prices):
		return current_prices * self.quantities

	def execute_trade(self, coin_indices, dollar_amt, current_prices):
		buy_index, sell_index = coin_indices
		self.quantities[buy_index] += (dollar_amt / current_prices[buy_index])
		self.quantities[sell_index] -= (dollar_amt / current_prices[sell_index])


	# def outliers(self, time_index, daily_prices):
	# 	all_d_vals = self.daily_prices[time_index] * self.quantities
	# 	min_pos, max_pos = all_d_vals.argmin(), all_d_vals.argmax()
	# 	outlier_coins = (self.coins[min_pos], self.coins[max_pos])
	# 	outlier_d_vals = (all_d_vals[min_pos], all_d_vals[max_pos])
	# 	return outlier_coins, outlier_d_vals
	#
	# def total_dollar_value(self, time_index, current_prices):
	# 	return current_prices.dot(self.quantities)
