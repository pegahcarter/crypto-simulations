import numpy as np

def hodl(df):

	amt_each = 1000	
	coin_list = df.columns.tolist()[1:]
	df = np.array(df)
	sims = pd.DataFrame(index=date_range)

	for sim_num in range(1000):
		random_list = random.sample(range(len(coin_list)-1), 5)
		coin_amts = amt_each / df[0, random_list]
		col = '-'.join([coin_list[i] for i in random_list])
		sims[col] = df[:, random_list].dot(coin_amts)
		sims.to_csv('hodl.csv')
		return sims


def rebalance():
	pass
