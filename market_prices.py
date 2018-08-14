import os
import sys
import ccxt
import pandas as pd
from openpyxl import load_workbook

exchange = ccxt.bittrex({'options': {'adjustForTimeDifference': True}})
df = pd.DataFrame()
dates = []

for item in exchange.fetch_ohlcv('DOGE/BTC', '1d'):
    if 1493800000000 < item[0] < 1525400000000: # May 5, 2017 to May 5, 2018
        dates.append(item[0])

df['date'] = dates
df['BTC'] = None
for item in exchange.fetch_ohlcv('BTC/USDT', '1d'):
    df.loc[df['date'] == item[0], 'BTC'] = item[1]

# Coins w/ market cap above $70 mil on May 5, 2017
# excludes MAID, BTS, BCN, SNGLS, DGD
coins = ['ETH','XRP','LTC','DASH','XEM','ETC','XMR','GNT','XLM','REP','DOGE','ZEC','GNO','STRAT','STEEM','FCT','DCR','PIVX','WAVES','LSK','ARDR']

for coin in coins:
    df[coin] = None
    for item in exchange.fetch_ohlcv(coin + '/BTC', '1d'):
        if item[0] < 1493800000000 or item[0] > 1525400000000:
            continue

        df.loc[df['date'] == item[0], coin] = item[1]

df['date'] /= 1000
df.reset_index(drop=True, inplace=True)
for col in df.columns[2:]:
    df[col] *= df['BTC']

wb = load_workbook('historical data.xlsx')
writer = pd.ExcelWriter('historical data.xlsx', engine='openpyxl')
df.to_excel(writer)
writer.save()
