import pandas as pd
import numpy as np
import random
import os

path = os.getcwd()
file = path + '/historical prices.csv'
historical_prices = pd.read_csv(file)
coin_list = historical_prices.columns.tolist()[1:]
coin_indexes = len(coin_list)-1

# Convert historical_prices to numpy array to improve performance
data = np.array(historical_prices[coin_list])

# Start with $5000 of Bitcoin at day 0 price
start_amt = 5000

# Simulate 2, 4, 6, 8, and 10 coins
for num_to_select in range(2,11,2):
    amt_each = start_amt / num_to_select
    simulations = pd.DataFrame({'date':df['date'].tolist()})

    for x in range(1000):

		# Randomly select coins to simulate
        random_list = random.sample(range(0, coin_indexes), num_to_select)
        col_name = '-'.join([coin_list[i] for i in random_list])

		# Get coin amount
        coin_amts = amt_each / data[0][random_list]

		# Record simulation
        simulations[col_name] = data[:, random_list].dot(coin_amts)

    simulations.set_index(['date'], inplace=True)
    simulations.to_csv(path + '/backtests/' + str(num_to_select) + '/' + str(num_to_select) + '_HODL.csv')
