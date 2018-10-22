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
from py.functions import coin_price, determine_ticker

# NOTE: how do I check if crypto.db exists without running 'through' bash console?
# If it doesn't exist, how can I create it through a python script?


# note: You'll have to change this path to the path of your API text file
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

# Don't include coins with quantities less than .05 - helps ignore dust of coins
# Note: If you're holding less than .05 of a coin with your portfolio, or holding GAS,
# you'll need to modify the line below.
coins = [asset['asset']
		 for asset in balance['info']['balances']
		 if float(asset['free']) > 0.05 and asset['asset'] != 'GAS']

engine = create_engine('sqlite:///sql/transactions.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

query = ''' SELECT * FROM transactions'''
transactions = pd.read_sql(sql=query, con=engine)

# Create initial transactions of coins if there are no recorded transactions
if len(transactions) == 0:
	Initialize(session, exchange, coins)
	# refresh transactions df
	transactions = pd.read_sql(sql=query, con=engine)
	rebalance_num = 1
else:
	rebalance_num = transactions['rebalance_num'].max() + 1


n = 1/(len(coins))
thresh = .02


i = 0
while True:
	i += 1
	if i > 4:
		sys.exit('5 trades completed. Ending rebalance.')

	balance = exchange.fetchBalance()
	coins = [asset['asset']
			 for asset in balance['info']['balances']
			 if float(asset['free']) > 0.05 and asset['asset'] != 'GAS']

	quantities, dollar_values = [], []
	for i, coin in enumerate(coins):
		quantity = balance[coin]['total']
		quantities.append(quantity)
		dollar_values.append(quantity * coin_price(coin))

	quantities = np.array(quantities)
	dollar_values = np.array(dollar_values)

	dollar_values = np.array([balance[coin]['total'] * coin_price(coin) for coin in coins])
	if (dollar_values.max() - dollar_values.min()) / dollar_values.sum() < 2 * n * thresh:
		break

	tickers = determine_ticker(coins[dollar_values.argmin()], coins[dollar_values.argmax()])
	weight_to_move = min([dollar_values.max()/dollar_values.sum() - n, n - dollar_values.min()/dollar_values.sum()])
	trade_dollars = weight_to_move * dollar_values.sum()

	for i in range(0,len(tickers),2):
		ratio = tickers[i]
		trade_coins = ratio.split('/')

		side = tickers[i+1]
		if side == 'sell':
			trade_sides = ['sell', 'buy']
		else:
			trade_sides = ['buy', 'sell']

		indices = [coins.index(trade_coins[0]), coins.index(trade_coins[1])]
		trade_quantities = trade_dollars / (dollar_values[indices] / quantities[indices])

		# Make trade with quantity of numerator
		exchange.create_order(ratio, 'market', side, trade_quantities[0])
		transactions = Update(coins, sides, quantities, transactions, session)
