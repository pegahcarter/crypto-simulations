import os
import sys
import ccxt
import numpy as np
import pandas as pd

# pull epoch dates used for market caps
market_cap = pd.read_csv(os.getcwd() + '/backtests/historical market cap.csv')
dates_epoch = market_cap['date']
date_range = [time.strftime('%m/%d/%Y', time.localtime(day)) for day in dates_epoch]

# Use coins listed on Bittrex
primary_exchange = ccxt.bittrex({'options': {'adjustForTimeDifference': True}})
market = primary_exchange.load_markets()
tickers = list(market.keys())

coins = set()
[[coins.add(coin) for coin in ticker.split('/') if coin != 'BTC'] for ticker in tickers]
coins = list(coins)

# Since we can't pull BTC/BTC, use BTC/USDT ticker.  Otherwise, use coin/BTC as ticker
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
