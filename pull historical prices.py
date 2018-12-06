import os
import sys
import ccxt
import numpy as np
import pandas as pd
import datetime

# ------------------------------------------------------------------------------
# Section to pull hourly price data
exchange = ccxt.binance({'options':{'adjustForTimeDifference':True}})

market = exchange.load_markets()
tickers = list(market.keys())

coins = set()
[[coins.add(coin) for coin in ticker.split('/') if coin != 'BTC'] for ticker in tickers]
coins = list(coins)

# Since we can't pull BTC/BTC, use BTC/USDT ticker.  Otherwise, use coin/BTC as ticker
tickers = [coin + '/BTC' for coin in coins]
tickers.insert(0, 'BTC/USDT')


datetime.datetime.fromtimestamp(data[0][0] / 1000)
datetime.datetime.fromtimestamp(data[-1][0] / 1000)




df = pd.DataFrame()
end_date = exchange.parse8601('2018-09-30 23:59:59')

msec = 1000
minute = 60 * msec
hour = minute * 60

for ticker in tickers:
	ticker = 'ETH/BTC'
	start_date = exchange.parse8601('2017-01-01 00:00:00')
	data = []
	# NOTE: Since this pulls while start_date < end_date, can it pull 500
	# trades starting on 9/30/2018, so that the last couple dates are over
	# the time frame we want to analyze? If so -
	# 	1. Do we adjust time frame analyzed to the larger date range?
	#	2. Do we eliminate all data with dates above the end date?
	#	3. Do we stop the loop at a specific time frame, so that the last
	# 		date of price information is the end date we want?

	while start_date < end_date:
		try:
			candles = np.array(exchange.fetch_ohlcv(ticker, '1h', start_date))
		except:
			continue

		start_date += len(candles) * hour
		data += candles[:, :2].tolist()



	df[ticker[:ticker.find('/')]] = data

# multiply all columns by BTC column to get $ prices, since they're currently all in BTC denomination
for col in df[df.columns[1:].values]:
	df[col] = np.multiply(df[col], df['BTC'])


timestamps = []
start_date = '2017-01-01 00:00:00'
end_date = '2018-10-01 00:00:00'

start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

day = start
while day < end:
	timestamps.append(day.strftime('%Y-%m-%d %H:%M:%S'))
	day += datetime.timedelta(hours=1)

len(timestamps)
timestamps[len(timestamps)-10:]
# ------------------------------------------------------------------------------

# pull epoch dates used for market caps
market_cap = pd.read_csv(os.getcwd() + '/backtests/historical market cap.csv')
dates_epoch = market_cap['date']
date_range = [time.strftime('%m/%d/%Y', time.localtime(day)) for day in dates_epoch]

# Use coins listed on Bittrex
primary_exchange = ccxt.bittrex({'options': {'adjustForTimeDifference':True}})
market = primary_exchange.load_markets()
tickers = list(market.keys())

coins = set()
[[coins.add(coin) for coin in ticker.split('/') if coin != 'BTC'] for ticker in tickers]
coins = list(coins)

# Since we can't pull BTC/BTC, use BTC/USDT ticker.  Otherwise, use coin/BTC as ticker
# I don't like this process to get tickers and coins - it seems like there's a lot of extra steps
# like - do I need to zip coins and tickers?  What if I do ticker[:ticker.find('/')]?



tickers = [coin + '/BTC' for coin in coins]
coins.insert(0, 'BTC')
tickers.insert(0, 'BTC/USDT')

df = [list(dates_epoch)]
coins_to_simulate = []

for coin, ticker in zip(coins, tickers):
	# Pull information if ticker exists
	try:
		data = np.array(primary_exchange.fetch_ohlcv(ticker, '1d'))[:, :2]
	except:
		continue

	coin_prices = [price \
				   for day, price in data \
				   if time.strftime('%m/%d/%Y', time.localtime(day/1000)) in date_range]

	# Only add coin if it has a full year of price data
	if len(coin_prices) == len(dates):
		df.append(coin_prices)
		coins_to_simulate.append(coin)

# Add date to the front of coins to create column names
coins_to_simulate.insert(0, 'date')

df_np = np.array(df)

# Since all coins are in BTC denomination, multiply by BTC price to get $ price
df_np[2:] *= df[1]

new_df = pd.DataFrame(df_np.transpose(), columns=coins_to_simulate)

new_df.set_index('date', drop=True, inplace=True)
new_df.to_csv(os.getcwd() + '/backtests/historical prices.csv')
