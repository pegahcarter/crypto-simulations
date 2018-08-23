import pandas as pd
import numpy as np
import random
import ccxt
import os
import time
import sys
import timeit

def update_quantity(add_side, add_amt, subtract_side, subtract_amt):
    coin_amts[coin_list.index(add_side)] += add_amt
    coin_amts[coin_list.index(subtract_side)] -= subtract_amt

historical_prices = pd.read_csv('historical_data.csv')
exchange = ccxt.binance()
tickers = set()
[tickers.add(ticker) for ticker in exchange.fetch_tickers()]

start_amt = 5000
thresh = .05
t0 = time.time()

for num_coins in range(2,11,2):
    avg_weight = 1/num_coins
    weight_thresh = np.float32(avg_weight * thresh)
    thresh_range = [avg_weight-weight_thresh, avg_weight + weight_thresh]

    amt_each = start_amt / num_coins

    simulation_summary = []
    rebalance_simulations = pd.DataFrame()

    path = os.getcwd() + '/backtests/' + str(num_coins) + '/' + str(num_coins) + '_'
    hodl_simulations = pd.read_csv(path + 'HODL.csv')
    hodl_simulations = hodl_simulations.drop(hodl_simulations.columns[[0]], axis=1)
    cols = hodl_simulations.columns.tolist()

    for num_simulation in range(len(cols)):
        fee = 0
        fees = 0
        trade_count = 0
        trades_eliminated = 0

        daily_totals = [start_amt]
        col_name = cols[num_simulation]
        coin_list = col_name.split('-')
        coin_amts = [amt_each / historical_prices[i][0] for i in coin_list]
        weights = np.multiply(avg_weight, num_coins)

        small_historical_prices = np.array(historical_prices[coin_list])

        # num_day = 1
        for num_day in range(1,len(historical_prices)):
            while True:

                dollar_values = np.multiply(small_historical_prices[num_day], coin_amts).tolist()
                total_dollar_value = sum(dollar_values)
                weights = np.divide(dollar_values, total_dollar_value).tolist()


                light_weight, heavy_weight = min(weights), max(weights)
                light_coin, heavy_coin = coin_list[weights.index(light_weight)], coin_list[weights.index(heavy_weight)]

                if heavy_weight - light_weight < 2 * avg_weight * thresh:
                    break
                elif avg_weight - light_weight < heavy_weight - avg_weight:
                    weight_to_sell = (heavy_weight - avg_weight)
                else:
                    weight_to_sell = (avg_weight - light_weight)

                ratios = [light_coin + '/' + heavy_coin, heavy_coin + '/' + light_coin]
                ticker = list(set(ratios) & tickers)
                dollar_amt = weight_to_sell * total_dollar_value

                if not ticker:
                    ticker = [heavy_coin + '/BTC', light_coin + '/BTC']
                    denom = ticker[1][:ticker[1].find('/')]
                    trade_count += 2
                else:
                    denom = ticker[0][ticker[0].find('/') + 1:]
                    trade_count += 1
                    trades_eliminated += 1

                numer = ticker[0][:ticker[0].find('/')]
                rate = len(ticker) * .0025
                fees += (dollar_amt * rate)

                numer_quantity = np.divide(dollar_amt, small_historical_prices[num_day][coin_list.index(numer)])
                denom_quantity = np.divide(dollar_amt, small_historical_prices[num_day][coin_list.index(denom)])
                denom_quantity_after_fees = (1-rate) * denom_quantity

                if numer == light_coin:
                    update_quantity(numer, numer_quantity, denom, denom_quantity_after_fees)
                else:
                    update_quantity(denom, denom_quantity_after_fees, numer, numer_quantity)

            # document total portfolio value on that day
            daily_totals.append(sum(small_historical_prices[num_day] * coin_amts))

        # Add year of rebalancing simulation to simulation dataset
        rebalance_simulations[col_name] = daily_totals

        # Document important features of the simulations
        end_price_HODL = hodl_simulations[col_name][len(hodl_simulations) - 1]
        end_price_rebalanced = daily_totals[len(daily_totals)-1]

        simulation_summary.append([col_name, fees, trade_count, trades_eliminated, end_price_HODL, end_price_rebalanced])

    simulation_summary = pd.DataFrame(simulation_summary, columns=['portfolio','total_fees','num_trades','num_trades_saved','end_price_HODL','end_price_rebalanced'])

    rebalance_simulations.to_csv(path + 'rebalanced.csv')
    simulation_summary.to_csv(path + 'summary.csv')

    # average simulation time - 8/16
    # 2   -  60/min
    # 4   -  50/min

    # 8/20 - rafactored simulation_summary to remove .loc
    # 2 - 120/min
    # 4 - 100/min

    # 8/21 - refactored pandas DataFrames into numpy arrays
    # 2 - 4,200/min
    # 4 - 3,000/min

    # 8/23 - refactored list of lists (data) to separate numpy lists / removed update_weight function
    # 2 - 8,000/min
    # 4 - 5,700/min
