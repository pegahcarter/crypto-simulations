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
exchange = ccxt.binance()
tickers = set()
[tickers.add(ticker) for ticker in exchange.fetchTickers()]

start_amt = 5000
thresh = .05
#num_coins = 6
for num_coins in range(4,5,2):
    print('------------------')
    print('\n# of coins:  ', num_coins)

    path = os.getcwd() + '/backtests/' + str(num_coins) + '/' + str(num_coins) + '_'
    avg_weight = 1/num_coins
    weight_thresh = np.float32(avg_weight * thresh)
    thresh_range = [avg_weight-weight_thresh, avg_weight + weight_thresh]

    amt_each = start_amt / num_coins

    simulation_summary = []
    rebalance_simulations = pd.DataFrame()
    hodl_simulations = pd.read_excel(path + 'HODL.xlsx')
    cols = hodl_simulations.columns.tolist()
    # num_simulation = 0
    t0 = time.time()
    for num_simulation in range(50): # len(cols)
        if num_simulation % 50 == 0:
           print(num_simulation, ' - ', (time.time()-t0)/60, ' min')

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

            while True:
                total_dollar_value = update_weight_and_value(num_day)
                weight_range = data['weight'][::num_coins-1].tolist()

                if weight_range[1] - weight_range[0] < 2 * avg_weight * thresh:
                    break
                elif avg_weight - weight_range[0] < weight_range[1] - avg_weight:
                    weight_to_sell = (weight_range[1] - avg_weight)
                else:
                    weight_to_sell = (avg_weight - weight_range[0])

                small_coin, large_coin = data.index.values[::num_coins-1]
                ratios = [small_coin + '/' + large_coin, large_coin + '/' + small_coin]
                ticker = list((set(ratios) & tickers))

                dollar_amt = np.float32(weight_to_sell * total_dollar_value)

                if len(ticker) < 1:
                    ticker = [large_coin + '/BTC', small_coin + '/BTC']
                    denom = ticker[1][:ticker[1].find('/')]
                    trade_count += 2
                else:
                    denom = ticker[0][ticker[0].find('/') + 1:]
                    trade_count += 1
                    trades_eliminated += 1

                numer = ticker[0][:ticker[0].find('/')]

                rate = len(ticker) * .0025
                fees += (dollar_amt * rate)

                numer_quantity = dollar_amt / historical_prices[numer][num_day]
                denom_quantity = dollar_amt / historical_prices[denom][num_day]
                denom_quantity_after_fees = (1-rate) * denom_quantity

                if numer == small_coin:
                    update_quantity(numer, numer_quantity, denom, denom_quantity_after_fees)
                else:
                    update_quantity(denom, denom_quantity_after_fees, numer, numer_quantity)

            # document total portfolio value on that day
            daily_totals.append(sum([historical_prices[coin][num_day] * data.at[coin, 'quantity'] for coin in data.index.values]))

        # Add year of rebalancing simulation to simulation dataset
        rebalance_simulations[col_name] = daily_totals

        # Document important features of the simulations
        end_price_HODL = hodl_simulations[col_name][len(hodl_simulations) - 1]

        simulation_summary.append([col_name, fees, trade_count, trades_eliminated, hodl_simulations[col_name][len(hodl_simulations) - 1], daily_totals[len(daily_totals)-1]])

    simulation_summary = pd.DataFrame(simulation_summary, columns=['portfolio','total_fees','num_trades','num_trades_saved','end_price_HODL','end_price_rebalanced'])
    #rebalance_writer = pd.ExcelWriter(path + 'rebalanced.xlsx', engine='openpyxl')
    #summary_writer = pd.ExcelWriter(path + 'summary.xlsx', engine='openpyxl')

    #rebalance_simulations.to_excel(rebalance_writer)
    #simulation_summary.to_excel(summary_writer)

    #rebalance_writer.save()
    #summary_writer.save()

def update_weight_and_value(num_day):
    data['dollar_value'] = [data['quantity'][coin] * historical_prices[coin][num_day] for coin in data.index.values]
    total = sum(data['dollar_value'])
    data['weight'] = data['dollar_value'] / total
    data.sort_values('weight', ascending=True, inplace=True)
    return total


def update_quantity(add_side, add_amt, subtract_side, subtract_amt):
    data.at[add_side, 'quantity'] += add_amt
    data.at[subtract_side, 'quantity'] -= subtract_amt

    # average simulation time - 8/16
    # 2   -  60/min
    # 4   -  50/min
    # 6   -  43/min
    # 8   -  32/min
    # 10  -  26/min

    # 8/20 - rafactored simulation_summary to remove .loc
    # 2 - 120/min
    # 4 - 100/min
    # 6 -
    # 8 -
    # 10 -
