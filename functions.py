import numpy as np
from Portfolio import Portfolio


def hodl(df, coin_list):

	date_range = df['date']
	sims = pd.DataFrame(index=date_range)
	coin_list = df.columns.tolist()[1:]
	df = np.array(df[coin_list])

	for sim_num in range(1000):
		random_list = random.sample(range(len(coin_list)-1), 5)

		myPortfolio = Portfolio(random_list)

		col = '-'.join([coin_list[i] for i in random_list])
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
