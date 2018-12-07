import pandas as pd
import numpy as np

hist_prices = pd.read_csv('data/historical/prices.csv')

class Portfolio(object):

	def __init__(self, coins):
		self.coins = coins
		self.quantities = [1000 / hist_prices[coin][0] for coin in coins]
		self.daily_prices = np.array(hist_prices[coins])

	def buy(self, coin, dollar_amt, time_index):
		# coin_pos = self.coins.index(coin)
		quantity = dollar_amt * self.daily_values[time_index, coin_pos]
		self.quantities[coin_pos] += quantity

	def sell(self, coin, dollar_amt, time_index):
		# coin_pos = self.coins.index(coin)
		quantity = dollar_amt * self.daily_values[time_index, coin_pos]
		self.quantities[coin_pos] -= quantity

	def execute_trade(self, coins_to_trade, dollar_amt, time_index):
		buy_coin, sell_coin = [self.coins.index(coins_to_trade[0]), self.coins.index(coins_to_trade[1])]
		self.quantities[buy_coin] += (dollar_amt * self.daily_prices[time_index, buy_coin])
		self.quantities[sell_coin] -= (dollar_amt * self.daily_prices[time_index, sell_coin])


	def outliers(self, time_index):
		all_d_vals = self.daily_prices[time_index] * self.quantities
		min_pos, max_pos = all_d_vals.argmin(), all_d_vals.argmax()
		outlier_coins = (self.coins[min_pos], self.coins[max_pos])
		outlier_d_vals = (all_d_vals[min_pos], all_d_vals[max_pos])
		return outlier_coins, outlier_d_vals

	def total_dollar_value(self, pos):
		return np.dot(self.daily_prices[pos], self.quantities)
