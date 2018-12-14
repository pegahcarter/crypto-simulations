import numpy as np
import pandas as pd

hodl = pd.read_csv('data/simulations/hodl.csv')
coin_lists = hodl.columns[1:].tolist()
df = pd.DataFrame(index=coin_lists)

strategies = [
	'hodl',
	'hourly',
	'daily',
	'weekly',
	'monthly'
]

for strategy in strategies:

	results = np.array(pd.read_csv('data/simulations/' + strategy + '.csv'))

	df[strategy] = results[len(results)-1, 1:]

df.to_csv('data/simulations/summary.csv')
