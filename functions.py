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
		sims[col] = myPortfolio.daily_prices.dot(myPortfolio.quantities)

	sims.to_csv('hodl.csv')
	return sims


def updatePortfolio():
	pass


def rebalance(df, hodl_df):

	# Set the threshold of weight difference to trigger a trade
	num_coins = 5
	thresh = 0.05
	avg_weight = 1 / num_coins
	weighted_thresh = np.float32(avg_weight * thresh)

	sims = np.empty(shape=(len(hodl_df.columns), len(hist_prices)))

	# Use the same coin combinations as the HODL simulation
	coin_lists = [col.split('-') for col in hodl_df.columns]

	for num_sim, coin_list in enumerate(coin_lists):

		Hour = Portfolio(coin_list)
		Day = Portfolio(coin_list)
		Month = Portfolio(coin_list)

		for num_day in range(1, len(hist_prices)):
			updatePortfolio(Hour)

			if num_day % 24 == 0:
				updatePortfolio(Day)

			if num_day % (24 * 30) == 0:
				updatePortfolio(Month)





def summarize():
	pass
