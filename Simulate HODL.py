import pandas as pd
import numpy as np
import random
from openpyxl import load_workbook
import os

path = os.getcwd()
file = path + '/historical_data.csv'
df = pd.read_csv(file)
coin_list = df.columns.tolist()[1:]
start_amt = 5000

for num_to_select in range(2,11,2):
    amt_each = start_amt / num_to_select
    simulations = pd.DataFrame()
    for x in range(1000):
        random_list = random.sample(coin_list, num_to_select)
        coin_amts = [amt_each / df[i][0] for i in random_list]
        coins_chosen = '-'.join(random_list)

        totals = []
        temp  = np.array(df[random_list])

        totals.append(sum(temp[num_to_select] * coin_amts))

        simulations[coins_chosen] = totals

    simulations.to_csv(path + '/backtests/' + str(num_to_select) + '/' + str(num_to_select) + '_HODL.csv')
