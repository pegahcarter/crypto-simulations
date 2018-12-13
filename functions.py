import numpy as np
import pandas as pd
from Portfolio import Portfolio
import random

def hodl(df):

	date_range = df['timestamp']
	sims = pd.DataFrame(index=date_range)
	coins = df.columns.tolist()[1:]
	df = np.array(df[coins])

	for sim_num in range(1000):
		random_list = random.sample(range(len(coins)-1), 5)
		random_coins = [coins[i] for i in random_list]

		myPortfolio = Portfolio(random_coins)

		col = '-'.join(random_coins)
		sims[col] = np.dot(myPortfolio.daily_prices, myPortfolio.quantities)

	sims.to_csv('data/simulations/hodl.csv')
	return sims


def rebalance(myPortfolio, time_index):
	coins_to_trade, dollar_values = myPortfolio.outliers(time_index)
	total_dollar_value = myPortfolio.total_dollar_value(time_index)

	# See how far the lightest and heaviest coin weight deviates from average weight
	weight_to_move = min([
		avg_weight - dollar_values[0]/total_dollar_value,
		dollar_values[1]/total_dollar_value - avg_weight
	])

	if weighted_thresh > weight_to_move:
		return myPortfolio

	trade_in_dollars = weight_to_move * total_dollar_value

	myPortfolio.execute_trade(coins_to_trade, trade_in_dollars, time_index)

	return rebalance(myPortfolio, time_index)


def summarize(myPortfolio):
	return
