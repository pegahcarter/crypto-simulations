import pandas as pd
import numpy as np
import ccxt
import os
from datetime import datetime

def main():
	transaction_history = pd.read_csv(os.getcwd() + '/rebalance portfolio/transactions.csv')
	if len(transaction_history) == 0:
		rebalance_id = 1
	else:
		rebalance_id = max(transaction_history['rebalance_id']) + 1

	with open(os.getcwd() + '/working files/api.txt', 'r') as f:
	    api = f.readlines()
	    apiKey = api[0][:len(api[0])-1]
	    secret = api[1][:len(api[1])]

	exchange = ccxt.binance({
	    'options': {'adjustForTimeDifference': True},
	    'apiKey': apiKey,
	    'secret': secret})

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
