import os
import sys
import ccxt
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import time

exchange = ccxt.bittrex()

market = exchange.load_markets()
tickers = list(market.keys())

coins = set()
[[coins.add(coin) for coin in ticker.split('/') if coin != 'BTC'] for ticker in tickers]
coins = list(coins)

# Since we can't pull BTC/BTC, use BTC/USDT ticker.  Otherwise, use coin/BTC as ticker
tickers = [coin + '/BTC' for coin in coins]
tickers.insert(0, 'BTC/USDT')

# This part makes the timestamp column of the dataset
end_date = datetime.strptime('2018-12-01 00:00:00', '%Y-%m-%d %H:%M:%S')
start_date = datetime.now() - timedelta(days=365)
timestamps = []
while start_date < datetime.now():
	timestamps.append(datetime.strftime(start_date, '%s'))
	start_date += timedelta(hours=1)

# Note: sometimes the above pulls a few extra rows depending on the hour of day,
# so w'll stick to a perfect years' worth of rows
df = pd.DataFrame(data=timestamps[:8760], columns=['timestamp'])

# This adds all the coin prices over the same time frame
for ticker in tickers:

	# We're pulling 500 1-hour rows per API call, and the API call uses the date
	#	input as the last date returned, and we want the first date returned to be 2017-12-01
	start_date = datetime.now() - timedelta(days=365)

	# Our list of price data for the coin
	prices = []

	try:
		while end_date > start_date:

			candles = np.array(exchange.fetch_ohlcv(ticker, '1h', exchange.parse8601(datetime.strftime(start_date, '%Y-%m-%d %H:%M:%S'))))
			prices += [price for price in candles[:,1]]
			start_date += timedelta(hours=len(candles))

	except:
		continue

	# Add the data if there's 8760 hrs of data (1 year)
	if len(prices) > 8760:
		df[ticker[:ticker.find('/')]] = prices[len(prices)-8760:]


# Removing the index so the timestamp is column 1
df.set_index('timestamp', drop=True,inplace=True)

# Multiply each coin price, because each price was pulled was in ?/BTC denomination
for col in df.drop('BTC',axis=1).columns.values:
	df[col] *= df['BTC']

# Save file
df.to_csv('data/historical/prices.csv')
