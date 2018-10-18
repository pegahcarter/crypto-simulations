import pandas as pd
import numpy as np
import ccxt
import os
import sys
import sys
from pathlib import Path
from datetime import datetime
import update
# NOTE: how do I check if crypto.db exists without running 'through' bash console?
# If it doesn't exist, how can I create it through a python script?
# import sql.setup

def main():

	def pull_coin_info(coin):
		p = data[data['symbol'] == coin]['price'].values[0]
		q = data[data['symbol'] == coin]['quantity'].values[0]
		dv = p * q
		return p, q, dv

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

	# note: You'll have to change this path to the path of your API text file
	with open('some file.txt', 'r') as f:
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

	data = update_data(coins)

	Initialize()

	n = 1/(len(coins))
	thresh = .02

	# Execute trades until all coin weights in portfolio are within our threshold range
	while data['weight'][0] - data['weight'][len(data) - 1] > 2 * n * thresh:

		order = rebalance_order(data['symbol'][0], data['symbol'][len(data) - 1])
		weight_to_move = min([data['weight'][0] - n, n - data['weight'][len(data) - 1]])

		for x in range(0,len(order),2):
			ratio = order[x]
			side = order[x + 1]
			ticker1, ticker2 = ratio[:ratio.find('/')], ratio[ratio.find('/') + 1:]

			quantity = round(weight_to_move * data['dollar_value'].sum() / data[data['symbol'] == ticker1]['price'].values[0], 5)
			dollar_value = quantity * data[data['symbol'] == ticker1]['price'].values[0]
			try:
				exchange.create_order(order[0], 'market', order[1], quantity)
			except:
				sys.exit('Error: please connect to a network without a proxy to execute trades.')

			Update()

		balance = exchange.fetchBalance()
		data = update_data(coins)


if __name__ == '__main__':
	main()
	print('Rebalance complete')
