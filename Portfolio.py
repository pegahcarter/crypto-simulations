import pandas as pd
import numpy as np

hist_prices = pd.read_csv('data/historical/prices.csv')

class Portfolio(object):

	def __init__(self, coins):
		self.coins = coins
		self.quantities = [1000 / hist_prices[coin][0] for coin in coins]

	def execute_trade(self, coin_indices, dollar_amt, current_prices):
		buy_index, sell_index = coin_indices
		self.quantities[buy_index] += (dollar_amt / current_prices[buy_index])
		self.quantities[sell_index] -= (dollar_amt / current_prices[sell_index])
