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
plt.title('')
plt.show()

file = os.getcwd() + '/backtests/10/10_summary.csv'
df = pd.read_csv(file)
df.head()

#box_df = pd.DataFrame(columns=['strategy', 'end_price'])
box_df = []
for i in range(len(df)):
	box_df.append(['HODL', df['end_price_HODL'][i]])
	box_df.append(['rebalanced', df['end_price_rebalanced'][i]])

box_df = pd.DataFrame(box_df, columns=['strategy', 'end_price'])

g1 = sns.boxplot(data=box_df,
			y='strategy', x='end_price',
			width = 0.5)


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
