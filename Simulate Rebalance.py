import pandas as pd
import numpy as np
import random
import ccxt
from openpyxl import load_workbook
import os
import time
import sys

file = os.getcwd() + '/historical data.xlsx'
historical_prices = pd.read_excel(file)
coins = historical_prices.columns.tolist()[1:]
exchange = ccxt.binance()
tickers = set()
[tickers.add(ticker) for ticker in exchange.fetchTickers()]

start_amt = 5000
thresh = .05
# t0 = time.time()

for num_coins in range(2,11,2):
    print('------------------')
    print('\n# of coins:  ', num_coins)

    path = os.getcwd() + '/backtests/' + str(num_coins) + '/' + str(num_coins) + '_'
    avg_weight = 1/num_coins
    weight_thresh = np.float32(avg_weight * thresh)
    thresh_range = [avg_weight-weight_thresh, avg_weight + weight_thresh]

    amt_each = start_amt / num_coins

    simulation_summary = pd.DataFrame(columns=['total_fees','num_of_trades','num_trades_saved','end_price_HODL','end_price_rebalanced'])
    rebalance_simulations = pd.DataFrame()
    hodl_simulations = pd.read_excel(path + 'HODL.xlsx')
    cols = hodl_simulations.columns.tolist()

    for num_simulation in range(0,len(cols)):
        if num_simulation % 50 == 0:
            print(num_simulation)

        fee = 0
        fees = 0
        trade_count = 0
        trades_eliminated = 0
        daily_totals = [start_amt]

        col_name = cols[num_simulation]
        coin_list = col_name.split('-')
        coin_amts = [amt_each / historical_prices[i][0] for i in coin_list]

        data = pd.DataFrame({'symbol': coin_list, 'quantity': coin_amts})
        data.set_index(keys='symbol',inplace=True)
        data['weight'] = avg_weight
        data['dollar_value'] = start_amt / num_coins

        for num_day in range(1,len(historical_prices)):
            data['dollar_value'] = [data['quantity'][coin] * historical_prices[coin][num_day] for coin in data.index.values]
            total_dollar_value = np.float32(sum(data['dollar_value']))
            data['weight'] = data['dollar_value'] / total_dollar_value

            data.sort_values('weight', ascending=True, inplace=True)

            while True:

                weight_range = data['weight'][::num_coins-1].tolist()

                if weight_range[1] - weight_range[0] < 2 * avg_weight * thresh:
                    break
                elif avg_weight - weight_range[0] < weight_range[1] - avg_weight:
                    weight_to_sell = (weight_range[1] - avg_weight) / 2
                else:
                    weight_to_sell = (avg_weight - weight_range[0]) / 2

                dollar_amt = np.float32(weight_to_sell * total_dollar_value)
                small_coin, large_coin = data.index.values[0], data.index.values[num_coins-1]
                ratios = [small_coin + '/' + large_coin, large_coin + '/' + small_coin]
                ticker = list((set(ratios) & tickers))

                if len(ticker) < 1:
                    ticker = [large_coin + '/BTC', small_coin + '/BTC']
                    trade_count += 2
                else:
                    trades_eliminated += 1
                    trade_count += 1

                numer = ticker[0][:ticker[0].find('/')]

                if len(ticker) == 2:
                    denom = ticker[1][:ticker[1].find('/')]
                else:
                    denom = ticker[0][ticker[0].find('/') + 1:]

                rate = len(ticker) * .0025
                fees += (dollar_amt * rate)

                numer_quantity = dollar_amt / np.float32(historical_prices[numer][num_day]) # for coin before '/')
                denom_quantity = dollar_amt / np.float32(historical_prices[denom][num_day])
                denom_quantity_after_fees = np.float32((1-rate) * denom_quantity)

                if numer == small_coin:
                    data.at[numer, 'quantity'] += numer_quantity
                    data.at[denom, 'quantity'] -= denom_quantity_after_fees
                else:
                    data.at[numer, 'quantity'] -= numer_quantity
                    data.at[denom, 'quantity'] += denom_quantity_after_fees

                total_dollar_value -= fee
                data['dollar_value'] = [data['quantity'][coin] * historical_prices[coin][num_day] for coin in data.index.values]
                data['weight'] = data['dollar_value'] / total_dollar_value
                data.sort_values('weight', ascending=True, inplace=True)

            # document total portfolio value on that day
            daily_totals.append(sum([historical_prices[coin][num_day] * data.at[coin, 'quantity'] for coin in data.index.values]))

        # Add year of rebalancing simulation to simulation dataset
        rebalance_simulations[col_name] = daily_totals

        # Document important features of the simulations
        end_price_HODL = hodl_simulations[col_name][len(hodl_simulations) - 1]
        simulation_summary.loc[col_name] = [fees, trade_count, trades_eliminated, hodl_simulations[col_name][len(hodl_simulations) - 1], daily_totals[len(daily_totals)-1]]

    rebalance_writer = pd.ExcelWriter(path + 'rebalanced.xlsx', engine='openpyxl')
    summary_writer = pd.ExcelWriter(path + 'summary.xlsx', engine='openpyxl')

    rebalance_simulations.to_excel(rebalance_writer)
    simulation_summary.to_excel(summary_writer)

    rebalance_writer.save()
    summary_writer.save()

    # average simulation time after 10 runs
    # 2   -  60/min - 17 min for 1000
    # 4   -  50/min - 20 min for 1000
    # 6   -  43/min - 23 min for 1000
    # 8   -  32/min - 31 min for 1000
    # 10  -  26/min - 38 min for 1000
    # -------------------------------
    #                   129 min total
