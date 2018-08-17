import pandas as pd
import numpy as np
import random
import ccxt
from openpyxl import load_workbook
import os

path = os.getcwd()
file = path + '/backtests/historical data.xlsx'
historical_prices = pd.read_excel(file)
coins = historical_prices.columns.tolist()[1:]
exchange = ccxt.binance()
tickers = set()
[tickers.add(ticker) for ticker in exchange.fetchTickers()]

thresh = .05
start_amt = 5000
num_coins = 4
avg_weight = 1/num_coins
weight_thresh = np.float32(avg_weight * thresh)
thresh_range = [avg_weight-weight_thresh, avg_weight + weight_thresh]

for num_coins in range(4,5,2):
    amt_each = start_amt / num_coins
    rebalance_simulations = pd.DataFrame()
    hodl_simulations = pd.read_excel(path + '/backtests/HODL/' + str(num_coins) + '.xlsx')
    cols = hodl_simulations.columns.tolist()

    for num_simulation in range(1): #range(len(cols))

        fee = 0
        fees = 0
        trade_count = 0
        trades_eliminated = 0
        totals = [start_amt]

        col_name = cols[num_simulation]
        coin_list = col_name.split('-')
        coin_amts = [amt_each / historical_prices[i][0] for i in coin_list]

        simulations = pd.DataFrame()
        data = pd.DataFrame({'symbol': coin_list, 'quantity': coin_amts})
        data.set_index(keys='symbol',inplace=True)
        data['weight'] = avg_weight
        data['dollar_value'] = start_amt / num_coins

        for num_day in range(1,5): # len(historical_prices)
            data['dollar_value'] = [data['quantity'][coin] * historical_prices[coin][num_day] for coin in coin_list]
            total_dollar_value = np.float32(sum(data['dollar_value']))
            data['weight'] = data['dollar_value'] / total_dollar_value

            data.sort_values('weight', ascending=True, inplace=True)
            test = 0
            print('Day #', num_day)
            while True:
                test += 1
                if test > 4:
                    print('looping needs fix')
                    break

                weight_range = data['weight'][::num_coins-1].tolist()
                print(data['weight'])
                print(sum(data['weight']))

                if weight_range[0] > thresh_range[0] and weight_range[1] < thresh_range[1]:
                    break
                elif avg_weight - weight_range[0] > weight_range[1] - avg_weight:
                    weight_to_sell = weight_range[1] - avg_weight
                else:
                    weight_to_sell = avg_weight - weight_range[0]

                weight_to_sell = abs(weight_to_sell)
                dollar_amt = np.float32(weight_to_sell * total_dollar_value)
                small_coin, large_coin = data.index.values[0], data.index.values[num_coins-1]
                ratios = [small_coin + '/' + large_coin, large_coin + '/' + small_coin]
                ticker = list((set(ratios) & set(tickers)))

                if not ticker:
                    ticker = [large_coin + '/BTC', small_coin + '/BTC']
                    trade_count += 2
                else:
                    trades_eliminated += 1
                    trade_count += 1

                numer = ticker[0][:ticker[0].find('/')]

                if len(ticker) == 2:
                    denom = ticker[1][:ticker[1].find('/')]
                else:
                    denom = ticker[0][:ticker[0].find('/')+1:]

                rate = len(ticker) * .0025
                fee = (1-rate) * dollar_amt
                fees += fee

                numer_quantity = dollar_amt / np.float32(historical_prices[numer][num_day]) # for coin before '/')
                denom_quantity = dollar_amt / np.float32(historical_prices[denom][num_day])
                denom_quantity_after_fees = np.float32((1-rate) * denom_quantity)

                if numer == small_coin:
                    data.at[numer, 'quantity'] += numer_quantity
                    data.at[denom, 'quantity'] -= denom_quantity_after_fees
                else:
                    data.at[numer, 'quantity'] -= numer_quantity
                    data.at[denom, 'quantity'] += denom_quantity_after_fees

                #total_dollar_value -= fee
                data['dollar_value'] = [data['quantity'][coin] * historical_prices[coin][num_day] for coin in coin_list]
                data['weight'] = data['dollar_value'] / total_dollar_value
                data.sort_values('weight', ascending=True, inplace=True)

            # document total portfolio value on that day
            totals.append(sum([historical_prices[coin][num_day] * data.at[coin, 'quantity'] for coin in coin_list]))

        simulations[col_name] = totals

        # TODO write to excel





----
HODL.py as example
file = 'historical data.xlsx'
historical_prices = pd.read_excel(file)
coin_list = historical_prices.columns.tolist()[1:]
start_amt = 5000

for num_to_select in range(2,11,2):
    amt_each = start_amt / num_to_select
    simulations = pd.DataFrame()
    for x in range(1000):
        random_list = random.sample(coin_list, num_to_select)
        coin_amts = [amt_each / historical_prices[i][0] for i in random_list]
        coins_chosen = '-'.join(random_list)
        totals = []

        for a in range(len(historical_prices)):
            totals.append(sum([historical_prices[random_list[b]][a] * coin_amts[b] for b in range(num_to_select)]))

        simulations[coins_chosen] = totals

    writer = pd.ExcelWriter(os.getcwd() + '/backtests/HODL/' + str(num_to_select) + '.xlsx', engine='openpyxl')
    simulations.to_excel(writer)
    writer.save()
