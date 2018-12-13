import numpy as np
import pandas as pd
from Portfolio import Portfolio, hist_prices, coins
import random

thresh = 0.05
avg_weight = 0.2
weighted_thresh = np.float32(avg_weight * thresh)

def hodl():

	# initialize our dataframe
	sims = pd.DataFrame(index=hist_prices['timestamp'])

	# convert our dataframe to numpy so we can find the dot product of quantities and prices
	df = np.array(hist_prices[coins])

	# run 250 simulations
	for sim_num in range(250):

		# randomly select 5 coins to simulate
		random_coins = random.sample(coins, 5)
		coin_indices = [coins.index(coin) for coin in random_coins]
		df_small = df[:, coin_indices]

		# create portfolio class object
		myPortfolio = Portfolio(random_coins)

		# Combine the coin list with '-' to use as the column name
		col = '-'.join(random_coins)

		# Multiply quantities we own by hourly prices to get price for each hour
		sims[col] = list(np.dot(df_small, myPortfolio.quantities))

	sims.to_csv('data/simulations/hodl.csv')
	return sims


def rebalance(myPortfolio, time_index, current_prices):

	#coins_to_trade, dollar_values = myPortfolio.outliers(time_index)
	dollar_values = myPortfolio.dollar_values(current_prices)

	# See how far the lightest and heaviest coin weight deviates from average weight
	weight_to_move = min([
		avg_weight - min(dollar_values)/sum(dollar_values),
		max(dollar_values)/sum(dollar_values) - avg_weight
	])

	if weighted_thresh > weight_to_move:
		return myPortfolio

	trade_in_dollars = weight_to_move * sum(dollar_values)
	coin_indices = dollar_values.argmin(), dollar_values.argmax()

	# myPortfolio.sell(coin_to_sell, trade_in_dollars, current_prices)
	# myPortfolio.buy(coin_to_buy, trade_in_dollars, current_prices)
	#

	myPortfolio.execute_trade(coin_indices, trade_in_dollars, current_prices)


	return rebalance(myPortfolio, time_index)


def summarize(myPortfolio):
	return
