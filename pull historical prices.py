import os
import sys
import ccxt
import numpy as np
import pandas as pd
import datetime

<<<<<<< HEAD
# ------------------------------------------------------------------------------
# Section to pull hourly price data
=======
>>>>>>> 9da73cdee6499d86fd5a1ef940231adab6030f33
exchange = ccxt.binance({'options':{'adjustForTimeDifference':True}})

market = exchange.load_markets()
tickers = list(market.keys())

coins = set()
[[coins.add(coin) for coin in ticker.split('/') if coin != 'BTC'] for ticker in tickers]
coins = list(coins)

# Since we can't pull BTC/BTC, use BTC/USDT ticker.  Otherwise, use coin/BTC as ticker
tickers = [coin + '/BTC' for coin in coins]
tickers.insert(0, 'BTC/USDT')

timestamps = []
start_date = '2017-01-01 00:00:00'
for i in range(16500):
	timestamps.append(start.strftime('%Y-%m-%d %H:%M:%S'))
	start += datetime.timedelta(hours=1)

df = pd.DataFrame()
df['date'] = timestamps

end_date = exchange.parse8601('2018-09-30 23:59:59')

msec = 1000
minute = 60 * msec
hour = minute * 60

for ticker in tickers:
	ticker = 'ETH/BTC'
	start_date = exchange.parse8601('2017-01-01 00:00:00')

for ticker in tickers:
	end_date = exchange.parse8601('2018-10-30 00:00:00')
	# Length of above when queried - 16500 (ETH/BTC) (or 33 queries of 500)

	data = []

	for i in range(33):
		try:
			candles = np.array(exchange.fetch_ohlcv(ticker, '1h', start_date))
		except:
			continue

		start_date += len(candles) * hour
<<<<<<< HEAD
		data += candles[:, :2].tolist()


=======
		data += candles[:, 1].tolist()
>>>>>>> 9da73cdee6499d86fd5a1ef940231adab6030f33

	if len(data) == 16500:
		df[ticker[:ticker.find('/')]] = data

# multiply all columns by BTC column to get $ prices, since they're currently all in BTC denomination
for col in df[df.columns[1:].values]:
	df[col] = np.multiply(df[col], df['BTC'])


new_df.set_index('date', drop=True, inplace=True)
new_df.to_csv(os.getcwd() + '/backtests/historical prices.csv')
