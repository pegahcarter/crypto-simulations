import pandas as pd
import numpy as np
import ccxt
import os
import sys
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from py.setup import Transactions, Base
from py.initialize import Initialize
# from py.functions import coin_price, determine_ticker

# NOTE: how do I check if crypto.db exists without running 'through' bash console?
# If it doesn't exist, how can I create it through a python script?

# NOTE: How can I publicly track transactions without revealing $ of portfolio?
# This would need to work for website.

# NOTE: You'll have to change this path to the path of your API text file
with open('C:/Users/Carter/Documents/Administrative/api.txt', 'r') as f:
	api = f.readlines()
	apiKey = api[0][:len(api[0])-1]
	secret = api[1][:len(api[1])]

try:
	exchange = ccxt.binance({
		'options': {'adjustForTimeDifference': True},
		'apiKey': apiKey,
		'secret': secret})

	balance = exchange.fetchBalance()
except:
	sys.exit('Error connecting to API socket.  Please ensure you are opening the \
		   correct api text file and are not using a network proxy, and try again')

# ------------------------------------------------------------------------------
# NOTE: need to figure out how to import functions in line 13.  Error message is:
#
#  File "C:\Users\Carter\Documents\GitHub\crypto-rebalance\rebalance portfolio\py\functions.py", line 5, in coin_price
# 	btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])
#
# NameError: name 'exchange' is not defined

def determine_ticker(coin1, coin2):
	try:
		exchange.fetch_ticker(coin1 + '/' + coin2)['info']
		return coin1 + '/' + coin2, 'sell'
	except:
		try:
			exchange.fetch_ticker(coin2 + '/' + coin1)['info']
			return coin2 + '/' + coin1, 'buy'
		except:
			return coin1 + '/BTC', 'sell', coin2 + '/BTC', 'buy'

# Function to get current coin price in $
def coin_price(coin):
	btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])
	if coin == 'BTC':
		price = btc_price
	else:
		btc_ratio = float(exchange.fetch_ticker(coin + '/BTC')['info']['lastPrice'])
		price = btc_ratio * btc_price

	return price

# ------------------------------------------------------------------------------
# Don't include coins with quantities less than .05 - helps ignore dust of coins
# Note: If you're holding less than .05 of a coin with your portfolio, or holding GAS,
# you'll need to modify the line below.
coins = [asset['asset']
		 for asset in balance['info']['balances']
		 if float(asset['free']) > 0.05 and asset['asset'] != 'GAS']

# Connect to our SQL database
engine = create_engine('sqlite:///sql/transactions.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

query = ''' SELECT * FROM transactions'''
transactions = pd.read_sql(sql=query, con=engine)


# Create initial transactions of coins if there are no recorded transactions
if len(transactions) == 0:
	for coin in coins:
		Initialize(session, exchange, coin)
	# refresh transactions df
	transactions = pd.read_sql(sql=query, con=engine)
	rebalance_num = 1
else:
	rebalance_num = transactions['rebalance_num'].max() + 1


n = 1/(len(coins))
thresh = .02
i = 0

while True:
	balance = exchange.fetchBalance()
	# NOTE: I had to re-create the coins list since our balance will change after
	# a transaction, and a second trade would be based on the old balance.
	# I should be able to fix this redunancy too.
	coins = [asset['asset']
			 for asset in balance['info']['balances']
			 if float(asset['free']) > 0.05 and asset['asset'] != 'GAS']

	quantities, dollar_values = [], []
	for coin in coins:
		quantity = balance[coin]['total']
		quantities.append(quantity)
		dollar_values.append(quantity * coin_price(coin))

	# Line comprehension of above loop - should I use this instead and make another
	# line comprehension for quantities? Or is it better visually to keep the current method?
	# dollar_values = np.array([balance[coin]['total'] * coin_price(coin) for coin in coins])

	# Convert our lists to np arrays since our lists don't work well with mathematical operations
	quantities = np.array(quantities)
	dollar_values = np.array(dollar_values)

	if (dollar_values.max() - dollar_values.min()) / dollar_values.sum() < 2 * n * thresh:
		break

	# To prevent infinite looping, let's break after 5 trades, but ONLY when the
	# program still is above 2 * n * thresh.
	i += 1
	if i == 5:
		sys.exit('5 trades completed. Ending rebalance.')


	# Determine if there's a trade ratio between the coins, or if we need to convert to BTC first
	tickers = determine_ticker(coins[dollar_values.argmin()], coins[dollar_values.argmax()])

	# Reference so that BTC won't be documented in the dual trade.
	if len(tickers) > 2:
		dual_trade = True
	else:
		dual_trade = False

	weight_to_move = min([dollar_values.max()/dollar_values.sum() - n, n - dollar_values.min()/dollar_values.sum()])
	trade_dollars = weight_to_move * dollar_values.sum()

	for x in range(0,len(tickers),2):
		ratio = tickers[x]
		trade_coins = ratio.split('/')

		side = tickers[x+1]
		if side == 'sell':
			trade_sides = ['sell', 'buy']
		else:
			trade_sides = ['buy', 'sell']

		# Easier way to reference both coins in our dollar_values list at the same time
		indices = [coins.index(trade_coins[0]), coins.index(trade_coins[1])]
		trade_quantities = trade_dollars / (dollar_values[indices] / quantities[indices])

		# Make trade with quantity of numerator
		exchange.create_order(ratio, 'market', side, trade_quantities[0])

		# Update SQL database
		transactions = Update(dual_trade, trade_coins, trade_sides, trade_quantities, transactions, session)

print('Rebalance complete.')
print('# of trades executed: ', i)
