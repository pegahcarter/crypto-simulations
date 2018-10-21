import pandas as pd
import numpy as np
import ccxt
import os
import sys
import sys
from pathlib import Path
from datetime import datetime
#import update
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql.setup import Transactions, Base
# from sql.initialize import Initialize

# NOTE: how do I check if crypto.db exists without running 'through' bash console?
# If it doesn't exist, how can I create it through a python script?
# import sql.setup


# Function to get current coin price in $
def coin_price(coin):
	btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])
	if coin == 'BTC':
		price = btc_price
	else:
		btc_ratio = float(exchange.fetch_ticker(coin + '/BTC')['info']['lastPrice'])
		price = btc_ratio * btc_price

	return price

# Function to determine ticker for trade and side of trade
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
	# NOTE: I had to copy and paste this function in to make it work... I'll need
	#		to fix that.
	#Initialize(session, exchange, coins)
	btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])
	for i, coin in enumerate(coins):
		quantity = balance[coin]['total']
		price = coin_price(coin)
		dollar_value = quantity * price

		session.add(Transactions(
			trade_num = i+1,
			rebalance_num = 0,
			date = datetime.now(),
			coin = coin,
			side = 'buy',
			units = quantity,
			price_per_unit = price,
			fees = dollar_value * 0.0075,
			previous_units = 0,
			cumulative_units = quantity,
			transacted_value = dollar_value,
			previous_cost = 0,
			cumulative_cost = dollar_value,
		))
		session.commit()
	# refresh transactions df
	transactions = pd.read_sql(sql=query, con=engine)
	rebalance_num = 1
else:
	rebalance_num = transactions['rebalance_num'].max() + 1


n = 1/(len(coins))
thresh = .02
# ------------------------------------------------------------------------------
## Calculating weight without data DataFrame


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
		# i = 0
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

		for coin, side, quantity in zip(trade_coins, trade_sides, trade_quantities):
			# coin, side, quantity = trade_coins[0], trade_sides[0], trade_quantities[0]
			temp = transactions.loc[transactions['coin'] == coin]
			previous_units = temp['cumulative_units'].values[len(temp)-1]
			previous_cost = temp['cumulative_cost'].values[len(temp)-1]

			if side == 'buy':
				transacted_value = trade_dollars * (1 + .0075)
				cumulative_cost = previous_cost + transacted_value
				cumulative_units = previous_units + quantity

				cost_of_transaction = 0
				cost_per_unit = 0

				gain_loss = 0
				realised_pct = 0
			# Otherwise, side == 'sell'
			else:
				transacted_value = trade_dollars * (1 - .0075)
				cumulative_cost = previous_cost - transacted_value
				cumulative_units = previous_units - quantity

				cost_of_transaction = previous_cost * quantity/previous_units
				cost_per_unit = previous_cost / previous_units

				gain_loss = transacted_value - cost_of_transaction
				realised_pct = gain_loss / cost_of_transaction

			# push to SQL
			session.add(Transactions(
				rebalance_num = rebalance_num,
				date = datetime.now(),
				coin = coin,
				side = side,
				units = quantity,
				price_per_unit = trade_dollars / quantity,
				fees = dollar_value * .0075,
				previous_units = previous_units,
				cumulative_units = cumulative_units,
				transacted_value = transacted_value,
				previous_cost = previous_cost,
				cost_of_transaction = cost_of_transaction,
				cost_per_unit = cost_per_unit,
				cumulative_cost = cumulative_cost,
				gain_loss = gain_loss,
				realised_pct = realised_pct
			))
			session.commit()


	# Update local transactions data frame
	engine = create_engine('sqlite:///sql/transactions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	transactions = pd.read_sql(sql=query, con=engine)

# ------------------------------------------------------------------------------
























# Execute trades until all coin weights in portfolio are within our threshold range
while data['weight'][0] - data['weight'][len(data) - 1] > 2 * n * thresh:

	# NOTE: change order to a different term
	tickers = determine_ticker(data['symbol'][0], data['symbol'][len(data) - 1])
	weight_to_move = min([data['weight'][0] - n, n - data['weight'][len(data) - 1]])

	for x in range(0,len(order),2):
		ratio = order[x]
		side = order[x + 1]
		ticker1, ticker2 = ratio[:ratio.find('/')], ratio[ratio.find('/') + 1:]

		quantity = round(weight_to_move * data['dollar_value'].sum() / data[data['symbol'] == ticker1]['price'].values[0], 5)
		dollar_value = quantity * data[data['symbol'] == ticker1]['price'].values[0]
		try:
			order = exchange.create_order(order[0], 'market', order[1], quantity)
		except:
			sys.exit('Error: please connect to a network without a proxy to execute trades.')

		Update(rebalance_num, session, order, transactions)
		# Refresh pandas DataFrame, instead of unnecessary appending
		transactions = pd.read_sql(sql=query, con=engine)

	balance = exchange.fetchBalance()
	data = update_data(coins)
