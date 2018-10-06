import pandas as pd
import numpy as np
import ccxt
import os
from datetime import datetime

def main():
	# Function to update transactions
	def update_transactions(side, ticker1, ticker2, quantity, dollar_value):
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

	# Function to return current portfolio values/weights
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

	path = 'C:/Users/Carter/Documents/Github/crypto-rebalance/'
	transaction_history = pd.read_csv(path + 'rebalance portfolio/transactions.csv')

	# note: You'll have to change this path to the path of your API text file
	with open('C:/Users/Carter/Documents/Old/Administrative/api.txt', 'r') as f:
		api = f.readlines()
		apiKey = api[0][:len(api[0])-1]
		secret = api[1][:len(api[1])]

	exchange = ccxt.binance({
		'options': {'adjustForTimeDifference': True},
		'apiKey': apiKey,
		'secret': secret})

	balance = exchange.fetchBalance()

	# Don't include coins with quantities less than .05 - helps ignore dust of coins
	# Note: If BTC is in your portfolio and you're holding less than .05 BTC,
	# you'll need to change line below.
	coins = [asset['asset'] for asset in balance['info']['balances'] if float(asset['free']) > 0.05 and asset['asset'] != 'GAS']

	data = update_data(coins)

	n = 1/(len(coins))
	thresh = .01

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

	rebalance_id = transaction_history['rebalance_id'][len(transaction_history) - 1] + 1
	while data['weight'][0] - data['weight'][len(data) - 1] > 2 * n * thresh:
		trade_id = transaction_history['trade_id'][len(transaction_history) - 1] + 1

		order = rebalance_order(data['symbol'][0], data['symbol'][len(data) - 1])
		weight_to_move = min([data['weight'][0] - n, n - data['weight'][len(data) - 1]])

		for x in range(0,len(order),2):
			x = 0
			ratio = order[x]
			side = order[x + 1]
			ticker1, ticker2 = ratio[:ratio.find('/')], ratio[ratio.find('/') + 1:]

			quantity = round(weight_to_move * data['dollar_value'].sum() / data[data['symbol'] == ticker1]['price'].values[0], 5)
			dollar_value = quantity * data[data['symbol'] == ticker1]['price'].values[0]
			exchange.create_order(order[0], 'market', order[1], quantity)
			transaction_history = update_transactions(side, ticker1, ticker2, quantity, dollar_value)

		balance = exchange.fetchBalance()
		data = update_data(coins)












# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

	if len(transaction_history) == 0:
		rebalance_id = 1
	else:
		rebalance_id = max(transaction_history['rebalance_id']) + 1
	tickers = set()
	[tickers.add(ticker) for ticker in exchange.fetch_tickers()]

	wallet = pd.DataFrame(exchange.fetchBalance()['info']['balances'])
	btc_price = exchange.fetch_ticker('BTC/USDT')['ask']
	coins = wallet.loc[wallet['free'].astype(float) > .1, 'asset'].tolist()

	avg_weight = 1/len(coins)
	thresh = .02
	trade_count = 0

	while True:
		quantities = wallet.loc[wallet['free'] != '0.00000000','free'].tolist()
		quantities = [float(i) for i in quantities]
		prices = [btc_price if coin == 'BTC' else exchange.fetch_ticker(coin + '/BTC')['ask'] * btc_price for coin in coins]
		dollar_values = np.multiply(quantities, prices).tolist()
		weights = np.divide(dollar_values, sum(dollar_values))

		if max(weights) - min(weights) < 2 * avg_weight * thresh:
			break

		weight_to_move = min([avg_weight-min(weights), max(weights)-avg_weight])
		dollar_amt = weight_to_move * total_dollar_value
		fee = dollar_amt * .0025

		light_coin, heavy_coin = coins[weights.argmin()], coins[weights.argmax()]
		ratios = {light_coin + '/' + heavy_coin, heavy_coin + '/' + light_coin}
		ticker = list(ratios & tickers)

		if ticker:
			single_trade = True
			side = ['sell']
			if ticker[0][:ticker[0].find('/')] == heavy_coin:
				side = ['buy']

		else:
			single_trade = False
			ticker = [heavy_coin + '/BTC', light_coin + '/BTC']
			side = ['sell', 'buy']

		for t, s in zip(ticker, side):
			numer, denom = t[:t.find('/')], t[t.find('/')+1:]
			quantity = dollar_amt / prices[coins.index(numer)]]

			if len(transaction_history) == 0:
				trade_id = 1
			else:
				trade_id = transactions['trade_id'][len(transactions) - 1] + 1

			exchange.create_order(t, 'market', s, quantity)
			transaction_history.append({
										'trade_id':trade_id,
										'rebalance_id':rebalance_id,
										'date':str(datetime.now()),
										'side': s,
										'ticker1':numer,
										'ticker2':denom,
										'quantity':quantity,
										'dollar_value':dollar_amt,
										'fees':fee,
										'single_trade':single_trade
										}, ignore_index=True)

			trade_count += 1

	transaction_history.to_csv('transactions.csv')
	print('Rebalance complete.  # of trades executed: {}'.format(trade_count))

if __name__ == '__main__':
	main()
