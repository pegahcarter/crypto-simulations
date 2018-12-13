import numpy as np
import pandas as pd
from Portfolio import Portfolio
import random

def hodl(df):

	# Use the same dates that are in prices.csv
	date_range = df['timestamp']

	# initialize our dataframe
	sims = pd.DataFrame(index=date_range)

	# Take the coin column names as our coin list
	coins = df.columns.tolist()[1:]

	# convert our dataframe to numpy so we can find the dot product of quantities and prices
	df = np.array(df[coins])

	# run 250 simulations
	for sim_num in range(250):

		# randomly select 5 coins to simulate
		random_coins = random.sample(coins, 5)

		# create portfolio class object
		myPortfolio = Portfolio(random_coins)

		# Combine the coin list with '-' to use as the column name
		col = '-'.join(random_coins)

		# Multiply quantities we own by hourly prices to get price for each hour
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
