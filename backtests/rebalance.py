import pandas as pd
import numpy as np
import random
import ccxt
from openpyxl import load_workbook
import os

def update_data(coins):
    df = pd.DataFrame(columns=['symbol', 'quantity', 'price', 'dollar_value'])
    btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])
    for coin in coins:
        quantity = balance[coin]['total']
        price = btc_price
        if coin != 'BTC':
            btc_ratio = float(exchange.fetch_ticker(coin + '/BTC')['info']['lastPrice'])
            price *= btc_ratio

        dollar_value = quantity * price
        df = df.append({'symbol': coin,'quantity':quantity,'price':price,'dollar_value':dollar_value}, ignore_index=True)

    df = df.sort_values('dollar_value', ascending=False).reset_index(drop=True)
    df['weight'] = df['dollar_value'].divide(data['dollar_value'].sum())
    return df


def rebalance(coin1, coin2, weight_to_sell, tickers):
    if coin1 + '/' + coin2 in tickers:
        order = coin1 + '/' + coin2, 'sell'
    elif coin2 + '/' + coin1 in tickers:
        order = coin2 + '/' + coin1
    else:
        order = coin1 + '/BTC', 'sell', coin2 + '/BTC', 'buy'

    dollar_amt = abs(weight_to_sell * data['dollar_value'].sum())
    for i in range(0, order, 2):
        coin_amt = float(dollar_amt / data.loc[data['symbol'] == order[i][:3], 'price'])
        single_trade = 'Y'
        if len(order) > 2:
            single_trade = 'N'

        trade_coin(order[i], order[i+1], coin_amt, dollar_amt, fees, single_trade)


def trade_coin(ratio, side, coin_amt, dollar_amt, single_trade):
    exchange.create_order(ratio, 'market', side, coin_amt)
    transactions = pd.read_excel('transactions.xlsx')
    num_rows = len(transactions.index)
    trade_id = transactions['trade_id'][num_rows] + 1
    trade_date = datetime.now()
    fees = dollar_amt * .00075
    transaction = [trade_id, trade_date, side, ratio[:3], ratio[4:], coin_amt, dollar_amt, fees, single_trade]
    for i in range(transaction):
        wb = load_workbook('transactions.xlsx')
        ws = wb.worksheets[0]
        ws.cell(row=num_row+1, column=i+1).value = transaction[i]
        wb.save('transactions.xlsx')

file = os.getcwd() + '/backtests/historical data.xlsx'
df = pd.read_excel(file)
coins = df.columns.tolist()[1:]
exchange = ccxt.binance()
tickers = set()
[tickers.add(ticker) for ticker in exchange.fetchTickers()]

thresh = .05
start_amt = 5000
num_coins = 4
avg_weight = np.float32(1/num_coins)
weight_thresh = np.float32(avg_weight * thresh)


#for num_coins in range(2,11,2):
amt_each = start_amt / num_coins
simulations = pd.DataFrame()
# for x in range(1000):
random_list = random.sample(coins, num_coins)
coin_amts = [amt_each / df[i][0] for i in random_list]


coins_chosen = '-'.join(random_list)
totals = []

data = pd.DataFrame({'symbol': random_list, 'quantity': coin_amts})

#for x in range(1,len(df)):
x = 1
data['dollar_value'] = [data['quantity'][coin] * df[data['symbol'][coin]][x] for coin in range(num_coins)]
total_dollar_value = np.float32(sum(data['dollar_value']))
data['weight'] = data['dollar_value'] / total_dollar_value
data = data.sort_values('weight', ascending=False).reset_index(drop=True)


while True:
    heavy_weight_dif = data['weight'][0] - avg_weight
    light_weight_dif = avg_weight - data['weight'][num_coins-1]
    if heavy_weight_dif < weight_thresh and light_weight_dif < weight_thresh:
        break
    elif heavy_weight_dif > light_weight_dif:
        weight_to_sell = light_weight_dif
    else:
        weight_to_sell = heavy_weight_dif

    rebalance(data['symbol'][0], data['symbol'][num_coins-1], weight_to_sell, tickers)
    data = update_data(coins)









file = 'historical data.xlsx'
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

        for a in range(len(df)):
            totals.append(sum([df[random_list[b]][a] * coin_amts[b] for b in range(num_to_select)]))

        simulations[coins_chosen] = totals

    writer = pd.ExcelWriter(os.getcwd() + '/backtests/HODL/' + str(num_to_select) + '.xlsx', engine='openpyxl')
    simulations.to_excel(writer)
    writer.save()
