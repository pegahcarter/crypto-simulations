import os
import sys
import ccxt
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta

# Section to pull hourly price data

exchange = ccxt.binance({'options':{'adjustForTimeDifference':True}})
exchange = ccxt.bittrex()

market = exchange.load_markets()
tickers = list(market.keys())


coins = set()
[[coins.add(coin) for coin in ticker.split('/') if coin != 'BTC'] for ticker in tickers]
coins = list(coins)

# Since we can't pull BTC/BTC, use BTC/USDT ticker.  Otherwise, use coin/BTC as ticker
tickers = [coin + '/BTC' for coin in coins]
tickers.insert(0, 'BTC/USDT')

# ------------------------------------------------------------------------------
# Using this section only to pull the epoch times for the data pulled
start_date = datetime.strptime('2017-12-01 00:00:00', '%Y-%m-%d %H:%M:%S') - timedelta(hours=500)
end_date = datetime.strptime('2018-12-01 00:00:00', '%Y-%m-%d %H:%M:%S')

timestamps = []
while start_date < end_date:
	candles = np.array(exchange.fetch_ohlcv('ETH/BTC', '1h', exchange.parse8601(datetime.strftime(start_date, '%Y-%m-%d %H:%M:%S')), 500))
	timestamps += [timestamp for timestamp in candles[:,0]/1000]

	start_date += timedelta(hours=len(candles))

# take the last 8760 date times (8760 hours = 1 year)
df = pd.DataFrame(data=timestamps[len(timestamps)-8760:], columns=['timestamp'])

for ticker in tickers:
	# We're pulling 500 1-hour rows per API call, and the API call uses the date
	#	input as the last date returned, and we want the first date returned to be 2017-12-01
	start_date = datetime.strptime('2017-12-01 00:00:00', '%Y-%m-%d %H:%M:%S') - timedelta(hours=500)
	prices = []

	try:
		while end_date > start_date:
			candles = np.array(exchange.fetch_ohlcv(ticker, '1h', exchange.parse8601(datetime.strftime(start_date, '%Y-%m-%d %H:%M:%S')), 500))
			prices += [price for price in candles[:,1]]
			start_date += timedelta(hours=len(candles))

	except:
		continue

	# Add the data if there's 8760 hrs of data (1 year)
	if len(prices) > 8760:
		df[ticker[:ticker.find('/')]] = prices[len(prices)-8760:]

# ------------------------------------------------------------------------------






timestamps = []
start_date = '2017-01-01 00:00:00'
for i in range(16500):
	timestamps.append(start.strftime('%Y-%m-%d %H:%M:%S'))
	start += datetime.timedelta(hours=1)

df = pd.DataFrame()
df['date'] = timestamps


msec = 1000
minute = 60 * msec
hour = minute * 60

end_date = exchange.parse8601('2018-12-01 00:00:00')


for ticker in tickers:
	ticker = 'ETH/BTC'
	start_date = exchange.parse8601('2017-12-01 00:00:00')

for ticker in tickers:
	# Length of above when queried - 16500 (ETH/BTC) (or 33 queries of 500)

	data = []

	for i in range(33):
		try:
			candles = np.array(exchange.fetch_ohlcv(ticker, '1h', start_date))
		except:
			continue

		start_date += len(candles) * hour

		data += candles[:, :2].tolist()

		data += candles[:, 1].tolist()

	if len(data) == 16500:
		df[ticker[:ticker.find('/')]] = data

# multiply all columns by BTC column to get $ prices, since they're currently all in BTC denomination
for col in df[df.columns[1:].values]:
	df[col] = np.multiply(df[col], df['BTC'])


new_df.set_index('date', drop=True, inplace=True)
new_df.to_csv(os.getcwd() + '/backtests/historical prices.csv')
