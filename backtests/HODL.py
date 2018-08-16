import pandas as pd
import random
from openpyxl import load_workbook
import os

file = 'historical data.xlsx'
df = pd.read_excel(file)
coin_list = df.columns.tolist()[1:]
print(len(coin_list) * len(coin_list)-1)
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
        # w/o line comprehension  - 0.01496
        #totals = [sum([df[random_list[b]][a] * coin_amts[b] for b in range(num_to_select)]) for a in range(len(df))]
        for a in range(len(df)):
            totals.append(sum([df[random_list[b]][a] * coin_amts[b] for b in range(num_to_select)]))

        simulations[coins_chosen] = totals

    writer = pd.ExcelWriter(os.getcwd() + '/backtests/HODL/' + str(num_to_select) + '.xlsx', engine='openpyxl')
    simulations.to_excel(writer)
    writer.save()
