import pandas as pd
import numpy as np

df = pd.read_csv('data/historical_prices.csv')

class Portfolio(object):

	def __init__(self, coins):
		self.coins = coins
		self.quantities = [1000 / df[coin][0] for coin in coins]
		self.daily_prices = np.array(df[coins])

	def buy(self, coin, dollar_amt, time_index):
		coin_pos = self.coins.index(coin)
		quantity = dollar_amt * self.daily_values[time_index, coin_pos]
		self.quantities[coin_pos] += quantity

	def sell(self, coin, dollar_amt, time_index):
		coin_pos = self.coins.index(coin)
		quantity = dollar_amt * self.daily_values[time_index, coin_pos]
		self.quantities[coin_pos] -= quantity

	def outliers(self, pos):
		all_d_vals = self.daily_prices[pos] * self.quantities
		min_pos, max_pos = all_d_vals.argmin(), all_d_vals.argmax()
		outlier_d_vals = [all_d_vals[min_pos], all_d_vals[max_pos]]
		outlier_coins = [self.coins[min_pos], self.coins[max_pos]]
		return outlier_d_vals, outlier_coins

	def total_dollar_value(self, pos):
		return np.dot(self.daily_prices[pos], self.quantities)
