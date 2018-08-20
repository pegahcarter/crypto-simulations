import pandas as pd
import random
from openpyxl import load_workbook
import os

path = os.getcwd()
file = path + '/historical data.xlsx'
df = pd.read_excel(file)
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

        # with line comprehension - 0.01897
        # w/o line comprehension  - 0.010
        [totals.append(sum([df[random_list[b]][a] * coin_amts[b] for b in range(num_to_select)])) for a in range(len(df))]

        simulations[coins_chosen] = totals

    writer = pd.ExcelWriter(path + '/backtests/' + str(num_to_select) + '/' + str(num_to_select) + '_HODL.xlsx', engine='openpyxl')
    simulations.to_excel(writer)
    writer.save()
