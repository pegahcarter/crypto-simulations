import os
import sys
import ccxt
import numpy as np
import pandas as pd

# Returns dates and prices for the ticker: excludes high, low, volume, etc.
def ticker_array(ticker):
	return np.array(exchange.fetch_ohlcv(ticker, '1d'))[:,:2]

# Use coins listed on Bittrex
primary_exchange = ccxt.bittrex({'options': {'adjustForTimeDifference': True}})
market = primary_exchange.load_markets()
tickers = list(market.keys())

coins = set()
[[coins.add(coin) for coin in ticker.split('/')] for ticker in tickers]
coins = list(coins)

# Since we can't pull BTC/BTC, use BTC/USDT ticker.  Otherwise, use coin/BTC as ticker
tickers = ['BTC/USDT'
		   if coin == 'BTC'
		   else coin + '/BTC'
		   for coin in coins]

# pull epoch dates used for market caps
market_cap = pd.read_csv(os.getcwd() + '/backtests/historical market cap.csv')
dates = market_cap['date'] * 1000.0

data = np.array(exchange.fetch_ohlcv('BTC/USDT'))

test = []
for day, price in data[:, :2]:
	if min(dates) <= day <= max(dates):
		test.append([day, price])


len(test)


















# Use DOGE/BTC as basis to pull dates, because DOGE
dates = []
[dates.append(day) for day, price in ticker_array('DOGE/BTC') if 1501373000000 < day < 1532910000000] # July 30, 2017 to July 30, 2018
df['date'] = dates

for coin, ticker in zip(coins, tickers):
	# Pull information if ticker exists
	try:
		data = ticker_array(ticker)
	except:
		continue

	prices = []
	[prices.append(price) for day, price in data if day in dates]

	# Only add coin if it has a full year of price data
	if len(prices) == len(dates):
		df[coin] = prices

for col in df.columns.values[2:]:
	df[col] *= df['BTC']

df.set_index(['date'], drop=True, inplace=True)
df.to_csv('historical prices.csv')
