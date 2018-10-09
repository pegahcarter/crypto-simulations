import pandas as pd
import numpy as np
import ccxt
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbs.sql.setup import Transactions, Base
import sqlite3
from pymongo import MongoClient
from pathlib import Path


from update_transactions import update_csv_transactions
from update_transactions import update_sql_transactions
from update_transactions import update_mongo_transactions


def main():

	csv_transactions = True
	sql_transactions = True
	mongo_transactions = True

	def pull_coin_info(coin):
		p = data[data['symbol'] == coin]['price'].values[0]
		q = data[data['symbol'] == coin]['quantity'].values[0]
		dv = p * q
		return p, q, dv

	def initialize_dbs(csv, sql, mongo):
		if csv:
			csv_db = Path(os.getcwd() + '/dbs/csv/transactions.csv')
			if not csv_db.isfile():
				portfolio = []
				transactions = []
				trade_id = 1
				for coin in coins:
					price, quantity, dollar_value = pull_coin_info(coin)
					portfolio.append([
						coin,					# coin
						price,					# current_price
						quantity,				# quantity
						dollar_value			# dollar_value
					])
					transactions.append([
						trade_id,				# trade_id
						0, 						# rebalance_id
						str(datetime.now()),	# date
						coin,					# coin
						'buy', 					# side
						coin + '/USD',			# ratio
						price, 					# price
						quantity, 				# quantity
						dollar_value, 			# dollar_value
						dollar_value * 0.0075	# fees
					])
					trade_id += 1

				portfolio_pd = pd.DataFrame(
					portfolio,
					columns = [
						'coin',
						'current_price',
						'quantity',
						'dollar_value'
					]
				)

				transactions_pd = pd.DataFrame(
					transactions,
					columns = [
						'trade_id',
						'rebalance_id',
						'date',
						'coin',
						'side',
						'ratio',
						'price',
						'quantity'
						'dollar_value',
						'fees'
					]
				)

				portfolio_pd.to_csv(os.getcwd() + '/dbs/csv/portfolio.csv')
				transactions_pd.to_csv(os.getcwd() + '/dbs/csv/transactions.csv')

		if sql:
			sql_db = Path(os.getcwd() + '/dbs/sql/rebalance.db')
			if not sql_db.is_file():
				import dbs.sql.setup
				engine = create_engine('sqlite:///dbs/sql/rebalance.db')
				Base.metadata.bind = engine
				DBSession = sessionmaker(bind=engine)
				session = DBSession()
				for coin in coins:
					price, quantity, dollar_value = pull_coin_info(coin)
					session.add(Portfolio(
						coin = coin,
						current_price = price,
						quantity = quantity,
						dollar_value = dollar_value
					))
					session.commit()
					session.add(Transactions(
						rebalance_id = 0,
						date = str(datetime.now()),
						coin = coin,
						side = 'buy',
						ratio = coin + '/USD',
						price = price,
						quantity = quantity,
						dollar_value = dollar_value
						fees = dollar_value * 0.0075
					))
					session.commit()


		if mongo:
			mongo_db = Path(os.getcwd() + '/dbs/mongo/rebalance.db')
			if not mongo_db:
				client = MongoClient()
				mongo_db = client['rebalance']
				for coin in coins:
					price, quantity, dollar_value = pull_coin_info(coins)
					mongo_db.insert_one({
						coin: {
							'quantity': quantity,
							'current_price': price,
							'dollar_value': dollar_value,
							'transactions': {
								'trade_id': 0,
								'rebalance_id': 0,
								'date': date,
								'side': 'buy',
								'coin_used_to_buy': 'USD',
								'price': price,
								'quantity': quantity,
								'dollar_value': dollar_value,
								'fees': dollar_value * 0.0075
							}
					})
		# End of initialize_dbs function

	def update_transactions(csv, sql, mongo):
		folder = os.getcwd() + '/dbs/'
		if csv:
			update_csv_transactions(folder + 'csv/')

		if sql:
			update_sql_transactions(folder + 'sql/')


		if mongo:
			update_mongo_transactions(folder + 'mongo/')

		# end of update_transactions function



	# Function to update transaction history
	def update_csv(side, ticker1, ticker2, quantity, dollar_value):
		df = transaction_history.append({
			'trade_id':trade_id,
			'rebalance_id':rebalance_id,
			'date':str(datetime.now()),
			'side': side,
			'ticker1':ticker1,
			'ticker2':ticker2,
			'quantity':quantity,
			'dollar_value': dollar_value,
			'fees':dollar_value * .0075,
			}, ignore_index=True)

		return df


	# Function to determine ticker for trade and side of trade
	def rebalance_order(coin1, coin2):
		try:
			exchange.fetch_ticker(coin1 + '/' + coin2)['info']
			return coin1 + '/' + coin2, 'sell'
		except:
			try:
				exchange.fetch_ticker(coin2 + '/' + coin1)['info']
				return coin2 + '/' + coin1, 'buy'
			except:
				return coin1 + '/BTC', 'sell', coin2 + '/BTC', 'buy'


	# Function that returns current portfolio values/weights
	def update_data(coins):
		btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])
		df = pd.DataFrame(columns=['symbol', 'quantity', 'price', 'dollar_value'])
		for coin in coins:
			quantity = balance[coin]['total']
			if coin == 'BTC':
				price = btc_price
			else:
				btc_ratio = float(exchange.fetch_ticker(coin + '/BTC')['info']['lastPrice'])
				price = btc_ratio * btc_price

			dollar_value = quantity * price
			df = df.append({
				'symbol': coin,
				'quantity': quantity,
				'price': price,
				'dollar_value': dollar_value
			}, ignore_index=True)

		df['weight'] = list(map(lambda x: x / df['dollar_value'].sum(), df['dollar_value']))
		df = df.sort_values('weight', ascending=False).reset_index(drop=True)
		return df


	transaction_history = pd.read_csv('transactions.csv')

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
	coins = [asset['asset'] for asset in balance['info']['balances'] if float(asset['free']) > 0.05 and asset['asset'] != 'GAS']

	data = update_data(coins)

	initialize_dbs()

	n = 1/(len(coins))
	thresh = .02

	# If there's no transaction history, add all coins in portfolio as initial transactions
	if len(transaction_history) == 0:
		trade_id, rebalance_id = 0, 0
		transaction_history = pd.DataFrame(
			columns = [
				'trade_id',
				'rebalance_id',
				'date',
				'side',
				'ticker1',
				'ticker2',
				'quantity',
				'dollar_value',
				'fees'
				]
			)

		for coin in coins:
			temp = data[data['symbol'] == coin]
			price, quantity = temp['price'].values[0], temp['quantity'].values[0]

			transaction_history = update_transactions('buy', coin, 'USD', quantity, quantity * price)

	trade_count = 0
	rebalance_id = transaction_history['rebalance_id'][len(transaction_history) - 1] + 1

	# Execute trades until all coin weights in portfolio are within our threshold range
	while data['weight'][0] - data['weight'][len(data) - 1] > 2 * n * thresh:
		trade_id = transaction_history['trade_id'][len(transaction_history) - 1] + 1

		order = rebalance_order(data['symbol'][0], data['symbol'][len(data) - 1])
		weight_to_move = min([data['weight'][0] - n, n - data['weight'][len(data) - 1]])

		for x in range(0,len(order),2):
			trade_count += 1
			ratio = order[x]
			side = order[x + 1]
			ticker1, ticker2 = ratio[:ratio.find('/')], ratio[ratio.find('/') + 1:]

			quantity = round(weight_to_move * data['dollar_value'].sum() / data[data['symbol'] == ticker1]['price'].values[0], 5)
			dollar_value = quantity * data[data['symbol'] == ticker1]['price'].values[0]
			try:
				exchange.create_order(order[0], 'market', order[1], quantity)
			except:
				sys.exit('Error: please connect to a network without a proxy to execute trades.')

			transaction_history = update_transactions(side, ticker1, ticker2, quantity, dollar_value)

		balance = exchange.fetchBalance()
		data = update_data(coins)

	print('Rebalance complete.  # of trades executed: {}'.format(trade_count))
	print('\n', data)

	if trade_count > 0:
		transaction_history.to_csv('transactions.csv', index=False)

if __name__ == '__main__':
	main()
