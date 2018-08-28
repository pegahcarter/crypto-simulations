import os
import sys
import ccxt
import pandas as pd

# Returns dates and prices for the ticker: excludes high, low, volume, etc.
def ticker_array(ticker):
	return np.array(exchange.fetch_ohlcv(ticker, '1d'))[:,:2]

df = pd.DataFrame()
exchange = ccxt.bittrex({'options': {'adjustForTimeDifference': True}})

# Coins w/ market cap above $100 mil on July 30, 2017 (excludes Bitconnect)
# For reference - https://coinmarketcap.com/historical/20170730/
coins = ['BTC','ETH','XRP','LTC','DASH','XEM','ETC','IOTA','XMR','EOS','NEO','ZEC',
		 'BTS','QTUM','USDT','STEEM','VERI','WAVES','ICN','SC','BCN','GNO','LSK',
		 'GNT','REP','DOGE','SNT','XLM','GBYTE','DCR','FCT','DGB','MAID','GAME',
		 'DGD','OMG','ARDR','MCAP','BAT','PPT','PIVX','NXT']

# Since we can't pull BTC/BTC, use BTC/USDT ticker.  Otherwise, use coin/BTC as ticker
tickers = ['BTC/USDT']
[tickers.append(coin + '/BTC') for coin in coins[1:]]

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


df.set_index(['date'], drop=True, inplace=True)
df.to_csv('historical prices.csv')
