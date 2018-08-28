import pandas as pd
import numpy as np
import random
import os

path = os.getcwd()
file = path + '/historical prices.csv'
df = pd.read_csv(file)
coin_list = df.columns.tolist()[1:]

# Start with $5000 of Bitcoin at day 0 price
start_amt = 5000 / df['BTC'][0]

# Simulate 2, 4, 6, 8, and 10 coins
for num_to_select in range(2,11,2):
    amt_each = start_amt / num_to_select
    simulations = pd.DataFrame({'date':df['date'].tolist()})

    for x in range(1000):

		# Randomly select coins to simulate
        random_list = random.sample(coin_list, num_to_select)

		# Get coin amount in Bitcoin denomination
        coin_amts = [amt_each / df[i][0] for i in random_list]

		# Record simulation
        simulations['-'.join(random_list)] = df[random_list].dot(coin_amts)

    simulations.set_index(['date'], inplace=True)
    simulations.to_csv(path + '/backtests/' + str(num_to_select) + '/' + str(num_to_select) + '_HODL.csv')
