import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ccxt
import os
import statistics
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns

%matplotlib inline

folder = os.getcwd() + '/backtests/10/10_'
file1 = pd.read_csv(folder + 'HODL.csv')
file2 = pd.read_csv(folder + 'rebalanced.csv')
dates = file1['date'].tolist()

sim_hodl = file1[file1.columns[1:]]
sim_rebalance = file2[file2.columns[1:]]

# histogram of rebalance performances compared to hodl performances
test1 = np.array(sim_hodl)
test2 = np.array(sim_rebalance)
end1 = test1[len(test1)-1, :]
end2 = test2[len(test2)-1, :]
result = (end2-end1) / end1
plt.hist(result, bins=25)
plt.show()


# average performance difference over time
avg_hodl = list(sim_hodl.mean(axis=1))
avg_rebalance = list(sim_rebalance.mean(axis=1))

diffs = np.subtract(avg_rebalance, avg_hodl)
pct = np.divide(diffs, avg_hodl)
plt.plot(dates, pct)


for i in range(2,11,2):
	folder = os.getcwd() + '/backtests/' + str(i) + '/' + str(i) + '_'
	sim_hodl = pd.read_csv(folder + 'HODL.csv')
	sim_rebalance = pd.read_csv(folder + 'rebalanced.csv')
	sim_hodl = sim_hodl[sim_hodl.columns[1:]]
	sim_rebalance = sim_rebalance[sim_rebalance.columns[1:]]

	avg_hodl = sim_hodl.mean(axis=1)
	avg_rebalance = sim_rebalance.mean(axis=1)
	a = (avg_rebalance - avg_hodl) / avg_hodl

	print(i)
	print('Percent of times to outperform HODL- ',len(a.loc[a>0])/len(a))
	print(a.mean(), '\n')


# -----------------------------------------------------------------------
# Enginering features from column names
folder = os.getcwd() + '/backtests/10/10_'
historical_data = pd.read_csv(os.getcwd() + '/historical prices.csv')
coins = historical_data.columns.values[1:]
file1 = pd.read_csv(folder + 'HODL.csv')
file2 = pd.read_csv(folder + 'rebalanced.csv')
dates = file1['date'].tolist()

sim_hodl = np.array(file1[file1.columns[1:]])
sim_rebalance = np.array(file2[file2.columns[1:]])
sim_hodl[len(sim_hodl)-1]

# Create dataframe with coin names as columns
df = pd.DataFrame(columns=coins)

# Add HODL and rebalance end price as feature
df['end_hodl'] = sim_hodl[len(sim_hodl)-1]
df['end_rebalance'] = sim_rebalance[len(sim_rebalance)-1]
df['performance'] = (df['end_rebalance'] - df['end_hodl'])/df['end_hodl']
df.loc[df['performance'] > 0, 'beat market'] = 1
df.loc[df['performance'] <= 0, 'beat market'] = 0

df[coins] = 0

cols = file1.columns.values[1:]
coin_lists = [lst.split('-') for lst in cols]

# fill in dataframe with coins used for each simulation
for i in range(len(coin_lists)):
	for coin in coin_lists[i]:
		df.loc[i, coin] = 1


tree = RandomForestClassifier()
X = df[coins]
Y = df['beat market']
tree.fit(X, Y)

# histogram of feature importance
feature_importance = tree.feature_importances_
feature_importance = 100 * (feature_importance / max(feature_importance))
temp = feature_importance.tolist()
top_feats = sorted(feature_importance,reverse=True)[:10]
sorted_features = np.array([temp.index(feat) for feat in top_feats])
pos = np.arange(sorted_features.shape[0]) + .5
plt.barh(pos, feature_importance[sorted_features], align='center')
plt.yticks(pos, X.columns[sorted_features])
plt.show()


# heatmap of variables
X = historical_data[coins]
correlations = X.corr()
sns.heatmap(correlations)

# Daily volatility of coin
X = np.array(historical_data[historical_data.columns.values[1:]])
d1 = X[:len(X)-1]
d2 = X[1:]

vol = pd.DataFrame(abs((d2-d1))/d1, columns=coins)

sdev = dict()
for col in vol:
	sdev[col] = round(statistics.stdev(vol[col]), 3)


# Make a dataset with XLM and one without - compare performance
xlm_yes = [l for l in cols if 'XLM' in l]
xlm_no = [l for l in cols if 'XLM' not in l]

file3 = pd.read_csv(os.getcwd() + '/backtests/10/10_summary.csv')

xlm_yes_df = file3.loc[file3['portfolio'].isin(xlm_yes)]
xlm_no_df = file3.loc[file3['portfolio'].isin(xlm_no)]

file1 = pd.read_csv(folder + 'HODL.csv')
file2 = pd.read_csv(folder + 'rebalanced.csv')

for a in [xlm_yes_df, xlm_no_df]:
	diffs = a['end_price_rebalanced'] - a['end_price_HODL']
	pos_returns = diffs[diffs>0]
	neg_returns = diffs[diffs<0]

	return_vs_hodl = diffs.mean() / a['end_price_HODL'].mean()

	print('\n\n\nAverage hodl result: ', round(a['end_price_HODL'].mean(), 2))
	print('Average rebalanced result: ', round(a['end_price_rebalanced'].mean(), 2))
	print('# rebalance sims that outperformed: ', len(pos_returns))
	print('# rebalance sims that underperformed: ', len(neg_returns))
	print('Percent of rebalance sims to outperform HODL: ', round((len(pos_returns)/(len(pos_returns) + len(neg_returns))),2))
	print('Avg rebalance performance compared to HODL', round(return_vs_hodl, 3))
